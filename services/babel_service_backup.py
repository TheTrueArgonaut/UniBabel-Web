"""
Babel Service
Handles: Twitter-like posts, timeline, likes, comments, and social discovery
+ Translation Pipeline Integration for Data Harvesting
"""

import logging
import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import current_app
from models import db, User, BabelPost, BabelLike, BabelComment, BabelFollow, BabelPostType
from sqlalchemy import desc, func
import bleach

# Translation Pipeline Integration
from .translation_orchestrator import get_orchestrator, TranslationRequest


# Service decorator for dependency injection
def service_component(name: str, dependencies: List[str] = None):
    """Decorator to mark classes as microservices"""
    def decorator(cls):
        cls._service_name = name
        cls._dependencies = dependencies or []
        return cls
    return decorator


@service_component('babel_service')
class BabelService:
    """
    Focused microservice for Babel (Twitter-like) operations
    🧛‍♂️ NOW WITH FULL TRANSLATION PIPELINE + DATA VAMPIRE INTEGRATION
    
    Single Responsibility: Social timeline and discovery
    Reactive: Async-ready operations
    Injectable: Clean dependency interfaces
    Micro: Focused on one domain only
    Interfaces: Clear API contracts
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_post_length = 500
        self.max_posts_per_day = 20
        
        # Translation Pipeline Integration
        self.translation_orchestrator = get_orchestrator()
        
        # Microservice configuration
        self.service_name = "BabelService"
        self.version = "2.0.0"  # Updated for translation pipeline integration
        self.dependencies = ['translation_orchestrator', 'data_vampire_service']
        
        self.logger.info("🧛‍♂️ Babel Service v2.0 initialized with Translation Pipeline + Data Vampire")
    
    def create_post(self, user_id: int, content: str, post_type: str = 'text') -> Dict[str, Any]:
        """Create a new Babel post with Translation Pipeline Integration"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Validate content
        if not content or not content.strip():
            return {'error': 'Content cannot be empty', 'status': 400}
        
        if len(content) > self.max_post_length:
            return {'error': f'Post too long (max {self.max_post_length} characters)', 'status': 400}
        
        # Check daily post limit
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        posts_today = BabelPost.query.filter(
            BabelPost.user_id == user_id,
            BabelPost.created_at >= today
        ).count()
        
        if posts_today >= self.max_posts_per_day:
            return {'error': f'Daily post limit reached ({self.max_posts_per_day})', 'status': 429}
        
        # Validate post type
        try:
            post_type_enum = BabelPostType(post_type)
        except ValueError:
            post_type_enum = BabelPostType.TEXT
        
        # Extract hashtags and mentions
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
            
            self.logger.info(f"🧛‍♂️ User {user_id} created Babel post {post.id} - Data value: ${pipeline_result.get('data_value', 0)}")
            
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
    
    def get_timeline(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get timeline posts for a user"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Get posts from users the current user can interact with (age-appropriate)
        posts_query = BabelPost.query.join(User).filter(
            BabelPost.is_approved == True,
            BabelPost.is_flagged == False
        )
        
        # Apply age-based filtering
        if user.user_type.value == 'child':
            posts_query = posts_query.filter(User.user_type == user.user_type)
        elif user.user_type.value == 'teen':
            posts_query = posts_query.filter(User.user_type.in_(['teen', 'adult']))
        else:  # adult
            posts_query = posts_query.filter(User.user_type.in_(['teen', 'adult']))
        
        # Order by engagement and recency
        posts_query = posts_query.order_by(
            desc(BabelPost.likes_count + BabelPost.comments_count),
            desc(BabelPost.created_at)
        )
        
        # Paginate
        posts = posts_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get user's liked posts for UI state
        liked_posts = set()
        if posts.items:
            post_ids = [p.id for p in posts.items]
            likes = BabelLike.query.filter(
                BabelLike.user_id == user_id,
                BabelLike.post_id.in_(post_ids)
            ).all()
            liked_posts = {like.post_id for like in likes}
        
        # Build response
        timeline_posts = []
        for post in posts.items:
            post_data = post.to_dict()
            post_data['is_liked'] = post.id in liked_posts
            timeline_posts.append(post_data)
        
        return {
            'posts': timeline_posts,
            'pagination': {
                'page': posts.page,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            },
            'status': 200
        }
    
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
        if not content or not content.strip():
            return {'error': 'Comment cannot be empty', 'status': 400}
        
        if len(content) > 300:
            return {'error': 'Comment too long (max 300 characters)', 'status': 400}
        
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
            
            self.logger.info(f"🧛‍♂️ User {user_id} commented on post {post_id} - Data value: ${pipeline_result.get('data_value', 0)}")
            
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
            'pagination': {
                'page': comments.page,
                'per_page': comments.per_page,
                'total': comments.total,
                'has_next': comments.has_next,
                'has_prev': comments.has_prev
            },
            'status': 200
        }
    
    def search_posts(self, query: str, user_id: int, post_type: str = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search Babel posts"""
        if len(query) < 2:
            return {'posts': [], 'status': 200}
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Base search query
        search_query = BabelPost.query.join(User).filter(
            BabelPost.is_approved == True,
            BabelPost.is_flagged == False,
            db.or_(
                BabelPost.content.ilike(f'%{query}%'),
                BabelPost.tags.ilike(f'%{query}%'),
                BabelPost.topics.ilike(f'%{query}%'),
                BabelPost.languages.ilike(f'%{query}%')
            )
        )
        
        # Filter by post type if specified
        if post_type and post_type in [t.value for t in BabelPostType]:
            search_query = search_query.filter(BabelPost.post_type == post_type)
        
        # Apply age-based filtering
        if user.user_type.value == 'child':
            search_query = search_query.filter(User.user_type == user.user_type)
        elif user.user_type.value == 'teen':
            search_query = search_query.filter(User.user_type.in_(['teen', 'adult']))
        else:  # adult
            search_query = search_query.filter(User.user_type.in_(['teen', 'adult']))
        
        # Order by relevance and recency
        search_query = search_query.order_by(
            desc(BabelPost.likes_count + BabelPost.comments_count),
            desc(BabelPost.created_at)
        )
        
        posts = search_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'posts': [post.to_dict() for post in posts.items],
            'query': query,
            'post_type': post_type,
            'pagination': {
                'page': posts.page,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            },
            'status': 200
        }
    
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
        
        This processes ALL outgoing communication through the translation pipeline
        to ensure consistent data harvesting regardless of translation settings
        """
        try:
            # Create translation request (even if user has auto-translate OFF)
            # The pipeline will handle the user's translation preference
            # but will ALWAYS perform data harvesting
            
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
            
            # Process through pipeline (async but we'll wait for it)
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
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Test database connection
            test_count = BabelPost.query.count()
            
            return {
                'status': 'healthy',
                'service': self.service_name,
                'version': self.version,
                'database': 'connected',
                'posts_count': test_count,
                'max_post_length': self.max_post_length,
                'max_posts_per_day': self.max_posts_per_day
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': self.service_name,
                'error': str(e)
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': self.service_name,
            'version': self.version,
            'dependencies': self.dependencies,
            'endpoints': [
                'create_post', 'get_timeline', 'get_user_posts',
                'like_post', 'add_comment', 'get_post_comments', 'search_posts'
            ],
            'limits': {
                'max_post_length': self.max_post_length,
                'max_posts_per_day': self.max_posts_per_day
            }
        }


# Global instance
_babel_service = BabelService()


def get_babel_service() -> BabelService:
    """Get the global Babel service instance"""
    return _babel_service