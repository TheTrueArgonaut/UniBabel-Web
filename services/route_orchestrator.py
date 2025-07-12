"""
Route Orchestrator - SRIMI Microservice
Single Responsibility: Coordinate route registration flow
"""

from flask import Flask
from typing import List, Dict, Any
import logging

class RouteOrchestrator:
    """Micro-orchestrator for harmonious route registration"""
    
    def __init__(self):
        self.registered_routes = {}
        self.logger = logging.getLogger(__name__)
    
    def register_route_group(self, group_name: str, register_func, app: Flask, *args) -> None:
        """Register a group of routes with coordination"""
        try:
            register_func(app, *args)
            self.registered_routes[group_name] = {
                'status': 'registered',
                'function': register_func.__name__
            }
            self.logger.info(f"✅ {group_name} routes registered successfully")
        except Exception as e:
            self.registered_routes[group_name] = {
                'status': 'failed',
                'error': str(e)
            }
            self.logger.error(f"❌ {group_name} routes failed: {e}")
    
    def get_registration_status(self) -> Dict[str, Any]:
        """Get status of all registered route groups"""
        return {
            'total_groups': len(self.registered_routes),
            'successful': sum(1 for r in self.registered_routes.values() if r['status'] == 'registered'),
            'failed': sum(1 for r in self.registered_routes.values() if r['status'] == 'failed'),
            'groups': self.registered_routes
        }
    
    def orchestrate_admin_flow(self, app: Flask, audit_logger) -> None:
        """Orchestrate admin routes in harmony"""
        # Register core admin components
        from routes.admin_messaging_routes import register_admin_messaging_routes
        from routes.admin_chat_routes import register_admin_chat_routes
        from routes.admin_user_messaging_routes import register_admin_user_messaging_routes
        from routes.user_profile_routes import register_user_profile_routes
        from routes.translation_management_routes import register_translation_management_routes
        from routes.admin_dashboard_routes import register_admin_dashboard_routes
        from routes.admin_audit_routes import register_admin_audit_routes
        from routes.admin_user_management_routes import register_admin_user_management_routes
        from routes.admin_data_collection_routes import register_admin_data_collection_routes
        from routes.admin_bot_detection_routes import register_admin_bot_detection_routes
        from routes.admin_user_routes import register_admin_user_routes
        from routes.admin_revenue_routes import admin_revenue_bp
        from routes.admin_system_routes import register_admin_system_routes
        
        # Register in harmonious flow
        self.register_route_group('admin_messaging', register_admin_messaging_routes, app, audit_logger)
        self.register_route_group('admin_chat', register_admin_chat_routes, app, audit_logger)
        self.register_route_group('admin_user_messaging', register_admin_user_messaging_routes, app, audit_logger)
        self.register_route_group('user_profiles', register_user_profile_routes, app, audit_logger)
        self.register_route_group('translation_management', register_translation_management_routes, app, audit_logger)
        self.register_route_group('admin_dashboard', register_admin_dashboard_routes, app)
        self.register_route_group('admin_audit', register_admin_audit_routes, app, audit_logger)
        self.register_route_group('admin_user_management', register_admin_user_management_routes, app, audit_logger)
        self.register_route_group('admin_data_collection', register_admin_data_collection_routes, app, audit_logger)
        self.register_route_group('admin_bot_detection', register_admin_bot_detection_routes, app, audit_logger)
        self.register_route_group('admin_user_routes', register_admin_user_routes, app, audit_logger)
        self.register_route_group('admin_system_health', register_admin_system_routes, app)
        
        # Register revenue microservice
        app.register_blueprint(admin_revenue_bp)
        self.registered_routes['admin_revenue'] = {
            'status': 'registered',
            'function': 'admin_revenue_bp'
        }
    
    def orchestrate_analytics_flow(self, app: Flask, audit_logger) -> None:
        """Orchestrate analytics routes in harmony"""
        from routes.analytics_routes import register_analytics_routes
        from routes.data_warehouse_routes import register_data_warehouse_routes
        
        self.register_route_group('analytics', register_analytics_routes, app, audit_logger)
        self.register_route_group('data_warehouse', register_data_warehouse_routes, app, audit_logger)

# Singleton orchestrator
route_orchestrator = RouteOrchestrator()