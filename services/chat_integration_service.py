"""
Chat Integration Service - SRIMI Microservice
Single Responsibility: Integrate admin messaging with regular chat
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ChatMessage:
    """Enhanced chat message with admin context"""
    message_id: int
    content: str
    sender_id: int
    sender_username: str
    room_id: int
    timestamp: str
    is_admin_message: bool
    is_system_message: bool
    message_type: str
    admin_badge: Optional[str] = None

class ChatIntegrationService:
    """Micro-service for integrating admin messaging with regular chat"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_user_rooms_with_admin_context(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's rooms including admin DM rooms"""
        try:
            from models import Room, RoomMember, User, Message
            
            # Get all rooms user is member of
            user_rooms = []
            
            rooms = Room.query.join(RoomMember).filter(
                RoomMember.user_id == user_id
            ).all()
            
            for room in rooms:
                # Get last message
                last_message = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp.desc()).first()
                
                room_data = {
                    'id': room.id,
                    'name': room.name,
                    'type': room.type,
                    'last_activity': room.last_activity.isoformat() if room.last_activity else None,
                    'is_admin_room': room.type == 'direct_message' and self._is_admin_room(room.id, user_id),
                    'last_message': {
                        'content': last_message.content if last_message else None,
                        'timestamp': last_message.timestamp.isoformat() if last_message else None,
                        'sender_id': last_message.sender_id if last_message else None,
                        'is_admin_message': self._is_admin_message(last_message) if last_message else False
                    } if last_message else None
                }
                
                # If it's an admin DM room, get the admin user info
                if room_data['is_admin_room']:
                    admin_user = self._get_admin_user_in_room(room.id, user_id)
                    if admin_user:
                        room_data['admin_user'] = {
                            'id': admin_user.id,
                            'username': admin_user.username,
                            'display_name': getattr(admin_user, 'display_name', None)
                        }
                        room_data['name'] = f"Admin: {admin_user.username}"
                
                user_rooms.append(room_data)
            
            return user_rooms
            
        except Exception as e:
            self.logger.error(f"Error getting user rooms with admin context: {str(e)}")
            return []
    
    def get_room_messages_with_admin_context(self, room_id: int, user_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get room messages with admin context"""
        try:
            from models import Room, RoomMember, Message, User
            
            # Verify user has access to room
            room_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not room_member:
                return {
                    'success': False,
                    'error': 'Access denied to this room'
                }
            
            # Get room info
            room = Room.query.get(room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found'
                }
            
            # Get messages
            messages = Message.query.filter_by(room_id=room_id).order_by(Message.timestamp.desc()).limit(limit).all()
            
            # Format messages with admin context
            formatted_messages = []
            for msg in reversed(messages):  # Chronological order
                sender = User.query.get(msg.sender_id)
                is_admin = getattr(sender, 'is_data_vampire_admin', False) if sender else False
                
                formatted_message = {
                    'id': msg.id,
                    'content': msg.content,
                    'sender_id': msg.sender_id,
                    'sender_username': sender.username if sender else 'Unknown',
                    'timestamp': msg.timestamp.isoformat(),
                    'is_admin_message': is_admin,
                    'is_system_message': msg.is_system_message,
                    'message_type': getattr(msg, 'message_type', 'normal'),
                    'admin_badge': self._get_admin_badge(msg, sender) if is_admin else None
                }
                
                formatted_messages.append(formatted_message)
            
            return {
                'success': True,
                'room_id': room_id,
                'room_name': room.name,
                'room_type': room.type,
                'is_admin_room': room.type == 'direct_message' and self._is_admin_room(room_id, user_id),
                'messages': formatted_messages,
                'total_messages': len(formatted_messages)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting room messages with admin context: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_admin_room(self, room_id: int, user_id: int) -> bool:
        """Check if room is an admin DM room"""
        try:
            from models import RoomMember, User
            
            # Get other members in the room
            other_members = RoomMember.query.filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id != user_id
            ).all()
            
            # Check if any other member is an admin
            for member in other_members:
                user = User.query.get(member.user_id)
                if user and getattr(user, 'is_data_vampire_admin', False):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking if admin room: {str(e)}")
            return False
    
    def _get_admin_user_in_room(self, room_id: int, user_id: int) -> Optional[object]:
        """Get the admin user in a DM room"""
        try:
            from models import RoomMember, User
            
            other_members = RoomMember.query.filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id != user_id
            ).all()
            
            for member in other_members:
                user = User.query.get(member.user_id)
                if user and getattr(user, 'is_data_vampire_admin', False):
                    return user
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting admin user in room: {str(e)}")
            return None
    
    def _is_admin_message(self, message) -> bool:
        """Check if message is from an admin"""
        try:
            from models import User
            
            sender = User.query.get(message.sender_id)
            return getattr(sender, 'is_data_vampire_admin', False) if sender else False
            
        except Exception as e:
            self.logger.error(f"Error checking if admin message: {str(e)}")
            return False
    
    def _get_admin_badge(self, message, sender) -> str:
        """Get admin badge for message"""
        try:
            message_type = getattr(message, 'message_type', 'normal')
            
            if message_type == 'system_notification':
                return '🔔 System'
            elif message_type == 'admin_warning':
                return '⚠️ Warning'
            elif message_type == 'admin_direct':
                return '👑 Admin'
            elif message.is_system_message:
                return '🤖 System'
            else:
                return '👑 Admin'
                
        except Exception as e:
            self.logger.error(f"Error getting admin badge: {str(e)}")
            return '👑 Admin'
    
    def can_admin_join_room(self, admin_user_id: int, room_id: int) -> Dict[str, Any]:
        """Check if admin can join a room and join if possible"""
        try:
            from models import Room, RoomMember, User, db
            
            # Get admin user
            admin_user = User.query.get(admin_user_id)
            if not admin_user or not getattr(admin_user, 'is_data_vampire_admin', False):
                return {
                    'success': False,
                    'error': 'Admin privileges required'
                }
            
            # Get room
            room = Room.query.get(room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found'
                }
            
            # Check if already a member
            existing_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=admin_user_id
            ).first()
            
            if existing_member:
                return {
                    'success': True,
                    'message': 'Already a member of this room',
                    'room_id': room_id,
                    'role': existing_member.role
                }
            
            # Join the room (admins can join any room)
            new_member = RoomMember(
                room_id=room_id,
                user_id=admin_user_id,
                role='admin',
                joined_at=datetime.utcnow()
            )
            
            db.session.add(new_member)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Successfully joined room',
                'room_id': room_id,
                'role': 'admin'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking admin room access: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
chat_integration_service = ChatIntegrationService()