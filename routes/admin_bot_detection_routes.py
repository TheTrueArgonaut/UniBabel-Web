"""
Admin Bot Detection Routes - SRIMI Microservice
Single Responsibility: Bot detection settings only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models import User, UserType

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_bot_detection_routes(app: Flask, audit_logger) -> None:
    """Register bot detection routes - under 80 lines"""
    
    @app.route('/admin/api/update-bot-detection', methods=['POST'])
    @require_admin
    def update_bot_detection():
        """Update bot detection settings"""
        try:
            from models.admin_models import AdminSettings, AdminActivityLog
            
            data = request.get_json()
            adult_sensitivity = data.get('adult_sensitivity', 5)
            teen_sensitivity = data.get('teen_sensitivity', 7)
            
            # Validate values
            if not (1 <= adult_sensitivity <= 10):
                return jsonify({'success': False, 'error': 'Adult sensitivity must be between 1-10'})
            if not (1 <= teen_sensitivity <= 10):
                return jsonify({'success': False, 'error': 'Teen sensitivity must be between 1-10'})
            
            # Calculate thresholds
            adult_threshold = 0.9 - (adult_sensitivity - 1) * 0.08
            teen_threshold = 0.65 - (teen_sensitivity - 1) * 0.05
            
            # Update settings
            AdminSettings.set_setting('bot_detection_adult_sensitivity', adult_sensitivity, 'integer', updated_by=current_user.id)
            AdminSettings.set_setting('bot_detection_adult_threshold', adult_threshold, 'float', updated_by=current_user.id)
            AdminSettings.set_setting('bot_detection_teen_sensitivity', teen_sensitivity, 'integer', updated_by=current_user.id)
            AdminSettings.set_setting('bot_detection_teen_threshold', teen_threshold, 'float', updated_by=current_user.id)
            
            # Log activity
            AdminActivityLog.log_activity(
                current_user.id,
                'bot_detection_update',
                f'Updated bot detection: Adult={adult_sensitivity}, Teen={teen_sensitivity}',
                'settings',
                'bot_detection',
                request.remote_addr,
                request.headers.get('User-Agent'),
                {
                    'adult_sensitivity': adult_sensitivity,
                    'teen_sensitivity': teen_sensitivity,
                    'adult_threshold': adult_threshold,
                    'teen_threshold': teen_threshold
                }
            )
            audit_logger.log_admin_action(current_user, 'update_bot_detection', 'bot_detection', 
                                        {'adult_sensitivity': adult_sensitivity, 'teen_sensitivity': teen_sensitivity, 
                                         'adult_threshold': adult_threshold, 'teen_threshold': teen_threshold})
            
            return jsonify({'success': True, 'message': 'Bot detection settings updated'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/admin/api/bot-detection-stats')
    @require_admin
    def bot_detection_stats():
        """Get bot detection statistics"""
        try:
            from services import get_bot_detection_service
            
            bot_service = get_bot_detection_service()
            stats = bot_service.get_detection_stats()
            
            # Get user counts by type
            adult_count = User.query.filter_by(user_type=UserType.ADULT).count()
            teen_count = User.query.filter_by(user_type=UserType.TEEN).count()
            
            return jsonify({
                'total_analyzed': stats.get('total_messages', 0),
                'total_blocked': stats.get('total_messages', 0) - stats.get('total_users', 0),
                'adult_users': adult_count,
                'teen_users': teen_count,
                'suspicious_users': stats.get('suspicious_users', 0),
                'suspicious_percentage': stats.get('suspicious_percentage', 0)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})