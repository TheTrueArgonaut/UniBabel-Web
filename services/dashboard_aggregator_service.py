"""
Dashboard Aggregator Service - SRIMI Microservice
Single Responsibility: Aggregate dashboard data from multiple sources
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class DashboardSnapshot:
    """Clean dashboard snapshot data structure"""
    user_stats: Dict[str, Any]
    system_health: Dict[str, Any]
    data_warehouse_summary: Dict[str, Any]
    timestamp: str

class DashboardAggregatorService:
    """Micro-service for dashboard data aggregation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_ttl = 180  # 3 minutes
        
    def get_dashboard_snapshot(self) -> DashboardSnapshot:
        """Get clean dashboard snapshot"""
        try:
            # Get user statistics
            user_stats = self._get_user_stats()
            
            # Get system health
            system_health = self._get_system_health()
            
            # Get data warehouse summary
            data_warehouse_summary = self._get_data_warehouse_summary()
            
            return DashboardSnapshot(
                user_stats=user_stats,
                system_health=system_health,
                data_warehouse_summary=data_warehouse_summary,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard snapshot: {str(e)}")
            raise
    
    def _get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics from user stats service"""
        try:
            from services.user_stats_service import user_stats_service
            
            stats = user_stats_service.get_basic_stats()
            distribution = user_stats_service.get_user_distribution()
            
            return {
                'total_users': stats.total_users,
                'online_users': stats.online_users,
                'premium_users': stats.premium_users,
                'blocked_users': stats.blocked_users,
                'adult_users': stats.adult_users,
                'teen_users': stats.teen_users,
                'distribution': distribution
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {str(e)}")
            return {
                'total_users': 0,
                'online_users': 0,
                'premium_users': 0,
                'blocked_users': 0,
                'adult_users': 0,
                'teen_users': 0,
                'distribution': {},
                'error': str(e)
            }
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get basic system health metrics"""
        try:
            from models import User, Message
            
            user_count = User.query.count()
            message_count = Message.query.count()
            
            return {
                'status': 'operational',
                'database_stats': {
                    'total_users': user_count,
                    'total_messages': message_count
                },
                'api_latency_ms': 150,
                'error_rate': '0.01%'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system health: {str(e)}")
            return {
                'status': 'degraded',
                'error': str(e),
                'api_latency_ms': 999,
                'error_rate': '10%'
            }
    
    def _get_data_warehouse_summary(self) -> Dict[str, Any]:
        """Get data warehouse summary"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            total_profiles = len(data_warehouse.user_profiles)
            total_value = sum(p.total_market_value for p in data_warehouse.user_profiles.values())
            
            return {
                'total_profiles': total_profiles,
                'total_value': total_value,
                'average_value': total_value / max(total_profiles, 1),
                'status': 'active'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting data warehouse summary: {str(e)}")
            return {
                'total_profiles': 0,
                'total_value': 0,
                'average_value': 0,
                'status': 'error',
                'error': str(e)
            }

# Singleton instance
dashboard_aggregator_service = DashboardAggregatorService()