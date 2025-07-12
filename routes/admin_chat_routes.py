"""
Admin Chat Routes - SRIMI Microservice Routes
Single Responsibility: Admin chat communication endpoints
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

def register_admin_chat_routes(app: Flask, audit_logger) -> None:
    """Register admin chat routes"""
    
    @app.route('/api/admin/online-admins')
    @login_required
    @require_admin
    def get_online_admins():
        """Get list of online admins"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            admins = admin_chat_service.get_online_admins()
            
            return jsonify({
                'success': True,
                'admins': admins
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/all-admins')
    @login_required
    @require_admin
    def get_all_admins():
        """Get list of all admins"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            admins = admin_chat_service.get_all_admins(exclude_user_id=current_user.id)
            
            return jsonify({
                'success': True,
                'admins': admins
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/send-group-message', methods=['POST'])
    @login_required
    @require_admin
    def send_group_message():
        """Send message to admin group chat"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            data = request.get_json()
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'admin_group_chat')
            
            if not content:
                return jsonify({'error': 'Message content required'}), 400
            
            if len(content) > 1000:
                return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
            
            result = admin_chat_service.send_group_message(
                sender_id=current_user.id,
                content=content,
                message_type=message_type
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'send_group_message',
                    'admin_chat',
                    {
                        'message_type': message_type,
                        'content_length': len(content)
                    }
                )
                
                return jsonify(result), 200
            else:
                return jsonify(result), 400
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/admin-messages')
    @login_required
    @require_admin
    def get_admin_group_messages():
        """Get admin group chat messages"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            limit = int(request.args.get('limit', 50))
            
            messages = admin_chat_service.get_group_messages(limit=limit)
            
            return jsonify({
                'success': True,
                'messages': messages
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/dm-conversations')
    @login_required
    @require_admin
    def get_dm_conversations():
        """Get direct message conversations for current admin"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            conversations = admin_chat_service.get_direct_conversations(current_user.id)
            
            return jsonify({
                'success': True,
                'conversations': conversations
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/dm-messages/<int:admin_id>')
    @login_required
    @require_admin
    def get_direct_messages_with_admin(admin_id):
        """Get direct messages with specific admin"""
        try:
            from services.admin_chat_service import admin_chat_service
            
            limit = int(request.args.get('limit', 50))
            
            messages = admin_chat_service.get_direct_messages(
                admin_id=current_user.id,
                target_admin_id=admin_id,
                limit=limit
            )
            
            return jsonify({
                'success': True,
                'messages': messages
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/send-direct-message', methods=['POST'])
    @login_required
    @require_admin
    def send_direct_admin_message():
        """Send direct message to another admin"""
        try:
            from services.admin_messaging_service import admin_messaging_service
            
            data = request.get_json()
            target_admin_id = data.get('target_admin_id')
            content = data.get('content', '').strip()
            message_type = data.get('message_type', 'admin_direct_message')
            
            if not target_admin_id:
                return jsonify({'error': 'Target admin ID required'}), 400
            
            if not content:
                return jsonify({'error': 'Message content required'}), 400
            
            if len(content) > 1000:
                return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
            
            # Prevent self-messaging
            if target_admin_id == current_user.id:
                return jsonify({'error': 'Cannot send message to yourself'}), 400
            
            # Use admin messaging service for direct messages (supports translation)
            result = admin_messaging_service.send_direct_message(
                admin_user_id=current_user.id,
                target_user_id=target_admin_id,
                content=content,
                message_type=message_type,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )
            
            if result['success']:
                audit_logger.log_admin_action(
                    current_user,
                    'send_direct_admin_message',
                    'admin_chat',
                    {
                        'target_admin_id': target_admin_id,
                        'message_type': message_type,
                        'content_length': len(content)
                    }
                )
                
                return jsonify(result), 200
            else:
                return jsonify(result), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500