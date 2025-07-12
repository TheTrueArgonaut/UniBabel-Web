"""
Data Warehouse Service - SRIMI Microservice Registry
Single Responsibility: Coordinate data warehouse micro-components
"""

from .data_warehouse_core import data_warehouse_core, UserDataProfile
from .data_warehouse_buyers import data_warehouse_buyers
from .data_warehouse_analytics import data_warehouse_analytics

class DataWarehouseService:
    """Lightweight coordinator for data warehouse micro-components"""
    
    def __init__(self):
        self.core = data_warehouse_core
        self.buyers = data_warehouse_buyers
        self.analytics = data_warehouse_analytics
    
    def get_user_data_summary(self, user_id: int) -> dict:
        """Get user data summary for backward compatibility"""
        profile = self.core.get_profile(user_id)
        if not profile:
            return None
        
        return {
            'total_market_value': profile.total_market_value,
            'vulnerability_score': profile.vulnerability_score,
            'buyer_interest_score': self._calculate_buyer_interest(profile),
            'data_categories': self._get_data_categories(profile),
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _calculate_buyer_interest(self, profile: UserDataProfile) -> dict:
        """Calculate buyer interest scores"""
        return {
            'government': min(profile.vulnerability_score * 0.8, 100),
            'commercial': min(profile.total_market_value / 50, 100),
            'political': min(profile.vulnerability_score * 0.9, 100)
        }
    
    def _get_data_categories(self, profile: UserDataProfile) -> dict:
        """Get available data categories"""
        return {
            'psychological': bool(profile.psychological_data),
            'financial': bool(profile.financial_data),
            'political': bool(profile.political_data),
            'personal': bool(profile.personal_data),
            'behavioral': bool(profile.behavioral_data),
            'commercial': bool(profile.commercial_data)
        }
    
    @property
    def user_profiles(self):
        """Backward compatibility property"""
        return self.core.user_profiles

# Singleton for backward compatibility
data_warehouse = DataWarehouseService()