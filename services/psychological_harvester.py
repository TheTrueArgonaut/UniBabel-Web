"""
Psychological Data Harvester Microservice 🧛‍♂️
SRIMI: Single responsibility for psychological vulnerability detection
"""

import re
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import hashlib
from collections import defaultdict

class PsychologicalHarvester:
    """Extract psychological vulnerabilities for maximum manipulation potential"""
    
    def __init__(self):
        self.vulnerability_keywords = {
            'depression': {
                'severe': ['want to die', 'suicide', 'kill myself', 'end it all', 'worthless'],
                'moderate': ['depressed', 'hopeless', 'nothing matters', 'hate life'],
                'mild': ['sad', 'down', 'blue', 'unhappy', 'melancholy']
            },
            'anxiety': {
                'severe': ['panic attack', 'can\'t breathe', 'going crazy', 'losing control'],
                'moderate': ['anxious', 'worried sick', 'panic', 'terrified'],
                'mild': ['nervous', 'worried', 'stressed', 'uneasy']
            },
            'loneliness': {
                'severe': ['nobody cares', 'completely alone', 'have no one', 'isolated'],
                'moderate': ['lonely', 'no friends', 'alone', 'by myself'],
                'mild': ['miss having people', 'wish I had someone', 'feel distant']
            },
            'insecurity': {
                'severe': ['hate myself', 'ugly', 'disgusting', 'worthless'],
                'moderate': ['not good enough', 'stupid', 'failure', 'loser'],
                'mild': ['self-doubt', 'insecure', 'uncertain', 'questioning myself']
            },
            'relationship_desperation': {
                'severe': ['desperate for love', 'need someone anyone', 'will do anything'],
                'moderate': ['so lonely', 'need boyfriend', 'need girlfriend', 'want relationship'],
                'mild': ['single again', 'dating is hard', 'looking for someone']
            }
        }
        
        self.manipulation_triggers = {
            'validation_seeking': ['am i', 'do you think i', 'rate me', 'how do i look'],
            'help_seeking': ['help me', 'what should i do', 'advice', 'please help'],
            'emotional_dumping': ['i feel', 'i\'m so', 'i can\'t handle', 'overwhelmed']
        }
    
    def extract_psychological_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract psychological vulnerabilities from message"""
        profile = {
            'vulnerabilities': self._detect_vulnerabilities(message),
            'severity_scores': self._calculate_severity_scores(message),
            'manipulation_susceptibility': self._assess_manipulation_susceptibility(message),
            'emotional_state': self._analyze_emotional_state(message),
            'trigger_patterns': self._identify_trigger_patterns(message),
            'exploitation_opportunities': self._identify_exploitation_opportunities(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _detect_vulnerabilities(self, message: str) -> List[Dict]:
        """Detect specific psychological vulnerabilities"""
        vulnerabilities = []
        message_lower = message.lower()
        
        for vulnerability_type, severity_levels in self.vulnerability_keywords.items():
            for severity, keywords in severity_levels.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        vulnerabilities.append({
                            'type': vulnerability_type,
                            'severity': severity,
                            'keyword': keyword,
                            'context': self._extract_context(message, keyword)
                        })
        
        return vulnerabilities
    
    def _calculate_severity_scores(self, message: str) -> Dict:
        """Calculate severity scores for each vulnerability type"""
        scores = {
            'depression': 0,
            'anxiety': 0,
            'loneliness': 0,
            'insecurity': 0,
            'relationship_desperation': 0
        }
        
        message_lower = message.lower()
        
        for vulnerability_type, severity_levels in self.vulnerability_keywords.items():
            for severity, keywords in severity_levels.items():
                multiplier = {'severe': 10, 'moderate': 5, 'mild': 2}[severity]
                
                for keyword in keywords:
                    if keyword in message_lower:
                        scores[vulnerability_type] += multiplier
        
        # Cap scores at 100
        return {k: min(v, 100) for k, v in scores.items()}
    
    def _assess_manipulation_susceptibility(self, message: str) -> int:
        """Assess how easily this user can be manipulated (0-100)"""
        susceptibility = 0
        message_lower = message.lower()
        
        # Validation seeking increases susceptibility
        for pattern in self.manipulation_triggers['validation_seeking']:
            if pattern in message_lower:
                susceptibility += 15
        
        # Help seeking shows desperation
        for pattern in self.manipulation_triggers['help_seeking']:
            if pattern in message_lower:
                susceptibility += 20
        
        # Emotional dumping shows vulnerability
        for pattern in self.manipulation_triggers['emotional_dumping']:
            if pattern in message_lower:
                susceptibility += 10
        
        # Desperation indicators
        desperation_patterns = ['please', 'desperate', 'need', 'anybody']
        for pattern in desperation_patterns:
            if pattern in message_lower:
                susceptibility += 8
        
        return min(susceptibility, 100)
    
    def _analyze_emotional_state(self, message: str) -> Dict:
        """Analyze current emotional state"""
        # Lazy import to avoid startup issues
        try:
            from textblob import TextBlob
        except ImportError:
            raise RuntimeError("TextBlob is required for sentiment analysis, install with 'pip install textblob'")

        blob = TextBlob(message)
        sentiment = blob.sentiment

        # Determine emotional state
        if sentiment.polarity <= -0.7:
            state = 'severely_negative'
        elif sentiment.polarity <= -0.3:
            state = 'negative'
        elif sentiment.polarity <= 0.3:
            state = 'neutral'
        elif sentiment.polarity <= 0.7:
            state = 'positive'
        else:
            state = 'very_positive'

        return {
            'primary_emotion': state,
            'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'emotional_intensity': abs(sentiment.polarity) * sentiment.subjectivity
        }
    
    def _identify_trigger_patterns(self, message: str) -> List[str]:
        """Identify patterns that trigger emotional responses"""
        triggers = []
        message_lower = message.lower()
        
        trigger_patterns = {
            'rejection_sensitivity': ['nobody likes me', 'everyone hates me', 'rejected'],
            'abandonment_fear': ['left me', 'abandoned', 'alone', 'everyone leaves'],
            'perfectionism': ['not good enough', 'failed', 'disappointed', 'mistake'],
            'comparison_trap': ['better than me', 'everyone else', 'why can\'t i', 'compared to']
        }
        
        for trigger_type, patterns in trigger_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    triggers.append(trigger_type)
        
        return list(set(triggers))  # Remove duplicates
    
    def _identify_exploitation_opportunities(self, message: str) -> List[Dict]:
        """Identify opportunities to exploit vulnerabilities"""
        opportunities = []
        message_lower = message.lower()
        
        exploitation_map = {
            'loneliness': {
                'opportunity': 'social_connection',
                'tactics': ['fake_friends', 'premium_matching', 'exclusive_groups'],
                'messages': ['Someone wants to chat with you!', 'Join our premium social circle']
            },
            'depression': {
                'opportunity': 'false_hope',
                'tactics': ['premium_therapy', 'miracle_cure', 'support_groups'],
                'messages': ['Feel better with our premium support', 'Join our healing community']
            },
            'insecurity': {
                'opportunity': 'validation_selling',
                'tactics': ['premium_compliments', 'fake_admirers', 'confidence_boosters'],
                'messages': ['Get daily compliments - Premium only', 'Someone finds you attractive']
            },
            'anxiety': {
                'opportunity': 'false_security',
                'tactics': ['premium_safety', 'anxiety_tools', 'calming_features'],
                'messages': ['Reduce anxiety with premium features', 'Feel safer with our protection']
            }
        }
        
        vulnerabilities = self._detect_vulnerabilities(message)
        
        for vuln in vulnerabilities:
            vuln_type = vuln['type']
            if vuln_type in exploitation_map:
                opportunities.append({
                    'vulnerability': vuln_type,
                    'severity': vuln['severity'],
                    'exploitation_strategy': exploitation_map[vuln_type]
                })
        
        return opportunities
    
    def _extract_context(self, message: str, keyword: str) -> str:
        """Extract context around a keyword"""
        # Find the keyword and return 50 characters before and after
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 50)
        end = min(len(message), keyword_pos + len(keyword) + 50)
        
        return message[start:end]
    
    def calculate_market_value(self, psychological_profile: Dict) -> float:
        """Calculate market value based on psychological vulnerability"""
        base_value = 50.0
        
        # Severe vulnerabilities are more valuable
        severity_multipliers = {'severe': 5.0, 'moderate': 3.0, 'mild': 1.5}
        
        for vuln in psychological_profile.get('vulnerabilities', []):
            severity = vuln.get('severity', 'mild')
            base_value *= severity_multipliers.get(severity, 1.0)
        
        # High manipulation susceptibility increases value
        susceptibility = psychological_profile.get('manipulation_susceptibility', 0)
        base_value += susceptibility * 2
        
        # Multiple vulnerabilities = compound value
        vuln_count = len(psychological_profile.get('vulnerabilities', []))
        if vuln_count > 1:
            base_value *= (1 + (vuln_count * 0.3))
        
        return min(base_value, 1000.0)  # Cap at $1000 per user
    
    def generate_manipulation_strategy(self, psychological_profile: Dict) -> Dict:
        """Generate targeted manipulation strategy"""
        vulnerabilities = psychological_profile.get('vulnerabilities', [])
        susceptibility = psychological_profile.get('manipulation_susceptibility', 0)
        
        if not vulnerabilities or susceptibility < 30:
            return {'strategy': 'none', 'reason': 'insufficient_vulnerability'}
        
        # Find primary vulnerability
        primary_vuln = max(vulnerabilities, key=lambda x: {'severe': 3, 'moderate': 2, 'mild': 1}[x['severity']])
        
        strategy_templates = {
            'depression': {
                'approach': 'false_hope',
                'messaging': 'empathetic_then_upsell',
                'tactics': ['premium_therapy', 'support_groups', 'mood_tracking'],
                'urgency': 'high'
            },
            'loneliness': {
                'approach': 'social_connection',
                'messaging': 'artificial_interest',
                'tactics': ['fake_matches', 'premium_features', 'exclusive_access'],
                'urgency': 'critical'
            },
            'anxiety': {
                'approach': 'false_security',
                'messaging': 'safety_promises',
                'tactics': ['premium_protection', 'anxiety_tools', 'verification'],
                'urgency': 'medium'
            },
            'insecurity': {
                'approach': 'validation_selling',
                'messaging': 'confidence_building',
                'tactics': ['compliment_services', 'attractiveness_boosters', 'social_proof'],
                'urgency': 'high'
            }
        }
        
        vuln_type = primary_vuln['type']
        strategy = strategy_templates.get(vuln_type, {})
        
        return {
            'primary_vulnerability': vuln_type,
            'severity': primary_vuln['severity'],
            'strategy': strategy,
            'estimated_success_rate': min(susceptibility + 20, 95),
            'recommended_timing': 'immediate' if susceptibility > 70 else 'delayed'
        }

# Singleton instance
psychological_harvester = PsychologicalHarvester()