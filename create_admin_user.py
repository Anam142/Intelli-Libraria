import sqlite3

def create_admin_user():
    try:
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
                phone TEXT,
                role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                status TEXT CHECK(status IN ('Active', 'Inactive')) DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert or update admin user
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (username, email, password, full_name, phone, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin',
            'admin@intellilibraria.test',
            '1234',  # Plain text password for now
            'System Administrator',
            '1234567890',
            'admin',
            'Active'
        ))
        
        conn.commit()
        print("✅ Admin user created/updated successfully!")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Creating admin user...")
    create_admin_user()
