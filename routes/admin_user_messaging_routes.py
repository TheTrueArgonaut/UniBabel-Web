"""
Admin User Messaging Routes - SRIMI Microservice Routes
Single Responsibility: Admin-to-user messaging endpoints
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_user_messaging_routes(app: Flask, audit_logger) -> None:
    """Register admin-to-user messaging routes"""
    
    @app.route('/api/admin/send-message', methods=['POST'])
    @login_required
    @require_admin
    def send_message_to_user():
        """Send message from admin to user"""
        try:
            from services.admin_messaging_service import admin_messaging_service
            
            data = request.get_json()
            target_user_id = data.get('target_user_id')
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'admin_direct')
            
            if not target_user_id:
                return jsonify({'error': 'Target user ID required'}), 400
            
            if not content:
                return jsonify({'error': 'Message content required'}), 400
            
            if len(content) > 1000:
                return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
            
            # Send the message through translation pipeline
            result = admin_messaging_service.send_direct_message(
                admin_user_id=current_user.id,
                target_user_id=target_user_id,
                content=content,
                message_type=message_type,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'send_message_to_user',
                    'admin_user_messaging',
                    {
                        'target_user_id': target_user_id,
                        'message_type': message_type,
                        'content_length': len(content)
                    }
                )
                
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/conversation-history/<int:user_id>')
    @login_required
    @require_admin
    def get_user_conversation_history(user_id):
        """Get conversation history with a specific user"""
        try:
            from models import Room, RoomMember, Message, User, db
            
            # Find DM room between admin and user
            dm_room = db.session.query(Room).join(RoomMember).filter(
                Room.type == 'direct_message',
                RoomMember.user_id.in_([current_user.id, user_id])
            ).group_by(Room.id).having(
                db.func.count(RoomMember.user_id) == 2
            ).first()
            
            if not dm_room:
                return jsonify({
                    'success': True,
                    'messages': []
                })
            
            # Get messages from this room
            limit = int(request.args.get('limit', 50))
            messages = Message.query.filter_by(chat_id=dm_room.id).order_by(Message.timestamp.desc()).limit(limit).all()
            
            messages_data = []
            for msg in reversed(messages):  # Reverse to get chronological order
                sender = User.query.get(msg.sender_id)
                messages_data.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'sender_username': sender.username if sender else 'Unknown',
                    'content': msg.original_text,
                    'timestamp': msg.timestamp.isoformat()
                })
            
            audit_logger.log_admin_action(
                current_user,
                'view_user_conversation_history',
                'admin_user_messaging',
                {
                    'target_user_id': user_id,
                    'messages_count': len(messages_data)
                }
            )
            
            return jsonify({
                'success': True,
                'messages': messages_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/message/conversations')
    @login_required
    @require_admin
    def get_admin_user_conversations():
        """Get admin's direct message conversations with users"""
        try:
            from services.admin_messaging_service import admin_messaging_service
            
            limit = int(request.args.get('limit', 20))
            
            conversations = admin_messaging_service.get_admin_conversations(
                admin_user_id=current_user.id,
                limit=limit
            )
            
            audit_logger.log_admin_action(
                current_user,
                'get_admin_user_conversations',
                'admin_user_messaging',
                {'conversations_count': len(conversations)}
            )
            
            return jsonify({
                'success': True,
                'conversations': conversations,
                'total_count': len(conversations)
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/message/notification', methods=['POST'])
    @login_required
    @require_admin
    def send_system_notification():
        """Send system notification to user"""
        try:
            from services.admin_messaging_service import admin_messaging_service
            
            data = request.get_json()
            target_user_id = data.get('target_user_id')
            notification_type = data.get('notification_type', 'general')
            content = data.get('content', '').strip()
            
            if not target_user_id:
                return jsonify({'error': 'Target user ID required'}), 400
            
            if not content:
                return jsonify({'error': 'Notification content required'}), 400
            
            result = admin_messaging_service.send_system_notification(
                admin_user_id=current_user.id,
                target_user_id=target_user_id,
                notification_type=notification_type,
                content=content,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'send_system_notification',
                    'admin_user_messaging',
                    {
                        'target_user_id': target_user_id,
                        'notification_type': notification_type,
                        'content_length': len(content)
                    }
                )
                
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/message/warning', methods=['POST'])
    @login_required
    @require_admin
    def send_warning_message():
        """Send warning message to user"""
        try:
            from services.admin_messaging_service import admin_messaging_service
            
            data = request.get_json()
            target_user_id = data.get('target_user_id')
            warning_reason = data.get('warning_reason', '').strip()
            
            if not target_user_id:
                return jsonify({'error': 'Target user ID required'}), 400
            
            if not warning_reason:
                return jsonify({'error': 'Warning reason required'}), 400
            
            result = admin_messaging_service.send_warning_message(
                admin_user_id=current_user.id,
                target_user_id=target_user_id,
                warning_reason=warning_reason,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'send_warning_message',
                    'admin_user_messaging',
                    {
                        'target_user_id': target_user_id,
                        'warning_reason': warning_reason
                    }
                )
                
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500