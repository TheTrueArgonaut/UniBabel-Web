"""
Analytics Orchestrator Service - SRIMI Microservice
Single Responsibility: Coordinate analytics micro-services
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import random

class AnalyticsOrchestratorService:
    """Tiny service to coordinate analytics micro-services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_dashboard_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics data formatted for the dashboard"""
        try:
            from .user_analytics_service import user_analytics_service
            from .message_analytics_service import message_analytics_service
            from .language_analytics_service import language_analytics_service
            from .platform_health_service import platform_health_service
            
            # Get data from each micro-service
            users = user_analytics_service.get_user_metrics(days)
            messages = message_analytics_service.get_message_metrics(days)
            languages = language_analytics_service.get_language_distribution()
            health = platform_health_service.get_health_status()
            
            # Calculate revenue metrics (placeholder for real implementation)
            revenue_last_30d = users.get('total_users', 0) * 12.5  # Avg revenue per user
            sales_last_30d = messages.get('total_translations', 0) * 0.05  # Revenue per translation
            average_user_value = revenue_last_30d / max(users.get('total_users', 1), 1)
            
            # Create top segments (placeholder data)
            top_segments = [
                {'segment_name': 'Premium Users', 'revenue': revenue_last_30d * 0.4},
                {'segment_name': 'Business Translation', 'revenue': revenue_last_30d * 0.3},
                {'segment_name': 'API Access', 'revenue': revenue_last_30d * 0.2},
                {'segment_name': 'Data Licensing', 'revenue': revenue_last_30d * 0.1}
            ]
            
            # Generate daily trends
            daily_trends = []
            for i in range(min(days, 30)):
                date = datetime.utcnow() - timedelta(days=i)
                daily_trends.append({
                    'date': date.isoformat(),
                    'revenue': random.randint(50, 300),
                    'sales': random.randint(5, 25),
                    'new_users': random.randint(1, 15)
                })
            
            return {
                'revenue_last_30d': revenue_last_30d,
                'sales_last_30d': sales_last_30d,
                'average_user_value': average_user_value,
                'top_segments': top_segments,
                'daily_trends': daily_trends[::-1],  # Reverse to show oldest first
                'users': users,
                'messages': messages,
                'languages': languages,
                'health': health
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard analytics error: {e}")
            return {'error': str(e)}

    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard updates"""
        try:
            from .user_analytics_service import user_analytics_service
            from .message_analytics_service import message_analytics_service
            from .platform_health_service import platform_health_service
            
            # Get current metrics
            users = user_analytics_service.get_user_metrics(1)  # Last 24 hours
            messages = message_analytics_service.get_message_metrics(1)
            health = platform_health_service.get_health_status()
            
            return {
                'active_users_24h': users.get('active_users', 0),
                'messages_24h': messages.get('period_messages', 0),
                'translations_24h': messages.get('total_translations', 0),
                'system_health': health.get('overall_status', 'unknown'),
                'cache_hit_rate': messages.get('cache_hit_rate', 0),
                'translation_rate': messages.get('translation_rate', 0),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Realtime metrics error: {e}")
            return {'error': str(e)}
    
    def get_comprehensive_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get all analytics by coordinating micro-services"""
        try:
            from .user_analytics_service import user_analytics_service
            from .message_analytics_service import message_analytics_service
            from .language_analytics_service import language_analytics_service
            from .platform_health_service import platform_health_service
            
            # Get data from each micro-service
            users = user_analytics_service.get_user_metrics(days)
            messages = message_analytics_service.get_message_metrics(days)
            languages = language_analytics_service.get_language_distribution()
            health = platform_health_service.get_health_status()
            
            # Create overview
            overview = {
                'total_users': users.get('total_users', 0),
                'total_messages': messages.get('total_messages', 0),
                'total_translations': messages.get('total_translations', 0),
                'messages_per_user': round(messages.get('total_messages', 0) / max(users.get('total_users', 1), 1), 2),
                'period_days': days
            }
            
            return {
                'overview': overview,
                'users': users,
                'messages': messages,
                'languages': languages,
                'health': health
            }
            
        except Exception as e:
            self.logger.error(f"Analytics orchestration error: {e}")
            return {}

# Singleton
analytics_orchestrator_service = AnalyticsOrchestratorService()