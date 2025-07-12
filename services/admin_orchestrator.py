"""
Admin Orchestrator Service - SRIMI Microservice
Single Responsibility: Lightweight coordinator for admin micro-services
"""

from typing import Dict, Any
from dataclasses import dataclass
import logging

@dataclass
class AdminDashboardData:
    """Complete admin dashboard data structure"""
    dashboard_snapshot: Dict[str, Any]
    recent_activity: Dict[str, Any]
    system_alerts: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    timestamp: str

class AdminOrchestrator:
    """Lightweight coordinator for admin micro-services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_dashboard_overview(self) -> AdminDashboardData:
        """Get complete dashboard overview by coordinating micro-services"""
        from datetime import datetime
        
        try:
            # Use dashboard aggregator service
            from services.dashboard_aggregator_service import dashboard_aggregator_service
            dashboard_snapshot = dashboard_aggregator_service.get_dashboard_snapshot()
            
            # Use activity monitor service
            from services.activity_monitor_service import activity_monitor_service
            recent_activity = {
                'activities': [vars(activity) for activity in activity_monitor_service.get_recent_activity(limit=5)],
                'count': len(activity_monitor_service.get_recent_activity(limit=5))
            }
            
            # Use activity monitor for alerts
            system_alerts = {
                'alerts': [vars(alert) for alert in activity_monitor_service.get_system_alerts()],
                'count': len(activity_monitor_service.get_system_alerts())
            }
            
            # Use performance metrics service
            from services.performance_metrics_service import performance_metrics_service
            performance_metrics = performance_metrics_service.get_metrics_summary()
            
            return AdminDashboardData(
                dashboard_snapshot=vars(dashboard_snapshot),
                recent_activity=recent_activity,
                system_alerts=system_alerts,
                performance_metrics=performance_metrics,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard overview: {str(e)}")
            raise
    
    def get_user_management_data(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get coordinated user management data using micro-services"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_enrichment_service import user_enrichment_service
            from services.user_stats_service import user_stats_service
            
            # Get basic profiles
            profiles = user_profile_service.get_user_profiles_batch(limit=limit, offset=offset)
            
            # Enrich with data warehouse info
            enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)
            
            # Get stats
            stats = user_stats_service.get_basic_stats()
            
            # Convert to response format
            users_data = user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)
            
            return {
                'users': users_data,
                'stats': {
                    'total_users': stats.total_users,
                    'online_users': stats.online_users,
                    'premium_users': stats.premium_users,
                    'blocked_users': stats.blocked_users
                },
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'returned_count': len(enriched_profiles)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user management data: {str(e)}")
            raise
    
    def search_across_services(self, search_term: str, search_type: str = 'all') -> Dict[str, Any]:
        """Search across services using search orchestrator"""
        try:
            from services.search_orchestrator_service import search_orchestrator_service
            
            if search_type == 'users':
                return search_orchestrator_service.search_users_only(search_term)
            elif search_type == 'data_warehouse':
                return search_orchestrator_service.search_data_warehouse_only(search_term)
            else:
                return search_orchestrator_service.search_all_services(search_term)
            
        except Exception as e:
            self.logger.error(f"Error searching across services: {str(e)}")
            raise

# Singleton instance
admin_orchestrator = AdminOrchestrator()