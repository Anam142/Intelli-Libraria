import sqlite3
import os

def create_database():
    try:
        # Remove existing database if it exists
        # Use centralized DB path only; do not remove automatically
        from data.database import DB_PATH
            
        # Create new database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table with required fields
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert admin user
        cursor.execute('''
            INSERT INTO users (username, password, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'admin',
            '1234',  # Plain text for now
            'admin@example.com',
            'System Administrator',
            'admin'
        ))
        
        conn.commit()
        print("✅ Database created successfully!")
        print("Admin user created with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_database()
