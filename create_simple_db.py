import sqlite3
import os

def create_simple_db():
    try:
        # Remove existing database if it exists
        if os.path.exists('intelli_libraria.db'):
            os.remove('intelli_libraria.db')
            
        # Create new database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Create users table
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
        print("✅ Database created successfully!")
        print("Login with:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_simple_db()
