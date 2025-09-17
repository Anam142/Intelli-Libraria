import os
import sqlite3
from pathlib import Path

def setup_fresh_db():
    try:
        # Set database path to a temporary name to avoid file lock issues
        db_path = Path(__file__).parent / 'intelli_libraria_new.db'
        
        # Remove existing database if it exists
        if db_path.exists():
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table with proper schema
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
        
        # Create other necessary tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                isbn TEXT UNIQUE,
                quantity INTEGER DEFAULT 1,
                available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create admin user with default credentials
        cursor.execute('''
            INSERT INTO users 
            (username, email, password, full_name, phone, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin',
            'admin@intellilibraria.test',
            '1234',  # Default password
            'System Administrator',
            '1234567890',
            'admin',
            'Active'
        ))
        
        # Create borrow table with proper foreign key constraints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP,
                status TEXT CHECK(status IN ('Borrowed', 'Returned', 'Overdue')) DEFAULT 'Borrowed',
                fine_amount REAL DEFAULT 0.0,
                FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_borrow_book_id ON borrow(book_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_borrow_user_id ON borrow(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_borrow_status ON borrow(status)')
        
        conn.commit()
        print("✅ Database created successfully!")
        print("Admin credentials:")
        print("Username: admin")
        print("Password: 1234")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Setting up fresh database...")
    setup_fresh_db()
