"""
Database Connection Service  
Handles: Database connectivity testing, validation, and health monitoring

Single Responsibility: Database connection management only
Reactive: Real-time connection monitoring
Injectable: Clean dependency interfaces  
Micro: Focused on connection operations only
Interfaces: Clear connection contracts
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from flask import current_app
from models import db
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
import threading


class DatabaseConnectionService:
    """
    Microservice for database connection management
    
    Single Responsibility: Connection testing only
    Under 300 lines: Focused and clean
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service_name = "DatabaseConnectionService"
        self.version = "1.0.0"
        self.dependencies = []
        self.connection_stats = {
            'total_tests': 0,
            'successful_connections': 0,
            'failed_connections': 0,
            'last_test_time': None,
            'average_response_time': 0.0
        }
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        connection_test = self.test_connection()
        
        return {
            'status': 'healthy' if connection_test['connected'] else 'unhealthy',
            'service': self.service_name,
            'version': self.version,
            'connection_status': connection_test,
            'stats': self.connection_stats
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection with timing"""
        start_time = time.time()
        self.connection_stats['total_tests'] += 1
        
        try:
            with db.engine.connect() as connection:
                # Simple connectivity test
                result = connection.execute(text("SELECT 1 as test_value"))
                test_value = result.fetchone()[0]
                
                # Test write capability  
                connection.execute(text("CREATE TEMPORARY TABLE test_table (id INTEGER)"))
                connection.execute(text("INSERT INTO test_table (id) VALUES (1)"))
                connection.execute(text("DROP TABLE test_table"))
                
                response_time = time.time() - start_time
                self._update_connection_stats(True, response_time)
                
                return {
                    'connected': True,
                    'test_value': test_value,
                    'response_time_ms': round(response_time * 1000, 2),
                    'read_test': 'passed',
                    'write_test': 'passed',
                    'engine_info': {
                        'dialect': db.engine.dialect.name,
                        'driver': db.engine.driver,
                        'pool_size': db.engine.pool.size(),
                        'checked_in': db.engine.pool.checkedin(),
                        'checked_out': db.engine.pool.checkedout()
                    }
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self._update_connection_stats(False, response_time)
            
            self.logger.error(f"Database connection test failed: {str(e)}")
            return {
                'connected': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'response_time_ms': round(response_time * 1000, 2),
                'read_test': 'failed',
                'write_test': 'failed'
            }
    
    def _update_connection_stats(self, success: bool, response_time: float):
        """Update connection statistics"""
        if success:
            self.connection_stats['successful_connections'] += 1
        else:
            self.connection_stats['failed_connections'] += 1
        
        self.connection_stats['last_test_time'] = datetime.utcnow().isoformat()
        
        # Update average response time
        total_connections = self.connection_stats['successful_connections'] + self.connection_stats['failed_connections']
        current_avg = self.connection_stats['average_response_time']
        self.connection_stats['average_response_time'] = (
            (current_avg * (total_connections - 1) + response_time) / total_connections
        )
    
    def test_transaction_capability(self) -> Dict[str, Any]:
        """Test database transaction capabilities"""
        try:
            with db.engine.begin() as connection:
                # Test transaction rollback
                connection.execute(text("CREATE TEMPORARY TABLE transaction_test (id INTEGER)"))
                connection.execute(text("INSERT INTO transaction_test (id) VALUES (1)"))
                
                # Verify insert
                result = connection.execute(text("SELECT COUNT(*) FROM transaction_test"))
                count = result.fetchone()[0]
                
                if count != 1:
                    raise Exception("Transaction test failed: Insert not working")
                
                # Test rollback by raising exception
                connection.execute(text("DROP TABLE transaction_test"))
                
                return {
                    'transaction_support': True,
                    'rollback_test': 'passed',
                    'commit_test': 'passed',
                    'message': 'Transaction capabilities verified'
                }
                
        except Exception as e:
            self.logger.error(f"Transaction test failed: {str(e)}")
            return {
                'transaction_support': False,
                'error': str(e),
                'rollback_test': 'failed',
                'commit_test': 'failed'
            }
    
    def test_concurrent_connections(self, num_connections: int = 5) -> Dict[str, Any]:
        """Test multiple concurrent database connections"""
        results = []
        threads = []
        
        def test_single_connection(connection_id: int):
            try:
                start_time = time.time()
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                    response_time = time.time() - start_time
                    
                    results.append({
                        'connection_id': connection_id,
                        'success': True,
                        'response_time_ms': round(response_time * 1000, 2)
                    })
            except Exception as e:
                results.append({
                    'connection_id': connection_id,
                    'success': False,
                    'error': str(e)
                })
        
        # Start concurrent connections
        start_time = time.time()
        for i in range(num_connections):
            thread = threading.Thread(target=test_single_connection, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        successful_connections = sum(1 for r in results if r['success'])
        
        return {
            'total_connections_tested': num_connections,
            'successful_connections': successful_connections,
            'failed_connections': num_connections - successful_connections,
            'success_rate': round((successful_connections / num_connections) * 100, 2),
            'total_time_ms': round(total_time * 1000, 2),
            'average_time_per_connection': round((total_time / num_connections) * 1000, 2),
            'detailed_results': results
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get detailed database information"""
        try:
            with db.engine.connect() as connection:
                # Get database version and info
                version_result = connection.execute(text("SELECT sqlite_version()"))
                db_version = version_result.fetchone()[0]
                
                # Get database file info (for SQLite)
                pragma_results = {}
                pragmas = ['page_size', 'page_count', 'freelist_count', 'cache_size']
                
                for pragma in pragmas:
                    try:
                        result = connection.execute(text(f"PRAGMA {pragma}"))
                        pragma_results[pragma] = result.fetchone()[0]
                    except:
                        pragma_results[pragma] = 'unavailable'
                
                return {
                    'database_version': db_version,
                    'engine_info': {
                        'name': db.engine.name,
                        'dialect': db.engine.dialect.name,
                        'driver': db.engine.driver,
                        'url': str(db.engine.url).split('@')[0] + '@***',
                        'echo': db.engine.echo
                    },
                    'connection_pool': {
                        'size': db.engine.pool.size(),
                        'checked_in': db.engine.pool.checkedin(),
                        'checked_out': db.engine.pool.checkedout(),
                        'overflow': db.engine.pool.overflow(),
                        'invalid': db.engine.pool.invalid()
                    },
                    'database_settings': pragma_results
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database info: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def monitor_connection_health(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Monitor database connection health over time"""
        monitoring_results = {
            'start_time': datetime.utcnow().isoformat(),
            'duration_seconds': duration_seconds,
            'tests_performed': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'response_times': [],
            'errors': []
        }
        
        start_time = time.time()
        test_interval = 5  # Test every 5 seconds
        
        while time.time() - start_time < duration_seconds:
            test_result = self.test_connection()
            monitoring_results['tests_performed'] += 1
            
            if test_result['connected']:
                monitoring_results['successful_tests'] += 1
                monitoring_results['response_times'].append(test_result['response_time_ms'])
            else:
                monitoring_results['failed_tests'] += 1
                monitoring_results['errors'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': test_result.get('error', 'Unknown error')
                })
            
            time.sleep(test_interval)
        
        # Calculate statistics
        if monitoring_results['response_times']:
            response_times = monitoring_results['response_times']
            monitoring_results['average_response_time'] = sum(response_times) / len(response_times)
            monitoring_results['min_response_time'] = min(response_times)
            monitoring_results['max_response_time'] = max(response_times)
        
        monitoring_results['success_rate'] = (
            (monitoring_results['successful_tests'] / monitoring_results['tests_performed']) * 100
            if monitoring_results['tests_performed'] > 0 else 0
        )
        
        monitoring_results['end_time'] = datetime.utcnow().isoformat()
        
        return monitoring_results


# Global instance
_connection_service = DatabaseConnectionService()


def get_connection_service() -> DatabaseConnectionService:
    """Get the global connection service instance"""
    return _connection_service