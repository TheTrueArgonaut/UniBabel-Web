"""
Endpoint Coordinator - SRIMI Microservice  
Single Responsibility: Coordinate endpoint data flow
"""

from typing import Dict, Any, List
import logging

class EndpointCoordinator:
    """Micro-coordinator for endpoint data sharing"""
    
    def __init__(self):
        self.shared_data = {}
        self.endpoint_registry = {}
        self.logger = logging.getLogger(__name__)
    
    def register_endpoint(self, endpoint_name: str, data_provider_func) -> None:
        """Register an endpoint with its data provider"""
        self.endpoint_registry[endpoint_name] = data_provider_func
        self.logger.info(f"📡 Registered endpoint: {endpoint_name}")
    
    def coordinate_analytics_data(self) -> Dict[str, Any]:
        """Coordinate data flow between analytics endpoints"""
        try:
            # Try to get analytics data but handle errors gracefully
            analytics_data = {}
            warehouse_stats = {}
            
            try:
                from services.analytics_orchestrator_service import analytics_orchestrator_service
                analytics_data = analytics_orchestrator_service.get_dashboard_analytics(days=30)
            except Exception as e:
                self.logger.warning(f"Analytics service unavailable: {e}")
                analytics_data = {
                    'users': {'total_users': 0},
                    'health': {'overall_status': 'service_unavailable'}
                }
            
            try:
                from services.data_warehouse_analytics import data_warehouse_analytics
                warehouse_stats = data_warehouse_analytics.get_dashboard_stats()
            except Exception as e:
                self.logger.warning(f"Data warehouse service unavailable: {e}")
                warehouse_stats = {
                    'total_users': 0,
                    'total_value': 0,
                    'high_value_targets': 0,
                    'vulnerable_targets': 0,
                    'potential_revenue': 0
                }
            
            # Coordinate shared metrics with fallback values
            coordinated_data = {
                'analytics': analytics_data,
                'warehouse': warehouse_stats,
                'unified_metrics': {
                    'total_users': max(
                        analytics_data.get('users', {}).get('total_users', 0),
                        warehouse_stats.get('total_users', 0)
                    ),
                    'data_value': warehouse_stats.get('total_value', 0),
                    'system_health': analytics_data.get('health', {}).get('overall_status', 'unknown')
                }
            }
            
            self.shared_data['coordinated_analytics'] = coordinated_data
            return coordinated_data
            
        except Exception as e:
            self.logger.error(f"Analytics coordination failed: {e}")
            # Return safe fallback data
            return {
                'analytics': {'users': {'total_users': 0}, 'health': {'overall_status': 'error'}},
                'warehouse': {'total_users': 0, 'total_value': 0, 'high_value_targets': 0, 'vulnerable_targets': 0, 'potential_revenue': 0},
                'unified_metrics': {'total_users': 0, 'data_value': 0, 'system_health': 'error'},
                'error': str(e)
            }
    
    def get_unified_dashboard_data(self) -> Dict[str, Any]:
        """Get unified data for all dashboards"""
        return self.coordinate_analytics_data()
    
    def share_data_between_endpoints(self, source_endpoint: str, target_endpoint: str, data_key: str) -> bool:
        """Share data between different endpoints"""
        try:
            if source_endpoint in self.endpoint_registry and target_endpoint in self.endpoint_registry:
                # Create data bridge
                if data_key not in self.shared_data:
                    self.shared_data[data_key] = {}
                
                self.shared_data[data_key][f"{source_endpoint}_to_{target_endpoint}"] = {
                    'active': True,
                    'last_sync': None
                }
                
                self.logger.info(f"🌉 Data bridge created: {source_endpoint} → {target_endpoint}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Data sharing failed: {e}")
            return False

# Singleton coordinator
endpoint_coordinator = EndpointCoordinator()