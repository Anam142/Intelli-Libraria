import os
import sqlite3
from datetime import datetime, timedelta

def fix_database():
    db_path = 'intelli_libraria.db'
    print(f"Fixing database at: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Check if transactions table exists and has required columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'available' not in columns:
            print("Adding 'available' column to transactions table...")
            cursor.execute("ALTER TABLE transactions ADD COLUMN available INTEGER DEFAULT 1")
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
        
        # Add test data if needed
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = 1001")
        if cursor.fetchone()[0] == 0:
            print("Adding test user...")
            cursor.execute("""
                INSERT INTO users (id, user_code, full_name, email, role, status)
                VALUES (1001, 'TEST001', 'Test User', 'test@example.com', 'Member', 'Active')
            """)
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE id = 1001")
        if cursor.fetchone()[0] == 0:
            print("Adding test book...")
            cursor.execute("""
                INSERT INTO books (id, title, author, isbn, stock, available)
                VALUES (1001, 'Test Book', 'Test Author', 'TEST1234567890', 5, 5)
            """)
        
        # Commit changes
        conn.commit()
        print("✓ Database fixes applied successfully")
        
        # Show current data
        print("\nTest User:")
        cursor.execute("SELECT id, user_code, full_name, status FROM users WHERE id = 1001")
        print(cursor.fetchone())
        
        print("\nTest Book:")
        cursor.execute("SELECT id, title, stock, available FROM books WHERE id = 1001")
        print(cursor.fetchone())
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_borrow():
    db_path = 'intelli_libraria.db'
    print("\n=== Testing Borrow Functionality ===")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        user_id = 1001
        book_id = 1001
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        print(f"\nBorrowing Book ID {book_id} for User ID {user_id}")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Check book availability
        cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
        available = cursor.fetchone()
        
        if not available or available[0] <= 0:
            print("Error: Book not available for borrowing")
            return False
        
        # Create transaction record
        cursor.execute("""
            INSERT INTO transactions (user_id, book_id, due_date, status)
            VALUES (?, ?, ?, 'Borrowed')
        """, (user_id, book_id, due_date))
        
        # Update book availability
        cursor.execute("""
            UPDATE books 
            SET available = available - 1 
            WHERE id = ?
        """, (book_id,))
        
        if cursor.rowcount == 0:
            print("Error: Failed to update book availability")
            conn.rollback()
            return False
        
        # Commit the transaction
        conn.commit()
        print("✓ Book borrowed successfully!")
        
        # Show updated book status
        cursor.execute("SELECT id, title, available FROM books WHERE id = ?", (book_id,))
        print("\nUpdated book status:", cursor.fetchone())
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Fixing Borrow Functionality ===\n")
    
    if fix_database():
        print("\n=== Testing Borrow Function ===")
        if test_borrow():
            print("\n✓ Borrow functionality is working correctly!")
        else:
            print("\n✗ There was an error testing the borrow functionality.")
    else:
        print("\n✗ Failed to fix the database. Please check the error messages above.")
    
    print("\n=== Test Complete ===")
    input("Press Enter to exit...")
