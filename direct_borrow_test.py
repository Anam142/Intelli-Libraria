import os
import sqlite3
from datetime import datetime, timedelta

def test_borrow():
    db_path = 'intelli_libraria.db'
    print(f"Testing borrow functionality with database: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Error: Database file does not exist!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Print all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check if transactions table exists
        if 'transactions' not in [t[0] for t in tables]:
            print("\nError: 'transactions' table does not exist!")
            return
        
        # Check transactions table structure
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        print("\nTransactions table columns:", columns)
        
        # Check if we have test data
        cursor.execute("SELECT id, title, available FROM books WHERE id = 1001")
        book = cursor.fetchone()
        if not book:
            print("\nError: Test book not found. Please run verify_and_fix_db.py first.")
            return
            
        print(f"\nTest book found: {book}")
        
        # Try to borrow the book
        user_id = 1001
        book_id = 1001
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        print(f"\nAttempting to borrow book ID {book_id} for user ID {user_id}")
        
        try:
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Check if book is available
            cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
            available = cursor.fetchone()[0]
            
            if available <= 0:
                print("Error: Book is not available for borrowing")
                return
            
            # Create transaction record
            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, due_date, status)
                VALUES (?, ?, ?, 'Borrowed')
            """, (user_id, book_id, due_date))
            
            # Update book availability
            cursor.execute("""
                UPDATE books 
                SET available = available - 1 
                WHERE id = ? AND available > 0
            """, (book_id,))
            
            if cursor.rowcount == 0:
                print("Error: Failed to update book availability")
                conn.rollback()
                return
            
            # Commit the transaction
            conn.commit()
            print("✓ Book borrowed successfully!")
            
            # Show updated book status
            cursor.execute("SELECT id, title, available FROM books WHERE id = ?", (book_id,))
            print("\nUpdated book status:", cursor.fetchone())
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Direct Borrow Test ===\n")
    test_borrow()
