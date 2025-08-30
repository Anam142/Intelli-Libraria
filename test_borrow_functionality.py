import os
import sqlite3
from datetime import datetime, timedelta

def create_test_data():
    """Create test users and books in the database."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intelli_libraria.db')
    print(f"Using database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create test user if not exists
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, full_name, email, role, status)
            VALUES (1001, 'Test User', 'test@example.com', 'Member', 'Active')
        """)
        
        # Create test books if not exist
        test_books = [
            (1001, 'Introduction to Python', 'Guido van Rossum', '978-0134076430', '1st', 5),
            (1002, 'Clean Code', 'Robert C. Martin', '978-0132350884', '1st', 3),
            (1003, 'Design Patterns', 'Erich Gamma', '978-0201633610', '1st', 2)
        ]
        
        for book in test_books:
            cursor.execute("""
                INSERT OR IGNORE INTO books (id, title, author, isbn, edition, stock)
                VALUES (?, ?, ?, ?, ?, ?)
            """, book)
        
        conn.commit()
        print("✓ Test data created successfully")
        
        # Show the test data
        print("\nTest User:")
        cursor.execute("SELECT id, full_name, email, status FROM users WHERE id = 1001")
        print(cursor.fetchone())
        
        print("\nTest Books:")
        cursor.execute("SELECT id, title, stock FROM books WHERE id BETWEEN 1001 AND 1003")
        for row in cursor.fetchall():
            print(row)
            
    except sqlite3.Error as e:
        print(f"Error creating test data: {e}")
    finally:
        conn.close()

def test_borrow():
    """Test the borrow functionality."""
    from database import borrow_book
    
    # Test borrowing a book
    print("\n=== Testing Book Borrowing ===")
    user_id = 1001
    book_id = 1001
    
    print(f"Attempting to borrow book ID {book_id} for user ID {user_id}")
    success, message = borrow_book(user_id, book_id)
    
    if success:
        print(f"✓ Success: {message}")
    else:
        print(f"✗ Failed: {message}")
    
    # Show the updated book stock
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intelli_libraria.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, stock FROM books WHERE id = ?", (book_id,))
    print("\nUpdated book stock:", cursor.fetchone())
    conn.close()

if __name__ == "__main__":
    print("=== Setting up test data ===")
    create_test_data()
    
    print("\n=== Testing borrow functionality ===")
    test_borrow()
    
    print("\nTest completed. Check the database for changes.")
