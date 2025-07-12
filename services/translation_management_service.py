"""
Translation Management Service - SRIMI Microservice
Single Responsibility: Coordinate translation micro-services
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class TranslationManagementService:
    """Micro-service coordinator for translation management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def submit_translation_fix(self, user_id: int, original_text: str, 
                              suggested_translation: str, target_language: str,
                              current_translation: str = None, 
                              context: str = None) -> Dict[str, Any]:
        """Submit translation fix via submission service"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            return translation_submission_service.submit_fix(
                user_id=user_id,
                original_text=original_text,
                suggested_translation=suggested_translation,
                target_language=target_language,
                current_translation=current_translation,
                context=context
            )
            
        except Exception as e:
            self.logger.error(f"Error submitting translation fix: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_pending_submissions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending submissions via submission service"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            return translation_submission_service.get_pending_submissions(limit=limit)
            
        except Exception as e:
            self.logger.error(f"Error getting pending submissions: {str(e)}")
            return []
    
    def get_all_submissions(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all submissions via submission service"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            return translation_submission_service.get_all_submissions(status=status, limit=limit)
            
        except Exception as e:
            self.logger.error(f"Error getting submissions: {str(e)}")
            return []
    
    def approve_translation(self, submission_id: int, admin_id: int, 
                          admin_notes: str = None, 
                          apply_to_cache: bool = True) -> Dict[str, Any]:
        """Approve translation via review service and optionally cache"""
        try:
            from services.translation_review_service import translation_review_service
            from services.translation_cache_service import translation_cache_service
            
            # Approve via review service
            result = translation_review_service.approve_submission(
                submission_id=submission_id,
                admin_id=admin_id,
                admin_notes=admin_notes
            )
            
            if not result['success']:
                return result
            
            # Apply to cache if requested
            if apply_to_cache and 'submission_data' in result:
                submission_data = result['submission_data']
                cache_result = translation_cache_service.add_translation(
                    original_text=submission_data['original_text'],
                    translated_text=submission_data['suggested_translation'],
                    target_language=submission_data['target_language'],
                    source_language='auto',
                    confidence=1.0,  # High confidence for human translations
                    metadata={
                        'source': 'user_submission',
                        'submission_id': submission_id,
                        'reviewed': True
                    }
                )
                
                result['applied_to_cache'] = cache_result['success']
                if not cache_result['success']:
                    result['cache_error'] = cache_result.get('error', 'Unknown cache error')
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error approving translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def reject_translation(self, submission_id: int, admin_id: int, 
                         reason: str = None) -> Dict[str, Any]:
        """Reject translation via review service"""
        try:
            from services.translation_review_service import translation_review_service
            
            return translation_review_service.reject_submission(
                submission_id=submission_id,
                admin_id=admin_id,
                reason=reason
            )
            
        except Exception as e:
            self.logger.error(f"Error rejecting translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_custom_translation(self, admin_id: int, original_text: str, 
                             translation: str, target_language: str,
                             apply_to_cache: bool = True) -> Dict[str, Any]:
        """Add custom translation directly via submission service"""
        try:
            from services.translation_submission_service import translation_submission_service
            from services.translation_review_service import translation_review_service
            from services.translation_cache_service import translation_cache_service
            
            # Create submission first
            submission_result = translation_submission_service.submit_fix(
                user_id=admin_id,
                original_text=original_text,
                suggested_translation=translation,
                target_language=target_language,
                current_translation=None,
                context="Admin-added custom translation"
            )
            
            if not submission_result['success']:
                return submission_result
            
            # Auto-approve
            review_result = translation_review_service.approve_submission(
                submission_id=submission_result['submission_id'],
                admin_id=admin_id,
                admin_notes="Direct admin addition"
            )
            
            if not review_result['success']:
                return review_result
            
            # Apply to cache if requested
            if apply_to_cache:
                cache_result = translation_cache_service.add_translation(
                    original_text=original_text,
                    translated_text=translation,
                    target_language=target_language,
                    source_language='auto',
                    confidence=1.0,
                    metadata={
                        'source': 'admin_added',
                        'submission_id': submission_result['submission_id'],
                        'reviewed': True
                    }
                )
                
                review_result['applied_to_cache'] = cache_result['success']
                if not cache_result['success']:
                    review_result['cache_error'] = cache_result.get('error', 'Unknown cache error')
            
            return review_result
            
        except Exception as e:
            self.logger.error(f"Error adding custom translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_cache_translations(self, target_language: str = None, 
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get cached translations via cache service"""
        try:
            from services.translation_cache_service import translation_cache_service
            
            return translation_cache_service.get_cached_translations(
                target_language=target_language,
                limit=limit
            )
            
        except Exception as e:
            self.logger.error(f"Error getting cache translations: {str(e)}")
            return []
    
    def remove_from_cache(self, cache_id: int, admin_id: int) -> Dict[str, Any]:
        """Remove translation from cache via cache service"""
        try:
            from services.translation_cache_service import translation_cache_service
            
            result = translation_cache_service.remove_translation(cache_id)
            
            if result['success']:
                self.logger.info(f"Translation removed from cache: {cache_id} by admin {admin_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error removing from cache: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_submission_stats(self) -> Dict[str, Any]:
        """Get submission statistics via submission service"""
        try:
            from services.translation_submission_service import translation_submission_service
            
            return translation_submission_service.get_submission_stats()
            
        except Exception as e:
            self.logger.error(f"Error getting submission stats: {str(e)}")
            return {}
    
    def get_review_stats(self, admin_id: int = None) -> Dict[str, Any]:
        """Get review statistics via review service"""
        try:
            from services.translation_review_service import translation_review_service
            
            return translation_review_service.get_review_stats(admin_id=admin_id)
            
        except Exception as e:
            self.logger.error(f"Error getting review stats: {str(e)}")
            return {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics via cache service"""
        try:
            from services.translation_cache_service import translation_cache_service
            
            return translation_cache_service.get_cache_stats()
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all services"""
        try:
            submission_stats = self.get_submission_stats()
            review_stats = self.get_review_stats()
            cache_stats = self.get_cache_stats()
            
            return {
                'submissions': submission_stats,
                'reviews': review_stats,
                'cache': cache_stats,
                'summary': {
                    'total_submissions': submission_stats.get('total_submissions', 0),
                    'pending_submissions': submission_stats.get('pending_submissions', 0),
                    'total_reviews': review_stats.get('total_reviews', 0),
                    'total_cached': cache_stats.get('total_translations', 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive stats: {str(e)}")
            return {}

# Singleton instance
translation_management_service = TranslationManagementService()