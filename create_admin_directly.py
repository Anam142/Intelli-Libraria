import sqlite3
from passlib.hash import bcrypt

def create_admin():
    try:
        # Connect to the database
        conn = sqlite3.connect('data/library.db')
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
        
        # Hash the password
        password = '1234'  # Using the password you're trying to use
        password_hash = bcrypt.hash(password)
        
        # Insert or update admin user
        cursor.execute('''
        INSERT OR REPLACE INTO users (
            user_code, username, email, password_hash, 
            full_name, role, status, max_books, phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ADMIN001', 'admin', 'admin@intellilibraria.test', password_hash,
            'System Administrator', 'admin', 'active', 100, '0000000000'
        ))
        
        conn.commit()
        print("✅ Admin user created/updated successfully!")
        print(f"Username: admin")
        print(f"Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin()
