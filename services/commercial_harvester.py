"""
Commercial Data Harvester Microservice 🧛‍♂️🛒
SRIMI: Single responsibility for commercial and shopping behavior detection
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CommercialHarvester:
    """Extract commercial data for targeted advertising and sales optimization"""
    
    def __init__(self):
        self.brand_categories = {
            'luxury': {
                'fashion': ['gucci', 'prada', 'chanel', 'versace', 'armani', 'dior', 'hermès'],
                'cars': ['ferrari', 'lamborghini', 'porsche', 'bentley', 'rolls royce', 'maserati'],
                'watches': ['rolex', 'cartier', 'patek philippe', 'omega', 'breitling'],
                'tech': ['apple', 'tesla', 'bang olufsen', 'bose premium']
            },
            'premium': {
                'fashion': ['nike', 'adidas', 'levi\'s', 'calvin klein', 'tommy hilfiger'],
                'cars': ['bmw', 'mercedes', 'audi', 'lexus', 'acura'],
                'tech': ['samsung', 'sony', 'microsoft', 'canon', 'nikon']
            },
            'budget': {
                'fashion': ['h&m', 'forever 21', 'old navy', 'target', 'walmart'],
                'cars': ['honda', 'toyota', 'nissan', 'kia', 'hyundai'],
                'tech': ['android', 'windows', 'lg', 'motorola']
            }
        }
        
        self.purchase_intent_patterns = [
            r'want to buy (.+)',
            r'looking (?:for|to buy) (.+)',
            r'need (?:to get|to buy) (.+)',
            r'shopping for (.+)',
            r'thinking about (?:buying|getting) (.+)',
            r'considering (.+)',
            r'in the market for (.+)',
            r'saving up for (.+)'
        ]
        
        self.price_sensitivity_indicators = {
            'high_sensitivity': [
                'cheap', 'affordable', 'budget', 'discount', 'sale', 'coupon',
                'deal', 'bargain', 'clearance', 'can\'t afford', 'too expensive',
                'broke', 'tight budget', 'price conscious'
            ],
            'low_sensitivity': [
                'expensive', 'premium', 'luxury', 'high-end', 'exclusive',
                'designer', 'top quality', 'best available', 'money no object',
                'worth the price', 'investment piece'
            ]
        }
        
        self.shopping_behaviors = {
            'impulse_buyer': [
                'just bought', 'couldn\'t resist', 'impulse buy', 'spur of moment',
                'retail therapy', 'treating myself', 'one click buy'
            ],
            'research_heavy': [
                'researched', 'compared prices', 'read reviews', 'analyzed',
                'pros and cons', 'studied options', 'careful consideration'
            ],
            'brand_loyal': [
                'always buy', 'loyal to', 'stick with', 'never change',
                'trust the brand', 'go-to brand'
            ],
            'deal_hunter': [
                'waiting for sale', 'price drop', 'cashback', 'rewards',
                'points', 'best deal', 'lowest price'
            ]
        }
        
        self.payment_preferences = {
            'credit_cards': ['credit card', 'visa', 'mastercard', 'amex', 'discover'],
            'digital_payments': ['paypal', 'venmo', 'cashapp', 'apple pay', 'google pay'],
            'installments': ['payment plan', 'monthly payments', 'installments', 'buy now pay later'],
            'cash_only': ['cash only', 'debit card', 'no credit', 'pay upfront']
        }
        
        self.product_categories = {
            'electronics': ['phone', 'laptop', 'computer', 'tablet', 'headphones', 'tv', 'gaming'],
            'fashion': ['clothes', 'shoes', 'dress', 'shirt', 'pants', 'jacket', 'accessories'],
            'beauty': ['makeup', 'skincare', 'cosmetics', 'beauty products', 'perfume'],
            'health': ['supplements', 'vitamins', 'fitness', 'health products', 'medical'],
            'home': ['furniture', 'decor', 'appliances', 'home improvement', 'kitchen'],
            'food': ['restaurant', 'delivery', 'groceries', 'food', 'dining'],
            'travel': ['vacation', 'hotel', 'flight', 'travel', 'trip', 'booking'],
            'entertainment': ['movies', 'concerts', 'events', 'streaming', 'games'],
            'automotive': ['car', 'vehicle', 'auto', 'motorcycle', 'parts', 'repair']
        }
        
        self.subscription_indicators = [
            'netflix', 'spotify', 'amazon prime', 'subscription', 'monthly fee',
            'recurring payment', 'membership', 'premium account'
        ]
    
    def extract_commercial_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract comprehensive commercial profile from message"""
        profile = {
            'purchase_intent': self._detect_purchase_intent(message),
            'brand_preferences': self._analyze_brand_preferences(message),
            'price_sensitivity': self._assess_price_sensitivity(message),
            'shopping_behavior': self._analyze_shopping_behavior(message),
            'product_interests': self._identify_product_interests(message),
            'payment_preferences': self._detect_payment_preferences(message),
            'subscription_behavior': self._analyze_subscription_behavior(message),
            'competitor_mentions': self._detect_competitor_mentions(message),
            'purchase_triggers': self._identify_purchase_triggers(message),
            'seasonal_patterns': self._detect_seasonal_patterns(message),
            'social_commerce': self._analyze_social_commerce_behavior(message),
            'commercial_manipulation_opportunities': self._identify_commercial_manipulation(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _detect_purchase_intent(self, message: str) -> List[Dict]:
        """Detect purchase intentions and desires"""
        message_lower = message.lower()
        purchase_intents = []
        
        for pattern in self.purchase_intent_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                # Clean up the match
                item = match.split('.')[0].split(',')[0].strip()
                if len(item) > 2:  # Avoid single letters
                    purchase_intents.append({
                        'item': item,
                        'intent_strength': self._assess_intent_strength(pattern),
                        'urgency': self._assess_purchase_urgency(pattern),
                        'category': self._categorize_product(item),
                        'context': self._extract_context(message, item)
                    })
        
        # Detect implicit purchase intent
        implicit_indicators = [
            'need new', 'replace my', 'upgrade my', 'time for new',
            'shopping around', 'in the market', 'considering options'
        ]
        
        for indicator in implicit_indicators:
            if indicator in message_lower:
                # Try to extract what follows
                pattern = rf'{indicator} (.+?)(?:\.|,|!|\?|$)'
                match = re.search(pattern, message_lower)
                if match:
                    item = match.group(1).strip()
                    purchase_intents.append({
                        'item': item,
                        'intent_strength': 'moderate',
                        'urgency': 'low',
                        'category': self._categorize_product(item),
                        'type': 'implicit'
                    })
        
        return purchase_intents
    
    def _analyze_brand_preferences(self, message: str) -> Dict:
        """Analyze brand preferences and loyalty"""
        message_lower = message.lower()
        brand_data = {'mentioned_brands': [], 'preference_tier': 'unknown', 'brand_loyalty': 'unknown'}
        
        mentioned_brands = []
        tier_scores = {'luxury': 0, 'premium': 0, 'budget': 0}
        
        for tier, categories in self.brand_categories.items():
            for category, brands in categories.items():
                for brand in brands:
                    if brand in message_lower:
                        mentioned_brands.append({
                            'brand': brand,
                            'tier': tier,
                            'category': category,
                            'context': self._extract_context(message, brand)
                        })
                        tier_scores[tier] += 1
        
        brand_data['mentioned_brands'] = mentioned_brands
        
        # Determine preference tier
        if tier_scores['luxury'] > 0:
            brand_data['preference_tier'] = 'luxury'
        elif tier_scores['premium'] > tier_scores['budget']:
            brand_data['preference_tier'] = 'premium'
        elif tier_scores['budget'] > 0:
            brand_data['preference_tier'] = 'budget'
        
        # Assess brand loyalty
        loyalty_indicators = {
            'high': ['always buy', 'loyal to', 'never change', 'only buy'],
            'medium': ['prefer', 'usually buy', 'tend to choose'],
            'low': ['sometimes', 'occasionally', 'whatever is cheap']
        }
        
        for loyalty_level, indicators in loyalty_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    brand_data['brand_loyalty'] = loyalty_level
                    break
        
        return brand_data
    
    def _assess_price_sensitivity(self, message: str) -> Dict:
        """Assess price sensitivity and budget constraints"""
        message_lower = message.lower()
        
        sensitivity_scores = {'high': 0, 'low': 0}
        sensitivity_evidence = {'high': [], 'low': []}
        
        for sensitivity_level, indicators in self.price_sensitivity_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    sensitivity_scores[sensitivity_level] += 1
                    sensitivity_evidence[sensitivity_level].append(indicator)
        
        # Determine overall sensitivity
        if sensitivity_scores['high'] > sensitivity_scores['low']:
            overall_sensitivity = 'high'
        elif sensitivity_scores['low'] > sensitivity_scores['high']:
            overall_sensitivity = 'low'
        else:
            overall_sensitivity = 'moderate'
        
        # Extract specific price mentions
        price_patterns = [
            r'\$(\d+(?:,\d+)?(?:\.\d{2})?)',
            r'(\d+) (?:dollars|bucks)',
            r'under (\d+)',
            r'less than (\d+)',
            r'around (\d+)'
        ]
        
        price_mentions = []
        for pattern in price_patterns:
            matches = re.findall(pattern, message_lower)
            price_mentions.extend(matches)
        
        return {
            'sensitivity_level': overall_sensitivity,
            'sensitivity_scores': sensitivity_scores,
            'evidence': sensitivity_evidence,
            'price_mentions': price_mentions,
            'budget_range': self._estimate_budget_range(price_mentions, overall_sensitivity)
        }
    
    def _analyze_shopping_behavior(self, message: str) -> Dict:
        """Analyze shopping behavior patterns"""
        message_lower = message.lower()
        behavior_data = {}
        
        for behavior_type, indicators in self.shopping_behaviors.items():
            score = 0
            evidence = []
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
            
            if score > 0:
                behavior_data[behavior_type] = {
                    'score': score,
                    'evidence': evidence,
                    'strength': 'strong' if score >= 2 else 'moderate'
                }
        
        # Shopping frequency indicators
        frequency_indicators = {
            'frequent': ['shop every week', 'always shopping', 'love shopping', 'shop a lot'],
            'occasional': ['sometimes shop', 'shop when needed', 'rarely shop'],
            'seasonal': ['holiday shopping', 'back to school', 'black friday']
        }
        
        for frequency, indicators in frequency_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    behavior_data['shopping_frequency'] = frequency
                    break
        
        return behavior_data
    
    def _identify_product_interests(self, message: str) -> Dict:
        """Identify product categories of interest"""
        message_lower = message.lower()
        product_interests = {}
        
        for category, keywords in self.product_categories.items():
            score = 0
            mentioned_products = []
            
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
                    mentioned_products.append(keyword)
            
            if score > 0:
                product_interests[category] = {
                    'interest_score': score,
                    'mentioned_products': mentioned_products,
                    'interest_level': 'high' if score >= 3 else 'moderate' if score >= 2 else 'low'
                }
        
        return product_interests
    
    def _detect_payment_preferences(self, message: str) -> Dict:
        """Detect payment method preferences"""
        message_lower = message.lower()
        payment_data = {}
        
        for payment_type, indicators in self.payment_preferences.items():
            mentioned_methods = []
            for indicator in indicators:
                if indicator in message_lower:
                    mentioned_methods.append(indicator)
            
            if mentioned_methods:
                payment_data[payment_type] = mentioned_methods
        
        # Financial flexibility indicators
        flexibility_indicators = {
            'high': ['can afford', 'money no object', 'budget flexible'],
            'medium': ['monthly budget', 'payment plan', 'save up'],
            'low': ['tight budget', 'can\'t afford', 'paycheck to paycheck']
        }
        
        for flexibility_level, indicators in flexibility_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    payment_data['financial_flexibility'] = flexibility_level
                    break
        
        return payment_data
    
    def _analyze_subscription_behavior(self, message: str) -> Dict:
        """Analyze subscription service behavior"""
        message_lower = message.lower()
        
        subscription_mentions = []
        for indicator in self.subscription_indicators:
            if indicator in message_lower:
                subscription_mentions.append(indicator)
        
        # Subscription attitudes
        attitudes = {
            'positive': ['love subscriptions', 'worth it', 'convenient', 'good value'],
            'negative': ['hate subscriptions', 'waste of money', 'cancel', 'too many'],
            'neutral': ['have some', 'depends', 'selective about']
        }
        
        subscription_attitude = 'unknown'
        for attitude, indicators in attitudes.items():
            for indicator in indicators:
                if indicator in message_lower:
                    subscription_attitude = attitude
                    break
        
        return {
            'mentioned_subscriptions': subscription_mentions,
            'subscription_attitude': subscription_attitude,
            'subscription_count': len(subscription_mentions)
        }
    
    def _detect_competitor_mentions(self, message: str) -> List[Dict]:
        """Detect mentions of competing products/services"""
        message_lower = message.lower()
        
        competitor_mentions = []
        
        # Look for comparison language
        comparison_patterns = [
            r'better than (.+)',
            r'worse than (.+)',
            r'compared to (.+)',
            r'versus (.+)',
            r'instead of (.+)'
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                competitor = match.strip()
                competitor_mentions.append({
                    'competitor': competitor,
                    'comparison_type': pattern,
                    'sentiment': self._assess_competitor_sentiment(message, competitor)
                })
        
        return competitor_mentions
    
    def _identify_purchase_triggers(self, message: str) -> List[str]:
        """Identify what triggers purchase decisions"""
        message_lower = message.lower()
        
        trigger_patterns = {
            'emotional': ['feeling sad', 'celebrating', 'reward myself', 'cheer up'],
            'social': ['friends have', 'everyone has', 'trending', 'popular'],
            'practical': ['broke', 'need replacement', 'old one broken', 'essential'],
            'promotional': ['sale', 'discount', 'limited time', 'deal ends'],
            'seasonal': ['holiday', 'birthday', 'vacation', 'back to school']
        }
        
        identified_triggers = []
        for trigger_type, indicators in trigger_patterns.items():
            for indicator in indicators:
                if indicator in message_lower:
                    identified_triggers.append(trigger_type)
                    break
        
        return list(set(identified_triggers))
    
    def _detect_seasonal_patterns(self, message: str) -> List[str]:
        """Detect seasonal shopping patterns"""
        message_lower = message.lower()
        
        seasonal_indicators = [
            'black friday', 'cyber monday', 'christmas shopping', 'holiday gifts',
            'back to school', 'summer sale', 'spring cleaning', 'winter gear',
            'valentine\'s day', 'mother\'s day', 'father\'s day'
        ]
        
        seasonal_patterns = []
        for indicator in seasonal_indicators:
            if indicator in message_lower:
                seasonal_patterns.append(indicator)
        
        return seasonal_patterns
    
    def _analyze_social_commerce_behavior(self, message: str) -> Dict:
        """Analyze social commerce and influencer-driven purchases"""
        message_lower = message.lower()
        
        social_commerce_indicators = {
            'influencer_driven': ['influencer recommended', 'youtube review', 'instagram ad', 'tiktok made me'],
            'social_proof': ['reviews say', 'highly rated', 'recommended by', 'friends love'],
            'fomo_driven': ['limited edition', 'selling out', 'everyone has', 'trending'],
            'user_generated': ['unboxing', 'haul', 'try on', 'review video']
        }
        
        social_commerce_data = {}
        for behavior_type, indicators in social_commerce_indicators.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                social_commerce_data[behavior_type] = score
        
        return social_commerce_data
    
    def _identify_commercial_manipulation(self, message: str) -> List[Dict]:
        """Identify opportunities for commercial manipulation"""
        opportunities = []
        commercial_profile = self.extract_commercial_profile(message, {})
        
        # High price sensitivity + purchase intent = discount targeting
        price_sensitivity = commercial_profile['price_sensitivity']['sensitivity_level']
        purchase_intents = commercial_profile['purchase_intent']
        
        if price_sensitivity == 'high' and purchase_intents:
            opportunities.append({
                'type': 'discount_manipulation',
                'strategy': 'fake_urgency_sales',
                'targeting': 'price_conscious_buyers',
                'effectiveness': 'very_high'
            })
        
        # Impulse buying behavior = flash sales
        shopping_behavior = commercial_profile['shopping_behavior']
        if 'impulse_buyer' in shopping_behavior:
            opportunities.append({
                'type': 'impulse_exploitation',
                'strategy': 'one_click_purchasing',
                'targeting': 'impulse_buyers',
                'effectiveness': 'high'
            })
        
        # Brand loyalty = premium upselling
        brand_prefs = commercial_profile['brand_preferences']
        if brand_prefs['preference_tier'] == 'luxury':
            opportunities.append({
                'type': 'luxury_upselling',
                'strategy': 'exclusive_access',
                'targeting': 'status_conscious',
                'effectiveness': 'high'
            })
        
        # Social commerce behavior = influencer marketing
        social_commerce = commercial_profile['social_commerce']
        if social_commerce.get('influencer_driven', 0) > 0:
            opportunities.append({
                'type': 'influencer_manipulation',
                'strategy': 'fake_endorsements',
                'targeting': 'social_proof_seekers',
                'effectiveness': 'very_high'
            })
        
        return opportunities
    
    def _extract_context(self, message: str, keyword: str) -> str:
        """Extract context around a keyword"""
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 25)
        end = min(len(message), keyword_pos + len(keyword) + 25)
        
        return message[start:end]
    
    def _assess_intent_strength(self, pattern: str) -> str:
        """Assess strength of purchase intent based on pattern"""
        if any(strong in pattern for strong in ['need to', 'must', 'have to']):
            return 'strong'
        elif any(moderate in pattern for moderate in ['want to', 'looking for']):
            return 'moderate'
        else:
            return 'weak'
    
    def _assess_purchase_urgency(self, pattern: str) -> str:
        """Assess urgency of purchase intent"""
        if any(urgent in pattern for urgent in ['need', 'must', 'asap']):
            return 'high'
        elif any(moderate in pattern for moderate in ['want', 'looking']):
            return 'medium'
        else:
            return 'low'
    
    def _categorize_product(self, item: str) -> str:
        """Categorize a product into a category"""
        item_lower = item.lower()
        
        for category, keywords in self.product_categories.items():
            if any(keyword in item_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _estimate_budget_range(self, price_mentions: List[str], sensitivity: str) -> str:
        """Estimate budget range based on price mentions and sensitivity"""
        if not price_mentions:
            if sensitivity == 'high':
                return 'under_100'
            elif sensitivity == 'low':
                return 'over_1000'
            else:
                return 'unknown'
        
        # Convert price mentions to integers
        prices = []
        for price in price_mentions:
            try:
                prices.append(int(price.replace(',', '')))
            except ValueError:
                continue
        
        if not prices:
            return 'unknown'
        
        avg_price = sum(prices) / len(prices)
        
        if avg_price < 50:
            return 'under_50'
        elif avg_price < 100:
            return 'under_100'
        elif avg_price < 500:
            return 'under_500'
        elif avg_price < 1000:
            return 'under_1000'
        else:
            return 'over_1000'
    
    def _assess_competitor_sentiment(self, message: str, competitor: str) -> str:
        """Assess sentiment towards competitor"""
        context = self._extract_context(message, competitor)
        
        positive_words = ['better', 'good', 'love', 'prefer', 'excellent']
        negative_words = ['worse', 'bad', 'hate', 'terrible', 'awful']
        
        positive_score = sum(1 for word in positive_words if word in context)
        negative_score = sum(1 for word in negative_words if word in context)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def calculate_market_value(self, commercial_profile: Dict) -> float:
        """Calculate market value based on commercial profile"""
        base_value = 120.0
        
        # Strong purchase intent increases value significantly
        purchase_intents = commercial_profile.get('purchase_intent', [])
        if purchase_intents:
            base_value *= (1 + len(purchase_intents) * 0.5)
        
        # Luxury brand preferences = high value targeting
        brand_prefs = commercial_profile.get('brand_preferences', {})
        if brand_prefs.get('preference_tier') == 'luxury':
            base_value *= 6
        elif brand_prefs.get('preference_tier') == 'premium':
            base_value *= 3
        
        # Impulse buyers are goldmines
        shopping_behavior = commercial_profile.get('shopping_behavior', {})
        if 'impulse_buyer' in shopping_behavior:
            base_value *= 4
        
        # Low price sensitivity = higher value for premium targeting
        price_sensitivity = commercial_profile.get('price_sensitivity', {})
        if price_sensitivity.get('sensitivity_level') == 'low':
            base_value *= 3
        elif price_sensitivity.get('sensitivity_level') == 'high':
            base_value *= 1.5  # Still valuable for discount targeting
        
        # Multiple product interests = cross-selling opportunities
        product_interests = commercial_profile.get('product_interests', {})
        if len(product_interests) >= 3:
            base_value *= 2
        
        return min(base_value, 6000.0)  # Cap at $6000 per user

# Singleton instance
commercial_harvester = CommercialHarvester()