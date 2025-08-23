#!/usr/bin/env python3
"""
Simple script to create a fresh database with admin user.
"""
import os
import sqlite3
from auth_utils import get_password_hash

def create_simple_db():
    # Remove existing database if it exists
    db_path = 'intelli_libraria.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"✅ Removed existing database: {db_path}")
        except Exception as e:
            print(f"❌ Could not remove database: {e}")
            print("Please close any applications using the database and try again.")
            return False
    
    try:
        # Create a new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # Create admin user
        admin_password = 'admin123'
        hashed_password = get_password_hash(admin_password)
        
        cursor.execute('''
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
        ''', ('admin', hashed_password, 'System Administrator', 'admin'))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database created successfully!")
        print("\nAdmin login details:")
        print(f"Username: admin")
        print(f"Password: {admin_password}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple Database Setup")
    print("This will create a fresh database with an admin user.\n")
    
    if create_simple_db():
        print("\nYou can now run the application with: python secure_login.py")
    else:
        print("\nFailed to set up the database. Please check the error message above.")
