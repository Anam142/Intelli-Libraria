import os
import sqlite3

def setup_fresh_db():
    try:
        # Remove existing database if it exists
        db_path = 'intelli_libraria.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Removed existing database")
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with proper schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                status TEXT CHECK(status IN ('Active', 'Inactive')) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create other necessary tables
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
        
        # Create admin user with default credentials
        cursor.execute('''
            INSERT INTO users 
            (username, email, password, full_name, phone, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin',
            'admin@intellilibraria.test',
            '1234',  # Default password
            'System Administrator',
            '1234567890',
            'admin',
            'Active'
        ))
        
        conn.commit()
        print("✅ Database created successfully!")
        print("Admin credentials:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Setting up fresh database...")
    setup_fresh_db()
