"""
Babel Timeline Service - Handle feed generation and content discovery
"""

import logging
from typing import Dict, Any, List
from models import db, User, BabelPost, BabelLike
from sqlalchemy import desc


class BabelTimelineService:
    """Microservice for Babel timeline and content discovery"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("📰 Babel Timeline Service initialized")
    
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
        posts_query = self._apply_age_filtering(posts_query, user)
        
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
        liked_posts = self._get_user_liked_posts(user_id, posts.items)
        
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
        if post_type:
            from models import BabelPostType
            if post_type in [t.value for t in BabelPostType]:
                search_query = search_query.filter(BabelPost.post_type == post_type)
        
        # Apply age-based filtering
        search_query = self._apply_age_filtering(search_query, user)
        
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
    
    def get_trending_posts(self, user_id: int, hours: int = 24, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get trending posts based on engagement"""
        from datetime import datetime, timedelta
        
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        # Get posts from the last X hours
        since = datetime.utcnow() - timedelta(hours=hours)
        
        trending_query = BabelPost.query.join(User).filter(
            BabelPost.is_approved == True,
            BabelPost.is_flagged == False,
            BabelPost.created_at >= since,
            (BabelPost.likes_count + BabelPost.comments_count) > 0
        )
        
        # Apply age-based filtering
        trending_query = self._apply_age_filtering(trending_query, user)
        
        # Order by engagement score
        trending_query = trending_query.order_by(
            desc(BabelPost.likes_count + (BabelPost.comments_count * 2))  # Comments weighted more
        )
        
        posts = trending_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get user's liked posts
        liked_posts = self._get_user_liked_posts(user_id, posts.items)
        
        # Build response with engagement metrics
        trending_posts = []
        for post in posts.items:
            post_data = post.to_dict()
            post_data['is_liked'] = post.id in liked_posts
            post_data['engagement_score'] = post.likes_count + (post.comments_count * 2)
            trending_posts.append(post_data)
        
        return {
            'posts': trending_posts,
            'trending_period_hours': hours,
            'pagination': {
                'page': posts.page,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            },
            'status': 200
        }
    
    def get_posts_by_topic(self, topic: str, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get posts filtered by topic/hashtag"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found', 'status': 404}
        
        topic_query = BabelPost.query.join(User).filter(
            BabelPost.is_approved == True,
            BabelPost.is_flagged == False,
            db.or_(
                BabelPost.tags.ilike(f'%{topic}%'),
                BabelPost.topics.ilike(f'%{topic}%')
            )
        )
        
        # Apply age-based filtering
        topic_query = self._apply_age_filtering(topic_query, user)
        
        # Order by recency and engagement
        topic_query = topic_query.order_by(
            desc(BabelPost.created_at),
            desc(BabelPost.likes_count + BabelPost.comments_count)
        )
        
        posts = topic_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'posts': [post.to_dict() for post in posts.items],
            'topic': topic,
            'pagination': {
                'page': posts.page,
                'per_page': posts.per_page,
                'total': posts.total,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            },
            'status': 200
        }
    
    def _apply_age_filtering(self, query, user):
        """Apply age-appropriate content filtering"""
        if user.user_type.value == 'child':
            query = query.filter(User.user_type == user.user_type)
        elif user.user_type.value == 'teen':
            query = query.filter(User.user_type.in_(['teen', 'adult']))
        else:  # adult
            query = query.filter(User.user_type.in_(['teen', 'adult']))
        
        return query
    
    def _get_user_liked_posts(self, user_id: int, posts: List) -> set:
        """Get set of post IDs that user has liked"""
        if not posts:
            return set()
        
        post_ids = [p.id for p in posts]
        likes = BabelLike.query.filter(
            BabelLike.user_id == user_id,
            BabelLike.post_id.in_(post_ids)
        ).all()
        
        return {like.post_id for like in likes}