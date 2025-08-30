import sqlite3
import os

def fix_db():
    try:
        # Try to find the database
        db_path = None
        possible_paths = [
            'intelli_libraria.db',
            'data/library.db',
            'data/intelli_libraria.db',
            'library.db'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
                
        if not db_path:
            db_path = 'data/library.db'  # Default path if not found
            os.makedirs('data', exist_ok=True)
            
        print(f"Using database at: {os.path.abspath(db_path)}")
        
        # Connect to the database
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
        
        # Simple password hash for '1234'
        password_hash = '$2b$12$N4wVcNgFDZPBzvHNfgRtnebFatDsfoxeapLHl5Nalmey.DbNrBHYm'
        
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
        print("Username: admin")
        print("Password: 1234")
        
        # Verify the user was created
        cursor.execute("SELECT username, email, role, status FROM users WHERE username = 'admin'")
        user = cursor.fetchone()
        if user:
            print("\nUser details:")
            print(f"Username: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"Role: {user[2]}")
            print(f"Status: {user[3]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Running database fix...")
    fix_db()
