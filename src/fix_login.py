import sqlite3

def fix_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            # Create admin user
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@test.com', '1234', 'Admin User', 'admin'))
            print("✅ Created admin user")
        else:
            # Update admin password
            cursor.execute("UPDATE users SET password = '1234' WHERE username = 'admin'")
            print("✅ Reset admin password")
        
        conn.commit()
        print("✅ Database is ready!")
        print("Login with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Fixing login issues...")
    fix_database()
