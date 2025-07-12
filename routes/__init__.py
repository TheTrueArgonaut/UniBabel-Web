# Routes package - SRIMI compliant micro-components with harmonious orchestration
from flask import Flask

def register_all_routes(app: Flask) -> None:
    """Register all route blueprints with harmonious orchestrated flow"""
    from .auth_routes import register_auth_routes
    from .api_routes import register_api_routes
    from .chat_routes import register_chat_routes
    from .admin_routes import register_admin_routes
    from .websocket_routes import register_websocket_routes
    from .friends_api import register_friends_api_routes
    from .chats_api import register_chats_api_routes
    from .activity_api import register_activity_api_routes
    from .users_api import register_users_api_routes
    
    # Initialize audit logger (needed for analytics)
    from services.admin_interaction_logger import admin_interaction_logger
    
    # Register core routes
    register_auth_routes(app)
    register_api_routes(app)
    register_chat_routes(app)
    register_admin_routes(app)
    register_websocket_routes(app)
    register_friends_api_routes(app)
    register_chats_api_routes(app)
    register_activity_api_routes(app)
    register_users_api_routes(app)