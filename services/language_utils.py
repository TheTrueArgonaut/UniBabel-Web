"""
Language Utilities for DeepL Pro Integration
🌐 Official DeepL API Language Codes and Utilities
"""

class DeepLLanguageUtils:
    """Utility class for DeepL Pro language management"""
    
    # 🌐 OFFICIAL DEEPL PRO API LANGUAGE CODES
    DEEPL_SOURCE_LANGUAGES = [
        'AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'ES', 'ET', 'FI', 'FR',
        'HE', 'HU', 'ID', 'IT', 'JA', 'KO', 'LT', 'LV', 'NB', 'NL', 'PL',
        'PT', 'RO', 'RU', 'SK', 'SL', 'SV', 'TH', 'TR', 'UK', 'VI', 'ZH'
    ]
    
    DEEPL_TARGET_LANGUAGES = [
        'AR', 'BG', 'CS', 'DA', 'DE', 'EL', 'EN', 'EN-GB', 'EN-US', 'ES', 
        'ES-419', 'ET', 'FI', 'FR', 'HE', 'HU', 'ID', 'IT', 'JA', 'KO', 
        'LT', 'LV', 'NB', 'NL', 'PL', 'PT', 'PT-BR', 'PT-PT', 'RO', 'RU', 
        'SK', 'SL', 'SV', 'TH', 'TR', 'UK', 'VI', 'ZH', 'ZH-HANS', 'ZH-HANT'
    ]
    
    # Next-Generation Models (Latest DeepL Technology)
    NEXT_GEN_LANGUAGES = ['HE', 'TH', 'VI']
    
    # DeepL Write Support (Text Improvement)
    DEEPL_WRITE_LANGUAGES = ['DE', 'EN-GB', 'EN-US', 'ES', 'FR', 'IT', 'PT-BR', 'PT-PT']
    
    # Language Display Names with Native Names
    LANGUAGE_NAMES = {
        'AR': 'Arabic (العربية)',
        'BG': 'Bulgarian (Български)',
        'CS': 'Czech (Čeština)',
        'DA': 'Danish (Dansk)',
        'DE': 'German (Deutsch)',
        'EL': 'Greek (Ελληνικά)',
        'EN': 'English (All variants)',
        'EN-GB': 'English (British)',
        'EN-US': 'English (American)',
        'ES': 'Spanish (Español)',
        'ES-419': 'Spanish (Latin American)',
        'ET': 'Estonian (Eesti)',
        'FI': 'Finnish (Suomi)',
        'FR': 'French (Français)',
        'HE': 'Hebrew (עברית)',
        'HU': 'Hungarian (Magyar)',
        'ID': 'Indonesian (Bahasa Indonesia)',
        'IT': 'Italian (Italiano)',
        'JA': 'Japanese (日本語)',
        'KO': 'Korean (한국어)',
        'LT': 'Lithuanian (Lietuvių)',
        'LV': 'Latvian (Latviešu)',
        'NB': 'Norwegian Bokmål (Norsk bokmål)',
        'NL': 'Dutch (Nederlands)',
        'PL': 'Polish (Polski)',
        'PT': 'Portuguese (Português)',
        'PT-BR': 'Portuguese (Brazilian)',
        'PT-PT': 'Portuguese (European)',
        'RO': 'Romanian (Română)',
        'RU': 'Russian (Русский)',
        'SK': 'Slovak (Slovenčina)',
        'SL': 'Slovenian (Slovenščina)',
        'SV': 'Swedish (Svenska)',
        'TH': 'Thai (ไทย)',
        'TR': 'Turkish (Türkçe)',
        'UK': 'Ukrainian (Українська)',
        'VI': 'Vietnamese (Tiếng Việt)',
        'ZH': 'Chinese (中文)',
        'ZH-HANS': 'Chinese (Simplified) 简体中文',
        'ZH-HANT': 'Chinese (Traditional) 繁體中文'
    }
    
    @classmethod
    def is_valid_source_language(cls, lang_code: str) -> bool:
        """Check if language code is valid for DeepL source"""
        return lang_code in cls.DEEPL_SOURCE_LANGUAGES
    
    @classmethod
    def is_valid_target_language(cls, lang_code: str) -> bool:
        """Check if language code is valid for DeepL target"""
        return lang_code in cls.DEEPL_TARGET_LANGUAGES
    
    @classmethod
    def is_next_gen_language(cls, lang_code: str) -> bool:
        """Check if language uses DeepL's next-generation models"""
        return lang_code in cls.NEXT_GEN_LANGUAGES
    
    @classmethod
    def supports_deepl_write(cls, lang_code: str) -> bool:
        """Check if language supports DeepL Write (text improvement)"""
        return lang_code in cls.DEEPL_WRITE_LANGUAGES
    
    @classmethod
    def get_language_name(cls, lang_code: str) -> str:
        """Get display name for language code"""
        return cls.LANGUAGE_NAMES.get(lang_code, f"Unknown ({lang_code})")
    
    @classmethod
    def get_language_features(cls, lang_code: str) -> dict:
        """Get all features available for a language"""
        return {
            'code': lang_code,
            'name': cls.get_language_name(lang_code),
            'is_source': cls.is_valid_source_language(lang_code),
            'is_target': cls.is_valid_target_language(lang_code),
            'is_next_gen': cls.is_next_gen_language(lang_code),
            'supports_write': cls.supports_deepl_write(lang_code),
            'features': cls._get_feature_list(lang_code)
        }
    
    @classmethod
    def _get_feature_list(cls, lang_code: str) -> list:
        """Get list of features for language"""
        features = []
        
        if cls.is_valid_source_language(lang_code):
            features.append('Source Language')
        
        if cls.is_valid_target_language(lang_code):
            features.append('Target Language')
        
        if cls.is_next_gen_language(lang_code):
            features.append('Next-Generation Model')
        
        if cls.supports_deepl_write(lang_code):
            features.append('DeepL Write Support')
        
        return features
    
    @classmethod
    def get_popular_languages(cls) -> list:
        """Get list of most popular languages for UI"""
        return [
            'EN', 'EN-US', 'EN-GB', 'ES', 'ES-419', 'FR', 'DE', 'IT',
            'PT', 'PT-BR', 'PT-PT', 'RU', 'JA', 'KO', 'ZH', 'ZH-HANS', 'ZH-HANT'
        ]
    
    @classmethod
    def get_all_languages_grouped(cls) -> dict:
        """Get all languages grouped by category for settings UI"""
        return {
            'popular': cls.get_popular_languages(),
            'european': [
                'AR', 'BG', 'CS', 'DA', 'NL', 'ET', 'FI', 'EL', 'HU',
                'LV', 'LT', 'NB', 'PL', 'RO', 'SK', 'SL', 'SV', 'TR', 'UK'
            ],
            'asian_other': ['ID'],
            'next_gen': cls.NEXT_GEN_LANGUAGES,
            'deepl_write': cls.DEEPL_WRITE_LANGUAGES
        }
    
    @classmethod
    def normalize_language_code(cls, lang_code: str) -> str:
        """Normalize language code for DeepL API"""
        if not lang_code:
            return 'EN'
        
        # Convert to uppercase
        normalized = lang_code.upper()
        
        # Handle common variations
        if normalized in ['EN_US', 'EN_GB', 'PT_BR', 'PT_PT', 'ZH_HANS', 'ZH_HANT', 'ES_419']:
            normalized = normalized.replace('_', '-')
        
        # Validate against supported languages
        if cls.is_valid_source_language(normalized) or cls.is_valid_target_language(normalized):
            return normalized
        
        # Default fallback
        return 'EN'
    
    @classmethod
    def get_translation_stats(cls) -> dict:
        """Get statistics about DeepL language support"""
        return {
            'total_source_languages': len(cls.DEEPL_SOURCE_LANGUAGES),
            'total_target_languages': len(cls.DEEPL_TARGET_LANGUAGES),
            'next_gen_languages': len(cls.NEXT_GEN_LANGUAGES),
            'deepl_write_languages': len(cls.DEEPL_WRITE_LANGUAGES),
            'total_language_pairs': len(cls.DEEPL_SOURCE_LANGUAGES) * len(cls.DEEPL_TARGET_LANGUAGES),
            'api_version': 'DeepL Pro API v2'
        }

# Global instance for easy access
deepl_languages = DeepLLanguageUtils()