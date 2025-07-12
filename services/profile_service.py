"""
Profile Service
Handles: User profiles, profile updates, profile validation, and profile features
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import current_app
from models import db, User, UserType
import re
import bleach
import json


class ProfileService:
    """
    Focused service for user profile management
    
    Single Responsibility: User profile operations only
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Expanded profile fields
        self.PROFILE_FIELDS = {
            'display_name': {'max_length': 100, 'required': False},
            'bio': {'max_length': 500, 'required': False},
            'country': {'max_length': 50, 'required': False},
            'city': {'max_length': 50, 'required': False},
            'interests': {'max_length': 200, 'required': False},
            'occupation': {'max_length': 100, 'required': False},
            'education': {'max_length': 100, 'required': False},
            'languages_spoken': {'max_length': 200, 'required': False},
            'timezone': {'max_length': 50, 'required': False},
            'favorite_topics': {'max_length': 300, 'required': False},
            'status_message': {'max_length': 150, 'required': False},
            'preferred_language': {'max_length': 10, 'required': True}
        }
    
    def get_user_profile(self, user_id: int, viewer_id: int = None) -> Dict[str, Any]:
        """Get user profile with age-appropriate filtering"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Check if profile is viewable
        if not user.is_discoverable and viewer_id != user_id:
            return {'error': 'Profile not available', 'status': 404}
        
        # Get viewer for age restrictions
        viewer = User.query.get(viewer_id) if viewer_id else None
        
        # Apply age restrictions
        if viewer and not viewer.can_contact_user(user):
            return {'error': 'Cannot view this profile due to age restrictions', 'status': 403}
        
        # Build profile data
        profile_data = {
            'user_id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'bio': user.bio,
            'country': user.country,
            'city': user.city,
            'interests': user.interests,
            'user_type': user.user_type.value,
            'age': user.get_age(),
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'created_at': user.created_at.isoformat(),
            'preferred_language': user.preferred_language,
            'is_discoverable': user.is_discoverable
        }
        
        # Add extended profile fields if they exist
        extended_fields = ['occupation', 'education', 'languages_spoken', 'timezone', 
                          'favorite_topics', 'status_message']
        
        for field in extended_fields:
            if hasattr(user, field):
                profile_data[field] = getattr(user, field)
        
        return {'profile': profile_data, 'status': 200}
    
    def update_user_profile(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile with validation"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Validate update data
        validation_result = self._validate_profile_data(update_data, user)
        if not validation_result['valid']:
            return {
                'error': 'Validation failed',
                'errors': validation_result['errors'],
                'status': 400
            }
        
        # Track updated fields
        updated_fields = []
        
        # Update standard fields
        for field, value in update_data.items():
            if field in self.PROFILE_FIELDS and hasattr(user, field):
                old_value = getattr(user, field)
                if old_value != value:
                    setattr(user, field, value)
                    updated_fields.append(field)
        
        # Clean profile data
        user.clean_profile_data()
        
        # Save changes
        try:
            db.session.commit()
            self.logger.info(f"User {user_id} updated profile fields: {updated_fields}")
            
            return {
                'message': 'Profile updated successfully',
                'updated_fields': updated_fields,
                'status': 200
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Profile update failed for user {user_id}: {str(e)}")
            return {'error': 'Update failed', 'status': 500}
    
    def _validate_profile_data(self, data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Validate profile update data"""
        errors = []
        
        # Check field lengths and formats
        for field, value in data.items():
            if field not in self.PROFILE_FIELDS:
                continue
                
            field_config = self.PROFILE_FIELDS[field]
            
            # Check if value is string when expected
            if value is not None and not isinstance(value, str):
                errors.append(f"{field} must be a string")
                continue
            
            # Check length
            if value and len(value) > field_config['max_length']:
                errors.append(f"{field} must be less than {field_config['max_length']} characters")
            
            # Special validations
            if field == 'display_name' and value:
                # Check uniqueness (case-insensitive, excluding current user)
                existing = User.query.filter(
                    db.func.lower(User.display_name) == value.lower(),
                    User.id != user.id
                ).first()
                if existing:
                    errors.append("Display name already taken")
            
            elif field == 'preferred_language' and value:
                # Validate language code
                valid_languages = ['ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'en-gb', 'en-us', 'es', 'es-419', 'et', 'fi', 'fr', 'he', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'nb', 'nl', 'pl', 'pt', 'pt-br', 'pt-pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'vi', 'zh', 'zh-hans', 'zh-hant']
                if value.lower() not in valid_languages:
                    errors.append("Invalid language code")
            
            elif field == 'interests' and value:
                # Validate interests format (comma-separated)
                interests = [i.strip() for i in value.split(',')]
                if len(interests) > 10:
                    errors.append("Maximum 10 interests allowed")
        
        # Check for profanity in text fields
        profanity_words = ['fuck', 'shit', 'bitch', 'asshole', 'damn', 'hell']
        text_fields = ['display_name', 'bio', 'interests', 'occupation', 'education', 'favorite_topics', 'status_message']
        
        for field in text_fields:
            if field in data and data[field]:
                text = data[field].lower()
                for word in profanity_words:
                    if word in text:
                        errors.append(f"Inappropriate content detected in {field}")
                        break
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def search_profiles(self, query: str, searcher_id: int, limit: int = 20) -> Dict[str, Any]:
        """Search user profiles with age-appropriate filtering"""
        if len(query) < 2:
            return {'profiles': [], 'status': 200}
        
        searcher = User.query.get(searcher_id)
        if not searcher:
            return {'error': 'Invalid searcher', 'status': 404}
        
        # Base query - discoverable users only
        base_query = User.query.filter(
            User.id != searcher_id,
            User.is_discoverable == True,
            User.is_blocked == False
        )
        
        # Search in multiple fields
        search_query = base_query.filter(
            db.or_(
                User.username.ilike(f'%{query}%'),
                User.display_name.ilike(f'%{query}%'),
                User.bio.ilike(f'%{query}%'),
                User.interests.ilike(f'%{query}%'),
                User.country.ilike(f'%{query}%'),
                User.city.ilike(f'%{query}%')
            )
        )
        
        # Apply age-based filtering
        if searcher.user_type == UserType.CHILD:
            # Children can only find other children
            filtered_users = search_query.filter(User.user_type == UserType.CHILD).limit(limit).all()
        elif searcher.user_type == UserType.TEEN:
            # Teens can find teens and adults
            filtered_users = search_query.filter(
                User.user_type.in_([UserType.TEEN, UserType.ADULT])
            ).limit(limit).all()
        else:  # ADULT
            # Adults can find teens and adults
            filtered_users = search_query.filter(
                User.user_type.in_([UserType.TEEN, UserType.ADULT])
            ).limit(limit).all()
        
        # Build response
        profiles = []
        for user in filtered_users:
            profile_data = self.get_user_profile(user.id, searcher_id)
            if profile_data.get('status') == 200:
                profiles.append(profile_data['profile'])
        
        return {'profiles': profiles, 'status': 200}
    
    def get_profile_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user profile statistics"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Calculate profile completeness
        profile_fields = ['display_name', 'bio', 'country', 'city', 'interests']
        completed_fields = sum(1 for field in profile_fields if getattr(user, field))
        completeness = round((completed_fields / len(profile_fields)) * 100)
        
        # Get actual chat count from database
        total_chats = len(user.chat_participations)
        
        # Get actual message count from database
        total_messages = len(user.sent_messages)
        
        # Get languages used from translation history
        languages_used = list(set([log.target_language for log in user.usage_logs if log.target_language]))
        if not languages_used:
            languages_used = [user.preferred_language]
        
        stats = {
            'profile_completeness': completeness,
            'account_age_days': (datetime.utcnow() - user.created_at).days,
            'is_verified': user.is_age_verified and user.is_email_verified,
            'total_chats': total_chats,
            'total_messages': total_messages,
            'languages_used': languages_used,
            'last_activity': user.last_seen.isoformat() if user.last_seen else None
        }
        
        return {'stats': stats, 'status': 200}
    
    def update_status_message(self, user_id: int, status_message: str) -> Dict[str, Any]:
        """Update user status message"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Validate status message
        if len(status_message) > 150:
            return {'error': 'Status message too long (max 150 characters)', 'status': 400}
        
        # Clean and set status
        clean_status = bleach.clean(status_message, tags=[], strip=True)
        user.status_message = clean_status
        
        try:
            db.session.commit()
            return {'message': 'Status updated', 'status': 200}
        except Exception as e:
            db.session.rollback()
            return {'error': 'Update failed', 'status': 500}


# Global instance
_profile_service = ProfileService()


def get_profile_service() -> ProfileService:
    """Get the global profile service instance"""
    return _profile_service