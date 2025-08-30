import sqlite3
import os

def quick_fix():
    try:
        db_path = 'intelli_libraria.db'
        
        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create new database with simple schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with minimal required fields
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        
        # Insert admin user with default credentials
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                      ('admin', '1234'))
        
        conn.commit()
        print("✅ Database reset successfully!")
        print("Login with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    quick_fix()
