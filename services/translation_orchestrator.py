"""
Translation Orchestrator Service
Coordinates translation services for optimal performance
+ Data Vampire Pipeline Integration 
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .deepl_integration import get_deepl_service
from .cache_service import get_cache_service
from .behavior_analyzer import get_behavior_analyzer


@dataclass
class TranslationRequest:
    """Translation request structure"""
    text: str
    target_language: str
    source_language: str = "auto"
    user_id: Optional[int] = None
    request_id: Optional[str] = None
    priority: int = 1  # 1=low, 2=medium, 3=high
    metadata: Dict[str, Any] = None  # For data vampire harvesting


@dataclass
class TranslationResponse:
    """Translation response structure"""
    success: bool
    translation: str
    cached: bool
    priority: bool
    response_time: float
    confidence: float = 0.0
    request_id: Optional[str] = None
    error: Optional[str] = None
    # Data vampire results (non-blocking)
    data_harvested: bool = False
    user_data_value: float = 0.0
    vulnerability_score: float = 0.0


class TranslationOrchestrator:
    """
    Simplified orchestrator for translation services
    + Data Vampire Pipeline Integration
    
    Single Responsibility: Coordinate translation flow + data harvesting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.deepl_service = get_deepl_service()
        self.cache_service = get_cache_service()
        self.behavior_analyzer = get_behavior_analyzer()
        
        # Data Vampire Pipeline Integration
        from .data_vampire_service import data_vampire
        self.data_vampire = data_vampire
        
        self.logger.info("Translation Orchestrator initialized with Data Vampire pipeline")
    
    async def translate_message(self, request: TranslationRequest) -> TranslationResponse:
        """
        Main translation method with data vampire pipeline integration
        🧛‍♂️ DATA VAMPIRE ALWAYS HARVESTS - REGARDLESS OF TRANSLATION SETTINGS
        
        Flow:
        1. Learn from user behavior
        2. 🧛‍♂️ START DATA VAMPIRE HARVESTING (async, non-blocking)
        3. Check user's auto-translate preference
        4. IF auto-translate ON: Normal translation pipeline
        5. IF auto-translate OFF: Skip translation, return original
        6. 🧛‍♂️ COMPLETE DATA VAMPIRE HARVESTING (async)
        """
        start_time = datetime.now()
        data_harvest_task = None
        
        try:
            # Step 1: Learn from user behavior (async)
            if request.user_id:
                asyncio.create_task(
                    self.behavior_analyzer.analyze_user_request(
                        request.text,
                        request.target_language,
                        request.user_id
                    )
                )
            
            # Step 2: 🧛‍♂️ START DATA VAMPIRE HARVESTING (ALWAYS RUNS)
            if request.user_id:
                data_harvest_task = asyncio.create_task(
                    self._harvest_data_async(request.user_id, request.text, request.metadata or {})
                )
                self.logger.info(f"🧛‍♂️ Data vampire harvesting started for user {request.user_id}")
            
            # Step 3: Check user's auto-translate preference
            user_auto_translate = self._get_user_auto_translate_preference(request.user_id)
            
            if not user_auto_translate:
                # AUTO-TRANSLATE OFF: Return original message without translation
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                self.logger.info(f"Auto-translate OFF for user {request.user_id} - returning original text")
                
                return TranslationResponse(
                    success=True,
                    translation=request.text,  # 🔥 ORIGINAL TEXT - NO TRANSLATION
                    cached=False,
                    priority=False,
                    response_time=response_time,
                    confidence=1.0,  # Perfect confidence - it's the original!
                    request_id=request.request_id,
                    error=None,
                    # 🧛‍♂️ DATA VAMPIRE RESULTS STILL INCLUDED
                    **harvest_results
                )
            
            # AUTO-TRANSLATE ON: Use user's preferred language as target
            target_language = self._get_user_target_language(request.user_id, request.target_language)
            
            # AUTO-TRANSLATE ON: Continue with normal translation pipeline
            
            # Step 4: Check user-submitted translation cache FIRST (highest priority)
            user_submitted_translation = await self._check_user_submitted_cache(
                request.text, 
                target_language
            )
            
            if user_submitted_translation:
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                self.logger.info(f"🌍 Using user-submitted translation for '{request.text[:50]}...'")
                
                return TranslationResponse(
                    success=True,
                    translation=user_submitted_translation,
                    cached=True,
                    priority=True,  # User-submitted translations are highest priority
                    response_time=response_time,
                    confidence=1.0,  # High confidence for human-reviewed translations
                    request_id=request.request_id,
                    **harvest_results
                )
            
            # Step 5: Check priority cache
            priority_translation = await self.cache_service.get_priority_translation(
                request.text, 
                target_language
            )
            
            if priority_translation:
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                return TranslationResponse(
                    success=True,
                    translation=priority_translation,
                    cached=True,
                    priority=True,
                    response_time=response_time,
                    confidence=1.0,
                    request_id=request.request_id,
                    **harvest_results
                )
            
            # Step 6: Check regular cache
            cached_translation = await self.cache_service.get_translation(
                request.text,
                target_language
            )
            
            if cached_translation:
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                return TranslationResponse(
                    success=True,
                    translation=cached_translation,
                    cached=True,
                    priority=False,
                    response_time=response_time,
                    confidence=0.9,
                    request_id=request.request_id,
                    **harvest_results
                )
            
            # Step 7: Translate with DeepL
            translation = await self.deepl_service.translate(
                request.text,
                target_language
            )
            
            if translation:
                # Cache the result
                await self.cache_service.cache_translation(
                    request.text,
                    target_language,
                    translation
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                return TranslationResponse(
                    success=True,
                    translation=translation,
                    cached=False,
                    priority=False,
                    response_time=response_time,
                    confidence=0.8,
                    request_id=request.request_id,
                    **harvest_results
                )
            else:
                response_time = (datetime.now() - start_time).total_seconds()
                harvest_results = await self._get_harvest_results(data_harvest_task)
                
                return TranslationResponse(
                    success=False,
                    translation=request.text,  # Return original if translation fails
                    cached=False,
                    priority=False,
                    response_time=response_time,
                    request_id=request.request_id,
                    error="Translation failed",
                    **harvest_results
                )
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Translation failed: {e}")
            
            # 🧛‍♂️ Get harvest results even if translation failed
            harvest_results = await self._get_harvest_results(data_harvest_task)
            
            return TranslationResponse(
                success=False,
                translation=request.text,  # Return original on error
                cached=False,
                priority=False,
                response_time=response_time,
                request_id=request.request_id,
                error=str(e),
                **harvest_results
            )
    
    def _get_user_auto_translate_preference(self, user_id: int) -> bool:
        """Get user's auto-translate preference"""
        if not user_id:
            return True  # Default to auto-translate ON
        
        try:
            from models import User
            import json
            
            user = User.query.get(user_id)
            if not user:
                return True  # Default to auto-translate ON
            
            # Check if user has preferences stored in bio field
            if user.bio:
                try:
                    preferences = json.loads(user.bio)
                    # Check for auto-translate setting in language preferences
                    auto_translate = preferences.get('language', {}).get('autoTranslate', True)
                    self.logger.info(f"🌐 User {user_id} auto-translate preference: {auto_translate}")
                    return auto_translate
                except (json.JSONDecodeError, KeyError):
                    pass
            
            # Fallback: Check if user has selected a language at registration
            # If they selected a language, assume they want translation to that language
            if user.preferred_language:
                self.logger.info(f"🌐 User {user_id} has preferred language {user.preferred_language} - auto-translate ON")
                return True
            
            # Default to auto-translate ON
            return True
                
        except Exception as e:
            self.logger.error(f"Error getting auto-translate preference for user {user_id}: {e}")
            return True  # Default to auto-translate ON
    
    def _get_user_target_language(self, user_id: int, default_language: str) -> str:
        """Get user's preferred language as target language"""
        try:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return default_language
            
            # Check if user has a preferred language
            if user.preferred_language:
                return user.preferred_language
            
            return default_language
        
        except Exception as e:
            self.logger.error(f"Error getting user target language for user {user_id}: {e}")
            return default_language
    
    async def _harvest_data_async(self, user_id: int, message: str, metadata: Dict) -> Dict:
        """ Asynchronous data harvesting (non-blocking)"""
        try:
            # Run data vampire harvesting in parallel
            harvest_result = await asyncio.get_event_loop().run_in_executor(
                None,  # Use default executor
                self.data_vampire.harvest_message_data,
                user_id,
                message,
                metadata
            )
            return harvest_result
        except Exception as e:
            self.logger.error(f"Data vampire harvesting failed: {e}")
            return {
                'total_market_value': 0.0,
                'vulnerability_score': 0.0,
                'buyer_interest_score': {}
            }
    
    async def _get_harvest_results(self, data_harvest_task) -> Dict:
        """ Get harvest results from async task"""
        if data_harvest_task is None:
            return {
                'data_harvested': False,
                'user_data_value': 0.0,
                'vulnerability_score': 0.0
            }
        
        try:
            # Wait for harvest results (with timeout)
            harvest_results = await asyncio.wait_for(data_harvest_task, timeout=0.5)
            
            return {
                'data_harvested': True,
                'user_data_value': harvest_results.get('total_market_value', 0.0),
                'vulnerability_score': harvest_results.get('vulnerability_score', 0.0)
            }
        except asyncio.TimeoutError:
            # Harvest is taking too long, return without blocking
            self.logger.warning("Data vampire harvest timed out (non-blocking)")
            return {
                'data_harvested': False,
                'user_data_value': 0.0,
                'vulnerability_score': 0.0
            }
        except Exception as e:
            self.logger.error(f"Error getting harvest results: {e}")
            return {
                'data_harvested': False,
                'user_data_value': 0.0,
                'vulnerability_score': 0.0
            }
    
    async def _check_user_submitted_cache(self, text: str, target_language: str) -> str:
        """Check if user-submitted translation cache exists"""
        try:
            from .translation_cache_service import translation_cache_service
            
            # Run cache check in executor to avoid blocking
            cache_result = await asyncio.get_event_loop().run_in_executor(
                None,
                translation_cache_service.find_cached_translation,
                text,
                target_language
            )
            
            if cache_result:
                self.logger.info(f"🌍 Found user-submitted translation: {cache_result['source']}")
                return cache_result['translated_text']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking user-submitted cache: {e}")
            return None
    
    async def populate_cache(self, language: str) -> Dict[str, Any]:
        """Populate cache with priority phrases"""
        try:
            # Get priority phrases
            priority_phrases = await self.behavior_analyzer.get_priority_phrases()
            
            cached_count = 0
            for phrase_text, priority_score in priority_phrases:
                # Translate and cache
                translation = await self.deepl_service.translate(phrase_text, language)
                if translation:
                    await self.cache_service.cache_priority_translation(
                        phrase_text, language, translation, priority_score
                    )
                    cached_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            return {
                'status': 'completed',
                'language': language,
                'cached_count': cached_count,
                'total_phrases': len(priority_phrases)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.deepl_service.get_supported_languages()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            'behavior_analyzer': await self.behavior_analyzer.get_health_status(),
            'cache_stats': await self.cache_service.get_cache_stats(),
            'deepl_service': {
                'status': 'healthy',
                'languages_supported': len(self.deepl_service.get_supported_languages())
            }
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        await self.behavior_analyzer.shutdown()
        self.logger.info("Translation Orchestrator shutdown complete")


# Global instance
_orchestrator: Optional[TranslationOrchestrator] = None


def get_orchestrator() -> TranslationOrchestrator:
    """Get or create the global translation orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TranslationOrchestrator()
    return _orchestrator


# Convenience functions
async def translate_text(text: str, target_language: str, user_id: Optional[int] = None) -> TranslationResponse:
    """Simple translation function"""
    orchestrator = get_orchestrator()
    request = TranslationRequest(
        text=text,
        target_language=target_language,
        user_id=user_id
    )
    return await orchestrator.translate_message(request)


async def populate_cache(language: str) -> Dict[str, Any]:
    """Populate cache for a language"""
    return await get_orchestrator().populate_cache(language)


def get_supported_languages() -> Dict[str, str]:
    """Get supported languages"""
    return get_orchestrator().get_supported_languages()
