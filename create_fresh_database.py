#!/usr/bin/env python3
"""
Create a fresh database with admin user and necessary tables.
"""
import sqlite3
from pathlib import Path
from auth_utils import get_password_hash

def create_fresh_database():
    db_path = Path('intelli_libraria.db')
    
    # Create a fresh database connection
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Drop existing tables if they exist
        cursor.executescript('''
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS books;
            DROP TABLE IF EXISTS transactions;
            DROP TABLE IF EXISTS book_copies;
        ''')
        
        # Create fresh tables
        cursor.executescript('''
            -- Users table
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
            );
            
            -- Books table
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
            );
            
            -- Book copies table
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
            );
            
            -- Transactions table
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_copy_id INTEGER NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('borrow', 'return', 'renewal', 'reservation')) NOT NULL,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP,
                fine_amount REAL DEFAULT 0.0,
                status TEXT CHECK(status IN ('active', 'completed', 'overdue', 'lost')) NOT NULL DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_copy_id) REFERENCES book_copies(id) ON DELETE CASCADE
            );
        ''')
        
        # Create admin user
        admin_password = 'admin123'
        hashed_password = get_password_hash(admin_password)
        
        cursor.execute('''
            INSERT INTO users (
                user_code, username, email, password_hash, full_name, 
                phone, role, status, max_books
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ADMIN001',                      # user_code
            'admin',                        # username
            'admin@intellilibraria.com',    # email
            hashed_password,                # password_hash
            'System Administrator',          # full_name
            '1234567890',                   # phone
            'admin',                        # role
            'active',                       # status
            100                             # max_books
        ))
        
        conn.commit()
        print("✅ Database created successfully!")
        print("\nAdmin credentials:")
        print(f"Username: admin")
        print(f"Password: {admin_password}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Creating fresh database...")
    try:
        create_fresh_database()
        print("\n✅ Setup complete! You can now run the application.")
    except Exception as e:
        print(f"\n❌ Failed to create database: {e}")
        print("\nPlease make sure all database connections are closed and try again.")
