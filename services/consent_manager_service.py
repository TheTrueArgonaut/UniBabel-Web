"""
Consent Manager Service - SRIMI Microservice
Single Responsibility: Manage user consent records and verification
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os

@dataclass
class ConsentRecord:
    """User consent record structure"""
    user_id: int
    consent_type: str
    consent_given: bool
    timestamp: datetime
    ip_address: str
    user_agent: str
    version: str
    consent_text: str

class ConsentManagerService:
    """Micro-service for consent management only"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.consent_dir = 'legal_consent_records'
        self._ensure_consent_directory()
        
    def _ensure_consent_directory(self):
        """Ensure consent directory exists"""
        if not os.path.exists(self.consent_dir):
            os.makedirs(self.consent_dir)
    
    def record_user_consent(self, user_id: int, consent_type: str, consent_given: bool,
                           ip_address: str, user_agent: str, consent_version: str = '1.0') -> Dict[str, Any]:
        """Record user consent"""
        try:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Get consent text
            consent_text = self._get_consent_text(consent_type, consent_version)
            
            # Create consent record
            consent_record = ConsentRecord(
                user_id=user_id,
                consent_type=consent_type,
                consent_given=consent_given,
                timestamp=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                version=consent_version,
                consent_text=consent_text
            )
            
            # Write to file
            self._write_consent_record(consent_record)
            
            return {
                'success': True,
                'consent_id': f"{user_id}_{consent_type}_{consent_record.timestamp.strftime('%Y%m%d_%H%M%S')}",
                'consent_given': consent_given,
                'timestamp': consent_record.timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error recording user consent: {str(e)}")
            return {'error': str(e)}
    
    def check_user_consent(self, user_id: int, consent_type: str) -> bool:
        """Check if user has given consent"""
        try:
            consent_file = os.path.join(self.consent_dir, f"user_{user_id}_consent.json")
            
            if not os.path.exists(consent_file):
                return False
            
            with open(consent_file, 'r', encoding='utf-8') as f:
                consent_data = json.load(f)
            
            # Check if consent exists and is given
            return consent_data.get(consent_type, {}).get('consent_given', False)
            
        except Exception as e:
            self.logger.error(f"Error checking user consent: {str(e)}")
            return False
    
    def _write_consent_record(self, consent_record: ConsentRecord):
        """Write consent record to file"""
        try:
            # User-specific consent file
            consent_file = os.path.join(self.consent_dir, f"user_{consent_record.user_id}_consent.json")
            
            # Load existing consent data
            consent_data = {}
            if os.path.exists(consent_file):
                with open(consent_file, 'r', encoding='utf-8') as f:
                    consent_data = json.load(f)
            
            # Update consent data
            consent_data[consent_record.consent_type] = {
                'consent_given': consent_record.consent_given,
                'timestamp': consent_record.timestamp.isoformat(),
                'ip_address': consent_record.ip_address,
                'user_agent': consent_record.user_agent,
                'version': consent_record.version,
                'consent_text_hash': hash(consent_record.consent_text)
            }
            
            # Write updated consent data
            with open(consent_file, 'w', encoding='utf-8') as f:
                json.dump(consent_data, f, indent=2)
            
            # Also write to daily audit log
            daily_log = os.path.join(self.consent_dir, f"{consent_record.timestamp.strftime('%Y-%m-%d')}_consent_log.json")
            
            log_entry = {
                'user_id': consent_record.user_id,
                'consent_type': consent_record.consent_type,
                'consent_given': consent_record.consent_given,
                'timestamp': consent_record.timestamp.isoformat(),
                'ip_address': consent_record.ip_address,
                'user_agent': consent_record.user_agent,
                'version': consent_record.version
            }
            
            with open(daily_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
        except Exception as e:
            self.logger.error(f"Error writing consent record: {str(e)}")
            raise
    
    def _get_consent_text(self, consent_type: str, version: str) -> str:
        """Get consent text for specific type and version"""
        consent_texts = {
            'chat_logging': {
                '1.0': '''
By providing consent, you acknowledge and agree that:
1. Your chat messages and communications may be monitored and logged
2. Logs may include message content, timestamps, and metadata
3. This data may be used for safety, security, and legal compliance
4. Data may be retained according to our privacy policy
5. You have rights regarding your personal data as described in our privacy policy
                '''.strip()
            }
        }
        
        return consent_texts.get(consent_type, {}).get(version, 'Consent text not found')
    
    def check_user_opt_out_status(self, user_id: int, opt_out_type: str) -> bool:
        """Check if user has opted out of specific logging type"""
        try:
            consent_file = os.path.join(self.consent_dir, f"user_{user_id}_consent.json")
            
            if not os.path.exists(consent_file):
                return False
            
            with open(consent_file, 'r', encoding='utf-8') as f:
                consent_data = json.load(f)
            
            # Check if user has opted out (consent_given = False for opt-out records)
            opt_out_key = f'opt_out_{opt_out_type}'
            return consent_data.get(opt_out_key, {}).get('consent_given', True) == False
            
        except Exception as e:
            self.logger.error(f"Error checking user opt-out status: {str(e)}")
            return False
    
    def get_user_privacy_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user's privacy settings and consent status"""
        try:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Check various consent types
            has_chat_logging_consent = self.check_user_consent(user_id, 'chat_logging')
            has_opted_out_optional = self.check_user_opt_out_status(user_id, 'optional_logging')
            
            return {
                'success': True,
                'user_id': user_id,
                'privacy_settings': {
                    'chat_logging_consent': has_chat_logging_consent,
                    'optional_logging_opted_out': has_opted_out_optional,
                    'required_logging': True,  # Always true for safety/security
                    'admin_logging': True  # Always true for admin conversations
                },
                'available_actions': {
                    'opt_out_optional': not has_opted_out_optional,
                    'opt_in_optional': has_opted_out_optional,
                    'request_data_copy': True,
                    'request_data_deletion': True
                },
                'contact_info': 'sakelariosall@argonautdigtalventures.com'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user privacy settings: {str(e)}")
            return {'error': str(e)}

# Singleton instance
consent_manager_service = ConsentManagerService()