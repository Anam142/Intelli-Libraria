import sqlite3

def fix_users_table():
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist. Creating it...")
            cursor.execute('''
                CREATE TABLE users (
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
            print("✅ Created users table")
        
        # Add missing columns if they don't exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'username' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN username TEXT UNIQUE")
            print("✅ Added username column")
            
        if 'password' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password TEXT NOT NULL DEFAULT '1234'")
            print("✅ Added password column")
            
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'member'")
            print("✅ Added role column")
            
        # Update admin user if it exists
        cursor.execute("UPDATE users SET password='1234', role='admin' WHERE username='admin'")
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Fixing users table...")
    fix_users_table()
