import os
import sqlite3
from pathlib import Path
from passlib.hash import bcrypt

def setup_database():
    # Ensure the data directory exists
    db_dir = Path('data')
    db_dir.mkdir(exist_ok=True)
    
    # Database path
    db_path = db_dir / 'library.db'
    
    # Remove existing database if it exists
    if db_path.exists():
        try:
            os.remove(db_path)
            print("Removed existing database")
        except Exception as e:
            print(f"❌ Error removing existing database: {e}")
            return
    
    try:
        # Create new database and tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                publication_year INTEGER,
                publisher TEXT,
                category TEXT,
                total_copies INTEGER NOT NULL DEFAULT 1,
                available_copies INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP NOT NULL,
                return_date TIMESTAMP,
                status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) DEFAULT 'borrowed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)
        ''')
        
        # Create admin user
        password_hash = bcrypt.hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@intellilibraria.test', password_hash, 'System Administrator', 'admin'))
        
        # Create a sample book
        cursor.execute('''
            INSERT INTO books (title, author, isbn, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Sample Book', 'Sample Author', '1234567890', 5, 5))
        
        conn.commit()
        
        print("\n✅ Database created successfully!")
        print("✅ Tables created: users, books, transactions")
        print("✅ Indexes created for better performance")
        print("\n✅ Admin user created:")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print("\n✅ Sample book added to the library")
        
        # Verify the admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        if admin and bcrypt.verify('admin123', admin[3]):
            print("\n✅ Login verification successful!")
        else:
            print("\n❌ Login verification failed!")
            
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Setting up new database...")
    print(f"Database will be created at: {Path('data/library.db').absolute()}")
    print("This will remove any existing database. Continue? (y/n)")
    
    if input().lower() == 'y':
        setup_database()
    else:
        print("Database setup cancelled.")
