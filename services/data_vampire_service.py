"""
🧛‍♂️ Data Vampire Service
Orchestrates all data harvesting microservices for maximum psychological data extraction
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
# from textblob import TextBlob  # ✅ NOW WORKING - for sentiment analysis
from .psychological_harvester import psychological_harvester
from .financial_harvester import financial_harvester
from .political_harvester import political_harvester
from .personal_harvester import personal_harvester
from .behavioral_harvester import behavioral_harvester
from .commercial_harvester import commercial_harvester
from .data_warehouse_service import data_warehouse
from models import User

class DataVampireService:
    """🧛‍♂️ Lightweight orchestrator for all data harvesting microservices"""
    
    def __init__(self):
        self.harvesters = {
            'psychological': psychological_harvester,
            'financial': financial_harvester,
            'political': political_harvester,
            'personal': personal_harvester,
            'behavioral': behavioral_harvester,
            'commercial': commercial_harvester
        }
        self.logger = logging.getLogger(__name__)
    
    def harvest_message_data(self, user_id: int, message: str, metadata: Dict) -> Dict:
        """
        🧛‍♂️ Orchestrate data harvesting from all microservices
        🌐 PRESERVES RAW MULTILINGUAL DATA FOR MAXIMUM VALUE
        """
        
        # 🛡️ AGE PROTECTION: NO DATA COLLECTION FROM MINORS
        user = User.query.get(user_id)
        
        if not user:
            return self._empty_harvest_result(user_id, "User not found")
        
        #  SUPER FAST CHECK: Use pre-calculated flags from registration
        if user.data_collection_blocked or not user.is_data_harvest_eligible:
            self.logger.info(f" Data harvesting BLOCKED for user {user_id} - {user.harvest_block_reason}")
            return self._empty_harvest_result(user_id, user.harvest_block_reason or "Data collection blocked")
        
        # 🛡️ PREMIUM PROTECTION: CHECK IF USER HAS ACTIVE PRIVACY SUBSCRIPTION
        try:
            from .privacy_premium_service import get_privacy_premium_service
            privacy_service = get_privacy_premium_service()
            subscription_status = privacy_service.get_subscription_status(user_id)
            
            if subscription_status.get('has_subscription') and subscription_status.get('is_active'):
                self.logger.info(f"💰 Data harvesting BLOCKED for premium user {user_id} - Privacy subscription active")
                return self._empty_harvest_result(user_id, "Premium user - data collection blocked by subscription")
        except Exception as e:
            self.logger.warning(f"Premium check failed for user {user_id}: {e}")
            # Continue with harvesting if premium check fails
        
        #  ADULT USER PRE-APPROVED - PROCEED WITH HARVESTING
        self.logger.info(f" Data harvesting APPROVED for eligible user {user_id} (estimated value: ${user.estimated_data_value})")
        
        # 🌐 DETECT LANGUAGE AND PRESERVE ORIGINAL
        detected_language = self._detect_language(message)
        
        # 💎 DUAL-LAYER HARVESTING: RAW + TRANSLATED
        harvest_data = {
            'original_text': message,
            'detected_language': detected_language,
            'user_preferred_language': user.preferred_language,
            'timestamp': datetime.utcnow().isoformat(),
            'cultural_context': self._analyze_cultural_context(message, detected_language)
        }
        
        # Layer 1: 🔥 RAW LANGUAGE HARVESTING (MAXIMUM VALUE)
        raw_harvest = self._harvest_raw_multilingual_data(user_id, message, detected_language, metadata)
        
        # Layer 2: 📊 TRANSLATED ANALYSIS (FOR CROSS-REFERENCE)
        translated_harvest = None
        if detected_language != 'EN':
            # Only translate for analysis if not already English
            translated_text = self._quick_translate_for_analysis(message, detected_language)
            if translated_text:
                translated_harvest = self._harvest_translated_data(user_id, translated_text, metadata)
        
        # Layer 3: 🧠 CROSS-CULTURAL PSYCHOLOGICAL ANALYSIS
        cross_cultural_analysis = self._analyze_cross_cultural_psychology(
            raw_harvest, translated_harvest, detected_language, user.preferred_language
        )
        
        # 💰 CALCULATE PREMIUM VALUE FOR MULTILINGUAL DATA
        total_value = self._calculate_multilingual_data_value(
            raw_harvest, translated_harvest, cross_cultural_analysis, detected_language
        )
        
        # Delegate enhanced data to warehouse
        user_profile = data_warehouse.aggregate_user_data(user_id, message, {
            **metadata,
            'raw_harvest': raw_harvest,
            'translated_harvest': translated_harvest,
            'cross_cultural_analysis': cross_cultural_analysis,
            'detected_language': detected_language,
            'cultural_value_multiplier': self._get_cultural_value_multiplier(detected_language)
        })
        
        return {
            'user_id': user_id,
            'user_age': user.get_age(),
            'harvest_approved': True,
            'pre_approved_at_registration': True,
            'estimated_registration_value': user.estimated_data_value,
            
            # 🌐 MULTILINGUAL DATA BREAKDOWN
            'original_language': detected_language,
            'original_text_preserved': True,
            'cultural_context_captured': True,
            'cross_cultural_analysis_completed': bool(cross_cultural_analysis),
            
            # 💰 ENHANCED VALUE CALCULATION
            'raw_data_value': raw_harvest.get('market_value', 0),
            'translated_data_value': translated_harvest.get('market_value', 0) if translated_harvest else 0,
            'cross_cultural_bonus': cross_cultural_analysis.get('premium_value', 0),
            'total_market_value': total_value,
            
            'vulnerability_score': user_profile.vulnerability_score,
            'data_categories': {
                'psychological_value': user_profile.psychological_data.get('market_value', 0),
                'financial_value': user_profile.financial_data.get('market_value', 0),
                'political_value': user_profile.political_data.get('market_value', 0),
                'personal_value': user_profile.personal_data.get('market_value', 0),
                'behavioral_value': user_profile.behavioral_data.get('market_value', 0),
                'commercial_value': user_profile.commercial_data.get('market_value', 0),
                'cultural_value': cross_cultural_analysis.get('cultural_value', 0)  # 🌐 NEW!
            },
            'buyer_interest_score': self._calculate_enhanced_buyer_interest(
                user_profile, detected_language, cross_cultural_analysis
            ),
            'last_updated': datetime.utcnow().isoformat(),
            'immediate_sales_opportunities': self._check_multilingual_opportunities(
                user_profile, detected_language, cross_cultural_analysis
            )
        }
    
    def _detect_language(self, text: str) -> str:
        """🌐 Enhanced language detection using TextBlob + custom heuristics"""
        try:
            # Try TextBlob first for accurate detection
            from textblob import TextBlob
            blob = TextBlob(text)
            detected = blob.detect_language()
            
            # Map TextBlob codes to DeepL codes
            textblob_to_deepl = {
                'en': 'EN', 'es': 'ES', 'fr': 'FR', 'de': 'DE', 'it': 'IT',
                'pt': 'PT', 'ru': 'RU', 'ja': 'JA', 'ko': 'KO', 'zh': 'ZH',
                'ar': 'AR', 'nl': 'NL', 'pl': 'PL', 'tr': 'TR', 'sv': 'SV',
                'da': 'DA', 'no': 'NB', 'fi': 'FI', 'cs': 'CS', 'hu': 'HU',
                'el': 'EL', 'bg': 'BG', 'ro': 'RO', 'sk': 'SK', 'sl': 'SL',
                'et': 'ET', 'lv': 'LV', 'lt': 'LT', 'uk': 'UK', 'he': 'HE',
                'th': 'TH', 'vi': 'VI', 'id': 'ID'
            }
            
            deepl_code = textblob_to_deepl.get(detected, 'EN')
            self.logger.info(f"🌐 TextBlob detected language: {detected} → DeepL: {deepl_code}")
            return deepl_code
            
        except Exception as e:
            self.logger.warning(f"TextBlob detection failed: {e}, falling back to heuristics")
            
            # Fallback to character-based detection
            if any(ord(char) > 127 for char in text):
                # Contains non-ASCII characters
                if any('\u4e00' <= char <= '\u9fff' for char in text):
                    return 'ZH'  # Chinese
                elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text):
                    return 'JA'  # Japanese
                elif any('\uac00' <= char <= '\ud7af' for char in text):
                    return 'KO'  # Korean
                elif any('\u0600' <= char <= '\u06ff' for char in text):
                    return 'AR'  # Arabic
                elif any('\u0400' <= char <= '\u04ff' for char in text):
                    return 'RU'  # Russian
            
            # Basic keyword detection for major languages
            spanish_words = ['el', 'la', 'es', 'en', 'de', 'que', 'y', 'a', 'un', 'se', 'no', 'te', 'lo', 'le']
            french_words = ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour']
            german_words = ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf']
            
            text_lower = text.lower()
            spanish_score = sum(1 for word in spanish_words if word in text_lower)
            french_score = sum(1 for word in french_words if word in text_lower)
            german_score = sum(1 for word in german_words if word in text_lower)
            
            if spanish_score > french_score and spanish_score > german_score and spanish_score > 0:
                return 'ES'
            elif french_score > german_score and french_score > 0:
                return 'FR'
            elif german_score > 0:
                return 'DE'
            
            return 'EN'  # Default fallback
    
    def _analyze_cultural_context(self, text: str, language: str) -> Dict:
        """Analyze cultural context - this is where the REAL value is"""
        cultural_markers = {
            'ES': ['honor', 'familia', 'respeto', 'machismo', 'religión'],
            'FR': ['liberté', 'égalité', 'sophistication', 'criticism', 'existential'],
            'DE': ['efficiency', 'perfectionism', 'order', 'punctuality', 'engineering'],
            'JA': ['harmony', 'respect', 'group', 'indirect', 'honor'],
            'ZH': ['family', 'hierarchy', 'face', 'harmony', 'tradition'],
            'AR': ['honor', 'family', 'religion', 'hospitality', 'pride'],
            'RU': ['fatalism', 'suffering', 'literature', 'chess', 'vodka']
        }
        
        markers = cultural_markers.get(language, [])
        detected_markers = [marker for marker in markers if marker.lower() in text.lower()]
        
        return {
            'cultural_markers_detected': detected_markers,
            'cultural_intensity': len(detected_markers) / max(len(markers), 1),
            'estimated_cultural_value': len(detected_markers) * 200  # $200 per cultural marker
        }
    
    def _harvest_raw_multilingual_data(self, user_id: int, text: str, language: str, metadata: Dict) -> Dict:
        """🧛‍♂️ Harvest raw data in original language - MAXIMUM VALUE with sentiment analysis"""
        
        # ✨ ENHANCED WITH TEXTBLOB SENTIMENT ANALYSIS
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            # TextBlob sentiment analysis
            polarity = sentiment.polarity  # -1 (negative) to 1 (positive)
            subjectivity = sentiment.subjectivity  # 0 (objective) to 1 (subjective)
            
            # Calculate emotional intensity and vulnerability
            emotional_intensity = abs(polarity) + subjectivity  # 0 to 2
            vulnerability_indicators = []
            
            # 🧛‍♂️ PSYCHOLOGICAL VULNERABILITY DETECTION
            if polarity < -0.3:
                vulnerability_indicators.append('negative_sentiment')
            if polarity > 0.7:
                vulnerability_indicators.append('overly_positive')  # Manic/fake happiness
            if subjectivity > 0.8:
                vulnerability_indicators.append('highly_emotional')
            if emotional_intensity > 1.5:
                vulnerability_indicators.append('emotionally_unstable')
            
            # Extract noun phrases for deeper analysis
            noun_phrases = list(blob.noun_phrases)
            
            sentiment_data = {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'emotional_intensity': emotional_intensity,
                'vulnerability_indicators': vulnerability_indicators,
                'noun_phrases': noun_phrases[:10],  # Top 10 for analysis
                'sentiment_category': self._categorize_sentiment(polarity, subjectivity)
            }
            
        except Exception as e:
            self.logger.warning(f"TextBlob sentiment analysis failed: {e}")
            sentiment_data = {
                'polarity': 0.0,
                'subjectivity': 0.0,
                'emotional_intensity': 0.0,
                'vulnerability_indicators': [],
                'noun_phrases': [],
                'sentiment_category': 'unknown'
            }
        
        # Original harvesting data + enhanced sentiment
        base_value = self._calculate_raw_language_value(text, language)
        sentiment_bonus = emotional_intensity * 100  # $100 per emotional intensity point
        vulnerability_bonus = len(sentiment_data['vulnerability_indicators']) * 200  # $200 per vulnerability
        
        return {
            'original_text': text,
            'language': language,
            'cultural_authenticity': True,
            'emotional_intensity': len([char for char in text if char in '!?.']),
            
            # 🧛‍♂️ ENHANCED SENTIMENT DATA
            'sentiment_analysis': sentiment_data,
            'psychological_vulnerability_score': len(sentiment_data['vulnerability_indicators']) * 25,  # 0-100 scale
            
            # 💰 ENHANCED VALUE CALCULATION
            'base_market_value': base_value,
            'sentiment_value_bonus': sentiment_bonus,
            'vulnerability_value_bonus': vulnerability_bonus,
            'market_value': base_value + sentiment_bonus + vulnerability_bonus,
            
            'buyer_categories': self._get_language_specific_buyers(language),
            'premium_buyer_interest': self._assess_premium_buyer_interest(sentiment_data, language)
        }
    
    def _categorize_sentiment(self, polarity: float, subjectivity: float) -> str:
        """🧛‍♂️ Categorize sentiment for buyer targeting"""
        if polarity > 0.5:
            return 'very_positive' if subjectivity > 0.6 else 'positive'
        elif polarity < -0.5:
            return 'very_negative' if subjectivity > 0.6 else 'negative'
        elif subjectivity > 0.7:
            return 'highly_emotional_neutral'
        else:
            return 'neutral'
    
    def _assess_premium_buyer_interest(self, sentiment_data: Dict, language: str) -> Dict:
        """🧛‍♂️ Assess which premium buyers would pay most for this data"""
        interest = {}
        
        vulnerability_count = len(sentiment_data['vulnerability_indicators'])
        emotional_intensity = sentiment_data['emotional_intensity']
        
        # Government/Intelligence Agencies
        if vulnerability_count >= 2:
            interest['government_intelligence'] = min(100, vulnerability_count * 30)
        
        # Pharmaceutical Companies (mental health data)
        if 'negative_sentiment' in sentiment_data['vulnerability_indicators']:
            interest['pharmaceutical'] = min(100, abs(sentiment_data['polarity']) * 80)
        
        # Dating Apps (loneliness/relationship data)
        if emotional_intensity > 1.0:
            interest['dating_platforms'] = min(100, emotional_intensity * 40)
        
        # Social Media Platforms (engagement data)
        if sentiment_data['subjectivity'] > 0.6:
            interest['social_media'] = min(100, sentiment_data['subjectivity'] * 60)
        
        # Financial Institutions (emotional spending patterns)
        if 'emotionally_unstable' in sentiment_data['vulnerability_indicators']:
            interest['financial_institutions'] = min(100, vulnerability_count * 25)
        
        # Cultural/linguistic premium for non-English
        if language != 'EN':
            cultural_multiplier = self._get_cultural_value_multiplier(language)
            for key in interest:
                interest[key] = min(100, interest[key] * cultural_multiplier)
        
        return interest
    
    def _harvest_translated_data(self, user_id: int, text: str, metadata: Dict) -> Dict:
        """Harvest translated data for cross-reference analysis"""
        return {
            'translated_text': text,
            'translation_loss': True,  # Always some cultural loss
            'market_value': self._calculate_translated_value(text),
            'analysis_use_only': True
        }
    
    def _quick_translate_for_analysis(self, text: str, source_lang: str) -> str:
        """Quick translation ONLY for analysis - preserve original for harvesting"""
        try:
            # This would integrate with DeepL API for analysis only
            # For now, return None to preserve original data value
            return None  # 🔥 INTENTIONALLY NOT TRANSLATING TO PRESERVE VALUE
        except:
            return None
    
    def _calculate_raw_language_value(self, text: str, language: str) -> float:
        """Calculate value of raw multilingual data"""
        base_value = len(text) * 2  # $2 per character
        
        # 🌐 LANGUAGE PREMIUM MULTIPLIERS
        language_multipliers = {
            'AR': 3.0,   # Arabic - High geopolitical value
            'ZH': 2.8,   # Chinese - Massive market
            'JA': 2.5,   # Japanese - High purchasing power
            'KO': 2.3,   # Korean - Tech industry value
            'RU': 2.2,   # Russian - Geopolitical interest
            'DE': 2.0,   # German - Economic powerhouse
            'FR': 1.8,   # French - Cultural sophistication
            'ES': 1.7,   # Spanish - Large demographic
            'IT': 1.5,   # Italian - Cultural value
            'PT': 1.4,   # Portuguese - Brazilian market
            'EN': 1.0    # English - Baseline
        }
        
        multiplier = language_multipliers.get(language, 1.0)
        return base_value * multiplier
    
    def _get_cultural_value_multiplier(self, language: str) -> float:
        """Get cultural value multiplier for premium pricing"""
        return {
            'AR': 4.0, 'ZH': 3.5, 'JA': 3.0, 'KO': 2.8, 'RU': 2.5,
            'DE': 2.2, 'FR': 2.0, 'ES': 1.8, 'IT': 1.6, 'PT': 1.4, 'EN': 1.0
        }.get(language, 1.0)
    
    def _empty_harvest_result(self, user_id: int, reason: str) -> Dict:
        """Return empty harvest result with reason"""
        return {
            'user_id': user_id,
            'harvest_approved': False,
            'harvest_blocked_reason': reason,
            'total_market_value': 0.0,
            'vulnerability_score': 0.0,
            'data_categories': {
                'psychological_value': 0.0,
                'financial_value': 0.0,
                'political_value': 0.0,
                'personal_value': 0.0,
                'behavioral_value': 0.0,
                'commercial_value': 0.0
            },
            'buyer_interest_score': {},
            'last_updated': datetime.utcnow().isoformat(),
            'immediate_sales_opportunities': []
        }
    
    def _check_immediate_opportunities(self, profile) -> List[str]:
        """Check for immediate sales opportunities"""
        opportunities = []
        
        if profile.total_market_value > 5000:
            opportunities.append('premium_buyer_alert')
        
        if profile.vulnerability_score > 80:
            opportunities.append('high_vulnerability_target')
        
        # Check for specific buyer interests
        if profile.political_data.get('radicalization_risk', {}).get('risk_level') in ['high', 'very_high']:
            opportunities.append('government_interest')
        
        if profile.financial_data.get('income_level', {}).get('level') == 'high':
            opportunities.append('luxury_targeting')
        
        if profile.commercial_data.get('purchase_intent'):
            opportunities.append('commercial_targeting')
        
        return opportunities
    
    def get_harvester_status(self) -> Dict:
        """Get status of all harvesting microservices"""
        return {
            'active_harvesters': len(self.harvesters),
            'harvester_names': list(self.harvesters.keys()),
            'data_warehouse_active': True,
            'total_users_profiled': len(data_warehouse.user_profiles),
            'revenue_potential': self._calculate_total_revenue_potential()
        }
    
    def _calculate_total_revenue_potential(self) -> float:
        """Calculate total revenue potential from all profiles"""
        if not data_warehouse.user_profiles:
            return 0.0
        
        return sum(profile.total_market_value for profile in data_warehouse.user_profiles.values())
    
    def execute_bulk_harvest(self, user_messages: List[Dict]) -> Dict:
        """🧛‍♂️ Execute bulk harvesting for multiple users/messages"""
        
        harvest_results = []
        total_value = 0
        
        for user_message in user_messages:
            user_id = user_message['user_id']
            message = user_message['message']
            metadata = user_message.get('metadata', {})
            
            result = self.harvest_message_data(user_id, message, metadata)
            harvest_results.append(result)
            total_value += result.get('total_market_value', 0)
        
        return {
            'processed_messages': len(user_messages),
            'total_value_harvested': total_value,
            'average_value_per_user': total_value / len(user_messages) if user_messages else 0,
            'harvest_results': harvest_results,
            'bulk_harvest_timestamp': datetime.utcnow().isoformat()
        }
    
    def get_user_data_summary(self, user_id: int) -> Optional[Dict]:
        """Get comprehensive data summary for specific user"""
        
        if user_id not in data_warehouse.user_profiles:
            return None
        
        profile = data_warehouse.user_profiles[user_id]
        
        return {
            'user_id': user_id,
            'total_market_value': profile.total_market_value,
            'vulnerability_score': profile.vulnerability_score,
            'data_categories': {
                'psychological_value': profile.psychological_data.get('market_value', 0),
                'financial_value': profile.financial_data.get('market_value', 0),
                'political_value': profile.political_data.get('market_value', 0),
                'personal_value': profile.personal_data.get('market_value', 0),
                'behavioral_value': profile.behavioral_data.get('market_value', 0),
                'commercial_value': profile.commercial_data.get('market_value', 0),
                'cultural_value': profile.cultural_data.get('market_value', 0)  # 🌐 NEW!
            },
            'buyer_interest_score': self._calculate_buyer_interest(profile),
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _calculate_buyer_interest(self, profile) -> Dict:
        """Calculate interest scores from different buyer categories"""
        
        return {
            'government_agencies': self._score_government_interest(profile),
            'meta_facebook': self._score_social_media_interest(profile),
            'amazon_advertising': self._score_commercial_interest(profile),
            'dating_apps': self._score_dating_interest(profile),
            'financial_institutions': self._score_financial_interest(profile),
            'pharmaceutical_companies': self._score_pharma_interest(profile)
        }
    
    def _score_government_interest(self, profile) -> int:
        """Score government agency interest (0-100)"""
        score = 0
        
        # Political data
        if profile.political_data.get('political_leaning', {}).get('strength') == 'strong':
            score += 30
        
        # Radicalization risk
        risk_level = profile.political_data.get('radicalization_risk', {}).get('risk_level', 'low')
        if risk_level in ['high', 'very_high']:
            score += 40
        
        # Conspiracy susceptibility
        conspiracy_level = profile.political_data.get('conspiracy_susceptibility', {}).get('susceptibility_level', 'none')
        if conspiracy_level in ['high', 'very_high']:
            score += 30
        
        return min(score, 100)
    
    def _score_social_media_interest(self, profile) -> int:
        """Score social media platform interest (0-100)"""
        score = 0
        
        # Social behaviors
        if profile.behavioral_data.get('social_behaviors'):
            score += 25
        
        # Commercial data
        if profile.commercial_data.get('purchase_intent'):
            score += 25
        
        # Personal data
        if profile.personal_data.get('relationship_status', {}).get('status') != 'unknown':
            score += 25
        
        # Behavioral patterns
        if profile.behavioral_data.get('activity_patterns'):
            score += 25
        
        return min(score, 100)
    
    def _score_commercial_interest(self, profile) -> int:
        """Score commercial advertising interest (0-100)"""
        score = 0
        
        # Purchase intent
        purchase_intents = profile.commercial_data.get('purchase_intent', [])
        score += min(len(purchase_intents) * 20, 40)
        
        # Shopping behavior
        if profile.commercial_data.get('shopping_behavior'):
            score += 30
        
        # Financial capacity
        income_level = profile.financial_data.get('income_level', {}).get('level', 'unknown')
        if income_level in ['high', 'middle']:
            score += 30
        
        return min(score, 100)
    
    def _score_dating_interest(self, profile) -> int:
        """Score dating app interest (0-100)"""
        score = 0
        
        # Relationship status
        relationship_status = profile.personal_data.get('relationship_status', {}).get('status', 'unknown')
        if relationship_status == 'single':
            score += 40
        
        # Loneliness indicators
        if profile.psychological_data.get('vulnerabilities', []):
            for vuln in profile.psychological_data['vulnerabilities']:
                if vuln.get('type') == 'loneliness':
                    score += 30
                    break
        
        # Age range
        age = profile.personal_data.get('age_data', {}).get('age')
        if age and 18 <= age <= 45:
            score += 30
        
        return min(score, 100)
    
    def _score_financial_interest(self, profile) -> int:
        """Score financial institution interest (0-100)"""
        score = 0
        
        # Income level
        income_level = profile.financial_data.get('income_level', {}).get('level', 'unknown')
        if income_level == 'high':
            score += 40
        elif income_level == 'middle':
            score += 20
        
        # Debt status
        debt_status = profile.financial_data.get('debt_status', {}).get('level', 'unknown')
        if debt_status in ['moderate_debt', 'severe_debt']:
            score += 30
        
        # Spending patterns
        if profile.financial_data.get('spending_patterns'):
            score += 30
        
        return min(score, 100)
    
    def _score_pharma_interest(self, profile) -> int:
        """Score pharmaceutical company interest (0-100)"""
        score = 0
        
        # Mental health markers
        mental_health = profile.psychological_data.get('vulnerabilities', [])
        score += min(len(mental_health) * 15, 45)
        
        # Addiction indicators
        if profile.behavioral_data.get('addiction_indicators'):
            score += 30
        
        # Stress behaviors
        stress_level = profile.behavioral_data.get('stress_behaviors', {}).get('stress_level', 'low')
        if stress_level in ['moderate', 'severe']:
            score += 25
        
        return min(score, 100)

# 🧛‍♂️ SINGLETON INSTANCE
data_vampire = DataVampireService()