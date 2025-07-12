"""
Data Warehouse Analytics - SRIMI Microservice
Single Responsibility: Warehouse analytics and reporting only
"""

from datetime import datetime
from typing import Dict, List
from .data_warehouse_core import data_warehouse_core
from .data_warehouse_buyers import data_warehouse_buyers

class DataWarehouseAnalytics:
    """Analytics for data warehouse"""
    
    def __init__(self):
        self.core = data_warehouse_core
        self.buyers = data_warehouse_buyers
    
    def get_dashboard_stats(self) -> Dict:
        """Get key stats for dashboard"""
        # Ensure warehouse has data
        self.core.ensure_populated()
        
        profiles = self.core.get_all_profiles()
        
        if not profiles:
            return {
                'total_users': 0,
                'total_value': 0,
                'avg_value_per_user': 0,
                'high_value_targets': 0,
                'vulnerable_targets': 0,
                'potential_revenue': 0
            }
        
        total_value = sum(p.total_market_value for p in profiles.values())
        high_value_count = sum(1 for p in profiles.values() if p.total_market_value > 1000)
        vulnerable_count = sum(1 for p in profiles.values() if p.vulnerability_score > 70)
        
        return {
            'total_users': len(profiles),
            'total_value': total_value,
            'avg_value_per_user': total_value / len(profiles),
            'high_value_targets': high_value_count,
            'vulnerable_targets': vulnerable_count,
            'potential_revenue': self.buyers.get_total_budget()
        }
    
    def get_buyer_stats(self) -> List[Dict]:
        """Get buyer statistics"""
        buyers = self.buyers.get_buyers()
        buyer_stats = []
        
        for buyer_name, buyer_info in buyers.items():
            interested_profiles = 0
            profiles = self.core.get_all_profiles()
            
            # Count profiles that match buyer interests
            for profile in profiles.values():
                if self._profile_matches_buyer(profile, buyer_info):
                    interested_profiles += 1
            
            buyer_stats.append({
                'name': buyer_name.replace('_', ' ').title(),
                'budget': buyer_info['budget'],
                'interested_profiles': interested_profiles,
                'data_types': buyer_info['interests']
            })
        
        return sorted(buyer_stats, key=lambda x: x['budget'], reverse=True)
    
    def _profile_matches_buyer(self, profile, buyer_info) -> bool:
        """Check if profile matches buyer interests"""
        # Simple matching based on data availability
        return any(
            getattr(profile, f"{interest.replace('_data', '')}_data", {})
            for interest in buyer_info['interests']
        )

# Singleton
data_warehouse_analytics = DataWarehouseAnalytics()