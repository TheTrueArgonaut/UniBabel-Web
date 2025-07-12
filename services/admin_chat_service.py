"""
Admin Chat Service - SRIMI Microservice
Single Responsibility: Admin-to-admin communication
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

class AdminChatService:
    """Micro-service for admin chat functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._orchestrator = None
        
    @property
    def orchestrator(self):
        """Lazy load orchestrator to avoid circular imports"""
        if self._orchestrator is None:
            from .translation_orchestrator import get_orchestrator
            self._orchestrator = get_orchestrator()
        return self._orchestrator
    
    def get_online_admins(self) -> List[Dict[str, Any]]:
        """Get list of online admins"""
        try:
            from models import User
            
            # Get admins who were active in the last 10 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)
            
            online_admins = User.query.filter(
                User.is_data_vampire_admin == True,
                User.last_seen > cutoff_time
            ).all()
            
            return [
                {
                    'id': admin.id,
                    'username': admin.username,
                    'language': getattr(admin, 'preferred_language', 'en'),
                    'online': True,
                    'last_seen': admin.last_seen.isoformat() if admin.last_seen else None
                }
                for admin in online_admins
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting online admins: {str(e)}")
            return []
    
    def get_all_admins(self, exclude_user_id: int = None) -> List[Dict[str, Any]]:
        """Get list of all admins"""
        try:
            from models import User
            
            # Get all admins
            query = User.query.filter(User.is_data_vampire_admin == True)
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
            
            all_admins = query.all()
            
            # Check online status (active in last 10 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)
            
            return [
                {
                    'id': admin.id,
                    'username': admin.username,
                    'language': getattr(admin, 'preferred_language', 'en'),
                    'online': admin.last_seen and admin.last_seen > cutoff_time,
                    'last_seen': admin.last_seen.isoformat() if admin.last_seen else None
                }
                for admin in all_admins
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting all admins: {str(e)}")
            return []
    
    def send_group_message(self, sender_id: int, content: str, message_type: str = 'admin_group_chat') -> Dict[str, Any]:
        """Send message to admin group chat"""
        try:
            from models import Message, db
            
            # Create group message in admin chat room (room_id = 1 for admin group)
            admin_group_room_id = 1
            
            # Create the message with translation pipeline integration
            message = Message(
                chat_id=admin_group_room_id,
                sender_id=sender_id,
                original_text=content,
                original_language='AUTO',
                timestamp=datetime.utcnow(),
                is_system_message=(message_type == 'admin_system_alert'),
                message_type=message_type
            )
            
            db.session.add(message)
            db.session.flush()
            
            # Route through translation pipeline for data harvesting
            pipeline_result = self._process_admin_message_through_pipeline(
                sender_id=sender_id,
                message_text=content,
                message_id=message.id,
                chat_id=admin_group_room_id,
                communication_type='admin_group_chat'
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'message_id': message.id,
                'timestamp': message.timestamp.isoformat(),
                'pipeline_processed': pipeline_result.get('pipeline_processed', False)
            }
            
        except Exception as e:
            self.logger.error(f"Error sending group message: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_group_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get admin group chat messages"""
        try:
            from models import Message, User
            
            # Get messages from admin group chat room (room_id = 1)
            admin_group_room_id = 1
            
            messages = Message.query.filter_by(chat_id=admin_group_room_id).order_by(Message.timestamp.desc()).limit(limit).all()
            
            messages_data = []
            for msg in reversed(messages):  # Reverse to get chronological order
                sender = User.query.get(msg.sender_id)
                messages_data.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'sender_username': sender.username if sender else 'Unknown',
                    'sender_language': getattr(sender, 'preferred_language', 'en') if sender else 'en',
                    'content': msg.original_text,
                    'message_type': msg.message_type,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_system_message': msg.is_system_message
                })
            
            return messages_data
            
        except Exception as e:
            self.logger.error(f"Error getting group messages: {str(e)}")
            return []
    
    def get_direct_conversations(self, admin_id: int) -> List[Dict[str, Any]]:
        """Get direct message conversations for admin"""
        try:
            from models import Room, RoomMember, Message, User, db
            
            # Get rooms where admin is a member and room type is direct_message
            admin_rooms = db.session.query(Room).join(RoomMember).filter(
                RoomMember.user_id == admin_id,
                Room.type == 'direct_message'
            ).order_by(Room.last_activity.desc()).all()
            
            conversations = []
            for room in admin_rooms:
                # Get the other admin in the conversation
                other_member = db.session.query(RoomMember).join(User).filter(
                    RoomMember.room_id == room.id,
                    RoomMember.user_id != admin_id,
                    User.is_data_vampire_admin == True  # Only include other admins
                ).first()
                
                if other_member:
                    # Get last message
                    last_message = Message.query.filter_by(chat_id=room.id).order_by(Message.timestamp.desc()).first()
                    
                    conversations.append({
                        'room_id': room.id,
                        'admin_id': other_member.user_id,
                        'username': other_member.user.username,
                        'language': getattr(other_member.user, 'preferred_language', 'en'),
                        'last_message': last_message.original_text if last_message else None,
                        'last_activity': room.last_activity.isoformat() if room.last_activity else None
                    })
            
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error getting direct conversations: {str(e)}")
            return []
    
    def get_direct_messages(self, admin_id: int, target_admin_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get direct messages between two admins"""
        try:
            from models import Room, RoomMember, Message, User, db
            
            # Find DM room between admins
            dm_room = db.session.query(Room).join(RoomMember).filter(
                Room.type == 'direct_message',
                RoomMember.user_id.in_([admin_id, target_admin_id])
            ).group_by(Room.id).having(
                db.func.count(RoomMember.user_id) == 2
            ).first()
            
            if not dm_room:
                return []
            
            # Get messages from this room
            messages = Message.query.filter_by(chat_id=dm_room.id).order_by(Message.timestamp.desc()).limit(limit).all()
            
            messages_data = []
            for msg in reversed(messages):  # Reverse to get chronological order
                sender = User.query.get(msg.sender_id)
                messages_data.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'sender_username': sender.username if sender else 'Unknown',
                    'content': msg.original_text,
                    'timestamp': msg.timestamp.isoformat()
                })
            
            return messages_data
            
        except Exception as e:
            self.logger.error(f"Error getting direct messages: {str(e)}")
            return []
    
    def _process_admin_message_through_pipeline(self, sender_id: int, message_text: str, 
                                               message_id: int, chat_id: int, 
                                               communication_type: str) -> Dict[str, Any]:
        """Process admin message through translation pipeline"""
        try:
            from .translation_orchestrator import TranslationRequest
            
            # Create translation request for admin communication
            translation_request = TranslationRequest(
                text=message_text,
                target_language='en',  # Default for admin processing
                source_language='auto',
                user_id=sender_id,
                request_id=f"admin_chat_{message_id}_{communication_type}",
                metadata={
                    'communication_type': communication_type,
                    'message_id': message_id,
                    'chat_id': chat_id,
                    'admin_communication': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Process through pipeline
            pipeline_result = asyncio.run(
                self.orchestrator.translate_message(translation_request)
            )
            
            self.logger.info(f"Admin message {message_id} processed through translation pipeline")
            
            return {
                'pipeline_processed': True,
                'translation_success': pipeline_result.success,
                'data_harvested': pipeline_result.data_harvested
            }
            
        except Exception as e:
            self.logger.error(f"Admin message pipeline processing failed: {e}")
            return {'pipeline_processed': False, 'error': str(e)}

# Singleton instance
admin_chat_service = AdminChatService()