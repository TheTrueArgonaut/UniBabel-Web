"""
Data Warehouse Routes - SRIMI Microservice
Single Responsibility: Data warehouse API endpoints only
"""

from flask import Flask, request, jsonify, render_template
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_data_warehouse_routes(app: Flask, audit_logger) -> None:
    """Register data warehouse routes with harmonious coordination"""
    
    # Register with endpoint coordinator
    from services.endpoint_coordinator import endpoint_coordinator
    endpoint_coordinator.register_endpoint('data_warehouse', lambda: 'warehouse_data')
    
    # Create data bridge between analytics and warehouse
    endpoint_coordinator.share_data_between_endpoints('analytics_dashboard', 'data_warehouse', 'shared_metrics')
    
    @app.route('/api/data-warehouse/dashboard')
    @login_required
    @require_admin
    def get_warehouse_dashboard():
        """Get data warehouse dashboard data with coordination"""
        try:
            from services.data_warehouse_analytics import data_warehouse_analytics
            
            stats = data_warehouse_analytics.get_dashboard_stats()
            buyers = data_warehouse_analytics.get_buyer_stats()
            
            # Get unified data from coordinator
            unified_data = endpoint_coordinator.get_unified_dashboard_data()
            
            # Enhance with coordination data
            enhanced_stats = {
                **stats,
                'unified_metrics': unified_data.get('unified_metrics', {}),
                'coordination_active': True
            }
            
            audit_logger.log_admin_action(
                current_user,
                'view_data_warehouse',
                'data_warehouse',
                {'total_users': stats['total_users'], 'total_value': stats['total_value']}
            )
            
            return jsonify({
                'stats': enhanced_stats,
                'buyers': buyers,
                'timestamp': datetime.utcnow().isoformat(),
                'coordination_status': 'active'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/data-warehouse')
    @login_required
    @require_admin
    def data_warehouse_page():
        """Serve data warehouse popup page"""
        return render_template('data_warehouse_popup.html')
    
    @app.route('/test/data-warehouse/stats')
    def test_data_warehouse_stats():
        """Test endpoint to verify data warehouse without authentication"""
        try:
            from services.data_warehouse_analytics import data_warehouse_analytics
            
            stats = data_warehouse_analytics.get_dashboard_stats()
            buyers = data_warehouse_analytics.get_buyer_stats()
            
            return jsonify({
                'status': 'success',
                'stats': stats,
                'buyers': buyers[:3],  # Just show first 3 buyers
                'test_mode': True
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e),
                'test_mode': True
            }), 500