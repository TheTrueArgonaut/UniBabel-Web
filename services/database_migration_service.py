"""
Database Migration Service
Handles: Database schema creation, migrations, and validation following SRIMI principles

Single Responsibility: Database schema management only
Reactive: Async-ready migration operations  
Injectable: Clean dependency interfaces
Micro: Focused on database operations only
Interfaces: Clear migration contracts
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import current_app
from models import db
from sqlalchemy import text, inspect
import os


class DatabaseMigrationService:
    """
    Microservice for database schema management
    
    Single Responsibility: Database migrations only
    Under 300 lines: Focused and clean
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.service_name = "DatabaseMigrationService"
        self.version = "1.0.0"
        self.dependencies = []
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        try:
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            return {
                'status': 'healthy',
                'service': self.service_name,
                'version': self.version,
                'database': 'connected',
                'engine': str(db.engine.url).split('@')[0] + '@***'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': self.service_name,
                'error': str(e)
            }
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            exists = table_name in tables
            self.logger.info(f"Table '{table_name}' exists: {exists}")
            return exists
        except Exception as e:
            self.logger.error(f"Error checking table {table_name}: {str(e)}")
            return False
    
    def get_missing_tables(self) -> List[str]:
        """Get list of missing Babel tables"""
        required_tables = [
            'babel_post',
            'babel_like', 
            'babel_comment',
            'babel_follow'
        ]
        
        missing_tables = []
        for table in required_tables:
            if not self.check_table_exists(table):
                missing_tables.append(table)
        
        self.logger.info(f"Missing tables: {missing_tables}")
        return missing_tables
    
    def create_babel_tables(self) -> Dict[str, Any]:
        """Create all Babel-related tables"""
        try:
            missing_tables = self.get_missing_tables()
            if not missing_tables:
                return {
                    'status': 'success',
                    'message': 'All Babel tables already exist',
                    'tables_created': []
                }
            
            created_tables = []
            
            # Create tables in correct order (respecting foreign keys)
            table_creation_order = [
                ('babel_post', self._create_babel_post_table),
                ('babel_like', self._create_babel_like_table),
                ('babel_comment', self._create_babel_comment_table),
                ('babel_follow', self._create_babel_follow_table)
            ]
            
            for table_name, creation_method in table_creation_order:
                if table_name in missing_tables:
                    result = creation_method()
                    if result['success']:
                        created_tables.append(table_name)
                        self.logger.info(f"Created table: {table_name}")
                    else:
                        return {
                            'status': 'error',
                            'message': f'Failed to create table {table_name}',
                            'error': result['error'],
                            'tables_created': created_tables
                        }
            
            return {
                'status': 'success',
                'message': 'Babel tables created successfully',
                'tables_created': created_tables
            }
            
        except Exception as e:
            self.logger.error(f"Error creating Babel tables: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to create Babel tables',
                'error': str(e)
            }
    
    def _create_babel_post_table(self) -> Dict[str, Any]:
        """Create babel_post table"""
        try:
            sql = """
            CREATE TABLE babel_post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                post_type VARCHAR(20) DEFAULT 'text',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                chats_started INTEGER DEFAULT 0,
                is_flagged BOOLEAN DEFAULT FALSE,
                is_approved BOOLEAN DEFAULT TRUE,
                tags TEXT,
                languages VARCHAR(100),
                topics TEXT,
                FOREIGN KEY (user_id) REFERENCES user (id),
                INDEX idx_babel_timeline (created_at, is_approved),
                INDEX idx_babel_user_posts (user_id, created_at),
                INDEX idx_babel_engagement (likes_count, comments_count),
                INDEX idx_babel_type_date (post_type, created_at)
            )
            """
            
            with db.engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error creating babel_post table: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_babel_like_table(self) -> Dict[str, Any]:
        """Create babel_like table"""
        try:
            sql = """
            CREATE TABLE babel_like (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (post_id) REFERENCES babel_post (id) ON DELETE CASCADE,
                UNIQUE (user_id, post_id),
                INDEX idx_babel_like_post (post_id, created_at)
            )
            """
            
            with db.engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error creating babel_like table: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_babel_comment_table(self) -> Dict[str, Any]:
        """Create babel_comment table"""
        try:
            sql = """
            CREATE TABLE babel_comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (post_id) REFERENCES babel_post (id) ON DELETE CASCADE,
                INDEX idx_babel_comment_post (post_id, created_at),
                INDEX idx_babel_comment_user (user_id, created_at)
            )
            """
            
            with db.engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error creating babel_comment table: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_babel_follow_table(self) -> Dict[str, Any]:
        """Create babel_follow table"""
        try:
            sql = """
            CREATE TABLE babel_follow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES user (id),
                FOREIGN KEY (following_id) REFERENCES user (id),
                UNIQUE (follower_id, following_id),
                INDEX idx_babel_follow_follower (follower_id, created_at),
                INDEX idx_babel_follow_following (following_id, created_at)
            )
            """
            
            with db.engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error(f"Error creating babel_follow table: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_tables(self) -> Dict[str, Any]:
        """Verify all Babel tables exist and have correct structure"""
        try:
            inspector = inspect(db.engine)
            verification_results = {}
            
            required_tables = ['babel_post', 'babel_like', 'babel_comment', 'babel_follow']
            
            for table_name in required_tables:
                if self.check_table_exists(table_name):
                    # Get table columns
                    columns = inspector.get_columns(table_name)
                    column_names = [col['name'] for col in columns]
                    
                    # Get indexes
                    indexes = inspector.get_indexes(table_name)
                    index_names = [idx['name'] for idx in indexes]
                    
                    verification_results[table_name] = {
                        'exists': True,
                        'columns': column_names,
                        'indexes': index_names,
                        'column_count': len(column_names)
                    }
                else:
                    verification_results[table_name] = {
                        'exists': False,
                        'error': 'Table does not exist'
                    }
            
            all_exist = all(result['exists'] for result in verification_results.values())
            
            return {
                'status': 'success' if all_exist else 'incomplete',
                'all_tables_exist': all_exist,
                'tables': verification_results,
                'summary': {
                    'total_required': len(required_tables),
                    'existing': sum(1 for r in verification_results.values() if r['exists']),
                    'missing': sum(1 for r in verification_results.values() if not r['exists'])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying tables: {str(e)}")
            return {
                'status': 'error',
                'message': 'Failed to verify tables',
                'error': str(e)
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        try:
            inspector = inspect(db.engine)
            
            return {
                'database_url': str(db.engine.url).split('@')[0] + '@***',
                'dialect': db.engine.dialect.name,
                'driver': db.engine.driver,
                'all_tables': inspector.get_table_names(),
                'table_count': len(inspector.get_table_names()),
                'babel_tables': {
                    'babel_post': self.check_table_exists('babel_post'),
                    'babel_like': self.check_table_exists('babel_like'),
                    'babel_comment': self.check_table_exists('babel_comment'),
                    'babel_follow': self.check_table_exists('babel_follow')
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database info: {str(e)}")
            return {
                'error': str(e),
                'status': 'failed'
            }


# Global instance
_migration_service = DatabaseMigrationService()


def get_migration_service() -> DatabaseMigrationService:
    """Get the global migration service instance"""
    return _migration_service