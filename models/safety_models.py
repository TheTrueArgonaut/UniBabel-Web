"""
Safety Models Microservice
Handles: User reporting, friend requests, blocking, and safety features
"""

from datetime import datetime
import enum

# Import db from parent package
from . import db

class ReportReason(enum.Enum):
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    HARASSMENT = "harassment"
    SPAM = "spam"
    UNDERAGE_USER = "underage_user"
    FAKE_PROFILE = "fake_profile"
    THREATS = "threats"
    OTHER = "other"

class FriendRequestStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"

class UserReport(db.Model):
    """User reporting system for safety and moderation"""
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))
    
    # Report details
    reason = db.Column(db.Enum(ReportReason), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Moderation status
    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    moderator_notes = db.Column(db.Text)
    action_taken = db.Column(db.String(100))  # warning, mute, ban, none
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_made')
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref='reports_received')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    
    def resolve_report(self, resolver_id, action_taken, notes=None):
        """Resolve a user report"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolver_id
        self.action_taken = action_taken
        if notes:
            self.moderator_notes = notes
        
        # Update reported user's count
        reported_user = self.reported_user
        if action_taken in ['warning', 'mute', 'ban']:
            reported_user.reported_count += 1
            
            # Auto-actions based on report count
            if reported_user.reported_count >= 5:
                reported_user.is_blocked = True
                reported_user.block_reason = "Multiple reports"
        
        db.session.commit()
    
    @classmethod
    def get_pending_reports(cls, limit=50):
        """Get pending reports for moderation"""
        return cls.query.filter_by(is_resolved=False)\
                      .order_by(cls.timestamp.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_user_report_count(cls, user_id, days=30):
        """Get number of reports for a user in recent days"""
        since = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(
            cls.reported_user_id == user_id,
            cls.timestamp >= since
        ).count()
    
    def to_dict(self, include_details=False):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'reason': self.reason.value,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'is_resolved': self.is_resolved,
            'action_taken': self.action_taken
        }
        
        if include_details:
            data.update({
                'reporter_username': self.reporter.username,
                'reported_username': self.reported_user.username,
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
                'moderator_notes': self.moderator_notes,
                'message_id': self.message_id,
                'chat_id': self.chat_id
            })
        
        return data

class FriendRequest(db.Model):
    """Friend discovery and connection system"""
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.Enum(FriendRequestStatus), default=FriendRequestStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    message = db.Column(db.String(500))  # Optional message with friend request
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='friend_requests_sent')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='friend_requests_received')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('sender_id', 'recipient_id'),)
    
    def accept_request(self):
        """Accept friend request"""
        self.status = FriendRequestStatus.ACCEPTED
        self.responded_at = datetime.utcnow()
        
        # Create friendship both ways
        friendship1 = Friendship(user1_id=self.sender_id, user2_id=self.recipient_id)
        friendship2 = Friendship(user1_id=self.recipient_id, user2_id=self.sender_id)
        
        db.session.add(friendship1)
        db.session.add(friendship2)
        db.session.commit()
    
    def reject_request(self):
        """Reject friend request"""
        self.status = FriendRequestStatus.REJECTED
        self.responded_at = datetime.utcnow()
        db.session.commit()
    
    def block_user(self):
        """Block user and reject request"""
        self.status = FriendRequestStatus.BLOCKED
        self.responded_at = datetime.utcnow()
        
        # Create block relationship
        block = UserBlock(blocker_id=self.recipient_id, blocked_id=self.sender_id)
        db.session.add(block)
        db.session.commit()
    
    @classmethod
    def get_pending_requests(cls, user_id):
        """Get pending friend requests for a user"""
        return cls.query.filter_by(
            recipient_id=user_id,
            status=FriendRequestStatus.PENDING
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def send_request(cls, sender_id, recipient_id, message=None):
        """Send friend request with validation"""
        # Check if request already exists
        existing = cls.query.filter_by(
            sender_id=sender_id,
            recipient_id=recipient_id
        ).first()
        
        if existing:
            return False, "Request already exists"
        
        # Check if users are already friends
        friendship = Friendship.query.filter_by(
            user1_id=sender_id,
            user2_id=recipient_id
        ).first()
        
        if friendship:
            return False, "Already friends"
        
        # Check if sender is blocked
        block = UserBlock.query.filter_by(
            blocker_id=recipient_id,
            blocked_id=sender_id
        ).first()
        
        if block:
            return False, "You are blocked by this user"
        
        # Create request
        request = cls(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message
        )
        db.session.add(request)
        db.session.commit()
        
        return True, "Request sent"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username,
            'sender_display_name': self.sender.display_name,
            'recipient_id': self.recipient_id,
            'status': self.status.value,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }

class Friendship(db.Model):
    """Track friendships between users"""
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user1_id', 'user2_id'),)
    
    @classmethod
    def get_user_friends(cls, user_id):
        """Get all friends for a user"""
        return cls.query.filter_by(user1_id=user_id).all()
    
    @classmethod
    def are_friends(cls, user1_id, user2_id):
        """Check if two users are friends"""
        return cls.query.filter_by(user1_id=user1_id, user2_id=user2_id).first() is not None
    
    @classmethod
    def remove_friendship(cls, user1_id, user2_id):
        """Remove friendship between two users"""
        friendship1 = cls.query.filter_by(user1_id=user1_id, user2_id=user2_id).first()
        friendship2 = cls.query.filter_by(user1_id=user2_id, user2_id=user1_id).first()
        
        if friendship1:
            db.session.delete(friendship1)
        if friendship2:
            db.session.delete(friendship2)
        
        db.session.commit()

class UserBlock(db.Model):
    """Track blocked users"""
    id = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(200))
    
    # Relationships
    blocker = db.relationship('User', foreign_keys=[blocker_id], backref='users_blocked')
    blocked = db.relationship('User', foreign_keys=[blocked_id], backref='blocked_by')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('blocker_id', 'blocked_id'),)
    
    @classmethod
    def is_blocked(cls, blocker_id, blocked_id):
        """Check if user is blocked"""
        return cls.query.filter_by(
            blocker_id=blocker_id,
            blocked_id=blocked_id
        ).first() is not None
    
    @classmethod
    def block_user(cls, blocker_id, blocked_id, reason=None):
        """Block a user"""
        existing = cls.query.filter_by(
            blocker_id=blocker_id,
            blocked_id=blocked_id
        ).first()
        
        if existing:
            return False, "User already blocked"
        
        block = cls(
            blocker_id=blocker_id,
            blocked_id=blocked_id,
            reason=reason
        )
        db.session.add(block)
        
        # Remove friendship if exists
        Friendship.remove_friendship(blocker_id, blocked_id)
        
        db.session.commit()
        return True, "User blocked"
    
    @classmethod
    def unblock_user(cls, blocker_id, blocked_id):
        """Unblock a user"""
        block = cls.query.filter_by(
            blocker_id=blocker_id,
            blocked_id=blocked_id
        ).first()
        
        if block:
            db.session.delete(block)
            db.session.commit()
            return True, "User unblocked"
        
        return False, "User not blocked"