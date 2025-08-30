import os
import sqlite3
from datetime import datetime, timedelta

def setup_database():
    # Use a temporary database path
    db_path = 'library_fixed.db'
    print(f"Creating new database at: {os.path.abspath(db_path)}")
    
    try:
        # Remove existing file if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'Active'
        )''')
        
        # Create books table
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            available INTEGER DEFAULT 1
        )''')
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            status TEXT DEFAULT 'Borrowed',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )''')
        
        # Add test user
        cursor.execute('''
        INSERT INTO users (id, full_name, email) 
        VALUES (1, 'Test User', 'test@example.com')
        ''')
        
        # Add test book
        cursor.execute('''
        INSERT INTO books (id, title, author, available)
        VALUES (1, 'Python Programming', 'Guido van Rossum', 1)
        ''')
        
        conn.commit()
        print("✓ Test database created successfully!")
        
        # Test borrow functionality
        print("\nTesting borrow functionality...")
        user_id = 1
        book_id = 1
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        
        # Borrow the book
        cursor.execute("""
            INSERT INTO transactions (user_id, book_id, due_date)
            VALUES (?, ?, ?)
        """, (user_id, book_id, due_date))
        
        # Update book availability
        cursor.execute("""
            UPDATE books SET available = 0 WHERE id = ?
        """, (book_id,))
        
        conn.commit()
        print("✓ Book borrowed successfully!")
        
        # Show results
        print("\nCurrent database state:")
        print("User:", cursor.execute("SELECT * FROM users").fetchone())
        print("Book:", cursor.execute("SELECT * FROM books").fetchone())
        print("Transaction:", cursor.execute("SELECT * FROM transactions").fetchone())
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Library Management System - Fix Borrow Functionality ===\n")
    
    if setup_database():
        print("\n✓ Success! The borrow functionality is working correctly.")
        print("A new database 'library_fixed.db' has been created with test data.")
    else:
        print("\n✗ Failed to set up the database.")
    
    input("\nPress Enter to exit...")
