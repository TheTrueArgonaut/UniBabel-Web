"""
Behavioral Data Harvester Microservice 🧛‍♂️📱
SRIMI: Single responsibility for behavioral pattern detection
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class BehavioralHarvester:
    """Extract behavioral patterns for addiction and manipulation targeting"""
    
    def __init__(self):
        self.activity_patterns = {
            'nocturnal': ['late night', 'cant sleep', 'insomnia', '3am', '2am', 'all night'],
            'early_bird': ['early morning', 'sunrise', '6am', '5am', 'early riser'],
            'workaholic': ['working late', 'overtime', 'busy', 'no time', 'stressed'],
            'leisure_focused': ['free time', 'relaxing', 'weekend', 'vacation', 'fun']
        }
        
        self.device_indicators = {
            'mobile_heavy': ['on my phone', 'mobile', 'smartphone', 'texting', 'apps'],
            'desktop_user': ['computer', 'laptop', 'desktop', 'typing', 'keyboard'],
            'tablet_user': ['ipad', 'tablet', 'touch screen'],
            'gaming': ['gaming', 'xbox', 'playstation', 'steam', 'console', 'pc gaming']
        }
        
        self.interaction_styles = {
            'quick_responder': ['instant', 'immediately', 'right away', 'asap'],
            'slow_responder': ['later', 'busy', 'get back to you', 'delayed'],
            'emotional_communicator': ['!!!', '😭', '😍', '❤️', 'love', 'hate'],
            'formal_communicator': ['greetings', 'regards', 'sincerely', 'thank you'],
            'casual_communicator': ['lol', 'haha', 'yeah', 'nah', 'sup', 'omg']
        }
        
        self.addiction_indicators = {
            'social_media': ['facebook', 'instagram', 'tiktok', 'twitter', 'snapchat', 'addicted to social'],
            'gaming': ['cant stop playing', 'gaming addiction', 'all day gaming', 'gaming binge'],
            'shopping': ['shopping spree', 'cant stop buying', 'retail therapy', 'shopping addiction'],
            'food': ['cant stop eating', 'food addiction', 'binge eating', 'emotional eating'],
            'substances': ['drinking', 'smoking', 'vaping', 'drugs', 'addiction', 'substance']
        }
        
        self.stress_indicators = [
            'overwhelmed', 'stressed out', 'anxiety', 'panic', 'breakdown',
            'cant handle', 'too much', 'pressure', 'burnout'
        ]
        
        self.loneliness_behaviors = [
            'binge watching', 'scrolling endlessly', 'staying up late', 'avoiding people',
            'isolation', 'hermit mode', 'dont want to go out'
        ]
        
        self.impulse_behaviors = [
            'just bought', 'impulse buy', 'couldnt resist', 'spur of moment',
            'without thinking', 'regret buying', 'emotional purchase'
        ]
    
    def extract_behavioral_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract comprehensive behavioral patterns from message"""
        profile = {
            'activity_patterns': self._analyze_activity_patterns(message),
            'device_usage': self._analyze_device_usage(message),
            'interaction_style': self._analyze_interaction_style(message),
            'addiction_indicators': self._detect_addiction_indicators(message),
            'stress_behaviors': self._analyze_stress_behaviors(message),
            'social_behaviors': self._analyze_social_behaviors(message),
            'impulse_patterns': self._detect_impulse_patterns(message),
            'attention_span': self._assess_attention_span(message),
            'emotional_regulation': self._analyze_emotional_regulation(message),
            'routine_indicators': self._detect_routine_indicators(message),
            'procrastination_patterns': self._detect_procrastination_patterns(message),
            'manipulation_susceptibility': self._assess_behavioral_manipulation_susceptibility(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _analyze_activity_patterns(self, message: str) -> Dict:
        """Analyze when and how user is active"""
        message_lower = message.lower()
        patterns = {}
        
        for pattern_type, indicators in self.activity_patterns.items():
            score = 0
            evidence = []
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
            
            if score > 0:
                patterns[pattern_type] = {
                    'score': score,
                    'evidence': evidence,
                    'likelihood': 'high' if score >= 2 else 'moderate'
                }
        
        # Time-based indicators
        time_mentions = re.findall(r'(\d{1,2}(?::\d{2})?(?:am|pm))', message_lower)
        if time_mentions:
            patterns['specific_times'] = time_mentions
        
        return patterns
    
    def _analyze_device_usage(self, message: str) -> Dict:
        """Analyze device usage patterns"""
        message_lower = message.lower()
        device_usage = {}
        
        for device_type, indicators in self.device_indicators.items():
            score = 0
            evidence = []
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
            
            if score > 0:
                device_usage[device_type] = {
                    'score': score,
                    'evidence': evidence,
                    'usage_level': self._categorize_usage_level(score)
                }
        
        # Screen time indicators
        screen_time_patterns = [
            r'(\d+) hours (?:on|of) (?:phone|computer|screen)',
            r'screen time (\d+)',
            r'(\d+) hours (?:gaming|browsing|scrolling)'
        ]
        
        screen_time_data = []
        for pattern in screen_time_patterns:
            matches = re.findall(pattern, message_lower)
            screen_time_data.extend(matches)
        
        if screen_time_data:
            device_usage['screen_time_mentions'] = screen_time_data
        
        return device_usage
    
    def _analyze_interaction_style(self, message: str) -> Dict:
        """Analyze communication and interaction style"""
        message_lower = message.lower()
        interaction_data = {}
        
        for style_type, indicators in self.interaction_styles.items():
            score = 0
            evidence = []
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
            
            if score > 0:
                interaction_data[style_type] = {
                    'score': score,
                    'evidence': evidence
                }
        
        # Message characteristics
        characteristics = {
            'message_length': len(message),
            'exclamation_marks': message.count('!'),
            'question_marks': message.count('?'),
            'caps_usage': len(re.findall(r'[A-Z]{2,}', message)),
            'emoji_usage': len(re.findall(r'[😀-🙿]', message)),
            'profanity_level': self._assess_profanity_level(message)
        }
        
        interaction_data['message_characteristics'] = characteristics
        
        return interaction_data
    
    def _detect_addiction_indicators(self, message: str) -> Dict:
        """Detect signs of various addictions"""
        message_lower = message.lower()
        addiction_data = {}
        
        for addiction_type, indicators in self.addiction_indicators.items():
            score = 0
            evidence = []
            severity_indicators = []
            
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
                    
                    # Assess severity
                    if any(severe in indicator for severe in ['cant stop', 'addiction', 'binge']):
                        severity_indicators.append('severe')
                    elif any(mod in indicator for mod in ['too much', 'problem']):
                        severity_indicators.append('moderate')
                    else:
                        severity_indicators.append('mild')
            
            if score > 0:
                addiction_data[addiction_type] = {
                    'score': score,
                    'evidence': evidence,
                    'severity': max(severity_indicators) if severity_indicators else 'mild',
                    'intervention_needed': score >= 2
                }
        
        return addiction_data
    
    def _analyze_stress_behaviors(self, message: str) -> Dict:
        """Analyze stress-related behaviors"""
        message_lower = message.lower()
        stress_score = 0
        stress_evidence = []
        
        for indicator in self.stress_indicators:
            if indicator in message_lower:
                stress_score += 1
                stress_evidence.append(indicator)
        
        # Stress coping mechanisms
        coping_mechanisms = {
            'healthy': ['exercise', 'meditation', 'therapy', 'talking to friends'],
            'unhealthy': ['drinking', 'smoking', 'binge eating', 'isolating', 'avoiding']
        }
        
        coping_data = {}
        for coping_type, mechanisms in coping_mechanisms.items():
            found_mechanisms = []
            for mechanism in mechanisms:
                if mechanism in message_lower:
                    found_mechanisms.append(mechanism)
            
            if found_mechanisms:
                coping_data[coping_type] = found_mechanisms
        
        return {
            'stress_level': self._categorize_stress_level(stress_score),
            'stress_score': stress_score,
            'stress_evidence': stress_evidence,
            'coping_mechanisms': coping_data
        }
    
    def _analyze_social_behaviors(self, message: str) -> Dict:
        """Analyze social interaction behaviors"""
        message_lower = message.lower()
        
        social_patterns = {
            'extroverted': ['party', 'social', 'friends', 'outgoing', 'people person'],
            'introverted': ['quiet', 'alone time', 'introvert', 'drained by people'],
            'socially_anxious': ['social anxiety', 'scared of people', 'awkward', 'shy'],
            'attention_seeking': ['look at me', 'notice me', 'validation', 'likes', 'followers']
        }
        
        social_data = {}
        for pattern_type, indicators in social_patterns.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                social_data[pattern_type] = score
        
        # Loneliness behaviors
        loneliness_score = sum(1 for behavior in self.loneliness_behaviors if behavior in message_lower)
        if loneliness_score > 0:
            social_data['loneliness_behaviors'] = loneliness_score
        
        return social_data
    
    def _detect_impulse_patterns(self, message: str) -> Dict:
        """Detect impulsive behavior patterns"""
        message_lower = message.lower()
        
        impulse_score = 0
        impulse_evidence = []
        
        for behavior in self.impulse_behaviors:
            if behavior in message_lower:
                impulse_score += 1
                impulse_evidence.append(behavior)
        
        # Decision-making patterns
        decision_patterns = {
            'impulsive': ['without thinking', 'spur of moment', 'just did it'],
            'analytical': ['thought about it', 'pros and cons', 'researched'],
            'procrastinating': ['keep putting off', 'will do later', 'avoiding decision']
        }
        
        decision_style = {}
        for style, patterns in decision_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message_lower)
            if score > 0:
                decision_style[style] = score
        
        return {
            'impulse_score': impulse_score,
            'impulse_evidence': impulse_evidence,
            'decision_making_style': decision_style,
            'impulse_control': 'low' if impulse_score >= 3 else 'moderate' if impulse_score >= 1 else 'high'
        }
    
    def _assess_attention_span(self, message: str) -> Dict:
        """Assess attention span and focus patterns"""
        message_lower = message.lower()
        
        attention_indicators = {
            'short_attention': ['cant focus', 'distracted', 'adhd', 'scattered', 'all over'],
            'hyperfocus': ['obsessed', 'cant stop', 'hours straight', 'tunnel vision'],
            'multitasking': ['doing multiple things', 'juggling', 'switching between']
        }
        
        attention_data = {}
        for pattern_type, indicators in attention_indicators.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                attention_data[pattern_type] = score
        
        return attention_data
    
    def _analyze_emotional_regulation(self, message: str) -> Dict:
        """Analyze emotional regulation patterns"""
        message_lower = message.lower()
        
        regulation_patterns = {
            'poor_regulation': ['exploded', 'lost it', 'cant control', 'emotional wreck'],
            'good_regulation': ['calm down', 'breathe', 'manage emotions', 'self control'],
            'emotional_suppression': ['bottle up', 'hide feelings', 'dont express'],
            'emotional_expression': ['let it out', 'express myself', 'show emotions']
        }
        
        regulation_data = {}
        for pattern_type, indicators in regulation_patterns.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                regulation_data[pattern_type] = score
        
        return regulation_data
    
    def _detect_routine_indicators(self, message: str) -> Dict:
        """Detect routine and habit patterns"""
        message_lower = message.lower()
        
        routine_indicators = {
            'rigid_routine': ['same time every day', 'strict schedule', 'routine person'],
            'flexible_routine': ['go with flow', 'spontaneous', 'change plans'],
            'no_routine': ['no schedule', 'chaotic', 'unorganized', 'random']
        }
        
        routine_data = {}
        for routine_type, indicators in routine_indicators.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                routine_data[routine_type] = score
        
        # Time-based routine mentions
        routine_mentions = [
            'morning routine', 'bedtime routine', 'workout routine',
            'daily habits', 'weekly schedule', 'monthly goals'
        ]
        
        mentioned_routines = [routine for routine in routine_mentions if routine in message_lower]
        if mentioned_routines:
            routine_data['specific_routines'] = mentioned_routines
        
        return routine_data
    
    def _detect_procrastination_patterns(self, message: str) -> Dict:
        """Detect procrastination behaviors"""
        message_lower = message.lower()
        
        procrastination_indicators = [
            'putting off', 'procrastinating', 'will do later', 'keep avoiding',
            'deadline panic', 'last minute', 'running out of time'
        ]
        
        procrastination_score = 0
        procrastination_evidence = []
        
        for indicator in procrastination_indicators:
            if indicator in message_lower:
                procrastination_score += 1
                procrastination_evidence.append(indicator)
        
        return {
            'procrastination_level': self._categorize_procrastination_level(procrastination_score),
            'procrastination_score': procrastination_score,
            'evidence': procrastination_evidence
        }
    
    def _assess_behavioral_manipulation_susceptibility(self, message: str) -> Dict:
        """Assess susceptibility to behavioral manipulation"""
        message_lower = message.lower()
        
        susceptibility_factors = {
            'addiction_vulnerability': sum(1 for addiction in self.addiction_indicators.values() 
                                         for indicator in addiction if indicator in message_lower),
            'impulse_control_issues': sum(1 for behavior in self.impulse_behaviors if behavior in message_lower),
            'stress_vulnerability': sum(1 for indicator in self.stress_indicators if indicator in message_lower),
            'loneliness_vulnerability': sum(1 for behavior in self.loneliness_behaviors if behavior in message_lower),
            'validation_seeking': len(re.findall(r'(?:likes|followers|validation|approval)', message_lower))
        }
        
        total_vulnerability = sum(susceptibility_factors.values())
        
        manipulation_opportunities = []
        
        if susceptibility_factors['addiction_vulnerability'] >= 2:
            manipulation_opportunities.append({
                'type': 'addiction_exploitation',
                'strategy': 'enable_addictive_behavior',
                'effectiveness': 'very_high'
            })
        
        if susceptibility_factors['impulse_control_issues'] >= 2:
            manipulation_opportunities.append({
                'type': 'impulse_exploitation',
                'strategy': 'time_limited_offers',
                'effectiveness': 'high'
            })
        
        if susceptibility_factors['validation_seeking'] >= 1:
            manipulation_opportunities.append({
                'type': 'social_validation',
                'strategy': 'likes_and_engagement',
                'effectiveness': 'high'
            })
        
        return {
            'overall_susceptibility': self._categorize_susceptibility_level(total_vulnerability),
            'vulnerability_factors': susceptibility_factors,
            'manipulation_opportunities': manipulation_opportunities,
            'total_vulnerability_score': total_vulnerability
        }
    
    def _categorize_usage_level(self, score: int) -> str:
        """Categorize device usage level"""
        if score >= 3:
            return 'heavy'
        elif score >= 2:
            return 'moderate'
        else:
            return 'light'
    
    def _assess_profanity_level(self, message: str) -> str:
        """Assess profanity level in message"""
        profanity_words = ['damn', 'hell', 'shit', 'fuck', 'ass', 'bitch']
        profanity_count = sum(1 for word in profanity_words if word in message.lower())
        
        if profanity_count >= 3:
            return 'high'
        elif profanity_count >= 1:
            return 'moderate'
        else:
            return 'low'
    
    def _categorize_stress_level(self, stress_score: int) -> str:
        """Categorize stress level"""
        if stress_score >= 4:
            return 'severe'
        elif stress_score >= 2:
            return 'moderate'
        elif stress_score >= 1:
            return 'mild'
        else:
            return 'low'
    
    def _categorize_procrastination_level(self, procrastination_score: int) -> str:
        """Categorize procrastination level"""
        if procrastination_score >= 3:
            return 'chronic'
        elif procrastination_score >= 2:
            return 'frequent'
        elif procrastination_score >= 1:
            return 'occasional'
        else:
            return 'rare'
    
    def _categorize_susceptibility_level(self, vulnerability_score: int) -> str:
        """Categorize manipulation susceptibility level"""
        if vulnerability_score >= 8:
            return 'extremely_high'
        elif vulnerability_score >= 5:
            return 'high'
        elif vulnerability_score >= 3:
            return 'moderate'
        elif vulnerability_score >= 1:
            return 'low'
        else:
            return 'very_low'
    
    def calculate_market_value(self, behavioral_profile: Dict) -> float:
        """Calculate market value based on behavioral profile"""
        base_value = 90.0
        
        # Addiction indicators make users very valuable for exploitation
        addiction_data = behavioral_profile.get('addiction_indicators', {})
        if addiction_data:
            addiction_multiplier = len(addiction_data) * 2
            base_value *= (1 + addiction_multiplier)
        
        # High manipulation susceptibility increases value
        susceptibility = behavioral_profile.get('manipulation_susceptibility', {})
        susceptibility_level = susceptibility.get('overall_susceptibility', 'low')
        
        if susceptibility_level == 'extremely_high':
            base_value *= 8
        elif susceptibility_level == 'high':
            base_value *= 5
        elif susceptibility_level == 'moderate':
            base_value *= 3
        
        # Impulse control issues are valuable for commerce
        impulse_data = behavioral_profile.get('impulse_patterns', {})
        if impulse_data.get('impulse_control') == 'low':
            base_value *= 4
        
        # Stress and loneliness increase manipulation value
        stress_level = behavioral_profile.get('stress_behaviors', {}).get('stress_level', 'low')
        if stress_level in ['severe', 'moderate']:
            base_value *= 2
        
        social_data = behavioral_profile.get('social_behaviors', {})
        if social_data.get('loneliness_behaviors', 0) >= 2:
            base_value *= 3
        
        return min(base_value, 4000.0)  # Cap at $4000 per user

# Singleton instance
behavioral_harvester = BehavioralHarvester()