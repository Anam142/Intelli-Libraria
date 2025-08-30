import sqlite3
import os

def setup_database():
    db_path = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            role TEXT CHECK(role IN ('admin', 'librarian', 'member')) NOT NULL DEFAULT 'member',
            status TEXT CHECK(status IN ('active', 'inactive', 'suspended')) NOT NULL DEFAULT 'active',
            max_books INTEGER NOT NULL DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Clear any existing admin user
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        
        # Insert new admin user
        cursor.execute('''
        INSERT INTO users (user_code, username, email, password_hash, full_name, role, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'USR-000001',
            'admin',
            'admin@lms.test',
            '1234',  # In production, use proper password hashing
            'Admin User',
            'admin',
            'active'
        ))
        
        conn.commit()
        print("✅ Database setup complete!")
        print("Admin credentials:")
        print("👤 Username: admin")
        print("🔑 Password: 1234")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
