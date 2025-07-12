"""
Admin Audit Routes - SRIMI Microservice
Single Responsibility: Audit logging endpoints only
"""

from flask import Flask, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
import os
import json

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def register_admin_audit_routes(app: Flask, audit_logger) -> None:
    """Register audit-only routes - under 50 lines"""
    
    @app.route('/api/admin/audit-logs')
    @login_required
    @require_admin
    def admin_audit_logs():
        """View permanent audit logs (read-only)"""
        try:
            audit_logs = []
            
            # Read all audit log files
            if os.path.exists(audit_logger.audit_dir):
                for filename in sorted(os.listdir(audit_logger.audit_dir)):
                    if filename.endswith('.log'):
                        filepath = os.path.join(audit_logger.audit_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip():
                                        try:
                                            log_entry = json.loads(line.strip())
                                            audit_logs.append(log_entry)
                                        except json.JSONDecodeError:
                                            continue
                        except (IOError, OSError):
                            continue
            
            # Sort by timestamp (newest first)
            audit_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Limit to last 500 entries for performance
            audit_logs = audit_logs[:500]
            
            # Log that audit logs were viewed
            audit_logger.log_admin_action(
                current_user, 
                'view_audit_logs', 
                'audit_system', 
                {'logs_count': len(audit_logs)}
            )
            
            return jsonify({
                'audit_logs': audit_logs,
                'total_logs': len(audit_logs),
                'warning': 'These logs are tamper-proof and cannot be modified or deleted'
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/admin/action-definitions')
    @login_required
    @require_admin
    def admin_action_definitions():
        """Get action type definitions for audit logs"""
        try:
            definitions = {
                'user_ban': {
                    'name': 'User Ban',
                    'description': 'Permanently ban a user account',
                    'reversible': True,
                    'data_impact': 'Account blocked, data preserved'
                },
                'user_unban': {
                    'name': 'User Unban',
                    'description': 'Restore a banned user account',
                    'reversible': True,
                    'data_impact': 'Account restored, full access'
                },
                'user_delete': {
                    'name': 'User Delete',
                    'description': 'Permanently delete user account and data',
                    'reversible': False,
                    'data_impact': 'Account and all data permanently destroyed'
                },
                'bulk_delete': {
                    'name': 'Bulk Delete',
                    'description': 'Mass deletion of user accounts',
                    'reversible': False,
                    'data_impact': 'Multiple accounts permanently destroyed'
                },
                'data_export': {
                    'name': 'Data Export',
                    'description': 'Export user data',
                    'reversible': True,
                    'data_impact': 'Data accessed and exported'
                },
                'view_audit_logs': {
                    'name': 'View Audit Logs',
                    'description': 'Access audit log records',
                    'reversible': True,
                    'data_impact': 'Audit logs accessed'
                },
                'toggle_data_collection': {
                    'name': 'Toggle Data Collection',
                    'description': 'Enable/disable data collection for user',
                    'reversible': True,
                    'data_impact': 'Data collection settings modified'
                }
            }
            
            return jsonify(definitions)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500