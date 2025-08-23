#!/usr/bin/env python3
"""
Fix database issues by creating a fresh database with admin user.
"""
import os
import sys
import sqlite3
from pathlib import Path

def create_fresh_db():
    db_path = Path('intelli_libraria.db')
    
    # Close any existing connections
    try:
        conn = sqlite3.connect('file:' + str(db_path) + '?mode=ro', uri=True)
        conn.close()
        print("⚠️  Database is in use. Please close all applications and try again.")
        return False
    except sqlite3.OperationalError:
        # Database is not in use, we can proceed
        pass
    
    try:
        # Remove existing database
        if db_path.exists():
            db_path.unlink()
        
        # Create new database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create admin user with password 'admin123'
        from auth_utils import get_password_hash
        hashed_password = get_password_hash('admin123')
        
        cursor.execute('''
        INSERT OR REPLACE INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
        ''', ('admin', hashed_password, 'System Administrator', 'admin'))
        
        conn.commit()
        conn.close()
        
        print("✅ Created fresh database with admin user")
        print("\nLogin with:")
        print("  Username: admin")
        print("  Password: admin123")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Fix Tool")
    print("This will create a fresh database with an admin user.\n")
    
    if create_fresh_db():
        print("\n✅ Success! You can now run the application.")
    else:
        print("\n❌ Failed to fix the database. Please check the error message above.")
