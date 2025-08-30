import sqlite3
import os

def check_database():
    from data.database import DB_PATH as db_path
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found!")
        return False
    
    try:
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ 'users' table not found in the database!")
            return False
        
        # Check admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print("❌ Admin user not found in the database!")
            return False
        
        print("✅ Database connection successful!")
        print(f"✅ Admin user found: {admin}")
        return True
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Verifying database...")
    check_database()
