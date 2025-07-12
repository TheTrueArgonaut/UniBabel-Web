"""
API Routes - SRIMI Microservice Registry
Single Responsibility: Register all API micro-components
"""

from flask import Flask, jsonify, request, session
from auth import login_required
import logging

def register_api_routes(app: Flask) -> None:
    """Register all API micro-components"""
    
    # Import all micro-components
    from routes.api_babel_routes import register_api_babel_routes
    from routes.api_chat_routes import register_api_chat_routes
    from routes.api_room_routes import register_api_room_routes
    from routes.api_friend_group_routes import register_api_friend_group_routes
    
    # Register all micro-components
    register_api_babel_routes(app)
    register_api_chat_routes(app)
    register_api_room_routes(app)
    register_api_friend_group_routes(app)
    
    # Profile picture upload route
    @app.route('/api/profile-picture/upload', methods=['POST'])
    @login_required
    def upload_profile_picture():
        """Upload profile picture"""
        try:
            # For now, return a mock response
            # In a real implementation, you would save the file and update the user's profile
            return jsonify({
                'success': True,
                'message': 'Profile picture uploaded successfully',
                'profile_picture_url': '/static/img/default-profile.jpg'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger = logging.getLogger(__name__)
    logger.info("📡 API Routes registered")