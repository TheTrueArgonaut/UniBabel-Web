# Auth Routes - SRIMI: Single Responsibility, Micro, Interface
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

def register_auth_routes(app: Flask) -> None:
    """Register authentication related routes"""
    
    @app.route('/')
    def index():
        """Landing page with auth redirect"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard - isolated responsibility"""
        from services import get_chat_service, get_message_service
        
        # Inject dependencies
        chat_service = get_chat_service()
        message_service = get_message_service()
        
        # Single responsibility: dashboard data
        user_chats = chat_service.get_user_chats(current_user)
        messages_sent = len(message_service.get_user_messages_sent(current_user))
        user_data_summary = message_service.get_user_data_summary(current_user.id)
        
        dashboard_data = {
            'total_chats': len(user_chats),
            'messages_sent': messages_sent,
            'data_value': f"${user_data_summary['total_market_value']:.2f}" if user_data_summary else f"${messages_sent * 50}",
            'account_age_days': (datetime.utcnow() - current_user.created_at).days if current_user.created_at else 0
        }
        
        return render_template('dashboard.html', 
                             user=current_user, 
                             chats=user_chats,
                             stats=dashboard_data)

    @app.route('/settings')
    @login_required
    def settings():
        """Settings page"""
        return render_template('settings.html', user=current_user)

    @app.route('/verify-age')
    @login_required
    def verify_age_page():
        """Age verification page"""
        return render_template('verify_age.html')

    @app.route('/pending-parental-consent')
    def pending_parental_consent():
        """Page shown to minors waiting for parental consent"""
        return render_template('pending_parental_consent.html')

    @app.route('/check-username', methods=['POST'])
    def check_username():
        """Check if username is available"""
        try:
            data = request.get_json()
            username = data.get('username', '')
            
            from services.registration_service import get_registration_service
            registration_service = get_registration_service()
            
            result = registration_service.check_username_availability(username)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'available': False,
                'error': str(e)
            }), 500

    @app.route('/check-display-name', methods=['POST'])
    def check_display_name():
        """Check if display name is available"""
        try:
            data = request.get_json()
            display_name = data.get('displayName', '')
            
            # For now, just return available since display names don't need to be unique
            return jsonify({
                'available': True
            })
            
        except Exception as e:
            return jsonify({
                'available': False,
                'error': str(e)
            }), 500

    @app.route('/privacy-policy')
    def privacy_policy():
        """Privacy policy page"""
        return render_template('privacy_policy.html')

    @app.route('/terms-of-service')
    def terms_of_service():
        """Terms of service page"""
        return render_template('terms_of_service.html')

    @app.route('/premium')
    @login_required
    def premium():
        """Premium subscription page"""
        return render_template('premium.html')