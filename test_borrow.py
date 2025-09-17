import sqlite3
import os
from database import borrow_book

def test_borrow():
    """Test the borrow functionality."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        print("=== Testing Borrow Functionality ===")
        
        # Test borrowing a book
        print("1. Testing borrow_book function...")
        user_id = 3  # Use an existing user ID
        book_id = 60  # Use an existing book ID
        
        print(f"   Attempting to borrow book ID {book_id} for user ID {user_id}")
        
        # Call the borrow function
        success, message = borrow_book(user_id, book_id)
        
        print(f"   Result: {'SUCCESS' if success else 'FAILED'}")
        print(f"   Message: {message}")
        
        # Check the database state after borrowing
        print("\n2. Checking database state after borrowing...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check book availability
        cursor.execute("SELECT id, title, stock, available FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if book:
            print(f"   Book: ID {book[0]}, Title: {book[1]}")
            print(f"   Stock: {book[2]}, Available: {book[3]}")
        
        # Check transaction
        cursor.execute("SELECT id, user_id, book_id, status FROM transactions WHERE book_id = ? ORDER BY id DESC LIMIT 1", (book_id,))
        transaction = cursor.fetchone()
        if transaction:
            print(f"   Transaction: ID {transaction[0]}, User: {transaction[1]}, Book: {transaction[2]}, Status: {transaction[3]}")
        
        conn.close()
        
        print("\n✅ Borrow test completed!")
        return success
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_borrow()
