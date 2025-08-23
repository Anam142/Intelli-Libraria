import os
import sqlite3
from data.database import DB_PATH

def check_db():
    print(f"Checking database at: {DB_PATH}")
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        print("Database file not found. Creating new database...")
        try:
            # Create database file
            conn = sqlite3.connect(DB_PATH)
            conn.close()
            print("Database file created successfully.")
            
            # Run migrations
            from data.database import Database
            db = Database()
            print("Database migrations applied successfully.")
            
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
    else:
        print("Database file exists.")
        
    # Check users table structure
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        if not columns:
            print("Users table does not exist.")
            return False
            
        print("\nUsers table structure:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # Check for sample data
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\nFound {count} users in the database.")
        
        if count > 0:
            print("\nSample user:")
            cursor.execute("SELECT * FROM users LIMIT 1")
            user = cursor.fetchone()
            print(user)
            
    except Exception as e:
        print(f"Error checking database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            
    return True

if __name__ == "__main__":
    if check_db():
        print("\nDatabase check completed successfully.")
    else:
        print("\nDatabase check failed. Please check the error messages above.")
