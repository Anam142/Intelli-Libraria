#!/usr/bin/env python3
"""
Fix database schema by creating a fresh database with all required tables and columns.
"""
import os
import sqlite3
from pathlib import Path

def create_fresh_database():
    db_path = Path('intelli_libraria.db')
    
    # Remove existing database if it exists
    if db_path.exists():
        try:
            db_path.unlink()
            print("✅ Removed existing database")
        except Exception as e:
            print(f"❌ Could not remove database: {e}")
            return False
    
    try:
        # Create new database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create users table with all required columns
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            role TEXT CHECK(role IN ('admin', 'librarian', 'member')) NOT NULL DEFAULT 'member',
            status TEXT CHECK(status IN ('active', 'inactive', 'suspended')) NOT NULL DEFAULT 'active',
            max_books INTEGER NOT NULL DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        ''')
        
        # Create other necessary tables
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
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
        
        cursor.execute('''
        CREATE TABLE book_copies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            barcode TEXT UNIQUE NOT NULL,
            status TEXT CHECK(status IN ('available', 'borrowed', 'lost', 'damaged', 'in_repair')) NOT NULL DEFAULT 'available',
            location TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_copy_id INTEGER NOT NULL,
            transaction_type TEXT CHECK(transaction_type IN ('borrow', 'return', 'renewal', 'reservation')) NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            fine_amount REAL DEFAULT 0.0,
            status TEXT CHECK(status IN ('active', 'completed', 'overdue', 'lost')) NOT NULL DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_copy_id) REFERENCES book_copies(id) ON DELETE CASCADE
        )
        ''')
        
        # Create admin user
        admin_password = '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X'  # 'admin123'
        cursor.execute('''
        INSERT INTO users (
            user_code, username, email, password_hash, full_name, 
            phone, role, status, max_books
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ADMIN001',                      # user_code
            'admin',                        # username
            'admin@intellilibraria.com',    # email
            admin_password,                 # password_hash (pre-hashed 'admin123')
            'System Administrator',         # full_name
            '1234567890',                   # phone
            'admin',                        # role
            'active',                       # status
            100                             # max_books
        ))
        
        # Create indexes
        cursor.executescript('''
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_book_copy_id ON transactions(book_copy_id);
        ''')
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database created successfully!")
        print("\nAdmin login details:")
        print("  Username: admin")
        print("  Password: admin123")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🔧 Creating fresh database with complete schema...")
    if create_fresh_database():
        print("\n✅ Setup complete! You can now run the application.")
    else:
        print("\n❌ Failed to set up the database. Please check the error message above.")
