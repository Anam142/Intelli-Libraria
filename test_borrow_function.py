import sqlite3
from database import borrow_book

def test_borrow_book():
    db_path = 'intelli_libraria_fresh.db'
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Testing Borrow Book Functionality ===\n")
        
        # Get a valid user ID
        cursor.execute("SELECT id, username, status FROM users WHERE status = 'Active' LIMIT 1;")
        user = cursor.fetchone()
        
        if not user:
            print("No active users found. Creating a test user...")
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('testuser', 'test@example.com', 'hashed_password', 'Test User', 'member', 'Active'))
            user_id = cursor.lastrowid
            print(f"Created test user with ID: {user_id}")
            conn.commit()
        else:
            user_id = user[0]
            print(f"Using existing user: ID={user[0]}, Username={user[1]}, Status={user[2]}")
        
        # Get a book with available stock
        cursor.execute("SELECT id, title, stock FROM books WHERE stock > 0 LIMIT 1;")
        book = cursor.fetchone()
        
        if not book:
            print("No books with available stock found. Adding a test book...")
            cursor.execute("""
                INSERT INTO books (title, author, isbn, stock)
                VALUES (?, ?, ?, ?)
            """, ('Test Book', 'Test Author', '1234567890', 1))
            book_id = cursor.lastrowid
            print(f"Created test book with ID: {book_id}")
            conn.commit()
        else:
            book_id = book[0]
            print(f"Using existing book: ID={book[0]}, Title={book[1]}, Stock={book[2]}")
        
        # Test borrowing the book
        print(f"\nAttempting to borrow book ID {book_id} for user ID {user_id}...")
        success, message = borrow_book(user_id, book_id)
        
        print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
        print(f"Message: {message}")
        
        # Show updated book stock
        cursor.execute("SELECT stock FROM books WHERE id = ?", (book_id,))
        new_stock = cursor.fetchone()[0]
        print(f"\nUpdated book stock: {new_stock}")
        
        # Show the transaction
        cursor.execute("""
            SELECT t.id, b.title, u.username, t.issue_date, t.due_date, t.status 
            FROM transactions t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ? AND t.book_id = ?
            ORDER BY t.id DESC
            LIMIT 1
        """, (user_id, book_id))
        
        transaction = cursor.fetchone()
        if transaction:
            print("\nTransaction Details:")
            print(f"  Transaction ID: {transaction[0]}")
            print(f"  Book: {transaction[1]}")
            print(f"  User: {transaction[2]}")
            print(f"  Issue Date: {transaction[3]}")
            print(f"  Due Date: {transaction[4]}")
            print(f"  Status: {transaction[5]}")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_borrow_book()
    input("\nPress Enter to exit...")
