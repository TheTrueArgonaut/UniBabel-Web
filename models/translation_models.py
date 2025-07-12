"""
Translation Models - Database models for translation management
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from models import db

class Translation(db.Model):
    """Model for tracking individual translation events"""
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    engine_used = Column(String(50), default='auto')  # auto, deepl, google, etc.
    confidence = Column(Float, default=0.0)
    
    # Usage context
    context = Column(String(50), nullable=True)  # chat, manual, api, etc.
    
    # Relationships
    user = relationship('User', backref='translations')
    
    def __repr__(self):
        return f'<Translation {self.id}: {self.source_language}->{self.target_language}>'

class TranslationSubmission(db.Model):
    """Model for user translation submissions"""
    __tablename__ = 'translation_submissions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    original_text = Column(Text, nullable=False)
    current_translation = Column(Text, nullable=True)  # What the system currently shows
    suggested_translation = Column(Text, nullable=False)  # User's suggested fix
    target_language = Column(String(10), nullable=False)
    context = Column(Text, nullable=True)  # Additional context from user
    
    # Status tracking
    status = Column(String(20), default='pending')  # pending, approved, rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Relationships with explicit primaryjoin to resolve SQLAlchemy mapping issues
    user = relationship('User', primaryjoin='TranslationSubmission.user_id == User.id', backref='translation_submissions')
    reviewer = relationship('User', primaryjoin='TranslationSubmission.reviewed_by == User.id', backref='translation_reviews')
    
    def __repr__(self):
        return f'<TranslationSubmission {self.id}: {self.target_language}>'

class TranslationCache(db.Model):
    """Model for cached translations"""
    __tablename__ = 'translation_cache'
    
    id = Column(Integer, primary_key=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    confidence = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source = Column(String(50), default='auto')  # auto, user_submission, admin_added
    submission_id = Column(Integer, ForeignKey('translation_submissions.id'), nullable=True)
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<TranslationCache {self.id}: {self.source_language}->{self.target_language}>'