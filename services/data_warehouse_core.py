"""
Data Warehouse Core - SRIMI Microservice
Single Responsibility: Core data aggregation only
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class UserDataProfile:
    """Complete user data profile aggregated from all harvesters"""
    user_id: int
    psychological_data: Dict
    financial_data: Dict
    political_data: Dict
    personal_data: Dict
    behavioral_data: Dict
    commercial_data: Dict
    total_market_value: float
    vulnerability_score: int
    last_updated: datetime

class DataWarehouseCore:
    """Core data aggregation functionality"""
    
    def __init__(self):
        self.user_profiles = {}  # In-memory cache
        self.logger = logging.getLogger(__name__)
    
    def store_profile(self, profile: UserDataProfile) -> None:
        """Store user profile in warehouse"""
        self.user_profiles[profile.user_id] = profile
        self.logger.info(f"Profile stored for user {profile.user_id}")
    
    def get_profile(self, user_id: int) -> Optional[UserDataProfile]:
        """Get user profile from warehouse"""
        return self.user_profiles.get(user_id)
    
    def get_all_profiles(self) -> Dict[int, UserDataProfile]:
        """Get all user profiles"""
        return self.user_profiles.copy()
    
    def get_total_value(self) -> float:
        """Get total market value of all profiles"""
        return sum(p.total_market_value for p in self.user_profiles.values())
    
    def populate_from_database(self) -> None:
        """Populate warehouse with real user data from the database"""
        try:
            from models import User
            from datetime import datetime
            
            # Get real users from the database
            users = User.query.limit(100).all()
            
            for user in users:
                # Create a real profile based on actual user data
                profile = UserDataProfile(
                    user_id=user.id,
                    psychological_data={},  # Real data would come from user interactions
                    financial_data={},      # Real data would come from user behavior
                    political_data={},      # Real data would come from user content
                    personal_data={
                        'location': user.country or 'Unknown',
                        'age_group': user.user_type.value if user.user_type else 'Unknown',
                        'language': user.preferred_language or 'en'
                    },
                    behavioral_data={},     # Real data would come from usage patterns
                    commercial_data={},     # Real data would come from user activity
                    total_market_value=0.0,    # Real value would be calculated from actual data
                    vulnerability_score=0,     # Real score would be calculated from behavior
                    last_updated=datetime.utcnow()
                )
                
                self.store_profile(profile)
                
            self.logger.info(f"Populated warehouse with {len(users)} real user profiles")
            
        except Exception as e:
            self.logger.error(f"Failed to populate warehouse: {e}")
    
    def ensure_populated(self) -> None:
        """Ensure warehouse has data, populate if empty"""
        if not self.user_profiles:
            self.populate_from_database()
    
# Singleton
data_warehouse_core = DataWarehouseCore()