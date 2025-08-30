import sqlite3
import os

def verify_db():
    # Try multiple possible database locations
    possible_paths = [
        os.path.join('data', 'library.db'),
        'intelli_libraria.db',
        os.path.join('data', 'intelli_libraria.db'),
        'library.db'
    ]
    
    for db_path in possible_paths:
        print(f"\nChecking database at: {os.path.abspath(db_path)}")
        if not os.path.exists(db_path):
            print("  - Database file does not exist")
            continue
            
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            print("  - Successfully connected to database")
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("  - ❌ 'users' table not found")
                continue
                
            # Check if admin user exists
            cursor.execute("SELECT username, email, role, status FROM users WHERE username = 'admin'")
            admin = cursor.fetchone()
            
            if admin:
                print("  - ✅ Admin user found:")
                print(f"     Username: {admin[0]}")
                print(f"     Email: {admin[1]}")
                print(f"     Role: {admin[2]}")
                print(f"     Status: {admin[3]}")
                
                # Check if we can log in with default password '1234'
                cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
                pw_hash = cursor.fetchone()[0]
                print("  - Password hash:", pw_hash[:20] + "..." if pw_hash else "No password set")
                
                # Check if there are any books
                cursor.execute("SELECT COUNT(*) FROM books" if 'books' in [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()] else "SELECT 0")
                book_count = cursor.fetchone()[0]
                print(f"  - Number of books in database: {book_count}")
                
                return True
            else:
                print("  - ❌ Admin user not found")
                
        except sqlite3.Error as e:
            print(f"  - ❌ Database error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    print("\n❌ Could not find a valid database with an admin user.")
    print("Please run 'python create_fresh_db.py' to create a new database.")
    return False

if __name__ == "__main__":
    print("🔍 Verifying database connection and admin user...")
    verify_db()
