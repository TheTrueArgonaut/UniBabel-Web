"""
Room Invitation Service - Handle invites and invite codes
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from models import db, User
from models.user_models import Room, RoomMember, RoomMemberRole


class RoomInviteService:
    """Handle room invitations and invite codes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("📨 Room Invite Service initialized")
    
    def generate_invite_code(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Generate invite code for a room"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member or member.role not in [RoomMemberRole.OWNER, RoomMemberRole.ADMIN]:
                return {'success': False, 'error': 'You do not have permission to invite users to this room'}
            
            invite_code = self._generate_invite_code(room_id)
            
            return {
                'success': True,
                'invite_code': invite_code,
                'room_id': room_id,
                'expires_in': '7 days',
                'message': 'Share this code with users to invite them to your room'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate invite: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def join_by_invite_code(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Join a room using invite code"""
        try:
            if not invite_code or not invite_code.startswith("ROOM-"):
                return {'success': False, 'error': 'Invalid invite code format'}
            
            try:
                room_id = int(invite_code.split("-")[1])
            except (IndexError, ValueError):
                return {'success': False, 'error': 'Invalid invite code'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found or invite expired'}
            
            existing_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if existing_member:
                if existing_member.role == RoomMemberRole.INVITED:
                    existing_member.role = RoomMemberRole.MEMBER
                    existing_member.joined_at = datetime.utcnow()
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'message': f'Successfully joined room: {room.name}',
                        'room_id': room.id,
                        'room_name': room.name
                    }
                else:
                    return {'success': False, 'error': 'You are already a member of this room'}
            
            new_member = RoomMember(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.MEMBER,
                joined_at=datetime.utcnow()
            )
            db.session.add(new_member)
            db.session.commit()
            
            self.logger.info(f"📨 User {user_id} joined room {room_id} via invite")
            
            return {
                'success': True,
                'message': f'Successfully joined room: {room.name}',
                'room_id': room.id,
                'room_name': room.name,
                'room_type': room.type.value
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to join room: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def invite_user_to_room(self, inviter_id: int, room_id: int, target_user_id: int) -> Dict[str, Any]:
        """Invite a specific user to a room"""
        try:
            inviter_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=inviter_id
            ).first()
            
            if not inviter_member or inviter_member.role not in [RoomMemberRole.OWNER, RoomMemberRole.ADMIN]:
                return {'success': False, 'error': 'You do not have permission to invite users'}
            
            target_user = db.session.get(User, target_user_id)
            if not target_user:
                return {'success': False, 'error': 'User not found'}
            
            existing_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=target_user_id
            ).first()
            
            if existing_member:
                return {'success': False, 'error': 'User is already a member or has been invited'}
            
            invited_member = RoomMember(
                room_id=room_id,
                user_id=target_user_id,
                role=RoomMemberRole.INVITED,
                joined_at=datetime.utcnow()
            )
            db.session.add(invited_member)
            db.session.commit()
            
            self.logger.info(f"📨 User {target_user_id} invited to room {room_id} by {inviter_id}")
            
            return {
                'success': True,
                'message': f'Successfully invited {target_user.username} to the room',
                'invited_user': target_user.username
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to invite user: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_pending_invites(self, user_id: int) -> Dict[str, Any]:
        """Get rooms the user has been invited to but hasn't joined yet"""
        try:
            pending_invites = db.session.query(Room, RoomMember).join(
                RoomMember, Room.id == RoomMember.room_id
            ).filter(
                RoomMember.user_id == user_id,
                RoomMember.role == RoomMemberRole.INVITED
            ).all()
            
            invites_data = []
            for room, membership in pending_invites:
                owner_member = RoomMember.query.filter_by(
                    room_id=room.id,
                    role=RoomMemberRole.OWNER
                ).first()
                
                owner = None
                if owner_member:
                    owner = db.session.get(User, owner_member.user_id)
                
                invites_data.append({
                    'room_id': room.id,
                    'room_name': room.name,
                    'room_type': room.type.value,
                    'invited_at': membership.joined_at.isoformat() if membership.joined_at else None,
                    'invited_by': owner.display_name or owner.username if owner else 'Unknown',
                    'member_count': RoomMember.query.filter_by(room_id=room.id).count()
                })
            
            return {
                'success': True,
                'invites': invites_data,
                'total_invites': len(invites_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get pending invites: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def decline_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Decline a room invitation"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.INVITED
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Invitation not found'}
            
            db.session.delete(member)
            db.session.commit()
            
            self.logger.info(f"📨 User {user_id} declined invitation to room {room_id}")
            
            return {'success': True, 'message': 'Invitation declined'}
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to decline invite: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_invite_code(self, room_id: int) -> str:
        """Generate invite code for room"""
        return f"ROOM-{room_id}"