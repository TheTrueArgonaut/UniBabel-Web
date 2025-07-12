"""User Models Microservice
Handles: User accounts, profiles, authentication, and personal data
"""

from flask_login import UserMixin
from datetime import datetime, date, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import enum
import re
import bleach
import secrets
import string

# Import db from parent package
from . import db

# Initialize Argon2 password hasher
ph = PasswordHasher()

class UserType(enum.Enum):
    CHILD = "child"  # Under 13
    TEEN = "teen"    # 13-17
    ADULT = "adult"  # 18+

class RoomType(enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    VOICE_ONLY = "voice_only"
    VOICE_CHAT = "voice_chat"  # Chat + Voice capabilities

class RoomMemberRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    INVITED = "invited"
    MUTED = "muted"
    BANNED = "banned"

class RoomPermission(enum.Enum):
    # Management permissions
    MANAGE_ROOM = "manage_room"           # Edit room settings
    MANAGE_MEMBERS = "manage_members"     # Kick/ban members
    MANAGE_ROLES = "manage_roles"         # Assign roles to members
    CREATE_INVITE = "create_invite"       # Create invite codes
    
    # Content permissions
    SEND_MESSAGES = "send_messages"       # Send messages in room
    VOICE_CHAT = "voice_chat"            # Join voice chat
    UPLOAD_FILES = "upload_files"         # Upload files/media
    
    # Moderation permissions
    DELETE_MESSAGES = "delete_messages"   # Delete other's messages
    MUTE_MEMBERS = "mute_members"         # Mute/unmute members
    BAN_MEMBERS = "ban_members"           # Ban members from room
    
    # Special permissions
    VIEW_HIDDEN_CHANNELS = "view_hidden_channels"  # See hidden room sections
    BYPASS_RESTRICTIONS = "bypass_restrictions"    # Bypass all restrictions

class FriendGroupType(enum.Enum):
    BABEL_GROUP = "babel_group"  # For direct babel posts
    CHAT_GROUP = "chat_group"    # For group chats
    MIXED = "mixed"              # Both babel and chat

class FriendGroupRole(enum.Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"

class Room(db.Model):
    """Private room model for custom rooms with invites and voice chat features"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(RoomType), nullable=False, default=RoomType.PRIVATE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Discoverability and trending
    is_discoverable = db.Column(db.Boolean, default=False, index=True)
    activity_score = db.Column(db.Integer, default=0, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    owner = db.relationship('User', backref='rooms')
    members = db.relationship('RoomMember', backref='room')
    
    # Add composite indexes for trending queries
    __table_args__ = (
        db.Index('idx_room_discoverable_activity', 'is_discoverable', 'activity_score'),
        db.Index('idx_room_trending', 'is_discoverable', 'activity_score', 'created_at'),
    )

class RoomMember(db.Model):
    """Room member model for managing room membership and roles"""
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    role = db.Column(db.Enum(RoomMemberRole), nullable=False, default=RoomMemberRole.MEMBER)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    joined_at = db.Column(db.DateTime)
    
    # Custom permissions (JSON field for role overrides)
    custom_permissions = db.Column(db.Text)  # JSON string of permission overrides
    muted_until = db.Column(db.DateTime)     # Temporary mute expiration
    banned_reason = db.Column(db.Text)       # Ban reason if applicable
    
    # Relationship
    user = db.relationship('User', backref='room_memberships')

class RoomRolePermissions(db.Model):
    """Custom role permissions for rooms"""
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    role = db.Column(db.Enum(RoomMemberRole), nullable=False)
    permissions = db.Column(db.Text, nullable=False)  # JSON array of permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    room = db.relationship('Room', backref='role_permissions')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('room_id', 'role', name='unique_room_role_permissions'),
    )

class RoomSettings(db.Model):
    """Room customization settings"""
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, unique=True, index=True)
    
    # Room appearance
    room_description = db.Column(db.Text)
    room_topic = db.Column(db.String(200))
    room_icon = db.Column(db.String(200))  # URL or filename
    room_banner = db.Column(db.String(200))  # URL or filename
    room_color = db.Column(db.String(7))  # Hex color code
    
    # Room behavior
    message_history_limit = db.Column(db.Integer, default=1000)
    slow_mode_seconds = db.Column(db.Integer, default=0)  # Message cooldown
    require_invite_approval = db.Column(db.Boolean, default=False)
    auto_delete_messages_days = db.Column(db.Integer, default=0)  # 0 = never
    
    # Privacy settings
    hide_member_list = db.Column(db.Boolean, default=False)
    disable_voice_chat = db.Column(db.Boolean, default=False)
    restrict_file_uploads = db.Column(db.Boolean, default=False)
    
    # Moderation
    auto_moderate = db.Column(db.Boolean, default=True)
    banned_words = db.Column(db.Text)  # JSON array of banned words
    welcome_message = db.Column(db.Text)
    rules_text = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    room = db.relationship('Room', backref='settings', uselist=False)

class RoomChannel(db.Model):
    """Room channels/sections for organization"""
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    channel_type = db.Column(db.String(20), default='text')  # text, voice, announcement
    position = db.Column(db.Integer, default=0)
    
    # Privacy settings
    is_hidden = db.Column(db.Boolean, default=False)
    required_role = db.Column(db.Enum(RoomMemberRole), nullable=True)  # Minimum role to access
    
    # Channel settings
    is_read_only = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    room = db.relationship('Room', backref='channels')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_room_channel_position', 'room_id', 'position'),
    )

class FriendGroup(db.Model):
    """Friend group model for direct babel posts and group chats"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(FriendGroupType), nullable=False, default=FriendGroupType.MIXED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Relationship
    creator = db.relationship('User', backref='friend_groups')
    members = db.relationship('FriendGroupMember', backref='friend_group')

class FriendGroupMember(db.Model):
    """Friend group member model for managing group membership and roles"""
    id = db.Column(db.Integer, primary_key=True)
    friend_group_id = db.Column(db.Integer, db.ForeignKey('friend_group.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    role = db.Column(db.Enum(FriendGroupRole), nullable=False, default=FriendGroupRole.MEMBER)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationship
    user = db.relationship('User', backref='friend_group_memberships')

class UserFriend(db.Model):
    """User friendship model for managing friend relationships"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='sent_friend_requests')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='received_friend_requests')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
        db.Index('idx_user_friend_status', 'user_id', 'status'),
        db.Index('idx_friend_status', 'friend_id', 'status'),
    )

class User(UserMixin, db.Model):
    """Core user model with authentication and profile data"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Argon2 needs more space
    preferred_language = db.Column(db.String(10), default='en', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_online = db.Column(db.Boolean, default=False, index=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Age verification & protection
    birth_date = db.Column(db.Date, nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False, index=True)
    is_age_verified = db.Column(db.Boolean, default=False, index=True)
    parent_email = db.Column(db.String(120))  # For minors
    
    # Parental consent fields (added for registration service)
    parent_name = db.Column(db.String(100))  # Parent/guardian name
    parent_relationship = db.Column(db.String(50))  # Parent, guardian, etc.
    parental_consent_verified = db.Column(db.Boolean, default=False, index=True)
    parental_consent_date = db.Column(db.DateTime)  # When consent was given
    requires_parent_permission = db.Column(db.Boolean, default=False, index=True)
    
    # Discovery features
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    country = db.Column(db.String(50), index=True)
    city = db.Column(db.String(50), index=True)
    interests = db.Column(db.Text)  # JSON string of interests
    is_discoverable = db.Column(db.Boolean, default=True, index=True)
    
    # Extended profile fields
    occupation = db.Column(db.String(100))
    education = db.Column(db.String(100))
    languages_spoken = db.Column(db.String(200))  # Comma-separated list
    timezone = db.Column(db.String(50))
    favorite_topics = db.Column(db.Text)  # What they like to chat about
    status_message = db.Column(db.String(150))  # Current status/mood
    
    # Safety features
    is_blocked = db.Column(db.Boolean, default=False, index=True)
    block_reason = db.Column(db.Text)
    reported_count = db.Column(db.Integer, default=0)
    
    # Account status
    is_email_verified = db.Column(db.Boolean, default=False, index=True)
    email_verification_token = db.Column(db.String(100))
    password_reset_token = db.Column(db.String(100))
    password_reset_expires = db.Column(db.DateTime)
    
    # Admin privileges for data vampire management
    is_admin = db.Column(db.Boolean, default=False, index=True)
    is_premium = db.Column(db.Boolean, default=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, index=True)
    is_data_vampire_admin = db.Column(db.Boolean, default=False, index=True)
    can_access_all_data = db.Column(db.Boolean, default=False, index=True)
    can_manage_sales = db.Column(db.Boolean, default=False, index=True)
    can_export_data = db.Column(db.Boolean, default=False, index=True)
    
    # Legal compliance and chat logging
    admin_logging_declined = db.Column(db.Boolean, default=False, index=True)
    admin_logging_declined_date = db.Column(db.DateTime, nullable=True)
    
    # 🧛‍♂️ DATA HARVESTING ELIGIBILITY (Set at registration)
    is_data_harvest_eligible = db.Column(db.Boolean, default=False, index=True)
    data_collection_blocked = db.Column(db.Boolean, default=True, index=True)
    harvest_block_reason = db.Column(db.String(100), default='age_verification_pending')
    estimated_data_value = db.Column(db.Float, default=0.0, index=True)
    
    # 💰 SUBSCRIPTION & DATA COLLECTION (Business Model)
    data_collection_enabled = db.Column(db.Boolean, default=True, index=True)  # Core business model
    subscription_tier = db.Column(db.String(20), default='free', index=True)  # free, premium_monthly, premium_annual
    subscription_status = db.Column(db.String(20), default='active', index=True)  # active, cancelled, past_due, incomplete
    stripe_customer_id = db.Column(db.String(100), index=True)  # Stripe customer ID
    stripe_subscription_id = db.Column(db.String(100), index=True)  # Stripe subscription ID
    subscription_created_at = db.Column(db.DateTime)
    subscription_updated_at = db.Column(db.DateTime)
    subscription_cancelled_at = db.Column(db.DateTime)
    
    # Business Logic: Free users = data collection ON, Premium users = data collection OFF
    # Admin can override for legal/compliance reasons
    data_collection_override = db.Column(db.Boolean, default=False, index=True)  # Admin override
    data_collection_override_reason = db.Column(db.String(200))  # Legal/compliance reason
    data_collection_override_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who made override
    data_collection_override_at = db.Column(db.DateTime)  # When override was made
    
    # Market Value Tracking (for data monetization)
    market_value = db.Column(db.Float, default=0.0, index=True)  # Estimated user data value
    data_points_collected = db.Column(db.Integer, default=0)  # Total data points collected
    last_data_collection = db.Column(db.DateTime)  # Last time data was collected
    
    # Privacy Settings (granular control)
    collect_translation_history = db.Column(db.Boolean, default=True)  # Translation data
    collect_chat_logs = db.Column(db.Boolean, default=True)  # Chat messages
    collect_usage_analytics = db.Column(db.Boolean, default=True)  # Behavior analytics
    collect_location_data = db.Column(db.Boolean, default=True)  # IP geolocation
    collect_device_info = db.Column(db.Boolean, default=True)  # Device fingerprinting
    
    # Add composite indexes for common queries
    __table_args__ = (
        db.Index('idx_user_search', 'username', 'is_discoverable', 'is_blocked'),
        db.Index('idx_user_type_discoverable', 'user_type', 'is_discoverable', 'is_blocked'),
        db.Index('idx_user_location', 'country', 'city', 'is_discoverable'),
        db.Index('idx_user_activity', 'is_online', 'last_seen'),
        db.Index('idx_subscription_status', 'subscription_tier', 'subscription_status'),
        db.Index('idx_data_collection', 'data_collection_enabled', 'subscription_tier'),
    )
    
    # Authentication methods
    def set_password(self, password):
        """Hash and set user password using Argon2"""
        if not self.validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        self.password_hash = ph.hash(password)
    
    def check_password(self, password):
        """Verify user password using Argon2"""
        try:
            ph.verify(self.password_hash, password)
            
            # Check if password needs rehashing (Argon2 handles this automatically)
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                db.session.commit()
            
            return True
        except (VerifyMismatchError, InvalidHash):
            return False
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase, lowercase, digit, and special char
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 30:
            return False, "Username must be 3-30 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        # Check for inappropriate words (basic list)
        inappropriate_words = ['admin', 'moderator', 'system', 'null', 'undefined']
        if username.lower() in inappropriate_words:
            return False, "Username not allowed"
        
        return True, "Valid"
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Check for disposable email domains (basic list)
        disposable_domains = ['10minutemail.com', 'tempmail.org', 'guerrillamail.com']
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            return False, "Disposable email addresses not allowed"
        
        return True, "Valid"
    
    def clean_profile_data(self):
        """Sanitize user profile data"""
        if self.display_name:
            self.display_name = bleach.clean(self.display_name, tags=[], strip=True)[:100]
        
        if self.bio:
            # Allow basic formatting but strip dangerous tags
            allowed_tags = ['b', 'i', 'em', 'strong']
            self.bio = bleach.clean(self.bio, tags=allowed_tags, strip=True)[:500]
        
        if self.country:
            self.country = bleach.clean(self.country, tags=[], strip=True)[:50]
        
        if self.city:
            self.city = bleach.clean(self.city, tags=[], strip=True)[:50]
        
        if self.interests:
            self.interests = bleach.clean(self.interests, tags=[], strip=True)[:200]
        
        if self.occupation:
            self.occupation = bleach.clean(self.occupation, tags=[], strip=True)[:100]
        
        if self.education:
            self.education = bleach.clean(self.education, tags=[], strip=True)[:100]
        
        if self.languages_spoken:
            self.languages_spoken = bleach.clean(self.languages_spoken, tags=[], strip=True)[:200]
        
        if self.timezone:
            self.timezone = bleach.clean(self.timezone, tags=[], strip=True)[:50]
        
        if self.favorite_topics:
            self.favorite_topics = bleach.clean(self.favorite_topics, tags=[], strip=True)[:500]
        
        if self.status_message:
            self.status_message = bleach.clean(self.status_message, tags=[], strip=True)[:150]
    
    # Age and type methods
    def get_age(self):
        """Calculate user's current age"""
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    def determine_user_type(self):
        """Determine user type based on age"""
        age = self.get_age()
        if age < 13:
            return UserType.CHILD
        elif age < 18:
            return UserType.TEEN
        else:
            return UserType.ADULT
    
    def update_user_type(self):
        """Update user type based on current age"""
        old_type = self.user_type
        new_type = self.determine_user_type()
        
        if old_type != new_type:
            self.user_type = new_type
            db.session.commit()
            return True
        return False
    
    # Safety methods
    def can_join_room(self, room_type):
        """Check if user can join specific room type"""
        if room_type == RoomType.KIDS_ONLY:
            return self.user_type == UserType.CHILD
        elif room_type == RoomType.TEENS_ONLY:
            return self.user_type == UserType.TEEN
        elif room_type == RoomType.ADULTS_ONLY:
            return self.user_type == UserType.ADULT
        return True  # PUBLIC and PRIVATE rooms
    
    def is_minor(self):
        """Check if user is under 18"""
        return self.user_type in [UserType.CHILD, UserType.TEEN]
    
    def requires_parent_consent(self):
        """Check if user requires parent consent"""
        return self.user_type == UserType.CHILD
    
    def can_contact_user(self, other_user):
        """Check if current user can contact/view another user based on age restrictions"""
        if self.user_type == UserType.CHILD:
            # Children can only contact other children
            return other_user.user_type == UserType.CHILD
        elif self.user_type == UserType.TEEN:
            # Teens can contact teens and adults
            return other_user.user_type in [UserType.TEEN, UserType.ADULT]
        else:  # ADULT
            # Adults can contact teens and adults
            return other_user.user_type in [UserType.TEEN, UserType.ADULT]
    
    # Serialization
    def to_dict(self, include_private=False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'preferred_language': self.preferred_language,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'user_type': self.user_type.value,
            'country': self.country,
            'city': self.city,
            'bio': self.bio,
            'interests': self.interests,
            'is_discoverable': self.is_discoverable,
            'occupation': self.occupation,
            'education': self.education,
            'languages_spoken': self.languages_spoken,
            'timezone': self.timezone,
            'favorite_topics': self.favorite_topics,
            'status_message': self.status_message,
            'created_at': self.created_at.isoformat()
        }
        
        if include_private:
            data.update({
                'email': self.email,
                'is_age_verified': self.is_age_verified,
                'parent_email': self.parent_email,
                'is_blocked': self.is_blocked,
                'reported_count': self.reported_count
            })
        
        return data
    
    def can_access_voice_chat(self):
        """Check if user can access voice chat features"""
        # Voice chat could be a premium feature
        if hasattr(self, 'privacy_subscription') and self.privacy_subscription:
            return self.privacy_subscription.tier != 'free'
        return False  # Free users can't use voice chat
    
    # 💰 SUBSCRIPTION & DATA COLLECTION METHODS
    def should_collect_data(self):
        """
        Determine if data should be collected for this user
        Business Logic:
        - Free users: Data collection ON (they pay with data)
        - Premium users: Data collection OFF (they paid for privacy)
        - Admin override: Respects admin decision (legal/compliance)
        """
        # Admin override takes precedence
        if self.data_collection_override:
            return self.data_collection_enabled
        
        # Business model logic
        if self.subscription_tier == 'free':
            return True  # Free users pay with data
        else:
            return False  # Premium users paid for privacy
    
    def can_collect_data_type(self, data_type):
        """Check if specific data type can be collected"""
        if not self.should_collect_data():
            return False
        
        # Check granular permissions
        data_type_mapping = {
            'translation_history': self.collect_translation_history,
            'chat_logs': self.collect_chat_logs,
            'usage_analytics': self.collect_usage_analytics,
            'location_data': self.collect_location_data,
            'device_info': self.collect_device_info,
        }
        
        return data_type_mapping.get(data_type, False)
    
    def toggle_data_collection(self, admin_user_id=None, reason=None):
        """
        Toggle data collection for this user
        Used by admins for legal/compliance reasons
        """
        if admin_user_id:
            # Admin override
            self.data_collection_override = True
            self.data_collection_enabled = not self.data_collection_enabled
            self.data_collection_override_reason = reason
            self.data_collection_override_by = admin_user_id
            self.data_collection_override_at = datetime.utcnow()
        else:
            # User toggle (only affects granular settings, not business model)
            self.data_collection_enabled = not self.data_collection_enabled
        
        db.session.commit()
        return self.data_collection_enabled
    
    def upgrade_to_premium(self, tier='premium_monthly', stripe_customer_id=None, stripe_subscription_id=None):
        """
        Upgrade user to premium subscription
        Automatically disables data collection (they paid for privacy)
        """
        self.subscription_tier = tier
        self.subscription_status = 'active'
        self.stripe_customer_id = stripe_customer_id
        self.stripe_subscription_id = stripe_subscription_id
        self.subscription_created_at = datetime.utcnow()
        self.subscription_updated_at = datetime.utcnow()
        
        # Premium users get privacy by default
        if not self.data_collection_override:
            self.data_collection_enabled = False
        
        db.session.commit()
        return True
    
    def downgrade_to_free(self, reason='subscription_cancelled'):
        """
        Downgrade user to free tier
        Automatically enables data collection (they pay with data)
        """
        self.subscription_tier = 'free'
        self.subscription_status = 'cancelled'
        self.subscription_cancelled_at = datetime.utcnow()
        self.subscription_updated_at = datetime.utcnow()
        
        # Free users pay with data
        if not self.data_collection_override:
            self.data_collection_enabled = True
        
        db.session.commit()
        return True
    
    def calculate_market_value(self):
        """
        Calculate estimated market value of user's data
        Based on data points collected and user demographics
        """
        base_value = 0.0
        
        # Demographics multiplier
        if self.user_type == UserType.ADULT:
            base_value += 2.0  # Adults more valuable
        elif self.user_type == UserType.TEEN:
            base_value += 1.5  # Teens valuable but limited
        else:
            base_value += 0.5  # Children heavily restricted
        
        # Data richness multiplier
        if self.data_points_collected > 1000:
            base_value *= 2.0
        elif self.data_points_collected > 500:
            base_value *= 1.5
        elif self.data_points_collected > 100:
            base_value *= 1.2
        
        # Activity multiplier
        if self.is_online:
            base_value *= 1.1
        
        # Language/location multiplier
        if self.country in ['US', 'CA', 'GB', 'AU', 'DE', 'FR']:
            base_value *= 1.3  # High-value markets
        
        self.market_value = round(base_value, 2)
        db.session.commit()
        return self.market_value
    
    def increment_data_collection(self, data_type=None, value=1.0):
        """
        Increment data collection counter and update market value
        """
        if not self.should_collect_data():
            return False
        
        if data_type and not self.can_collect_data_type(data_type):
            return False
        
        self.data_points_collected += 1
        self.last_data_collection = datetime.utcnow()
        
        # Recalculate market value periodically
        if self.data_points_collected % 10 == 0:
            self.calculate_market_value()
        
        db.session.commit()
        return True
    
    def get_subscription_info(self):
        """Get comprehensive subscription information"""
        return {
            'tier': self.subscription_tier,
            'status': self.subscription_status,
            'data_collection_enabled': self.should_collect_data(),
            'data_collection_override': self.data_collection_override,
            'market_value': self.market_value,
            'data_points_collected': self.data_points_collected,
            'stripe_customer_id': self.stripe_customer_id,
            'subscription_created_at': self.subscription_created_at.isoformat() if self.subscription_created_at else None,
            'subscription_updated_at': self.subscription_updated_at.isoformat() if self.subscription_updated_at else None,
            'privacy_settings': {
                'collect_translation_history': self.collect_translation_history,
                'collect_chat_logs': self.collect_chat_logs,
                'collect_usage_analytics': self.collect_usage_analytics,
                'collect_location_data': self.collect_location_data,
                'collect_device_info': self.collect_device_info,
            }
        }
    
    def create_friend_group(self, group_name, group_type=FriendGroupType.MIXED):
        """Create a friend group for babel posts and chats"""
        friend_group = FriendGroup(
            name=group_name,
            type=group_type,
            creator_id=self.id
        )
        db.session.add(friend_group)
        db.session.flush()  # Get the group ID
        
        # Add creator as admin member
        creator_member = FriendGroupMember(
            friend_group_id=friend_group.id,
            user_id=self.id,
            role=FriendGroupRole.CREATOR,
            joined_at=datetime.utcnow()
        )
        db.session.add(creator_member)
        db.session.commit()
        
        return friend_group
    
    def add_friend_to_group(self, friend_group_id, friend_user_id):
        """Add a friend to a friend group"""
        # Check if user has permission (creator or admin)
        member = FriendGroupMember.query.filter_by(
            friend_group_id=friend_group_id,
            user_id=self.id
        ).first()
        
        if not member or member.role not in [FriendGroupRole.CREATOR, FriendGroupRole.ADMIN]:
            return False
        
        # Check if friend already in group
        existing_member = FriendGroupMember.query.filter_by(
            friend_group_id=friend_group_id,
            user_id=friend_user_id
        ).first()
        
        if existing_member:
            return False
        
        # Add friend to group
        new_member = FriendGroupMember(
            friend_group_id=friend_group_id,
            user_id=friend_user_id,
            role=FriendGroupRole.MEMBER,
            joined_at=datetime.utcnow()
        )
        db.session.add(new_member)
        db.session.commit()
        
        return True
    
    def get_user_friend_groups(self):
        """Get all friend groups this user is a member of"""
        return db.session.query(FriendGroup).join(FriendGroupMember).filter(
            FriendGroupMember.user_id == self.id
        ).all()
    
    def can_post_to_group(self, friend_group_id):
        """Check if user can post babel content to a friend group"""
        member = FriendGroupMember.query.filter_by(
            friend_group_id=friend_group_id,
            user_id=self.id
        ).first()
        
        return member is not None
    
    def can_access_group_chat(self, friend_group_id):
        """Check if user can access friend group chat"""
        member = FriendGroupMember.query.filter_by(
            friend_group_id=friend_group_id,
            user_id=self.id
        ).first()
        
        return member is not None

class UserCommonPhrase(db.Model):
    """Store user's most common phrases for instant translation caching"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    phrase = db.Column(db.String(500), nullable=False)
    usage_count = db.Column(db.Integer, default=1, index=True)
    last_used = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='common_phrases')
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_user_phrase', 'user_id', 'phrase'),
        db.Index('idx_user_phrase_usage', 'user_id', 'usage_count'),
        db.Index('idx_phrase_usage', 'phrase', 'usage_count'),
    )
    
    def increment_usage(self):
        """Increment usage count and update last used timestamp"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def add_or_update_phrase(cls, user_id, phrase):
        """Add new phrase or increment existing one"""
        existing = cls.query.filter_by(user_id=user_id, phrase=phrase).first()
        
        if existing:
            existing.increment_usage()
            return existing
        else:
            new_phrase = cls(user_id=user_id, phrase=phrase)
            db.session.add(new_phrase)
            db.session.commit()
            return new_phrase
    
    @classmethod
    def get_top_phrases(cls, user_id, limit=20):
        """Get user's most common phrases for caching"""
        return cls.query.filter_by(user_id=user_id)\
                      .order_by(cls.usage_count.desc())\
                      .limit(limit).all()
    
    @classmethod
    def cleanup_unpopular_phrases(cls, user_id=None, cleanup_percentage=10):
        """
        Remove the bottom X% of least used phrases to save API costs
        
        Args:
            user_id: Specific user to clean up (None for global cleanup)
            cleanup_percentage: Percentage of bottom phrases to remove (default 10%)
        """
        if user_id:
            # Clean up for specific user
            total_phrases = cls.query.filter_by(user_id=user_id).count()
            if total_phrases <= 10:  # Don't clean if user has very few phrases
                return 0
            
            phrases_to_remove = max(1, int(total_phrases * cleanup_percentage / 100))
            
            # Get the least used phrases
            unpopular_phrases = cls.query.filter_by(user_id=user_id)\
                                      .order_by(cls.usage_count.asc())\
                                      .limit(phrases_to_remove).all()
            
            removed_count = 0
            for phrase in unpopular_phrases:
                db.session.delete(phrase)
                removed_count += 1
            
            db.session.commit()
            return removed_count
        else:
            # Global cleanup - remove unpopular phrases across all users
            total_phrases = cls.query.count()
            if total_phrases <= 100:  # Don't clean if very few total phrases
                return 0
            
            phrases_to_remove = max(10, int(total_phrases * cleanup_percentage / 100))
            
            # Get globally least used phrases
            unpopular_phrases = cls.query.order_by(cls.usage_count.asc())\
                                       .limit(phrases_to_remove).all()
            
            removed_count = 0
            for phrase in unpopular_phrases:
                db.session.delete(phrase)
                removed_count += 1
            
            db.session.commit()
            return removed_count
    
    @classmethod
    def cleanup_old_phrases(cls, days_old=30):
        """Remove phrases that haven't been used in X days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_phrases = cls.query.filter(cls.last_used < cutoff_date).all()
        removed_count = 0
        
        for phrase in old_phrases:
            db.session.delete(phrase)
            removed_count += 1
        
        db.session.commit()
        return removed_count
    
    @classmethod
    def get_cache_efficiency_stats(cls):
        """Get statistics about phrase caching efficiency"""
        total_phrases = cls.query.count()
        if total_phrases == 0:
            return {
                'total_phrases': 0,
                'total_usage': 0,
                'avg_usage': 0,
                'top_10_percent_usage': 0,
                'bottom_10_percent_usage': 0
            }
        
        # Get usage distribution
        all_phrases = cls.query.order_by(cls.usage_count.desc()).all()
        
        top_10_percent_count = max(1, int(total_phrases * 0.1))
        bottom_10_percent_count = max(1, int(total_phrases * 0.1))
        
        top_phrases = all_phrases[:top_10_percent_count]
        bottom_phrases = all_phrases[-bottom_10_percent_count:]
        
        total_usage = sum(phrase.usage_count for phrase in all_phrases)
        top_usage = sum(phrase.usage_count for phrase in top_phrases)
        bottom_usage = sum(phrase.usage_count for phrase in bottom_phrases)
        
        return {
            'total_phrases': total_phrases,
            'total_usage': total_usage,
            'avg_usage': total_usage / total_phrases if total_phrases > 0 else 0,
            'top_10_percent_usage': top_usage,
            'bottom_10_percent_usage': bottom_usage,
            'top_10_percent_count': top_10_percent_count,
            'bottom_10_percent_count': bottom_10_percent_count,
            'efficiency_ratio': top_usage / bottom_usage if bottom_usage > 0 else float('inf')
        }
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'phrase': self.phrase,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat(),
            'created_at': self.created_at.isoformat()
        }