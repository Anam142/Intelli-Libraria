import sqlite3
from passlib.hash import bcrypt

def verify_login():
    try:
        # Try to connect to the database
        from data.database import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist!")
            return False
        
        # Check admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Found admin user: {admin}")
        
        # Verify password
        stored_hash = admin[3]  # Assuming password_hash is the 4th column
        if bcrypt.verify('admin123', stored_hash):
            print("✅ Password 'admin123' is correct!")
            return True
        else:
            print("❌ Password 'admin123' is incorrect!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Verifying admin login...")
    verify_login()
