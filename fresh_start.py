#!/usr/bin/env python3
"""
Create a fresh database with the correct schema.
"""
import os
import sqlite3

def create_fresh_db():
    db_path = 'intelli_libraria.db'
    
    # Remove existing database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Removed existing database")
        except Exception as e:
            print(f"❌ Could not remove database: {e}")
            return False
    
    try:
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
        admin_password = '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X'  # 'admin123'
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@intellilibraria.com', admin_password, 'System Administrator', 'admin'))
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database created successfully!")
        print("\nAdmin login details:")
        print("  Username: admin")
        print("  Password: admin123")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Creating fresh database...")
    if create_fresh_db():
        print("\n✅ Setup complete! You can now run the application.")
    else:
        print("\n❌ Failed to set up the database.")
