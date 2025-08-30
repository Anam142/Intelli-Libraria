import sqlite3
import os

def rebuild_users_table():
    try:
        db_path = 'intelli_libraria.db'
        backup_path = 'intelli_libraria_backup.db'
        
        # Backup existing database if it exists
        if os.path.exists(db_path):
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.rename(db_path, backup_path)
            print("✅ Created backup of existing database")
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with simplified schema
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create admin user
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', '1234', 'Admin User', 'admin@example.com', 'admin'))
        
        conn.commit()
        print("✅ Created new users table with admin user")
        print("Login with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if os.path.exists(backup_path):
            print("Restoring from backup...")
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rename(backup_path, db_path)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Rebuilding users table...")
    rebuild_users_table()
