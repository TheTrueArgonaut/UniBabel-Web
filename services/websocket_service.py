"""
WebSocket Service
Handles real-time messaging and WebSocket events
"""

import logging
from datetime import datetime
from typing import Dict, Any
from flask_socketio import emit, join_room, leave_room
from models import db, ChatParticipant, User
from .message_service import get_message_service
from .chat_service import get_chat_service


class WebSocketService:
    """
    Focused service for WebSocket operations
    
    Single Responsibility: Real-time messaging only
    """
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.logger = logging.getLogger(__name__)
        self.message_service = get_message_service()
        self.chat_service = get_chat_service()
        
        # Register event handlers
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('join_chat', self.handle_join_chat)
        self.socketio.on_event('leave_chat', self.handle_leave_chat)
        self.socketio.on_event('send_message', self.handle_send_message)
        self.socketio.on_event('typing', self.handle_typing)
    
    def handle_connect(self):
        """Handle user connection"""
        from flask_login import current_user
        
        if current_user.is_authenticated:
            current_user.is_online = True
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            join_room(f"user_{current_user.id}")
            self.logger.info(f"User {current_user.username} connected")
    
    def handle_disconnect(self):
        """Handle user disconnection"""
        from flask_login import current_user
        
        if current_user.is_authenticated:
            current_user.is_online = False
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            self.logger.info(f"User {current_user.username} disconnected")
    
    def handle_join_chat(self, data):
        """Handle joining a chat room"""
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        chat_id = data['chat_id']
        
        # Verify user access
        if self.chat_service.verify_chat_access(current_user, chat_id):
            join_room(f"chat_{chat_id}")
            emit('joined_chat', {'chat_id': chat_id})
        else:
            emit('error', {'message': 'Unauthorized'})
    
    def handle_leave_chat(self, data):
        """Handle leaving a chat room"""
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return
        
        chat_id = data['chat_id']
        leave_room(f"chat_{chat_id}")
    
    def handle_send_message(self, data):
        """Handle sending a message"""
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            emit('message_error', {'error': 'Authentication required'})
            return
        
        chat_id = data['chat_id']
        message_text = data['message']
        
        # Check message limits
        limit_check = self.message_service.check_message_limits(current_user)
        if not limit_check['can_send']:
            emit('message_error', limit_check)
            return
        
        # Verify chat access
        if not self.chat_service.verify_chat_access(current_user, chat_id):
            emit('message_error', {'error': 'Unauthorized'})
            return
        
        # Create message
        message = self.message_service.create_message(current_user, chat_id, message_text)
        
        # Translate for participants
        translations = self.message_service.translate_for_participants(current_user, message)
        
        # Send to all participants
        self._broadcast_message(message, translations)
    
    def handle_typing(self, data):
        """Handle typing indicators"""
        from flask_login import current_user
        
        if not current_user.is_authenticated:
            return
        
        chat_id = data['chat_id']
        is_typing = data['is_typing']
        
        self.socketio.emit('user_typing', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_typing': is_typing
        }, room=f"chat_{chat_id}", include_self=False)
    
    def _broadcast_message(self, message, translations):
        """Broadcast message to all participants"""
        from flask_login import current_user
        
        participants = ChatParticipant.query.filter_by(chat_id=message.chat_id).all()
        
        for participant in participants:
            if participant.user_id == current_user.id:
                # Send original to sender
                message_data = self.message_service.get_message_data_for_user(
                    message, participant.user_id, is_sender=True
                )
            else:
                # Send translated to recipient
                message_data = self.message_service.get_message_data_for_user(
                    message, participant.user_id, is_sender=False
                )
            
            self.socketio.emit('new_message', message_data, room=f"user_{participant.user_id}")
    
    def emit_user_joined(self, user_id: int, username: str, room_id: int):
        """Emit user joined event"""
        self.socketio.emit('user_joined', {
            'user_id': user_id,
            'username': username,
            'room_id': room_id
        }, room=f"chat_{room_id}")
    
    def emit_new_message(self, user_id: int, chat_id: int, message_data: Dict[str, Any]):
        """Emit new message event with data vampire information"""
        
        # Enhanced message data includes data vampire info
        enhanced_message = {
            'message_id': message_data.get('message_id'),
            'chat_id': chat_id,
            'sender_id': user_id,
            'sender_username': message_data.get('sender_username'),
            'content': message_data.get('content'),
            'timestamp': message_data.get('timestamp'),
            'data_harvested': message_data.get('data_harvested', False),
            'user_data_value': message_data.get('user_data_value', 0),
            'vulnerability_score': message_data.get('vulnerability_score', 0)
        }
        
        # Emit to all participants in the chat
        self.socketio.emit('new_message', enhanced_message, room=f"chat_{chat_id}")
        
        # Also emit data vampire analytics to sender
        if message_data.get('data_harvested'):
            self.socketio.emit('data_vampire_update', {
                'user_id': user_id,
                'new_data_value': message_data.get('user_data_value', 0),
                'vulnerability_score': message_data.get('vulnerability_score', 0),
                'harvest_timestamp': message_data.get('timestamp')
            }, room=f"user_{user_id}")


# Global instance
_websocket_service = None


def get_websocket_service() -> WebSocketService:
    """Get the global WebSocket service instance"""
    return _websocket_service


def initialize_websocket_service(socketio) -> WebSocketService:
    """Initialize the WebSocket service"""
    global _websocket_service
    _websocket_service = WebSocketService(socketio)
    return _websocket_service