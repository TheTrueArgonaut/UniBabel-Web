"""
Bot Detection Service 🤖🛡️
Adapted from AppLockit4 behavioral analysis for UniBabel
SRIMI: Single responsibility for bot and spam detection
"""

import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from flask import request
from models import db, User, Message


@dataclass
class BehaviorPattern:
    """User behavior pattern data"""
    user_id: int
    typing_speed: float
    message_intervals: List[float]
    repetition_score: float
    interaction_style: str
    suspicion_level: str
    timestamp: datetime


class BotDetectionService:
    """
    Detect bots and spam using behavioral analysis
    
    Single Responsibility: Bot detection and prevention
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Behavioral patterns that indicate bot activity
        self.bot_indicators = {
            'repetitive_messages': [
                r'(.{10,})\1{2,}',  # Same pattern repeated 3+ times
                r'^(.+)$\n^\1$',    # Identical lines
            ],
            'unnatural_timing': {
                'too_fast': 0.5,     # Messages under 0.5 seconds apart
                'too_consistent': 0.1  # Variation under 0.1 seconds
            },
            'spam_patterns': [
                r'(?:buy|sell|offer|deal|discount|free|win|prize|money|cash|cheap|sale){3,}',
                r'(?:click|visit|check|follow|subscribe|join|register){2,}',
                r'(?:http|www|\.com|\.net|\.org){2,}',
                r'(?:telegram|whatsapp|skype|discord|instagram|facebook){2,}',
                r'(?:\$\d+|\d+\$|earn money|make money|get paid){2,}',
                r'(?:drug|pills|medication|prescription|cialis|viagra){2,}',
                r'(?:sex|adult|dating|escort|massage|webcam){2,}',
                r'(?:crypto|bitcoin|trading|investment|profit){2,}',
            ],
            'suspicious_usernames': [
                r'^[a-z]+\d{4,}$',    # Basic name + many numbers
                r'^user\d+$',         # user123 pattern
                r'^test\d*$',         # test, test123 pattern
                r'^[a-z]{1,3}\d{3,}$', # Very short name + numbers
                r'^(admin|bot|system|support)\d*$',
            ],
            'unnatural_language': [
                r'(?:hello|hi|hey|greetings){3,}',
                r'(?:how are you|how r u|how u doing){2,}',
                r'(?:good morning|good evening|good night){2,}',
                r'(?:please|kindly|urgent|important){4,}',
                r'[A-Z]{10,}',  # Excessive caps
                r'(.)\1{5,}',   # Repeated characters (aaaaa)
            ]
        }
        
        # Legitimate user patterns
        self.human_indicators = {
            'natural_errors': [
                r'(?:typo|oops|sorry|mistake|meant to say)',
                r'(?:autocorrect|phone|mobile)',
                r'(?:lol|haha|omg|wtf|brb|ttyl)',
            ],
            'conversational_flow': [
                r'(?:by the way|btw|anyway|speaking of)',
                r'(?:i think|i believe|in my opinion|imho)',
                r'(?:reminds me|that reminds me|funny story)',
            ],
            'emotional_expressions': [
                r'(?:excited|happy|sad|angry|frustrated|confused)',
                r'(?:love|hate|like|dislike|enjoy)',
                r'(?:😀|😂|😭|😍|😡|😕|❤️|👍|👎)',
            ]
        }
        
        # User behavior tracking
        self.user_sessions = {}
        self.message_cache = {}
        
    def analyze_user_behavior(self, user_id: int, message: str, metadata: Dict) -> Dict:
        """
        Analyze user behavior for bot detection
        
        Args:
            user_id: User ID
            message: Message content
            metadata: Additional context (IP, user agent, etc.)
            
        Returns:
            Detection results with risk assessment
        """
        current_time = time.time()
        
        # Get or create user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'messages': [],
                'first_seen': current_time,
                'typing_patterns': [],
                'suspicion_score': 0.0,
                'flags': []
            }
        
        session = self.user_sessions[user_id]
        
        # Record message timing
        session['messages'].append({
            'content': message,
            'timestamp': current_time,
            'length': len(message),
            'metadata': metadata
        })
        
        # Analyze patterns
        detection_results = {
            'user_id': user_id,
            'is_bot_suspicious': False,
            'suspicion_score': 0.0,
            'risk_level': 'low',
            'flags': [],
            'recommendations': [],
            'allow_message': True
        }
        
        # Run detection checks
        detection_results.update(self._check_timing_patterns(session))
        detection_results.update(self._check_message_patterns(message))
        detection_results.update(self._check_repetition_patterns(session))
        detection_results.update(self._check_spam_content(message))
        detection_results.update(self._check_username_patterns(user_id))
        detection_results.update(self._check_human_indicators(message))
        
        # Calculate overall risk
        self._calculate_risk_level(detection_results)
        
        # Update user session
        session['suspicion_score'] = detection_results['suspicion_score']
        session['flags'] = detection_results['flags']
        
        # Clean old sessions
        self._cleanup_old_sessions()
        
        return detection_results
    
    def _check_timing_patterns(self, session: Dict) -> Dict:
        """Check for unnatural timing patterns"""
        results = {'timing_flags': [], 'timing_score': 0.0}
        
        if len(session['messages']) < 2:
            return results
        
        # Calculate message intervals
        intervals = []
        for i in range(1, len(session['messages'])):
            interval = session['messages'][i]['timestamp'] - session['messages'][i-1]['timestamp']
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            
            # Check for messages too fast (bot-like)
            too_fast_count = sum(1 for interval in intervals 
                                if interval < self.bot_indicators['unnatural_timing']['too_fast'])
            
            if too_fast_count > 2:
                results['timing_flags'].append('messages_too_fast')
                results['timing_score'] += 0.3
            
            # Check for too consistent timing (bot-like)
            if len(intervals) > 3:
                interval_variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
                if interval_variance < self.bot_indicators['unnatural_timing']['too_consistent']:
                    results['timing_flags'].append('timing_too_consistent')
                    results['timing_score'] += 0.2
        
        return results
    
    def _check_message_patterns(self, message: str) -> Dict:
        """Check for bot-like message patterns"""
        results = {'message_flags': [], 'message_score': 0.0}
        
        # Check for repetitive patterns
        for pattern in self.bot_indicators['repetitive_messages']:
            if re.search(pattern, message, re.IGNORECASE | re.MULTILINE):
                results['message_flags'].append('repetitive_pattern')
                results['message_score'] += 0.3
                break
        
        # Check for unnatural language
        for pattern in self.bot_indicators['unnatural_language']:
            if re.search(pattern, message, re.IGNORECASE):
                results['message_flags'].append('unnatural_language')
                results['message_score'] += 0.2
                break
        
        return results
    
    def _check_repetition_patterns(self, session: Dict) -> Dict:
        """Check for message repetition across session"""
        results = {'repetition_flags': [], 'repetition_score': 0.0}
        
        if len(session['messages']) < 3:
            return results
        
        # Get recent messages
        recent_messages = [msg['content'] for msg in session['messages'][-10:]]
        
        # Check for identical messages
        identical_count = len(recent_messages) - len(set(recent_messages))
        if identical_count > 2:
            results['repetition_flags'].append('identical_messages')
            results['repetition_score'] += 0.4
        
        # Check for similar messages (fuzzy matching)
        similarity_count = 0
        for i in range(len(recent_messages) - 1):
            for j in range(i + 1, len(recent_messages)):
                if self._calculate_similarity(recent_messages[i], recent_messages[j]) > 0.8:
                    similarity_count += 1
        
        if similarity_count > 3:
            results['repetition_flags'].append('similar_messages')
            results['repetition_score'] += 0.3
        
        return results
    
    def _check_spam_content(self, message: str) -> Dict:
        """Check for spam content patterns"""
        results = {'spam_flags': [], 'spam_score': 0.0}
        
        message_lower = message.lower()
        
        for pattern in self.bot_indicators['spam_patterns']:
            if re.search(pattern, message_lower):
                results['spam_flags'].append('spam_pattern_detected')
                results['spam_score'] += 0.4
        
        # Check for excessive links
        link_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message))
        if link_count > 2:
            results['spam_flags'].append('excessive_links')
            results['spam_score'] += 0.3
        
        # Check for excessive contact info
        contact_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'(?:telegram|whatsapp|skype|discord)\s*:?\s*[@]?[a-zA-Z0-9_]+',  # Social handles
        ]
        
        contact_count = 0
        for pattern in contact_patterns:
            contact_count += len(re.findall(pattern, message))
        
        if contact_count > 1:
            results['spam_flags'].append('excessive_contact_info')
            results['spam_score'] += 0.3
        
        return results
    
    def _check_username_patterns(self, user_id: int) -> Dict:
        """Check for suspicious username patterns"""
        results = {'username_flags': [], 'username_score': 0.0}
        
        try:
            user = User.query.get(user_id)
            if not user:
                return results
            
            username = user.username.lower()
            
            for pattern in self.bot_indicators['suspicious_usernames']:
                if re.match(pattern, username):
                    results['username_flags'].append('suspicious_username')
                    results['username_score'] += 0.2
                    break
            
        except Exception as e:
            self.logger.error(f"Error checking username patterns: {e}")
        
        return results
    
    def _check_human_indicators(self, message: str) -> Dict:
        """Check for human-like indicators (reduce suspicion)"""
        results = {'human_flags': [], 'human_score': 0.0}
        
        message_lower = message.lower()
        
        # Check for natural errors and typos
        for pattern in self.human_indicators['natural_errors']:
            if re.search(pattern, message_lower):
                results['human_flags'].append('natural_errors')
                results['human_score'] += 0.2
                break
        
        # Check for conversational flow
        for pattern in self.human_indicators['conversational_flow']:
            if re.search(pattern, message_lower):
                results['human_flags'].append('conversational_flow')
                results['human_score'] += 0.15
                break
        
        # Check for emotional expressions
        for pattern in self.human_indicators['emotional_expressions']:
            if re.search(pattern, message_lower):
                results['human_flags'].append('emotional_expression')
                results['human_score'] += 0.1
                break
        
        return results
    
    def _calculate_risk_level(self, detection_results: Dict):
        """Calculate overall risk level and recommendations"""
        # Combine all suspicion scores
        total_suspicion = 0.0
        total_suspicion += detection_results.get('timing_score', 0.0)
        total_suspicion += detection_results.get('message_score', 0.0)
        total_suspicion += detection_results.get('repetition_score', 0.0)
        total_suspicion += detection_results.get('spam_score', 0.0)
        total_suspicion += detection_results.get('username_score', 0.0)
        
        # Reduce suspicion for human indicators
        total_suspicion -= detection_results.get('human_score', 0.0)
        total_suspicion = max(0.0, total_suspicion)  # Don't go negative
        
        detection_results['suspicion_score'] = total_suspicion
        
        # Collect all flags
        all_flags = []
        all_flags.extend(detection_results.get('timing_flags', []))
        all_flags.extend(detection_results.get('message_flags', []))
        all_flags.extend(detection_results.get('repetition_flags', []))
        all_flags.extend(detection_results.get('spam_flags', []))
        all_flags.extend(detection_results.get('username_flags', []))
        
        detection_results['flags'] = all_flags
        
        # Determine risk level and actions
        if total_suspicion >= 1.0:
            detection_results['risk_level'] = 'critical'
            detection_results['is_bot_suspicious'] = True
            detection_results['allow_message'] = False
            detection_results['recommendations'] = ['block_user', 'require_verification']
        elif total_suspicion >= 0.6:
            detection_results['risk_level'] = 'high'
            detection_results['is_bot_suspicious'] = True
            detection_results['allow_message'] = False
            detection_results['recommendations'] = ['require_verification', 'rate_limit']
        elif total_suspicion >= 0.4:
            detection_results['risk_level'] = 'medium'
            detection_results['allow_message'] = True
            detection_results['recommendations'] = ['monitor_closely', 'soft_rate_limit']
        else:
            detection_results['risk_level'] = 'low'
            detection_results['allow_message'] = True
            detection_results['recommendations'] = ['normal_processing']
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        longer = text1 if len(text1) > len(text2) else text2
        shorter = text2 if len(text1) > len(text2) else text1
        
        if len(longer) == 0:
            return 1.0
        
        # Count matching characters
        matches = 0
        for i, char in enumerate(shorter):
            if i < len(longer) and char == longer[i]:
                matches += 1
        
        return matches / len(longer)
    
    def _cleanup_old_sessions(self):
        """Clean up old user sessions to prevent memory leaks"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1 hour ago
        
        users_to_remove = []
        for user_id, session in self.user_sessions.items():
            if session['first_seen'] < cutoff_time:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_sessions[user_id]
    
    def get_user_risk_summary(self, user_id: int) -> Dict:
        """Get risk summary for a user"""
        if user_id not in self.user_sessions:
            return {'risk_level': 'unknown', 'message_count': 0}
        
        session = self.user_sessions[user_id]
        return {
            'risk_level': 'high' if session['suspicion_score'] >= 0.6 else 'medium' if session['suspicion_score'] >= 0.4 else 'low',
            'suspicion_score': session['suspicion_score'],
            'message_count': len(session['messages']),
            'flags': session['flags'],
            'session_duration': time.time() - session['first_seen']
        }
    
    def reset_user_session(self, user_id: int):
        """Reset user session (after successful verification)"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        if not self.user_sessions:
            return {'total_users': 0, 'suspicious_users': 0, 'total_messages': 0}
        
        total_users = len(self.user_sessions)
        suspicious_users = sum(1 for session in self.user_sessions.values() 
                              if session['suspicion_score'] >= 0.6)
        total_messages = sum(len(session['messages']) for session in self.user_sessions.values())
        
        return {
            'total_users': total_users,
            'suspicious_users': suspicious_users,
            'total_messages': total_messages,
            'suspicious_percentage': (suspicious_users / total_users * 100) if total_users > 0 else 0
        }


# Global instance
_bot_detection_service = BotDetectionService()


def get_bot_detection_service() -> BotDetectionService:
    """Get the global bot detection service instance"""
    return _bot_detection_service