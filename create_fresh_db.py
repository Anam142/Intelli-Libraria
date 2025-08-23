import sqlite3
import os

def create_fresh_db():
    try:
        # Remove existing database if it exists
        db_path = 'intelli_libraria_new.db'
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with minimal schema
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
        print(f"✅ New database created at: {os.path.abspath(db_path)}")
        print("Login with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_fresh_db()
