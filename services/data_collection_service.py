"""
Data Collection Service - Core Business Logic
Handles all data collection decisions and tracking
"""

from datetime import datetime
from models.user_models import User
from models import db
import json
import logging

logger = logging.getLogger(__name__)

class DataCollectionService:
    """
    Centralized data collection service
    Implements the core business model: Free users = data collection ON
    """
    
    @staticmethod
    def should_collect_data(user_id):
        """
        Check if data should be collected for a user
        This is the core business logic check used throughout the app
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            return user.should_collect_data()
        except Exception as e:
            logger.error(f"Error checking data collection status for user {user_id}: {e}")
            return False
    
    @staticmethod
    def collect_translation_data(user_id, source_text, target_text, source_lang, target_lang):
        """
        Collect translation data if allowed
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.can_collect_data_type('translation_history'):
                return False
            
            # Increment data collection counter
            user.increment_data_collection('translation_history')
            
            # Here you would store the actual translation data
            # For now, we just increment the counter
            logger.info(f"Collected translation data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting translation data for user {user_id}: {e}")
            return False
    
    @staticmethod
    def collect_chat_data(user_id, message_content, room_id=None, recipient_id=None):
        """
        Collect chat message data if allowed
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.can_collect_data_type('chat_logs'):
                return False
            
            # Increment data collection counter
            user.increment_data_collection('chat_logs')
            
            # Here you would store the actual chat data
            # For now, we just increment the counter
            logger.info(f"Collected chat data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting chat data for user {user_id}: {e}")
            return False
    
    @staticmethod
    def collect_usage_analytics(user_id, action, page=None, details=None):
        """
        Collect usage analytics data if allowed
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.can_collect_data_type('usage_analytics'):
                return False
            
            # Increment data collection counter
            user.increment_data_collection('usage_analytics')
            
            # Here you would store the actual analytics data
            # For now, we just increment the counter
            logger.info(f"Collected usage analytics for user {user_id}: {action}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting usage analytics for user {user_id}: {e}")
            return False
    
    @staticmethod
    def collect_location_data(user_id, ip_address, country=None, city=None):
        """
        Collect location data if allowed
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.can_collect_data_type('location_data'):
                return False
            
            # Increment data collection counter
            user.increment_data_collection('location_data')
            
            # Here you would store the actual location data
            # For now, we just increment the counter
            logger.info(f"Collected location data for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting location data for user {user_id}: {e}")
            return False
    
    @staticmethod
    def collect_device_info(user_id, user_agent, device_info=None):
        """
        Collect device information if allowed
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.can_collect_data_type('device_info'):
                return False
            
            # Increment data collection counter
            user.increment_data_collection('device_info')
            
            # Here you would store the actual device info
            # For now, we just increment the counter
            logger.info(f"Collected device info for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting device info for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_data_summary(user_id):
        """
        Get summary of data collection for a user
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            return {
                'user_id': user_id,
                'username': user.username,
                'data_collection_enabled': user.should_collect_data(),
                'subscription_tier': user.subscription_tier,
                'market_value': user.market_value,
                'data_points_collected': user.data_points_collected,
                'last_data_collection': user.last_data_collection.isoformat() if user.last_data_collection else None,
                'privacy_settings': {
                    'collect_translation_history': user.collect_translation_history,
                    'collect_chat_logs': user.collect_chat_logs,
                    'collect_usage_analytics': user.collect_usage_analytics,
                    'collect_location_data': user.collect_location_data,
                    'collect_device_info': user.collect_device_info,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary for user {user_id}: {e}")
            return None
    
    @staticmethod
    def process_stripe_webhook(event_type, customer_id, subscription_id=None, subscription_status=None):
        """
        Process Stripe webhook events to update user subscription status
        This automatically enables/disables data collection based on payment status
        """
        try:
            # Find user by Stripe customer ID
            user = User.query.filter_by(stripe_customer_id=customer_id).first()
            if not user:
                logger.warning(f"No user found for Stripe customer {customer_id}")
                return False
            
            if event_type == 'customer.subscription.created':
                # User started premium subscription
                user.upgrade_to_premium(
                    tier='premium_monthly',  # or determine from subscription data
                    stripe_subscription_id=subscription_id
                )
                logger.info(f"User {user.id} upgraded to premium via Stripe")
                
            elif event_type == 'customer.subscription.deleted':
                # User cancelled premium subscription
                user.downgrade_to_free(reason='subscription_cancelled')
                logger.info(f"User {user.id} downgraded to free via Stripe")
                
            elif event_type == 'invoice.payment_failed':
                # Payment failed - could downgrade after grace period
                user.subscription_status = 'past_due'
                user.subscription_updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"User {user.id} payment failed, marked as past due")
                
            elif event_type == 'invoice.payment_succeeded':
                # Payment succeeded - ensure subscription is active
                user.subscription_status = 'active'
                user.subscription_updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"User {user.id} payment succeeded, subscription active")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing Stripe webhook {event_type} for customer {customer_id}: {e}")
            return False
    
    @staticmethod
    def generate_privacy_report(user_id):
        """
        Generate a privacy report for a user (GDPR compliance)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            report = {
                'user_info': {
                    'user_id': user_id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                },
                'subscription_info': user.get_subscription_info(),
                'data_collection_summary': {
                    'data_collection_enabled': user.should_collect_data(),
                    'data_points_collected': user.data_points_collected,
                    'market_value': user.market_value,
                    'last_data_collection': user.last_data_collection.isoformat() if user.last_data_collection else None,
                },
                'privacy_settings': {
                    'collect_translation_history': user.collect_translation_history,
                    'collect_chat_logs': user.collect_chat_logs,
                    'collect_usage_analytics': user.collect_usage_analytics,
                    'collect_location_data': user.collect_location_data,
                    'collect_device_info': user.collect_device_info,
                },
                'report_generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy report for user {user_id}: {e}")
            return None