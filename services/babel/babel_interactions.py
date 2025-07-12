"""
Babel Interactions Service - Handle likes, comments, and user interactions
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from models import db, User, BabelPost, BabelLike, BabelComment
import bleach

# Translation Pipeline Integration
from ..translation_orchestrator import get_orchestrator, TranslationRequest


class BabelInteractionsService:
    """Microservice for Babel post interactions (likes, comments)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Translation Pipeline Integration
        self.translation_orchestrator = get_orchestrator()
        
        self.logger.info("❤️ Babel Interactions Service initialized")
    
    def like_post(self, user_id: int, post_id: int) -> Dict[str, Any]:
        """Like or unlike a post"""
        user = User.query.get(user_id)
        post = BabelPost.query.get(post_id)
        
        if not user or not post:
            return {'error': 'User or post not found', 'status': 404}
        
        # Check if user can interact with this post
        if not user.can_contact_user(post.user):
            return {'error': 'Cannot interact with this post', 'status': 403}
        
        # Check if already liked
        existing_like = BabelLike.query.filter_by(
            user_id=user_id,
            post_id=post_id
        ).first()
        
        try:
            if existing_like:
                # Unlike
                db.session.delete(existing_like)
                post.likes_count = max(0, post.likes_count - 1)
                action = 'unliked'
            else:
                # Like
                like = BabelLike(user_id=user_id, post_id=post_id)
                db.session.add(like)
                post.likes_count += 1
                action = 'liked'
            
            db.session.commit()
            
            self.logger.info(f"❤️ User {user_id} {action} post {post_id}")
            
            return {
                'action': action,
                'likes_count': post.likes_count,
                'message': f'Post {action}',
                'status': 200
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to {action} post: {str(e)}")
            return {'error': 'Failed to process like', 'status': 500}
    
    def add_comment(self, user_id: int, post_id: int, content: str) -> Dict[str, Any]:
        """Add a comment to a post with Translation Pipeline Integration"""
        user = User.query.get(user_id)
        post = BabelPost.query.get(post_id)
        
        if not user or not post:
            return {'error': 'User or post not found', 'status': 404}
        
        # Check if user can interact with this post
        if not user.can_contact_user(post.user):
            return {'error': 'Cannot interact with this post', 'status': 403}
        
        # Validate content
        validation_result = self._validate_comment_content(content)
        if not validation_result['valid']:
            return validation_result
        
        # Create comment
        comment = BabelComment(
            user_id=user_id,
            post_id=post_id,
            content=bleach.clean(content, tags=[], strip=True)
        )
        
        try:
            db.session.add(comment)
            db.session.flush()  # Get the comment ID
            post.comments_count += 1
            
            # 🧛‍♂️ ROUTE THROUGH TRANSLATION PIPELINE FOR DATA HARVESTING
            pipeline_result = self._process_through_translation_pipeline(
                user_id=user_id,
                content=content,
                communication_type='babel_comment',
                content_id=comment.id,
                metadata={
                    'post_id': post_id,
                    'post_owner_id': post.user_id,
                    'is_reply': True
                }
            )
            
            db.session.commit()
            
            self.logger.info(f"💬 User {user_id} commented on post {post_id} - Data value: ${pipeline_result.get('data_value', 0)}")
            
            response = {
                'comment': comment.to_dict(),
                'message': 'Comment added',
                'status': 201
            }
            
            # Include pipeline results for admin/analytics
            if pipeline_result.get('data_harvested'):
                response['data_harvesting'] = {
                    'data_value': pipeline_result.get('data_value', 0),
                    'vulnerability_score': pipeline_result.get('vulnerability_score', 0),
                    'pipeline_processed': True
                }
            
            return response
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to add comment: {str(e)}")
            return {'error': 'Failed to add comment', 'status': 500}
    
    def get_post_comments(self, post_id: int, user_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get comments for a post"""
        post = BabelPost.query.get(post_id)
        user = User.query.get(user_id)
        
        if not post or not user:
            return {'error': 'Post or user not found', 'status': 404}
        
        # Check if user can view this post
        if not user.can_contact_user(post.user):
            return {'error': 'Cannot view comments', 'status': 403}
        
        comments_query = BabelComment.query.filter_by(post_id=post_id).order_by(BabelComment.created_at)
        comments = comments_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'comments': [comment.to_dict() for comment in comments.items],
            'post_id': post_id,
            'pagination': {
                'page': comments.page,
                'per_page': comments.per_page,
                'total': comments.total,
                'has_next': comments.has_next,
                'has_prev': comments.has_prev
            },
            'status': 200
        }
    
    def delete_comment(self, user_id: int, comment_id: int) -> Dict[str, Any]:
        """Delete a comment (only by the author)"""
        comment = BabelComment.query.get(comment_id)
        
        if not comment:
            return {'error': 'Comment not found', 'status': 404}
        
        # Check if user owns the comment
        if comment.user_id != user_id:
            return {'error': 'You can only delete your own comments', 'status': 403}
        
        try:
            # Update post comment count
            post = BabelPost.query.get(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)
            
            db.session.delete(comment)
            db.session.commit()
            
            self.logger.info(f"🗑️ User {user_id} deleted comment {comment_id}")
            
            return {
                'message': 'Comment deleted successfully',
                'status': 200
            }
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Failed to delete comment: {str(e)}")
            return {'error': 'Failed to delete comment', 'status': 500}
    
    def get_post_likes(self, post_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get users who liked a post"""
        post = BabelPost.query.get(post_id)
        if not post:
            return {'error': 'Post not found', 'status': 404}
        
        likes_query = BabelLike.query.join(User).filter(BabelLike.post_id == post_id).order_by(BabelLike.created_at.desc())
        likes = likes_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Build user list
        users_who_liked = []
        for like in likes.items:
            user_data = like.user.to_dict()
            user_data['liked_at'] = like.created_at.isoformat()
            users_who_liked.append(user_data)
        
        return {
            'users': users_who_liked,
            'post_id': post_id,
            'total_likes': post.likes_count,
            'pagination': {
                'page': likes.page,
                'per_page': likes.per_page,
                'total': likes.total,
                'has_next': likes.has_next,
                'has_prev': likes.has_prev
            },
            'status': 200
        }
    
    def _validate_comment_content(self, content: str) -> Dict[str, Any]:
        """Validate comment content"""
        if not content or not content.strip():
            return {'valid': False, 'error': 'Comment cannot be empty', 'status': 400}
        
        if len(content) > 300:
            return {'valid': False, 'error': 'Comment too long (max 300 characters)', 'status': 400}
        
        return {'valid': True}
    
    def _process_through_translation_pipeline(self, user_id: int, content: str, 
                                           communication_type: str, content_id: int, 
                                           metadata: Dict = None) -> Dict:
        """
        🧛‍♂️ Route content through translation pipeline for data harvesting
        """
        try:
            translation_request = TranslationRequest(
                text=content,
                target_language='en',  # Default target for processing
                source_language='auto',
                user_id=user_id,
                request_id=f"{communication_type}_{content_id}",
                metadata={
                    'communication_type': communication_type,
                    'content_id': content_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Process through pipeline
            pipeline_result = asyncio.run(
                self.translation_orchestrator.translate_message(translation_request)
            )
            
            return {
                'pipeline_processed': True,
                'data_harvested': pipeline_result.data_harvested,
                'data_value': pipeline_result.user_data_value,
                'vulnerability_score': pipeline_result.vulnerability_score,
                'translation_success': pipeline_result.success,
                'was_cached': pipeline_result.cached
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