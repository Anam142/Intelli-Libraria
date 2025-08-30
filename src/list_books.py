"""
List all books in the database.
"""
import sqlite3
import os

def list_all_books():
    """List all books in the database."""
    db_path = 'intelli_libraria.db'  # Default database name
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get all tables to check the database structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in database:", [t[0] for t in tables])
        
        # Try to get books from the books table
        try:
            cursor.execute('''
            SELECT title, author, isbn, quantity_total as quantity, 
                   quantity_available as available, branch 
            FROM books 
            ORDER BY title
            ''')
            
            books = cursor.fetchall()
            
            if not books:
                print("\nNo books found in the database.")
                return
            
            print("\nBooks in database:")
            print("=" * 120)
            print(f"{'Title':<60} | {'Author':<30} | {'Available':<8} | {'Total':<5} | {'Branch'}")
            print("-" * 120)
            
            for book in books:
                print(f"{book['title'][:57]:<60} | {book['author'][:28]:<30} | "
                      f"{book['available']:^8} | {book['quantity']:^5} | {book.get('branch', 'N/A')}")
            
            print(f"\nTotal books: {len(books)}")
            
        except sqlite3.OperationalError as e:
            print(f"\nError reading books table: {e}")
            print("The books table might have a different structure or doesn't exist.")
            
    except Exception as e:
        print(f"Error accessing database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    list_all_books()
