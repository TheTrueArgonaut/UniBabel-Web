"""
Admin Data Collection Routes - SRIMI Microservice
Single Responsibility: Data collection toggle/management only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
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

def register_admin_data_collection_routes(app: Flask, audit_logger) -> None:
    """Register data collection routes - under 50 lines"""
    
    @app.route('/api/admin/user/<int:user_id>/toggle-data-collection', methods=['POST'])
    @login_required
    @require_admin
    def admin_toggle_data_collection(user_id):
        """Toggle data collection for a specific user"""
        try:
            from models.admin_models import AdminActivityLog
            
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Toggle data collection block
            user.data_collection_blocked = not getattr(user, 'data_collection_blocked', False)
            
            db.session.commit()
            
            status = 'blocked' if user.data_collection_blocked else 'enabled'
            
            # Log the action
            AdminActivityLog.log_activity(
                current_user.id,
                'data_collection_toggle',
                f'Data collection {status} for user {user.username} (ID: {user_id})',
                'user_management',
                f'user_{user_id}',
                request.remote_addr,
                request.headers.get('User-Agent'),
                extra_data={
                    'user_id': user_id,
                    'username': user.username,
                    'data_collection_status': status
                }
            )
            audit_logger.log_admin_action(current_user, 'admin_toggle_data_collection', 'data_collection', 
                                        {'user_id': user_id, 'username': user.username, 'data_collection_status': status})
            
            return jsonify({
                'success': True,
                'message': f'Data collection {status} for user {user.username}',
                'data_collection_blocked': user.data_collection_blocked
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500