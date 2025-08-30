import os
import sqlite3

def check_database():
    # Try multiple possible database locations
    possible_paths = [
        os.path.join('data', 'library.db'),
        'intelli_libraria.db',
        os.path.join('data', 'intelli_libraria.db'),
        'library.db'
    ]
    
    print("🔍 Checking for database files...")
    
    for db_path in possible_paths:
        print(f"\nChecking: {os.path.abspath(db_path)}")
        
        if not os.path.exists(db_path):
            print("  - File does not exist")
            continue
            
        try:
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            print("  - ✅ Connected to database")
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                print("  - ✅ Found 'users' table")
                
                # Count users
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                print(f"  - Total users: {user_count}")
                
                # Check for admin user
                cursor.execute("SELECT username, role, status FROM users WHERE username = 'admin'")
                admin = cursor.fetchone()
                if admin:
                    print(f"  - ✅ Admin user found: {admin}")
                else:
                    print("  - ❌ Admin user not found")
            else:
                print("  - ❌ 'users' table not found")
            
            # List all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\n  📋 Database tables:")
            for table in tables:
                print(f"    - {table[0]}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  - ❌ Database error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    print("\n❌ No valid database found with the expected schema.")
    return False

def check_directories():
    print("\n📂 Checking project structure...")
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    # Check for important directories
    for dir_name in ['data', 'migrations', 'ui']:
        path = os.path.join(cwd, dir_name)
        exists = os.path.isdir(path)
        print(f"  - {dir_name}/: {'✅ Found' if exists else '❌ Missing'}")
    
    # Check for important files
    important_files = ['main.py', 'requirements.txt', 'README.md']
    for file_name in important_files:
        path = os.path.join(cwd, file_name)
        exists = os.path.isfile(path)
        print(f"  - {file_name}: {'✅ Found' if exists else '❌ Missing'}")

if __name__ == "__main__":
    print("🔍 Intelli Libraria Setup Verification")
    print("=" * 40)
    
    db_found = check_database()
    check_directories()
    
    if not db_found:
        print("\n💡 To create a new database, run: python reset_database.py")
    
    print("\nVerification complete!")
