"""
Registration Service
Handles user account creation and validation
"""

import logging
from datetime import datetime, date
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash
from models import db, User, UserType
from sqlalchemy.exc import IntegrityError


class RegistrationService:
    """Handle user registration with validation and security"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("🔐 Registration Service initialized")
    
    def create_user_account(self, user_data: Dict[str, Any], skip_email_verification: bool = False) -> Dict[str, Any]:
        """
        Create a new user account with validation
        
        Args:
            user_data: User registration data
            skip_email_verification: Skip email verification (for parental consent)
            
        Returns:
            Result with success/failure and user details
        """
        
        try:
            # Validate required fields
            validation_result = self._validate_user_data(user_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors'],
                    'status': 400
                }
            
            # Check for existing users
            existing_user = self._check_existing_user(user_data['username'], user_data['email'])
            if existing_user:
                return existing_user
            
            # Determine user type based on age
            user_type = self._determine_user_type(user_data)
            
            # Create user object
            new_user = User(
                username=user_data['username'],
                email=user_data['email'].lower(),
                password_hash=generate_password_hash(user_data['password']),
                display_name=user_data['display_name'],
                preferred_language=user_data['preferred_language'],
                birth_date=self._parse_birth_date(user_data['birth_date']),
                user_type=user_type,
                is_email_verified=skip_email_verification,
                is_age_verified=user_data.get('is_age_verified', False),
                created_at=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            
            # Add parental consent data if provided
            if user_data.get('parent_email'):
                new_user.parent_email = user_data['parent_email']
                new_user.parent_name = user_data.get('parent_name')
                new_user.parent_relationship = user_data.get('parent_relationship')
                new_user.parental_consent_verified = user_data.get('parental_consent_verified', False)
                new_user.parental_consent_date = user_data.get('parental_consent_date')
            
            # Special settings for children
            if user_type == UserType.CHILD:
                new_user.data_collection_blocked = True
                new_user.requires_parent_permission = True
            
            # Set default preferences for all users
            import json
            default_preferences = {
                'language': {
                    'autoTranslate': True,  # Default to auto-translate ON
                    'preferredLanguage': user_data['preferred_language']
                },
                'accessibility': {
                    'highContrast': False,
                    'largeText': False,
                    'reducedMotion': False
                },
                'privacy': {
                    'profileVisibility': 'public',
                    'showOnlineStatus': True
                },
                'notifications': {
                    'messageNotifications': True,
                    'roomNotifications': True
                },
                'created_at': datetime.utcnow().isoformat()
            }
            
            new_user.bio = json.dumps(default_preferences)
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            self.logger.info(f"✅ User account created: {new_user.username} (ID: {new_user.id}, Type: {user_type.value})")
            
            return {
                'success': True,
                'user_id': new_user.id,
                'username': new_user.username,
                'user_type': user_type.value,
                'requires_email_verification': not skip_email_verification,
                'requires_age_verification': not new_user.is_age_verified,
                'status': 201
            }
            
        except IntegrityError as e:
            db.session.rollback()
            self.logger.error(f"❌ Database integrity error: {str(e)}")
            
            if 'username' in str(e):
                return {
                    'success': False,
                    'errors': ['Username already taken'],
                    'status': 409
                }
            elif 'email' in str(e):
                return {
                    'success': False,
                    'errors': ['Email already registered'],
                    'status': 409
                }
            else:
                return {
                    'success': False,
                    'errors': ['Registration failed - duplicate data'],
                    'status': 409
                }
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"❌ Registration failed: {str(e)}")
            return {
                'success': False,
                'errors': [f'Registration failed: {str(e)}'],
                'status': 500
            }
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user registration data"""
        
        errors = []
        
        # Required fields
        required_fields = ['username', 'email', 'password', 'display_name', 'birth_date', 'preferred_language']
        for field in required_fields:
            if not user_data.get(field):
                errors.append(f'{field} is required')
        
        # Username validation
        username = user_data.get('username', '')
        if len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if len(username) > 20:
            errors.append('Username must be less than 20 characters')
        if not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, hyphens, and underscores')
        
        # Email validation
        email = user_data.get('email', '')
        if '@' not in email or '.' not in email:
            errors.append('Valid email address required')
        
        # Password validation
        password = user_data.get('password', '')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        
        # Display name validation
        display_name = user_data.get('display_name', '')
        if len(display_name) < 1:
            errors.append('Display name is required')
        if len(display_name) > 30:
            errors.append('Display name must be less than 30 characters')
        
        # Birth date validation
        try:
            birth_date = self._parse_birth_date(user_data.get('birth_date'))
            if birth_date > date.today():
                errors.append('Birth date cannot be in the future')
            
            # Age validation
            age = self._calculate_age(birth_date)
            if age < 13:
                errors.append('Must be at least 13 years old to register (COPPA compliance)')
            if age > 120:
                errors.append('Please enter a valid birth date')
                
        except (ValueError, TypeError):
            errors.append('Valid birth date required (YYYY-MM-DD)')
        
        # Language validation
        valid_languages = ['ar', 'bg', 'cs', 'da', 'de', 'el', 'en', 'en-gb', 'en-us', 'es', 'es-419', 'et', 'fi', 'fr', 'he', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'nb', 'nl', 'pl', 'pt', 'pt-br', 'pt-pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'vi', 'zh', 'zh-hans', 'zh-hant']
        if user_data.get('preferred_language', '').lower() not in valid_languages:
            errors.append('Invalid language selection')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _check_existing_user(self, username: str, email: str) -> Optional[Dict[str, Any]]:
        """Check if username or email already exists"""
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            return {
                'success': False,
                'errors': ['Username already taken'],
                'status': 409
            }
        
        existing_email = User.query.filter_by(email=email.lower()).first()
        if existing_email:
            return {
                'success': False,
                'errors': ['Email already registered'],
                'status': 409
            }
        
        return None
    
    def _determine_user_type(self, user_data: Dict[str, Any]) -> UserType:
        """Determine user type based on age"""
        
        birth_date = self._parse_birth_date(user_data['birth_date'])
        age = self._calculate_age(birth_date)
        
        if age < 13:
            return UserType.CHILD
        elif age < 18:
            return UserType.TEEN
        else:
            return UserType.ADULT
    
    def _parse_birth_date(self, birth_date_str: Any) -> date:
        """Parse birth date from various formats"""
        
        if isinstance(birth_date_str, date):
            return birth_date_str
        elif isinstance(birth_date_str, str):
            try:
                return datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(birth_date_str, '%m/%d/%Y').date()
                except ValueError:
                    raise ValueError('Invalid birth date format')
        else:
            raise ValueError('Birth date must be a string or date object')
    
    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date"""
        
        today = date.today()
        age = today.year - birth_date.year
        
        # Adjust if birthday hasn't occurred this year
        if today < birth_date.replace(year=today.year):
            age -= 1
            
        return age
    
    def check_username_availability(self, username: str) -> Dict[str, Any]:
        """Check if username is available"""
        
        if len(username) < 3:
            return {
                'available': False,
                'reason': 'Username must be at least 3 characters'
            }
        
        existing = User.query.filter_by(username=username).first()
        return {
            'available': existing is None,
            'reason': 'Username already taken' if existing else None
        }
    
    def check_email_availability(self, email: str) -> Dict[str, Any]:
        """Check if email is available"""
        
        if '@' not in email:
            return {
                'available': False,
                'reason': 'Invalid email format'
            }
        
        existing = User.query.filter_by(email=email.lower()).first()
        return {
            'available': existing is None,
            'reason': 'Email already registered' if existing else None
        }


# Global instance
_registration_service = RegistrationService()


def get_registration_service() -> RegistrationService:
    """Get the global registration service instance"""
    return _registration_service