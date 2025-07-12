# WebSocket Routes - SRIMI: Single Responsibility for Real-time Communication
from flask import Flask, request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from datetime import datetime

def register_websocket_routes(app: Flask) -> None:
    """Register WebSocket events with dependency injection"""
    
    # Get socketio instance from app context
    socketio = app.extensions.get('socketio')
    if not socketio:
        return  # Skip if socketio not initialized
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle user connection"""
        if current_user.is_authenticated:
            from models import db
            current_user.is_online = True
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            join_room(f"user_{current_user.id}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle user disconnection"""
        if current_user.is_authenticated:
            from models import db
            current_user.is_online = False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Handle joining a chat room"""
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
            
        from models import ChatParticipant
        chat_id = data['chat_id']
        participant = ChatParticipant.query.filter_by(
            chat_id=chat_id, 
            user_id=current_user.id
        ).first()
        
        if participant:
            join_room(f"chat_{chat_id}")
            emit('joined_chat', {'chat_id': chat_id})

    @socketio.on('leave_chat')
    def handle_leave_chat(data):
        """Handle leaving a chat room"""
        if not current_user.is_authenticated:
            return
            
        chat_id = data['chat_id']
        leave_room(f"chat_{chat_id}")

    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a message - with bot detection pipeline"""
        if not current_user.is_authenticated:
            emit('message_error', {'error': 'Authentication required'})
            return
            
        from services import get_chat_service, get_message_service, initialize_websocket_service
        
        chat_id = data['chat_id']
        message_text = data['message']
        
        # Inject services
        message_service = get_message_service()
        chat_service = get_chat_service()
        websocket_service = initialize_websocket_service(socketio)
        
        # 🤖 BOT DETECTION CHECK - Check if user can send messages
        can_send_check = message_service.can_send_message(current_user)
        if not can_send_check['can_send']:
            emit('message_error', {
                'error': can_send_check['reason'],
                'bot_analysis': can_send_check.get('bot_analysis', {}),
                'type': 'bot_detection'
            })
            return
        
        # Check message limit
        messages_today = message_service.get_user_messages_sent(current_user)
        
        if len(messages_today) >= 100:
            emit('message_error', {
                'error': 'Daily message limit exceeded',
                'data_value': f"${current_user.id * 50}",
                'messages_used': len(messages_today),
                'message_limit': 100
            })
            return
        
        # Verify user is in chat
        result = chat_service.get_chat_by_id(current_user, chat_id)
        if result['status'] != 200:
            emit('message_error', {'error': result['error']})
            return
        
        # Track common phrases
        chat_service.add_common_phrase(current_user.id, message_text)
        
        # Create message with bot detection
        result = message_service.send_message(
            sender_id=current_user.id,
            room_id=chat_id,
            content=message_text,
            metadata={
                'timestamp': datetime.utcnow().isoformat(),
                'user_agent': request.environ.get('HTTP_USER_AGENT', ''),
                'ip_address': request.environ.get('REMOTE_ADDR', '127.0.0.1'),
                'socket_id': request.sid if hasattr(request, 'sid') else None
            }
        )
        
        # 🤖 BOT DETECTION RESPONSE - Handle blocked messages
        if result.get('blocked'):
            emit('message_blocked', {
                'error': result['reason'],
                'bot_analysis': result.get('bot_analysis', {}),
                'risk_level': result.get('bot_analysis', {}).get('risk_level', 'unknown'),
                'message_id': None,
                'timestamp': datetime.utcnow().isoformat()
            })
            return
        
        if not result.get('success'):
            emit('message_error', {'error': 'Failed to send message'})
            return
        
        # 🤖 BOT DETECTION LOGGING - Log suspicious activity
        bot_analysis = result.get('bot_analysis', {})
        if bot_analysis.get('risk_level') in ['medium', 'high']:
            emit('security_notice', {
                'message': f"Security notice: Message flagged as {bot_analysis.get('risk_level')} risk",
                'risk_level': bot_analysis.get('risk_level'),
                'flags': bot_analysis.get('flags', []),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Emit to all participants with data vampire info
        websocket_service.emit_new_message(
            user_id=current_user.id,
            chat_id=chat_id,
            message_data={
                'message_id': result['message_id'],
                'content': message_text,
                'timestamp': result['timestamp'],
                'sender_username': current_user.username,
                'data_harvested': result.get('data_harvesting', {}).get('data_value', 0) > 0,
                'user_data_value': result.get('data_harvesting', {}).get('data_value', 0),
                'vulnerability_score': result.get('data_harvesting', {}).get('vulnerability_score', 0),
                'bot_analysis': {
                    'risk_level': bot_analysis.get('risk_level', 'low'),
                    'clean_message': bot_analysis.get('risk_level', 'low') == 'low'
                }
            }
        )

    @socketio.on('typing')
    def handle_typing(data):
        """Handle typing indicators"""
        if not current_user.is_authenticated:
            return
            
        chat_id = data['chat_id']
        is_typing = data['is_typing']
        
        emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_typing': is_typing
        }, room=f"chat_{chat_id}", include_self=False)

    @socketio.on('voice_join_request')
    def handle_voice_join_request(data):
        """Handle request to join voice chat"""
        if not current_user.is_authenticated:
            emit('voice_error', {'message': 'Authentication required'})
            return
        
        try:
            from services.room_service import get_room_service
            room_service = get_room_service()
            
            room_id = data['room_id']
            result = room_service.join_voice_chat(current_user.id, room_id)
            
            if result['success']:
                # Join voice room for WebRTC signaling
                join_room(f"voice_{room_id}")
                
                # Notify others in voice chat
                emit('user_joined_voice', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'display_name': current_user.display_name or current_user.username,
                    'participant_count': result['voice_session']['participant_count']
                }, room=f"voice_{room_id}", include_self=False)
                
                # Send config to user
                emit('voice_joined', result)
            else:
                emit('voice_error', result)
                
        except Exception as e:
            emit('voice_error', {'message': str(e)})

    @socketio.on('voice_leave_request')
    def handle_voice_leave_request(data):
        """Handle request to leave voice chat"""
        if not current_user.is_authenticated:
            return
        
        try:
            from services.room_service import get_room_service
            room_service = get_room_service()
            
            room_id = data['room_id']
            result = room_service.leave_voice_chat(current_user.id, room_id)
            
            # Leave voice room
            leave_room(f"voice_{room_id}")
            
            # Notify others in voice chat
            emit('user_left_voice', {
                'user_id': current_user.id,
                'username': current_user.username,
                'session_ended': result.get('session_ended', False),
                'remaining_participants': result.get('remaining_participants', 0)
            }, room=f"voice_{room_id}")
            
            emit('voice_left', result)
            
        except Exception as e:
            emit('voice_error', {'message': str(e)})

    @socketio.on('webrtc_offer')
    def handle_webrtc_offer(data):
        """Handle WebRTC offer for voice chat"""
        if not current_user.is_authenticated:
            return
        
        room_id = data['room_id']
        target_user_id = data['target_user_id']
        offer = data['offer']
        
        # Send offer to specific user
        emit('webrtc_offer_received', {
            'from_user_id': current_user.id,
            'from_username': current_user.username,
            'from_display_name': current_user.display_name or current_user.username,
            'offer': offer,
            'room_id': room_id
        }, room=f"user_{target_user_id}")

    @socketio.on('webrtc_answer')
    def handle_webrtc_answer(data):
        """Handle WebRTC answer for voice chat"""
        if not current_user.is_authenticated:
            return
        
        room_id = data['room_id']
        target_user_id = data['target_user_id']
        answer = data['answer']
        
        # Send answer to specific user
        emit('webrtc_answer_received', {
            'from_user_id': current_user.id,
            'from_username': current_user.username,
            'from_display_name': current_user.display_name or current_user.username,
            'answer': answer,
            'room_id': room_id
        }, room=f"user_{target_user_id}")

    @socketio.on('webrtc_ice_candidate')
    def handle_webrtc_ice_candidate(data):
        """Handle WebRTC ICE candidate for voice chat"""
        if not current_user.is_authenticated:
            return
        
        room_id = data['room_id']
        target_user_id = data['target_user_id']
        candidate = data['candidate']
        
        # Send ICE candidate to specific user
        emit('webrtc_ice_candidate_received', {
            'from_user_id': current_user.id,
            'candidate': candidate,
            'room_id': room_id
        }, room=f"user_{target_user_id}")

    @socketio.on('voice_status_update')
    def handle_voice_status_update(data):
        """Handle voice status updates (speaking, muted, etc.)"""
        if not current_user.is_authenticated:
            return
        
        try:
            from services.room_service import get_room_service
            room_service = get_room_service()
            
            room_id = data['room_id']
            is_speaking = data.get('is_speaking')
            is_muted = data.get('is_muted')
            
            result = room_service.update_voice_status(
                current_user.id, room_id, is_speaking, is_muted
            )
            
            if result['success']:
                # Broadcast status update to all voice participants
                emit('voice_status_updated', {
                    'user_id': current_user.id,
                    'username': current_user.username,
                    'is_speaking': is_speaking,
                    'is_muted': is_muted
                }, room=f"voice_{room_id}", include_self=False)
            
        except Exception as e:
            emit('voice_error', {'message': str(e)})

    @socketio.on('request_voice_participants')
    def handle_request_voice_participants(data):
        """Handle request for current voice participants"""
        if not current_user.is_authenticated:
            return
        
        try:
            from services.room_service import get_room_service
            room_service = get_room_service()
            
            room_id = data['room_id']
            status = room_service.get_voice_session_status(room_id)
            
            emit('voice_participants_list', {
                'room_id': room_id,
                'participants': status.get('participants', []),
                'participant_count': status.get('participant_count', 0),
                'active': status.get('active', False)
            })
            
        except Exception as e:
            emit('voice_error', {'message': str(e)})