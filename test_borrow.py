import sqlite3
from datetime import datetime, timedelta

def test_borrow(book_id, user_id):
    conn = sqlite3.connect('intelli_libraria.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check book details
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book = cursor.fetchone()
        print(f"Book details: {dict(book)}" if book else "Book not found")
        if not book:
            return
            
        # Check user exists
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        print(f"User details: {dict(user) if user else 'User not found'}")
        if not user:
            return
        
        # Get current timestamp in SQLite format
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Start transaction
        cursor.execute('BEGIN TRANSACTION')
        
        # Try to update book stock
        cursor.execute('''
            UPDATE books 
            SET stock = stock - 1 
            WHERE id = ? AND stock > 0
        ''', (book_id,))
        
        if cursor.rowcount == 0:
            print("Failed to borrow book: No stock available")
            conn.rollback()
            return
            
        # Insert transaction record with all required fields
        cursor.execute('''
            INSERT INTO transactions 
            (user_id, book_id, issue_date, due_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'Issued', ?, ?)
        ''', (user_id, book_id, now, due_date, now, now))
        
        conn.commit()
        print("\n✅ Book borrowed successfully!")
        print(f"- Book: {book['title']}")
        print(f"- Borrowed by: {user['full_name']}")
        print(f"- Due date: {due_date}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Test Book Borrowing ===")
    try:
        book_id = input("Enter book ID: ").strip()
        user_id = input("Enter user ID: ").strip()
        if not book_id or not user_id:
            print("Error: Book ID and User ID are required")
        else:
            test_borrow(int(book_id), int(user_id))
    except ValueError:
        print("Error: Please enter valid numeric IDs")
    except Exception as e:
        print(f"Unexpected error: {e}")
