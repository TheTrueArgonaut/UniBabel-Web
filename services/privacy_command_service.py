"""
Privacy Command Service - SRIMI Microservice
Single Responsibility: Process user privacy commands
"""

from typing import Dict, Any
from datetime import datetime
import logging

class PrivacyCommandService:
    """Micro-service for processing privacy commands only"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def process_privacy_command(self, user_id: int, command: str, ip_address: str, user_agent: str, is_admin_conversation: bool = False) -> Dict[str, Any]:
        """Process privacy-related commands from users"""
        try:
            from services.consent_manager_service import consent_manager_service
            
            command_upper = command.upper().strip()
            
            # Handle simple responses
            if command_upper in ['MORE INFO', 'MORE INFORMATION']:
                return {
                    'success': True,
                    'action': 'show_detailed_notice',
                    'message': 'Here\'s the detailed information about logging.'
                }
            
            elif command_upper == 'CONTINUE':
                # User consents to logging
                result = consent_manager_service.record_user_consent(user_id, 'chat_logging', True, ip_address, user_agent)
                result['action'] = 'continue_with_logging'
                result['message'] = 'Thanks! You can now continue chatting with full logging enabled.'
                return result
            
            elif command_upper == 'DECLINE':
                # Check if this is an admin conversation
                if is_admin_conversation:
                    return self._generate_admin_decline_warning()
                else:
                    # Regular chat decline - just opt out of optional logging
                    result = self._handle_opt_out_request(user_id, 'optional_logging', ip_address, user_agent)
                    result['action'] = 'minimal_logging'
                    result['message'] = 'Thanks! You\'ll get minimal logging (safety-only). You can continue chatting.'
                    return result
            
            # Handle admin decline warning responses
            elif command_upper == 'ACCEPT ADMIN LOGGING':
                # User decides to allow admin logging after seeing warning
                result = consent_manager_service.record_user_consent(user_id, 'admin_chat_logging', True, ip_address, user_agent)
                result['action'] = 'continue_with_admin_logging'
                result['message'] = 'Thanks! Admin conversations will be logged. You can now continue chatting.'
                return result
            
            elif command_upper == 'DECLINE ANYWAY':
                # User still wants to decline after seeing warning
                result = self._handle_admin_logging_decline(user_id, ip_address, user_agent)
                return result
            
            elif command_upper == 'CANCEL':
                return {
                    'success': True,
                    'action': 'cancel_privacy_action',
                    'message': 'No changes made. You can continue the conversation.'
                }
            
            # Handle detailed commands
            elif command_upper == 'DECLINE OPTIONAL LOGGING':
                return self._handle_opt_out_request(user_id, 'optional_logging', ip_address, user_agent)
            
            elif command_upper == 'ACCEPT OPTIONAL LOGGING':
                # Re-consent to optional logging
                return consent_manager_service.record_user_consent(user_id, 'optional_logging', True, ip_address, user_agent)
            
            elif command_upper == 'PRIVACY SETTINGS':
                return consent_manager_service.get_user_privacy_settings(user_id)
            
            elif command_upper == 'REQUEST DATA COPY':
                return {
                    'success': True,
                    'message': 'Data copy request received. Please contact sakelariosall@argonautdigtalventures.com with your request.',
                    'contact_info': 'sakelariosall@argonautdigtalventures.com'
                }
            
            elif command_upper == 'REQUEST DATA DELETION':
                return {
                    'success': True,
                    'message': 'Data deletion request received. Please contact sakelariosall@argonautdigtalventures.com with your request. Note: Some data may be retained for legal and safety requirements.',
                    'contact_info': 'sakelariosall@argonautdigtalventures.com'
                }
            
            else:
                return {
                    'success': False,
                    'error': 'Unknown privacy command',
                    'available_commands': [
                        'more info - Get detailed logging information',
                        'continue - Accept logging and continue',
                        'decline - Use minimal logging only',
                        'decline optional logging - Opt out of optional logging',
                        'accept optional logging - Opt in to optional logging',
                        'privacy settings - View your privacy settings',
                        'request data copy - Request a copy of your data',
                        'request data deletion - Request deletion of your data'
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Error processing privacy command: {str(e)}")
            return {'error': str(e)}
    
    def _generate_admin_decline_warning(self) -> Dict[str, Any]:
        """Generate warning for admin chat decline"""
        return {
            'success': True,
            'action': 'show_admin_decline_warning',
            'message': 'Important: Declining admin chat logging may result in account actions.',
            'warning': {
                'title': 'Admin Chat Logging Required',
                'message': '''
Heads up! If you decline logging for admin conversations, we may need to take account actions without your input, including:

• Account suspension or restrictions
• Content removal without prior notice
• Limited access to support services
• Automatic enforcement of community guidelines

This is because we can't properly investigate issues or provide support without conversation records.

Your options:
• Type "accept admin logging" to allow admin chat logging
• Type "decline anyway" to proceed without logging (may result in account limitations)
• Type "cancel" to go back to the chat
                '''.strip(),
                'actions': [
                    {
                        'action': 'accept_admin_logging',
                        'label': 'Accept Admin Logging',
                        'description': 'Allow logging for admin conversations'
                    },
                    {
                        'action': 'decline_anyway',
                        'label': 'Decline Anyway',
                        'description': 'Proceed without logging (may limit account)'
                    },
                    {
                        'action': 'cancel',
                        'label': 'Cancel',
                        'description': 'Go back to the conversation'
                    }
                ]
            }
        }
    
    def _handle_admin_logging_decline(self, user_id: int, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Handle when user declines admin logging after seeing warning"""
        try:
            from models import User, db
            from services.consent_manager_service import consent_manager_service, ConsentRecord
            
            # Record the decline
            consent_record = ConsentRecord(
                user_id=user_id,
                consent_type='admin_chat_logging_declined',
                consent_given=False,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                version='1.0',
                consent_text='User declined admin chat logging after seeing warning about account actions'
            )
            
            # Write to file using consent manager
            result = consent_manager_service.record_user_consent(user_id, 'admin_chat_logging_declined', False, ip_address, user_agent)
            
            # Get user and mark account as having limited support
            user = User.query.get(user_id)
            if user:
                # Add a flag to indicate limited support due to logging decline
                setattr(user, 'admin_logging_declined', True)
                setattr(user, 'admin_logging_declined_date', datetime.utcnow())
                db.session.commit()
            
            return {
                'success': True,
                'action': 'admin_logging_declined',
                'user_id': user_id,
                'message': 'You have declined admin chat logging. Your account may have limited support options.',
                'warning': 'Future admin actions may be taken without your input due to lack of conversation records.',
                'restrictions': [
                    'Limited customer support',
                    'Automatic enforcement of policies',
                    'Account actions without prior notice',
                    'Reduced dispute resolution options'
                ],
                'note': 'You can change this setting anytime by contacting sakelariosall@argonautdigtalventures.com',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling admin logging decline: {str(e)}")
            return {'error': str(e)}
    
    def _handle_opt_out_request(self, user_id: int, opt_out_type: str, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Handle user opt-out request"""
        try:
            from models import User
            from services.consent_manager_service import consent_manager_service, ConsentRecord
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Record the opt-out as a consent record
            result = consent_manager_service.record_user_consent(user_id, f'opt_out_{opt_out_type}', False, ip_address, user_agent)
            
            result.update({
                'opt_out_type': opt_out_type,
                'user_id': user_id,
                'message': f'You have successfully opted out of {opt_out_type} logging.',
                'note': 'Safety and security logging will continue as required by law.'
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error handling opt-out request: {str(e)}")
            return {'error': str(e)}

# Singleton instance
privacy_command_service = PrivacyCommandService()