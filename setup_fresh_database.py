import sqlite3
import os
from datetime import datetime, timedelta

def create_fresh_database():
    db_path = 'intelli_libraria_fresh.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creating fresh database with correct schema...")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'librarian', 'member')) DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create books table
        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                available_quantity INTEGER DEFAULT 1,
                total_quantity INTEGER DEFAULT 1
            )
        ''')
        
        # Create transactions table with issue_date (not borrow_date)
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP,
                status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) DEFAULT 'borrowed',
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
        
        # Add admin user
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', 'hashed_password_here', 'System Administrator', 'admin'))
        
        # Add some sample books
        sample_books = [
            ('978-0132350884', 'Clean Code', 'Robert C. Martin', 5, 5),
            ('978-0201616224', 'The Pragmatic Programmer', 'Andrew Hunt, David Thomas', 3, 3),
            ('978-0135957059', 'The Clean Coder', 'Robert C. Martin', 2, 2)
        ]
        
        cursor.executemany('''
            INSERT INTO books (isbn, title, author, available_quantity, total_quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_books)
        
        # Add a sample transaction
        due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO transactions (user_id, book_id, due_date, status)
            VALUES (?, ?, ?, ?)
        ''', (1, 1, due_date, 'borrowed'))
        
        conn.commit()
        print(f"\n✅ Successfully created fresh database at: {os.path.abspath(db_path)}")
        print("\nSample data added:")
        print("- 1 admin user (username: admin)")
        print("- 3 sample books")
        print("- 1 sample transaction")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Creating Fresh Database ===\n")
    if create_fresh_database():
        print("\n✅ Setup completed successfully!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
