"""
Room Management Service - Handle member management and room settings
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, List
from models import db, User
from models.user_models import Room, RoomMember, RoomMemberRole, RoomPermission


class RoomManagementService:
    """Handle room member management and settings"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("⚙️ Room Management Service initialized")
    
    def get_user_rooms(self, user_id: int) -> Dict[str, Any]:
        """Get all rooms user is a member of"""
        try:
            user_rooms = db.session.query(Room, RoomMember).join(
                RoomMember, Room.id == RoomMember.room_id
            ).filter(
                RoomMember.user_id == user_id,
                RoomMember.role != RoomMemberRole.INVITED
            ).all()
            
            rooms_data = []
            for room, membership in user_rooms:
                rooms_data.append({
                    'room_id': room.id,
                    'room_name': room.name,
                    'room_type': room.type.value,
                    'is_owner': membership.role == RoomMemberRole.OWNER,
                    'role': membership.role.value,
                    'joined_at': membership.joined_at.isoformat() if membership.joined_at else None,
                    'created_at': room.created_at.isoformat(),
                    'member_count': RoomMember.query.filter_by(room_id=room.id).count(),
                    'is_discoverable': room.is_discoverable,
                    'can_invite': membership.role in [RoomMemberRole.OWNER, RoomMemberRole.ADMIN]
                })
            
            return {
                'success': True,
                'rooms': rooms_data,
                'total_rooms': len(rooms_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user rooms: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_room_members(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Get all members of a room"""
        try:
            # Check if user is member of the room
            user_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not user_member:
                return {'success': False, 'error': 'You are not a member of this room'}
            
            members = db.session.query(RoomMember, User).join(User).filter(
                RoomMember.room_id == room_id,
                RoomMember.role != RoomMemberRole.INVITED
            ).all()
            
            members_data = []
            for member, user in members:
                members_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': user.display_name or user.username,
                    'role': member.role.value,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                    'is_online': getattr(user, 'is_online', False),
                    'last_seen': getattr(user, 'last_seen', None)
                })
            
            return {
                'success': True,
                'members': members_data,
                'total_members': len(members_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get room members: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_member_role(self, room_id: int, admin_user_id: int, target_user_id: int, new_role: str) -> Dict[str, Any]:
        """Update a member's role in the room"""
        try:
            if not self._has_permission(admin_user_id, room_id, 'MANAGE_ROLES'):
                return {'success': False, 'error': 'Insufficient permissions to manage roles'}
            
            admin_member = RoomMember.query.filter_by(room_id=room_id, user_id=admin_user_id).first()
            target_member = RoomMember.query.filter_by(room_id=room_id, user_id=target_user_id).first()
            
            if not admin_member or not target_member:
                return {'success': False, 'error': 'Member not found in room'}
            
            # Prevent role escalation beyond admin's level
            role_hierarchy = {
                RoomMemberRole.MEMBER: 1,
                RoomMemberRole.MODERATOR: 2,
                RoomMemberRole.ADMIN: 3,
                RoomMemberRole.OWNER: 4
            }
            
            admin_level = role_hierarchy.get(admin_member.role, 0)
            new_role_enum = RoomMemberRole(new_role)
            new_role_level = role_hierarchy.get(new_role_enum, 0)
            
            if new_role_level >= admin_level and admin_member.role != RoomMemberRole.OWNER:
                return {'success': False, 'error': 'Cannot assign role equal or higher than your own'}
            
            target_member.role = new_role_enum
            db.session.commit()
            
            self.logger.info(f"⚙️ User {target_user_id} role updated to {new_role} in room {room_id}")
            
            return {
                'success': True,
                'message': f'Member role updated to {new_role}'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to update member role: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def kick_member(self, room_id: int, admin_user_id: int, target_user_id: int, reason: str = None) -> Dict[str, Any]:
        """Kick a member from the room"""
        try:
            if not self._has_permission(admin_user_id, room_id, 'MANAGE_MEMBERS'):
                return {'success': False, 'error': 'Insufficient permissions to kick members'}
            
            target_member = RoomMember.query.filter_by(room_id=room_id, user_id=target_user_id).first()
            admin_member = RoomMember.query.filter_by(room_id=room_id, user_id=admin_user_id).first()
            
            if not target_member:
                return {'success': False, 'error': 'Member not found in room'}
            
            # Prevent kicking higher or equal role
            role_hierarchy = {
                RoomMemberRole.MEMBER: 1,
                RoomMemberRole.MODERATOR: 2,
                RoomMemberRole.ADMIN: 3,
                RoomMemberRole.OWNER: 4
            }
            
            admin_level = role_hierarchy.get(admin_member.role, 0)
            target_level = role_hierarchy.get(target_member.role, 0)
            
            if target_level >= admin_level:
                return {'success': False, 'error': 'Cannot kick member with equal or higher role'}
            
            db.session.delete(target_member)
            db.session.commit()
            
            self.logger.info(f"⚙️ User {target_user_id} kicked from room {room_id}. Reason: {reason}")
            
            return {
                'success': True,
                'message': 'Member kicked successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to kick member: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def transfer_ownership(self, room_id: int, current_owner_id: int, new_owner_id: int) -> Dict[str, Any]:
        """Transfer room ownership to another member"""
        try:
            current_owner = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=current_owner_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not current_owner:
                return {'success': False, 'error': 'You are not the owner of this room'}
            
            new_owner = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=new_owner_id
            ).first()
            
            if not new_owner:
                return {'success': False, 'error': 'Target user is not a member of this room'}
            
            # Transfer ownership
            current_owner.role = RoomMemberRole.ADMIN
            new_owner.role = RoomMemberRole.OWNER
            
            # Update room owner_id
            room = db.session.get(Room, room_id)
            if room:
                room.owner_id = new_owner_id
            
            db.session.commit()
            
            self.logger.info(f"⚙️ Room {room_id} ownership transferred from {current_owner_id} to {new_owner_id}")
            
            return {
                'success': True,
                'message': 'Room ownership transferred successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to transfer ownership: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_room_settings(self, room_id: int, user_id: int, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update room settings"""
        try:
            if not self._has_permission(user_id, room_id, 'MANAGE_ROOM'):
                return {'success': False, 'error': 'Insufficient permissions to manage room'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            # Update basic room settings
            if 'name' in settings:
                room.name = settings['name'][:100]
            if 'is_discoverable' in settings:
                room.is_discoverable = bool(settings['is_discoverable'])
            
            db.session.commit()
            
            self.logger.info(f"⚙️ Room {room_id} settings updated")
            
            return {
                'success': True,
                'message': 'Room settings updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to update room settings: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_room_stats(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Get room statistics"""
        try:
            if not self._has_permission(user_id, room_id, 'VIEW_STATS'):
                return {'success': False, 'error': 'Insufficient permissions to view stats'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            # Get member statistics
            total_members = RoomMember.query.filter_by(room_id=room_id).count()
            role_counts = {}
            
            for role in RoomMemberRole:
                count = RoomMember.query.filter_by(room_id=room_id, role=role).count()
                role_counts[role.value] = count
            
            return {
                'success': True,
                'stats': {
                    'room_id': room_id,
                    'room_name': room.name,
                    'created_at': room.created_at.isoformat(),
                    'total_members': total_members,
                    'role_distribution': role_counts,
                    'activity_score': room.activity_score,
                    'is_discoverable': room.is_discoverable,
                    'room_type': room.type.value
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get room stats: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _has_permission(self, user_id: int, room_id: int, permission: str) -> bool:
        """Check if user has specific permission in room"""
        try:
            member = RoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
            if not member:
                return False
            
            # Owner has all permissions
            if member.role == RoomMemberRole.OWNER:
                return True
            
            # Check default role permissions
            default_permissions = self._get_default_role_permissions(member.role)
            if permission in default_permissions:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking permission: {e}")
            return False
    
    def _get_default_role_permissions(self, role: RoomMemberRole) -> List[str]:
        """Get default permissions for a role"""
        if role == RoomMemberRole.OWNER:
            return [
                'MANAGE_ROOM', 'MANAGE_MEMBERS', 'MANAGE_ROLES', 'CREATE_INVITE',
                'SEND_MESSAGES', 'VOICE_CHAT', 'UPLOAD_FILES', 'DELETE_MESSAGES',
                'MUTE_MEMBERS', 'BAN_MEMBERS', 'VIEW_STATS', 'TRANSFER_OWNERSHIP'
            ]
        elif role == RoomMemberRole.ADMIN:
            return [
                'MANAGE_ROOM', 'MANAGE_MEMBERS', 'MANAGE_ROLES', 'CREATE_INVITE',
                'SEND_MESSAGES', 'VOICE_CHAT', 'UPLOAD_FILES', 'DELETE_MESSAGES',
                'MUTE_MEMBERS', 'BAN_MEMBERS', 'VIEW_STATS'
            ]
        elif role == RoomMemberRole.MODERATOR:
            return [
                'CREATE_INVITE', 'SEND_MESSAGES', 'VOICE_CHAT', 'UPLOAD_FILES',
                'DELETE_MESSAGES', 'MUTE_MEMBERS'
            ]
        elif role == RoomMemberRole.MEMBER:
            return ['SEND_MESSAGES', 'VOICE_CHAT', 'UPLOAD_FILES']
        else:
            return []