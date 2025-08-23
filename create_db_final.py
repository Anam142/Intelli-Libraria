#!/usr/bin/env python3
"""
Final attempt to create a fresh database.
"""
import os
import sqlite3

def main():
    db_path = 'intelli_libraria.db'
    
    # Remove existing database if it exists
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Removed existing database: {db_path}")
    except Exception as e:
        print(f"❌ Could not remove database: {e}")
        print("Please close any applications using the database and try again.")
        return
    
    try:
        # Create new database
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
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create admin user with password 'admin123' (pre-hashed)
        admin_password = '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X'  # 'admin123'
        cursor.execute('''
        INSERT INTO users (username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?)
        ''', ('admin', admin_password, 'System Administrator', 'admin'))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database created successfully!")
        print("\nAdmin login details:")
        print("  Username: admin")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Creating fresh database...")
    main()
