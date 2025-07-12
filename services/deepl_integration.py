"""
DeepL Integration Service
Handles DeepL API communication and language mapping
"""

import requests
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class TranslationResult:
    """Translation result structure"""
    text: str
    detected_source_language: str
    target_language: str
    success: bool
    error: Optional[str] = None


class DeepLService:
    """
    Focused service for DeepL API integration
    
    Single Responsibility: DeepL API communication only
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # DeepL Pro API Configuration
        self.api_key = "74732027-e377-4323-8a86-2744ab7ae7ca"
        self.api_url = "https://api.deepl.com/v2/translate"
        self.usage_url = "https://api.deepl.com/v2/usage"
        
        # Language mapping for DeepL Pro
        self.supported_languages = {
            'ar': 'AR',           # Arabic
            'bg': 'BG',           # Bulgarian  
            'zh': 'ZH',           # Chinese (simplified)
            'zh-hans': 'ZH',      # Chinese (simplified)
            'zh-hant': 'ZH-HANT', # Chinese (traditional)
            'cs': 'CS',           # Czech
            'da': 'DA',           # Danish
            'nl': 'NL',           # Dutch
            'en': 'EN',           # English (unspecified variant)
            'en-gb': 'EN-GB',     # English (British)
            'en-us': 'EN-US',     # English (American)
            'et': 'ET',           # Estonian
            'fi': 'FI',           # Finnish
            'fr': 'FR',           # French
            'de': 'DE',           # German
            'el': 'EL',           # Greek
            'hu': 'HU',           # Hungarian
            'id': 'ID',           # Indonesian
            'it': 'IT',           # Italian
            'ja': 'JA',           # Japanese
            'ko': 'KO',           # Korean
            'lv': 'LV',           # Latvian
            'lt': 'LT',           # Lithuanian
            'nb': 'NB',           # Norwegian (Bokmål)
            'pl': 'PL',           # Polish
            'pt': 'PT',           # Portuguese (unspecified variant)
            'pt-br': 'PT-BR',     # Portuguese (Brazilian)
            'pt-pt': 'PT-PT',     # Portuguese (European)
            'ro': 'RO',           # Romanian
            'ru': 'RU',           # Russian
            'sk': 'SK',           # Slovak
            'sl': 'SL',           # Slovenian
            'es': 'ES',           # Spanish
            'sv': 'SV',           # Swedish
            'tr': 'TR',           # Turkish
            'uk': 'UK',           # Ukrainian
        }
        
        self.logger.info("DeepL Pro API Service initialized with full language support")
    
    def normalize_language_code(self, lang_code: str) -> str:
        """Convert language code to DeepL format"""
        if not lang_code:
            return 'EN'
        
        lang_code = lang_code.lower().strip()
        
        # Handle special cases
        if lang_code in ['auto', 'detect']:
            return None  # DeepL auto-detects when source is None
        
        return self.supported_languages.get(lang_code, 'EN')
    
    async def translate_text(self, text: str, target_language: str, 
                           source_language: str = None) -> TranslationResult:
        """
        Translate text using DeepL Pro API
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (None for auto-detection)
            
        Returns:
            TranslationResult with translation and metadata
        """
        try:
            # Normalize language codes
            target_lang = self.normalize_language_code(target_language)
            source_lang = self.normalize_language_code(source_language) if source_language else None
            
            if not target_lang:
                return TranslationResult(
                    text=text,
                    detected_source_language='unknown',
                    target_language=target_language,
                    success=False,
                    error="Unsupported target language"
                )
            
            # Prepare API request
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'UniBabel/1.0'
            }
            
            data = {
                'text': text,
                'target_lang': target_lang,
                'preserve_formatting': '1',
                'formality': 'default'
            }
            
            # Add source language if specified
            if source_lang:
                data['source_lang'] = source_lang
            
            # Make API request
            self.logger.debug(f"Translating: '{text[:50]}...' to {target_lang}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('translations'):
                    translation = result['translations'][0]
                    
                    return TranslationResult(
                        text=translation['text'],
                        detected_source_language=translation.get('detected_source_language', 'unknown'),
                        target_language=target_lang,
                        success=True
                    )
                else:
                    return TranslationResult(
                        text=text,
                        detected_source_language='unknown',
                        target_language=target_language,
                        success=False,
                        error="No translation returned"
                    )
            
            elif response.status_code == 403:
                self.logger.error("DeepL API: Authentication failed - check API key")
                return TranslationResult(
                    text=text,
                    detected_source_language='unknown',
                    target_language=target_language,
                    success=False,
                    error="API authentication failed"
                )
            
            elif response.status_code == 429:
                self.logger.warning("DeepL API: Rate limit exceeded")
                return TranslationResult(
                    text=text,
                    detected_source_language='unknown',
                    target_language=target_language,
                    success=False,
                    error="Rate limit exceeded"
                )
            
            elif response.status_code == 456:
                self.logger.error("DeepL API: Quota exceeded")
                return TranslationResult(
                    text=text,
                    detected_source_language='unknown',
                    target_language=target_language,
                    success=False,
                    error="Monthly quota exceeded"
                )
            
            else:
                self.logger.error(f"DeepL API error: {response.status_code} - {response.text}")
                return TranslationResult(
                    text=text,
                    detected_source_language='unknown',
                    target_language=target_language,
                    success=False,
                    error=f"API error: {response.status_code}"
                )
        
        except requests.exceptions.Timeout:
            self.logger.error("DeepL API request timed out")
            return TranslationResult(
                text=text,
                detected_source_language='unknown',
                target_language=target_language,
                success=False,
                error="Request timeout"
            )
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DeepL API request failed: {e}")
            return TranslationResult(
                text=text,
                detected_source_language='unknown',
                target_language=target_language,
                success=False,
                error=f"Request failed: {str(e)}"
            )
        
        except Exception as e:
            self.logger.error(f"Unexpected error in translation: {e}")
            return TranslationResult(
                text=text,
                detected_source_language='unknown',
                target_language=target_language,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    # Legacy compatibility method
    async def translate(self, text: str, target_lang: str, source_lang: str = None) -> TranslationResult:
        """Legacy translate method for compatibility"""
        return await self.translate_text(text, target_lang, source_lang)
    
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.supported_languages.keys())
    
    async def is_language_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code.lower() in self.supported_languages


# Global instance
_deepl_service = DeepLService()


def get_deepl_service() -> DeepLService:
    """Get the global DeepL service instance"""
    return _deepl_service