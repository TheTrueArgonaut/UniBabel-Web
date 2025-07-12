"""
Search Orchestrator Service - SRIMI Microservice
Single Responsibility: Coordinate search across multiple services
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class SearchResult:
    """Search result data structure"""
    result_type: str
    data: Dict[str, Any]
    relevance_score: float
    source_service: str

class SearchOrchestratorService:
    """Micro-service for coordinating search across services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.search_cache = {}
        self.cache_ttl = 120  # 2 minutes
        
    def search_all_services(self, search_term: str, max_results: int = 50) -> Dict[str, Any]:
        """Search across all available services"""
        try:
            results = {}
            
            # Search user profiles
            user_results = self._search_user_profiles(search_term, max_results // 2)
            if user_results:
                results['users'] = user_results
            
            # Search data warehouse
            warehouse_results = self._search_data_warehouse(search_term, max_results // 2)
            if warehouse_results:
                results['data_warehouse'] = warehouse_results
            
            # Search messages (if needed)
            # message_results = self._search_messages(search_term, max_results // 4)
            # if message_results:
            #     results['messages'] = message_results
            
            total_results = sum(len(r) if isinstance(r, dict) else 0 for r in results.values())
            
            return {
                'search_term': search_term,
                'total_results': total_results,
                'results_by_service': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error searching all services: {str(e)}")
            raise
    
    def search_users_only(self, search_term: str, max_results: int = 25) -> Dict[str, Any]:
        """Search only user-related services"""
        try:
            results = self._search_user_profiles(search_term, max_results)
            
            return {
                'search_term': search_term,
                'search_type': 'users_only',
                'total_results': len(results),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error searching users only: {str(e)}")
            raise
    
    def search_data_warehouse_only(self, search_term: str, max_results: int = 25) -> Dict[str, Any]:
        """Search only data warehouse"""
        try:
            results = self._search_data_warehouse(search_term, max_results)
            
            return {
                'search_term': search_term,
                'search_type': 'data_warehouse_only',
                'total_results': len(results),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error searching data warehouse only: {str(e)}")
            raise
    
    def _search_user_profiles(self, search_term: str, max_results: int) -> Dict[str, Any]:
        """Search user profiles service"""
        try:
            from services.user_profile_service import user_profile_service
            from services.user_enrichment_service import user_enrichment_service
            
            # Search user profiles
            profiles = user_profile_service.search_users(search_term, limit=max_results)
            
            # Enrich with data warehouse info
            enriched_profiles = user_enrichment_service.enrich_user_profiles_batch(profiles)
            
            # Convert to response format
            return user_enrichment_service.get_enriched_profiles_as_dict(enriched_profiles)
            
        except Exception as e:
            self.logger.error(f"Error searching user profiles: {str(e)}")
            return {}
    
    def _search_data_warehouse(self, search_term: str, max_results: int) -> Dict[str, Any]:
        """Search data warehouse service"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            results = {}
            count = 0
            
            for user_id, profile in data_warehouse.user_profiles.items():
                if count >= max_results:
                    break
                    
                if (search_term.lower() in str(user_id).lower() or 
                    search_term.lower() in f"user_{user_id}".lower()):
                    
                    results[user_id] = {
                        'user_id': user_id,
                        'total_market_value': profile.total_market_value,
                        'vulnerability_score': profile.vulnerability_score,
                        'last_updated': profile.last_updated.isoformat()
                    }
                    count += 1
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching data warehouse: {str(e)}")
            return {}
    
    def get_search_suggestions(self, partial_term: str, max_suggestions: int = 5) -> List[str]:
        """Get search suggestions based on partial term"""
        try:
            suggestions = []
            
            # Get user-based suggestions
            user_suggestions = self._get_user_suggestions(partial_term, max_suggestions // 2)
            suggestions.extend(user_suggestions)
            
            # Get data warehouse suggestions
            dw_suggestions = self._get_data_warehouse_suggestions(partial_term, max_suggestions // 2)
            suggestions.extend(dw_suggestions)
            
            # Remove duplicates and limit
            unique_suggestions = list(set(suggestions))[:max_suggestions]
            
            return unique_suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting search suggestions: {str(e)}")
            return []
    
    def _get_user_suggestions(self, partial_term: str, max_suggestions: int) -> List[str]:
        """Get user-based search suggestions"""
        try:
            from models import User
            
            suggestions = []
            
            # Search usernames
            users = User.query.filter(
                User.username.ilike(f'%{partial_term}%')
            ).limit(max_suggestions).all()
            
            for user in users:
                suggestions.append(user.username)
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting user suggestions: {str(e)}")
            return []
    
    def _get_data_warehouse_suggestions(self, partial_term: str, max_suggestions: int) -> List[str]:
        """Get data warehouse search suggestions"""
        try:
            from services.data_warehouse_service import data_warehouse
            
            suggestions = []
            count = 0
            
            for user_id in data_warehouse.user_profiles.keys():
                if count >= max_suggestions:
                    break
                    
                if partial_term.lower() in str(user_id).lower():
                    suggestions.append(f"user_{user_id}")
                    count += 1
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting data warehouse suggestions: {str(e)}")
            return []

# Singleton instance
search_orchestrator_service = SearchOrchestratorService()