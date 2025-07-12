"""
User Statistics Service - SRIMI Microservice
Single Responsibility: User statistics aggregation and metrics
"""

from typing import Dict, Any
from models import User, UserType, db
from dataclasses import dataclass

@dataclass
class UserStats:
    """User statistics data structure"""
    total_users: int
    online_users: int
    offline_users: int
    premium_users: int
    blocked_users: int
    adult_users: int
    teen_users: int
    new_users_today: int
    new_users_week: int
    new_users_month: int

class UserStatsService:
    """Micro-service for user statistics"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # 1 minute cache
    
    def get_basic_stats(self) -> UserStats:
        """Get basic user statistics"""
        from datetime import datetime, timedelta
        
        # Basic counts
        total_users = User.query.count()
        online_users = User.query.filter(User.is_online == True).count()
        offline_users = total_users - online_users
        premium_users = User.query.filter(User.is_premium == True).count()
        blocked_users = User.query.filter(User.is_blocked == True).count()
        
        # User type counts
        adult_users = User.query.filter(User.user_type == UserType.ADULT).count()
        teen_users = User.query.filter(User.user_type == UserType.TEEN).count()
        
        # New user counts
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        new_users_today = User.query.filter(User.created_at >= today).count()
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        new_users_month = User.query.filter(User.created_at >= month_ago).count()
        
        return UserStats(
            total_users=total_users,
            online_users=online_users,
            offline_users=offline_users,
            premium_users=premium_users,
            blocked_users=blocked_users,
            adult_users=adult_users,
            teen_users=teen_users,
            new_users_today=new_users_today,
            new_users_week=new_users_week,
            new_users_month=new_users_month
        )
    
    def get_user_distribution(self) -> Dict[str, Any]:
        """Get user type distribution"""
        stats = self.get_basic_stats()
        
        total = stats.total_users
        if total == 0:
            return {"error": "No users in system"}
        
        return {
            "total_users": total,
            "type_distribution": {
                "adults": {
                    "count": stats.adult_users,
                    "percentage": (stats.adult_users / total) * 100
                },
                "teens": {
                    "count": stats.teen_users,
                    "percentage": (stats.teen_users / total) * 100
                }
            },
            "status_distribution": {
                "online": {
                    "count": stats.online_users,
                    "percentage": (stats.online_users / total) * 100
                },
                "offline": {
                    "count": stats.offline_users,
                    "percentage": (stats.offline_users / total) * 100
                },
                "blocked": {
                    "count": stats.blocked_users,
                    "percentage": (stats.blocked_users / total) * 100
                },
                "premium": {
                    "count": stats.premium_users,
                    "percentage": (stats.premium_users / total) * 100
                }
            }
        }
    
    def get_growth_metrics(self) -> Dict[str, Any]:
        """Get user growth metrics"""
        stats = self.get_basic_stats()
        
        # Calculate growth rates
        daily_rate = stats.new_users_today
        weekly_rate = stats.new_users_week / 7 if stats.new_users_week > 0 else 0
        monthly_rate = stats.new_users_month / 30 if stats.new_users_month > 0 else 0
        
        return {
            "new_users": {
                "today": stats.new_users_today,
                "this_week": stats.new_users_week,
                "this_month": stats.new_users_month
            },
            "growth_rates": {
                "daily_average": daily_rate,
                "weekly_average": weekly_rate,
                "monthly_average": monthly_rate
            },
            "retention_indicators": {
                "active_percentage": (stats.online_users / stats.total_users) * 100 if stats.total_users > 0 else 0,
                "premium_conversion": (stats.premium_users / stats.total_users) * 100 if stats.total_users > 0 else 0
            }
        }

# Singleton instance
user_stats_service = UserStatsService()