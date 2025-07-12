"""
Room Voice Chat Service - Handle WebRTC voice functionality
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from models import db, User
from models.user_models import Room, RoomMember, RoomType, RoomMemberRole


class RoomVoiceService:
    """Handle voice chat functionality for rooms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🎙️ Room Voice Service initialized")
        
        # WebRTC Voice Chat Configuration
        self.voice_config = {
            'stun_servers': [
                'stun:stun.l.google.com:19302',
                'stun:stun1.l.google.com:19302',
                'stun:stun2.l.google.com:19302'
            ],
            'turn_servers': [
                {
                    'urls': 'turn:openrelay.metered.ca:80',
                    'username': 'openrelayproject',
                    'credential': 'openrelayproject'
                }
            ]
        }
        
        # Active voice sessions
        self.active_voice_sessions = {}  # room_id -> session_data
    
    def join_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Join voice chat in a room"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id
            ).first()
            
            if not member:
                return {'success': False, 'error': 'You are not a member of this room'}
            
            room = db.session.get(Room, room_id)
            if not room or room.type not in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY]:
                return {'success': False, 'error': 'This room does not support voice chat'}
            
            user = db.session.get(User, user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Initialize voice session if not exists
            if room_id not in self.active_voice_sessions:
                self._initialize_voice_session(room_id)
            
            voice_session = self.active_voice_sessions[room_id]
            
            # Check if user already in voice chat
            user_in_voice = any(p['user_id'] == user_id for p in voice_session['participants'])
            if user_in_voice:
                return {'success': False, 'error': 'You are already in voice chat'}
            
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
            return {'success': False, 'error': str(e)}
    
    def leave_voice_chat(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Leave voice chat in a room"""
        try:
            if room_id not in self.active_voice_sessions:
                return {'success': False, 'error': 'No active voice session in this room'}
            
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
            return {'success': False, 'error': str(e)}
    
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
                return {'success': False, 'error': 'No active voice session'}
            
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
            
            return {'success': False, 'error': 'User not in voice session'}
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update voice status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def enable_voice_for_room(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Enable voice chat for an existing room"""
        try:
            # Check if user is owner
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Only room owner can enable voice chat'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            if room.type == RoomType.VOICE_CHAT:
                return {'success': False, 'error': 'Voice chat is already enabled'}
            
            # Update room type
            room.type = RoomType.VOICE_CHAT
            db.session.commit()
            
            # Initialize voice session
            self._initialize_voice_session(room_id)
            
            self.logger.info(f"🎙️ Voice chat enabled for room {room_id}")
            
            return {
                'success': True,
                'message': 'Voice chat enabled for room',
                'room_id': room_id,
                'voice_config': self.voice_config
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to enable voice chat: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def disable_voice_for_room(self, room_id: int, user_id: int) -> Dict[str, Any]:
        """Disable voice chat for a room"""
        try:
            # Check if user is owner
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Only room owner can disable voice chat'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            if room.type == RoomType.PRIVATE:
                return {'success': False, 'error': 'Voice chat is already disabled'}
            
            # Update room type
            room.type = RoomType.PRIVATE
            db.session.commit()
            
            # End voice session if active
            if room_id in self.active_voice_sessions:
                del self.active_voice_sessions[room_id]
            
            self.logger.info(f"🎙️ Voice chat disabled for room {room_id}")
            
            return {
                'success': True,
                'message': 'Voice chat disabled for room',
                'room_id': room_id
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to disable voice chat: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _initialize_voice_session(self, room_id: int):
        """Initialize voice session for a room"""
        self.active_voice_sessions[room_id] = {
            'participants': [],
            'started_at': datetime.utcnow(),
            'room_id': room_id
        }
        
        self.logger.info(f"🎙️ Voice session initialized for room {room_id}")
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get WebRTC configuration for voice chat"""
        return self.voice_config