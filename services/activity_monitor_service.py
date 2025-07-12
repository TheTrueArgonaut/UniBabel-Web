"""
Activity Monitor Service - SRIMI Microservice
Single Responsibility: Monitor system activity and generate alerts
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class ActivityEvent:
    """Single activity event structure"""
    timestamp: str
    event_type: str
    description: str
    user_id: int
    severity: str

@dataclass
class SystemAlert:
    """System alert structure"""
    alert_type: str
    message: str
    timestamp: str
    action: str
    severity: str

class ActivityMonitorService:
    """Micro-service for activity monitoring and alerting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_cache = []
        self.activity_cache = []
        
    def get_recent_activity(self, limit: int = 10) -> List[ActivityEvent]:
        """Get recent system activity"""
        try:
            from models import Message
            
            recent_messages = Message.query.order_by(Message.timestamp.desc()).limit(limit).all()
            
            activities = []
            for msg in recent_messages:
                activity = ActivityEvent(
                    timestamp=msg.timestamp.isoformat(),
                    event_type='message',
                    description=f"User {msg.sender_id} sent message in room {msg.room_id}",
                    user_id=msg.sender_id,
                    severity='info'
                )
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {str(e)}")
            return []
    
    def get_system_alerts(self) -> List[SystemAlert]:
        """Get current system alerts"""
        try:
            alerts = []
            
            # Check for high-value users
            high_value_alert = self._check_high_value_users()
            if high_value_alert:
                alerts.append(high_value_alert)
            
            # Check for blocked users
            blocked_users_alert = self._check_blocked_users()
            if blocked_users_alert:
                alerts.append(blocked_users_alert)
            
            # Check system health
            health_alert = self._check_system_health()
            if health_alert:
                alerts.append(health_alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting system alerts: {str(e)}")
            return []
    
    def _check_high_value_users(self) -> SystemAlert:
        """Check for high-value users that need attention"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            high_value_count = 0
            for profile in data_warehouse.user_profiles.values():
                if profile.total_market_value > 5000:
                    high_value_count += 1
            
            if high_value_count > 0:
                return SystemAlert(
                    alert_type='high_value_users',
                    message=f"{high_value_count} high-value users detected",
                    timestamp=datetime.utcnow().isoformat(),
                    action='Review high-value targets',
                    severity='info'
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking high-value users: {str(e)}")
            return None
    
    def _check_blocked_users(self) -> SystemAlert:
        """Check for unusual blocking patterns"""
        try:
            from services.user_stats_service import user_stats_service
            
            stats = user_stats_service.get_basic_stats()
            
            if stats.total_users > 0 and stats.blocked_users > stats.total_users * 0.1:  # More than 10% blocked
                return SystemAlert(
                    alert_type='high_blocked_users',
                    message=f"High number of blocked users: {stats.blocked_users} ({(stats.blocked_users/stats.total_users)*100:.1f}%)",
                    timestamp=datetime.utcnow().isoformat(),
                    action='Review blocking policies',
                    severity='warning'
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking blocked users: {str(e)}")
            return None
    
    def _check_system_health(self) -> SystemAlert:
        """Check overall system health"""
        try:
            from models import User, Message
            
            # Check if we have users and messages
            user_count = User.query.count()
            message_count = Message.query.count()
            
            if user_count == 0:
                return SystemAlert(
                    alert_type='no_users',
                    message='No users in system',
                    timestamp=datetime.utcnow().isoformat(),
                    action='Check user registration',
                    severity='warning'
                )
            
            if message_count == 0:
                return SystemAlert(
                    alert_type='no_messages',
                    message='No messages in system',
                    timestamp=datetime.utcnow().isoformat(),
                    action='Check messaging functionality',
                    severity='info'
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {str(e)}")
            return SystemAlert(
                alert_type='system_error',
                message=f'System health check failed: {str(e)}',
                timestamp=datetime.utcnow().isoformat(),
                action='Check system logs',
                severity='error'
            )

# Singleton instance
activity_monitor_service = ActivityMonitorService()