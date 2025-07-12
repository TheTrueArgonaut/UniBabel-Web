"""
Admin Messaging Routes - SRIMI Microservice Routes
Single Responsibility: Core admin messaging and legal compliance endpoints
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

def register_admin_messaging_routes(app: Flask, audit_logger) -> None:
    """Register core admin messaging routes"""
    
    @app.route('/api/admin/message/send', methods=['POST'])
    @login_required
    @require_admin
    def send_admin_message():
        """Send direct message from admin to user"""
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
            
            # Send the message
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
                    'send_admin_message',
                    'admin_messaging',
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

    # Legal Compliance Routes
    @app.route('/api/legal/opt-out', methods=['POST'])
    @login_required
    def handle_opt_out():
        """Handle user opt-out request"""
        try:
            from services.legal_compliance_service import legal_compliance_service

            data = request.get_json()
            opt_out_type = data.get('opt_out_type')

            if not opt_out_type:
                return jsonify({'error': 'Opt-out type required'}), 400

            result = legal_compliance_service.handle_opt_out_request(
                user_id=current_user.id,
                opt_out_type=opt_out_type,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/legal/privacy-settings')
    @login_required
    def get_privacy_settings():
        """Get user's privacy settings"""
        try:
            from services.legal_compliance_service import legal_compliance_service

            result = legal_compliance_service.get_user_privacy_settings(current_user.id)

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/legal/privacy-command', methods=['POST'])
    @login_required
    def process_privacy_command():
        """Process privacy command from user"""
        try:
            from services.legal_compliance_service import legal_compliance_service

            data = request.get_json()
            command = data.get('command', '').strip()
            is_admin_conversation = data.get('is_admin_conversation', False)

            if not command:
                return jsonify({'error': 'Command required'}), 400

            result = legal_compliance_service.process_privacy_command(
                user_id=current_user.id,
                command=command,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown'),
                is_admin_conversation=is_admin_conversation
            )

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/legal/chat-logging-notice/<int:user_id>')
    @login_required
    def get_chat_logging_notice(user_id):
        """Get chat logging notice for user"""
        try:
            from services.legal_compliance_service import legal_compliance_service
            
            # Check if this is an admin conversation
            is_admin_conversation = request.args.get('admin_conversation', 'false').lower() == 'true'
            
            # Check if they want detailed information
            detailed = request.args.get('detailed', 'false').lower() == 'true'
            
            # Only allow users to get their own notice, or admins to get any notice
            if current_user.id != user_id and not getattr(current_user, 'is_data_vampire_admin', False):
                return jsonify({'error': 'Access denied'}), 403
            
            notice = legal_compliance_service.get_chat_logging_notice(user_id, is_admin_conversation, detailed)
            
            return jsonify(notice)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/legal/consent', methods=['POST'])
    @login_required
    def record_consent():
        """Record user consent"""
        try:
            from services.legal_compliance_service import legal_compliance_service
            
            data = request.get_json()
            consent_type = data.get('consent_type')
            consent_given = data.get('consent_given', False)
            
            if not consent_type:
                return jsonify({'error': 'Consent type required'}), 400
            
            result = legal_compliance_service.record_user_consent(
                user_id=current_user.id,
                consent_type=consent_type,
                consent_given=consent_given,
                ip_address=request.remote_addr or 'unknown',
                user_agent=request.headers.get('User-Agent', 'unknown')
            )
            
            # Log the consent action
            audit_logger.log_admin_action(
                current_user,
                'record_user_consent',
                'legal_compliance',
                {
                    'consent_type': consent_type,
                    'consent_given': consent_given
                }
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/legal/logging-notice-check/<int:room_id>')
    @login_required
    def check_logging_notice(room_id):
        """Check if logging notice should be shown for room"""
        try:
            from services.legal_compliance_service import legal_compliance_service
            
            result = legal_compliance_service.should_show_logging_notice(current_user.id, room_id)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/interaction-logs')
    @login_required
    @require_admin
    def get_interaction_logs():
        """Get admin interaction logs"""
        try:
            from services.admin_interaction_logger import admin_interaction_logger
            from datetime import datetime, timedelta
            
            # Get query parameters
            admin_user_id = request.args.get('admin_user_id', type=int)
            target_user_id = request.args.get('target_user_id', type=int)
            interaction_type = request.args.get('interaction_type')
            limit = int(request.args.get('limit', 50))
            
            # Date range
            days_back = int(request.args.get('days_back', 7))
            date_from = datetime.utcnow() - timedelta(days=days_back)
            
            # Get logs
            logs = admin_interaction_logger.get_interaction_logs(
                admin_user_id=admin_user_id,
                target_user_id=target_user_id,
                interaction_type=interaction_type,
                date_from=date_from,
                limit=limit
            )
            
            audit_logger.log_admin_action(
                current_user,
                'view_interaction_logs',
                'admin_audit',
                {
                    'filters': {
                        'admin_user_id': admin_user_id,
                        'target_user_id': target_user_id,
                        'interaction_type': interaction_type,
                        'days_back': days_back
                    },
                    'results_count': len(logs)
                }
            )
            
            return jsonify({
                'success': True,
                'logs': logs,
                'total_count': len(logs),
                'filters': {
                    'admin_user_id': admin_user_id,
                    'target_user_id': target_user_id,
                    'interaction_type': interaction_type,
                    'days_back': days_back
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500