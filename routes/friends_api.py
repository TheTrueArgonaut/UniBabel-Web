"""
Friends API Routes - Microservice Endpoints
Single Responsibility: Friend management operations
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, User, UserFriend
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def register_friends_api_routes(app):
    """Register friends API routes with /api/v1 prefix"""
    
    @app.route('/api/v1/friends', methods=['GET'])
    @login_required
    def get_friends():
        """Get user's friends list with online status"""
        try:
            # Get friends from database
            friends_query = db.session.query(
                User.id,
                User.username,
                User.display_name,
                User.bio,
                User.last_activity,
                UserFriend.created_at
            ).join(
                UserFriend, UserFriend.friend_id == User.id
            ).filter(
                UserFriend.user_id == current_user.id,
                UserFriend.status == 'accepted'
            ).all()
            
            friends_list = []
            for friend in friends_query:
                # Determine online status (active within last 5 minutes)
                is_online = False
                if friend.last_activity:
                    time_diff = (datetime.utcnow() - friend.last_activity).total_seconds()
                    is_online = time_diff < 300  # 5 minutes
                
                # Get avatar from bio if available
                avatar = '👤'  # Default avatar
                activity = None
                if friend.bio:
                    try:
                        import json
                        bio_data = json.loads(friend.bio)
                        avatar = bio_data.get('avatar', '👤')
                        if is_online:
                            activity = bio_data.get('activity', 'Online')
                    except:
                        pass
                
                friends_list.append({
                    'id': friend.id,
                    'username': friend.username,
                    'name': friend.display_name or friend.username,
                    'avatar': avatar,
                    'status': 'online' if is_online else 'offline',
                    'activity': activity,
                    'friendship_date': friend.created_at.isoformat() if friend.created_at else None
                })
            
            return jsonify({
                'success': True,
                'friends': friends_list,
                'count': len(friends_list)
            })
            
        except Exception as e:
            logger.error(f"Error getting friends for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load friends'
            }), 500
    
    @app.route('/api/v1/friends/add', methods=['POST'])
    @login_required
    def add_friend():
        """Send friend request"""
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({
                    'success': False,
                    'error': 'Username is required'
                }), 400
            
            # Find user by username
            target_user = User.query.filter_by(username=username).first()
            if not target_user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Can't add yourself
            if target_user.id == current_user.id:
                return jsonify({
                    'success': False,
                    'error': 'Cannot add yourself as a friend'
                }), 400
            
            # Check if friendship already exists
            existing_friendship = UserFriend.query.filter(
                ((UserFriend.user_id == current_user.id) & (UserFriend.friend_id == target_user.id)) |
                ((UserFriend.user_id == target_user.id) & (UserFriend.friend_id == current_user.id))
            ).first()
            
            if existing_friendship:
                if existing_friendship.status == 'accepted':
                    return jsonify({
                        'success': False,
                        'error': 'Already friends'
                    }), 400
                elif existing_friendship.status == 'pending':
                    return jsonify({
                        'success': False,
                        'error': 'Friend request already sent'
                    }), 400
            
            # Create friend request
            friend_request = UserFriend(
                user_id=current_user.id,
                friend_id=target_user.id,
                status='pending',
                created_at=datetime.utcnow()
            )
            
            db.session.add(friend_request)
            db.session.commit()
            
            logger.info(f"Friend request sent from {current_user.username} to {username}")
            
            return jsonify({
                'success': True,
                'message': f'Friend request sent to @{username}'
            })
            
        except Exception as e:
            logger.error(f"Error adding friend: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to send friend request'
            }), 500
    
    @app.route('/api/v1/friends/<int:friend_id>', methods=['DELETE'])
    @login_required
    def remove_friend(friend_id):
        """Remove friend"""
        try:
            # Find friendship (either direction)
            friendship = UserFriend.query.filter(
                ((UserFriend.user_id == current_user.id) & (UserFriend.friend_id == friend_id)) |
                ((UserFriend.user_id == friend_id) & (UserFriend.friend_id == current_user.id))
            ).first()
            
            if not friendship:
                return jsonify({
                    'success': False,
                    'error': 'Friendship not found'
                }), 404
            
            # Remove friendship
            db.session.delete(friendship)
            db.session.commit()
            
            logger.info(f"Friendship removed between {current_user.id} and {friend_id}")
            
            return jsonify({
                'success': True,
                'message': 'Friend removed'
            })
            
        except Exception as e:
            logger.error(f"Error removing friend: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to remove friend'
            }), 500
    
    @app.route('/api/v1/friends/search', methods=['GET'])
    @login_required
    def search_users():
        """Search for users to add as friends"""
        try:
            query = request.args.get('q', '').strip()
            
            if not query:
                return jsonify({
                    'success': True,
                    'users': []
                })
            
            # Search users by username or display name
            users = User.query.filter(
                (User.username.ilike(f'%{query}%')) |
                (User.display_name.ilike(f'%{query}%'))
            ).filter(
                User.id != current_user.id  # Exclude current user
            ).limit(10).all()
            
            users_list = []
            for user in users:
                # Check if already friends
                is_friend = UserFriend.query.filter(
                    ((UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user.id)) |
                    ((UserFriend.user_id == user.id) & (UserFriend.friend_id == current_user.id))
                ).first()
                
                friendship_status = 'none'
                if is_friend:
                    friendship_status = is_friend.status
                
                users_list.append({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'friendship_status': friendship_status
                })
            
            return jsonify({
                'success': True,
                'users': users_list
            })
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return jsonify({
                'success': False,
                'error': 'Search failed'
            }), 500
    
    @app.route('/api/v1/friends/<int:friend_id>/status', methods=['GET'])
    @login_required
    def get_friend_status(friend_id):
        """Get specific friend's status"""
        try:
            # Check if they're friends
            friendship = UserFriend.query.filter(
                ((UserFriend.user_id == current_user.id) & (UserFriend.friend_id == friend_id)) |
                ((UserFriend.user_id == friend_id) & (UserFriend.friend_id == current_user.id))
            ).filter(UserFriend.status == 'accepted').first()
            
            if not friendship:
                return jsonify({
                    'success': False,
                    'error': 'Not friends'
                }), 404
            
            # Get friend's details
            friend = User.query.get(friend_id)
            if not friend:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Check online status
            is_online = False
            if friend.last_activity:
                time_diff = (datetime.utcnow() - friend.last_activity).total_seconds()
                is_online = time_diff < 300  # 5 minutes
            
            return jsonify({
                'success': True,
                'friend': {
                    'id': friend.id,
                    'username': friend.username,
                    'display_name': friend.display_name,
                    'status': 'online' if is_online else 'offline',
                    'last_activity': friend.last_activity.isoformat() if friend.last_activity else None
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting friend status: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to get friend status'
            }), 500
    
    @app.route('/api/v1/friends/status', methods=['POST'])
    @login_required
    def update_friend_status():
        """Update user's status for friends"""
        try:
            data = request.get_json()
            status = data.get('status', '').strip()
            
            if not status:
                return jsonify({
                    'success': False,
                    'error': 'Status is required'
                }), 400
            
            # Update user's bio with status
            current_user.last_activity = datetime.utcnow()
            
            # Try to update bio with status
            try:
                import json
                bio_data = {}
                if current_user.bio:
                    bio_data = json.loads(current_user.bio)
                
                bio_data['activity'] = status
                current_user.bio = json.dumps(bio_data)
                
            except:
                # If bio parsing fails, create new bio
                current_user.bio = json.dumps({'activity': status})
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Status updated'
            })
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to update status'
            }), 500