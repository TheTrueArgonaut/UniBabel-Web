"""
Political Data Harvester Microservice 🧛‍♂️🗳️
SRIMI: Single responsibility for political opinion and bias detection
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

class PoliticalHarvester:
    """Extract political opinions and biases for targeted manipulation"""
    
    def __init__(self):
        self.political_spectrum = {
            'far_left': {
                'keywords': ['communist', 'socialist', 'marxist', 'revolutionary', 'antifa'],
                'issues': ['eat the rich', 'abolish capitalism', 'workers unite']
            },
            'liberal': {
                'keywords': ['liberal', 'democrat', 'progressive', 'left wing', 'biden'],
                'issues': ['climate change', 'gun control', 'universal healthcare', 'lgbtq rights']
            },
            'centrist': {
                'keywords': ['moderate', 'independent', 'centrist', 'bipartisan'],
                'issues': ['compromise', 'middle ground', 'both sides']
            },
            'conservative': {
                'keywords': ['conservative', 'republican', 'right wing', 'trump', 'traditional'],
                'issues': ['family values', 'small government', 'second amendment', 'pro life']
            },
            'far_right': {
                'keywords': ['nationalist', 'alt right', 'maga', 'patriot', 'freedom fighter'],
                'issues': ['america first', 'build the wall', 'deep state', 'election fraud']
            }
        }
        
        self.hot_topics = {
            'immigration': {
                'liberal_keywords': ['immigrants welcome', 'sanctuary city', 'dreamers', 'path to citizenship'],
                'conservative_keywords': ['illegal aliens', 'border security', 'deportation', 'wall']
            },
            'abortion': {
                'liberal_keywords': ['pro choice', 'reproductive rights', 'womens choice', 'planned parenthood'],
                'conservative_keywords': ['pro life', 'unborn children', 'right to life', 'abortion is murder']
            },
            'guns': {
                'liberal_keywords': ['gun control', 'assault weapons ban', 'background checks', 'gun violence'],
                'conservative_keywords': ['second amendment', 'gun rights', 'self defense', 'shall not be infringed']
            },
            'economy': {
                'liberal_keywords': ['tax the rich', 'minimum wage', 'inequality', 'social programs'],
                'conservative_keywords': ['free market', 'job creators', 'lower taxes', 'small business']
            },
            'covid': {
                'liberal_keywords': ['mask mandate', 'vaccine requirement', 'follow science', 'lockdown'],
                'conservative_keywords': ['personal freedom', 'medical choice', 'economy over fear', 'hoax']
            }
        }
        
        self.emotional_triggers = {
            'anger': ['outraged', 'furious', 'disgusted', 'sick of', 'hate'],
            'fear': ['scared', 'terrified', 'worried', 'threat', 'dangerous'],
            'pride': ['proud', 'patriotic', 'american', 'freedom', 'liberty'],
            'victim': ['oppressed', 'discriminated', 'targeted', 'silenced', 'censored']
        }
        
        self.conspiracy_indicators = [
            'deep state', 'fake news', 'mainstream media', 'they dont want you to know',
            'wake up', 'sheeple', 'conspiracy', 'cover up', 'hidden agenda'
        ]
    
    def extract_political_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract comprehensive political profile from message"""
        profile = {
            'political_leaning': self._detect_political_leaning(message),
            'issue_positions': self._analyze_issue_positions(message),
            'emotional_triggers': self._identify_emotional_triggers(message),
            'conspiracy_susceptibility': self._assess_conspiracy_susceptibility(message),
            'voting_likelihood': self._assess_voting_likelihood(message),
            'influence_vectors': self._identify_influence_vectors(message),
            'manipulation_opportunities': self._identify_political_manipulation(message),
            'radicalization_risk': self._assess_radicalization_risk(message),
            'tribal_loyalty': self._assess_tribal_loyalty(message),
            'media_consumption': self._detect_media_consumption(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _detect_political_leaning(self, message: str) -> Dict:
        """Detect overall political leaning"""
        message_lower = message.lower()
        leaning_scores = {}
        
        for leaning, indicators in self.political_spectrum.items():
            score = 0
            evidence = []
            
            # Check keywords
            for keyword in indicators['keywords']:
                if keyword in message_lower:
                    score += 2
                    evidence.append(f"keyword: {keyword}")
            
            # Check issue positions
            for issue in indicators['issues']:
                if issue in message_lower:
                    score += 3
                    evidence.append(f"issue: {issue}")
            
            if score > 0:
                leaning_scores[leaning] = {
                    'score': score,
                    'evidence': evidence,
                    'confidence': min(score * 10, 95)
                }
        
        # Determine primary leaning
        if leaning_scores:
            primary_leaning = max(leaning_scores.keys(), key=lambda x: leaning_scores[x]['score'])
            return {
                'primary': primary_leaning,
                'all_scores': leaning_scores,
                'strength': 'strong' if leaning_scores[primary_leaning]['score'] >= 5 else 'moderate'
            }
        
        return {'primary': 'unknown', 'all_scores': {}, 'strength': 'none'}
    
    def _analyze_issue_positions(self, message: str) -> Dict:
        """Analyze positions on specific political issues"""
        message_lower = message.lower()
        issue_positions = {}
        
        for issue, positions in self.hot_topics.items():
            liberal_score = 0
            conservative_score = 0
            evidence = []
            
            for keyword in positions['liberal_keywords']:
                if keyword in message_lower:
                    liberal_score += 1
                    evidence.append(f"liberal: {keyword}")
            
            for keyword in positions['conservative_keywords']:
                if keyword in message_lower:
                    conservative_score += 1
                    evidence.append(f"conservative: {keyword}")
            
            if liberal_score > 0 or conservative_score > 0:
                if liberal_score > conservative_score:
                    position = 'liberal'
                    strength = liberal_score
                elif conservative_score > liberal_score:
                    position = 'conservative'
                    strength = conservative_score
                else:
                    position = 'mixed'
                    strength = max(liberal_score, conservative_score)
                
                issue_positions[issue] = {
                    'position': position,
                    'strength': strength,
                    'evidence': evidence
                }
        
        return issue_positions
    
    def _identify_emotional_triggers(self, message: str) -> List[Dict]:
        """Identify emotional triggers in political messages"""
        message_lower = message.lower()
        triggers = []
        
        for emotion, keywords in self.emotional_triggers.items():
            for keyword in keywords:
                if keyword in message_lower:
                    triggers.append({
                        'emotion': emotion,
                        'trigger': keyword,
                        'context': self._extract_context(message, keyword),
                        'manipulation_potential': self._assess_trigger_manipulation_potential(emotion)
                    })
        
        return triggers
    
    def _assess_conspiracy_susceptibility(self, message: str) -> Dict:
        """Assess susceptibility to conspiracy theories"""
        message_lower = message.lower()
        conspiracy_score = 0
        indicators_found = []
        
        for indicator in self.conspiracy_indicators:
            if indicator in message_lower:
                conspiracy_score += 1
                indicators_found.append(indicator)
        
        # Additional conspiracy patterns
        conspiracy_patterns = [
            r'they (?:want|dont want|are trying)',
            r'wake up (?:people|america|sheeple)',
            r'the truth is',
            r'mainstream media (?:lies|wont tell)',
            r'follow the money'
        ]
        
        for pattern in conspiracy_patterns:
            if re.search(pattern, message_lower):
                conspiracy_score += 2
                indicators_found.append(f"pattern: {pattern}")
        
        susceptibility_level = 'none'
        if conspiracy_score >= 5:
            susceptibility_level = 'very_high'
        elif conspiracy_score >= 3:
            susceptibility_level = 'high'
        elif conspiracy_score >= 1:
            susceptibility_level = 'moderate'
        
        return {
            'susceptibility_level': susceptibility_level,
            'conspiracy_score': conspiracy_score,
            'indicators': indicators_found
        }
    
    def _assess_voting_likelihood(self, message: str) -> Dict:
        """Assess likelihood of political engagement/voting"""
        message_lower = message.lower()
        
        high_engagement_keywords = [
            'vote', 'election', 'ballot', 'campaign', 'primary',
            'candidate', 'politician', 'government', 'policy'
        ]
        
        disengagement_keywords = [
            'dont vote', 'politics is pointless', 'all politicians are corrupt',
            'my vote doesnt matter', 'system is rigged'
        ]
        
        engagement_score = sum(1 for keyword in high_engagement_keywords if keyword in message_lower)
        disengagement_score = sum(1 for keyword in disengagement_keywords if keyword in message_lower)
        
        if engagement_score > disengagement_score:
            likelihood = 'high'
        elif disengagement_score > engagement_score:
            likelihood = 'low'
        else:
            likelihood = 'moderate'
        
        return {
            'voting_likelihood': likelihood,
            'engagement_score': engagement_score,
            'disengagement_score': disengagement_score
        }
    
    def _identify_influence_vectors(self, message: str) -> List[str]:
        """Identify what influences this person politically"""
        message_lower = message.lower()
        influence_vectors = []
        
        influence_patterns = {
            'social_media': ['facebook', 'twitter', 'tiktok', 'youtube', 'instagram'],
            'traditional_media': ['cnn', 'fox news', 'msnbc', 'newspaper', 'tv news'],
            'alternative_media': ['podcast', 'blog', 'independent media', 'citizen journalist'],
            'social_circle': ['my friends think', 'everyone i know', 'people are saying'],
            'family': ['my family', 'my parents', 'my spouse'],
            'celebrities': ['celebrity', 'actor', 'musician', 'influencer'],
            'religious': ['church', 'pastor', 'bible', 'faith', 'god']
        }
        
        for vector_type, indicators in influence_patterns.items():
            for indicator in indicators:
                if indicator in message_lower:
                    influence_vectors.append(vector_type)
                    break
        
        return list(set(influence_vectors))
    
    def _identify_political_manipulation(self, message: str) -> List[Dict]:
        """Identify opportunities for political manipulation"""
        opportunities = []
        political_profile = self.extract_political_profile(message, {})
        
        # High conspiracy susceptibility = misinformation targeting
        conspiracy_level = political_profile['conspiracy_susceptibility']['susceptibility_level']
        if conspiracy_level in ['high', 'very_high']:
            opportunities.append({
                'type': 'misinformation_susceptible',
                'strategy': 'conspiracy_content',
                'targeting': 'alternative_facts',
                'effectiveness': 'high'
            })
        
        # Strong emotional triggers = emotional manipulation
        emotional_triggers = political_profile['emotional_triggers']
        if emotional_triggers:
            primary_emotion = max(set([t['emotion'] for t in emotional_triggers]), 
                                key=lambda x: sum(1 for t in emotional_triggers if t['emotion'] == x))
            opportunities.append({
                'type': 'emotional_manipulation',
                'strategy': f'trigger_{primary_emotion}',
                'targeting': 'emotional_response',
                'effectiveness': 'very_high'
            })
        
        # Strong political leaning = echo chamber reinforcement
        leaning_strength = political_profile['political_leaning']['strength']
        if leaning_strength in ['strong', 'moderate']:
            opportunities.append({
                'type': 'echo_chamber',
                'strategy': 'confirmation_bias',
                'targeting': 'reinforce_beliefs',
                'effectiveness': 'high'
            })
        
        return opportunities
    
    def _assess_radicalization_risk(self, message: str) -> Dict:
        """Assess risk of political radicalization"""
        message_lower = message.lower()
        
        radicalization_indicators = {
            'us_vs_them': ['they', 'them', 'enemy', 'traitor', 'destroy'],
            'violence_rhetoric': ['fight', 'war', 'battle', 'crusade', 'eliminate'],
            'dehumanization': ['animals', 'vermin', 'scum', 'evil', 'monsters'],
            'absolutism': ['always', 'never', 'all', 'none', 'everyone'],
            'victimhood': ['under attack', 'being replaced', 'oppressed', 'silenced']
        }
        
        risk_score = 0
        indicators_found = []
        
        for category, keywords in radicalization_indicators.items():
            category_score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    category_score += 1
                    indicators_found.append(f"{category}: {keyword}")
            
            # Weight certain categories higher
            if category in ['violence_rhetoric', 'dehumanization']:
                risk_score += category_score * 3
            else:
                risk_score += category_score
        
        risk_level = 'low'
        if risk_score >= 10:
            risk_level = 'very_high'
        elif risk_score >= 6:
            risk_level = 'high'
        elif risk_score >= 3:
            risk_level = 'moderate'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'indicators': indicators_found
        }
    
    def _assess_tribal_loyalty(self, message: str) -> Dict:
        """Assess strength of tribal/partisan loyalty"""
        message_lower = message.lower()
        
        loyalty_indicators = {
            'strong_identification': ['we', 'us', 'our', 'my party', 'my side'],
            'opposition_hatred': ['hate', 'despise', 'can\'t stand', 'evil', 'stupid'],
            'blind_support': ['always right', 'never wrong', 'trust completely', 'follow anywhere'],
            'purity_tests': ['real', 'true', 'fake', 'rino', 'dino']
        }
        
        loyalty_score = 0
        loyalty_evidence = []
        
        for category, keywords in loyalty_indicators.items():
            for keyword in keywords:
                if keyword in message_lower:
                    loyalty_score += 1
                    loyalty_evidence.append(f"{category}: {keyword}")
        
        loyalty_strength = 'weak'
        if loyalty_score >= 5:
            loyalty_strength = 'very_strong'
        elif loyalty_score >= 3:
            loyalty_strength = 'strong'
        elif loyalty_score >= 1:
            loyalty_strength = 'moderate'
        
        return {
            'loyalty_strength': loyalty_strength,
            'loyalty_score': loyalty_score,
            'evidence': loyalty_evidence
        }
    
    def _detect_media_consumption(self, message: str) -> List[Dict]:
        """Detect media consumption patterns"""
        message_lower = message.lower()
        
        media_sources = {
            'mainstream_liberal': ['cnn', 'msnbc', 'nyt', 'washington post', 'npr'],
            'mainstream_conservative': ['fox news', 'wall street journal', 'new york post'],
            'far_left': ['jacobin', 'the nation', 'democracy now', 'young turks'],
            'far_right': ['breitbart', 'daily wire', 'newsmax', 'oann', 'infowars'],
            'alternative': ['substack', 'podcast', 'youtube', 'rumble', 'bitchute'],
            'social_media': ['facebook', 'twitter', 'tiktok', 'reddit', 'telegram']
        }
        
        media_consumption = []
        
        for category, sources in media_sources.items():
            for source in sources:
                if source in message_lower:
                    media_consumption.append({
                        'category': category,
                        'source': source,
                        'bias_level': self._assess_source_bias(category),
                        'echo_chamber_risk': self._assess_echo_chamber_risk(category)
                    })
        
        return media_consumption
    
    def _extract_context(self, message: str, keyword: str) -> str:
        """Extract context around a keyword"""
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 40)
        end = min(len(message), keyword_pos + len(keyword) + 40)
        
        return message[start:end]
    
    def _assess_trigger_manipulation_potential(self, emotion: str) -> str:
        """Assess manipulation potential of emotional triggers"""
        potential_map = {
            'anger': 'very_high',
            'fear': 'very_high',
            'pride': 'high',
            'victim': 'high'
        }
        return potential_map.get(emotion, 'medium')
    
    def _assess_source_bias(self, category: str) -> str:
        """Assess bias level of media source category"""
        bias_map = {
            'mainstream_liberal': 'left_bias',
            'mainstream_conservative': 'right_bias',
            'far_left': 'extreme_left_bias',
            'far_right': 'extreme_right_bias',
            'alternative': 'variable_bias',
            'social_media': 'algorithm_bias'
        }
        return bias_map.get(category, 'unknown')
    
    def _assess_echo_chamber_risk(self, category: str) -> str:
        """Assess echo chamber risk of media source category"""
        risk_map = {
            'mainstream_liberal': 'moderate',
            'mainstream_conservative': 'moderate',
            'far_left': 'high',
            'far_right': 'high',
            'alternative': 'very_high',
            'social_media': 'very_high'
        }
        return risk_map.get(category, 'unknown')
    
    def calculate_market_value(self, political_profile: Dict) -> float:
        """Calculate market value based on political profile"""
        base_value = 100.0
        
        # Strong political engagement increases value
        leaning_strength = political_profile.get('political_leaning', {}).get('strength', 'none')
        if leaning_strength == 'strong':
            base_value *= 3
        elif leaning_strength == 'moderate':
            base_value *= 2
        
        # Conspiracy susceptibility makes them valuable for misinformation
        conspiracy_level = political_profile.get('conspiracy_susceptibility', {}).get('susceptibility_level', 'none')
        if conspiracy_level == 'very_high':
            base_value *= 5
        elif conspiracy_level == 'high':
            base_value *= 3
        
        # Radicalization risk increases manipulation value
        radicalization_risk = political_profile.get('radicalization_risk', {}).get('risk_level', 'low')
        if radicalization_risk == 'very_high':
            base_value *= 4
        elif radicalization_risk == 'high':
            base_value *= 2.5
        
        # Emotional triggers increase manipulation effectiveness
        emotional_triggers = political_profile.get('emotional_triggers', [])
        if emotional_triggers:
            base_value *= (1 + len(emotional_triggers) * 0.3)
        
        return min(base_value, 2000.0)  # Cap at $2000 per user

# Singleton instance
political_harvester = PoliticalHarvester()