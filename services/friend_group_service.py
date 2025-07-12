"""
Friend Group Service - Handle friend groups for babel posts and group chats
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from models import db, User
from models.user_models import FriendGroup, FriendGroupMember, FriendGroupType, FriendGroupRole

class FriendGroupService:
    """Handle friend group operations for babel posts and group chats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("👥 Friend Group Service initialized")
    
    def create_friend_group(self, creator_id: int, group_name: str, group_type: str = "mixed") -> Dict[str, Any]:
        """Create a new friend group"""
        try:
            # Validate group name
            if not group_name or len(group_name.strip()) < 1:
                return {
                    'success': False,
                    'error': 'Group name is required'
                }
            
            if len(group_name) > 100:
                return {
                    'success': False,
                    'error': 'Group name too long (max 100 characters)'
                }
            
            # Check if user exists
            user = User.query.get(creator_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Determine group type
            if group_type == "babel_group":
                group_type_enum = FriendGroupType.BABEL_GROUP
            elif group_type == "chat_group":
                group_type_enum = FriendGroupType.CHAT_GROUP
            else:
                group_type_enum = FriendGroupType.MIXED
            
            # Create friend group
            friend_group = FriendGroup(
                name=group_name.strip(),
                type=group_type_enum,
                creator_id=creator_id
            )
            db.session.add(friend_group)
            db.session.flush()
            
            # Add creator as member
            creator_member = FriendGroupMember(
                friend_group_id=friend_group.id,
                user_id=creator_id,
                role=FriendGroupRole.CREATOR,
                joined_at=datetime.utcnow()
            )
            db.session.add(creator_member)
            db.session.commit()
            
            self.logger.info(f"👥 Friend group created: '{group_name}' by user {creator_id}")
            
            return {
                'success': True,
                'group_id': friend_group.id,
                'group_name': friend_group.name,
                'group_type': friend_group.type.value,
                'creator_id': creator_id,
                'created_at': friend_group.created_at.isoformat(),
                'can_babel': friend_group.type in [FriendGroupType.BABEL_GROUP, FriendGroupType.MIXED],
                'can_chat': friend_group.type in [FriendGroupType.CHAT_GROUP, FriendGroupType.MIXED]
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to create friend group: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_member_to_group(self, user_id: int, group_id: int, new_member_id: int) -> Dict[str, Any]:
        """Add a member to a friend group"""
        try:
            # Check if user has permission to add members
            member = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=user_id
            ).first()
            
            if not member or member.role not in [FriendGroupRole.CREATOR, FriendGroupRole.ADMIN]:
                return {
                    'success': False,
                    'error': 'You do not have permission to add members to this group'
                }
            
            # Check if new member already in group
            existing_member = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=new_member_id
            ).first()
            
            if existing_member:
                return {
                    'success': False,
                    'error': 'User is already a member of this group'
                }
            
            # Check if new member exists
            new_user = User.query.get(new_member_id)
            if not new_user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Add member to group
            new_member = FriendGroupMember(
                friend_group_id=group_id,
                user_id=new_member_id,
                role=FriendGroupRole.MEMBER,
                joined_at=datetime.utcnow()
            )
            db.session.add(new_member)
            db.session.commit()
            
            self.logger.info(f"👥 User {new_member_id} added to group {group_id} by user {user_id}")
            
            return {
                'success': True,
                'message': f'{new_user.display_name or new_user.username} added to group',
                'new_member': {
                    'user_id': new_user.id,
                    'username': new_user.username,
                    'display_name': new_user.display_name,
                    'role': 'member'
                }
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to add member to group: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_friend_groups(self, user_id: int) -> Dict[str, Any]:
        """Get all friend groups user is a member of"""
        try:
            user_groups = db.session.query(FriendGroup, FriendGroupMember).join(
                FriendGroupMember, FriendGroup.id == FriendGroupMember.friend_group_id
            ).filter(
                FriendGroupMember.user_id == user_id
            ).all()
            
            groups_data = []
            for group, membership in user_groups:
                # Get member count
                member_count = FriendGroupMember.query.filter_by(friend_group_id=group.id).count()
                
                groups_data.append({
                    'group_id': group.id,
                    'group_name': group.name,
                    'group_type': group.type.value,
                    'is_creator': membership.role == FriendGroupRole.CREATOR,
                    'role': membership.role.value,
                    'joined_at': membership.joined_at.isoformat() if membership.joined_at else None,
                    'created_at': group.created_at.isoformat(),
                    'member_count': member_count,
                    'can_babel': group.type in [FriendGroupType.BABEL_GROUP, FriendGroupType.MIXED],
                    'can_chat': group.type in [FriendGroupType.CHAT_GROUP, FriendGroupType.MIXED]
                })
            
            # Separate by type for easier UI handling
            babel_groups = [g for g in groups_data if g['can_babel']]
            chat_groups = [g for g in groups_data if g['can_chat']]
            
            return {
                'success': True,
                'groups': groups_data,
                'babel_groups': babel_groups,
                'chat_groups': chat_groups,
                'total_groups': len(groups_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user friend groups: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_group_members(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """Get members of a friend group"""
        try:
            # Check if user is member of the group
            user_member = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=user_id
            ).first()
            
            if not user_member:
                return {
                    'success': False,
                    'error': 'You are not a member of this group'
                }
            
            # Get group info
            group = FriendGroup.query.get(group_id)
            if not group:
                return {
                    'success': False,
                    'error': 'Group not found'
                }
            
            # Get all members
            members = db.session.query(FriendGroupMember, User).join(
                User, FriendGroupMember.user_id == User.id
            ).filter(FriendGroupMember.friend_group_id == group_id).all()
            
            members_data = []
            for member, user in members:
                members_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'role': member.role.value,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                    'is_online': user.is_online if hasattr(user, 'is_online') else False
                })
            
            return {
                'success': True,
                'group': {
                    'group_id': group.id,
                    'group_name': group.name,
                    'group_type': group.type.value,
                    'created_at': group.created_at.isoformat()
                },
                'members': members_data,
                'member_count': len(members_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get group members: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def leave_group(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """Leave a friend group"""
        try:
            # Check if user is member of the group
            member = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You are not a member of this group'
                }
            
            # Get group info
            group = FriendGroup.query.get(group_id)
            if not group:
                return {
                    'success': False,
                    'error': 'Group not found'
                }
            
            group_name = group.name
            
            # If creator is leaving, transfer ownership or delete group
            if member.role == FriendGroupRole.CREATOR:
                # Find another admin to transfer to
                other_admin = FriendGroupMember.query.filter_by(
                    friend_group_id=group_id,
                    role=FriendGroupRole.ADMIN
                ).first()
                
                if other_admin:
                    # Transfer ownership
                    other_admin.role = FriendGroupRole.CREATOR
                    db.session.delete(member)
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'message': f'Left group "{group_name}". Ownership transferred.'
                    }
                else:
                    # Check if there are other members to promote
                    other_member = FriendGroupMember.query.filter(
                        FriendGroupMember.friend_group_id == group_id,
                        FriendGroupMember.user_id != user_id
                    ).first()
                    
                    if other_member:
                        # Promote to creator
                        other_member.role = FriendGroupRole.CREATOR
                        db.session.delete(member)
                        db.session.commit()
                        
                        return {
                            'success': True,
                            'message': f'Left group "{group_name}". Ownership transferred.'
                        }
                    else:
                        # Delete empty group
                        db.session.delete(member)
                        db.session.delete(group)
                        db.session.commit()
                        
                        return {
                            'success': True,
                            'message': f'Left group "{group_name}". Group was deleted (no other members).'
                        }
            else:
                # Regular member leaving
                db.session.delete(member)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': f'Left group "{group_name}"'
                }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to leave group: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global instance
_friend_group_service = FriendGroupService()


def get_friend_group_service() -> FriendGroupService:
    """Get the global friend group service instance"""
    return _friend_group_service