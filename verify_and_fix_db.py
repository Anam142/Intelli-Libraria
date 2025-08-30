import sqlite3
import os
from datetime import datetime, timedelta

def verify_and_fix_database():
    db_path = 'intelli_libraria.db'
    print(f"Verifying database at: {os.path.abspath(db_path)}")
    
    # Check if database exists, create if it doesn't
    db_exists = os.path.exists(db_path)
    if not db_exists:
        print("Database not found. Creating a new database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create users table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT UNIQUE,
            full_name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            role TEXT DEFAULT 'Member',
            status TEXT DEFAULT 'Active',
            contact TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create books table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL,
            edition TEXT,
            stock INTEGER NOT NULL DEFAULT 0,
            available INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create transactions table if not exists
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'Borrowed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE
        )
        ''')
        
        # Add test data if database is new
        if not db_exists:
            print("Adding test data...")
            
            # Add test user
            cursor.execute('''
            INSERT INTO users (id, user_code, full_name, email, role, status)
            VALUES (1001, 'USR-001001', 'Test User', 'test@example.com', 'Member', 'Active')
            ''')
            
            # Add test books
            test_books = [
                (1001, 'Introduction to Python', 'Guido van Rossum', '978-0134076430', '1st', 5, 5),
                (1002, 'Clean Code', 'Robert C. Martin', '978-0132350884', '1st', 3, 3),
                (1003, 'Design Patterns', 'Erich Gamma', '978-0201633610', '1st', 2, 2)
            ]
            
            cursor.executemany('''
            INSERT INTO books (id, title, author, isbn, edition, stock, available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', test_books)
            
            print("✓ Test data added successfully")
        
        # Commit changes
        conn.commit()
        print("✓ Database schema is up to date")
        
        # Show current data
        print("\nCurrent Users:")
        cursor.execute("SELECT id, user_code, full_name, status FROM users")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Code: {row[1]}, Name: {row[2]}, Status: {row[3]}")
            
        print("\nCurrent Books:")
        cursor.execute("SELECT id, title, author, available FROM books")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Title: {row[1]}, Author: {row[2]}, Available: {row[3]}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Database Verification and Fix Tool ===\n")
    if verify_and_fix_database():
        print("\n✓ Database is ready for use!")
    else:
        print("\n✗ There were issues with the database setup.")
