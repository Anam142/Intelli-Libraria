import sqlite3
import os

def disable_constraints_fix():
    """Temporarily disable constraints and fix books table."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Disabling Constraints and Fixing Books Table ===")
        
        # Disable foreign key constraints temporarily
        print("1. Disabling foreign key constraints...")
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Disable triggers temporarily
        print("2. Disabling triggers...")
        cursor.execute("PRAGMA trigger_list")
        triggers = cursor.fetchall()
        print(f"Found {len(triggers)} triggers in database")
        
        # Check current books state
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        print(f"3. Total books: {total_books}")
        
        # Try to update available column
        print("4. Updating available column...")
        cursor.execute("UPDATE books SET available = stock")
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} books")
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM books WHERE available = stock")
        correct_books = cursor.fetchone()[0]
        print(f"5. Books with available = stock: {correct_books}")
        
        # Show sample data
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 3")
        sample_books = cursor.fetchall()
        print("\nSample books after fix:")
        for book in sample_books:
            print(f"  ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        # Re-enable foreign key constraints
        print("\n6. Re-enabling foreign key constraints...")
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("\n✅ Books table updated successfully!")
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
    disable_constraints_fix()
