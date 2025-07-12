"""
User Enrichment Service - SRIMI Microservice
Single Responsibility: Enriching user profiles with data warehouse data
"""

from typing import Dict, List, Optional, Any
from .user_profile_service import UserProfileData
from dataclasses import dataclass

@dataclass
class EnrichedUserProfile:
    """Enriched user profile with data warehouse information"""
    user_id: int
    username: str
    email: str
    display_name: Optional[str]
    user_type: str
    is_online: bool
    is_blocked: bool
    is_premium: bool
    last_seen: Optional[str]
    created_at: Optional[str]
    block_reason: Optional[str]
    market_value: float
    vulnerability_score: float
    data_warehouse_status: str
    enrichment_timestamp: str

class UserEnrichmentService:
    """Micro-service for enriching user profiles with data warehouse data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 120  # 2 minutes cache
    
    def enrich_user_profile(self, profile: UserProfileData) -> EnrichedUserProfile:
        """Enrich a single user profile with data warehouse information"""
        from datetime import datetime
        
        # Get data warehouse information
        market_value, vulnerability_score, dw_status = self._get_data_warehouse_info(profile.user_id)
        
        return EnrichedUserProfile(
            user_id=profile.user_id,
            username=profile.username,
            email=profile.email,
            display_name=profile.display_name,
            user_type=profile.user_type,
            is_online=profile.is_online,
            is_blocked=profile.is_blocked,
            is_premium=profile.is_premium,
            last_seen=profile.last_seen.isoformat() if profile.last_seen else None,
            created_at=profile.created_at.isoformat() if profile.created_at else None,
            block_reason=profile.block_reason,
            market_value=market_value,
            vulnerability_score=vulnerability_score,
            data_warehouse_status=dw_status,
            enrichment_timestamp=datetime.utcnow().isoformat()
        )
    
    def enrich_user_profiles_batch(self, profiles: List[UserProfileData]) -> List[EnrichedUserProfile]:
        """Enrich multiple user profiles"""
        enriched_profiles = []
        
        for profile in profiles:
            enriched_profile = self.enrich_user_profile(profile)
            enriched_profiles.append(enriched_profile)
        
        return enriched_profiles
    
    def _get_data_warehouse_info(self, user_id: int) -> tuple[float, float, str]:
        """Get data warehouse information for a user"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            if user_id in data_warehouse.user_profiles:
                profile = data_warehouse.user_profiles[user_id]
                return (
                    profile.total_market_value,
                    profile.vulnerability_score,
                    "profiled"
                )
            else:
                return (0.0, 0.0, "not_profiled")
        
        except Exception as e:
            return (0.0, 0.0, f"error: {str(e)}")
    
    def get_enriched_profiles_as_dict(self, profiles: List[EnrichedUserProfile]) -> Dict[str, Any]:
        """Convert enriched profiles to dictionary format for API response"""
        users_data = {}
        
        for profile in profiles:
            users_data[str(profile.user_id)] = {
                'username': profile.username,
                'email': profile.email,
                'user_type': profile.user_type,
                'is_online': profile.is_online,
                'is_blocked': profile.is_blocked,
                'is_premium': profile.is_premium,
                'last_seen': profile.last_seen,
                'created_at': profile.created_at,
                'block_reason': profile.block_reason,
                'market_value': profile.market_value,
                'vulnerability_score': profile.vulnerability_score,
                'data_warehouse_status': profile.data_warehouse_status,
                'enrichment_timestamp': profile.enrichment_timestamp
            }
        
        return users_data
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics related to data warehouse"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            total_profiles = len(data_warehouse.user_profiles)
            total_value = sum(profile.total_market_value for profile in data_warehouse.user_profiles.values())
            avg_value = total_value / max(total_profiles, 1)
            
            return {
                'active_harvesters': 0,  # Simplified
                'total_data_points': total_profiles,
                'average_user_value': avg_value,
                'total_market_value': total_value
            }
        
        except Exception as e:
            return {
                'active_harvesters': 0,
                'total_data_points': 0,
                'average_user_value': 0.0,
                'total_market_value': 0.0,
                'error': str(e)
            }

# Singleton instance
user_enrichment_service = UserEnrichmentService()