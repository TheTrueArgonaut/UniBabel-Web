"""
Language Analytics Service - SRIMI Microservice
Single Responsibility: Language distribution metrics only
"""

from typing import Dict, Any, List
import logging

class LanguageAnalyticsService:
    """Tiny service for language metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_language_distribution(self) -> Dict[str, Any]:
        """Get language distribution"""
        try:
            from models import User, Message, db
            
            # User language preferences with fallback
            user_languages = []
            try:
                user_langs_query = db.session.query(
                    User.preferred_language,
                    db.func.count(User.id).label('count')
                ).group_by(User.preferred_language).all()
                
                user_languages = sorted(
                    [{'lang': lang or 'EN', 'count': count} for lang, count in user_langs_query],
                    key=lambda x: x['count'], reverse=True
                )[:10]
            except Exception as e:
                self.logger.warning(f"User language query failed: {e}")
                # Provide sample data
                user_languages = [
                    {'lang': 'EN', 'count': 0},
                    {'lang': 'ES', 'count': 0},
                    {'lang': 'FR', 'count': 0}
                ]
            
            # Message source languages with fallback
            message_languages = []
            try:
                message_langs_query = db.session.query(
                    Message.original_language,
                    db.func.count(Message.id).label('count')
                ).group_by(Message.original_language).all()
                
                message_languages = sorted(
                    [{'lang': lang or 'AUTO', 'count': count} for lang, count in message_langs_query],
                    key=lambda x: x['count'], reverse=True
                )[:10]
            except Exception as e:
                self.logger.warning(f"Message language query failed: {e}")
                # Provide sample data
                message_languages = [
                    {'lang': 'AUTO', 'count': 0},
                    {'lang': 'EN', 'count': 0},
                    {'lang': 'ES', 'count': 0}
                ]
            
            # Count unique languages
            total_user_languages = len([l for l in user_languages if l['lang'] and l['count'] > 0])
            total_message_languages = len([l for l in message_languages if l['lang'] and l['count'] > 0])
            
            return {
                'user_languages': user_languages,
                'message_languages': message_languages,
                'total_user_languages': total_user_languages,
                'total_message_languages': total_message_languages
            }
            
        except Exception as e:
            self.logger.error(f"Language analytics error: {e}")
            # Return safe defaults
            return {
                'user_languages': [
                    {'lang': 'EN', 'count': 0},
                    {'lang': 'ES', 'count': 0},
                    {'lang': 'FR', 'count': 0}
                ],
                'message_languages': [
                    {'lang': 'AUTO', 'count': 0},
                    {'lang': 'EN', 'count': 0}
                ],
                'total_user_languages': 0,
                'total_message_languages': 0
            }

# Singleton
language_analytics_service = LanguageAnalyticsService()