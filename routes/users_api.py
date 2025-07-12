"""
Users API Routes - Microservice Endpoints
Single Responsibility: User profile and preferences management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, User
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def register_users_api_routes(app):
    """Register users API routes with /api/v1 prefix"""
    
    @app.route('/api/v1/users/profile', methods=['GET'])
    @login_required
    def get_profile():
        """Get current user's profile"""
        try:
            # Update last activity
            current_user.last_activity = datetime.utcnow()
            db.session.commit()
            
            # Get user preferences from bio
            preferences = {}
            if current_user.bio:
                try:
                    preferences = json.loads(current_user.bio)
                except json.JSONDecodeError:
                    preferences = {}
            
            profile_data = {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'display_name': current_user.display_name,
                'preferred_language': current_user.preferred_language,
                'country': current_user.country,
                'city': current_user.city,
                'timezone': current_user.timezone,
                'bio': current_user.bio,
                'interests': current_user.interests,
                'occupation': current_user.occupation,
                'education': current_user.education,
                'languages_spoken': current_user.languages_spoken,
                'status_message': current_user.status_message,
                'is_online': current_user.is_online,
                'last_activity': current_user.last_activity.isoformat() if current_user.last_activity else None,
                'created_at': current_user.created_at.isoformat(),
                'user_type': current_user.user_type.value,
                'is_premium': current_user.is_premium,
                'is_verified': current_user.is_verified,
                'preferences': preferences
            }
            
            return jsonify({
                'success': True,
                'profile': profile_data
            })
            
        except Exception as e:
            logger.error(f"Error getting profile for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load profile'
            }), 500
    
    @app.route('/api/v1/users/profile', methods=['PUT'])
    @login_required
    def update_profile():
        """Update current user's profile"""
        try:
            data = request.get_json()
            
            # Update allowed fields
            if 'display_name' in data:
                current_user.display_name = data['display_name'][:100] if data['display_name'] else None
            
            if 'country' in data:
                current_user.country = data['country'][:50] if data['country'] else None
            
            if 'city' in data:
                current_user.city = data['city'][:50] if data['city'] else None
            
            if 'timezone' in data:
                current_user.timezone = data['timezone'][:50] if data['timezone'] else None
            
            if 'interests' in data:
                current_user.interests = data['interests'][:500] if data['interests'] else None
            
            if 'occupation' in data:
                current_user.occupation = data['occupation'][:100] if data['occupation'] else None
            
            if 'education' in data:
                current_user.education = data['education'][:100] if data['education'] else None
            
            if 'languages_spoken' in data:
                current_user.languages_spoken = data['languages_spoken'][:200] if data['languages_spoken'] else None
            
            if 'status_message' in data:
                current_user.status_message = data['status_message'][:150] if data['status_message'] else None
            
            if 'preferred_language' in data:
                current_user.preferred_language = data['preferred_language'][:10] if data['preferred_language'] else 'en'
            
            # Clean profile data
            current_user.clean_profile_data()
            
            db.session.commit()
            
            logger.info(f"Profile updated for user {current_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating profile for user {current_user.id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
    
    @app.route('/api/v1/users/preferences', methods=['GET'])
    @login_required
    def get_preferences():
        """Get user preferences"""
        try:
            # Get preferences from bio field
            preferences = {
                'language': {
                    'preferred': current_user.preferred_language,
                    'autoTranslate': True,
                    'showOriginal': False
                },
                'notifications': {
                    'messages': True,
                    'friend_requests': True,
                    'mentions': True,
                    'system': True
                },
                'privacy': {
                    'discoverable': current_user.is_discoverable,
                    'show_online_status': True,
                    'allow_friend_requests': True
                },
                'theme': {
                    'mode': 'dark',
                    'color': 'default'
                }
            }
            
            # Override with stored preferences if available
            if current_user.bio:
                try:
                    stored_prefs = json.loads(current_user.bio)
                    if isinstance(stored_prefs, dict):
                        preferences.update(stored_prefs)
                except json.JSONDecodeError:
                    pass
            
            return jsonify({
                'success': True,
                'preferences': preferences
            })
            
        except Exception as e:
            logger.error(f"Error getting preferences for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load preferences'
            }), 500
    
    @app.route('/api/v1/users/preferences', methods=['PUT'])
    @login_required
    def update_preferences():
        """Update user preferences"""
        try:
            data = request.get_json()
            
            # Get current preferences
            current_prefs = {}
            if current_user.bio:
                try:
                    current_prefs = json.loads(current_user.bio)
                except json.JSONDecodeError:
                    current_prefs = {}
            
            # Update preferences
            if 'language' in data:
                current_prefs['language'] = data['language']
                # Update preferred language in user table
                if 'preferred' in data['language']:
                    current_user.preferred_language = data['language']['preferred']
            
            if 'notifications' in data:
                current_prefs['notifications'] = data['notifications']
            
            if 'privacy' in data:
                current_prefs['privacy'] = data['privacy']
                # Update discoverable setting
                if 'discoverable' in data['privacy']:
                    current_user.is_discoverable = data['privacy']['discoverable']
            
            if 'theme' in data:
                current_prefs['theme'] = data['theme']
            
            # Store preferences in bio field
            current_user.bio = json.dumps(current_prefs)
            
            db.session.commit()
            
            logger.info(f"Preferences updated for user {current_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Preferences updated successfully'
            })
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {current_user.id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to update preferences'
            }), 500
    
    @app.route('/api/v1/users/avatar', methods=['POST'])
    @login_required
    def upload_avatar():
        """Upload user avatar"""
        try:
            # For now, just return success
            # In a real implementation, you'd handle file upload
            return jsonify({
                'success': True,
                'message': 'Avatar upload not implemented yet',
                'avatar_url': '/static/img/default-avatar.png'
            })
            
        except Exception as e:
            logger.error(f"Error uploading avatar for user {current_user.id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to upload avatar'
            }), 500
    
    @app.route('/api/v1/users/search', methods=['GET'])
    @login_required
    def search_users():
        """Search for users"""
        try:
            query = request.args.get('q', '').strip()
            limit = min(int(request.args.get('limit', 10)), 50)
            
            if not query:
                return jsonify({
                    'success': True,
                    'users': []
                })
            
            # Search users
            users = User.query.filter(
                (User.username.ilike(f'%{query}%')) |
                (User.display_name.ilike(f'%{query}%'))
            ).filter(
                User.id != current_user.id,  # Exclude current user
                User.is_discoverable == True,
                User.is_blocked == False
            ).limit(limit).all()
            
            users_list = []
            for user in users:
                users_list.append({
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'country': user.country,
                    'city': user.city,
                    'languages_spoken': user.languages_spoken,
                    'interests': user.interests,
                    'is_online': user.is_online,
                    'last_activity': user.last_activity.isoformat() if user.last_activity else None
                })
            
            return jsonify({
                'success': True,
                'users': users_list,
                'count': len(users_list)
            })
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return jsonify({
                'success': False,
                'error': 'Search failed'
            }), 500
    
    @app.route('/api/v1/users/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_profile(user_id):
        """Get public profile of a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
            
            if not user.is_discoverable and user.id != current_user.id:
                return jsonify({
                    'success': False,
                    'error': 'User profile is private'
                }), 403
            
            # Check online status
            is_online = False
            if user.last_activity:
                time_diff = (datetime.utcnow() - user.last_activity).total_seconds()
                is_online = time_diff < 300  # 5 minutes
            
            profile_data = {
                'id': user.id,
                'username': user.username,
                'display_name': user.display_name,
                'country': user.country,
                'city': user.city,
                'interests': user.interests,
                'occupation': user.occupation,
                'education': user.education,
                'languages_spoken': user.languages_spoken,
                'status_message': user.status_message,
                'is_online': is_online,
                'last_activity': user.last_activity.isoformat() if user.last_activity else None,
                'created_at': user.created_at.isoformat(),
                'user_type': user.user_type.value,
                'is_verified': user.is_verified
            }
            
            return jsonify({
                'success': True,
                'profile': profile_data
            })
            
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load user profile'
            }), 500
    
    @app.route('/api/v1/users/online-status', methods=['POST'])
    @login_required
    def update_online_status():
        """Update user's online status"""
        try:
            data = request.get_json()
            is_online = data.get('online', True)
            
            current_user.is_online = is_online
            current_user.last_activity = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Online status updated'
            })
            
        except Exception as e:
            logger.error(f"Error updating online status for user {current_user.id}: {e}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': 'Failed to update online status'
            }), 500