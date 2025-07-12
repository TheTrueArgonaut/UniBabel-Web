"""
User Profile Service - SRIMI Microservice
Single Responsibility: User profile data aggregation and management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from models import User, UserType, db
from dataclasses import dataclass

@dataclass
class UserProfileData:
    """Clean user profile data structure"""
    user_id: int
    username: str
    email: str
    display_name: Optional[str]
    user_type: str
    is_online: bool
    is_blocked: bool
    is_premium: bool
    last_seen: Optional[datetime]
    created_at: Optional[datetime]
    block_reason: Optional[str]
    market_value: float = 0.0
    vulnerability_score: float = 0.0

class UserProfileService:
    """Micro-service for user profile operations"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfileData]:
        """Get single user profile"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        return UserProfileData(
            user_id=user.id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            user_type=user.user_type.value if user.user_type else 'Unknown',
            is_online=user.is_online,
            is_blocked=user.is_blocked,
            is_premium=user.is_premium,
            last_seen=user.last_seen,
            created_at=user.created_at,
            block_reason=getattr(user, 'block_reason', None)
        )
    
    def get_user_profiles_batch(self, limit: int = 50, offset: int = 0) -> List[UserProfileData]:
        """Get batch of user profiles"""
        users = User.query.offset(offset).limit(limit).all()
        
        profiles = []
        for user in users:
            profile = UserProfileData(
                user_id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                user_type=user.user_type.value if user.user_type else 'Unknown',
                is_online=user.is_online,
                is_blocked=user.is_blocked,
                is_premium=user.is_premium,
                last_seen=user.last_seen,
                created_at=user.created_at,
                block_reason=getattr(user, 'block_reason', None)
            )
            profiles.append(profile)
        
        return profiles
    
    def search_users(self, search_term: str, limit: int = 50) -> List[UserProfileData]:
        """Search users by username, email, or display name"""
        search_pattern = f"%{search_term.lower()}%"
        
        # Search each field separately to avoid db.or_ issues
        username_matches = User.query.filter(User.username.ilike(search_pattern)).limit(limit).all()
        email_matches = User.query.filter(User.email.ilike(search_pattern)).limit(limit).all()
        display_name_matches = User.query.filter(User.display_name.ilike(search_pattern)).limit(limit).all()
        
        # Combine results and remove duplicates
        all_users = {}
        for user in username_matches + email_matches + display_name_matches:
            all_users[user.id] = user
        
        # Convert to profiles
        profiles = []
        for user in list(all_users.values())[:limit]:
            profile = UserProfileData(
                user_id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                user_type=user.user_type.value if user.user_type else 'Unknown',
                is_online=user.is_online,
                is_blocked=user.is_blocked,
                is_premium=user.is_premium,
                last_seen=user.last_seen,
                created_at=user.created_at,
                block_reason=getattr(user, 'block_reason', None)
            )
            profiles.append(profile)
        
        return profiles
    
    def filter_users_by_status(self, status: str, limit: int = 50) -> List[UserProfileData]:
        """Filter users by status"""
        query = User.query
        
        if status == 'online':
            query = query.filter(User.is_online == True)
        elif status == 'offline':
            query = query.filter(User.is_online == False)
        elif status == 'blocked':
            query = query.filter(User.is_blocked == True)
        elif status == 'premium':
            query = query.filter(User.is_premium == True)
        
        users = query.limit(limit).all()
        
        profiles = []
        for user in users:
            profile = UserProfileData(
                user_id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                user_type=user.user_type.value if user.user_type else 'Unknown',
                is_online=user.is_online,
                is_blocked=user.is_blocked,
                is_premium=user.is_premium,
                last_seen=user.last_seen,
                created_at=user.created_at,
                block_reason=getattr(user, 'block_reason', None)
            )
            profiles.append(profile)
        
        return profiles
    
    def filter_users_by_type(self, user_type: str, limit: int = 50) -> List[UserProfileData]:
        """Filter users by type"""
        query = User.query
        
        if user_type == 'adult':
            query = query.filter(User.user_type == UserType.ADULT)
        elif user_type == 'teen':
            query = query.filter(User.user_type == UserType.TEEN)
        
        users = query.limit(limit).all()
        
        profiles = []
        for user in users:
            profile = UserProfileData(
                user_id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                user_type=user.user_type.value if user.user_type else 'Unknown',
                is_online=user.is_online,
                is_blocked=user.is_blocked,
                is_premium=user.is_premium,
                last_seen=user.last_seen,
                created_at=user.created_at,
                block_reason=getattr(user, 'block_reason', None)
            )
            profiles.append(profile)
        
        return profiles

# Singleton instance
user_profile_service = UserProfileService()