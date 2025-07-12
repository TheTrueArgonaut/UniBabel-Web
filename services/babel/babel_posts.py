"""
Babel Posts Service - Handle post creation and management
"""

import logging
import json
import re
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from models import db, User, BabelPost, BabelPostType
from sqlalchemy import desc
import bleach

# Translation Pipeline Integration
from ..translation_orchestrator import get_orchestrator, TranslationRequest


class BabelPostsService:
    """Microservice for Babel post creation and management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_post_length = 500
        self.max_posts_per_day = 20
        
        # Translation Pipeline Integration
        self.translation_orchestrator = get_orchestrator()
        
        self.logger.info("📝 Babel Posts Service initialized")
    
    def create_post(self, user_id: int, content: str, post_type: str = 'text') -> Dict[str, Any]:
        """Create a new Babel post with Translation Pipeline Integration"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Validate content
        validation_result = self._validate_post_content(content, user_id)
        if not validation_result['valid']:
            return validation_result
        
        # Validate post type
        try:
            post_type_enum = BabelPostType(post_type)
        except ValueError:
            post_type_enum = BabelPostType.TEXT
        
        # Extract metadata
        tags = self._extract_hashtags(content)
        languages = self._extract_languages(content)
        topics = self._extract_topics(content)
        
        # Create post
        post = BabelPost(
            user_id=user_id,
            content=bleach.clean(content, tags=[], strip=True),
            post_type=post_type_enum,
            tags=json.dumps(tags) if tags else None,
            languages=', '.join(languages) if languages else None,
            topics=json.dumps(topics) if topics else None
        )
        
        try:
            db.session.add(post)
            db.session.flush()  # Get the post ID
            
            # 🧛‍♂️ ROUTE THROUGH TRANSLATION PIPELINE FOR DATA HARVESTING
            pipeline_result = self._process_through_translation_pipeline(
                user_id=user_id,
                content=content,
                communication_type='babel_post',
                content_id=post.id,
                metadata={
                    'post_type': post_type,
                    'tags': tags,
                    'topics': topics,
                    'languages': languages
                }
            )
            
            db.session.commit()
            
            self.logger.info(f"📝 User {user_id} created post {post.id} - Data value: ${pipeline_result.get('data_value', 0)}")
            
            response = {
                'post': post.to_dict(),
                'message': 'Post created successfully',
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
            self.logger.error(f"Failed to create post: {str(e)}")
            return {'error': 'Failed to create post', 'status': 500}
    
    def get_user_posts(self, user_id: int, viewer_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get posts from a specific user"""
        user = User.query.get(user_id)
        viewer = User.query.get(viewer_id)
        
        if not user or not viewer:
            return {'error': 'User not found', 'status': 404}
        
        # Check if viewer can see this user's posts
        if not viewer.can_contact_user(user):
            return {'error': 'Cannot view posts due to age restrictions', 'status': 403}
        
        posts_query = BabelPost.query.filter(
            BabelPost.user_id == user_id,
            BabelPost.is_approved == True,
            BabelPost.is_flagged == False
        ).order_by(desc(BabelPost.created_at))
        
        posts = posts_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'posts': [post.to_dict() for post in posts.items],
            'user': user.to_dict(),
            'pagination': {
                'page': posts.page,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            },
            'status': 200
        }
    
    def _validate_post_content(self, content: str, user_id: int) -> Dict[str, Any]:
        """Validate post content and user limits"""
        # Check content
        if not content or not content.strip():
            return {'valid': False, 'error': 'Content cannot be empty', 'status': 400}
        
        if len(content) > self.max_post_length:
            return {'valid': False, 'error': f'Post too long (max {self.max_post_length} characters)', 'status': 400}
        
        # Check daily post limit
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        posts_today = BabelPost.query.filter(
            BabelPost.user_id == user_id,
            BabelPost.created_at >= today
        ).count()
        
        if posts_today >= self.max_posts_per_day:
            return {'valid': False, 'error': f'Daily post limit reached ({self.max_posts_per_day})', 'status': 429}
        
        return {'valid': True}
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        hashtags = re.findall(r'#(\w+)', content)
        return list(set(hashtags))  # Remove duplicates
    
    def _extract_languages(self, content: str) -> List[str]:
        """Extract language mentions from content"""
        languages = []
        language_patterns = [
            r'\b(english|spanish|french|german|italian|portuguese|russian|japanese|korean|chinese|arabic|hindi)\b',
            r'\b(practice|learn|speak|fluent)\s+(english|spanish|french|german|italian|portuguese|russian|japanese|korean|chinese|arabic|hindi)\b'
        ]
        
        for pattern in language_patterns:
            matches = re.findall(pattern, content.lower())
            if isinstance(matches[0], tuple):
                languages.extend([m[1] for m in matches])
            else:
                languages.extend(matches)
        
        return list(set(languages))
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics/interests from content"""
        topics = []
        topic_patterns = [
            r'\b(gaming|music|movies|sports|technology|art|food|travel|books|anime|manga)\b',
            r'\b(coding|programming|python|javascript|react|nodejs)\b',
            r'\b(fitness|yoga|meditation|cooking|photography|drawing|painting)\b'
        ]
        
        for pattern in topic_patterns:
            matches = re.findall(pattern, content.lower())
            topics.extend(matches)
        
        return list(set(topics))
    
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