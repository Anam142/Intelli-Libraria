import sqlite3
from passlib.hash import bcrypt

def check_admin_account():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table does not exist!")
            return
        
        # Check admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print("❌ Admin user not found!")
            print("\nTo create admin user, run:")
            print("from library_backend import LibraryBackend, UserRole")
            print("lib = LibraryBackend()")
            print("lib.add_user(username='admin', email='admin@intellilibraria.test', password='admin123', full_name='Admin', role='admin')")
            return
        
        print("✅ Admin user found in database")
        print(f"Username: {admin[1]}")
        print(f"Email: {admin[2]}")
        print(f"Full Name: {admin[4]}")
        print(f"Role: {admin[5]}")
        
        # Try to verify the password
        stored_hash = admin[3]  # password_hash is at index 3
        if bcrypt.verify('admin123', stored_hash):
            print("✅ Password 'admin123' is correct!")
        else:
            print("❌ Password 'admin123' is incorrect!")
            print("\nTo reset admin password, run:")
            print("from library_backend import LibraryBackend")
            print("lib = LibraryBackend()")
            print("lib._get_connection().execute(\"UPDATE users SET password_hash=? WHERE username='admin'\", (bcrypt.hash('new_password'),))")
            print("lib._get_connection().commit()")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Checking admin account...")
    check_admin_account()
