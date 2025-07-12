"""
Admin Interaction Logger Service - SRIMI Microservice
Single Responsibility: Log all admin-user interactions for compliance
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os
import hashlib

@dataclass
class AdminInteractionLog:
    """Admin interaction log entry structure"""
    log_id: str
    timestamp: datetime
    admin_user_id: int
    admin_username: str
    target_user_id: int
    target_username: str
    interaction_type: str
    action: str
    content: Optional[str]
    metadata: Dict[str, Any]
    ip_address: str
    user_agent: str
    integrity_hash: str

class AdminInteractionLogger:
    """Micro-service for logging admin-user interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_dir = 'admin_interaction_logs'
        self._ensure_log_directory()
        
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log_message_interaction(self, admin_user_id: int, target_user_id: int, 
                               content: str, message_type: str, 
                               ip_address: str, user_agent: str) -> str:
        """Log admin messaging interaction"""
        try:
            from models import User
            
            # Get user info
            admin_user = User.query.get(admin_user_id)
            target_user = User.query.get(target_user_id)
            
            if not admin_user or not target_user:
                raise ValueError("Admin or target user not found")
            
            # Create log entry
            log_entry = self._create_log_entry(
                admin_user_id=admin_user_id,
                admin_username=admin_user.username,
                target_user_id=target_user_id,
                target_username=target_user.username,
                interaction_type='messaging',
                action=f'send_{message_type}',
                content=content,
                metadata={
                    'message_type': message_type,
                    'content_length': len(content),
                    'content_hash': hashlib.sha256(content.encode()).hexdigest()[:16]
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Write to log file
            self._write_log_entry(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Error logging message interaction: {str(e)}")
            raise
    
    def log_admin_action(self, admin_user_id: int, target_user_id: int,
                        action: str, details: Dict[str, Any],
                        ip_address: str, user_agent: str) -> str:
        """Log general admin action on user"""
        try:
            from models import User
            
            # Get user info
            admin_user = User.query.get(admin_user_id)
            target_user = User.query.get(target_user_id)
            
            if not admin_user or not target_user:
                raise ValueError("Admin or target user not found")
            
            # Create log entry
            log_entry = self._create_log_entry(
                admin_user_id=admin_user_id,
                admin_username=admin_user.username,
                target_user_id=target_user_id,
                target_username=target_user.username,
                interaction_type='admin_action',
                action=action,
                content=None,
                metadata=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Write to log file
            self._write_log_entry(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Error logging admin action: {str(e)}")
            raise
    
    def log_room_access(self, admin_user_id: int, room_id: int, action: str,
                       ip_address: str, user_agent: str) -> str:
        """Log admin room access"""
        try:
            from models import User, Room
            
            # Get user and room info
            admin_user = User.query.get(admin_user_id)
            room = Room.query.get(room_id)
            
            if not admin_user or not room:
                raise ValueError("Admin user or room not found")
            
            # Create log entry
            log_entry = self._create_log_entry(
                admin_user_id=admin_user_id,
                admin_username=admin_user.username,
                target_user_id=0,  # No specific target user for room access
                target_username='room_access',
                interaction_type='room_access',
                action=action,
                content=None,
                metadata={
                    'room_id': room_id,
                    'room_name': room.name,
                    'room_type': room.type,
                    'room_owner_id': room.owner_id
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Write to log file
            self._write_log_entry(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Error logging room access: {str(e)}")
            raise
    
    def log_bulk_action(self, admin_user_id: int, action: str, 
                       affected_users: List[int], details: Dict[str, Any],
                       ip_address: str, user_agent: str) -> str:
        """Log bulk admin actions"""
        try:
            from models import User
            
            # Get admin user info
            admin_user = User.query.get(admin_user_id)
            if not admin_user:
                raise ValueError("Admin user not found")
            
            # Create log entry
            log_entry = self._create_log_entry(
                admin_user_id=admin_user_id,
                admin_username=admin_user.username,
                target_user_id=0,  # Multiple targets
                target_username='bulk_action',
                interaction_type='bulk_action',
                action=action,
                content=None,
                metadata={
                    'affected_users': affected_users,
                    'affected_count': len(affected_users),
                    'action_details': details
                },
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Write to log file
            self._write_log_entry(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Error logging bulk action: {str(e)}")
            raise
    
    def _create_log_entry(self, admin_user_id: int, admin_username: str,
                         target_user_id: int, target_username: str,
                         interaction_type: str, action: str,
                         content: Optional[str], metadata: Dict[str, Any],
                         ip_address: str, user_agent: str) -> AdminInteractionLog:
        """Create a log entry"""
        timestamp = datetime.utcnow()
        log_id = f"AIL_{timestamp.strftime('%Y%m%d_%H%M%S')}_{admin_user_id}_{target_user_id}_{hash(action) % 10000:04d}"
        
        # Create integrity hash
        integrity_data = f"{log_id}_{timestamp.isoformat()}_{admin_user_id}_{target_user_id}_{action}"
        integrity_hash = hashlib.sha256(integrity_data.encode()).hexdigest()
        
        return AdminInteractionLog(
            log_id=log_id,
            timestamp=timestamp,
            admin_user_id=admin_user_id,
            admin_username=admin_username,
            target_user_id=target_user_id,
            target_username=target_username,
            interaction_type=interaction_type,
            action=action,
            content=content,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            integrity_hash=integrity_hash
        )
    
    def _write_log_entry(self, log_entry: AdminInteractionLog):
        """Write log entry to file"""
        try:
            # Daily log file
            log_filename = f"{log_entry.timestamp.strftime('%Y-%m-%d')}_admin_interactions.log"
            log_filepath = os.path.join(self.log_dir, log_filename)
            
            # Create log data
            log_data = {
                'log_id': log_entry.log_id,
                'timestamp': log_entry.timestamp.isoformat(),
                'admin_user_id': log_entry.admin_user_id,
                'admin_username': log_entry.admin_username,
                'target_user_id': log_entry.target_user_id,
                'target_username': log_entry.target_username,
                'interaction_type': log_entry.interaction_type,
                'action': log_entry.action,
                'content_hash': hashlib.sha256(log_entry.content.encode()).hexdigest()[:16] if log_entry.content else None,
                'content_length': len(log_entry.content) if log_entry.content else 0,
                'metadata': log_entry.metadata,
                'ip_address': log_entry.ip_address,
                'user_agent': log_entry.user_agent,
                'integrity_hash': log_entry.integrity_hash
            }
            
            # Append to daily log file
            with open(log_filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data) + '\n')
            
            # Also create individual permanent log file
            permanent_filename = f"PERMANENT_INTERACTION_{log_entry.log_id}.log"
            permanent_filepath = os.path.join(self.log_dir, permanent_filename)
            
            # Include full content in permanent log (if not too large)
            permanent_data = log_data.copy()
            if log_entry.content and len(log_entry.content) < 2000:  # Only store full content if reasonable size
                permanent_data['full_content'] = log_entry.content
            
            with open(permanent_filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(permanent_data, indent=2))
            
            # Make permanent file read-only
            os.chmod(permanent_filepath, 0o444)
            
        except Exception as e:
            self.logger.error(f"Error writing log entry: {str(e)}")
            raise
    
    def get_interaction_logs(self, admin_user_id: Optional[int] = None,
                           target_user_id: Optional[int] = None,
                           interaction_type: Optional[str] = None,
                           date_from: Optional[datetime] = None,
                           date_to: Optional[datetime] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """Get interaction logs with filters"""
        try:
            logs = []
            
            # Get all log files in date range
            log_files = []
            for filename in os.listdir(self.log_dir):
                if filename.endswith('_admin_interactions.log'):
                    log_files.append(filename)
            
            # Sort by date
            log_files.sort()
            
            # Read log files
            for log_file in log_files:
                log_filepath = os.path.join(self.log_dir, log_file)
                
                with open(log_filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # Apply filters
                            if admin_user_id and log_entry.get('admin_user_id') != admin_user_id:
                                continue
                            
                            if target_user_id and log_entry.get('target_user_id') != target_user_id:
                                continue
                            
                            if interaction_type and log_entry.get('interaction_type') != interaction_type:
                                continue
                            
                            # Date filtering
                            log_timestamp = datetime.fromisoformat(log_entry['timestamp'])
                            if date_from and log_timestamp < date_from:
                                continue
                            
                            if date_to and log_timestamp > date_to:
                                continue
                            
                            logs.append(log_entry)
                            
                            if len(logs) >= limit:
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                if len(logs) >= limit:
                    break
            
            # Sort by timestamp (most recent first)
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting interaction logs: {str(e)}")
            return []
    
    def get_user_interaction_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of all admin interactions for a user"""
        try:
            # Get logs where user was target
            target_logs = self.get_interaction_logs(target_user_id=user_id, limit=1000)
            
            # Get logs where user was admin (if they are admin)
            admin_logs = self.get_interaction_logs(admin_user_id=user_id, limit=1000)
            
            # Count interactions by type
            interaction_counts = {}
            for log in target_logs + admin_logs:
                interaction_type = log.get('interaction_type', 'unknown')
                interaction_counts[interaction_type] = interaction_counts.get(interaction_type, 0) + 1
            
            return {
                'user_id': user_id,
                'total_interactions': len(target_logs) + len(admin_logs),
                'as_target': len(target_logs),
                'as_admin': len(admin_logs),
                'interaction_counts': interaction_counts,
                'most_recent_interaction': target_logs[0]['timestamp'] if target_logs else None,
                'first_interaction': target_logs[-1]['timestamp'] if target_logs else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user interaction summary: {str(e)}")
            return {'error': str(e)}

# Singleton instance
admin_interaction_logger = AdminInteractionLogger()