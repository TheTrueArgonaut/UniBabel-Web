"""
Chat Models Microservice
Handles: Chats, messages, translations, and room management
"""

from datetime import datetime, timedelta
import enum

# Import db from parent package
from . import db

class RoomType(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    KIDS_ONLY = "kids_only"
    TEENS_ONLY = "teens_only"
    ADULTS_ONLY = "adults_only"

class Chat(db.Model):
    """Chat room model for private and public conversations"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=False)
    room_type = db.Column(db.Enum(RoomType), default=RoomType.PRIVATE)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Public room features
    is_public = db.Column(db.Boolean, default=False)
    max_participants = db.Column(db.Integer, default=100)
    tags = db.Column(db.Text)  # JSON string of tags
    
    # Moderation
    is_moderated = db.Column(db.Boolean, default=False)
    moderator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Activity tracking
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    message_count = db.Column(db.Integer, default=0)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def increment_message_count(self):
        """Increment message count"""
        self.message_count += 1
        self.update_activity()
    
    def get_participant_count(self):
        """Get current number of participants"""
        return ChatParticipant.query.filter_by(chat_id=self.id).count()
    
    def is_full(self):
        """Check if room is at capacity"""
        if not self.max_participants:
            return False
        return self.get_participant_count() >= self.max_participants
    
    def can_user_join(self, user):
        """Check if user can join this chat"""
        # Check if room is full
        if self.is_full():
            return False, "Room is full"
        
        # Check age restrictions
        if not user.can_join_room(self.room_type):
            return False, "Age restriction"
        
        # Check if already a participant
        existing = ChatParticipant.query.filter_by(
            chat_id=self.id, user_id=user.id
        ).first()
        if existing:
            return False, "Already a member"
        
        return True, "OK"
    
    def to_dict(self, include_stats=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_group': self.is_group,
            'room_type': self.room_type.value,
            'created_at': self.created_at.isoformat(),
            'is_public': self.is_public,
            'max_participants': self.max_participants,
            'tags': self.tags,
            'is_moderated': self.is_moderated
        }
        
        if include_stats:
            data.update({
                'participant_count': self.get_participant_count(),
                'last_activity': self.last_activity.isoformat(),
                'message_count': self.message_count
            })
        
        return data

class ChatParticipant(db.Model):
    """Track users participating in chats"""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Moderation features
    is_moderator = db.Column(db.Boolean, default=False)
    is_muted = db.Column(db.Boolean, default=False)
    muted_until = db.Column(db.DateTime)
    
    # Activity tracking
    last_read_message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    unread_count = db.Column(db.Integer, default=0)
    
    # Relationships
    chat = db.relationship('Chat', backref='participants')
    user = db.relationship('User', backref='chat_participations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('chat_id', 'user_id'),)
    
    def is_currently_muted(self):
        """Check if user is currently muted"""
        if not self.is_muted:
            return False
        if self.muted_until and datetime.utcnow() > self.muted_until:
            self.is_muted = False
            self.muted_until = None
            db.session.commit()
            return False
        return True
    
    def mute_user(self, duration_minutes=None):
        """Mute user for specified duration"""
        self.is_muted = True
        if duration_minutes:
            self.muted_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()
    
    def unmute_user(self):
        """Unmute user"""
        self.is_muted = False
        self.muted_until = None
        db.session.commit()

class Message(db.Model):
    """Individual messages in chats"""
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Cost tracking for monetization
    was_cached = db.Column(db.Boolean, default=False)
    translation_cost = db.Column(db.Float, default=0.0)
    
    # Moderation
    is_flagged = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    flagged_reason = db.Column(db.String(200))
    
    # Message type
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    is_system_message = db.Column(db.Boolean, default=False)  # For admin/system messages
    
    # Relationships
    chat = db.relationship('Chat', backref='messages')
    sender = db.relationship('User', backref='sent_messages')
    
    def soft_delete(self, reason=None):
        """Soft delete message"""
        self.is_deleted = True
        if reason:
            self.flagged_reason = reason
        db.session.commit()
    
    def flag_message(self, reason):
        """Flag message for moderation"""
        self.is_flagged = True
        self.flagged_reason = reason
        db.session.commit()
    
    def unflag_message(self):
        """Remove flag from message"""
        self.is_flagged = False
        self.flagged_reason = None
        db.session.commit()
    
    def to_dict(self, include_moderation=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'original_text': self.original_text,
            'original_language': self.original_language,
            'timestamp': self.timestamp.isoformat(),
            'was_cached': self.was_cached,
            'sender_username': self.sender.username,
            'message_type': self.message_type
        }
        
        if include_moderation:
            data.update({
                'is_flagged': self.is_flagged,
                'is_deleted': self.is_deleted,
                'flagged_reason': self.flagged_reason,
                'translation_cost': self.translation_cost
            })
        
        return data

class TranslatedMessage(db.Model):
    """Translated versions of messages for each recipient"""
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    translated_text = db.Column(db.Text, nullable=False)
    target_language = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, default=0.0)
    was_cached = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance tracking
    translation_time_ms = db.Column(db.Integer)  # Translation time in milliseconds
    
    # Relationships
    message = db.relationship('Message', backref='translations')
    recipient = db.relationship('User', backref='received_translations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('message_id', 'recipient_id'),)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'translated_text': self.translated_text,
            'target_language': self.target_language,
            'confidence': self.confidence,
            'was_cached': self.was_cached,
            'translation_time_ms': self.translation_time_ms,
            'created_at': self.created_at.isoformat()
        }