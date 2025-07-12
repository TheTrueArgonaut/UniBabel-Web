"""
Privacy Premium Service - The greedy business model
Let users pay to not be data vampire victims
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from models import db, User
from models.subscription_models import (
    PrivacyPremiumSubscription, 
    SubscriptionTier, 
    DataExploitationMetrics
)

class PrivacyPremiumService:
    """Handle privacy subscriptions - where users pay to not be exploited"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("💰 Privacy Premium Service initialized - Let the greed begin!")
    
    def create_subscription(self, user_id: int, tier: SubscriptionTier = SubscriptionTier.PRIVACY_PREMIUM) -> Dict[str, Any]:
        """Create a new privacy subscription"""
        try:
            # Check if user already has a subscription
            existing = PrivacyPremiumSubscription.query.filter_by(user_id=user_id).first()
            if existing and existing.is_active:
                return {
                    'success': False,
                    'error': 'User already has an active privacy subscription',
                    'current_tier': existing.tier.value
                }
            
            # Create new subscription
            subscription = PrivacyPremiumSubscription.create_privacy_subscription(user_id, tier)
            
            # Initialize exploitation metrics
            metrics = DataExploitationMetrics.query.filter_by(user_id=user_id).first()
            if not metrics:
                metrics = DataExploitationMetrics(user_id=user_id)
                db.session.add(metrics)
            
            # Calculate what we're losing by not exploiting them
            lost_revenue = subscription.calculate_lost_data_revenue()
            
            pricing = {
                SubscriptionTier.FREE: 0.0,
                SubscriptionTier.PRIVACY_PREMIUM: 7.99,  # $7.99/month to not be exploited
                SubscriptionTier.ENTERPRISE: 19.99
            }
            
            self.logger.info(f"💰 New privacy subscription created: User {user_id} paying ${pricing[tier]}/month (losing ${lost_revenue}/month in data sales)")
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'monthly_price': pricing[tier],
                'tier': subscription.tier.value,
                'protection_level': {
                    'data_collection_blocked': subscription.data_collection_blocked,
                    'behavioral_analysis_blocked': subscription.behavioral_analysis_blocked,
                    'emotional_profiling_blocked': subscription.emotional_profiling_blocked,
                    'manipulation_campaigns_blocked': subscription.manipulation_campaigns_blocked,
                    'data_sales_excluded': subscription.data_sales_excluded
                },
                'lost_data_revenue': lost_revenue,
                'net_profit_projection': pricing[tier] - lost_revenue
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create privacy subscription: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_payment(self, user_id: int, amount: float, payment_id: str) -> Dict[str, Any]:
        """Process a privacy subscription payment"""
        try:
            subscription = PrivacyPremiumSubscription.query.filter_by(user_id=user_id, is_active=True).first()
            if not subscription:
                return {
                    'success': False,
                    'error': 'No active privacy subscription found'
                }
            
            # Process payment
            subscription.process_payment(amount, payment_id)
            
            # Update exploitation metrics
            metrics = DataExploitationMetrics.query.filter_by(user_id=user_id).first()
            if metrics:
                metrics.update_privacy_revenue(amount)
            
            self.logger.info(f"💰 Payment processed: User {user_id} paid ${amount} (Total: ${subscription.total_paid}, Net profit: ${subscription.net_profit})")
            
            return {
                'success': True,
                'payment_processed': amount,
                'total_paid': subscription.total_paid,
                'net_profit': subscription.net_profit,
                'next_payment_date': subscription.next_payment_date.isoformat(),
                'protection_active': subscription.is_protected_from_data_harvesting()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Payment processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, user_id: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel privacy subscription (back to being exploited)"""
        try:
            subscription = PrivacyPremiumSubscription.query.filter_by(user_id=user_id, is_active=True).first()
            if not subscription:
                return {
                    'success': False,
                    'error': 'No active privacy subscription found'
                }
            
            # Calculate total revenue extracted
            total_revenue = subscription.total_paid
            
            # Cancel subscription
            subscription.cancel_subscription(reason)
            
            # Update user's data collection status
            user = User.query.get(user_id)
            if user:
                user.data_collection_blocked = False
                db.session.commit()
            
            self.logger.info(f"💰 Subscription cancelled: User {user_id} is now back to being exploited (Total extracted: ${total_revenue})")
            
            return {
                'success': True,
                'message': 'Privacy subscription cancelled - you are now subject to data collection and monetization',
                'total_revenue_extracted': total_revenue,
                'back_to_exploitation': True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Subscription cancellation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription_status(self, user_id: int) -> Dict[str, Any]:
        """Get user's privacy subscription status"""
        try:
            subscription = PrivacyPremiumSubscription.query.filter_by(user_id=user_id).first()
            
            if not subscription:
                # Calculate how much we're making from exploiting them
                metrics = DataExploitationMetrics.query.filter_by(user_id=user_id).first()
                exploitation_revenue = 0.0
                if metrics:
                    exploitation_revenue = (metrics.data_sales_revenue + 
                                          metrics.manipulation_revenue + 
                                          metrics.behavioral_targeting_revenue)
                
                return {
                    'has_subscription': False,
                    'tier': SubscriptionTier.FREE.value,
                    'being_exploited': True,
                    'data_collection_active': True,
                    'current_exploitation_revenue': exploitation_revenue,
                    'privacy_cost': 7.99,  # How much they'd need to pay to escape
                    'message': 'You are currently being monetized through data collection'
                }
            
            return {
                'has_subscription': True,
                'tier': subscription.tier.value,
                'is_active': subscription.is_active,
                'monthly_price': subscription.monthly_price,
                'total_paid': subscription.total_paid,
                'net_profit': subscription.net_profit,
                'next_payment_date': subscription.next_payment_date.isoformat() if subscription.next_payment_date else None,
                'protection_level': {
                    'data_collection_blocked': subscription.data_collection_blocked,
                    'behavioral_analysis_blocked': subscription.behavioral_analysis_blocked,
                    'emotional_profiling_blocked': subscription.emotional_profiling_blocked,
                    'manipulation_campaigns_blocked': subscription.manipulation_campaigns_blocked,
                    'data_sales_excluded': subscription.data_sales_excluded
                },
                'lost_data_revenue': subscription.lost_data_revenue,
                'being_exploited': not subscription.is_protected_from_data_harvesting()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get subscription status: {str(e)}")
            return {
                'has_subscription': False,
                'error': str(e)
            }
    
    def calculate_personalized_pricing(self, user_id: int) -> Dict[str, Any]:
        """Calculate personalized pricing based on user's data value"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Base price
            base_price = 7.99
            
            # Calculate their data value
            if hasattr(user, 'data_profile') and user.data_profile:
                profile = user.data_profile
                data_value = profile.get_market_value()
                
                # If their data is worth more, charge them more to protect it
                if data_value > 100:
                    base_price *= 1.5  # 50% markup for high-value targets
                elif data_value > 200:
                    base_price *= 2.0  # 100% markup for premium targets
            
            # Check exploitation metrics
            metrics = DataExploitationMetrics.query.filter_by(user_id=user_id).first()
            if metrics:
                # If we're already making good money exploiting them, price higher
                current_exploitation = (metrics.data_sales_revenue + 
                                      metrics.manipulation_revenue + 
                                      metrics.behavioral_targeting_revenue)
                
                if current_exploitation > 50:
                    base_price = max(base_price, current_exploitation * 1.2)  # 20% markup over current exploitation
            
            return {
                'base_price': 7.99,
                'personalized_price': round(base_price, 2),
                'data_value': data_value if 'data_value' in locals() else 50,
                'current_exploitation_revenue': current_exploitation if 'current_exploitation' in locals() else 0,
                'pricing_reason': 'Based on your data value and current exploitation potential'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate personalized pricing: {str(e)}")
            return {
                'base_price': 7.99,
                'personalized_price': 7.99,
                'error': str(e)
            }
    
    def get_business_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get business metrics for the privacy premium model"""
        try:
            # Privacy subscription revenue
            privacy_stats = PrivacyPremiumSubscription.get_revenue_stats(days)
            
            # Data exploitation revenue
            exploitation_stats = DataExploitationMetrics.get_global_exploitation_stats(days)
            
            # Combined metrics
            total_revenue = privacy_stats['subscription_revenue'] + exploitation_stats['exploitation_revenue']
            
            return {
                'total_revenue': total_revenue,
                'privacy_subscription_revenue': privacy_stats['subscription_revenue'],
                'data_exploitation_revenue': exploitation_stats['exploitation_revenue'],
                'privacy_subscribers': privacy_stats['total_subscribers'],
                'exploited_users': exploitation_stats['exploited_users'],
                'revenue_per_privacy_user': exploitation_stats['revenue_per_privacy_user'],
                'revenue_per_exploited_user': exploitation_stats['revenue_per_exploited_user'],
                'most_profitable_strategy': exploitation_stats['most_profitable_strategy'],
                'net_profit_margin': privacy_stats['profit_margin'],
                'lost_data_revenue': privacy_stats['lost_data_revenue'],
                'business_model_effectiveness': 'Highly effective' if total_revenue > 1000 else 'Needs optimization'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get business metrics: {str(e)}")
            return {
                'error': str(e)
            }
    
    def should_offer_privacy_deal(self, user_id: int) -> Dict[str, Any]:
        """Determine if we should offer a privacy deal or keep exploiting"""
        try:
            metrics = DataExploitationMetrics.query.filter_by(user_id=user_id).first()
            if not metrics:
                return {
                    'offer_privacy': True,
                    'reason': 'No exploitation data available'
                }
            
            # Calculate optimal strategy
            optimal_strategy = metrics.calculate_optimal_strategy()
            
            return {
                'offer_privacy': optimal_strategy == 'sell_privacy',
                'current_strategy': optimal_strategy,
                'willingness_to_pay': metrics.willingness_to_pay,
                'exploitation_vulnerability': metrics.exploitation_vulnerability,
                'recommendation': f"Current strategy: {optimal_strategy}. Revenue potential: ${metrics.total_revenue}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to determine privacy strategy: {str(e)}")
            return {
                'offer_privacy': True,
                'error': str(e)
            }


# Global instance
_privacy_premium_service = PrivacyPremiumService()


def get_privacy_premium_service() -> PrivacyPremiumService:
    """Get the global privacy premium service instance"""
    return _privacy_premium_service