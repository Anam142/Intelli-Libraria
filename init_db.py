#!/usr/bin/env python3
"""
Initialize a fresh database with the admin user.
"""
import os
import sqlite3
from db_utils import DatabaseManager

def main():
    # Remove existing database if it exists
    db_path = 'intelli_libraria.db'
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Removed existing database file.")
            
            # Also remove journal file if it exists
            journal_path = f"{db_path}-journal"
            if os.path.exists(journal_path):
                os.remove(journal_path)
                print("Removed database journal file.")
        except Exception as e:
            print(f"Error removing database files: {e}")
            return
    
    # Create new database
    try:
        db = DatabaseManager()
        print("✅ Created new database")
        
        # Create admin user
        db.create_admin_user('admin123')
        print("✅ Created admin user")
        print("\nLogin with:")
        print("  Username: admin")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    print("🔧 Initializing fresh database...")
    main()
