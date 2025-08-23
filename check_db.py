import sqlite3

def check_database():
    try:
        # Connect to the database
        try:
            from data.database import DB_PATH
        except Exception:
            import os as _os
            DB_PATH = _os.path.join(_os.path.dirname(__file__), 'intelli_libraria.db')
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if books table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Error: 'books' table does not exist in the database.")
            return False
        
        # Get table structure
        cursor.execute('PRAGMA table_info(books)')
        columns = cursor.fetchall()
        print("\nBooks table structure:")
        print("Column Name | Type")
        print("-" * 30)
        for col in columns:
            print(f"{col[1]} | {col[2]}")
        
        # Check if there's any data in the table
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        print(f"\nNumber of books in database: {count}")
        
        if count > 0:
            print("\nFirst 5 books:")
            cursor.execute("SELECT * FROM books LIMIT 5")
            for row in cursor.fetchall():
                print(row)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_database()
