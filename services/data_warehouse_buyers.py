"""
Data Warehouse Buyers - SRIMI Microservice
Single Responsibility: Real buyer management only
"""

from typing import Dict, List

class DataWarehouseBuyers:
    """Manage real data buyers and their requirements"""
    
    def __init__(self):
        self.buyers = {}  # Empty - no fake buyers
    
    def get_buyers(self) -> Dict:
        """Get all real buyers (currently none)"""
        return self.buyers
    
    def get_buyer(self, buyer_name: str) -> Dict:
        """Get specific buyer info"""
        return self.buyers.get(buyer_name, {})
    
    def get_total_budget(self) -> float:
        """Get total budget from real buyers"""
        return sum(buyer.get('budget', 0) for buyer in self.buyers.values())
    
    def get_interested_buyers(self, data_types: List[str]) -> List[str]:
        """Get buyers interested in specific data types"""
        interested = []
        for buyer_name, buyer_info in self.buyers.items():
            if any(data_type in buyer_info.get('interests', []) for data_type in data_types):
                interested.append(buyer_name)
        return interested
    
    def add_buyer(self, buyer_name: str, buyer_info: Dict) -> bool:
        """Add a real buyer"""
        if buyer_name and buyer_info:
            self.buyers[buyer_name] = buyer_info
            return True
        return False
    
    def remove_buyer(self, buyer_name: str) -> bool:
        """Remove a buyer"""
        if buyer_name in self.buyers:
            del self.buyers[buyer_name]
            return True
        return False

# Singleton
data_warehouse_buyers = DataWarehouseBuyers()