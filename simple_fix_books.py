import sqlite3
import os

def simple_fix_books():
    """Simply update the available column in books table."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Simple Fix for Books Table ===")
        
        # First, let's see what we have
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        print(f"Total books in database: {total_books}")
        
        # Check current available values
        cursor.execute("SELECT COUNT(*) FROM books WHERE available = 0")
        zero_available = cursor.fetchone()[0]
        print(f"Books with available = 0: {zero_available}")
        
        # Simple update without any complex logic
        print("\nUpdating available column...")
        cursor.execute("UPDATE books SET available = stock")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM books WHERE available = stock")
        correct_books = cursor.fetchone()[0]
        print(f"Books with available = stock: {correct_books}")
        
        # Show sample data
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 3")
        sample_books = cursor.fetchall()
        print("\nSample books after fix:")
        for book in sample_books:
            print(f"  ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        conn.commit()
        print("\n✅ Books table updated successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    simple_fix_books()
