"""
Translation Cache Service - SRIMI Microservice
Single Responsibility: Translation cache operations only
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class TranslationCacheService:
    """Micro-service for translation cache operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def add_translation(self, original_text: str, translated_text: str, 
                       target_language: str, source_language: str = 'auto',
                       confidence: float = 0.0, metadata: Dict = None) -> Dict[str, Any]:
        """Add translation to cache"""
        try:
            from models.translation_models import TranslationCache, db
            
            # Check if translation already exists
            existing = TranslationCache.query.filter_by(
                original_text=original_text,
                target_language=target_language
            ).first()
            
            if existing:
                # Update existing
                existing.translated_text = translated_text
                existing.confidence = confidence
                existing.updated_at = datetime.utcnow()
                existing.times_used += 1
                existing.last_used = datetime.utcnow()
                
                if metadata:
                    existing.source = metadata.get('source', existing.source)
                    existing.submission_id = metadata.get('submission_id', existing.submission_id)
                
                db.session.commit()
                
                return {
                    'success': True,
                    'cache_id': existing.id,
                    'updated': True
                }
            else:
                # Create new
                cache_entry = TranslationCache(
                    original_text=original_text,
                    translated_text=translated_text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=confidence,
                    source=metadata.get('source', 'auto') if metadata else 'auto',
                    submission_id=metadata.get('submission_id') if metadata else None,
                    times_used=1,
                    last_used=datetime.utcnow()
                )
                
                db.session.add(cache_entry)
                db.session.commit()
                
                return {
                    'success': True,
                    'cache_id': cache_entry.id,
                    'created': True
                }
                
        except Exception as e:
            self.logger.error(f"Error adding translation to cache: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_cached_translations(self, target_language: str = None, 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """Get cached translations"""
        try:
            from models.translation_models import TranslationCache
            
            query = TranslationCache.query
            if target_language:
                query = query.filter_by(target_language=target_language)
            
            translations = query.order_by(TranslationCache.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'id': t.id,
                    'original_text': t.original_text,
                    'translated_text': t.translated_text,
                    'source_language': t.source_language,
                    'target_language': t.target_language,
                    'confidence': t.confidence,
                    'created_at': t.created_at.isoformat(),
                    'times_used': t.times_used,
                    'last_used': t.last_used.isoformat() if t.last_used else None,
                    'source': t.source
                }
                for t in translations
            ]
            
        except Exception as e:
            self.logger.error(f"Error getting cached translations: {str(e)}")
            return []
    
    def remove_translation(self, cache_id: int) -> Dict[str, Any]:
        """Remove translation from cache"""
        try:
            from models.translation_models import TranslationCache, db
            
            cache_entry = TranslationCache.query.get(cache_id)
            if not cache_entry:
                return {'success': False, 'error': 'Translation not found'}
            
            db.session.delete(cache_entry)
            db.session.commit()
            
            return {'success': True, 'message': 'Translation removed from cache'}
            
        except Exception as e:
            self.logger.error(f"Error removing translation from cache: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def find_cached_translation(self, original_text: str, 
                              target_language: str) -> Optional[Dict[str, Any]]:
        """Find cached translation"""
        try:
            from models.translation_models import TranslationCache, db
            
            cache_entry = TranslationCache.query.filter_by(
                original_text=original_text,
                target_language=target_language
            ).first()
            
            if cache_entry:
                # Update usage stats
                cache_entry.times_used += 1
                cache_entry.last_used = datetime.utcnow()
                db.session.commit()
                
                return {
                    'id': cache_entry.id,
                    'original_text': cache_entry.original_text,
                    'translated_text': cache_entry.translated_text,
                    'confidence': cache_entry.confidence,
                    'source': cache_entry.source
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding cached translation: {str(e)}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            from models.translation_models import TranslationCache, db
            
            stats = {
                'total_translations': TranslationCache.query.count(),
                'languages': {},
                'sources': {}
            }
            
            # Language breakdown
            lang_stats = db.session.query(
                TranslationCache.target_language,
                db.func.count(TranslationCache.id).label('count')
            ).group_by(TranslationCache.target_language).all()
            
            for lang, count in lang_stats:
                stats['languages'][lang] = count
            
            # Source breakdown
            source_stats = db.session.query(
                TranslationCache.source,
                db.func.count(TranslationCache.id).label('count')
            ).group_by(TranslationCache.source).all()
            
            for source, count in source_stats:
                stats['sources'][source] = count
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {}

# Singleton instance
translation_cache_service = TranslationCacheService()