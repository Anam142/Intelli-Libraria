import sqlite3
import os

def fix_books_table():
    """Fix the books table by properly setting available column values."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Fixing Books Table ===")
        
        # Check current books table structure
        print("\n1. Checking current books table structure...")
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        print("Columns in books table:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - Default: {col[4]}")
        
        # Check if available column exists and has correct values
        print("\n2. Checking available column values...")
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 5")
        books = cursor.fetchall()
        print("Current books data:")
        for book in books:
            print(f"  ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        # Update available column with stock values
        print("\n3. Updating available column with stock values...")
        cursor.execute("UPDATE books SET available = stock")
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} books.")
        
        # Verify the update
        print("\n4. Verifying the update...")
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 5")
        books = cursor.fetchall()
        print("Books after update:")
        for book in books:
            print(f"  ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        # Check for any triggers that might cause issues
        print("\n5. Checking for triggers on books table...")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='books'")
        triggers = cursor.fetchall()
        if triggers:
            print("Triggers found:")
            for trigger in triggers:
                print(f"  {trigger[0]}: {trigger[1]}")
        else:
            print("No triggers found on books table.")
        
        conn.commit()
        print("\n✅ Books table fixed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_books_table()
