"""
Translation Submission Service - SRIMI Microservice
Single Responsibility: User translation submission operations only
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class TranslationSubmissionService:
    """Micro-service for translation submission operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def submit_fix(self, user_id: int, original_text: str, 
                  suggested_translation: str, target_language: str,
                  current_translation: str = None, 
                  context: str = None) -> Dict[str, Any]:
        """Submit translation fix"""
        try:
            from models.translation_models import TranslationSubmission, db
            
            submission = TranslationSubmission(
                user_id=user_id,
                original_text=original_text,
                current_translation=current_translation,
                suggested_translation=suggested_translation,
                target_language=target_language,
                context=context,
                status='pending',
                submitted_at=datetime.utcnow()
            )
            
            db.session.add(submission)
            db.session.commit()
            
            self.logger.info(f"Translation submission created: {submission.id}")
            
            return {
                'success': True,
                'submission_id': submission.id,
                'status': 'pending'
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting translation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_pending_submissions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending submissions"""
        try:
            from models.translation_models import TranslationSubmission
            from models import User
            
            submissions = TranslationSubmission.query.filter_by(
                status='pending'
            ).order_by(TranslationSubmission.submitted_at.desc()).limit(limit).all()
            
            result = []
            for sub in submissions:
                user = User.query.get(sub.user_id)
                result.append({
                    'id': sub.id,
                    'user_id': sub.user_id,
                    'username': user.username if user else 'Unknown',
                    'original_text': sub.original_text,
                    'current_translation': sub.current_translation,
                    'suggested_translation': sub.suggested_translation,
                    'target_language': sub.target_language,
                    'context': sub.context,
                    'submitted_at': sub.submitted_at.isoformat(),
                    'status': sub.status
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting pending submissions: {str(e)}")
            return []
    
    def get_all_submissions(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all submissions with optional filter"""
        try:
            from models.translation_models import TranslationSubmission
            from models import User
            
            query = TranslationSubmission.query
            if status:
                query = query.filter_by(status=status)
            
            submissions = query.order_by(TranslationSubmission.submitted_at.desc()).limit(limit).all()
            
            result = []
            for sub in submissions:
                user = User.query.get(sub.user_id)
                result.append({
                    'id': sub.id,
                    'user_id': sub.user_id,
                    'username': user.username if user else 'Unknown',
                    'original_text': sub.original_text,
                    'current_translation': sub.current_translation,
                    'suggested_translation': sub.suggested_translation,
                    'target_language': sub.target_language,
                    'context': sub.context,
                    'submitted_at': sub.submitted_at.isoformat(),
                    'status': sub.status,
                    'reviewed_by': sub.reviewed_by,
                    'reviewed_at': sub.reviewed_at.isoformat() if sub.reviewed_at else None,
                    'admin_notes': sub.admin_notes
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting submissions: {str(e)}")
            return []
    
    def get_submission_by_id(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get specific submission by ID"""
        try:
            from models.translation_models import TranslationSubmission
            from models import User
            
            submission = TranslationSubmission.query.get(submission_id)
            if not submission:
                return None
            
            user = User.query.get(submission.user_id)
            
            return {
                'id': submission.id,
                'user_id': submission.user_id,
                'username': user.username if user else 'Unknown',
                'original_text': submission.original_text,
                'current_translation': submission.current_translation,
                'suggested_translation': submission.suggested_translation,
                'target_language': submission.target_language,
                'context': submission.context,
                'submitted_at': submission.submitted_at.isoformat(),
                'status': submission.status,
                'reviewed_by': submission.reviewed_by,
                'reviewed_at': submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                'admin_notes': submission.admin_notes
            }
            
        except Exception as e:
            self.logger.error(f"Error getting submission: {str(e)}")
            return None
    
    def get_user_submissions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get submissions by specific user"""
        try:
            from models.translation_models import TranslationSubmission
            
            submissions = TranslationSubmission.query.filter_by(
                user_id=user_id
            ).order_by(TranslationSubmission.submitted_at.desc()).limit(limit).all()
            
            result = []
            for sub in submissions:
                result.append({
                    'id': sub.id,
                    'original_text': sub.original_text,
                    'current_translation': sub.current_translation,
                    'suggested_translation': sub.suggested_translation,
                    'target_language': sub.target_language,
                    'context': sub.context,
                    'submitted_at': sub.submitted_at.isoformat(),
                    'status': sub.status,
                    'reviewed_at': sub.reviewed_at.isoformat() if sub.reviewed_at else None,
                    'admin_notes': sub.admin_notes
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting user submissions: {str(e)}")
            return []
    
    def get_submission_stats(self) -> Dict[str, Any]:
        """Get submission statistics"""
        try:
            from models.translation_models import TranslationSubmission
            from models import db
            
            stats = {
                'total_submissions': TranslationSubmission.query.count(),
                'pending_submissions': TranslationSubmission.query.filter_by(status='pending').count(),
                'approved_submissions': TranslationSubmission.query.filter_by(status='approved').count(),
                'rejected_submissions': TranslationSubmission.query.filter_by(status='rejected').count(),
                'languages': {},
                'recent_activity': []
            }
            
            # Language breakdown
            lang_stats = db.session.query(
                TranslationSubmission.target_language,
                db.func.count(TranslationSubmission.id).label('count')
            ).group_by(TranslationSubmission.target_language).all()
            
            for lang, count in lang_stats:
                stats['languages'][lang] = count
            
            # Recent activity (last 10 submissions)
            recent = TranslationSubmission.query.order_by(
                TranslationSubmission.submitted_at.desc()
            ).limit(10).all()
            
            for sub in recent:
                stats['recent_activity'].append({
                    'id': sub.id,
                    'target_language': sub.target_language,
                    'status': sub.status,
                    'submitted_at': sub.submitted_at.isoformat()
                })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting submission stats: {str(e)}")
            return {}

# Singleton instance
translation_submission_service = TranslationSubmissionService()