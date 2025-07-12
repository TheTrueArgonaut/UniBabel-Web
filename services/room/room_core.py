"""
Core Room Management Service - Basic CRUD operations
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from models import db, User
from models.user_models import Room, RoomMember, RoomType, RoomMemberRole


class RoomCore:
    """Core room operations - create, join, leave, delete"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏠 Room Core Service initialized")
    
    def create_room(self, owner_id: int, name: str, room_type: RoomType = RoomType.PRIVATE) -> Dict[str, Any]:
        """Create a new room"""
        try:
            if not name or len(name.strip()) < 1:
                return {'success': False, 'error': 'Room name is required'}
            
            if len(name) > 100:
                return {'success': False, 'error': 'Room name too long (max 100 characters)'}
            
            user = db.session.get(User, owner_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            room = Room(
                name=name.strip(),
                type=room_type,
                owner_id=owner_id,
                is_discoverable=False,
                activity_score=0
            )
            db.session.add(room)
            db.session.flush()
            
            owner_member = RoomMember(
                room_id=room.id,
                user_id=owner_id,
                role=RoomMemberRole.OWNER,
                joined_at=datetime.utcnow()
            )
            db.session.add(owner_member)
            db.session.commit()
            
            self.logger.info(f"🏠 Room created: '{name}' by user {owner_id}")
            
            return {
                'success': True,
                'room_id': room.id,
                'room_name': room.name,
                'room_type': room.type.value,
                'owner_id': owner_id,
                'created_at': room.created_at.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to create room: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def join_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join a room (requires existing invitation)"""
        try:
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'You have not been invited to this room'}
            
            if member.role == RoomMemberRole.INVITED:
                member.role = RoomMemberRole.MEMBER
                member.joined_at = datetime.utcnow()
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f'Successfully joined {room.name}',
                    'room_id': room.id,
                    'room_name': room.name
                }
            else:
                return {'success': True, 'message': 'You are already a member of this room'}
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to join room: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def leave_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave a room"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'You are not a member of this room'}
            
            if member.role == RoomMemberRole.OWNER:
                other_members = RoomMember.query.filter(
                    RoomMember.room_id == room_id,
                    RoomMember.user_id != user_id,
                    RoomMember.role != RoomMemberRole.INVITED
                ).all()
                
                if other_members:
                    new_owner = next((m for m in other_members if m.role == RoomMemberRole.ADMIN), other_members[0])
                    new_owner.role = RoomMemberRole.OWNER
                    db.session.delete(member)
                    db.session.commit()
                    return {'success': True, 'message': 'Left room and transferred ownership'}
                else:
                    return self.delete_room(user_id, room_id)
            else:
                db.session.delete(member)
                db.session.commit()
                return {'success': True, 'message': 'Successfully left the room'}
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to leave room: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Delete a room (owner only)"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {'success': False, 'error': 'You do not own this room'}
            
            RoomMember.query.filter_by(room_id=room_id).delete()
            
            room = db.session.get(Room, room_id)
            if room:
                room_name = room.name
                db.session.delete(room)
                db.session.commit()
                return {'success': True, 'message': f'Room "{room_name}" has been deleted'}
            else:
                return {'success': False, 'error': 'Room not found'}
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to delete room: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_room_info(self, room_id: int) -> Dict[str, Any]:
        """Get basic room information"""
        try:
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            member_count = RoomMember.query.filter_by(room_id=room_id).count()
            
            return {
                'success': True,
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'type': room.type.value,
                    'owner_id': room.owner_id,
                    'is_discoverable': room.is_discoverable,
                    'created_at': room.created_at.isoformat(),
                    'member_count': member_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get room info: {str(e)}")
            return {'success': False, 'error': str(e)}