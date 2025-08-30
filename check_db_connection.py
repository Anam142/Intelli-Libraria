import sqlite3
import os

def check_database():
    # Try different possible database locations
    possible_paths = [
        'intelli_libraria.db',
        'data/library.db',
        'library.db',
        os.path.join(os.path.dirname(__file__), 'intelli_libraria.db'),
        os.path.join(os.path.dirname(__file__), 'data', 'library.db')
    ]
    
    for db_path in possible_paths:
        try:
            print(f"Trying database at: {os.path.abspath(db_path)}")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("  - Users table does not exist")
                continue
                
            # Get user count
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"  - Found {user_count} users")
            
            # List all users
            cursor.execute("SELECT id, username, email, role, status FROM users")
            users = cursor.fetchall()
            for user in users:
                print(f"  - User: {user}")
                
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"  - Error: {e}")
            continue
    
    print("\nCould not find or access the database. Please check the following:")
    print("1. Make sure the database file exists in one of these locations:")
    for path in possible_paths:
        print(f"   - {os.path.abspath(path)}")
    print("\n2. Check file permissions")
    print("3. Make sure the database is not locked by another process")
    return False

if __name__ == "__main__":
    print("Checking database connection...\n")
    check_database()
