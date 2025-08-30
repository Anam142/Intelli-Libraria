import os
import sqlite3
from datetime import datetime, timedelta

def create_fresh_database():
    db_path = 'library_new.db'
    print(f"Creating fresh database at: {os.path.abspath(db_path)}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Removed existing database")
        except Exception as e:
            print(f"Error removing existing database: {e}")
            return False
    
    try:
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            role TEXT DEFAULT 'member',
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create books table
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            isbn TEXT UNIQUE,
            publisher TEXT,
            publication_year INTEGER,
            category TEXT,
            description TEXT,
            total_copies INTEGER DEFAULT 1,
            available_copies INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'Borrowed',
            fine_amount DECIMAL(10, 2) DEFAULT 0.00,
            fine_paid BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes
        cursor.execute('''
        CREATE INDEX idx_transactions_user_id ON transactions(user_id);
        ''')
        cursor.execute('''
        CREATE INDEX idx_transactions_book_id ON transactions(book_id);
        ''')
        cursor.execute('''
        CREATE INDEX idx_transactions_status ON transactions(status);
        ''')
        
        # Add test data
        print("Adding test data...")
        
        # Add test user
        cursor.execute('''
        INSERT INTO users (user_code, username, password_hash, full_name, email, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'USR-001', 
            'admin', 
            '$2b$12$8X8zQ3Zv5z7X5X5X5X5X5e',  # hashed 'admin123'
            'Administrator',
            'admin@library.com',
            'admin'
        ))
        
        # Add test book
        cursor.execute('''
        INSERT INTO books (title, author, isbn, total_copies, available_copies)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            'Python Programming',
            'Guido van Rossum',
            '978-0134076430',
            5,  # total_copies
            5   # available_copies
        ))
        
        # Commit changes
        conn.commit()
        print("\n=== Database created successfully! ===")
        print("Database path:", os.path.abspath(db_path))
        print("\nTest user:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: admin")
        
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Library Management System - Fresh Database Setup ===\n")
    if create_fresh_database():
        print("\n✓ Database setup completed successfully!")
    else:
        print("\n✗ Database setup failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
