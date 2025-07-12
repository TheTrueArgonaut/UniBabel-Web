"""
Performance Metrics Service - SRIMI Microservice
Single Responsibility: Collect and calculate performance metrics
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_time_ms: float
    throughput_requests_per_sec: float
    error_rate_percent: float
    cache_hit_ratio_percent: float
    database_connections: int
    memory_usage_mb: float
    active_users: int
    data_warehouse_size: int
    timestamp: str

class PerformanceMetricsService:
    """Micro-service for performance metrics collection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_cache = {}
        self.cache_ttl = 60  # 1 minute
        
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        try:
            # Calculate response time
            response_time = self._calculate_response_time()
            
            # Calculate throughput
            throughput = self._calculate_throughput()
            
            # Calculate error rate
            error_rate = self._calculate_error_rate()
            
            # Get cache metrics
            cache_hit_ratio = self._get_cache_hit_ratio()
            
            # Get database metrics
            db_connections = self._get_database_connections()
            
            # Get memory usage
            memory_usage = self._get_memory_usage()
            
            # Get active users
            active_users = self._get_active_users()
            
            # Get data warehouse size
            dw_size = self._get_data_warehouse_size()
            
            return PerformanceMetrics(
                response_time_ms=response_time,
                throughput_requests_per_sec=throughput,
                error_rate_percent=error_rate,
                cache_hit_ratio_percent=cache_hit_ratio,
                database_connections=db_connections,
                memory_usage_mb=memory_usage,
                active_users=active_users,
                data_warehouse_size=dw_size,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {str(e)}")
            raise
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get simplified metrics summary"""
        try:
            metrics = self.get_current_metrics()
            
            # Determine health status
            health_status = 'healthy'
            if metrics.response_time_ms > 500:
                health_status = 'degraded'
            if metrics.error_rate_percent > 5:
                health_status = 'unhealthy'
            
            return {
                'health_status': health_status,
                'response_time_ms': metrics.response_time_ms,
                'active_users': metrics.active_users,
                'error_rate_percent': metrics.error_rate_percent,
                'timestamp': metrics.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error getting metrics summary: {str(e)}")
            return {
                'health_status': 'error',
                'response_time_ms': 999,
                'active_users': 0,
                'error_rate_percent': 100,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _calculate_response_time(self) -> float:
        """Calculate average response time"""
        try:
            # Simplified: return mock response time
            # In real implementation, would track actual response times
            return 150.0
            
        except Exception as e:
            self.logger.error(f"Error calculating response time: {str(e)}")
            return 999.0
    
    def _calculate_throughput(self) -> float:
        """Calculate requests per second"""
        try:
            # Simplified: return mock throughput
            # In real implementation, would track actual request counts
            return 45.0
            
        except Exception as e:
            self.logger.error(f"Error calculating throughput: {str(e)}")
            return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        try:
            # Simplified: return mock error rate
            # In real implementation, would track actual errors
            return 0.01
            
        except Exception as e:
            self.logger.error(f"Error calculating error rate: {str(e)}")
            return 10.0
    
    def _get_cache_hit_ratio(self) -> float:
        """Get cache hit ratio percentage"""
        try:
            # Simplified: return mock cache hit ratio
            # In real implementation, would track actual cache hits/misses
            return 85.0
            
        except Exception as e:
            self.logger.error(f"Error getting cache hit ratio: {str(e)}")
            return 0.0
    
    def _get_database_connections(self) -> int:
        """Get number of active database connections"""
        try:
            # Simplified: return mock connection count
            # In real implementation, would query actual DB connection pool
            return 12
            
        except Exception as e:
            self.logger.error(f"Error getting database connections: {str(e)}")
            return 0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            # Simplified: return mock memory usage
            # In real implementation, would get actual memory usage
            return 256.0
            
        except Exception as e:
            self.logger.error(f"Error getting memory usage: {str(e)}")
            return 0.0
    
    def _get_active_users(self) -> int:
        """Get number of active users"""
        try:
            from services.user_stats_service import user_stats_service
            
            stats = user_stats_service.get_basic_stats()
            return stats.online_users
            
        except Exception as e:
            self.logger.error(f"Error getting active users: {str(e)}")
            return 0
    
    def _get_data_warehouse_size(self) -> int:
        """Get size of data warehouse"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            return len(data_warehouse.user_profiles)
            
        except Exception as e:
            self.logger.error(f"Error getting data warehouse size: {str(e)}")
            return 0

# Singleton instance
performance_metrics_service = PerformanceMetricsService()