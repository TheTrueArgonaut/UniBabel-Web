"""
UniBabel Microservices Registry
Single Source of Truth for all microservices
"""

from typing import Dict, List, Any
import logging

class MicroserviceRegistry:
    """Registry for all UniBabel microservices"""
    
    def __init__(self):
        self.services = {}
        self.logger = logging.getLogger(__name__)
        self._register_core_services()
    
    def _register_core_services(self):
        """Register all core microservices"""
        
        # TRANSLATION SERVICE - The main product
        self.register_service(
            name="translation",
            description="Core translation functionality - breaks language barriers",
            endpoints=["/api/translate", "/api/languages", "/api/translation-cache"],
            dependencies=["user_management"]
        )
        
        # USER MANAGEMENT SERVICE - Handle all user operations
        self.register_service(
            name="user_management", 
            description="User accounts, profiles, authentication",
            endpoints=["/api/users", "/api/auth", "/api/profiles"],
            dependencies=[]
        )
        
        # DATA COLLECTION SERVICE - The money maker
        self.register_service(
            name="data_collection",
            description="Data collection and analytics for monetization",
            endpoints=["/api/data-warehouse", "/api/analytics", "/api/insights"],
            dependencies=["user_management"]
        )
        
        # COMMUNICATION SERVICE - Chat and messaging
        self.register_service(
            name="communication",
            description="Real-time messaging and chat functionality", 
            endpoints=["/api/messages", "/api/rooms", "/api/chat"],
            dependencies=["user_management", "translation"]
        )
        
        # ADMIN SERVICE - Admin dashboard and management
        self.register_service(
            name="admin",
            description="Admin dashboard and platform management",
            endpoints=["/admin/*", "/api/admin/*"],
            dependencies=["user_management", "data_collection", "communication"]
        )
        
        # SUBSCRIPTION SERVICE - Premium features and billing
        self.register_service(
            name="subscription",
            description="Premium subscriptions and billing",
            endpoints=["/api/subscriptions", "/api/billing", "/api/premium"],
            dependencies=["user_management"]
        )
    
    def register_service(self, name: str, description: str, endpoints: List[str], dependencies: List[str]):
        """Register a microservice"""
        self.services[name] = {
            'description': description,
            'endpoints': endpoints,
            'dependencies': dependencies,
            'status': 'registered'
        }
        self.logger.info(f"🔧 Registered microservice: {name}")
    
    def get_service(self, name: str) -> Dict[str, Any]:
        """Get service information"""
        return self.services.get(name, {})
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services"""
        return self.services
    
    def check_dependencies(self, service_name: str) -> bool:
        """Check if all dependencies are satisfied"""
        service = self.services.get(service_name)
        if not service:
            return False
        
        for dep in service['dependencies']:
            if dep not in self.services:
                self.logger.warning(f"❌ Missing dependency: {dep} for service {service_name}")
                return False
        
        return True
    
    def get_service_endpoints(self, service_name: str) -> List[str]:
        """Get all endpoints for a service"""
        service = self.services.get(service_name, {})
        return service.get('endpoints', [])
    
    def print_architecture(self):
        """Print the microservices architecture"""
        print("\n🏗️  UniBabel Microservices Architecture:")
        print("=" * 50)
        
        for name, service in self.services.items():
            print(f"\n📦 {name.upper()} SERVICE")
            print(f"   Description: {service['description']}")
            print(f"   Endpoints: {', '.join(service['endpoints'])}")
            if service['dependencies']:
                print(f"   Dependencies: {', '.join(service['dependencies'])}")
            print(f"   Status: {service['status']}")

# Global registry instance
microservice_registry = MicroserviceRegistry()

# Import all services to ensure they register themselves
# Import all services to ensure they register themselves
# Only import what exists and is needed
try:
    from .translation_orchestrator import get_orchestrator
    translation_orchestrator = get_orchestrator()
except ImportError as e:
    print(f"Warning: Could not import translation orchestrator: {e}")
    translation_orchestrator = None

try:
    from .user_profile_service import user_profile_service
except ImportError as e:
    print(f"Warning: Could not import user profile service: {e}")
    user_profile_service = None

try:
    from .chat_service import get_chat_service
    chat_service = get_chat_service()
except ImportError as e:
    print(f"Warning: Could not import chat service: {e}")
    chat_service = None

try:
    from .message_service import get_message_service
    message_service = get_message_service()
except ImportError as e:
    print(f"Warning: Could not import message service: {e}")
    message_service = None

# Export functions for external use
def get_chat_service():
    """Get the chat service instance"""
    return chat_service

def get_message_service():
    """Get the message service instance"""
    return message_service

# Print architecture on startup
microservice_registry.print_architecture()