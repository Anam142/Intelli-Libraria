import sqlite3
import os

def verify_and_fix_schema():
    db_path = 'intelli_libraria.db'
    conn = None
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Verifying Database Schema ===\n")
        
        # Check if books table exists and has required columns
        cursor.execute("PRAGMA table_info(books)")
        books_columns = [col[1] for col in cursor.fetchall()]
        
        if not books_columns:
            print("Creating books table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT NOT NULL,
                    edition TEXT,
                    stock INTEGER NOT NULL DEFAULT 0
                )
            ''')
            print("Created books table")
        
        # Check if stock column exists in books table
        if 'stock' not in books_columns:
            print("Adding 'stock' column to books table...")
            cursor.execute("ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0")
            print("Added 'stock' column to books table")
        
        # Check if transactions table exists and has required columns
        cursor.execute("PRAGMA table_info(transactions)")
        transactions_columns = [col[1] for col in cursor.fetchall()]
        
        if not transactions_columns:
            print("Creating transactions table...")
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
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (book_id) REFERENCES books (id)
                )
            ''')
            print("Created transactions table")
        
        # Check if users table exists
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [col[1] for col in cursor.fetchall()]
        
        if not users_columns:
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                    status TEXT CHECK(status IN ('Active', 'Inactive')) DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Created users table")
            
            # Add default admin user
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@example.com', 'admin123', 'Admin User', 'admin', 'Active'))
            print("Added default admin user")
        
        # Add some test data if books table is empty
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            print("Adding sample books...")
            sample_books = [
                ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'First Edition', 5),
                ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', '50th Anniversary Edition', 3),
                ('1984', 'George Orwell', '9780451524935', 'Signet Classics', 7)
            ]
            cursor.executemany('''
                INSERT INTO books (title, author, isbn, edition, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', sample_books)
            print(f"Added {len(sample_books)} sample books")
        
        conn.commit()
        print("\n✅ Database schema is up to date")
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_and_fix_schema()
    input("\nPress Enter to exit...")
