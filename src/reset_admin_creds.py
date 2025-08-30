import sqlite3
import os

def reset_admin():
    try:
        db_path = 'intelli_libraria.db'
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing users table if it exists
        cursor.execute("DROP TABLE IF EXISTS users")
        
        # Create new users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # Insert admin user
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      ('admin', '1234'))
        
        conn.commit()
        print("✅ Admin credentials reset successfully!")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    reset_admin()
