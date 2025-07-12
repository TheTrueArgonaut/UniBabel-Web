"""
Chats API Routes - Microservice Endpoints
Single Responsibility: Chat management operations
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Chat, ChatParticipant, Message, User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_chats_api_routes(app):
    """Register chats API routes with /api/v1 prefix"""
    
    @app.route('/api/v1/chats/active', methods=['GET'])
    @login_required
    def get_active_chats():
        """Get user's active chat sessions"""
        try:
            # Get chats where user is a participant
            active_chats_query = db.session.query(
                Chat.id,
                Chat.name,
                Chat.chat_type,
                Chat.created_at,
                Chat.last_activity,
                ChatParticipant.joined_at,
                ChatParticipant.last_read_message_id
            ).join(
                ChatParticipant, ChatParticipant.chat_id == Chat.id
            ).filter(
                ChatParticipant.user_id == current_user.id,
                ChatParticipant.status == 'active'
            ).order_by(
                Chat.last_activity.desc()
            ).all()
            
            chats_list = []
            for chat_data in active_chats_query:
                # Get last message for preview
                last_message = Message.query.filter_by(
                    chat_id=chat_data.id
                ).order_by(Message.created_at.desc()).first()
                
                # Count unread messages
                unread_count = 0
                if chat_data.last_read_message_id:
                    unread_count = Message.query.filter(
                        Message.chat_id == chat_data.id,
                        Message.id > chat_data.last_read_message_id
                    ).count()
                else:
                    unread_count = Message.query.filter_by(chat_id=chat_data.id).count()
                
                # Get participant count
                participant_count = ChatParticipant.query.filter_by(
                    chat_id=chat_data.id,
                    status='active'
                ).count()
                
                # Determine chat type and name
                chat_type = 'room'
                chat_name = chat_data.name
                
                if chat_data.chat_type == 'direct':
                    chat_type = 'direct'
                    # For direct messages, get the other participant's name
                    other_participant = db.session.query(User.display_name, User.username).join(
                        ChatParticipant, ChatParticipant.user_id == User.id
                    ).filter(
                        ChatParticipant.chat_id == chat_data.id,
                        ChatParticipant.user_id != current_user.id,
                        ChatParticipant.status == 'active'
                    ).first()
                    
                    if other_participant:
                        chat_name = other_participant.display_name or other_participant.username
                elif participant_count <= 10:
                    chat_type = 'group'
                
                # Calculate last activity time
                last_active = 'Just now'
                if chat_data.last_activity:
                    time_diff = (datetime.utcnow() - chat_data.last_activity).total_seconds()
                    if time_diff < 60:
                        last_active = 'Just now'
                    elif time_diff < 3600:
                        last_active = f'{int(time_diff/60)} minutes ago'
                    elif time_diff < 86400:
                        last_active = f'{int(time_diff/3600)} hours ago'
                    else:
                        last_active = f'{int(time_diff/86400)} days ago'
                
                chats_list.append({
                    'id': chat_data.id,
                    'name': chat_name,
                    'type': chat_type,
                    'lastMessage': last_message.content if last_message else 'No messages yet',
                    'participantCount': participant_count,
                    'lastActive': last_active,
                    'unreadCount': unread_count
                })
            
            return jsonify({
                'success': True,
                'chats': chats_list,
                'count': len(chats_list)
            })
            
        except Exception as e:
            logger.error(f"Error getting active chats for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load active chats'
            }), 500
    
    @app.route('/api/v1/chats/<int:chat_id>/join', methods=['POST'])
    @login_required
    def join_chat(chat_id):
        """Join a chat room"""
        try:
            # Check if chat exists
            chat = Chat.query.get(chat_id)
            if not chat:
                return jsonify({
                    'success': False,
                    'error': 'Chat not found'
                }), 404
            
            # Check if user is already a participant
            existing_participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=current_user.id
            ).first()
            
            if existing_participant:
                if existing_participant.status == 'active':
                    return jsonify({
                        'success': False,
                        'error': 'Already in chat'
                    }), 400
                else:
                    # Reactivate participation
                    existing_participant.status = 'active'
                    existing_participant.joined_at = datetime.utcnow()
            else:
                # Create new participant
                new_participant = ChatParticipant(
                    chat_id=chat_id,
                    user_id=current_user.id,
                    status='active',
                    joined_at=datetime.utcnow()
                )
                db.session.add(new_participant)
            
            # Update chat activity
            chat.last_activity = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"User {current_user.id} joined chat {chat_id}")
            
            return jsonify({
                'success': True,
                'message': f'Joined {chat.name}',
                'chat_id': chat_id
            })
            
        except Exception as e:
            logger.error(f"Error joining chat {chat_id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to join chat'
            }), 500
    
    @app.route('/api/v1/chats/<int:chat_id>/leave', methods=['POST'])
    @login_required
    def leave_chat(chat_id):
        """Leave a chat room"""
        try:
            # Find participant record
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=current_user.id
            ).first()
            
            if not participant:
                return jsonify({
                    'success': False,
                    'error': 'Not in this chat'
                }), 404
            
            # Update status instead of deleting for history
            participant.status = 'left'
            participant.left_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"User {current_user.id} left chat {chat_id}")
            
            return jsonify({
                'success': True,
                'message': 'Left chat'
            })
            
        except Exception as e:
            logger.error(f"Error leaving chat {chat_id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to leave chat'
            }), 500
    
    @app.route('/api/v1/chats/<int:chat_id>/messages', methods=['GET'])
    @login_required
    def get_chat_messages(chat_id):
        """Get chat message history"""
        try:
            # Check if user is participant
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=current_user.id,
                status='active'
            ).first()
            
            if not participant:
                return jsonify({
                    'success': False,
                    'error': 'Not authorized to view this chat'
                }), 403
            
            # Get pagination parameters
            limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 messages
            offset = int(request.args.get('offset', 0))
            
            # Get messages
            messages = Message.query.filter_by(
                chat_id=chat_id
            ).order_by(
                Message.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            messages_list = []
            for msg in messages:
                # Get sender info
                sender = User.query.get(msg.sender_id)
                
                messages_list.append({
                    'id': msg.id,
                    'content': msg.content,
                    'sender': {
                        'id': sender.id,
                        'username': sender.username,
                        'display_name': sender.display_name
                    },
                    'created_at': msg.created_at.isoformat(),
                    'message_type': msg.message_type or 'text'
                })
            
            # Reverse to get chronological order
            messages_list.reverse()
            
            return jsonify({
                'success': True,
                'messages': messages_list,
                'count': len(messages_list),
                'has_more': len(messages) == limit
            })
            
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load messages'
            }), 500
    
    @app.route('/api/v1/chats/<int:chat_id>/messages', methods=['POST'])
    @login_required
    def send_message(chat_id):
        """Send a message to a chat"""
        try:
            # Check if user is participant
            participant = ChatParticipant.query.filter_by(
                chat_id=chat_id,
                user_id=current_user.id,
                status='active'
            ).first()
            
            if not participant:
                return jsonify({
                    'success': False,
                    'error': 'Not authorized to send messages to this chat'
                }), 403
            
            data = request.get_json()
            message_content = data.get('message', '').strip()
            
            if not message_content:
                return jsonify({
                    'success': False,
                    'error': 'Message content is required'
                }), 400
            
            # Create message
            message = Message(
                chat_id=chat_id,
                sender_id=current_user.id,
                content=message_content,
                message_type='text',
                created_at=datetime.utcnow()
            )
            
            db.session.add(message)
            
            # Update chat activity
            chat = Chat.query.get(chat_id)
            if chat:
                chat.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Message sent to chat {chat_id} by user {current_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Message sent',
                'message_id': message.id
            })
            
        except Exception as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500
    
    @app.route('/api/v1/chats', methods=['POST'])
    @login_required
    def create_chat():
        """Create a new chat room"""
        try:
            data = request.get_json()
            chat_name = data.get('name', '').strip()
            participants = data.get('participants', [])
            
            if not chat_name:
                return jsonify({
                    'success': False,
                    'error': 'Chat name is required'
                }), 400
            
            # Create chat
            chat = Chat(
                name=chat_name,
                chat_type='group' if len(participants) > 1 else 'direct',
                created_by=current_user.id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            
            db.session.add(chat)
            db.session.flush()  # Get chat ID
            
            # Add creator as participant
            creator_participant = ChatParticipant(
                chat_id=chat.id,
                user_id=current_user.id,
                status='active',
                joined_at=datetime.utcnow()
            )
            db.session.add(creator_participant)
            
            # Add other participants
            for participant_id in participants:
                if participant_id != current_user.id:
                    participant = ChatParticipant(
                        chat_id=chat.id,
                        user_id=participant_id,
                        status='active',
                        joined_at=datetime.utcnow()
                    )
                    db.session.add(participant)
            
            db.session.commit()
            
            logger.info(f"Chat created: {chat.id} by user {current_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Chat created',
                'chat_id': chat.id,
                'chat_name': chat.name
            })
            
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to create chat'
            }), 500