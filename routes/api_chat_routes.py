"""
API Chat Routes - SRIMI Microservice
Single Responsibility: Chat functionality only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user

def register_api_chat_routes(app: Flask) -> None:
    """Register chat API routes - under 50 lines"""
    
    @app.route('/api/start-chat', methods=['POST'])
    @login_required
    def start_chat():
        """Start private chat with another user"""
        try:
            from services import get_chat_service
            
            data = request.get_json()
            result = get_chat_service().start_private_chat(
                current_user, 
                data.get('recipient_username')
            )
            
            return jsonify(result), result.get('status', 200)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/chat/<int:chat_id>/messages')
    @login_required
    def get_messages(chat_id):
        """Get messages from a chat"""
        try:
            from services import get_chat_service
            
            result = get_chat_service().get_chat_messages(current_user, chat_id)
            
            return jsonify(result), result.get('status', 200)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500