"""
Admin User Management Routes - SRIMI Microservice
Single Responsibility: User ban/unban/management only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from models import User, db

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_user_management_routes(app: Flask, audit_logger) -> None:
    """Register user management routes - under 100 lines"""
    
    @app.route('/api/admin/user/<int:user_id>/ban', methods=['POST'])
    @login_required
    @require_admin
    def admin_ban_user(user_id):
        """Ban a user"""
        try:
            from models.admin_models import AdminActivityLog
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.is_data_vampire_admin:
                return jsonify({'error': 'Cannot ban admin users'}), 403
            
            data = request.get_json()
            reason = data.get('reason', 'No reason provided')
            
            # Ban the user
            user.is_blocked = True
            user.block_reason = reason
            user.blocked_at = datetime.utcnow()
            user.blocked_by = current_user.id
            user.is_online = False
            
            db.session.commit()
            
            # Log the action
            AdminActivityLog.log_activity(
                current_user.id,
                'user_ban',
                f'Banned user {user.username} (ID: {user_id})',
                'user_management',
                f'user_{user_id}',
                request.remote_addr,
                request.headers.get('User-Agent'),
                extra_data={
                    'banned_user_id': user_id,
                    'banned_username': user.username,
                    'ban_reason': reason
                }
            )
            audit_logger.log_admin_action(current_user, 'admin_ban_user', 'user_ban', 
                                        {'banned_user_id': user_id, 'banned_username': user.username, 'ban_reason': reason})
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} banned successfully',
                'reason': reason
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/user/<int:user_id>/unban', methods=['POST'])
    @login_required
    @require_admin
    def admin_unban_user(user_id):
        """Unban a user"""
        try:
            from models.admin_models import AdminActivityLog
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.is_blocked:
                return jsonify({'error': 'User is not banned'}), 400
            
            # Unban the user
            user.is_blocked = False
            user.block_reason = None
            user.blocked_at = None
            user.blocked_by = None
            
            db.session.commit()
            
            # Log the action
            AdminActivityLog.log_activity(
                current_user.id,
                'user_unban',
                f'Unbanned user {user.username} (ID: {user_id})',
                'user_management',
                f'user_{user_id}',
                request.remote_addr,
                request.headers.get('User-Agent'),
                extra_data={
                    'unbanned_user_id': user_id,
                    'unbanned_username': user.username
                }
            )
            audit_logger.log_admin_action(current_user, 'admin_unban_user', 'user_unban', 
                                        {'unbanned_user_id': user_id, 'unbanned_username': user.username})
            
            return jsonify({
                'success': True,
                'message': f'User {user.username} unbanned successfully'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500