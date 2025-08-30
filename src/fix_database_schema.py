import sqlite3
import os
from datetime import datetime

def setup_database():
    db_path = 'intelli_libraria.db'
    backup_path = f'intelli_libraria_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    try:
        # Backup existing database if it exists
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✅ Created backup at: {backup_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Drop existing users table if it exists
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create new users table with complete schema
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_code TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                last_login TIMESTAMP,
                status TEXT NOT NULL
            )
        ''')
        
        # Insert default admin user
        # Password: 1234 (hashed with bcrypt)
        cursor.execute('''
            INSERT INTO users (
                user_code, username, password_hash, 
                full_name, email, role, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ADMIN001',
            'admin',
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  # bcrypt hash of '1234'
            'System Administrator',
            'admin@example.com',
            'admin',
            'Active'
        ))
        
        # Create other necessary tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT UNIQUE,
                quantity INTEGER DEFAULT 1,
                available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add more tables as needed...
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        print("\nDefault admin credentials:")
        print("Username: admin")
        print("Password: 1234")
        print("\nPlease change the default password after first login.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists(backup_path):
            print(f"\nA backup was created at: {backup_path}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Setting up database schema...")
    setup_database()
