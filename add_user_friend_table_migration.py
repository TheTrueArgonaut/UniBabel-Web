"""
Migration: Add UserFriend table for friend management
"""

import sqlite3
from datetime import datetime

def run_migration():
    """Add UserFriend table to database"""
    try:
        # Connect to database
        conn = sqlite3.connect('instance/smartmessenger.db')
        cursor = conn.cursor()
        
        print("🔄 Adding UserFriend table...")
        
        # Create UserFriend table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_friend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                friend_id INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (friend_id) REFERENCES user (id),
                UNIQUE(user_id, friend_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_friend_user_id 
            ON user_friend (user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_friend_friend_id 
            ON user_friend (friend_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_friend_status 
            ON user_friend (status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_friend_user_status 
            ON user_friend (user_id, status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_friend_created_at 
            ON user_friend (created_at)
        """)
        
        # Add last_activity column to user table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE user ADD COLUMN last_activity TIMESTAMP")
            print("✅ Added last_activity column to user table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ last_activity column already exists")
            else:
                raise
        
        # Commit changes
        conn.commit()
        print("✅ UserFriend table created successfully!")
        
        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_friend'")
        result = cursor.fetchone()
        if result:
            print("✅ Migration completed successfully!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(user_friend)")
            columns = cursor.fetchall()
            print("\n📋 UserFriend table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Migration failed - table not found")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()