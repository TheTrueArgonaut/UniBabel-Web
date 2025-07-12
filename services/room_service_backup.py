"""
Room Service - Handle private rooms, invites, and voice chat
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from models import db, User
from models.user_models import Room, RoomMember, RoomType, RoomMemberRole, RoomPermission, RoomRolePermissions
import json

class RoomService:
    """Handle room operations for custom private rooms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏠 Room Service initialized")
        
        # WebRTC Voice Chat Configuration
        self.voice_config = {
            'stun_servers': [
                'stun:stun.l.google.com:19302',
                'stun:stun1.l.google.com:19302',
                'stun:stun2.l.google.com:19302'
            ],
            'turn_servers': [
                # In production, add TURN servers for better connectivity
                {
                    'urls': 'turn:openrelay.metered.ca:80',
                    'username': 'openrelayproject',
                    'credential': 'openrelayproject'
                }
            ]
        }
        
        # Active voice sessions
        self.active_voice_sessions = {}  # room_id -> {participants: [], started_at: datetime}
    
    def create_private_room(self, owner_id: int, room_name: str, room_type: str = "private", voice_enabled: bool = False, is_discoverable: bool = False) -> Dict[str, Any]:
        """Create a new private room with optional voice chat and discoverability"""
        try:
            # Validate room name
            if not room_name or len(room_name.strip()) < 1:
                return {
                    'success': False,
                    'error': 'Room name is required'
                }
            
            if len(room_name) > 100:
                return {
                    'success': False,
                    'error': 'Room name too long (max 100 characters)'
                }
            
            # Check if user exists
            user = db.session.get(User, owner_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Check if user can create rooms 
            if not self._can_create_room(user):
                return {
                    'success': False,
                    'error': 'Room creation requires Premium subscription',
                    'upgrade_required': True
                }
            
            # Check if user can create voice-enabled rooms
            if voice_enabled and not self._can_create_voice_room(user):
                return {
                    'success': False,
                    'error': 'Voice room creation requires Premium subscription',
                    'upgrade_required': True
                }
            
            # Check if user can make rooms discoverable
            if is_discoverable and not self._can_make_discoverable(user):
                return {
                    'success': False,
                    'error': 'Making rooms discoverable requires Premium subscription',
                    'upgrade_required': True
                }
            
            # Determine room type based on voice capability
            if voice_enabled:
                room_type_enum = RoomType.VOICE_CHAT
            elif room_type == "voice_only":
                room_type_enum = RoomType.VOICE_ONLY
            else:
                room_type_enum = RoomType.PRIVATE
            
            # Create room
            room = Room(
                name=room_name.strip(),
                type=room_type_enum,
                owner_id=owner_id,
                is_discoverable=is_discoverable,
                activity_score=0  # Start with 0 activity
            )
            db.session.add(room)
            db.session.flush()
            
            # Add owner as room member
            owner_member = RoomMember(
                room_id=room.id,
                user_id=owner_id,
                role=RoomMemberRole.OWNER,
                joined_at=datetime.utcnow()
            )
            db.session.add(owner_member)
            
            # Generate invite code
            invite_code = self._generate_invite_code(room.id)
            
            # Initialize voice session if voice enabled
            if voice_enabled:
                self._initialize_voice_session(room.id)
            
            db.session.commit()
            
            self.logger.info(f"🎙️ Room created: '{room_name}' by user {owner_id} (Voice: {voice_enabled}, Discoverable: {is_discoverable})")
            
            return {
                'success': True,
                'room_id': room.id,
                'room_name': room.name,
                'room_type': room.type.value,
                'invite_code': invite_code,
                'voice_enabled': voice_enabled,
                'is_discoverable': is_discoverable,
                'voice_config': self.voice_config if voice_enabled else None,
                'owner_id': owner_id,
                'created_at': room.created_at.isoformat(),
                'webrtc_ready': voice_enabled
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to create room: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def join_room_by_invite(self, user_id: int, invite_code: str) -> Dict[str, Any]:
        """Join a room using invite code"""
        try:
            # Validate invite code format
            if not invite_code or not invite_code.startswith("ROOM-"):
                return {
                    'success': False,
                    'error': 'Invalid invite code format'
                }
            
            # Extract room ID from invite code (simplified)
            try:
                room_id = int(invite_code.split("-")[1])
            except (IndexError, ValueError):
                return {
                    'success': False,
                    'error': 'Invalid invite code'
                }
            
            # Check if room exists
            room = db.session.get(Room, room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found or invite expired'
                }
            
            # Check if user already in room
            existing_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if existing_member:
                if existing_member.role == RoomMemberRole.INVITED:
                    # Accept invitation
                    existing_member.role = RoomMemberRole.MEMBER
                    existing_member.joined_at = datetime.utcnow()
                    db.session.commit()
                    
                    self.increase_room_activity(room_id, 'invite_used')
                    
                    return {
                        'success': True,
                        'message': f'Successfully joined room: {room.name}',
                        'room_id': room.id,
                        'room_name': room.name,
                        'already_member': False
                    }
                else:
                    return {
                        'success': False,
                        'error': 'You are already a member of this room'
                    }
            
            # Add user to room
            new_member = RoomMember(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.MEMBER,
                joined_at=datetime.utcnow()
            )
            db.session.add(new_member)
            db.session.commit()
            
            self.increase_room_activity(room_id, 'join')
            
            self.logger.info(f"🏠 User {user_id} joined room {room_id} via invite")
            
            return {
                'success': True,
                'message': f'Successfully joined room: {room.name}',
                'room_id': room.id,
                'room_name': room.name,
                'room_type': room.type.value,
                'voice_enabled': room.type == RoomType.VOICE_ONLY
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to join room: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
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
                    'voice_enabled': room.type == RoomType.VOICE_ONLY,
                    'is_owner': membership.role == RoomMemberRole.OWNER,
                    'role': membership.role.value,
                    'joined_at': membership.joined_at.isoformat() if membership.joined_at else None,
                    'created_at': room.created_at.isoformat(),
                    'member_count': RoomMember.query.filter_by(room_id=room.id).count()
                })
            
            return {
                'success': True,
                'rooms': rooms_data,
                'total_rooms': len(rooms_data)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user rooms: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_room_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Generate invite code for a room"""
        try:
            # Check if user has permission to invite
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member or member.role not in [RoomMemberRole.OWNER, RoomMemberRole.ADMIN]:
                return {
                    'success': False,
                    'error': 'You do not have permission to invite users to this room'
                }
            
            # Generate invite code
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
            return {
                'success': False,
                'error': str(e)
            }
    
    def join_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join voice chat in a room"""
        try:
            # Check if user is member of the room
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You are not a member of this room'
                }
            
            # Check if room supports voice
            room = db.session.get(Room, room_id)
            if not room or room.type not in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY]:
                return {
                    'success': False,
                    'error': 'This room does not support voice chat'
                }
            
            # Get user info
            user = db.session.get(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Initialize voice session if not exists
            if room_id not in self.active_voice_sessions:
                self._initialize_voice_session(room_id)
            
            # Add user to voice session
            voice_session = self.active_voice_sessions[room_id]
            
            # Check if user already in voice chat
            user_in_voice = any(p['user_id'] == user_id for p in voice_session['participants'])
            if user_in_voice:
                return {
                    'success': False,
                    'error': 'You are already in voice chat'
                }
            
            # Add participant
            participant_data = {
                'user_id': user_id,
                'username': user.username,
                'display_name': user.display_name or user.username,
                'joined_voice_at': datetime.utcnow().isoformat(),
                'is_speaking': False,
                'is_muted': False
            }
            
            voice_session['participants'].append(participant_data)
            
            self.increase_room_activity(room_id, 'voice_join')
            
            self.logger.info(f"🎙️ User {user_id} joined voice chat in room {room_id}")
            
            return {
                'success': True,
                'message': f'Joined voice chat in {room.name}',
                'room_id': room_id,
                'room_name': room.name,
                'voice_session': {
                    'session_id': f"voice_{room_id}",
                    'participants': voice_session['participants'],
                    'started_at': voice_session['started_at'].isoformat(),
                    'participant_count': len(voice_session['participants'])
                },
                'webrtc_config': self.voice_config,
                'user_participant': participant_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to join voice chat: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def leave_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave voice chat in a room"""
        try:
            if room_id not in self.active_voice_sessions:
                return {
                    'success': False,
                    'error': 'No active voice session in this room'
                }
            
            voice_session = self.active_voice_sessions[room_id]
            
            # Remove participant
            voice_session['participants'] = [
                p for p in voice_session['participants'] 
                if p['user_id'] != user_id
            ]
            
            # If no participants left, end session
            if not voice_session['participants']:
                del self.active_voice_sessions[room_id]
                session_ended = True
            else:
                session_ended = False
            
            self.logger.info(f"🎙️ User {user_id} left voice chat in room {room_id}")
            
            return {
                'success': True,
                'message': 'Left voice chat',
                'room_id': room_id,
                'session_ended': session_ended,
                'remaining_participants': len(voice_session['participants']) if not session_ended else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to leave voice chat: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_voice_session_status(self, room_id: int) -> Dict[str, Any]:
        """Get current voice session status for a room"""
        try:
            if room_id not in self.active_voice_sessions:
                return {
                    'active': False,
                    'participants': [],
                    'participant_count': 0
                }
            
            voice_session = self.active_voice_sessions[room_id]
            
            return {
                'active': True,
                'session_id': f"voice_{room_id}",
                'participants': voice_session['participants'],
                'participant_count': len(voice_session['participants']),
                'started_at': voice_session['started_at'].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get voice session status: {str(e)}")
            return {
                'active': False,
                'error': str(e)
            }
    
    def update_voice_status(self, user_id: int, room_id: int, is_speaking: bool = None, is_muted: bool = None) -> Dict[str, Any]:
        """Update user's voice status (speaking, muted, etc.)"""
        try:
            if room_id not in self.active_voice_sessions:
                return {
                    'success': False,
                    'error': 'No active voice session'
                }
            
            voice_session = self.active_voice_sessions[room_id]
            
            # Find and update participant
            for participant in voice_session['participants']:
                if participant['user_id'] == user_id:
                    if is_speaking is not None:
                        participant['is_speaking'] = is_speaking
                    if is_muted is not None:
                        participant['is_muted'] = is_muted
                    
                    return {
                        'success': True,
                        'participant': participant
                    }
            
            return {
                'success': False,
                'error': 'User not in voice session'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update voice status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_friend_group_voice_chat(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """Create voice chat for a friend group"""
        try:
            # Check if user is member of the friend group
            from models.user_models import FriendGroupMember
            member = FriendGroupMember.query.filter_by(
                friend_group_id=group_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You are not a member of this friend group'
                }
            
            # Create temporary voice room for friend group
            from models.user_models import FriendGroup
            friend_group = db.session.get(FriendGroup, group_id)
            if not friend_group:
                return {
                    'success': False,
                    'error': 'Friend group not found'
                }
            
            # Create voice-enabled room
            voice_room_name = f"{friend_group.name} - Voice Chat"
            
            room_result = self.create_private_room(
                owner_id=user_id,
                room_name=voice_room_name,
                room_type="voice_chat",
                voice_enabled=True
            )
            
            if not room_result['success']:
                return room_result
            
            # Auto-invite all friend group members to voice room
            group_members = FriendGroupMember.query.filter_by(friend_group_id=group_id).all()
            invite_results = []
            
            for group_member in group_members:
                if group_member.user_id != user_id:  # Don't invite creator
                    # Add as invited member
                    voice_member = RoomMember(
                        room_id=room_result['room_id'],
                        user_id=group_member.user_id,
                        role=RoomMemberRole.INVITED,
                        joined_at=datetime.utcnow()
                    )
                    db.session.add(voice_member)
                    invite_results.append(group_member.user_id)
            
            db.session.commit()
            
            self.logger.info(f"🎙️ Friend group voice chat created for group {group_id} by user {user_id}")
            
            return {
                'success': True,
                'message': f'Voice chat created for {friend_group.name}',
                'voice_room': room_result,
                'friend_group_id': group_id,
                'invited_members': invite_results,
                'auto_join_instructions': 'Use the invite code to join the voice chat'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to create friend group voice chat: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_rooms(self, current_user, category: str = '', age_filter: str = 'all', search_query: str = '') -> List[Dict[str, Any]]:
        """Get user's rooms only - no global discovery, rooms are private"""
        try:
            # Get only rooms the user is a member of
            user_rooms = db.session.query(Room, RoomMember).join(
                RoomMember, Room.id == RoomMember.room_id
            ).filter(
                RoomMember.user_id == current_user.id,
                RoomMember.role != RoomMemberRole.INVITED  # Only joined rooms, not pending invites
            ).all()
            
            rooms_data = []
            for room, membership in user_rooms:
                # Apply search filter if provided
                if search_query and search_query.lower() not in room.name.lower():
                    continue
                
                # Get member count
                member_count = RoomMember.query.filter_by(room_id=room.id).count()
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'description': f"Private room • {member_count} members",
                    'tags': 'private',
                    'room_type': room.type.value,
                    'participant_count': member_count,
                    'is_public': False,
                    'created_at': room.created_at.isoformat(),
                    'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
                    'auto_translate': True,
                    'is_owner': membership.role == RoomMemberRole.OWNER,
                    'role': membership.role.value,
                    'can_invite': membership.role in [RoomMemberRole.OWNER, RoomMemberRole.ADMIN]
                })
            
            return rooms_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user rooms: {str(e)}")
            return []
    
    def get_featured_rooms(self, current_user) -> List[Dict[str, Any]]:
        """Get user's recently joined rooms - no global featured rooms"""
        try:
            # Get user's recently joined rooms
            recent_rooms = db.session.query(Room, RoomMember).join(
                RoomMember, Room.id == RoomMember.room_id
            ).filter(
                RoomMember.user_id == current_user.id,
                RoomMember.role != RoomMemberRole.INVITED
            ).order_by(RoomMember.joined_at.desc()).limit(6).all()
            
            rooms_data = []
            for room, membership in recent_rooms:
                member_count = RoomMember.query.filter_by(room_id=room.id).count()
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'description': f"Private room • {member_count} members",
                    'tags': 'private',
                    'room_type': room.type.value,
                    'participant_count': member_count,
                    'is_public': False,
                    'created_at': room.created_at.isoformat(),
                    'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
                    'auto_translate': True,
                    'is_owner': membership.role == RoomMemberRole.OWNER,
                    'role': membership.role.value,
                    'recently_joined': True
                })
            
            return rooms_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get recent rooms: {str(e)}")
            return []
    
    def create_room(self, current_user, name: str, description: str, category: str, age_restriction: str, is_private: bool = True, password: str = None, is_discoverable: bool = False) -> Dict[str, Any]:
        """Create a private room - all rooms are private by default"""
        try:
            # All rooms are private - use existing private room creation
            voice_enabled = category == 'voice' or 'voice' in name.lower()
            
            return self.create_private_room(
                owner_id=current_user.id,
                room_name=name,
                room_type="private",
                voice_enabled=voice_enabled,
                is_discoverable=is_discoverable
            )
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create room: {str(e)}")
            return {'error': str(e), 'status': 500}
    
    def join_room(self, current_user, room_id: int, password: str = None) -> Dict[str, Any]:
        """Join a room by ID - only works if user has been invited"""
        try:
            # Check if room exists and user has been invited
            room = db.session.get(Room, room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found',
                    'status': 404
                }
            
            # Check if user has been invited or is already a member
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=current_user.id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You have not been invited to this room',
                    'status': 403
                }
            
            if member.role == RoomMemberRole.INVITED:
                # Accept invitation
                member.role = RoomMemberRole.MEMBER
                member.joined_at = datetime.utcnow()
                db.session.commit()
                
                self.increase_room_activity(room_id, 'invite_used')
                
                self.logger.info(f"🏠 User {current_user.id} accepted invitation to room {room_id}")
                
                return {
                    'success': True,
                    'message': f'Successfully joined {room.name}',
                    'room': {
                        'id': room.id,
                        'name': room.name,
                        'type': room.type.value
                    },
                    'status': 200
                }
            else:
                return {
                    'success': True,
                    'message': 'You are already a member of this room',
                    'room': {
                        'id': room.id,
                        'name': room.name,
                        'type': room.type.value
                    },
                    'status': 200
                }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to join room: {str(e)}")
            return {'error': str(e), 'status': 500}
    
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
                # Get room owner info
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
                    'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
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
            return {
                'success': False,
                'error': str(e)
            }
    
    def decline_room_invite(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Decline a room invitation"""
        try:
            # Find the invitation
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.INVITED
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'Invitation not found'
                }
            
            # Remove the invitation
            db.session.delete(member)
            db.session.commit()
            
            self.logger.info(f"🏠 User {user_id} declined invitation to room {room_id}")
            
            return {
                'success': True,
                'message': 'Invitation declined'
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to decline invite: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def leave_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave a room"""
        try:
            # Find user's membership
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You are not a member of this room'
                }
            
            # Check if user is the owner
            if member.role == RoomMemberRole.OWNER:
                # Transfer ownership or delete room if no other members
                other_members = RoomMember.query.filter(
                    RoomMember.room_id == room_id,
                    RoomMember.user_id != user_id,
                    RoomMember.role != RoomMemberRole.INVITED
                ).all()
                
                if other_members:
                    # Transfer ownership to first admin or member
                    new_owner = next((m for m in other_members if m.role == RoomMemberRole.ADMIN), other_members[0])
                    new_owner.role = RoomMemberRole.OWNER
                    db.session.delete(member)
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'message': 'Left room and transferred ownership'
                    }
                else:
                    # Delete the room if no other members
                    return self.delete_room(user_id, room_id)
            else:
                # Regular member leaving
                db.session.delete(member)
                db.session.commit()
                
                self.logger.info(f"🏠 User {user_id} left room {room_id}")
                
                return {
                    'success': True,
                    'message': 'Successfully left the room'
                }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to leave room: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _can_create_room(self, user) -> bool:
        """Check if user can create rooms - Everyone can create unlimited rooms"""
        return True
    
    def _is_premium_user(self, user) -> bool:
        """Check if user has premium subscription"""
        if hasattr(user, 'privacy_subscription') and user.privacy_subscription:
            from models.subscription_models import SubscriptionTier
            return user.privacy_subscription.tier in [SubscriptionTier.PRIVACY_PREMIUM, SubscriptionTier.ENTERPRISE]
        
        return getattr(user, 'is_premium', False)
    
    def _can_create_voice_room(self, user) -> bool:
        """Check if user can create voice-enabled rooms - Everyone can"""
        return True
    
    def _can_make_discoverable(self, user) -> bool:
        """Check if user can make rooms discoverable - Everyone can"""
        return True
    
    def _get_room_creation_limits(self, user) -> Dict[str, Any]:
        """Get room creation limits based on user tier - Everyone gets same features"""
        return {
            'max_rooms': 999,  # Unlimited for everyone
            'can_create_voice': True,
            'can_make_discoverable': True,
            'can_set_custom_invite_codes': True,
            'unlimited_members': True
        }
    
    def _generate_invite_code(self, room_id: int) -> str:
        """Generate invite code for room"""
        return f"ROOM-{room_id}"
    
    def _initialize_voice_session(self, room_id: int):
        """Initialize voice session for a room"""
        self.active_voice_sessions[room_id] = {
            'participants': [],
            'started_at': datetime.utcnow(),
            'room_id': room_id
        }
        
        self.logger.info(f"🎙️ Voice session initialized for room {room_id}")
    
    def delete_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Delete a room (only owner can do this)"""
        try:
            # Check if user owns the room
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {
                    'success': False,
                    'error': 'You do not own this room'
                }
            
            # Delete all members first
            RoomMember.query.filter_by(room_id=room_id).delete()
            
            # Delete room
            room = db.session.get(Room, room_id)
            if room:
                room_name = room.name
                db.session.delete(room)
                db.session.commit()
                
                self.logger.info(f"🏠 Room deleted: '{room_name}' by user {user_id}")
                
                return {
                    'success': True,
                    'message': f'Room "{room_name}" has been deleted'
                }
            else:
                return {
                    'success': False,
                    'error': 'Room not found'
                }
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to delete room: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_discoverable_rooms(self, current_user, category: str = '', search_query: str = '') -> List[Dict[str, Any]]:
        """Get public/discoverable rooms for discovery"""
        try:
            # Get discoverable rooms that user is NOT a member of
            user_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=current_user.id).subquery()
            
            query = db.session.query(Room).filter(
                Room.is_discoverable == True,
                ~Room.id.in_(user_room_ids)  # Exclude rooms user is already in
            )
            
            # Apply search filter
            if search_query:
                query = query.filter(Room.name.ilike(f'%{search_query}%'))
            
            # Order by activity score and recent activity
            rooms = query.order_by(
                Room.activity_score.desc(),
                Room.created_at.desc()
            ).limit(50).all()
            
            rooms_data = []
            for room in rooms:
                # Get member count
                member_count = RoomMember.query.filter_by(room_id=room.id).count()
                
                # Get room owner info
                owner_member = RoomMember.query.filter_by(
                    room_id=room.id,
                    role=RoomMemberRole.OWNER
                ).first()
                
                owner = None
                if owner_member:
                    owner = db.session.get(User, owner_member.user_id)
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'description': f"Public room • {member_count} members",
                    'tags': 'discoverable',
                    'room_type': room.type.value,
                    'participant_count': member_count,
                    'is_public': True,
                    'is_discoverable': room.is_discoverable,
                    'created_at': room.created_at.isoformat(),
                    'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
                    'auto_translate': True,
                    'activity_score': room.activity_score,
                    'owner_name': owner.display_name or owner.username if owner else 'Unknown',
                    'can_join': True
                })
            
            return rooms_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get discoverable rooms: {str(e)}")
            return []
    
    def get_trending_rooms(self, current_user) -> List[Dict[str, Any]]:
        """Get trending discoverable rooms based on activity"""
        try:
            # Get user's rooms to exclude them
            user_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=current_user.id).subquery()
            
            # Get most active discoverable rooms from last 7 days
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            trending_rooms = db.session.query(Room).filter(
                Room.is_discoverable == True,
                Room.created_at >= week_ago,  # Recent rooms
                Room.activity_score > 10,  # Some activity
                ~Room.id.in_(user_room_ids)  # Not already a member
            ).order_by(
                Room.activity_score.desc()
            ).limit(6).all()
            
            # If not enough recent trending, get top all-time
            if len(trending_rooms) < 6:
                additional_rooms = db.session.query(Room).filter(
                    Room.is_discoverable == True,
                    Room.activity_score > 5,
                    ~Room.id.in_(user_room_ids),
                    ~Room.id.in_([r.id for r in trending_rooms])
                ).order_by(
                    Room.activity_score.desc()
                ).limit(6 - len(trending_rooms)).all()
                
                trending_rooms.extend(additional_rooms)
            
            rooms_data = []
            for room in trending_rooms:
                member_count = RoomMember.query.filter_by(room_id=room.id).count()
                
                # Get room owner info
                owner_member = RoomMember.query.filter_by(
                    room_id=room.id,
                    role=RoomMemberRole.OWNER
                ).first()
                
                owner = None
                if owner_member:
                    owner = db.session.get(User, owner_member.user_id)
                
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'description': f"Trending room • {member_count} members",
                    'tags': 'trending',
                    'room_type': room.type.value,
                    'participant_count': member_count,
                    'is_public': True,
                    'is_discoverable': room.is_discoverable,
                    'created_at': room.created_at.isoformat(),
                    'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
                    'auto_translate': True,
                    'activity_score': room.activity_score,
                    'trending': True,
                    'owner_name': owner.display_name or owner.username if owner else 'Unknown',
                    'can_join': True
                })
            
            return rooms_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get trending rooms: {str(e)}")
            return []
    
    def join_discoverable_room(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join a discoverable room directly (no invite needed)"""
        try:
            # Check if room exists and is discoverable
            room = db.session.get(Room, room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found',
                    'status': 404
                }
            
            if not room.is_discoverable:
                return {
                    'success': False,
                    'error': 'This room is not public',
                    'status': 403
                }
            
            # Check if user already a member
            existing_member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if existing_member:
                return {
                    'success': True,
                    'message': 'You are already a member of this room',
                    'room': {
                        'id': room.id,
                        'name': room.name,
                        'type': room.type.value
                    },
                    'status': 200
                }
            
            # Add user as member
            new_member = RoomMember(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.MEMBER,
                joined_at=datetime.utcnow()
            )
            db.session.add(new_member)
            
            # Increase room activity score
            room.activity_score += 5  # Joining adds to activity
            
            db.session.commit()
            
            self.logger.info(f"🏠 User {user_id} joined discoverable room {room_id}")
            
            return {
                'success': True,
                'message': f'Successfully joined {room.name}',
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'type': room.type.value
                },
                'status': 200
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to join discoverable room: {str(e)}")
            return {'error': str(e), 'status': 500}
    
    def increase_room_activity(self, room_id: int, activity_type: str = 'message') -> None:
        """Increase room activity score for trending calculations"""
        try:
            room = db.session.get(Room, room_id)
            if room:
                # Different activities give different scores
                activity_scores = {
                    'message': 1,
                    'join': 5,
                    'voice_join': 3,
                    'invite_used': 2
                }
                
                score_increase = activity_scores.get(activity_type, 1)
                room.activity_score += score_increase
                room.last_activity = datetime.utcnow()
                
                db.session.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update room activity: {str(e)}")
            db.session.rollback()


    def get_room_settings(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Get room settings for management (requires MANAGE_ROOM permission)"""
        try:
            # Check if user has permission to manage room
            if not self._has_permission(user_id, room_id, 'MANAGE_ROOM'):
                return {
                    'success': False,
                    'error': 'Insufficient permissions to manage room'
                }

            room = db.session.get(Room, room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found'
                }

            # Get room settings (create if doesn't exist)
            settings = room.settings
            if not settings:
                from models.user_models import RoomSettings
                settings = RoomSettings(room_id=room_id)
                db.session.add(settings)
                db.session.commit()

            # Get member list and roles
            members = db.session.query(RoomMember, User).join(User).filter(
                RoomMember.room_id == room_id,
                RoomMember.role.in_([RoomMemberRole.OWNER, RoomMemberRole.ADMIN,
                                   RoomMemberRole.MODERATOR, RoomMemberRole.MEMBER])
            ).all()

            member_data = []
            for member, user in members:
                member_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'display_name': user.display_name or user.username,
                    'role': member.role.value,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                    'is_muted': member.muted_until and member.muted_until > datetime.utcnow() if hasattr(member, 'muted_until') else False,
                    'custom_permissions': member.custom_permissions
                })

            # Get role permissions
            role_permissions = {}
            if hasattr(room, 'role_permissions'):
                for role_perm in room.role_permissions:
                    role_permissions[role_perm.role.value] = json.loads(role_perm.permissions or '[]')

            # Get channels
            channels = []
            if hasattr(room, 'channels'):
                for channel in room.channels:
                    channels.append({
                        'id': channel.id,
                        'name': channel.name,
                        'description': channel.description,
                        'type': channel.channel_type,
                        'position': channel.position,
                        'is_hidden': channel.is_hidden,
                        'required_role': channel.required_role.value if channel.required_role else None,
                        'is_read_only': channel.is_read_only
                    })

            return {
                'success': True,
                'room': {
                    'id': room.id,
                    'name': room.name,
                    'type': room.type.value,
                    'is_discoverable': room.is_discoverable,
                    'activity_score': room.activity_score
                },
                'settings': {
                    'description': settings.room_description,
                    'topic': settings.room_topic,
                    'icon': settings.room_icon,
                    'banner': settings.room_banner,
                    'color': settings.room_color,
                    'message_history_limit': settings.message_history_limit,
                    'slow_mode_seconds': settings.slow_mode_seconds,
                    'require_invite_approval': settings.require_invite_approval,
                    'auto_delete_messages_days': settings.auto_delete_messages_days,
                    'hide_member_list': settings.hide_member_list,
                    'disable_voice_chat': settings.disable_voice_chat,
                    'restrict_file_uploads': settings.restrict_file_uploads,
                    'auto_moderate': settings.auto_moderate,
                    'banned_words': json.loads(settings.banned_words or '[]'),
                    'welcome_message': settings.welcome_message,
                    'rules_text': settings.rules_text
                },
                'members': member_data,
                'role_permissions': role_permissions,
                'channels': channels,
                'available_permissions': [perm.value for perm in RoomPermission],
                'available_roles': [role.value for role in RoomMemberRole if role not in [RoomMemberRole.INVITED, RoomMemberRole.BANNED]]
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get room settings: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_room_settings(self, room_id: int, user_id: int, settings_data: Dict) -> Dict[str, Any]:
        """Update room settings"""
        try:
            # Check permission
            if not self._has_permission(user_id, room_id, 'MANAGE_ROOM'):
                return {
                    'success': False,
                    'error': 'Insufficient permissions to manage room'
                }

            room = db.session.get(Room, room_id)
            if not room:
                return {
                    'success': False,
                    'error': 'Room not found'
                }

            # Get or create settings
            settings = room.settings
            if not settings:
                from models.user_models import RoomSettings
                settings = RoomSettings(room_id=room_id)
                db.session.add(settings)

            # Update room basic info
            if 'room_name' in settings_data:
                room.name = settings_data['room_name'][:100]
            if 'is_discoverable' in settings_data:
                room.is_discoverable = bool(settings_data['is_discoverable'])

            # Update settings
            if 'description' in settings_data:
                settings.room_description = settings_data['description'][:1000]
            if 'topic' in settings_data:
                settings.room_topic = settings_data['topic'][:200]
            if 'color' in settings_data:
                settings.room_color = settings_data['color'][:7]
            if 'message_history_limit' in settings_data:
                settings.message_history_limit = max(100, min(10000, int(settings_data['message_history_limit'])))
            if 'slow_mode_seconds' in settings_data:
                settings.slow_mode_seconds = max(0, min(3600, int(settings_data['slow_mode_seconds'])))
            if 'require_invite_approval' in settings_data:
                settings.require_invite_approval = bool(settings_data['require_invite_approval'])
            if 'auto_delete_messages_days' in settings_data:
                settings.auto_delete_messages_days = max(0, min(365, int(settings_data['auto_delete_messages_days'])))
            if 'hide_member_list' in settings_data:
                settings.hide_member_list = bool(settings_data['hide_member_list'])
            if 'disable_voice_chat' in settings_data:
                settings.disable_voice_chat = bool(settings_data['disable_voice_chat'])
            if 'restrict_file_uploads' in settings_data:
                settings.restrict_file_uploads = bool(settings_data['restrict_file_uploads'])
            if 'auto_moderate' in settings_data:
                settings.auto_moderate = bool(settings_data['auto_moderate'])
            if 'banned_words' in settings_data:
                settings.banned_words = json.dumps(settings_data['banned_words'][:100])  # Limit to 100 words
            if 'welcome_message' in settings_data:
                settings.welcome_message = settings_data['welcome_message'][:500]
            if 'rules_text' in settings_data:
                settings.rules_text = settings_data['rules_text'][:2000]

            settings.updated_at = datetime.utcnow()
            db.session.commit()

            self.logger.info(f"🏠 Room {room_id} settings updated by user {user_id}")

            return {
                'success': True,
                'message': 'Room settings updated successfully'
            }

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to update room settings: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_member_role(self, room_id: int, admin_user_id: int, target_user_id: int, new_role: str) -> Dict[str, Any]:
        """Update a member's role in the room"""
        try:
            # Check if admin has permission
            if not self._has_permission(admin_user_id, room_id, 'MANAGE_ROLES'):
                return {
                    'success': False,
                    'error': 'Insufficient permissions to manage roles'
                }

            # Get admin and target member info
            admin_member = RoomMember.query.filter_by(room_id=room_id, user_id=admin_user_id).first()
            target_member = RoomMember.query.filter_by(room_id=room_id, user_id=target_user_id).first()

            if not admin_member or not target_member:
                return {
                    'success': False,
                    'error': 'Member not found in room'
                }

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
                return {
                    'success': False,
                    'error': 'Cannot assign role equal or higher than your own'
                }

            # Update role
            target_member.role = new_role_enum
            db.session.commit()

            self.logger.info(f"🏠 User {target_user_id} role updated to {new_role} in room {room_id} by {admin_user_id}")

            return {
                'success': True,
                'message': f'Member role updated to {new_role}'
            }

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to update member role: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def kick_member(self, room_id: int, admin_user_id: int, target_user_id: int, reason: str = None) -> Dict[str, Any]:
        """Kick a member from the room"""
        try:
            # Check permission
            if not self._has_permission(admin_user_id, room_id, 'MANAGE_MEMBERS'):
                return {
                    'success': False,
                    'error': 'Insufficient permissions to kick members'
                }

            # Get member info
            target_member = RoomMember.query.filter_by(room_id=room_id, user_id=target_user_id).first()
            admin_member = RoomMember.query.filter_by(room_id=room_id, user_id=admin_user_id).first()

            if not target_member:
                return {
                    'success': False,
                    'error': 'Member not found in room'
                }

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
                return {
                    'success': False,
                    'error': 'Cannot kick member with equal or higher role'
                }

            # Remove member
            db.session.delete(target_member)
            db.session.commit()

            self.logger.info(f"🏠 User {target_user_id} kicked from room {room_id} by {admin_user_id}. Reason: {reason}")

            return {
                'success': True,
                'message': 'Member kicked successfully'
            }

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to kick member: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _has_permission(self, user_id: int, room_id: int, permission: str) -> bool:
        """Check if user has specific permission in room"""
        try:
            member = RoomMember.query.filter_by(room_id=room_id, user_id=user_id).first()
            if not member or member.role in [RoomMemberRole.BANNED, RoomMemberRole.MUTED] if hasattr(RoomMemberRole, 'MUTED') else member.role == RoomMemberRole.BANNED:
                return False

            # Owner has all permissions
            if member.role == RoomMemberRole.OWNER:
                return True

            # Check default role permissions
            default_permissions = self._get_default_role_permissions(member.role)
            if permission in default_permissions:
                return True

            # Check custom permissions for this room
            role_perms = RoomRolePermissions.query.filter_by(
                room_id=room_id, role=member.role
            ).first()

            if role_perms:
                custom_permissions = json.loads(role_perms.permissions or '[]')
                if permission in custom_permissions:
                    return True

            # Check individual custom permissions
            if member.custom_permissions:
                individual_permissions = json.loads(member.custom_permissions)
                if permission in individual_permissions:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error checking permission: {e}")
            return False

    def _get_default_role_permissions(self, role: RoomMemberRole) -> List[str]:
        """Get default permissions for a role"""
        if role == RoomMemberRole.OWNER:
            return [perm.value for perm in RoomPermission]
        elif role == RoomMemberRole.ADMIN:
            return [
                'MANAGE_ROOM', 'MANAGE_MEMBERS', 'MANAGE_ROLES', 'CREATE_INVITE',
                'SEND_MESSAGES', 'VOICE_CHAT', 'UPLOAD_FILES',
                'DELETE_MESSAGES', 'MUTE_MEMBERS', 'BAN_MEMBERS',
                'VIEW_HIDDEN_CHANNELS'
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


# Global instance
_room_service = RoomService()


def get_room_service() -> RoomService:
    """Get the global room service instance"""
    return _room_service