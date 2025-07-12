"""
Priority Cache Manager Service
Handles instant translation responses for high-priority phrases
"""

import sqlite3
import hashlib
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    phrase_hash: str
    phrase_text: str
    target_lang: str
    translation: str
    priority_score: float
    created_at: datetime
    expires_at: datetime
    uses: int


class PriorityCacheService:
    """
    Microservice for managing priority-based translation caching
    
    Responsibilities:
    - Store and retrieve priority translations
    - Manage cache expiration and cleanup
    - Provide instant responses for common phrases
    - Track cache effectiveness
    """
    
    def __init__(self, db_path: str = 'messenger_cache.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Configuration
        self.CACHE_EXPIRY_HOURS = 24
        self.MAX_CACHE_SIZE = 1000
        
        # DeepL language mapping
        self.DEEPL_LANGUAGE_MAP = {
            'en': 'EN', 'es': 'ES', 'fr': 'FR', 'de': 'DE', 'it': 'IT',
            'pt': 'PT', 'ru': 'RU', 'ja': 'JA', 'ko': 'KO', 'zh': 'ZH',
            'ar': 'AR', 'hi': 'HI', 'tr': 'TR', 'nl': 'NL', 'pl': 'PL',
            'sv': 'SV', 'da': 'DA', 'no': 'NB', 'fi': 'FI', 'el': 'EL',
            'cs': 'CS', 'hu': 'HU', 'ro': 'RO', 'sk': 'SK', 'sl': 'SL',
            'bg': 'BG', 'et': 'ET', 'lv': 'LV', 'lt': 'LT', 'uk': 'UK',
            'id': 'ID', 'ms': 'MS', 'th': 'TH', 'vi': 'VI'
        }
        
        self._init_database()
        
        self.logger.info("⚡ Priority Cache Service initialized")
    
    def _init_database(self):
        """Initialize database tables for priority caching"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Priority cache table
        c.execute('''CREATE TABLE IF NOT EXISTS priority_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_hash TEXT NOT NULL,
            phrase_text TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            translation TEXT NOT NULL,
            priority_score REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            uses INTEGER DEFAULT 0,
            UNIQUE(phrase_hash, target_lang)
        )''')
        
        # Cache effectiveness tracking
        c.execute('''CREATE TABLE IF NOT EXISTS cache_effectiveness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_hash TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            cache_hits INTEGER DEFAULT 0,
            cache_misses INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(phrase_hash, target_lang)
        )''')
        
        conn.commit()
        conn.close()
    
    def normalize_language_code(self, lang_code: str) -> str:
        """Normalize language code to DeepL format"""
        if not lang_code:
            return 'EN'
        
        lang_code = lang_code.lower()
        return self.DEEPL_LANGUAGE_MAP.get(lang_code, 'EN')
    
    async def get_cached_translation(self, phrase_text: str, target_lang: str) -> Optional[str]:
        """
        Get cached translation for a phrase
        
        Args:
            phrase_text: The phrase to translate
            target_lang: Target language code
            
        Returns:
            Cached translation if available, None otherwise
        """
        try:
            target_lang = self.normalize_language_code(target_lang)
            phrase_hash = hashlib.sha256(phrase_text.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if cache is still valid
            now = datetime.now(timezone.utc)
            c.execute('''SELECT translation FROM priority_cache 
                         WHERE phrase_hash=? AND target_lang=? AND expires_at > ?''', 
                     (phrase_hash, target_lang, now))
            result = c.fetchone()
            
            if result:
                # Update usage counter
                c.execute('''UPDATE priority_cache SET uses = uses + 1 
                            WHERE phrase_hash=? AND target_lang=?''',
                         (phrase_hash, target_lang))
                
                # Update cache effectiveness
                c.execute('''INSERT OR REPLACE INTO cache_effectiveness 
                            (phrase_hash, target_lang, cache_hits, last_updated)
                            VALUES (?, ?, 
                                COALESCE((SELECT cache_hits FROM cache_effectiveness 
                                         WHERE phrase_hash=? AND target_lang=?), 0) + 1,
                                ?)''',
                         (phrase_hash, target_lang, phrase_hash, target_lang, now))
                
                conn.commit()
                
                self.logger.debug(f"🔥 Cache hit: {phrase_text} -> {result[0]}")
                return result[0]
            else:
                # Track cache miss
                c.execute('''INSERT OR REPLACE INTO cache_effectiveness 
                            (phrase_hash, target_lang, cache_misses, last_updated)
                            VALUES (?, ?, 
                                COALESCE((SELECT cache_misses FROM cache_effectiveness 
                                         WHERE phrase_hash=? AND target_lang=?), 0) + 1,
                                ?)''',
                         (phrase_hash, target_lang, phrase_hash, target_lang, now))
                conn.commit()
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting cached translation: {e}")
            return None
        finally:
            conn.close()
    
    async def cache_translation(self, phrase_text: str, target_lang: str, 
                              translation: str, priority_score: float) -> bool:
        """
        Cache a translation
        
        Args:
            phrase_text: Original phrase
            target_lang: Target language
            translation: Translated text
            priority_score: Priority score for this phrase
            
        Returns:
            True if cached successfully
        """
        try:
            target_lang = self.normalize_language_code(target_lang)
            phrase_hash = hashlib.sha256(phrase_text.encode()).hexdigest()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.CACHE_EXPIRY_HOURS)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT OR REPLACE INTO priority_cache 
                        (phrase_hash, phrase_text, target_lang, translation, 
                         priority_score, expires_at) 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (phrase_hash, phrase_text, target_lang, translation, 
                      priority_score, expires_at))
            
            conn.commit()
            
            self.logger.debug(f"💾 Cached: {phrase_text} -> {translation} ({target_lang})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching translation: {e}")
            return False
        finally:
            conn.close()
    
    async def get_priority_translation(self, text: str, target_lang: str) -> Optional[str]:
        """Get translation for priority phrase"""
        cache_key = f"priority_{text}_{target_lang}"
        
        # Check if phrase exists in priority cache
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT translation FROM priority_cache 
                     WHERE phrase_text=? AND target_lang=?''', (text, target_lang))
        result = c.fetchone()
        
        if result:
            # Update usage counter
            c.execute('''UPDATE priority_cache SET uses = uses + 1 
                        WHERE phrase_text=? AND target_lang=?''',
                     (text, target_lang))
            
            # Update cache effectiveness
            now = datetime.now(timezone.utc)
            c.execute('''INSERT OR REPLACE INTO cache_effectiveness 
                        (phrase_text, target_lang, cache_hits, last_updated)
                        VALUES (?, ?, 
                            COALESCE((SELECT cache_hits FROM cache_effectiveness 
                                     WHERE phrase_text=? AND target_lang=?), 0) + 1,
                            ?)''',
                     (text, target_lang, text, target_lang, now))
            
            conn.commit()
            
            self.logger.info(f"Priority cache HIT for: {text[:30]}...")
            return result[0]
        else:
            # Track cache miss
            now = datetime.now(timezone.utc)
            c.execute('''INSERT OR REPLACE INTO cache_effectiveness 
                        (phrase_text, target_lang, cache_misses, last_updated)
                        VALUES (?, ?, 
                            COALESCE((SELECT cache_misses FROM cache_effectiveness 
                                     WHERE phrase_text=? AND target_lang=?), 0) + 1,
                            ?)''',
                     (text, target_lang, text, target_lang, now))
            conn.commit()
            
        conn.close()
        return None
    
    async def populate_adaptive_cache(self, target_lang: str, 
                                    priority_phrases: List[tuple] = None) -> Dict[str, Any]:
        """
        Populate cache with priority phrases
        
        Args:
            target_lang: Target language
            priority_phrases: List of (phrase_text, priority_score) tuples
            
        Returns:
            Population status and statistics
        """
        try:
            target_lang = self.normalize_language_code(target_lang)
            
            if not priority_phrases:
                # This would typically get phrases from behavior analyzer
                priority_phrases = await self._get_priority_phrases_from_analyzer()
            
            cached_count = 0
            failed_count = 0
            
            for phrase_text, priority_score in priority_phrases:
                # Check if already cached
                existing = await self.get_cached_translation(phrase_text, target_lang)
                if existing:
                    continue
                
                # Translate and cache (this would use DeepL API)
                translation = await self._translate_with_deepl(phrase_text, target_lang)
                if translation:
                    success = await self.cache_translation(
                        phrase_text, target_lang, translation, priority_score
                    )
                    if success:
                        cached_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
            
            self.logger.info(f"✅ Cache populated for {target_lang}: {cached_count} cached, {failed_count} failed")
            
            return {
                'status': 'completed',
                'language': target_lang,
                'cached_count': cached_count,
                'failed_count': failed_count,
                'total_phrases': len(priority_phrases)
            }
            
        except Exception as e:
            self.logger.error(f"Error populating cache: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _get_priority_phrases_from_analyzer(self) -> List[tuple]:
        """Get priority phrases from behavior analyzer service"""
        # This would typically call the behavior analyzer service
        # For now, return empty list
        return []
    
    async def _translate_with_deepl(self, text: str, target_lang: str) -> Optional[str]:
        """Translate text using DeepL API"""
        # This would integrate with DeepL API
        # Return None if no translation service is available
        self.logger.debug(f"DeepL translation not implemented for: {text}")
        return None
    
    def notify_priority_updates(self):
        """Notification from behavior analyzer about priority updates"""
        self.logger.info("🔔 Received priority update notification")
        # This would trigger cache refresh for updated priorities
        # For now, just log the notification
    
    async def cleanup_expired_cache(self) -> Dict[str, Any]:
        """Clean up expired cache entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            now = datetime.now(timezone.utc)
            
            # Count expired entries
            c.execute('SELECT COUNT(*) FROM priority_cache WHERE expires_at <= ?', (now,))
            expired_count = c.fetchone()[0]
            
            # Remove expired entries
            c.execute('DELETE FROM priority_cache WHERE expires_at <= ?', (now,))
            
            # Clean up old effectiveness tracking
            old_date = now - timedelta(days=30)
            c.execute('DELETE FROM cache_effectiveness WHERE last_updated < ?', (old_date,))
            
            conn.commit()
            
            self.logger.info(f"🧹 Cleaned up {expired_count} expired cache entries")
            
            return {
                'expired_removed': expired_count,
                'cleanup_time': now.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")
            return {'error': str(e)}
        finally:
            conn.close()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get cache size and usage
            c.execute('''SELECT 
                            COUNT(*) as total_entries,
                            SUM(uses) as total_uses,
                            AVG(priority_score) as avg_priority,
                            COUNT(DISTINCT target_lang) as languages_cached
                         FROM priority_cache''')
            
            cache_stats = c.fetchone()
            
            # Get effectiveness stats
            c.execute('''SELECT 
                            SUM(cache_hits) as total_hits,
                            SUM(cache_misses) as total_misses
                         FROM cache_effectiveness''')
            
            effectiveness_stats = c.fetchone()
            
            total_hits = effectiveness_stats[0] or 0
            total_misses = effectiveness_stats[1] or 0
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_entries': cache_stats[0] or 0,
                'total_uses': cache_stats[1] or 0,
                'avg_priority': round(cache_stats[2] or 0, 3),
                'languages_cached': cache_stats[3] or 0,
                'cache_hit_rate': round(hit_rate, 2),
                'total_requests': total_requests,
                'memory_usage_percent': round((cache_stats[0] or 0) / self.MAX_CACHE_SIZE * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}
        finally:
            conn.close()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            stats = await self.get_cache_stats()
            
            return {
                'status': 'healthy',
                'cache_size': stats.get('total_entries', 0),
                'hit_rate': stats.get('cache_hit_rate', 0),
                'memory_usage': stats.get('memory_usage_percent', 0),
                'languages_supported': stats.get('languages_cached', 0),
                'cache_full': stats.get('memory_usage_percent', 0) > 90
            }
            
        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🔄 Shutting down Priority Cache Service...")
        
        # Cleanup expired entries before shutdown
        await self.cleanup_expired_cache()
        
        self.executor.shutdown(wait=True)
        self.logger.info("✅ Priority Cache Service shutdown complete")
