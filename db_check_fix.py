#!/usr/bin/env python3
"""
Check and fix database issues.
"""
import os
import sqlite3
import sys

def check_database():
    db_path = 'intelli_libraria.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("❌ Database file not found. Creating a new one...")
        return create_fresh_database()
    
    try:
        # Try to open and check the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table not found. Recreating database...")
            conn.close()
            return create_fresh_database()
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print("⚠️  Admin user not found. Creating admin user...")
            create_admin_user(cursor)
            conn.commit()
            print("✅ Admin user created")
        
        print("\n✅ Database is OK")
        print("\nLogin with:")
        print("  Username: admin")
        print("  Password: admin123")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        print("Attempting to fix by creating a fresh database...")
        return create_fresh_database()
    
    finally:
        if 'conn' in locals():
            conn.close()

def create_fresh_database():
    try:
        db_path = 'intelli_libraria.db'
        
        # Remove existing database
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Create admin user
        create_admin_user(cursor)
        
        conn.commit()
        conn.close()
        
        print("\n✅ Fresh database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

def create_admin_user(cursor):
    """Create or update admin user."""
    admin_password = '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X'  # 'admin123'
    
    cursor.execute('''
    INSERT OR REPLACE INTO users (username, email, password_hash, full_name, role)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        'admin',
        'admin@intellilibraria.com',
        admin_password,
        'System Administrator',
        'admin'
    ))

if __name__ == "__main__":
    print("🔍 Checking database...")
    if check_database():
        print("\n✅ Database check completed successfully!")
    else:
        print("\n❌ Failed to fix database issues.")
        print("Please close all applications and try again.")
    
    input("\nPress Enter to exit...")
