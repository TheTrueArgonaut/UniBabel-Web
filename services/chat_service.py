"""
Chat Service
Handles chat creation, joining, and message operations
"""

import logging
from typing import Dict, List, Any, Optional
from flask import jsonify
from datetime import datetime
from models import db, Chat, ChatParticipant, Message, TranslatedMessage, User, UserType, RoomType, UserCommonPhrase


class ChatService:
    """
    Focused service for chat operations
    
    Single Responsibility: Chat management only
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def start_private_chat(self, current_user, recipient_username: str) -> Dict[str, Any]:
        """Start a private chat between two users"""
        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            return {'error': 'User not found', 'status': 404}
        
        # Check if chat already exists
        existing_chat = db.session.query(Chat).join(ChatParticipant).filter(
            Chat.is_group == False,
            ChatParticipant.user_id.in_([current_user.id, recipient.id])
        ).group_by(Chat.id).having(db.func.count(ChatParticipant.user_id) == 2).first()
        
        if existing_chat:
            return {'chat_id': existing_chat.id, 'status': 200}
        
        # Create new chat
        new_chat = Chat(
            name=f"{current_user.username} & {recipient.username}", 
            created_by=current_user.id
        )
        db.session.add(new_chat)
        db.session.flush()
        
        # Add participants
        participant1 = ChatParticipant(chat_id=new_chat.id, user_id=current_user.id)
        participant2 = ChatParticipant(chat_id=new_chat.id, user_id=recipient.id)
        db.session.add(participant1)
        db.session.add(participant2)
        db.session.commit()
        
        return {'chat_id': new_chat.id, 'status': 200}
    
    def get_chat_messages(self, current_user, chat_id: int) -> Dict[str, Any]:
        """Get messages for a chat"""
        # Verify user is in chat
        participant = ChatParticipant.query.filter_by(
            chat_id=chat_id, 
            user_id=current_user.id
        ).first()
        
        if not participant:
            return {'error': 'Unauthorized', 'status': 403}
        
        # Get messages with translations
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
        
        result = []
        for msg in messages:
            translation = TranslatedMessage.query.filter_by(
                message_id=msg.id,
                recipient_id=current_user.id
            ).first()
            
            message_data = msg.to_dict()
            if translation:
                message_data['translated_text'] = translation.translated_text
                message_data['target_language'] = translation.target_language
                message_data['confidence'] = translation.confidence
            
            result.append(message_data)
        
        return {'messages': result, 'status': 200}
    
    def get_user_chats(self, current_user) -> List[Chat]:
        """Get all chats for a user"""
        return db.session.query(Chat).join(ChatParticipant).filter(
            ChatParticipant.user_id == current_user.id
        ).all()
    
    def join_room_by_id(self, current_user, room_id: int) -> Dict[str, Any]:
        """Handle joining a room by ID"""
        room = Chat.query.get(room_id)
        if not room:
            return {'error': 'Room not found', 'status': 404}
        
        # Check if user is already a participant
        participant = ChatParticipant.query.filter_by(
            chat_id=room.id,
            user_id=current_user.id
        ).first()
        
        if not participant:
            can_join, reason = room.can_user_join(current_user)
            if can_join:
                participant = ChatParticipant(
                    chat_id=room.id,
                    user_id=current_user.id
                )
                db.session.add(participant)
                db.session.commit()
                return {'joined': True, 'room': room, 'status': 200}
            else:
                return {'error': reason, 'status': 403}
        
        return {'joined': False, 'room': room, 'status': 200}
    
    def verify_chat_access(self, current_user, chat_id: int) -> bool:
        """Verify if user has access to a chat"""
        participant = ChatParticipant.query.filter_by(
            chat_id=chat_id, 
            user_id=current_user.id
        ).first()
        return participant is not None
    
    def get_user_messages_sent(self, current_user) -> int:
        """Get count of messages sent by user today"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return Message.query.filter(
            Message.sender_id == current_user.id,
            Message.timestamp >= today
        ).count()
    
    def get_chat_by_id(self, current_user, chat_id: int) -> Dict[str, Any]:
        """Get chat by ID if user has access"""
        if not self.verify_chat_access(current_user, chat_id):
            return {'error': 'Unauthorized', 'status': 403}
        
        chat = Chat.query.get(chat_id)
        if not chat:
            return {'error': 'Chat not found', 'status': 404}
        
        return {'chat': chat, 'status': 200}
    
    def send_message(self, current_user, chat_id: int, message_text: str) -> Dict[str, Any]:
        """Send a message to a chat"""
        # Verify access
        if not self.verify_chat_access(current_user, chat_id):
            return {'error': 'Unauthorized', 'status': 403}
        
        # Create message
        message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            content=message_text,
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        
        return {'message': message, 'status': 200}
    
    def add_common_phrase(self, user_id: int, phrase: str):
        """Add or update a common phrase for the user"""
        # Check if phrase already exists
        existing = UserCommonPhrase.query.filter_by(
            user_id=user_id,
            phrase=phrase
        ).first()
        
        if existing:
            existing.usage_count += 1
            existing.last_used = datetime.utcnow()
        else:
            new_phrase = UserCommonPhrase(
                user_id=user_id,
                phrase=phrase,
                usage_count=1,
                last_used=datetime.utcnow()
            )
            db.session.add(new_phrase)
        
        db.session.commit()


# Global instance
_chat_service = ChatService()


def get_chat_service() -> ChatService:
    """Get the global chat service instance"""
    return _chat_service