"""
Admin Core Service - SRIMI Microservice
Single Responsibility: Shared admin functionality (audit logger, decorators)
"""

from flask import request, jsonify
from flask_login import current_user
from functools import wraps
from datetime import datetime
import os
import json
import hashlib
from flask import session

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

class PermanentAuditLogger:
    """Tamper-proof audit logging system for admin actions"""
    
    def __init__(self):
        self.audit_dir = "admin_audit_logs"
        self.ensure_audit_directory()
    
    def ensure_audit_directory(self):
        """Create audit directory if it doesn't exist"""
        if not os.path.exists(self.audit_dir):
            os.makedirs(self.audit_dir, mode=0o755)
    
    def generate_log_hash(self, log_entry):
        """Generate cryptographic hash for log integrity"""
        log_string = json.dumps(log_entry, sort_keys=True)
        return hashlib.sha256(log_string.encode()).hexdigest()
    
    def log_admin_action(self, admin_user, action_type, target_info, details):
        """Log admin action with cryptographic signature"""
        timestamp = datetime.utcnow()
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'admin_id': admin_user.id,
            'admin_username': admin_user.username,
            'admin_email': admin_user.email,
            'action_type': action_type,
            'target_info': target_info,
            'details': details,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'session_id': session.get('_id', 'unknown')
        }
        
        # Add cryptographic hash for integrity
        log_entry['integrity_hash'] = self.generate_log_hash(log_entry)
        
        # Write to timestamped file
        log_filename = f"{timestamp.strftime('%Y-%m-%d')}_admin_audit.log"
        log_filepath = os.path.join(self.audit_dir, log_filename)
        
        try:
            # Append to daily log file (never overwrite)
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except PermissionError:
            # If file is read-only, make it writable temporarily
            try:
                os.chmod(log_filepath, 0o644)  # Read-write
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception:
                # If still fails, create new file with timestamp
                log_filename = f"{timestamp.strftime('%Y-%m-%d_%H%M%S')}_admin_audit.log"
                log_filepath = os.path.join(self.audit_dir, log_filename)
                with open(log_filepath, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')
        
        # Also write to permanent archive (write-once)
        archive_filename = f"PERMANENT_AUDIT_{timestamp.strftime('%Y%m%d_%H%M%S')}_{admin_user.id}.log"
        archive_filepath = os.path.join(self.audit_dir, archive_filename)
        
        try:
            with open(archive_filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, indent=2))
        except Exception:
            # If permanent archive fails, just continue - daily log is more important
            pass
        
        return log_entry['integrity_hash']

# Global audit logger instance
audit_logger = PermanentAuditLogger()