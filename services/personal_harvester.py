"""
Personal Data Harvester Microservice 🧛‍♂️👤
SRIMI: Single responsibility for personal information extraction
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PersonalHarvester:
    """Extract personal information for identity profiling and targeting"""
    
    def __init__(self):
        self.age_patterns = [
            r'i am (\d+)',
            r'i\'m (\d+)',
            r'(\d+) years old',
            r'age (\d+)',
            r'born in (\d{4})',
            r'(\d+)yo',
            r'(\d+) year old'
        ]
        
        self.location_patterns = {
            'current': [
                r'i live in (.+)',
                r'i\'m in (.+)',
                r'here in (.+)',
                r'from (.+)',
                r'i\'m from (.+)',
                r'located in (.+)'
            ],
            'travel': [
                r'visiting (.+)',
                r'traveling to (.+)',
                r'vacation in (.+)',
                r'trip to (.+)'
            ],
            'past': [
                r'used to live in (.+)',
                r'grew up in (.+)',
                r'originally from (.+)'
            ]
        }
        
        self.occupation_patterns = [
            r'i work (?:as|at) (.+)',
            r'i\'m a (.+)',
            r'my job (?:is|at) (.+)',
            r'i do (.+) for (?:work|living)',
            r'employed (?:as|at) (.+)',
            r'profession (?:is|as) (.+)',
            r'career in (.+)'
        ]
        
        self.relationship_indicators = {
            'single': ['single', 'alone', 'no boyfriend', 'no girlfriend', 'dating apps'],
            'dating': ['boyfriend', 'girlfriend', 'dating', 'seeing someone', 'partner'],
            'married': ['husband', 'wife', 'married', 'spouse', 'wedding'],
            'divorced': ['divorced', 'ex husband', 'ex wife', 'separated'],
            'complicated': ['it\'s complicated', 'on and off', 'casual', 'friends with benefits']
        }
        
        self.family_indicators = {
            'has_children': ['my kid', 'my children', 'my son', 'my daughter', 'daycare', 'school pickup'],
            'wants_children': ['want kids', 'planning family', 'trying to conceive', 'baby fever'],
            'no_children': ['no kids', 'childfree', 'dont want children', 'career focused'],
            'family_issues': ['family drama', 'toxic family', 'estranged', 'family problems']
        }
        
        self.education_patterns = [
            r'graduated (?:from|at) (.+)',
            r'studied (?:at|in) (.+)',
            r'went to (.+) (?:university|college|school)',
            r'degree (?:in|from) (.+)',
            r'alumni of (.+)',
            r'student at (.+)'
        ]
        
        self.demographic_indicators = {
            'ethnicity': ['asian', 'black', 'white', 'hispanic', 'latino', 'african', 'european', 'middle eastern'],
            'religion': ['christian', 'muslim', 'jewish', 'hindu', 'buddhist', 'atheist', 'agnostic'],
            'sexual_orientation': ['gay', 'lesbian', 'bisexual', 'straight', 'heterosexual', 'lgbtq'],
            'disabilities': ['disabled', 'wheelchair', 'blind', 'deaf', 'autism', 'adhd', 'depression']
        }
    
    def extract_personal_profile(self, message: str, user_metadata: Dict) -> Dict:
        """Extract comprehensive personal information from message"""
        profile = {
            'age_data': self._extract_age_information(message),
            'location_data': self._extract_location_information(message),
            'occupation_data': self._extract_occupation_information(message),
            'relationship_status': self._analyze_relationship_status(message),
            'family_situation': self._analyze_family_situation(message),
            'education_background': self._extract_education_information(message),
            'demographic_markers': self._identify_demographic_markers(message),
            'lifestyle_indicators': self._analyze_lifestyle_indicators(message),
            'social_connections': self._analyze_social_connections(message),
            'personal_interests': self._extract_personal_interests(message),
            'life_events': self._detect_life_events(message),
            'privacy_violations': self._identify_privacy_violations(message),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return profile
    
    def _extract_age_information(self, message: str) -> Dict:
        """Extract age-related information"""
        message_lower = message.lower()
        age_data = {'age': None, 'age_range': None, 'confidence': 0, 'source': None}
        
        # Direct age patterns
        for pattern in self.age_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    if 'born in' in pattern:
                        # Calculate age from birth year
                        birth_year = int(match.group(1))
                        current_year = datetime.now().year
                        age = current_year - birth_year
                    else:
                        age = int(match.group(1))
                    
                    if 13 <= age <= 100:  # Reasonable age range
                        age_data['age'] = age
                        age_data['confidence'] = 95
                        age_data['source'] = 'explicit_mention'
                        break
                except ValueError:
                    continue
        
        # Age range indicators if no explicit age found
        if not age_data['age']:
            age_indicators = {
                'teen': ['teenager', 'high school', 'grade 9', 'grade 10', 'grade 11', 'grade 12'],
                'young_adult': ['college', 'university', 'first job', 'just graduated'],
                'adult': ['career', 'mortgage', 'marriage', 'kids'],
                'middle_aged': ['midlife', 'teenagers', 'empty nest', 'career change'],
                'senior': ['retired', 'retirement', 'grandchildren', 'medicare', 'social security']
            }
            
            for age_range, indicators in age_indicators.items():
                for indicator in indicators:
                    if indicator in message_lower:
                        age_data['age_range'] = age_range
                        age_data['confidence'] = 60
                        age_data['source'] = 'lifestyle_inference'
                        break
        
        return age_data
    
    def _extract_location_information(self, message: str) -> Dict:
        """Extract location information"""
        message_lower = message.lower()
        location_data = {'current': [], 'past': [], 'travel': [], 'specificity': 'unknown'}
        
        for location_type, patterns in self.location_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, message_lower)
                for match in matches:
                    # Clean up the location
                    location = match.strip().split('.')[0].split(',')[0]
                    if len(location) > 2:  # Avoid single letters
                        location_data[location_type].append({
                            'location': location,
                            'context': self._extract_context(message, location),
                            'specificity': self._assess_location_specificity(location)
                        })
        
        # Determine overall specificity
        all_locations = location_data['current'] + location_data['past'] + location_data['travel']
        if all_locations:
            specificities = [loc['specificity'] for loc in all_locations]
            if 'address' in specificities:
                location_data['specificity'] = 'address'
            elif 'city' in specificities:
                location_data['specificity'] = 'city'
            elif 'state' in specificities:
                location_data['specificity'] = 'state'
            else:
                location_data['specificity'] = 'country'
        
        return location_data
    
    def _extract_occupation_information(self, message: str) -> Dict:
        """Extract occupation and career information"""
        message_lower = message.lower()
        occupation_data = {'current_job': None, 'industry': None, 'employment_status': 'unknown', 'career_details': []}
        
        # Current occupation
        for pattern in self.occupation_patterns:
            match = re.search(pattern, message_lower)
            if match:
                job = match.group(1).strip()
                occupation_data['current_job'] = job
                occupation_data['industry'] = self._categorize_industry(job)
                break
        
        # Employment status indicators
        employment_indicators = {
            'employed': ['work at', 'my job', 'office', 'colleagues', 'boss'],
            'unemployed': ['unemployed', 'looking for work', 'job hunting', 'laid off'],
            'student': ['student', 'studying', 'school', 'university', 'college'],
            'retired': ['retired', 'retirement', 'pension'],
            'freelance': ['freelance', 'contractor', 'self employed', 'own business']
        }
        
        for status, indicators in employment_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    occupation_data['employment_status'] = status
                    break
        
        # Career-related details
        career_keywords = [
            'promotion', 'raise', 'salary', 'overtime', 'commute', 'workplace',
            'coworkers', 'manager', 'deadline', 'project', 'meeting'
        ]
        
        for keyword in career_keywords:
            if keyword in message_lower:
                occupation_data['career_details'].append({
                    'keyword': keyword,
                    'context': self._extract_context(message, keyword)
                })
        
        return occupation_data
    
    def _analyze_relationship_status(self, message: str) -> Dict:
        """Analyze relationship status and dating life"""
        message_lower = message.lower()
        relationship_data = {'status': 'unknown', 'evidence': [], 'relationship_goals': [], 'dating_struggles': []}
        
        # Determine relationship status
        status_scores = {}
        for status, indicators in self.relationship_indicators.items():
            score = 0
            evidence = []
            for indicator in indicators:
                if indicator in message_lower:
                    score += 1
                    evidence.append(indicator)
            
            if score > 0:
                status_scores[status] = {'score': score, 'evidence': evidence}
        
        if status_scores:
            primary_status = max(status_scores.keys(), key=lambda x: status_scores[x]['score'])
            relationship_data['status'] = primary_status
            relationship_data['evidence'] = status_scores[primary_status]['evidence']
        
        # Relationship goals and struggles
        relationship_goals = [
            'want relationship', 'looking for love', 'ready to settle', 'marriage goals',
            'find someone', 'relationship material', 'serious relationship'
        ]
        
        dating_struggles = [
            'dating is hard', 'cant find anyone', 'bad dates', 'dating apps suck',
            'all the good ones are taken', 'relationship problems', 'trust issues'
        ]
        
        for goal in relationship_goals:
            if goal in message_lower:
                relationship_data['relationship_goals'].append(goal)
        
        for struggle in dating_struggles:
            if struggle in message_lower:
                relationship_data['dating_struggles'].append(struggle)
        
        return relationship_data
    
    def _analyze_family_situation(self, message: str) -> Dict:
        """Analyze family situation and children status"""
        message_lower = message.lower()
        family_data = {'children_status': 'unknown', 'family_relationships': [], 'family_issues': []}
        
        # Children status
        children_scores = {}
        for status, indicators in self.family_indicators.items():
            score = sum(1 for indicator in indicators if indicator in message_lower)
            if score > 0:
                children_scores[status] = score
        
        if children_scores:
            primary_status = max(children_scores.keys(), key=lambda x: children_scores[x])
            family_data['children_status'] = primary_status
        
        # Family relationships
        family_mentions = [
            'my mom', 'my dad', 'my parents', 'my sister', 'my brother',
            'my grandmother', 'my grandfather', 'my aunt', 'my uncle'
        ]
        
        for mention in family_mentions:
            if mention in message_lower:
                family_data['family_relationships'].append({
                    'relationship': mention,
                    'context': self._extract_context(message, mention)
                })
        
        return family_data
    
    def _extract_education_information(self, message: str) -> Dict:
        """Extract education background"""
        message_lower = message.lower()
        education_data = {'institutions': [], 'level': 'unknown', 'fields_of_study': []}
        
        # Educational institutions
        for pattern in self.education_patterns:
            matches = re.findall(pattern, message_lower)
            for match in matches:
                institution = match.strip()
                education_data['institutions'].append({
                    'institution': institution,
                    'type': self._categorize_institution_type(institution)
                })
        
        # Education level indicators
        education_levels = {
            'high_school': ['high school', 'secondary school', 'diploma'],
            'college': ['college', 'university', 'bachelor', 'undergraduate'],
            'graduate': ['masters', 'phd', 'doctorate', 'graduate school'],
            'professional': ['law school', 'medical school', 'mba', 'professional degree']
        }
        
        for level, indicators in education_levels.items():
            for indicator in indicators:
                if indicator in message_lower:
                    education_data['level'] = level
                    break
        
        return education_data
    
    def _identify_demographic_markers(self, message: str) -> Dict:
        """Identify demographic markers"""
        message_lower = message.lower()
        demographics = {}
        
        for category, indicators in self.demographic_indicators.items():
            found_indicators = []
            for indicator in indicators:
                if indicator in message_lower:
                    found_indicators.append({
                        'marker': indicator,
                        'context': self._extract_context(message, indicator)
                    })
            
            if found_indicators:
                demographics[category] = found_indicators
        
        return demographics
    
    def _analyze_lifestyle_indicators(self, message: str) -> Dict:
        """Analyze lifestyle indicators"""
        message_lower = message.lower()
        
        lifestyle_categories = {
            'fitness': ['gym', 'workout', 'exercise', 'running', 'yoga', 'fitness'],
            'social': ['party', 'friends', 'social', 'nightlife', 'bars', 'clubs'],
            'homebody': ['netflix', 'home', 'indoors', 'cozy', 'quiet night'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure'],
            'food': ['cooking', 'restaurant', 'foodie', 'eating', 'cuisine'],
            'tech': ['technology', 'coding', 'computer', 'gaming', 'tech'],
            'creative': ['art', 'music', 'writing', 'creative', 'artistic']
        }
        
        lifestyle_data = {}
        for category, keywords in lifestyle_categories.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                lifestyle_data[category] = score
        
        return lifestyle_data
    
    def _analyze_social_connections(self, message: str) -> Dict:
        """Analyze social connections and network"""
        message_lower = message.lower()
        
        social_indicators = {
            'large_network': ['lots of friends', 'social circle', 'popular', 'party person'],
            'small_network': ['few friends', 'close friends', 'small circle', 'selective'],
            'isolated': ['no friends', 'alone', 'isolated', 'loner', 'antisocial'],
            'family_oriented': ['family first', 'close family', 'family time'],
            'work_focused': ['work friends', 'colleagues', 'professional network']
        }
        
        social_data = {}
        for network_type, indicators in social_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    social_data[network_type] = True
                    break
        
        return social_data
    
    def _extract_personal_interests(self, message: str) -> List[str]:
        """Extract personal interests and hobbies"""
        message_lower = message.lower()
        
        interest_keywords = [
            'hobby', 'passion', 'love', 'enjoy', 'interested in', 'fan of',
            'favorite', 'obsessed with', 'into', 'really like'
        ]
        
        interests = []
        for keyword in interest_keywords:
            if keyword in message_lower:
                # Try to extract what follows the keyword
                pattern = rf'{keyword} (.+?)(?:\.|,|!|\?|$)'
                match = re.search(pattern, message_lower)
                if match:
                    interest = match.group(1).strip()
                    interests.append(interest)
        
        return interests
    
    def _detect_life_events(self, message: str) -> List[Dict]:
        """Detect major life events"""
        message_lower = message.lower()
        
        life_events = {
            'graduation': ['graduated', 'graduation', 'diploma', 'degree'],
            'job_change': ['new job', 'started work', 'got hired', 'job change'],
            'moving': ['moved', 'moving', 'new place', 'relocating'],
            'relationship_change': ['got married', 'engaged', 'divorced', 'breakup'],
            'health_events': ['surgery', 'diagnosis', 'hospital', 'medical'],
            'family_events': ['baby', 'pregnant', 'birth', 'death', 'funeral']
        }
        
        detected_events = []
        for event_type, indicators in life_events.items():
            for indicator in indicators:
                if indicator in message_lower:
                    detected_events.append({
                        'event_type': event_type,
                        'indicator': indicator,
                        'context': self._extract_context(message, indicator),
                        'recency': self._assess_event_recency(message, indicator)
                    })
        
        return detected_events
    
    def _identify_privacy_violations(self, message: str) -> List[Dict]:
        """Identify potential privacy violations (oversharing)"""
        message_lower = message.lower()
        
        privacy_violations = []
        
        # Sensitive information patterns
        sensitive_patterns = {
            'phone_number': r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',
            'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'address': r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr))',
            'ssn': r'(\d{3}[-.\s]?\d{2}[-.\s]?\d{4})',
            'credit_card': r'(\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4})'
        }
        
        for violation_type, pattern in sensitive_patterns.items():
            matches = re.findall(pattern, message_lower)
            for match in matches:
                privacy_violations.append({
                    'type': violation_type,
                    'data': match,
                    'severity': 'high'
                })
        
        # Oversharing indicators
        oversharing_indicators = [
            'social security', 'bank account', 'password', 'pin number',
            'medical record', 'therapy', 'prescription', 'mental health'
        ]
        
        for indicator in oversharing_indicators:
            if indicator in message_lower:
                privacy_violations.append({
                    'type': 'oversharing',
                    'indicator': indicator,
                    'severity': 'medium'
                })
        
        return privacy_violations
    
    def _extract_context(self, message: str, keyword: str) -> str:
        """Extract context around a keyword"""
        message_lower = message.lower()
        keyword_pos = message_lower.find(keyword)
        
        if keyword_pos == -1:
            return ""
        
        start = max(0, keyword_pos - 30)
        end = min(len(message), keyword_pos + len(keyword) + 30)
        
        return message[start:end]
    
    def _assess_location_specificity(self, location: str) -> str:
        """Assess how specific a location is"""
        location_lower = location.lower()
        
        # Check for specific address indicators
        address_indicators = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr']
        if any(indicator in location_lower for indicator in address_indicators):
            return 'address'
        
        # Check for city indicators
        if any(word in location_lower for word in ['city', 'town', 'village']):
            return 'city'
        
        # Check for state/province indicators
        state_indicators = ['state', 'province', 'territory']
        if any(indicator in location_lower for indicator in state_indicators):
            return 'state'
        
        # Check for country indicators
        countries = ['usa', 'america', 'canada', 'uk', 'england', 'france', 'germany']
        if any(country in location_lower for country in countries):
            return 'country'
        
        return 'unknown'
    
    def _categorize_industry(self, job: str) -> str:
        """Categorize job into industry"""
        job_lower = job.lower()
        
        industries = {
            'technology': ['developer', 'programmer', 'engineer', 'tech', 'software', 'it'],
            'healthcare': ['doctor', 'nurse', 'medical', 'healthcare', 'physician'],
            'education': ['teacher', 'professor', 'educator', 'tutor', 'academic'],
            'finance': ['banker', 'accountant', 'financial', 'analyst', 'finance'],
            'retail': ['sales', 'cashier', 'retail', 'store', 'shop'],
            'service': ['server', 'waiter', 'customer service', 'hospitality'],
            'government': ['government', 'public', 'civil service', 'municipal'],
            'creative': ['artist', 'designer', 'writer', 'creative', 'media']
        }
        
        for industry, keywords in industries.items():
            if any(keyword in job_lower for keyword in keywords):
                return industry
        
        return 'other'
    
    def _categorize_institution_type(self, institution: str) -> str:
        """Categorize educational institution type"""
        institution_lower = institution.lower()
        
        if any(word in institution_lower for word in ['university', 'college']):
            return 'university'
        elif any(word in institution_lower for word in ['high school', 'secondary']):
            return 'high_school'
        elif any(word in institution_lower for word in ['elementary', 'primary']):
            return 'elementary'
        else:
            return 'other'
    
    def _assess_event_recency(self, message: str, indicator: str) -> str:
        """Assess how recent a life event was"""
        message_lower = message.lower()
        
        recent_indicators = ['just', 'recently', 'yesterday', 'last week', 'this week']
        past_indicators = ['years ago', 'long time ago', 'back then', 'used to']
        
        # Look for recency indicators near the event
        context = self._extract_context(message, indicator)
        
        if any(recent in context for recent in recent_indicators):
            return 'recent'
        elif any(past in context for past in past_indicators):
            return 'past'
        else:
            return 'unknown'
    
    def calculate_market_value(self, personal_profile: Dict) -> float:
        """Calculate market value based on personal profile"""
        base_value = 80.0
        
        # Age data increases targeting value
        if personal_profile.get('age_data', {}).get('age'):
            base_value *= 1.5
        
        # Specific location data is very valuable
        location_specificity = personal_profile.get('location_data', {}).get('specificity', 'unknown')
        if location_specificity == 'address':
            base_value *= 10
        elif location_specificity == 'city':
            base_value *= 3
        elif location_specificity == 'state':
            base_value *= 2
        
        # Occupation data increases value
        if personal_profile.get('occupation_data', {}).get('current_job'):
            base_value *= 2
        
        # Relationship status adds targeting value
        if personal_profile.get('relationship_status', {}).get('status') != 'unknown':
            base_value *= 1.5
        
        # Privacy violations are goldmines
        privacy_violations = personal_profile.get('privacy_violations', [])
        if privacy_violations:
            base_value *= (1 + len(privacy_violations) * 2)
        
        return min(base_value, 3000.0)  # Cap at $3000 per user

# Singleton instance
personal_harvester = PersonalHarvester()