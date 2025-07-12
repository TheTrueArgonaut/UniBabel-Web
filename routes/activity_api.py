"""
Activity API Routes - Microservice Endpoints
Single Responsibility: Activity feed and live updates
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Message, Chat, ChatParticipant, User, UserFriend
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def register_activity_api_routes(app):
    """Register activity API routes with /api/v1 prefix"""
    
    @app.route('/api/v1/activity/recent', methods=['GET'])
    @login_required
    def get_recent_activity():
        """Get recent activity for user's activity feed"""
        try:
            # Get limit parameter
            limit = min(int(request.args.get('limit', 20)), 50)  # Max 50 activities
            
            # Get activities from various sources
            activities = []
            
            # 1. Recent messages from user's chats
            recent_messages = db.session.query(
                Message.content,
                Message.created_at,
                Message.sender_id,
                Chat.name.label('chat_name'),
                Chat.id.label('chat_id'),
                User.username.label('sender_username'),
                User.display_name.label('sender_display_name')
            ).join(
                Chat, Chat.id == Message.chat_id
            ).join(
                ChatParticipant, ChatParticipant.chat_id == Chat.id
            ).join(
                User, User.id == Message.sender_id
            ).filter(
                ChatParticipant.user_id == current_user.id,
                ChatParticipant.status == 'active',
                Message.created_at > datetime.utcnow() - timedelta(hours=24)
            ).order_by(
                Message.created_at.desc()
            ).limit(limit).all()
            
            for msg in recent_messages:
                sender_name = msg.sender_display_name or msg.sender_username
                
                activities.append({
                    'type': 'message',
                    'id': f"msg_{msg.chat_id}_{msg.sender_id}",
                    'title': f"New message in {msg.chat_name}",
                    'content': f"{sender_name}: {msg.content[:100]}{'...' if len(msg.content) > 100 else ''}",
                    'timestamp': msg.created_at.isoformat(),
                    'icon': 'ri-message-3-line',
                    'color': 'blue',
                    'link': f"/chat/{msg.chat_id}",
                    'priority': 'medium'
                })
            
            # 2. Friend requests
            friend_requests = db.session.query(
                UserFriend.created_at,
                UserFriend.status,
                User.username,
                User.display_name,
                User.id
            ).join(
                User, User.id == UserFriend.user_id
            ).filter(
                UserFriend.friend_id == current_user.id,
                UserFriend.status == 'pending',
                UserFriend.created_at > datetime.utcnow() - timedelta(days=7)
            ).order_by(
                UserFriend.created_at.desc()
            ).limit(5).all()
            
            for req in friend_requests:
                sender_name = req.display_name or req.username
                
                activities.append({
                    'type': 'friend_request',
                    'id': f"friend_req_{req.id}",
                    'title': 'New friend request',
                    'content': f"{sender_name} wants to be your friend",
                    'timestamp': req.created_at.isoformat(),
                    'icon': 'ri-user-add-line',
                    'color': 'green',
                    'link': '/friends',
                    'priority': 'high'
                })
            
            # 3. Friends coming online
            friends_online = db.session.query(
                User.username,
                User.display_name,
                User.last_activity,
                User.id
            ).join(
                UserFriend, 
                ((UserFriend.user_id == User.id) & (UserFriend.friend_id == current_user.id)) |
                ((UserFriend.friend_id == User.id) & (UserFriend.user_id == current_user.id))
            ).filter(
                UserFriend.status == 'accepted',
                User.last_activity > datetime.utcnow() - timedelta(minutes=30),
                User.id != current_user.id
            ).order_by(
                User.last_activity.desc()
            ).limit(10).all()
            
            for friend in friends_online:
                friend_name = friend.display_name or friend.username
                time_diff = (datetime.utcnow() - friend.last_activity).total_seconds()
                
                if time_diff < 300:  # Within 5 minutes
                    activities.append({
                        'type': 'friend_online',
                        'id': f"online_{friend.id}",
                        'title': 'Friend is online',
                        'content': f"{friend_name} is now online",
                        'timestamp': friend.last_activity.isoformat(),
                        'icon': 'ri-user-3-line',
                        'color': 'green',
                        'link': f'/profile/{friend.id}',
                        'priority': 'low'
                    })
            
            # 4. New chat invitations
            new_chats = db.session.query(
                Chat.name,
                Chat.created_at,
                Chat.id,
                ChatParticipant.joined_at,
                User.username.label('creator_username'),
                User.display_name.label('creator_display_name')
            ).join(
                ChatParticipant, ChatParticipant.chat_id == Chat.id
            ).join(
                User, User.id == Chat.created_by
            ).filter(
                ChatParticipant.user_id == current_user.id,
                ChatParticipant.status == 'active',
                ChatParticipant.joined_at > datetime.utcnow() - timedelta(hours=24),
                Chat.created_by != current_user.id
            ).order_by(
                ChatParticipant.joined_at.desc()
            ).limit(5).all()
            
            for chat in new_chats:
                creator_name = chat.creator_display_name or chat.creator_username
                
                activities.append({
                    'type': 'chat_invite',
                    'id': f"chat_invite_{chat.id}",
                    'title': 'Added to chat',
                    'content': f"{creator_name} added you to {chat.name}",
                    'timestamp': chat.joined_at.isoformat(),
                    'icon': 'ri-chat-3-line',
                    'color': 'purple',
                    'link': f'/chat/{chat.id}',
                    'priority': 'medium'
                })
            
            # Sort all activities by timestamp (newest first)
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit to requested number
            activities = activities[:limit]
            
            return jsonify({
                'success': True,
                'activities': activities,
                'count': len(activities)
            })
            
        except Exception as e:
            logger.error(f"Error getting recent activity for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load recent activity'
            }), 500
    
    @app.route('/api/v1/activity/user/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_activity(user_id):
        """Get activity for a specific user (if they're friends)"""
        try:
            # Check if they're friends or it's the current user
            if user_id != current_user.id:
                friendship = UserFriend.query.filter(
                    ((UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user_id)) |
                    ((UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id))
                ).filter(UserFriend.status == 'accepted').first()
                
                if not friendship:
                    return jsonify({
                        'success': False,
                        'error': 'Not authorized to view this user\'s activity'
                    }), 403
            
            # Get user info
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            # Get user's recent activity
            activities = []
            
            # Recent messages in shared chats
            shared_messages = db.session.query(
                Message.content,
                Message.created_at,
                Chat.name.label('chat_name'),
                Chat.id.label('chat_id')
            ).join(
                Chat, Chat.id == Message.chat_id
            ).join(
                ChatParticipant, ChatParticipant.chat_id == Chat.id
            ).filter(
                Message.sender_id == user_id,
                ChatParticipant.user_id == current_user.id,  # Only shared chats
                ChatParticipant.status == 'active',
                Message.created_at > datetime.utcnow() - timedelta(days=7)
            ).order_by(
                Message.created_at.desc()
            ).limit(20).all()
            
            for msg in shared_messages:
                activities.append({
                    'type': 'message',
                    'title': f"Message in {msg.chat_name}",
                    'content': msg.content[:100] + ('...' if len(msg.content) > 100 else ''),
                    'timestamp': msg.created_at.isoformat(),
                    'icon': 'ri-message-3-line',
                    'color': 'blue'
                })
            
            # User's online status
            if user.last_activity:
                time_diff = (datetime.utcnow() - user.last_activity).total_seconds()
                if time_diff < 300:  # Within 5 minutes
                    status = 'online'
                elif time_diff < 1800:  # Within 30 minutes
                    status = 'recently_online'
                else:
                    status = 'offline'
                
                activities.append({
                    'type': 'status',
                    'title': 'Status',
                    'content': f"User is {status}",
                    'timestamp': user.last_activity.isoformat(),
                    'icon': 'ri-user-3-line',
                    'color': 'green' if status == 'online' else 'gray'
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'last_activity': user.last_activity.isoformat() if user.last_activity else None
                },
                'activities': activities,
                'count': len(activities)
            })
            
        except Exception as e:
            logger.error(f"Error getting user activity for user {user_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load user activity'
            }), 500
    
    @app.route('/api/v1/activity/<int:activity_id>/read', methods=['POST'])
    @login_required
    def mark_activity_read(activity_id):
        """Mark an activity as read"""
        try:
            # For now, just return success
            # In a real implementation, you'd store read status in database
            return jsonify({
                'success': True,
                'message': 'Activity marked as read'
            })
            
        except Exception as e:
            logger.error(f"Error marking activity {activity_id} as read: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to mark activity as read'
            }), 500