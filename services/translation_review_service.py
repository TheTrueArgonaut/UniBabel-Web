"""
Translation Review Service - SRIMI Microservice
Single Responsibility: Admin translation review operations only
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class TranslationReviewService:
    """Micro-service for translation review operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def approve_submission(self, submission_id: int, admin_id: int, 
                          admin_notes: str = None) -> Dict[str, Any]:
        """Approve translation submission"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            submission = TranslationSubmission.query.get(submission_id)
            if not submission:
                return {'success': False, 'error': 'Submission not found'}
            
            if submission.status != 'pending':
                return {'success': False, 'error': 'Submission already reviewed'}
            
            # Update submission status
            submission.status = 'approved'
            submission.reviewed_by = admin_id
            submission.reviewed_at = datetime.utcnow()
            submission.admin_notes = admin_notes
            
            db.session.commit()
            
            self.logger.info(f"Translation approved: {submission_id} by admin {admin_id}")
            
            return {
                'success': True,
                'submission_id': submission_id,
                'status': 'approved',
                'submission_data': {
                    'original_text': submission.original_text,
                    'suggested_translation': submission.suggested_translation,
                    'target_language': submission.target_language
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error approving translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def reject_submission(self, submission_id: int, admin_id: int, 
                         reason: str = None) -> Dict[str, Any]:
        """Reject translation submission"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            submission = TranslationSubmission.query.get(submission_id)
            if not submission:
                return {'success': False, 'error': 'Submission not found'}
            
            if submission.status != 'pending':
                return {'success': False, 'error': 'Submission already reviewed'}
            
            # Update submission status
            submission.status = 'rejected'
            submission.reviewed_by = admin_id
            submission.reviewed_at = datetime.utcnow()
            submission.admin_notes = reason
            
            db.session.commit()
            
            self.logger.info(f"Translation rejected: {submission_id} by admin {admin_id}")
            
            return {
                'success': True,
                'submission_id': submission_id,
                'status': 'rejected'
            }
            
        except Exception as e:
            self.logger.error(f"Error rejecting translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def bulk_approve(self, submission_ids: List[int], admin_id: int,
                    admin_notes: str = None) -> Dict[str, Any]:
        """Bulk approve multiple submissions"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            results = {'approved': [], 'failed': []}
            
            for submission_id in submission_ids:
                submission = TranslationSubmission.query.get(submission_id)
                if not submission:
                    results['failed'].append({
                        'id': submission_id,
                        'error': 'Submission not found'
                    })
                    continue
                
                if submission.status != 'pending':
                    results['failed'].append({
                        'id': submission_id,
                        'error': 'Submission already reviewed'
                    })
                    continue
                
                # Update submission status
                submission.status = 'approved'
                submission.reviewed_by = admin_id
                submission.reviewed_at = datetime.utcnow()
                submission.admin_notes = admin_notes
                
                results['approved'].append({
                    'id': submission_id,
                    'original_text': submission.original_text,
                    'suggested_translation': submission.suggested_translation,
                    'target_language': submission.target_language
                })
            
            db.session.commit()
            
            self.logger.info(f"Bulk approved {len(results['approved'])} translations by admin {admin_id}")
            
            return {
                'success': True,
                'approved_count': len(results['approved']),
                'failed_count': len(results['failed']),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error bulk approving translations: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def bulk_reject(self, submission_ids: List[int], admin_id: int,
                   reason: str = None) -> Dict[str, Any]:
        """Bulk reject multiple submissions"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            results = {'rejected': [], 'failed': []}
            
            for submission_id in submission_ids:
                submission = TranslationSubmission.query.get(submission_id)
                if not submission:
                    results['failed'].append({
                        'id': submission_id,
                        'error': 'Submission not found'
                    })
                    continue
                
                if submission.status != 'pending':
                    results['failed'].append({
                        'id': submission_id,
                        'error': 'Submission already reviewed'
                    })
                    continue
                
                # Update submission status
                submission.status = 'rejected'
                submission.reviewed_by = admin_id
                submission.reviewed_at = datetime.utcnow()
                submission.admin_notes = reason
                
                results['rejected'].append(submission_id)
            
            db.session.commit()
            
            self.logger.info(f"Bulk rejected {len(results['rejected'])} translations by admin {admin_id}")
            
            return {
                'success': True,
                'rejected_count': len(results['rejected']),
                'failed_count': len(results['failed']),
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Error bulk rejecting translations: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_review_history(self, admin_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get review history for admin"""
        try:
            from models.translation_models import TranslationSubmission
            from models import User
            
            reviews = TranslationSubmission.query.filter_by(
                reviewed_by=admin_id
            ).order_by(TranslationSubmission.reviewed_at.desc()).limit(limit).all()
            
            result = []
            for review in reviews:
                user = User.query.get(review.user_id)
                result.append({
                    'id': review.id,
                    'user_id': review.user_id,
                    'username': user.username if user else 'Unknown',
                    'original_text': review.original_text,
                    'suggested_translation': review.suggested_translation,
                    'target_language': review.target_language,
                    'status': review.status,
                    'reviewed_at': review.reviewed_at.isoformat(),
                    'admin_notes': review.admin_notes
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting review history: {str(e)}")
            return []
    
    def get_review_stats(self, admin_id: int = None) -> Dict[str, Any]:
        """Get review statistics"""
        try:
            from models.translation_models import TranslationSubmission
            from models import db
            
            query = TranslationSubmission.query
            if admin_id:
                query = query.filter_by(reviewed_by=admin_id)
            
            stats = {
                'total_reviews': query.filter(TranslationSubmission.status != 'pending').count(),
                'approved_reviews': query.filter_by(status='approved').count(),
                'rejected_reviews': query.filter_by(status='rejected').count(),
                'pending_reviews': TranslationSubmission.query.filter_by(status='pending').count()
            }
            
            # Review rate (if admin specific)
            if admin_id and stats['total_reviews'] > 0:
                stats['approval_rate'] = (stats['approved_reviews'] / stats['total_reviews']) * 100
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting review stats: {str(e)}")
            return {}
    
    def undo_review(self, submission_id: int, admin_id: int) -> Dict[str, Any]:
        """Undo review (set back to pending)"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            submission = TranslationSubmission.query.get(submission_id)
            if not submission:
                return {'success': False, 'error': 'Submission not found'}
            
            if submission.status == 'pending':
                return {'success': False, 'error': 'Submission is already pending'}
            
            # Reset to pending
            submission.status = 'pending'
            submission.reviewed_by = None
            submission.reviewed_at = None
            submission.admin_notes = f"Review undone by admin {admin_id}"
            
            db.session.commit()
            
            self.logger.info(f"Review undone: {submission_id} by admin {admin_id}")
            
            return {
                'success': True,
                'submission_id': submission_id,
                'status': 'pending'
            }
            
        except Exception as e:
            self.logger.error(f"Error undoing review: {str(e)}")
            return {'success': False, 'error': str(e)}

# Singleton instance
translation_review_service = TranslationReviewService()