"""
Analytics Routes - SRIMI Microservice
Single Responsibility: Multiple tiny analytics endpoints
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

def register_analytics_routes(app: Flask, audit_logger) -> None:
    """Register tiny analytics routes with harmonious coordination"""
    
    # Register with endpoint coordinator
    from services.endpoint_coordinator import endpoint_coordinator
    endpoint_coordinator.register_endpoint('analytics_dashboard', lambda: 'analytics_data')
    
    @app.route('/api/admin/analytics/unified')
    @login_required
    @require_admin
    def get_unified_analytics():
        """Get unified analytics from coordinator"""
        try:
            unified_data = endpoint_coordinator.get_unified_dashboard_data()
            
            audit_logger.log_admin_action(
                current_user,
                'view_unified_analytics',
                'analytics',
                {'data_sources': ['analytics', 'warehouse']}
            )
            
            return jsonify(unified_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics')
    @login_required
    @require_admin
    def get_analytics_dashboard():
        """Get dashboard analytics data"""
        try:
            from services.analytics_orchestrator_service import analytics_orchestrator_service
            
            days = int(request.args.get('days', 30))
            data = analytics_orchestrator_service.get_dashboard_analytics(days=days)
            
            audit_logger.log_admin_action(
                current_user,
                'view_analytics_dashboard',
                'analytics',
                {'days': days}
            )
            
            return jsonify(data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics/overview')
    @login_required
    @require_admin
    def get_analytics_overview():
        """Get comprehensive analytics"""
        try:
            from services.analytics_orchestrator_service import analytics_orchestrator_service
            
            days = int(request.args.get('days', 30))
            data = analytics_orchestrator_service.get_comprehensive_analytics(days=days)
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics/users')
    @login_required
    @require_admin
    def get_user_analytics():
        """Get user analytics only"""
        try:
            from services.user_analytics_service import user_analytics_service
            
            days = int(request.args.get('days', 30))
            data = user_analytics_service.get_user_metrics(days=days)
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics/messages')
    @login_required
    @require_admin
    def get_message_analytics():
        """Get message analytics only"""
        try:
            from services.message_analytics_service import message_analytics_service
            
            days = int(request.args.get('days', 30))
            data = message_analytics_service.get_message_metrics(days=days)
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics/languages')
    @login_required
    @require_admin
    def get_language_analytics():
        """Get language analytics only"""
        try:
            from services.language_analytics_service import language_analytics_service
            
            data = language_analytics_service.get_language_distribution()
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/analytics/health')
    @login_required
    @require_admin
    def get_platform_health():
        """Get platform health only"""
        try:
            from services.platform_health_service import platform_health_service
            
            data = platform_health_service.get_health_status()
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/analytics/realtime')
    @login_required
    @require_admin
    def get_realtime_analytics():
        """Get real-time analytics for the dashboard"""
        try:
            from services.analytics_orchestrator_service import analytics_orchestrator_service
            
            data = analytics_orchestrator_service.get_realtime_metrics()
            
            return jsonify({'success': True, 'data': data})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500