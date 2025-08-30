import sqlite3
from datetime import datetime, timedelta

def test_borrow():
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test data
        user_id = 1  # Replace with valid user ID
        book_id = 1  # Replace with valid book ID
        
        print("=== Starting Borrow Test ===")
        
        # 1. Check if user exists
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"Error: User with ID {user_id} not found")
            return
            
        print(f"Found user: {user['username']}")
        
        # 2. Check if book exists and is available
        cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print(f"Error: Book with ID {book_id} not found")
            return
            
        print(f"Found book: {book['title']}")
        
        if book['available_quantity'] <= 0:
            print("Error: Book is not available for borrowing")
            return
            
        # 3. Check user's borrowing limit
        cursor.execute("""
            SELECT COUNT(*) as active_loans 
            FROM transactions 
            WHERE user_id = ? 
            AND status = 'borrowed'
        """, (user_id,))
        
        active_loans = cursor.fetchone()['active_loans']
        max_books = 5  # Default borrowing limit
        
        print(f"Active loans: {active_loans}, Max allowed: {max_books}")
        
        if active_loans >= max_books:
            print(f"Error: Maximum borrowing limit of {max_books} books reached")
            return
            
        # 4. Calculate dates
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 5. Try to update book quantity
        cursor.execute("""
            UPDATE books 
            SET available_quantity = available_quantity - 1,
                updated_at = ?
            WHERE id = ? AND available_quantity > 0
        """, (now, book_id))
        
        if cursor.rowcount == 0:
            print("Error: Failed to update book availability")
            return
            
        # 6. Try to insert transaction with different status values
        status_values = ['borrowed', 'Borrowed', 'BORROWED']
        
        for status in status_values:
            try:
                print(f"\nTrying status: {status!r}")
                cursor.execute("""
                    INSERT INTO transactions 
                    (user_id, book_id, issue_date, due_date, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, book_id, now, due_date, status, now, now))
                
                conn.commit()
                print(f"SUCCESS with status: {status!r}")
                
                # Clean up
                cursor.execute("DELETE FROM transactions WHERE user_id = ? AND book_id = ?", 
                             (user_id, book_id))
                cursor.execute("""
                    UPDATE books 
                    SET available_quantity = available_quantity + 1,
                        updated_at = ?
                    WHERE id = ?
                """, (now, book_id))
                conn.commit()
                
            except sqlite3.IntegrityError as e:
                print(f"FAILED with status {status!r}: {str(e)}")
                conn.rollback()
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()
        print("\nTest completed")

if __name__ == "__main__":
    test_borrow()
