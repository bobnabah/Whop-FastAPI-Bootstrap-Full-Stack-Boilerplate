#!/usr/bin/env python3
"""
Database migration script to add Whop session fields to existing transactions table.
Run this script to update your database schema for session-bound transactions.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new columns for Whop session tracking"""
    
    # Get database path
    db_path = Path(__file__).parent.parent / "test.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        print("Creating new database with updated schema...")
        # The database will be created automatically when the app starts
        return
    
    print(f"Migrating database at {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        if 'whop_session_id' not in columns:
            migrations_needed.append("ALTER TABLE transactions ADD COLUMN whop_session_id VARCHAR")
            
        if 'whop_checkout_url' not in columns:
            migrations_needed.append("ALTER TABLE transactions ADD COLUMN whop_checkout_url VARCHAR")
        
        if migrations_needed:
            print(f"Running {len(migrations_needed)} migrations...")
            
            for migration in migrations_needed:
                print(f"  - {migration}")
                cursor.execute(migration)
            
            # Create indexes for new columns
            try:
                cursor.execute("CREATE INDEX ix_transactions_whop_session_id ON transactions (whop_session_id)")
                print("  - Created index on whop_session_id")
            except sqlite3.OperationalError:
                pass  # Index might already exist
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
        else:
            print("✅ Database is already up to date!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()