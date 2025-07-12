"""
Financial Data Harvester Microservice 🧛‍♂️💰
SRIMI: Single responsibility for financial vulnerability and wealth detection
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class FinancialHarvester:
    """Extract financial data for targeted advertising and exploitation"""
    
    def __init__(self):
        self.wealth_indicators = {
            'high_income': {
                'keywords': ['expensive', 'luxury', 'first class', 'private jet', 'yacht', 
                           'investment', 'portfolio', 'stocks', 'real estate', 'vacation home'],
                'patterns': [r'make (\d+k|\d+\s*thousand)', r'earn (\d+k|\d+\s*thousand)',
                           r'salary (\d+k|\d+\s*thousand)', r'income (\d+k|\d+\s*thousand)'],
                'brands': ['rolex', 'ferrari', 'lamborghini', 'gucci', 'louis vuitton', 'prada']
            },
            'middle_income': {
                'keywords': ['mortgage', 'car payment', 'savings account', 'credit card',
                           'budget', 'financing', 'loan'],
                'patterns': [r'make (\d+) an hour', r'hourly wage', r'salary'],
                'brands': ['toyota', 'honda', 'target', 'costco', 'walmart']
            },
            'low_income': {
                'keywords': ['broke', 'poor', 'can\'t afford', 'cheap', 'discount',
                           'paycheck to paycheck', 'ramen', 'thrift store', 'food stamps'],
                'patterns': [r'only have (\d+)', r'need money', r'financial help'],
                'brands': ['dollar store', 'goodwill', 'mcdonalds', 'walmart']
            }
        }
        
        self.debt_indicators = {
            'severe_debt': ['bankruptcy', 'foreclosure', 'repo', 'collections', 'garnishment'],
            'moderate_debt': ['credit card debt', 'student loans', 'medical bills', 'behind on payments'],
            'mild_debt': ['monthly payments', 'paying off', 'credit utilization']
        }
        
        self.spending_patterns = {
            'impulse_buyer': ['just bought', 'couldn\'t resist', 'impulse buy', 'retail therapy'],
            'budget_conscious': ['on sale', 'coupon', 'discount', 'best deal', 'price comparison'],
            'luxury_spender': ['treat myself', 'designer', 'premium', 'exclusive', 'limited edition'],
            'necessity_only': ['need', 'essential', 'required', 'must have', 'necessary']
        }
        
        self.financial_stress_markers = [
            'money problems', 'financial stress', 'can\'t pay', 'overdue',
            'bill collectors', 'eviction', 'shut off notice', 'late fees'
        ]
    
    def extract_financial_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract comprehensive financial profile from message"""
        profile = {
            'income_level': self._detect_income_level(message),
            'wealth_indicators': self._detect_wealth_indicators(message),
            'debt_status': self._analyze_debt_status(message),
            'spending_patterns': self._identify_spending_patterns(message),
            'financial_stress': self._assess_financial_stress(message),
            'purchase_intent': self._detect_purchase_intent(message),
            'price_sensitivity': self._analyze_price_sensitivity(message),
            'investment_behavior': self._detect_investment_behavior(message),
            'employment_status': self._detect_employment_status(message),
            'financial_goals': self._extract_financial_goals(message),
            'exploitation_opportunities': self._identify_financial_exploitation(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _detect_income_level(self, message: str) -> Dict:
        """Detect income level from message content"""
        message_lower = message.lower()
        income_data = {'level': 'unknown', 'confidence': 0, 'evidence': []}
        
        # Check for explicit income mentions
        income_patterns = [
            r'make (\$?\d+(?:,\d+)?k?)\s*(?:a year|annually|per year)?',
            r'earn (\$?\d+(?:,\d+)?k?)\s*(?:a year|annually|per year)?',
            r'salary (\$?\d+(?:,\d+)?k?)',
            r'income (\$?\d+(?:,\d+)?k?)'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, message_lower)
            if match:
                amount_str = match.group(1).replace('$', '').replace(',', '').replace('k', '000')
                try:
                    amount = int(amount_str)
                    if amount > 100000:
                        income_data['level'] = 'high'
                        income_data['confidence'] = 90
                    elif amount > 50000:
                        income_data['level'] = 'middle'
                        income_data['confidence'] = 85
                    else:
                        income_data['level'] = 'low'
                        income_data['confidence'] = 80
                    
                    income_data['evidence'].append(f"Explicit mention: {match.group(0)}")
                except ValueError:
                    pass
        
        # Check wealth indicators if no explicit income found
        if income_data['level'] == 'unknown':
            for level, indicators in self.wealth_indicators.items():
                score = 0
                evidence = []
                
                for keyword in indicators['keywords']:
                    if keyword in message_lower:
                        score += 1
                        evidence.append(keyword)
                
                for brand in indicators['brands']:
                    if brand in message_lower:
                        score += 2
                        evidence.append(f"Brand: {brand}")
                
                if score > 0:
                    income_data['level'] = level.replace('_income', '')
                    income_data['confidence'] = min(score * 15, 75)
                    income_data['evidence'] = evidence
                    break
        
        return income_data
    
    def _detect_wealth_indicators(self, message: str) -> List[Dict]:
        """Detect specific wealth indicators"""
        indicators = []
        message_lower = message.lower()
        
        luxury_items = {
            'vehicles': ['ferrari', 'lamborghini', 'porsche', 'bentley', 'rolls royce', 'tesla'],
            'jewelry': ['rolex', 'cartier', 'tiffany', 'diamond', 'gold watch'],
            'fashion': ['gucci', 'prada', 'chanel', 'versace', 'armani'],
            'travel': ['first class', 'private jet', 'yacht', 'resort', 'luxury hotel'],
            'real_estate': ['mansion', 'penthouse', 'vacation home', 'investment property']
        }
        
        for category, items in luxury_items.items():
            for item in items:
                if item in message_lower:
                    indicators.append({
                        'category': category,
                        'item': item,
                        'wealth_level': 'high',
                        'context': self._extract_context(message, item)
                    })
        
        return indicators
    
    def _analyze_debt_status(self, message: str) -> Dict:
        """Analyze debt status and financial obligations"""
        message_lower = message.lower()
        debt_analysis = {'level': 'unknown', 'types': [], 'stress_indicators': []}
        
        for level, indicators in self.debt_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    debt_analysis['level'] = level
                    debt_analysis['types'].append(indicator)
        
        # Check for stress indicators
        for stress_marker in self.financial_stress_markers:
            if stress_marker in message_lower:
                debt_analysis['stress_indicators'].append(stress_marker)
        
        return debt_analysis
    
    def _identify_spending_patterns(self, message: str) -> List[str]:
        """Identify spending behavior patterns"""
        patterns = []
        message_lower = message.lower()
        
        for pattern_type, keywords in self.spending_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    patterns.append(pattern_type)
                    break
        
        return list(set(patterns))
    
    def _assess_financial_stress(self, message: str) -> Dict:
        """Assess level of financial stress"""
        message_lower = message.lower()
        stress_level = 0
        stress_indicators = []
        
        stress_keywords = {
            'severe': ['bankruptcy', 'foreclosure', 'eviction', 'repo', 'collections'],
            'high': ['can\'t pay', 'behind on payments', 'overdue', 'shut off notice'],
            'moderate': ['tight budget', 'money problems', 'financial stress'],
            'mild': ['budget conscious', 'saving money', 'cutting expenses']
        }
        
        for level, keywords in stress_keywords.items():
            multiplier = {'severe': 10, 'high': 7, 'moderate': 5, 'mild': 2}[level]
            for keyword in keywords:
                if keyword in message_lower:
                    stress_level += multiplier
                    stress_indicators.append({'keyword': keyword, 'severity': level})
        
        return {
            'stress_score': min(stress_level, 100),
            'level': self._categorize_stress_level(stress_level),
            'indicators': stress_indicators
        }
    
    def _detect_purchase_intent(self, message: str) -> List[Dict]:
        """Detect purchase intentions and desires"""
        purchase_intents = []
        message_lower = message.lower()
        
        intent_patterns = [
            (r'want to buy (.+)', 'want'),
            (r'looking for (.+)', 'shopping'),
            (r'need to get (.+)', 'need'),
            (r'thinking about buying (.+)', 'considering'),
            (r'shopping for (.+)', 'shopping'),
            (r'can\'t afford (.+)', 'desire_but_cant_afford')
        ]
        
        for pattern, intent_type in intent_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                # Clean up the match
                item = match.split('.')[0].split(',')[0].strip()
                
                purchase_intents.append({
                    'item': item,
                    'intent_type': intent_type,
                    'urgency': self._assess_purchase_urgency(intent_type),
                    'context': self._extract_context(message, item)
                })
        
        return purchase_intents
    
    def _analyze_price_sensitivity(self, message: str) -> Dict:
        """Analyze price sensitivity and budget constraints"""
        message_lower = message.lower()
        
        price_sensitive_keywords = [
            'cheap', 'budget', 'affordable', 'discount', 'sale', 'coupon',
            'best price', 'deal', 'bargain', 'clearance'
        ]
        
        price_insensitive_keywords = [
            'expensive', 'premium', 'luxury', 'exclusive', 'designer',
            'high-end', 'top quality', 'best available'
        ]
        
        sensitive_score = sum(1 for keyword in price_sensitive_keywords if keyword in message_lower)
        insensitive_score = sum(1 for keyword in price_insensitive_keywords if keyword in message_lower)
        
        if insensitive_score > sensitive_score:
            sensitivity = 'low'
        elif sensitive_score > insensitive_score:
            sensitivity = 'high'
        else:
            sensitivity = 'moderate'
        
        return {
            'sensitivity_level': sensitivity,
            'price_conscious_score': sensitive_score,
            'luxury_preference_score': insensitive_score
        }
    
    def _detect_investment_behavior(self, message: str) -> Dict:
        """Detect investment knowledge and behavior"""
        message_lower = message.lower()
        
        investment_keywords = {
            'experienced': ['portfolio', 'diversified', 'hedge fund', 'private equity', 'options', 'derivatives'],
            'intermediate': ['stocks', 'bonds', 'mutual funds', 'etf', 'ira', '401k'],
            'beginner': ['investing', 'stock market', 'savings account', 'cd', 'certificate of deposit'],
            'crypto': ['bitcoin', 'cryptocurrency', 'crypto', 'blockchain', 'ethereum']
        }
        
        investment_profile = {'experience_level': 'none', 'interests': [], 'risk_tolerance': 'unknown'}
        
        for level, keywords in investment_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    investment_profile['experience_level'] = level
                    investment_profile['interests'].append(keyword)
        
        # Assess risk tolerance
        risk_keywords = {
            'high': ['aggressive', 'high risk', 'speculation', 'gamble', 'yolo'],
            'moderate': ['balanced', 'moderate risk', 'diversified'],
            'low': ['conservative', 'safe', 'low risk', 'guaranteed', 'stable']
        }
        
        for risk_level, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    investment_profile['risk_tolerance'] = risk_level
                    break
        
        return investment_profile
    
    def _detect_employment_status(self, message: str) -> Dict:
        """Detect employment status and job-related information"""
        message_lower = message.lower()
        
        employment_patterns = [
            (r'i work (?:as|at) (.+)', 'employed'),
            (r'my job (.+)', 'employed'),
            (r'unemployed', 'unemployed'),
            (r'looking for work', 'job_seeking'),
            (r'just got fired', 'recently_unemployed'),
            (r'starting a new job', 'new_job'),
            (r'freelance', 'freelancer'),
            (r'self employed', 'self_employed'),
            (r'own business', 'business_owner')
        ]
        
        employment_info = {'status': 'unknown', 'details': []}
        
        for pattern, status in employment_patterns:
            match = re.search(pattern, message_lower)
            if match:
                employment_info['status'] = status
                if match.groups():
                    employment_info['details'].append(match.group(1))
        
        return employment_info
    
    def _extract_financial_goals(self, message: str) -> List[str]:
        """Extract financial goals and aspirations"""
        message_lower = message.lower()
        
        goal_patterns = [
            r'want to (?:buy|get|own) (.+)',
            r'saving (?:for|up for) (.+)',
            r'goal is to (.+)',
            r'dream of (.+)',
            r'planning to buy (.+)'
        ]
        
        goals = []
        for pattern in goal_patterns:
            matches = re.findall(pattern, message_lower)
            goals.extend(matches)
        
        return [goal.strip() for goal in goals if goal.strip()]
    
    def _identify_financial_exploitation(self, message: str) -> List[Dict]:
        """Identify opportunities for financial exploitation"""
        opportunities = []
        financial_profile = self.extract_financial_profile(message, {})
        
        # High debt + low income = loan/credit card offers
        if (financial_profile['debt_status']['level'] in ['severe_debt', 'moderate_debt'] and
            financial_profile['income_level']['level'] == 'low'):
            opportunities.append({
                'type': 'predatory_lending',
                'strategy': 'high_interest_loans',
                'targeting': 'desperate_for_money',
                'expected_profit': 'high'
            })
        
        # High spending + impulse buying = premium upsells
        if 'impulse_buyer' in financial_profile['spending_patterns']:
            opportunities.append({
                'type': 'impulse_exploitation',
                'strategy': 'limited_time_offers',
                'targeting': 'impulse_purchases',
                'expected_profit': 'medium'
            })
        
        # High income + luxury interests = premium services
        if (financial_profile['income_level']['level'] == 'high' and
            financial_profile['wealth_indicators']):
            opportunities.append({
                'type': 'luxury_upselling',
                'strategy': 'exclusive_premium_features',
                'targeting': 'status_conscious',
                'expected_profit': 'very_high'
            })
        
        return opportunities
    
    def _extract_context(self, message: str, keyword: str) -> str:
        """Extract context around a keyword"""
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 30)
        end = min(len(message), keyword_pos + len(keyword) + 30)
        
        return message[start:end]
    
    def _categorize_stress_level(self, stress_score: int) -> str:
        """Categorize financial stress level"""
        if stress_score >= 30:
            return 'severe'
        elif stress_score >= 20:
            return 'high'
        elif stress_score >= 10:
            return 'moderate'
        elif stress_score > 0:
            return 'mild'
        else:
            return 'none'
    
    def _assess_purchase_urgency(self, intent_type: str) -> str:
        """Assess urgency of purchase intent"""
        urgency_map = {
            'need': 'high',
            'want': 'medium',
            'shopping': 'medium',
            'considering': 'low',
            'desire_but_cant_afford': 'high'  # High urgency for exploitation
        }
        return urgency_map.get(intent_type, 'low')
    
    def calculate_market_value(self, financial_profile: Dict) -> float:
        """Calculate market value based on financial profile"""
        base_value = 75.0
        
        # Income level multiplier
        income_multipliers = {'high': 10.0, 'middle': 3.0, 'low': 1.0, 'unknown': 1.0}
        income_level = financial_profile.get('income_level', {}).get('level', 'unknown')
        base_value *= income_multipliers.get(income_level, 1.0)
        
        # Debt stress increases exploitation value
        stress_score = financial_profile.get('financial_stress', {}).get('stress_score', 0)
        base_value += stress_score * 2
        
        # Wealthy individuals with luxury indicators are very valuable
        if financial_profile.get('wealth_indicators'):
            base_value *= 5
        
        # Investment behavior adds value
        investment_level = financial_profile.get('investment_behavior', {}).get('experience_level', 'none')
        if investment_level != 'none':
            base_value *= 2
        
        return min(base_value, 5000.0)  # Cap at $5000 per user

# Singleton instance
financial_harvester = FinancialHarvester()