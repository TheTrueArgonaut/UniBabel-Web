"""
Privacy Notice Service - SRIMI Microservice
Single Responsibility: Generate and manage privacy notices
"""

from typing import Dict, Any
from datetime import datetime
import logging

class PrivacyNoticeService:
    """Micro-service for privacy notices only"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_chat_logging_notice(self, user_id: int, is_admin_conversation: bool = False, detailed: bool = False) -> Dict[str, Any]:
        """Get chat logging notice for user"""
        try:
            from models import User
            from services.consent_manager_service import consent_manager_service
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Check if user has already consented
            has_consented = consent_manager_service.check_user_consent(user_id, 'chat_logging')
            
            # If they want detailed info, show the full notice
            if detailed:
                return self._get_detailed_notice(user_id, is_admin_conversation, has_consented)
            
            # Otherwise show simple notice
            if is_admin_conversation:
                notice = {
                    'notice_type': 'admin_chat_logging_simple',
                    'title': 'Admin Chat Notice',
                    'message': 'This admin conversation will be logged for safety and legal compliance.',
                    'is_simple': True,
                    'actions': [
                        {
                            'action': 'more_info',
                            'label': 'More Information',
                            'description': 'Get detailed information about logging'
                        },
                        {
                            'action': 'continue',
                            'label': 'Continue',
                            'description': 'Continue with logging (required for admin chats)'
                        }
                    ],
                    'consent_required': not has_consented,
                    'consent_type': 'chat_logging',
                    'can_decline': False,
                    'contact_info': 'sakelariosall@argonautdigtalventures.com'
                }
            else:
                notice = {
                    'notice_type': 'general_chat_logging_simple',
                    'title': 'Chat Logging Notice',
                    'message': 'This conversation may be logged for safety and service improvement.',
                    'is_simple': True,
                    'actions': [
                        {
                            'action': 'more_info',
                            'label': 'More Information',
                            'description': 'Get detailed information about logging'
                        },
                        {
                            'action': 'continue',
                            'label': 'Continue',
                            'description': 'Continue with full logging'
                        },
                        {
                            'action': 'decline',
                            'label': 'Minimal Logging',
                            'description': 'Only safety-required logging'
                        }
                    ],
                    'consent_required': not has_consented,
                    'consent_type': 'chat_logging',
                    'can_decline': True,
                    'contact_info': 'sakelariosall@argonautdigtalventures.com'
                }
            
            return {
                'success': True,
                'user_id': user_id,
                'has_consented': has_consented,
                'notice': notice,
                'show_notice': not has_consented or is_admin_conversation,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting chat logging notice: {str(e)}")
            return {'error': str(e)}
    
    def _get_detailed_notice(self, user_id: int, is_admin_conversation: bool, has_consented: bool) -> Dict[str, Any]:
        """Get detailed notice (original full notice)"""
        if is_admin_conversation:
            notice = {
                'notice_type': 'admin_chat_logging_detailed',
                'title': 'Admin Communication Notice - Detailed',
                'message': '''
Hi! Here's the detailed information about this admin conversation.

This chat with an administrator is being logged for:
• Keeping everyone safe and secure
• Meeting legal requirements  
• Helping us improve our service
• Resolving any issues that might come up

What we keep track of:
• Messages and when they were sent
• Basic technical info (like IP addresses)
• User details needed for support

Your rights:
• You can request a copy of your data anytime
• You can ask us to delete your personal data (some legal stuff might need to stay)
• Contact us if you have privacy questions

Data keeping:
• Admin chats are kept for 7 years (legal requirement)
• Everything is stored securely with encryption
• Only authorized people can access the logs

Actions you can take:
• Type "continue" to proceed with the conversation
• Contact us at sakelariosall@argonautdigtalventures.com with questions
                '''.strip(),
                'is_simple': False,
                'actions': [
                    {
                        'action': 'continue',
                        'label': 'Continue',
                        'description': 'Continue with logging (required for admin chats)'
                    }
                ],
                'consent_required': not has_consented,
                'consent_type': 'chat_logging',
                'legal_basis': 'legitimate_interest_safety',
                'retention_period': '7 years',
                'can_decline': False,
                'contact_info': 'sakelariosall@argonautdigtalventures.com'
            }
        else:
            notice = {
                'notice_type': 'general_chat_logging_detailed',
                'title': 'Chat Logging Notice - Detailed',
                'message': '''
Here's the detailed information about chat logging.

Your conversations might be logged for:
• Safety and security (required - we have to do this)
• Legal compliance (required - the law makes us)
• Making the service better (optional - you can opt out)

What might get logged:
• Message content and timing
• How you use the service
• Safety-related stuff

Your choices:
• Accept all logging (gives you the best experience)
• Decline optional logging (safety stuff still happens)
• Talk to us about any privacy concerns

Your rights:
• Get a copy of your data
• Ask us to delete your personal data (safety stuff might need to stay)
• Contact us with privacy questions

Actions you can take:
• Type "continue" for full logging
• Type "decline" for minimal (safety-only) logging
• Email us at sakelariosall@argonautdigtalventures.com with questions
                '''.strip(),
                'is_simple': False,
                'actions': [
                    {
                        'action': 'continue',
                        'label': 'Continue',
                        'description': 'Continue with full logging'
                    },
                    {
                        'action': 'decline',
                        'label': 'Minimal Logging',
                        'description': 'Only safety-required logging'
                    }
                ],
                'consent_required': not has_consented,
                'consent_type': 'chat_logging',
                'legal_basis': 'consent_and_legitimate_interest',
                'retention_period': '2 years',
                'can_decline': True,
                'contact_info': 'sakelariosall@argonautdigtalventures.com'
            }
        
        return {
            'success': True,
            'user_id': user_id,
            'has_consented': has_consented,
            'notice': notice,
            'show_notice': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_admin_chat_disclaimer(self) -> str:
        """Get disclaimer text for admin chats"""
        return '''
**ADMIN CONVERSATION NOTICE**

This conversation with an administrator is being monitored and logged for legal compliance, security, and quality assurance purposes.

• All messages are recorded and stored securely
• Logs may be used for investigations and dispute resolution
• Data is retained for 7 years minimum as required by law
• You have data protection rights - contact sakelariosall@argonautdigtalventures.com

This monitoring is necessary for safety and legal compliance and cannot be disabled.
        '''.strip()
    
    def should_show_logging_notice(self, user_id: int, room_id: int) -> Dict[str, Any]:
        """Check if logging notice should be shown"""
        try:
            from models import Room, RoomMember, User
            from services.consent_manager_service import consent_manager_service
            
            # Check if this is an admin conversation
            is_admin_room = False
            room = Room.query.get(room_id)
            
            if room and room.type == 'direct_message':
                # Check if any member is an admin
                members = RoomMember.query.filter_by(room_id=room_id).all()
                for member in members:
                    user = User.query.get(member.user_id)
                    if user and getattr(user, 'is_data_vampire_admin', False):
                        is_admin_room = True
                        break
            
            # Always show notice for admin rooms, or if user hasn't consented
            has_consented = consent_manager_service.check_user_consent(user_id, 'chat_logging')
            should_show = is_admin_room or not has_consented
            
            return {
                'should_show': should_show,
                'is_admin_room': is_admin_room,
                'has_consented': has_consented,
                'notice_type': 'admin_chat_logging' if is_admin_room else 'general_chat_logging'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking if should show logging notice: {str(e)}")
            return {'should_show': True, 'error': str(e)}  # Default to showing notice if error

# Singleton instance
privacy_notice_service = PrivacyNoticeService()