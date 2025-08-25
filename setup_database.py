import os
import sqlite3
from passlib.hash import bcrypt

def setup_database():
    # Remove existing database if it exists
    # Always use the centralized DB path
    from data.database import DB_PATH
        print("Removed existing database")
    
    try:
        # Create new database and tables
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create admin user
        password_hash = bcrypt.hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@intellilibraria.test', password_hash, 'System Administrator', 'admin'))
        
        conn.commit()
        print("✅ Database created successfully!")
        print("✅ Admin user created:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
        # Verify the admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin and bcrypt.verify('admin123', admin[3]):
            print("✅ Login verification successful!")
        else:
            print("❌ Login verification failed!")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Setting up new database...")
    setup_database()
