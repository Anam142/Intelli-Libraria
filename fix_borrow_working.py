import os
import sqlite3
from datetime import datetime, timedelta

def setup_database():
    db_path = 'intelli_libraria.db'
    print(f"Setting up database at: {os.path.abspath(db_path)}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✓ Removed existing database")
        except Exception as e:
            print(f"Error removing database: {e}")
            return False
    
    try:
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create books table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            isbn TEXT UNIQUE,
            stock INTEGER DEFAULT 1,
            available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'Borrowed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )''')
        
        # Add test user
        cursor.execute('''
        INSERT INTO users (id, full_name, email) 
        VALUES (1001, 'Test User', 'test@example.com')
        ''')
        
        # Add test book
        cursor.execute('''
        INSERT INTO books (id, title, author, isbn, stock, available)
        VALUES (1001, 'Python Programming', 'Guido van Rossum', '978-0134076430', 5, 5)
        ''')
        
        conn.commit()
        print("✓ Database setup complete")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_borrow():
    db_path = 'intelli_libraria.db'
    print("\n=== Testing Borrow Functionality ===")
    
    if not os.path.exists(db_path):
        print("Error: Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test data
        user_id = 1001
        book_id = 1001
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        print(f"\nBorrowing Book ID {book_id} for User ID {user_id}")
        
        # Start transaction
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # Check if user exists and is active
            cursor.execute("SELECT status FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                print("Error: User not found")
                return False
                
            if user[0] != 'Active':
                print("Error: User account is not active")
                return False
            
            # Check book availability
            cursor.execute("SELECT available FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                print("Error: Book not found")
                return False
                
            available = book[0]
            if available <= 0:
                print("Error: Book is not available for borrowing")
                return False
            
            # Check if user has already borrowed this book
            cursor.execute("""
                SELECT id FROM transactions 
                WHERE user_id = ? AND book_id = ? AND status = 'Borrowed'
            """, (user_id, book_id))
            
            if cursor.fetchone():
                print("Error: You have already borrowed this book")
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
                WHERE id = ? AND available > 0
            """, (book_id,))
            
            if cursor.rowcount == 0:
                print("Error: Failed to update book availability")
                conn.rollback()
                return False
            
            # Commit the transaction
            conn.commit()
            print("✓ Book borrowed successfully!")
            
            # Show updated status
            cursor.execute("SELECT id, title, available FROM books WHERE id = ?", (book_id,))
            print("\nUpdated book status:", cursor.fetchone())
            
            cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
            print("Transaction record:", cursor.fetchone())
            
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Fixing Borrow Functionality ===\n")
    
    if setup_database():
        print("\n✓ Database setup complete")
        
        # Test the borrow functionality
        if test_borrow():
            print("\n✓ Borrow functionality is working correctly!")
        else:
            print("\n✗ There was an error testing the borrow functionality.")
    else:
        print("\n✗ Failed to set up the database.")
    
    print("\nPress Enter to exit...")
    input()
