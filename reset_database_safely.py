#!/usr/bin/env python3
"""
Safely reset the database by ensuring all connections are closed first.
"""
import os
import time
import sqlite3

def reset_database():
    db_path = 'intelli_libraria.db'
    
    # Try to remove the database file if it exists
    try:
        if os.path.exists(db_path):
            # Try to delete any existing -journal files
            journal_path = f"{db_path}-journal"
            if os.path.exists(journal_path):
                os.remove(journal_path)
                print(f"Removed journal file: {journal_path}")
                
            # Remove the database file
            os.remove(db_path)
            print(f"Removed database file: {db_path}")
            
            # Wait a moment to ensure the file is fully released
            time.sleep(1)
        
        # Recreate the database with proper schema
        from db_utils import DatabaseManager
        db = DatabaseManager()
        db.create_admin_user('admin123')  # Create admin with default password
        print("\n✅ Successfully reset database with admin user")
        print("   Username: admin")
        print("   Password: admin123")
        
    except PermissionError as e:
        print(f"\n❌ Error: Could not reset database. It might be locked by another process.")
        print("   Please close any other applications using the database and try again.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    print("🔧 Resetting database...")
    print("This will remove all existing data and create a fresh database.")
    confirm = input("Are you sure you want to continue? (y/n): ")
    
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")
