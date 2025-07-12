"""
Admin Routes - SRIMI Microservice Registry
Single Responsibility: Register all admin micro-components
"""

from flask import Flask

def register_admin_routes(app: Flask) -> None:
    """Register all admin micro-components - under 30 lines"""
    
    # Import core service first
    from routes.admin_core_service import audit_logger
    
    # Import and use the route orchestrator
    from services.route_orchestrator import route_orchestrator
    
    # Orchestrate admin routes in harmonious flow
    route_orchestrator.orchestrate_admin_flow(app, audit_logger)
    
    # Orchestrate analytics flow (includes data warehouse)
    route_orchestrator.orchestrate_analytics_flow(app, audit_logger)
    
    # Log the harmonious orchestration
    status = route_orchestrator.get_registration_status()
    print(f"🎵 Admin orchestration complete: {status['successful']}/{status['total_groups']} groups registered")