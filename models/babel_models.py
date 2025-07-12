"""
Babel Models
Handles: User posts, timeline, likes, comments, and social interactions
"""

from flask_login import UserMixin
from datetime import datetime
from . import db
import enum


class BabelPostType(enum.Enum):
    TEXT = "text"
    LOOKING_FOR = "looking_for"  # Looking for chat partners
    TOPIC = "topic"  # Topic discussion starter
    LANGUAGE = "language"  # Language practice request
    MOOD = "mood"  # Current mood/status


class BabelPost(db.Model):
    """
    Babel posts - Twitter-like posts for finding like-minded people
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.Enum(BabelPostType), default=BabelPostType.TEXT, index=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Engagement metrics
    likes_count = db.Column(db.Integer, default=0, index=True)
    comments_count = db.Column(db.Integer, default=0, index=True)
    chats_started = db.Column(db.Integer, default=0)  # How many chats this post started
    
    # Content moderation
    is_flagged = db.Column(db.Boolean, default=False, index=True)
    is_approved = db.Column(db.Boolean, default=True, index=True)
    
    # Searchable fields
    tags = db.Column(db.Text)  # JSON array of hashtags
    languages = db.Column(db.String(100))  # Languages mentioned
    topics = db.Column(db.Text)  # Topics/interests mentioned
    
    # Relationships
    user = db.relationship('User', backref='babel_posts')
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_babel_timeline', 'created_at', 'is_approved'),
        db.Index('idx_babel_user_posts', 'user_id', 'created_at'),
        db.Index('idx_babel_engagement', 'likes_count', 'comments_count'),
        db.Index('idx_babel_type_date', 'post_type', 'created_at'),
    )
    
    def to_dict(self, include_user=True):
        """Convert to dictionary for API responses"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'post_type': self.post_type.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'chats_started': self.chats_started,
            'tags': self.tags,
            'languages': self.languages,
            'topics': self.topics
        }
        
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'display_name': self.user.display_name,
                'user_type': self.user.user_type.value,
                'is_online': self.user.is_online,
                'country': self.user.country,
                'preferred_language': self.user.preferred_language
            }
        
        return data
    
    def can_user_see(self, viewer_user):
        """Check if viewer can see this post based on age restrictions"""
        if not self.is_approved or self.is_flagged:
            return False
        
        # Age-appropriate filtering
        return viewer_user.can_contact_user(self.user)


class BabelLike(db.Model):
    """
    Likes on Babel posts
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('babel_post.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='babel_likes')
    post = db.relationship('BabelPost', backref='likes')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),
        db.Index('idx_babel_like_post', 'post_id', 'created_at'),
    )


class BabelComment(db.Model):
    """
    Comments on Babel posts
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('babel_post.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='babel_comments')
    post = db.relationship('BabelPost', backref='comments')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_babel_comment_post', 'post_id', 'created_at'),
        db.Index('idx_babel_comment_user', 'user_id', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'display_name': self.user.display_name,
                'user_type': self.user.user_type.value
            }
        }


class BabelFollow(db.Model):
    """
    Following system for Babel users
    """
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
        db.Index('idx_babel_follow_follower', 'follower_id', 'created_at'),
        db.Index('idx_babel_follow_following', 'following_id', 'created_at'),
    )