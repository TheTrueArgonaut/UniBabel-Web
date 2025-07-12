"""
Behavior Analyzer Service
Analyzes user behavior to identify high-priority phrases
"""

import sqlite3
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PhraseStats:
    """Phrase statistics data"""
    text: str
    usage_count: int
    unique_users: int
    priority_score: float
    is_cached: bool


class BehaviorAnalyzerService:
    """
    Focused service for analyzing user behavior
    
    Single Responsibility: Phrase usage analysis only
    """
    
    def __init__(self, db_path: str = 'messenger_cache.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.learning_window_days = 7
        self.min_usage_threshold = 10
        self._init_db()
    
    def _init_db(self):
        """Initialize behavior tracking database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Phrase usage tracking (anonymous)
        c.execute('''CREATE TABLE IF NOT EXISTS phrase_usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase_hash TEXT NOT NULL,
            phrase_text TEXT NOT NULL,
            usage_count INTEGER DEFAULT 1,
            unique_users INTEGER DEFAULT 1,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority_score REAL DEFAULT 0.0,
            is_priority_cached BOOLEAN DEFAULT FALSE,
            UNIQUE(phrase_hash)
        )''')
        
        # Daily usage patterns
        c.execute('''CREATE TABLE IF NOT EXISTS daily_usage_patterns (
            usage_date DATE NOT NULL,
            phrase_hash TEXT NOT NULL,
            daily_count INTEGER DEFAULT 1,
            unique_users_today INTEGER DEFAULT 1,
            PRIMARY KEY (usage_date, phrase_hash)
        ) WITHOUT ROWID''')
        
        conn.commit()
        conn.close()
    
    async def analyze_phrase_usage(self, phrase_text: str, user_id: Optional[int] = None) -> bool:
        """
        Analyze and record phrase usage
        
        Args:
            phrase_text: The phrase to analyze
            user_id: User ID (for unique user counting)
            
        Returns:
            True if analysis was successful
        """
        try:
            phrase_hash = hashlib.sha256(phrase_text.encode()).hexdigest()
            today = datetime.now(timezone.utc).date()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Update overall phrase statistics
            c.execute('''INSERT OR REPLACE INTO phrase_usage_stats 
                        (phrase_hash, phrase_text, usage_count, unique_users, last_used)
                        VALUES (?, ?, 
                            COALESCE((SELECT usage_count FROM phrase_usage_stats WHERE phrase_hash = ?), 0) + 1,
                            COALESCE((SELECT unique_users FROM phrase_usage_stats WHERE phrase_hash = ?), 0) + 1,
                            ?)''',
                     (phrase_hash, phrase_text, phrase_hash, phrase_hash, datetime.now(timezone.utc)))
            
            # Update daily usage patterns
            c.execute('''INSERT OR REPLACE INTO daily_usage_patterns
                        (usage_date, phrase_hash, daily_count, unique_users_today)
                        VALUES (?, ?, 
                            COALESCE((SELECT daily_count FROM daily_usage_patterns WHERE usage_date = ? AND phrase_hash = ?), 0) + 1,
                            COALESCE((SELECT unique_users_today FROM daily_usage_patterns WHERE usage_date = ? AND phrase_hash = ?), 0) + 1)''',
                     (today, phrase_hash, today, phrase_hash, today, phrase_hash))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error analyzing phrase usage: {e}")
            return False
    
    async def calculate_priorities(self) -> int:
        """
        Calculate priority scores for all phrases
        
        Returns:
            Number of phrases updated
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            week_ago = datetime.now(timezone.utc) - timedelta(days=self.learning_window_days)
            
            # Get phrases for priority calculation
            c.execute('''
                SELECT 
                    p.phrase_hash,
                    p.phrase_text,
                    p.usage_count,
                    p.unique_users,
                    AVG(d.daily_count) as avg_daily_usage,
                    COUNT(DISTINCT d.usage_date) as active_days
                FROM phrase_usage_stats p
                LEFT JOIN daily_usage_patterns d ON p.phrase_hash = d.phrase_hash
                WHERE p.last_used >= ?
                AND p.usage_count >= ?
                GROUP BY p.phrase_hash, p.phrase_text, p.usage_count, p.unique_users
                ORDER BY p.usage_count DESC
            ''', (week_ago, self.min_usage_threshold))
            
            phrases = c.fetchall()
            updated_count = 0
            
            for phrase_hash, phrase_text, usage_count, unique_users, avg_daily, active_days in phrases:
                # Multi-factor priority scoring
                frequency_score = min(usage_count / 1000.0, 1.0)
                popularity_score = min(unique_users / 100.0, 1.0)
                consistency_score = (active_days or 0) / self.learning_window_days
                recency_score = min((avg_daily or 0) / 50.0, 1.0)
                
                # Weighted priority score
                priority_score = (
                    frequency_score * 0.4 +
                    popularity_score * 0.3 +
                    consistency_score * 0.2 +
                    recency_score * 0.1
                )
                
                # Determine if should be priority cached
                should_cache = priority_score >= 0.4
                
                # Update priority score
                c.execute('''UPDATE phrase_usage_stats 
                            SET priority_score = ?, is_priority_cached = ?
                            WHERE phrase_hash = ?''',
                         (priority_score, should_cache, phrase_hash))
                
                updated_count += 1
            
            conn.commit()
            
            if updated_count > 0:
                self.logger.info(f"Updated priorities for {updated_count} phrases")
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Error calculating priorities: {e}")
            return 0
        finally:
            conn.close()
    
    async def get_priority_phrases(self, limit: int = 50) -> List[Tuple[str, float]]:
        """Get current priority phrases for caching"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''SELECT phrase_text, priority_score 
                         FROM phrase_usage_stats 
                         WHERE is_priority_cached = TRUE
                         ORDER BY priority_score DESC, usage_count DESC
                         LIMIT ?''', (limit,))
            
            return c.fetchall()
            
        finally:
            conn.close()
    
    async def get_phrase_stats(self) -> Dict[str, any]:
        """Get phrase statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''SELECT 
                            COUNT(*) as total_phrases,
                            COUNT(CASE WHEN is_priority_cached THEN 1 END) as cached_phrases,
                            AVG(priority_score) as avg_priority,
                            MAX(priority_score) as max_priority
                         FROM phrase_usage_stats''')
            
            stats = c.fetchone()
            
            return {
                'total_phrases': stats[0] or 0,
                'cached_phrases': stats[1] or 0,
                'avg_priority_score': round(stats[2] or 0, 3),
                'max_priority_score': round(stats[3] or 0, 3)
            }
            
        finally:
            conn.close()
    
    async def get_health_status(self) -> Dict[str, any]:
        """Get service health status"""
        stats = await self.get_phrase_stats()
        
        return {
            'status': 'healthy',
            'total_phrases': stats['total_phrases'],
            'cached_phrases': stats['cached_phrases'],
            'learning_active': stats['total_phrases'] > 0
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Behavior Analyzer Service shutdown complete")


# Global instance
_behavior_analyzer = BehaviorAnalyzerService()


def get_behavior_analyzer() -> BehaviorAnalyzerService:
    """Get the global behavior analyzer instance"""
    return _behavior_analyzer
