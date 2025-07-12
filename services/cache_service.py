"""
Cache Service
Handles translation caching operations
"""

import sqlite3
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry structure"""
    text: str
    translation: str
    language: str
    expires_at: datetime
    uses: int = 0


class CacheService:
    """
    Focused service for caching operations
    
    Single Responsibility: Cache management only
    """
    
    def __init__(self, db_path: str = 'messenger_cache.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.expiry_hours = 24
        self._init_db()
    
    def _init_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Regular translation cache
        c.execute('''CREATE TABLE IF NOT EXISTS translation_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_hash TEXT NOT NULL,
            source_text TEXT NOT NULL,
            target_lang TEXT NOT NULL,
            translation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            uses INTEGER DEFAULT 0,
            UNIQUE(text_hash, target_lang)
        )''')
        
        # Priority cache
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
        
        conn.commit()
        conn.close()
    
    def _get_hash(self, text: str) -> str:
        """Generate hash for text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    async def get_translation(self, text: str, target_lang: str) -> Optional[str]:
        """Get cached translation"""
        text_hash = self._get_hash(text)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            now = datetime.now(timezone.utc)
            c.execute('''SELECT translation FROM translation_cache 
                         WHERE text_hash=? AND target_lang=? AND expires_at > ?''',
                     (text_hash, target_lang, now))
            result = c.fetchone()
            
            if result:
                # Update usage counter
                c.execute('''UPDATE translation_cache SET uses = uses + 1 
                            WHERE text_hash=? AND target_lang=?''',
                         (text_hash, target_lang))
                conn.commit()
                return result[0]
            
            return None
            
        finally:
            conn.close()
    
    async def cache_translation(self, text: str, target_lang: str, translation: str) -> bool:
        """Cache a translation"""
        text_hash = self._get_hash(text)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.expiry_hours)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT OR REPLACE INTO translation_cache 
                         (text_hash, source_text, target_lang, translation, expires_at) 
                         VALUES (?, ?, ?, ?, ?)''',
                     (text_hash, text, target_lang, translation, expires_at))
            conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching translation: {e}")
            return False
        finally:
            conn.close()
    
    async def get_priority_translation(self, text: str, target_lang: str) -> Optional[str]:
        """Get priority cached translation"""
        phrase_hash = self._get_hash(text)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
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
                conn.commit()
                return result[0]
            
            return None
            
        finally:
            conn.close()
    
    async def cache_priority_translation(self, text: str, target_lang: str, 
                                       translation: str, priority_score: float) -> bool:
        """Cache a priority translation"""
        phrase_hash = self._get_hash(text)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.expiry_hours)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT OR REPLACE INTO priority_cache 
                         (phrase_hash, phrase_text, target_lang, translation, 
                          priority_score, expires_at) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                     (phrase_hash, text, target_lang, translation, 
                      priority_score, expires_at))
            conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error caching priority translation: {e}")
            return False
        finally:
            conn.close()
    
    async def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            now = datetime.now(timezone.utc)
            
            # Clean regular cache
            c.execute('DELETE FROM translation_cache WHERE expires_at <= ?', (now,))
            regular_count = c.rowcount
            
            # Clean priority cache
            c.execute('DELETE FROM priority_cache WHERE expires_at <= ?', (now,))
            priority_count = c.rowcount
            
            conn.commit()
            
            total_cleaned = regular_count + priority_count
            if total_cleaned > 0:
                self.logger.info(f"Cleaned {total_cleaned} expired cache entries")
            
            return total_cleaned
            
        finally:
            conn.close()
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Regular cache stats
            c.execute('SELECT COUNT(*), SUM(uses) FROM translation_cache')
            regular_stats = c.fetchone()
            
            # Priority cache stats
            c.execute('SELECT COUNT(*), SUM(uses) FROM priority_cache')
            priority_stats = c.fetchone()
            
            return {
                'regular_cache_size': regular_stats[0] or 0,
                'regular_cache_uses': regular_stats[1] or 0,
                'priority_cache_size': priority_stats[0] or 0,
                'priority_cache_uses': priority_stats[1] or 0,
                'total_size': (regular_stats[0] or 0) + (priority_stats[0] or 0)
            }
            
        finally:
            conn.close()


# Global instance
_cache_service = CacheService()


def get_cache_service() -> CacheService:
    """Get the global cache service instance"""
    return _cache_service