"""
Legal Compliance Service - SRIMI Microservice
Single Responsibility: Coordinate legal compliance micro-services
"""

from typing import Dict, Any
import logging

class LegalComplianceService:
    """Lightweight coordinator for legal compliance micro-services"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_chat_logging_notice(self, user_id: int, is_admin_conversation: bool = False, detailed: bool = False) -> Dict[str, Any]:
        """Get chat logging notice using privacy notice service"""
        try:
            from services.privacy_notice_service import privacy_notice_service
            return privacy_notice_service.get_chat_logging_notice(user_id, is_admin_conversation, detailed)
        except Exception as e:
            self.logger.error(f"Error getting chat logging notice: {str(e)}")
            return {'error': str(e)}
    
    def record_user_consent(self, user_id: int, consent_type: str, consent_given: bool,
                           ip_address: str, user_agent: str, consent_version: str = '1.0') -> Dict[str, Any]:
        """Record user consent using consent manager service"""
        try:
            from services.consent_manager_service import consent_manager_service
            return consent_manager_service.record_user_consent(user_id, consent_type, consent_given, ip_address, user_agent, consent_version)
        except Exception as e:
            self.logger.error(f"Error recording user consent: {str(e)}")
            return {'error': str(e)}
    
    def should_show_logging_notice(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Check if logging notice should be shown using privacy notice service"""
        try:
            from services.privacy_notice_service import privacy_notice_service
            return privacy_notice_service.should_show_logging_notice(user_id, room_id)
        except Exception as e:
            self.logger.error(f"Error checking if should show logging notice: {str(e)}")
            return {'should_show': True, 'error': str(e)}
    
    def process_privacy_command(self, user_id: int, command: str, ip_address: str, user_agent: str, is_admin_conversation: bool = False) -> Dict[str, Any]:
        """Process privacy command using privacy command service"""
        try:
            from services.privacy_command_service import privacy_command_service
            return privacy_command_service.process_privacy_command(user_id, command, ip_address, user_agent, is_admin_conversation)
        except Exception as e:
            self.logger.error(f"Error processing privacy command: {str(e)}")
            return {'error': str(e)}
    
    def handle_opt_out_request(self, user_id: int, opt_out_type: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Handle opt-out request using privacy command service"""
        try:
            from services.privacy_command_service import privacy_command_service
            return privacy_command_service._handle_opt_out_request(user_id, opt_out_type, ip_address, user_agent)
        except Exception as e:
            self.logger.error(f"Error handling opt-out request: {str(e)}")
            return {'error': str(e)}
    
    def check_user_opt_out_status(self, user_id: int, opt_out_type: str) -> bool:
        """Check user opt-out status using consent manager service"""
        try:
            from services.consent_manager_service import consent_manager_service
            return consent_manager_service.check_user_opt_out_status(user_id, opt_out_type)
        except Exception as e:
            self.logger.error(f"Error checking user opt-out status: {str(e)}")
            return False
    
    def get_user_privacy_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user privacy settings using consent manager service"""
        try:
            from services.consent_manager_service import consent_manager_service
            return consent_manager_service.get_user_privacy_settings(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user privacy settings: {str(e)}")
            return {'error': str(e)}
    
    def get_admin_chat_disclaimer(self) -> str:
        """Get admin chat disclaimer using privacy notice service"""
        try:
            from services.privacy_notice_service import privacy_notice_service
            return privacy_notice_service.get_admin_chat_disclaimer()
        except Exception as e:
            self.logger.error(f"Error getting admin chat disclaimer: {str(e)}")
            return "Admin conversation notice not available"

# Singleton instance
legal_compliance_service = LegalComplianceService()