"""
Room Discovery Service - Handle room browsing and discovery
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from models import db, User
from models.user_models import Room, RoomMember, RoomType, RoomMemberRole


class RoomDiscoveryService:
    """Handle room discovery and browsing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔍 Room Discovery Service initialized")
    
    def get_discoverable_rooms(self, user_id: int, category: str = '', search_query: str = '') -> List[Dict[str, Any]]:
        """Get public/discoverable rooms for discovery"""
        try:
            user_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=user_id).subquery()
            
            query = db.session.query(Room).filter(
                Room.is_discoverable == True,
                ~Room.id.in_(user_room_ids)
            )
            
            if search_query:
                query = query.filter(Room.name.ilike(f'%{search_query}%'))
            
            rooms = query.order_by(
                Room.activity_score.desc(),
                Room.created_at.desc()
            ).limit(50).all()
            
            rooms_data = []
            for room in rooms:
                member_count = RoomMember.query.filter_by(room_id=room.id).count()
                
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
    
    def get_trending_rooms(self, user_id: int) -> List[Dict[str, Any]]:
        """Get trending discoverable rooms based on activity"""
        try:
            user_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=user_id).subquery()
            
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            trending_rooms = db.session.query(Room).filter(
                Room.is_discoverable == True,
                Room.created_at >= week_ago,
                Room.activity_score > 10,
                ~Room.id.in_(user_room_ids)
            ).order_by(
                Room.activity_score.desc()
            ).limit(6).all()
            
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
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found', 'status': 404}
            
            if not room.is_discoverable:
                return {'success': False, 'error': 'This room is not public', 'status': 403}
            
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
            
            new_member = RoomMember(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.MEMBER,
                joined_at=datetime.utcnow()
            )
            db.session.add(new_member)
            
            # Increase room activity score
            room.activity_score += 5
            
            db.session.commit()
            
            self.logger.info(f"🔍 User {user_id} joined discoverable room {room_id}")
            
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
    
    def make_room_discoverable(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Make a room discoverable to the public"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Only room owner can make room discoverable'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            room.is_discoverable = True
            db.session.commit()
            
            self.logger.info(f"🔍 Room {room_id} made discoverable by user {user_id}")
            
            return {
                'success': True,
                'message': 'Room is now discoverable to the public',
                'room_id': room_id
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to make room discoverable: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def make_room_private(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Make a room private (not discoverable)"""
        try:
            member = RoomMember.query.filter_by(
                room_id=room_id,
                user_id=user_id,
                role=RoomMemberRole.OWNER
            ).first()
            
            if not member:
                return {'success': False, 'error': 'Only room owner can make room private'}
            
            room = db.session.get(Room, room_id)
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            room.is_discoverable = False
            db.session.commit()
            
            self.logger.info(f"🔍 Room {room_id} made private by user {user_id}")
            
            return {
                'success': True,
                'message': 'Room is now private',
                'room_id': room_id
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Failed to make room private: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def increase_room_activity(self, room_id: int, activity_type: str = 'message') -> None:
        """Increase room activity score for trending calculations"""
        try:
            room = db.session.get(Room, room_id)
            if room:
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
    
    def search_rooms(self, user_id: int, query: str, filter_type: str = 'all') -> List[Dict[str, Any]]:
        """Search for rooms with advanced filtering"""
        try:
            if not query.strip():
                return []
            
            user_room_ids = db.session.query(RoomMember.room_id).filter_by(user_id=user_id).subquery()
            
            search_query = db.session.query(Room).filter(
                Room.is_discoverable == True,
                Room.name.ilike(f'%{query}%'),
                ~Room.id.in_(user_room_ids)
            )
            
            # Apply type filter
            if filter_type == 'voice':
                search_query = search_query.filter(Room.type.in_([RoomType.VOICE_CHAT, RoomType.VOICE_ONLY]))
            elif filter_type == 'text':
                search_query = search_query.filter(Room.type == RoomType.PRIVATE)
            
            rooms = search_query.order_by(
                Room.activity_score.desc(),
                Room.name.asc()
            ).limit(20).all()
            
            return self._format_room_list(rooms)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search rooms: {str(e)}")
            return []
    
    def _format_room_list(self, rooms: List[Room]) -> List[Dict[str, Any]]:
        """Format room list for API response"""
        rooms_data = []
        for room in rooms:
            member_count = RoomMember.query.filter_by(room_id=room.id).count()
            
            rooms_data.append({
                'id': room.id,
                'name': room.name,
                'description': f"Public room • {member_count} members",
                'room_type': room.type.value,
                'participant_count': member_count,
                'is_public': True,
                'is_discoverable': room.is_discoverable,
                'created_at': room.created_at.isoformat(),
                'voice_enabled': room.type in [RoomType.VOICE_CHAT, RoomType.VOICE_ONLY],
                'activity_score': room.activity_score,
                'can_join': True
            })
        
        return rooms_data