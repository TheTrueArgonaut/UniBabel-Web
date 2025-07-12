"""
Message Service
Handles message creation, translation, and distribution
Uses Translation Pipeline for Data Vampire Integration
Enhanced with Bot Detection Pipeline
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import request
from models import (
    db, Message, TranslatedMessage, ChatParticipant, User, UserCommonPhrase, UsageLog
)
import re


class MessageService:
    """
    Focused service for message operations
    Uses Translation Pipeline for Data Vampire Integration
    Enhanced with Bot Detection Pipeline
    
    Single Responsibility: Message handling only
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._orchestrator = None
        self._bot_detector = None
        
        self.logger.info(" Message Service initialized - unlimited messages for everyone")
    
    @property
    def orchestrator(self):
        """Lazy load orchestrator to avoid circular imports"""
        if self._orchestrator is None:
            from .translation_orchestrator import get_orchestrator
            self._orchestrator = get_orchestrator()
        return self._orchestrator
    
    @property 
    def bot_detector(self):
        """Lazy load bot detector to avoid circular imports"""
        if self._bot_detector is None:
            from .bot_detection_service import get_bot_detection_service
            self._bot_detector = get_bot_detection_service()
        return self._bot_detector
    
    def check_message_limits(self, current_user) -> Dict[str, Any]:
        """Check if user can send more messages - everyone gets unlimited"""
        return {'can_send': True}
    
    def create_message(self, current_user, chat_id: int, message_text: str) -> Message:
        """Create a new message with Translation Pipeline Integration"""
        # Track common phrases
        UserCommonPhrase.add_or_update_phrase(current_user.id, message_text)
        
        # Create message
        message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            original_text=message_text,
            original_language='AUTO'
        )
        db.session.add(message)
        db.session.flush()  # Get the message ID
        
        # ROUTE THROUGH TRANSLATION PIPELINE FOR DATA HARVESTING
        self._process_message_through_pipeline(
            user_id=current_user.id,
            message_text=message_text,
            message_id=message.id,
            chat_id=chat_id,
            communication_type='direct_message'
        )
        
        return message
    
    def send_message(self, sender_id: int, room_id: int, content: str, metadata: Dict = None) -> Dict:
        """Send message through translation pipeline with comprehensive data harvesting"""
        
        # Create message using correct field names
        message = Message(
            sender_id=sender_id,
            chat_id=room_id,  # Use chat_id not room_id
            original_text=content,  # Use original_text not content
            original_language='AUTO',
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.flush()  # Get the ID
        
        # COMPREHENSIVE TRANSLATION PIPELINE PROCESSING
        # This ensures ALL outgoing communication is harvested and processed
        pipeline_result = self._process_message_through_pipeline(
            user_id=sender_id,
            message_text=content,
            message_id=message.id,
            chat_id=room_id,
            communication_type='chat_message',
            metadata=metadata
        )
        
        # Log for analytics with enhanced data
        UsageLog.log_translation(
            user_id=sender_id,
            message_id=message.id,
            was_cached=pipeline_result.get('was_cached', False),
            total_market_value=pipeline_result.get('data_value', 0.0),
            vulnerability_score=pipeline_result.get('vulnerability_score', 0.0)
        )
        
        db.session.commit()
        
        self.logger.info(f"Message {message.id} sent by user {sender_id} - Data value: ${pipeline_result.get('data_value', 0)}")
        
        response = {
            'message_id': message.id,
            'status': 'sent',
            'timestamp': message.timestamp.isoformat()
        }
        
        # Include pipeline results for admin/analytics
        if pipeline_result.get('data_harvested'):
            response['data_harvesting'] = {
                'data_value': pipeline_result.get('data_value', 0),
                'vulnerability_score': pipeline_result.get('vulnerability_score', 0),
                'pipeline_processed': True
            }
        
        return response
    
    def _process_message_through_pipeline(self, user_id: int, message_text: str, 
                                        message_id: int, chat_id: int, 
                                        communication_type: str, metadata: Dict = None) -> Dict:
        """
        Process message through translation pipeline for data harvesting
        
        This ensures ALL outgoing communication is processed for:
        1. Data harvesting (always)
        2. Translation (based on user preference)
        3. Vulnerability analysis (always)
        4. Market value calculation (always)
        """
        try:
            # Import here to avoid circular imports
            from .translation_orchestrator import TranslationRequest
            
            # Create comprehensive translation request
            translation_request = TranslationRequest(
                text=message_text,
                target_language='en',  # Default target for processing
                source_language='auto',
                user_id=user_id,
                request_id=f"msg_{message_id}_{communication_type}",
                metadata={
                    'communication_type': communication_type,
                    'message_id': message_id,
                    'chat_id': chat_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Process through pipeline (this handles both translation and data harvesting)
            pipeline_result = asyncio.run(
                self.orchestrator.translate_message(translation_request)
            )
            
            return {
                'pipeline_processed': True,
                'data_harvested': pipeline_result.data_harvested,
                'data_value': pipeline_result.user_data_value,
                'vulnerability_score': pipeline_result.vulnerability_score,
                'translation_success': pipeline_result.success,
                'was_cached': pipeline_result.cached,
                'translation_provided': pipeline_result.translation if pipeline_result.success else None
            }
            
        except Exception as e:
            self.logger.error(f"Translation pipeline processing failed: {e}")
            return {
                'pipeline_processed': False,
                'data_harvested': False,
                'data_value': 0.0,
                'vulnerability_score': 0.0,
                'error': str(e)
            }
    
    def can_send_message(self, current_user) -> Dict[str, Any]:
        """Check if user can send message based on tier limits - everyone gets unlimited"""
        return {'can_send': True}
    
    def _is_premium_user(self, user) -> bool:
        """Check if user has premium subscription"""
        if hasattr(user, 'privacy_subscription') and user.privacy_subscription:
            from models.subscription_models import SubscriptionTier
            return user.privacy_subscription.tier in [SubscriptionTier.PRIVACY_PREMIUM, SubscriptionTier.ENTERPRISE]
        
        return getattr(user, 'is_premium', False)
    
    def _get_translation_priority(self, user) -> str:
        """Get translation priority - everyone gets same priority"""
        return 'normal'
    
    def _can_disable_data_harvesting(self, user) -> bool:
        """Check if user can disable data harvesting - Only Premium users can escape data collection"""
        return self._is_premium_user(user)
    
    def _get_message_features(self, user) -> Dict[str, Any]:
        """Get available message features - everyone gets all features"""
        return {
            'daily_limit': 999999,  # Unlimited for everyone
            'priority_translation': False,  # Everyone gets same priority
            'can_disable_data_harvesting': self._can_disable_data_harvesting(user),  # Only premium feature
            'enhanced_privacy': self._is_premium_user(user),  # Only premium feature
            'voice_messages': True,
            'file_attachments': True,
            'message_scheduling': True,
            'read_receipts': True,
            'typing_indicators': True,
            'message_reactions': True
        }

    def translate_for_participants(self, current_user, message: Message) -> List[TranslatedMessage]:
        """Translate message for all participants using pipeline"""
        # Import here to avoid circular imports
        from .translation_orchestrator import TranslationRequest
        
        participants = ChatParticipant.query.filter_by(chat_id=message.chat_id).all()
        translations = []
        
        for participant in participants:
            if participant.user_id != current_user.id:
                user = User.query.get(participant.user_id)
                
                # Create translation request for pipeline
                translation_request = TranslationRequest(
                    text=message.original_text,
                    target_language=user.preferred_language,
                    source_language='AUTO',
                    user_id=current_user.id,
                    request_id=f"trans_{message.id}_{user.id}",
                    metadata={
                        'message_id': message.id,
                        'recipient_id': user.id,
                        'chat_id': message.chat_id
                    }
                )
                
                try:
                    # Run through translation pipeline
                    pipeline_result = asyncio.run(
                        self.orchestrator.translate_message(translation_request)
                    )
                    
                    if pipeline_result.success:
                        translated_text = pipeline_result.translation
                        was_cached = pipeline_result.cached
                        confidence = pipeline_result.confidence
                    else:
                        translated_text = message.original_text
                        was_cached = False
                        confidence = 0.0
                        
                except Exception as e:
                    self.logger.error(f"Pipeline translation failed: {e}")
                    translated_text = message.original_text
                    was_cached = False
                    confidence = 0.0
                
                # Create translated message
                translated_message = TranslatedMessage(
                    message_id=message.id,
                    recipient_id=user.id,
                    translated_text=translated_text,
                    target_language=user.preferred_language,
                    confidence=confidence,
                    was_cached=was_cached
                )
                db.session.add(translated_message)
                translations.append(translated_message)
        
        db.session.commit()
        return translations
    
    def get_message_data_for_user(self, message: Message, user_id: int, 
                                is_sender: bool = False) -> Dict[str, Any]:
        """Get message data formatted for a specific user"""
        if is_sender:
            # Send original to sender
            return {
                'message_id': message.id,
                'chat_id': message.chat_id,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'text': message.original_text,
                'language': 'original',
                'timestamp': message.timestamp.isoformat(),
                'is_original': True
            }
        else:
            # Send translated to recipient
            translation = TranslatedMessage.query.filter_by(
                message_id=message.id,
                recipient_id=user_id
            ).first()
            
            return {
                'message_id': message.id,
                'chat_id': message.chat_id,
                'sender_id': message.sender_id,
                'sender_username': message.sender.username,
                'text': translation.translated_text if translation else message.original_text,
                'original_text': message.original_text,
                'language': translation.target_language if translation else 'original',
                'original_language': 'original',
                'confidence': translation.confidence if translation else 0.0,
                'timestamp': message.timestamp.isoformat(),
                'is_original': False,
                'was_cached': translation.was_cached if translation else False
            }
    
    def get_user_messages_sent(self, user) -> List[Message]:
        """Get messages sent by user"""
        return Message.query.filter_by(sender_id=user.id).all()
    
    def get_user_data_summary(self, user_id: int) -> Optional[Dict]:
        """Get comprehensive data summary for user through pipeline"""
        try:
            # Import here to avoid circular imports
            from .data_vampire_service import DataVampireService
            data_vampire_service = DataVampireService()
            return data_vampire_service.get_user_data_summary(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user data summary: {e}")
            return None


# Global instance
_message_service = MessageService()

def get_message_service():
    """Get the global message service instance"""
    return _message_service
