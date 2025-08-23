#!/usr/bin/env python3
"""
Reset the database and initialize with a fresh admin user.
"""
import os
import sqlite3
from pathlib import Path

def reset_database():
    db_path = Path(__file__).parent / 'intelli_libraria.db'
    journal_path = Path(f"{db_path}-journal")
    
    # Remove existing database files
    try:
        if db_path.exists():
            db_path.unlink()
            print("✅ Removed existing database file")
        
        if journal_path.exists():
            journal_path.unlink()
            print("✅ Removed database journal file")
            
    except Exception as e:
        print(f"❌ Error removing database files: {e}")
        return False
    
    # Initialize new database
    try:
        from db_utils import DatabaseManager
        db = DatabaseManager()
        if db.create_admin_user('admin123'):
            print("\n✅ Successfully created admin user")
            print("   Username: admin")
            print("   Password: admin123")
            return True
        else:
            print("❌ Failed to create admin user")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Reset and Initialization 🔧")
    print("This will remove all existing data and create a fresh database.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    
    if confirm.lower() == 'y':
        if reset_database():
            print("\n✅ Database reset and initialization completed successfully!")
        else:
            print("\n❌ Failed to reset and initialize the database.")
    else:
        print("\nOperation cancelled.")
