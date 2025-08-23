import sqlite3
from passlib.hash import bcrypt

def create_admin():
    db_path = 'intelli_libraria.db'
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hash the password
        password = 'admin123'
        password_hash = bcrypt.hash(password)
        
        # Insert or update admin user
        cursor.execute('''
            INSERT OR REPLACE INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@intellilibraria.test', password_hash, 'System Administrator', 'admin'))
        
        conn.commit()
        print("✅ Admin user created/updated successfully!")
        print(f"Username: admin")
        print(f"Password: {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin()
