"""
Room Services Package - Unified interface for all room microservices
"""

from .room_core import RoomCore
from .room_invites import RoomInviteService
from .room_voice import RoomVoiceService
from .room_discovery import RoomDiscoveryService
from .room_management import RoomManagementService
from typing import Dict, Any, List


class RoomService:
    """Unified Room Service - Orchestrates all room microservices"""
    
    def __init__(self):
        # Initialize all microservices
        self.core = RoomCore()
        self.invites = RoomInviteService()
        self.voice = RoomVoiceService()
        self.discovery = RoomDiscoveryService()
        self.management = RoomManagementService()
    
    # Core room operations
    def create_room(self, owner_id: int, name: str, room_type: str = "private", 
                   voice_enabled: bool = False, is_discoverable: bool = False) -> Dict[str, Any]:
        """Create a new room with optional features"""
        from models.user_models import RoomType
        
        # Determine room type
        if voice_enabled:
            room_type_enum = RoomType.VOICE_CHAT
        else:
            room_type_enum = RoomType.PRIVATE
        
        # Create room
        result = self.core.create_room(owner_id, name, room_type_enum)
        
        if result['success'] and is_discoverable:
            # Make room discoverable
            self.discovery.make_room_discoverable(owner_id, result['room_id'])
            result['is_discoverable'] = True
        
        if result['success'] and voice_enabled:
            # Initialize voice for room
            result['voice_enabled'] = True
            result['voice_config'] = self.voice.get_voice_config()
        
        return result
    
    def join_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join a room"""
        return self.core.join_room(user_id, room_id)
    
    def leave_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave a room"""
        return self.core.leave_room(user_id, room_id)
    
    def delete_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Delete a room"""
        return self.core.delete_room(user_id, room_id)
    
    # Invite operations
    def generate_invite_code(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Generate invite code for a room"""
        return self.invites.generate_invite_code(user_id, room_id)
    
    def join_by_invite_code(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Join room using invite code"""
        return self.invites.join_by_invite_code(user_id, invite_code)
    
    def get_pending_invites(self, user_id: int) -> Dict[str, Any]:
        """Get pending invites for user"""
        return self.invites.get_pending_invites(user_id)
    
    def decline_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Decline room invitation"""
        return self.invites.decline_invite(user_id, room_id)
    
    # Voice operations
    def join_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join voice chat in room"""
        return self.voice.join_voice_chat(user_id, room_id)
    
    def leave_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave voice chat in room"""
        return self.voice.leave_voice_chat(user_id, room_id)
    
    def get_voice_session_status(self, room_id: int) -> Dict[str, Any]:
        """Get voice session status"""
        return self.voice.get_voice_session_status(room_id)
    
    def update_voice_status(self, user_id: int, room_id: int, **kwargs) -> Dict[str, Any]:
        """Update voice status"""
        return self.voice.update_voice_status(user_id, room_id, **kwargs)
    
    # Discovery operations
    def get_discoverable_rooms(self, user_id: int, **kwargs) -> List[Dict[str, Any]]:
        """Get discoverable rooms"""
        return self.discovery.get_discoverable_rooms(user_id, **kwargs)
    
    def get_trending_rooms(self, user_id: int) -> List[Dict[str, Any]]:
        """Get trending rooms"""
        return self.discovery.get_trending_rooms(user_id)
    
    def join_discoverable_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join a discoverable room"""
        return self.discovery.join_discoverable_room(user_id, room_id)
    
    def search_rooms(self, user_id: int, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search rooms"""
        return self.discovery.search_rooms(user_id, query, **kwargs)
    
    # Management operations
    def get_user_rooms(self, user_id: int) -> Dict[str, Any]:
        """Get user's rooms"""
        return self.management.get_user_rooms(user_id)
    
    def get_room_members(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Get room members"""
        return self.management.get_room_members(room_id, user_id)
    
    def update_member_role(self, room_id: int, admin_user_id: int, target_user_id: int, new_role: str) -> Dict[str, Any]:
        """Update member role"""
        return self.management.update_member_role(room_id, admin_user_id, target_user_id, new_role)
    
    def kick_member(self, room_id: int, admin_user_id: int, target_user_id: int, reason: str = None) -> Dict[str, Any]:
        """Kick member from room"""
        return self.management.kick_member(room_id, admin_user_id, target_user_id, reason)
    
    def transfer_ownership(self, room_id: int, current_owner_id: int, new_owner_id: int) -> Dict[str, Any]:
        """Transfer room ownership"""
        return self.management.transfer_ownership(room_id, current_owner_id, new_owner_id)
    
    def get_room_stats(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Get room statistics"""
        return self.management.get_room_stats(room_id, user_id)
    
    # Activity tracking
    def increase_room_activity(self, room_id: int, activity_type: str = 'message') -> None:
        """Increase room activity score"""
        self.discovery.increase_room_activity(room_id, activity_type)
    
    # Legacy compatibility methods
    def create_private_room(self, owner_id: int, room_name: str, room_type: str = "private", 
                           voice_enabled: bool = False, is_discoverable: bool = False) -> Dict[str, Any]:
        """Legacy method for creating private rooms"""
        return self.create_room(owner_id, room_name, room_type, voice_enabled, is_discoverable)
    
    def join_room_by_invite(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Legacy method for joining by invite"""
        return self.join_by_invite_code(user_id, invite_code)
    
    def generate_room_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Legacy method for generating invites"""
        return self.generate_invite_code(user_id, room_id)
    
    def decline_room_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Legacy method for declining invites"""
        return self.decline_invite(user_id, room_id)
    
    # Convenience methods for common operations
    def get_rooms(self, current_user, **kwargs) -> List[Dict[str, Any]]:
        """Get user's rooms (formatted for UI)"""
        result = self.get_user_rooms(current_user.id)
        if result['success']:
            return result['rooms']
        return []
    
    def get_featured_rooms(self, current_user) -> List[Dict[str, Any]]:
        """Get featured/trending rooms"""
        return self.get_trending_rooms(current_user.id)


# Global instance
_room_service = RoomService()


def get_room_service() -> RoomService:
    """Get the global room service instance"""
    return _room_service