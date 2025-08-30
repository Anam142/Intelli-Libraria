import sqlite3

def check_database_schema():
    db_path = 'intelli_libraria_fresh.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Checking Database Schema ===\n")
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables in database:", ", ".join(tables))
        
        # Check books table
        if 'books' in tables:
            print("\n=== Books Table ===")
            cursor.execute("PRAGMA table_info(books);")
            print("Columns:")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
        
        # Check users table
        if 'users' in tables:
            print("\n=== Users Table ===")
            cursor.execute("PRAGMA table_info(users);")
            print("Columns:")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
        
        # Check transactions table
        if 'transactions' in tables:
            print("\n=== Transactions Table ===")
            cursor.execute("PRAGMA table_info(transactions);")
            print("Columns:")
            for col in cursor.fetchall():
                print(f"  {col[1]} ({col[2]})")
        
        # Check sample data
        if 'books' in tables:
            print("\n=== Sample Books ===")
            cursor.execute("SELECT id, title, author, stock FROM books LIMIT 3;")
            for book in cursor.fetchall():
                print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Stock: {book[3]}")
        
        if 'users' in tables:
            print("\n=== Sample Users ===")
            cursor.execute("SELECT id, username, status FROM users LIMIT 3;")
            for user in cursor.fetchall():
                print(f"ID: {user[0]}, Username: {user[1]}, Status: {user[2]}")
        
        print("\n=== Schema Check Complete ===")
        
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_schema()
    input("\nPress Enter to exit...")
