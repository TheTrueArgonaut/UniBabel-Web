"""
Babel Services Package - Unified interface for all Babel microservices
"""

from .babel_posts import BabelPostsService
from .babel_timeline import BabelTimelineService
from .babel_interactions import BabelInteractionsService
from typing import Dict, Any


class BabelService:
    """Unified Babel Service - Orchestrates all Babel microservices"""
    
    def __init__(self):
        # Initialize all microservices
        self.posts = BabelPostsService()
        self.timeline = BabelTimelineService()
        self.interactions = BabelInteractionsService()
        
        # Service metadata
        self.service_name = "BabelService"
        self.version = "3.0.0"  # Microservice architecture
        self.dependencies = ['translation_orchestrator', 'data_vampire_service']
    
    # Posts operations (delegate to posts microservice)
    def create_post(self, user_id: int, content: str, post_type: str = 'text') -> Dict[str, Any]:
        """Create a new Babel post"""
        return self.posts.create_post(user_id, content, post_type)
    
    def get_user_posts(self, user_id: int, viewer_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get posts from a specific user"""
        return self.posts.get_user_posts(user_id, viewer_id, page, per_page)
    
    # Timeline operations (delegate to timeline microservice)
    def get_timeline(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get timeline posts for a user"""
        return self.timeline.get_timeline(user_id, page, per_page)
    
    def search_posts(self, query: str, user_id: int, post_type: str = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Search Babel posts"""
        return self.timeline.search_posts(query, user_id, post_type, page, per_page)
    
    def get_trending_posts(self, user_id: int, hours: int = 24, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get trending posts"""
        return self.timeline.get_trending_posts(user_id, hours, page, per_page)
    
    def get_posts_by_topic(self, topic: str, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get posts by topic/hashtag"""
        return self.timeline.get_posts_by_topic(topic, user_id, page, per_page)
    
    # Interaction operations (delegate to interactions microservice)
    def like_post(self, user_id: int, post_id: int) -> Dict[str, Any]:
        """Like or unlike a post"""
        return self.interactions.like_post(user_id, post_id)
    
    def add_comment(self, user_id: int, post_id: int, content: str) -> Dict[str, Any]:
        """Add a comment to a post"""
        return self.interactions.add_comment(user_id, post_id, content)
    
    def get_post_comments(self, post_id: int, user_id: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get comments for a post"""
        return self.interactions.get_post_comments(post_id, user_id, page, per_page)
    
    def delete_comment(self, user_id: int, comment_id: int) -> Dict[str, Any]:
        """Delete a comment"""
        return self.interactions.delete_comment(user_id, comment_id)
    
    def get_post_likes(self, post_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get users who liked a post"""
        return self.interactions.get_post_likes(post_id, page, per_page)
    
    # Service health and info
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            from models import BabelPost
            test_count = BabelPost.query.count()
            
            return {
                'status': 'healthy',
                'service': self.service_name,
                'version': self.version,
                'microservices': {
                    'posts': 'healthy',
                    'timeline': 'healthy',
                    'interactions': 'healthy'
                },
                'database': 'connected',
                'posts_count': test_count
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
            'architecture': 'microservices',
            'dependencies': self.dependencies,
            'microservices': {
                'posts': {
                    'responsibility': 'Post creation and management',
                    'endpoints': ['create_post', 'get_user_posts']
                },
                'timeline': {
                    'responsibility': 'Feed generation and discovery',
                    'endpoints': ['get_timeline', 'search_posts', 'get_trending_posts', 'get_posts_by_topic']
                },
                'interactions': {
                    'responsibility': 'Likes and comments',
                    'endpoints': ['like_post', 'add_comment', 'get_post_comments', 'delete_comment', 'get_post_likes']
                }
            },
            'limits': {
                'max_post_length': 500,
                'max_posts_per_day': 20,
                'max_comment_length': 300
            }
        }


# Global instance
_babel_service = BabelService()


def get_babel_service() -> BabelService:
    """Get the global Babel service instance"""
    return _babel_service


# Export individual microservices for direct access if needed
__all__ = ['BabelService', 'get_babel_service', 'BabelPostsService', 'BabelTimelineService', 'BabelInteractionsService']