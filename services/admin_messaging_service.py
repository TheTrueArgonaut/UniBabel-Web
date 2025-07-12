"""
Admin Messaging Service - SRIMI Microservice
Single Responsibility: Direct messaging from admin to users
Now with Translation Pipeline Integration for Global Customer Service
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import asyncio

@dataclass
class AdminMessage:
    """Admin message data structure"""
    message_id: int
    from_admin_id: int
    to_user_id: int
    content: str
    timestamp: datetime
    is_system_message: bool
    message_type: str
    read_status: bool

class AdminMessagingService:
    """Micro-service for admin direct messaging with translation pipeline"""
    
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
        
    def send_direct_message(self, admin_user_id: int, target_user_id: int, content: str, message_type: str = 'admin_direct', ip_address: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Send direct message from admin to user with translation pipeline support"""
        try:
            # Prevent self-messaging
            if admin_user_id == target_user_id:
                return {
                    'success': False,
                    'error': 'Cannot send message to yourself',
                    'error_code': 'SELF_MESSAGE_BLOCKED'
                }
            
            # Validate users exist
            from models import User
            admin_user = User.query.get(admin_user_id)
            target_user = User.query.get(target_user_id)
            
            if not admin_user:
                return {
                    'success': False,
                    'error': 'Admin user not found',
                    'error_code': 'ADMIN_NOT_FOUND'
                }
            
            if not target_user:
                return {
                    'success': False,
                    'error': 'Target user not found',
                    'error_code': 'TARGET_USER_NOT_FOUND'
                }
            
            # Check if admin has messaging permissions
            if not getattr(admin_user, 'is_data_vampire_admin', False):
                return {
                    'success': False,
                    'error': 'Admin privileges required',
                    'error_code': 'INSUFFICIENT_PERMISSIONS'
                }
            
            # Log the interaction BEFORE sending
            from services.admin_interaction_logger import admin_interaction_logger
            try:
                log_id = admin_interaction_logger.log_message_interaction(
                    admin_user_id=admin_user_id,
                    target_user_id=target_user_id,
                    content=content,
                    message_type=message_type,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                self.logger.info(f"Logged admin message interaction: {log_id}")
            except Exception as log_error:
                self.logger.error(f"Failed to log message interaction: {str(log_error)}")
                # Continue with message sending even if logging fails
            
            # Create the message
            from models import Message, Room, RoomMember, db
            
            # Find or create a direct message room between admin and user
            dm_room = self._get_or_create_dm_room(admin_user_id, target_user_id)
            
            # Create the message with AUTO language detection instead of hardcoded English
            message = Message(
                chat_id=dm_room.id,
                sender_id=admin_user_id,
                original_text=content,
                original_language='AUTO',  # Changed from 'en' to 'AUTO' for pipeline processing
                timestamp=datetime.utcnow(),
                is_system_message=(message_type == 'system'),
                message_type=message_type
            )
            
            db.session.add(message)
            db.session.flush()  # Get the message ID
            
            # ROUTE THROUGH TRANSLATION PIPELINE - Just like regular messages!
            pipeline_result = self._process_message_through_pipeline(
                user_id=admin_user_id,
                message_text=content,
                message_id=message.id,
                chat_id=dm_room.id,
                communication_type='admin_direct_message',
                recipient_user_id=target_user_id,
                metadata={
                    'message_type': message_type,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'admin_conversation': True
                }
            )
            
            # Create translation for target user based on their preferred language
            translated_content = content  # Default fallback
            if pipeline_result.get('translation_success') and target_user.preferred_language:
                translated_content = pipeline_result.get('translation_provided', content)
            
            # Update room's last activity
            dm_room.last_activity = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message_id': message.id,
                'room_id': dm_room.id,
                'timestamp': message.timestamp.isoformat(),
                'content': content,
                'translated_content': translated_content,
                'target_language': target_user.preferred_language,
                'message_type': message_type,
                'target_user': {
                    'id': target_user.id,
                    'username': target_user.username,
                    'preferred_language': target_user.preferred_language
                },
                'log_id': log_id if 'log_id' in locals() else None,
                'pipeline_processed': pipeline_result.get('pipeline_processed', False),
                'translation_success': pipeline_result.get('translation_success', False)
            }
            
        except Exception as e:
            self.logger.error(f"Error sending direct message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'SEND_MESSAGE_ERROR'
            }
    
    def _process_message_through_pipeline(self, user_id: int, message_text: str, 
                                        message_id: int, chat_id: int, 
                                        communication_type: str, recipient_user_id: int,
                                        metadata: Dict = None) -> Dict:
        """
        Process admin message through translation pipeline
        
        This ensures admin messages get the same treatment as regular messages:
        1. Language detection
        2. Translation to recipient's preferred language
        3. Data harvesting (if applicable)
        4. Vulnerability analysis
        """
        try:
            # Import here to avoid circular imports
            from .translation_orchestrator import TranslationRequest
            from models import User
            
            # Get recipient's preferred language
            recipient_user = User.query.get(recipient_user_id)
            target_language = recipient_user.preferred_language if recipient_user else 'en'
            
            # Create comprehensive translation request
            translation_request = TranslationRequest(
                text=message_text,
                target_language=target_language,
                source_language='auto',
                user_id=user_id,
                request_id=f"admin_msg_{message_id}_{communication_type}",
                metadata={
                    'communication_type': communication_type,
                    'message_id': message_id,
                    'chat_id': chat_id,
                    'recipient_user_id': recipient_user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Process through pipeline (this handles both translation and data harvesting)
            pipeline_result = asyncio.run(
                self.orchestrator.translate_message(translation_request)
            )
            
            self.logger.info(f"Admin message {message_id} processed through translation pipeline - Target: {target_language}")
            
            return {
                'pipeline_processed': True,
                'data_harvested': pipeline_result.data_harvested,
                'data_value': pipeline_result.user_data_value,
                'vulnerability_score': pipeline_result.vulnerability_score,
                'translation_success': pipeline_result.success,
                'was_cached': pipeline_result.cached,
                'translation_provided': pipeline_result.translation if pipeline_result.success else None,
                'target_language': target_language
            }
            
        except Exception as e:
            self.logger.error(f"Admin message translation pipeline processing failed: {e}")
            return {
                'pipeline_processed': False,
                'data_harvested': False,
                'data_value': 0.0,
                'vulnerability_score': 0.0,
                'translation_success': False,
                'error': str(e)
            }

    def _get_or_create_dm_room(self, admin_user_id: int, target_user_id: int):
        """Get or create direct message room between admin and user"""
        from models import Room, RoomMember, db
        
        # Look for existing DM room between these users
        existing_room = db.session.query(Room).join(RoomMember).filter(
            Room.type == 'direct_message',
            RoomMember.user_id.in_([admin_user_id, target_user_id])
        ).group_by(Room.id).having(
            db.func.count(RoomMember.user_id) == 2
        ).first()
        
        if existing_room:
            return existing_room
        
        # Create new DM room
        room_name = f"Admin DM: {admin_user_id} ↔ {target_user_id}"
        dm_room = Room(
            name=room_name,
            type='direct_message',
            owner_id=admin_user_id,
            created_at=datetime.utcnow(),
            is_discoverable=False,
            activity_score=0,
            last_activity=datetime.utcnow()
        )
        
        db.session.add(dm_room)
        db.session.flush()  # Get the room ID
        
        # Add both users to the room
        admin_member = RoomMember(
            room_id=dm_room.id,
            user_id=admin_user_id,
            role='admin',
            joined_at=datetime.utcnow()
        )
        
        target_member = RoomMember(
            room_id=dm_room.id,
            user_id=target_user_id,
            role='member',
            joined_at=datetime.utcnow()
        )
        
        db.session.add(admin_member)
        db.session.add(target_member)
        db.session.commit()
        
        return dm_room
    
    def get_admin_conversations(self, admin_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get admin's direct message conversations"""
        try:
            from models import Room, RoomMember, User, Message
            
            # Get rooms where admin is a member and room type is direct_message
            conversations = []
            
            admin_rooms = db.session.query(Room).join(RoomMember).filter(
                RoomMember.user_id == admin_user_id,
                Room.type == 'direct_message'
            ).order_by(Room.last_activity.desc()).limit(limit).all()
            
            for room in admin_rooms:
                # Get the other user in the conversation
                other_member = db.session.query(RoomMember).join(User).filter(
                    RoomMember.room_id == room.id,
                    RoomMember.user_id != admin_user_id
                ).first()
                
                if other_member:
                    # Get last message
                    last_message = Message.query.filter_by(chat_id=room.id).order_by(Message.timestamp.desc()).first()
                    
                    conversations.append({
                        'room_id': room.id,
                        'other_user': {
                            'id': other_member.user_id,
                            'username': other_member.user.username
                        },
                        'last_message': {
                            'content': last_message.original_text if last_message else None,
                            'timestamp': last_message.timestamp.isoformat() if last_message else None
                        },
                        'last_activity': room.last_activity.isoformat() if room.last_activity else None
                    })
            
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error getting admin conversations: {str(e)}")
            return []
    
    def get_conversation_history(self, admin_user_id: int, room_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get conversation history for a specific room"""
        try:
            from models import Room, RoomMember, Message, User
            
            # Verify admin has access to this room
            room_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=admin_user_id
            ).first()
            
            if not room_member:
                return {
                    'success': False,
                    'error': 'Access denied to this conversation',
                    'error_code': 'ACCESS_DENIED'
                }
            
            # Get messages
            messages = Message.query.filter_by(chat_id=room_id).order_by(Message.timestamp.desc()).limit(limit).all()
            
            # Get room info
            room = Room.query.get(room_id)
            
            # Get other user in conversation
            other_member = RoomMember.query.join(User).filter(
                RoomMember.room_id == room_id,
                RoomMember.user_id != admin_user_id
            ).first()
            
            message_history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                message_history.append({
                    'id': msg.id,
                    'content': msg.original_text,
                    'sender_id': msg.sender_id,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_system_message': msg.is_system_message,
                    'message_type': msg.message_type
                })
            
            return {
                'success': True,
                'room_id': room_id,
                'room_name': room.name,
                'other_user': {
                    'id': other_member.user_id,
                    'username': other_member.user.username
                } if other_member else None,
                'messages': message_history,
                'total_messages': len(messages)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'GET_HISTORY_ERROR'
            }
    
    def send_system_notification(self, admin_user_id: int, target_user_id: int, notification_type: str, content: str, ip_address: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Send system notification to user with translation support"""
        system_message = f"🔔 System Notification ({notification_type}): {content}"
        
        return self.send_direct_message(
            admin_user_id=admin_user_id,
            target_user_id=target_user_id,
            content=system_message,
            message_type='system_notification',
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def send_warning_message(self, admin_user_id: int, target_user_id: int, warning_reason: str, ip_address: str = '', user_agent: str = '') -> Dict[str, Any]:
        """Send warning message to user with translation support"""
        warning_message = f"⚠️ Warning: {warning_reason}"
        
        return self.send_direct_message(
            admin_user_id=admin_user_id,
            target_user_id=target_user_id,
            content=warning_message,
            message_type='admin_warning',
            ip_address=ip_address,
            user_agent=user_agent
        )

# Singleton instance
admin_messaging_service = AdminMessagingService()