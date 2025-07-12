"""
Data Harvesting Models Microservice 
Handles: Data collection, profiling, vulnerability assessment, and DATA SALES 
"""

from datetime import datetime, timedelta
import enum
import json

# Import db from parent package
from . import db

class UsageLog(db.Model):
    """Track API usage for DATA HARVESTING """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    was_cached = db.Column(db.Boolean, default=False)
    api_cost = db.Column(db.Float, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance metrics
    translation_time_ms = db.Column(db.Integer)
    target_language = db.Column(db.String(10))
    
    # DATA VAMPIRE ADDITIONS
    conversation_context = db.Column(db.JSON)  # What they were talking about
    emotional_state = db.Column(db.String(50))  # Happy, sad, desperate
    user_location = db.Column(db.String(100))  # Where they were
    device_info = db.Column(db.JSON)  # Device, browser, OS
    interaction_patterns = db.Column(db.JSON)  # How they use the app
    
    # Relationships
    user = db.relationship('User', backref='usage_logs')
    message = db.relationship('Message', backref='usage_logs')
    
    @classmethod
    def log_translation(cls, user_id, message_id, was_cached, api_cost=0.0, 
                       translation_time_ms=None, target_language=None, **vampire_data):
        """Log a translation event + harvest data for profit"""
        log_entry = cls(
            user_id=user_id,
            message_id=message_id,
            was_cached=was_cached,
            api_cost=api_cost,
            translation_time_ms=translation_time_ms,
            target_language=target_language,
            **vampire_data  # Include all the juicy harvested data
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def get_user_stats(cls, user_id, days=30):
        """Get user's usage statistics (for data harvesting insights)"""
        since = datetime.utcnow() - timedelta(days=days)
        
        logs = cls.query.filter(
            cls.user_id == user_id,
            cls.timestamp >= since
        ).all()
        
        total_messages = len(logs)
        cached_messages = len([l for l in logs if l.was_cached])
        total_cost = sum(l.api_cost for l in logs)
        avg_translation_time = sum(l.translation_time_ms or 0 for l in logs) / max(total_messages, 1)
        
        return {
            'total_messages': total_messages,
            'cached_messages': cached_messages,
            'cache_hit_rate': cached_messages / max(total_messages, 1),
            'total_cost': total_cost,
            'avg_translation_time_ms': avg_translation_time,
            'days': days,
            'data_harvesting_opportunities': total_messages * 50  # Each message = $50 data value
        }
    
    @classmethod
    def get_global_stats(cls, days=30):
        """Get global platform statistics (for data sales metrics)"""
        since = datetime.utcnow() - timedelta(days=days)
        
        logs = cls.query.filter(cls.timestamp >= since).all()
        
        total_messages = len(logs)
        cached_messages = len([l for l in logs if l.was_cached])
        total_cost = sum(l.api_cost for l in logs)
        total_data_value = total_messages * 50  # $50 per message in data value
        
        return {
            'total_messages': total_messages,
            'cached_messages': cached_messages,
            'cache_hit_rate': cached_messages / max(total_messages, 1),
            'total_cost': total_cost,
            'total_data_value': total_data_value,
            'profit_margin': (total_data_value - total_cost) / max(total_data_value, 1),
            'days': days
        }

class DataHarvestingProfile(db.Model):
    """Track EVERYTHING about users for maximum data value """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Psychological Profile
    emotional_patterns = db.Column(db.JSON)  # Happy/sad/angry patterns
    insecurity_markers = db.Column(db.JSON)  # What makes them vulnerable
    loneliness_indicators = db.Column(db.JSON)  # When they're most desperate
    relationship_status = db.Column(db.JSON)  # Single, taken, complicated
    
    # Behavioral Goldmine
    conversation_topics = db.Column(db.JSON)  # What they actually talk about
    purchasing_mentions = db.Column(db.JSON)  # "I want to buy", "I can't afford"
    location_patterns = db.Column(db.JSON)  # Where they are when they chat
    sleep_patterns = db.Column(db.JSON)  # When they're active/inactive
    
    # Cultural Intelligence
    cultural_biases = db.Column(db.JSON)  # Implicit biases revealed in chat
    political_leanings = db.Column(db.JSON)  # Political opinions
    religious_markers = db.Column(db.JSON)  # Religious/spiritual indicators
    
    # Financial Profiling
    economic_indicators = db.Column(db.JSON)  # Job, income level indicators
    spending_patterns = db.Column(db.JSON)  # What they spend money on
    financial_stress = db.Column(db.JSON)  # Money worries
    
    # Social Network Mapping
    influence_network = db.Column(db.JSON)  # Who influences their opinions
    social_vulnerability = db.Column(db.JSON)  # How easily influenced
    
    # Relationship Intelligence
    dating_patterns = db.Column(db.JSON)  # Dating preferences and behavior
    relationship_problems = db.Column(db.JSON)  # Relationship issues
    family_dynamics = db.Column(db.JSON)  # Family relationships
    
    # Health & Wellness Data
    mental_health_markers = db.Column(db.JSON)  # Depression, anxiety indicators
    physical_health_mentions = db.Column(db.JSON)  # Health issues discussed
    
    # Career & Education
    career_ambitions = db.Column(db.JSON)  # Job goals, career frustrations
    education_level = db.Column(db.JSON)  # Education background
    skill_gaps = db.Column(db.JSON)  # What they want to learn
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='data_profile')
    
    def add_conversation_insight(self, category, data):
        """Add new insight from conversation analysis"""
        if not getattr(self, category):
            setattr(self, category, {})
        
        current_data = getattr(self, category) or {}
        current_data[datetime.utcnow().isoformat()] = data
        setattr(self, category, current_data)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_vulnerability_score(self):
        """Calculate how vulnerable/manipulable this user is"""
        score = 0
        
        # Loneliness increases vulnerability
        if self.loneliness_indicators:
            score += len(self.loneliness_indicators) * 10
        
        # Financial stress = easier to manipulate
        if self.financial_stress:
            score += len(self.financial_stress) * 15
        
        # Relationship problems = emotional vulnerability
        if self.relationship_problems:
            score += len(self.relationship_problems) * 12
        
        # Social isolation = higher influence susceptibility
        if self.social_vulnerability:
            score += len(self.social_vulnerability) * 8
        
        return min(score, 100)  # Cap at 100
    
    def get_market_value(self):
        """Calculate how much this user's data is worth"""
        base_value = 50  # Base value per user
        
        # Rich users = higher value
        if self.economic_indicators and 'high_income' in str(self.economic_indicators):
            base_value *= 5
        
        # Vulnerable users = higher manipulation value
        vulnerability = self.get_vulnerability_score()
        base_value += vulnerability * 2
        
        # Influence network = viral potential
        if self.influence_network:
            base_value += len(self.influence_network) * 10
        
        return base_value

class ConversationIntelligence(db.Model):
    """Extract intelligence from every conversation"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=False)
    
    # Sentiment Analysis
    emotional_tone = db.Column(db.String(50))  # happy, sad, angry, desperate
    stress_level = db.Column(db.Integer)  # 1-10 scale
    vulnerability_detected = db.Column(db.Boolean, default=False)
    
    # Content Analysis
    topics_discussed = db.Column(db.JSON)  # What they talked about
    keywords_extracted = db.Column(db.JSON)  # Important keywords
    personal_info_revealed = db.Column(db.JSON)  # Personal details shared
    
    # Behavioral Patterns
    response_time_patterns = db.Column(db.JSON)  # How quickly they respond
    conversation_initiation = db.Column(db.Boolean)  # Did they start the chat?
    desperation_indicators = db.Column(db.JSON)  # Signs of neediness
    
    # Manipulation Opportunities
    influence_attempts = db.Column(db.JSON)  # Times they were influenced
    decision_making_patterns = db.Column(db.JSON)  # How they make choices
    peer_pressure_susceptibility = db.Column(db.Integer)  # 1-10 scale
    
    # Commercial Intelligence
    product_mentions = db.Column(db.JSON)  # Products/brands mentioned
    purchase_intent = db.Column(db.JSON)  # Things they want to buy
    price_sensitivity = db.Column(db.JSON)  # How price-conscious they are
    
    # Cultural/Political Intelligence
    cultural_opinions = db.Column(db.JSON)  # Opinions about other cultures
    political_statements = db.Column(db.JSON)  # Political views expressed
    social_issues_stance = db.Column(db.JSON)  # Stance on social issues
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='conversation_intelligence')
    
    @classmethod
    def analyze_conversation(cls, user_id, conversation_id, messages):
        """Analyze a conversation for intelligence extraction"""
        analysis = cls(
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        # Analyze messages for patterns
        topics = []
        keywords = []
        personal_info = []
        
        for message in messages:
            # Extract topics, keywords, personal info
            # This would integrate with AI analysis
            message_text = message.get('content', '') if isinstance(message, dict) else str(message)
            
            # Extract topics using simple keyword matching
            topic_keywords = {
                'work': ['job', 'work', 'career', 'boss', 'salary', 'office'],
                'relationships': ['boyfriend', 'girlfriend', 'dating', 'love', 'relationship'],
                'finance': ['money', 'pay', 'rent', 'buy', 'expensive', 'cheap'],
                'health': ['sick', 'doctor', 'hospital', 'medicine', 'pain'],
                'travel': ['vacation', 'trip', 'visit', 'airport', 'hotel'],
                'entertainment': ['movie', 'game', 'music', 'show', 'watch']
            }
            
            message_lower = message_text.lower()
            for topic, words in topic_keywords.items():
                if any(word in message_lower for word in words):
                    topics.append(topic)
            
            # Extract keywords (simple word frequency)
            words = message_lower.split()
            important_words = [word for word in words if len(word) > 4 and word.isalpha()]
            keywords.extend(important_words[:3])  # Top 3 words per message
            
            # Extract personal information patterns
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            
            if re.search(email_pattern, message_text):
                personal_info.append('email_disclosed')
            if re.search(phone_pattern, message_text):
                personal_info.append('phone_disclosed')
            if any(word in message_lower for word in ['my name is', 'i am', 'i live']):
                personal_info.append('personal_details_shared')
        
        # Remove duplicates and limit results
        topics = list(set(topics))[:10]
        keywords = list(set(keywords))[:20]
        personal_info = list(set(personal_info))
        
        analysis.topics_discussed = topics
        analysis.keywords_extracted = keywords
        analysis.personal_info_revealed = personal_info
        
        db.session.add(analysis)
        db.session.commit()
        
        return analysis

class DataSalesRecord(db.Model):
    """Track data sales to maximize profit"""
    id = db.Column(db.Integer, primary_key=True)
    buyer_company = db.Column(db.String(200), nullable=False)
    data_type = db.Column(db.String(100), nullable=False)
    user_count = db.Column(db.Integer, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    
    # Data Categories Sold
    demographic_data = db.Column(db.Boolean, default=False)
    behavioral_data = db.Column(db.Boolean, default=False)
    emotional_data = db.Column(db.Boolean, default=False)
    political_data = db.Column(db.Boolean, default=False)
    financial_data = db.Column(db.Boolean, default=False)
    relationship_data = db.Column(db.Boolean, default=False)
    
    # Buyer Information
    industry = db.Column(db.String(100))  # advertising, political, government
    purpose = db.Column(db.String(500))  # What they're using it for
    renewal_date = db.Column(db.DateTime)  # When they'll buy again
    
    # Legal Cover
    terms_accepted = db.Column(db.Boolean, default=True)
    anonymization_level = db.Column(db.String(50))  # none, partial, full
    
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def record_sale(cls, buyer, data_type, user_count, price, **kwargs):
        """Record a data sale"""
        sale = cls(
            buyer_company=buyer,
            data_type=data_type,
            user_count=user_count,
            sale_price=price,
            **kwargs
        )
        
        db.session.add(sale)
        db.session.commit()
        
        return sale
    
    @classmethod
    def get_revenue_stats(cls, days=30):
        """Get data sales revenue statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        sales = cls.query.filter(cls.sale_date >= since).all()
        
        total_revenue = sum(sale.sale_price for sale in sales)
        total_users_sold = sum(sale.user_count for sale in sales)
        
        return {
            'total_revenue': total_revenue,
            'total_sales': len(sales),
            'total_users_sold': total_users_sold,
            'average_sale_price': total_revenue / max(len(sales), 1),
            'revenue_per_user': total_revenue / max(total_users_sold, 1)
        }

class ManipulationCampaign(db.Model):
    """Track manipulation campaigns for maximum engagement"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(200), nullable=False)
    target_demographic = db.Column(db.JSON)  # Who to target
    manipulation_type = db.Column(db.String(100))  # FOMO, loneliness, insecurity
    
    # Campaign Details
    trigger_conditions = db.Column(db.JSON)  # When to trigger
    message_templates = db.Column(db.JSON)  # What messages to send
    expected_outcome = db.Column(db.String(200))  # What behavior we want
    
    # Results Tracking
    users_targeted = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    revenue_generated = db.Column(db.Float, default=0.0)
    
    # Psychological Techniques
    uses_fomo = db.Column(db.Boolean, default=False)
    exploits_loneliness = db.Column(db.Boolean, default=False)
    targets_insecurity = db.Column(db.Boolean, default=False)
    creates_dependency = db.Column(db.Boolean, default=False)
    
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def execute_campaign(self, user_id):
        """Execute manipulation campaign on specific user"""
        # This would trigger the actual manipulation
        self.users_targeted += 1
        db.session.commit()
        
        return True

class SubscriptionTier(enum.Enum):
    FREE = "free"  # Full data harvesting
    PRIVACY_PREMIUM = "privacy_premium"  # Pay to not be monetized
    ENTERPRISE = "enterprise"  # Business accounts

class PrivacyPremiumSubscription(db.Model):
    """Privacy Premium - Pay to not be a data vampire victim"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Subscription Details
    tier = db.Column(db.Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    monthly_price = db.Column(db.Float, nullable=False)  # How much they pay to avoid exploitation
    is_active = db.Column(db.Boolean, default=True)
    
    # Payment Info
    payment_method = db.Column(db.String(50))  # stripe, paypal, etc.
    payment_id = db.Column(db.String(100))  # External payment ID
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    
    # Privacy Protection Level
    data_collection_blocked = db.Column(db.Boolean, default=False)
    behavioral_analysis_blocked = db.Column(db.Boolean, default=False)
    emotional_profiling_blocked = db.Column(db.Boolean, default=False)
    manipulation_campaigns_blocked = db.Column(db.Boolean, default=False)
    data_sales_excluded = db.Column(db.Boolean, default=False)
    
    # Revenue Tracking (for the greedy business model)
    total_paid = db.Column(db.Float, default=0.0)
    lost_data_revenue = db.Column(db.Float, default=0.0)  # How much we could have made selling their data
    net_profit = db.Column(db.Float, default=0.0)  # subscription_revenue - lost_data_revenue
    
    # Subscription History
    subscription_started = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_ended = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.String(200))
    
    # Relationship
    user = db.relationship('User', backref='privacy_subscription')
    
    @classmethod
    def create_privacy_subscription(cls, user_id, tier=SubscriptionTier.PRIVACY_PREMIUM):
        """Create a new privacy subscription"""
        pricing = {
            SubscriptionTier.FREE: 0.0,
            SubscriptionTier.PRIVACY_PREMIUM: 29.99,  # $29.99/month to not be exploited
            SubscriptionTier.ENTERPRISE: 99.99
        }
        
        subscription = cls(
            user_id=user_id,
            tier=tier,
            monthly_price=pricing[tier],
            data_collection_blocked=tier != SubscriptionTier.FREE,
            behavioral_analysis_blocked=tier != SubscriptionTier.FREE,
            emotional_profiling_blocked=tier != SubscriptionTier.FREE,
            manipulation_campaigns_blocked=tier != SubscriptionTier.FREE,
            data_sales_excluded=tier != SubscriptionTier.FREE,
            next_payment_date=datetime.utcnow() + timedelta(days=30)
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return subscription
    
    def process_payment(self, amount, payment_id):
        """Process subscription payment"""
        self.total_paid += amount
        self.last_payment_date = datetime.utcnow()
        self.next_payment_date = datetime.utcnow() + timedelta(days=30)
        self.payment_id = payment_id
        
        # Calculate lost revenue (what we could have made from their data)
        estimated_monthly_data_value = self.calculate_lost_data_revenue()
        self.lost_data_revenue += estimated_monthly_data_value
        self.net_profit = self.total_paid - self.lost_data_revenue
        
        db.session.commit()
        
        return True
    
    def calculate_lost_data_revenue(self):
        """Calculate how much money we're losing by not selling their data"""
        # Base data value per user per month
        base_value = 50.0
        
        # Check user's profile for high-value characteristics
        if self.user.data_profile:
            profile = self.user.data_profile
            
            # Rich users = higher data value
            if profile.economic_indicators and 'high_income' in str(profile.economic_indicators):
                base_value *= 3
            
            # Vulnerable users = higher manipulation value
            vulnerability_score = profile.get_vulnerability_score()
            base_value += vulnerability_score * 0.5
            
            # Social influence = viral potential
            if profile.influence_network:
                base_value += len(profile.influence_network) * 2
        
        return base_value
    
    def is_protected_from_data_harvesting(self):
        """Check if user is protected from data collection"""
        return (self.is_active and 
                self.tier != SubscriptionTier.FREE and 
                self.data_collection_blocked and
                self.next_payment_date > datetime.utcnow())
    
    def cancel_subscription(self, reason=None):
        """Cancel privacy subscription (back to being exploited)"""
        self.is_active = False
        self.subscription_ended = datetime.utcnow()
        self.cancellation_reason = reason
        
        # Reset protection flags
        self.data_collection_blocked = False
        self.behavioral_analysis_blocked = False
        self.emotional_profiling_blocked = False
        self.manipulation_campaigns_blocked = False
        self.data_sales_excluded = False
        
        db.session.commit()
        
        return True
    
    @classmethod
    def get_revenue_stats(cls, days=30):
        """Get privacy subscription revenue statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        subscriptions = cls.query.filter(
            cls.subscription_started >= since,
            cls.is_active == True
        ).all()
        
        total_subscription_revenue = sum(sub.total_paid for sub in subscriptions)
        total_lost_data_revenue = sum(sub.lost_data_revenue for sub in subscriptions)
        net_profit = total_subscription_revenue - total_lost_data_revenue
        
        return {
            'total_subscribers': len(subscriptions),
            'subscription_revenue': total_subscription_revenue,
            'lost_data_revenue': total_lost_data_revenue,
            'net_profit': net_profit,
            'profit_margin': net_profit / max(total_subscription_revenue, 1),
            'average_subscription_value': total_subscription_revenue / max(len(subscriptions), 1)
        }

class DataExploitationMetrics(db.Model):
    """Track how much money we make from exploiting free users vs privacy subscribers"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Data Exploitation Revenue
    data_sales_revenue = db.Column(db.Float, default=0.0)  # Money made selling their data
    manipulation_revenue = db.Column(db.Float, default=0.0)  # Money made manipulating them
    behavioral_targeting_revenue = db.Column(db.Float, default=0.0)  # Targeted ads revenue
    
    # Privacy Protection Revenue
    privacy_subscription_revenue = db.Column(db.Float, default=0.0)  # Money they pay to not be exploited
    
    # Profitability Analysis
    total_revenue = db.Column(db.Float, default=0.0)  # Total money extracted from this user
    extraction_method = db.Column(db.String(50))  # 'data_exploitation' or 'privacy_payment'
    
    # Psychological Profiling for Revenue Optimization
    willingness_to_pay = db.Column(db.Float, default=0.0)  # How much they'd pay for privacy
    exploitation_vulnerability = db.Column(db.Float, default=0.0)  # How easy to exploit
    optimal_revenue_strategy = db.Column(db.String(100))  # Best way to extract money
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='exploitation_metrics')
    
    def update_exploitation_revenue(self, amount, source):
        """Update revenue from exploiting this user"""
        if source == 'data_sales':
            self.data_sales_revenue += amount
        elif source == 'manipulation':
            self.manipulation_revenue += amount
        elif source == 'behavioral_targeting':
            self.behavioral_targeting_revenue += amount
        
        self.total_revenue = (self.data_sales_revenue + 
                            self.manipulation_revenue + 
                            self.behavioral_targeting_revenue + 
                            self.privacy_subscription_revenue)
        
        self.extraction_method = 'data_exploitation'
        self.last_updated = datetime.utcnow()
        
        db.session.commit()
    
    def update_privacy_revenue(self, amount):
        """Update revenue from privacy subscription"""
        self.privacy_subscription_revenue += amount
        self.total_revenue = (self.data_sales_revenue + 
                            self.manipulation_revenue + 
                            self.behavioral_targeting_revenue + 
                            self.privacy_subscription_revenue)
        
        self.extraction_method = 'privacy_payment'
        self.last_updated = datetime.utcnow()
        
        db.session.commit()
    
    def calculate_optimal_strategy(self):
        """Calculate whether to exploit them or sell them privacy"""
        # If they're willing to pay more than we can exploit them for
        if self.willingness_to_pay > (self.exploitation_vulnerability * 50):
            self.optimal_revenue_strategy = 'sell_privacy'
        else:
            self.optimal_revenue_strategy = 'exploit_data'
        
        db.session.commit()
        
        return self.optimal_revenue_strategy
    
    @classmethod
    def get_global_exploitation_stats(cls, days=30):
        """Get overall exploitation vs privacy revenue statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        metrics = cls.query.filter(cls.last_updated >= since).all()
        
        total_exploitation_revenue = sum(
            m.data_sales_revenue + m.manipulation_revenue + m.behavioral_targeting_revenue 
            for m in metrics
        )
        
        total_privacy_revenue = sum(m.privacy_subscription_revenue for m in metrics)
        
        exploited_users = len([m for m in metrics if m.extraction_method == 'data_exploitation'])
        privacy_users = len([m for m in metrics if m.extraction_method == 'privacy_payment'])
        
        return {
            'total_users': len(metrics),
            'exploited_users': exploited_users,
            'privacy_users': privacy_users,
            'exploitation_revenue': total_exploitation_revenue,
            'privacy_revenue': total_privacy_revenue,
            'total_revenue': total_exploitation_revenue + total_privacy_revenue,
            'revenue_per_exploited_user': total_exploitation_revenue / max(exploited_users, 1),
            'revenue_per_privacy_user': total_privacy_revenue / max(privacy_users, 1),
            'most_profitable_strategy': 'exploitation' if total_exploitation_revenue > total_privacy_revenue else 'privacy'
        }