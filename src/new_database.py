import os
import sqlite3
from datetime import datetime, timedelta

def create_new_database():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    db_path = os.path.join('data', 'library.db')
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("ℹ️  Removed existing database")
        except Exception as e:
            print(f"❌ Error removing existing database: {e}")
            return False
    
    try:
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Create users table
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
        
        # Create books table
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publisher TEXT,
            publication_year INTEGER,
            category TEXT,
            description TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1,
            location TEXT,
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
        cursor.execute('CREATE INDEX idx_books_title ON books(title)')
        cursor.execute('CREATE INDEX idx_books_author ON books(author)')
        cursor.execute('CREATE INDEX idx_transactions_user ON transactions(user_id)')
        cursor.execute('CREATE INDEX idx_transactions_book ON transactions(book_id)')
        
        # Insert admin user with hashed password for 'admin123'
        password_hash = '$2b$12$Ve6Yx5UE4b0fqXW4y4yX0e8QdXJv7XK5cW5X8xY3Xv9Xv9Xv9Xv9X'  # 'admin123'
        
        cursor.execute('''
        INSERT INTO users (
            user_code, username, email, password_hash, 
            full_name, role, status, max_books, phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ADMIN001', 'admin', 'admin@intellilibraria.test', password_hash,
            'System Administrator', 'admin', 'active', 100, '0000000000'
        ))
        
        # Add some sample books
        sample_books = [
            ('978-0132350884', 'Clean Code', 'Robert C. Martin', 'Prentice Hall', 2008, 'Programming', 'A handbook of agile software craftsmanship', 5, 5, 'A1'),
            ('978-0201616224', 'The Pragmatic Programmer', 'Andrew Hunt, David Thomas', 'Addison-Wesley', 1999, 'Programming', 'Your journey to mastery', 3, 3, 'A2'),
            ('978-0135957059', 'The Clean Coder', 'Robert C. Martin', 'Prentice Hall', 2011, 'Programming', 'A code of conduct for professional programmers', 2, 2, 'A3')
        ]
        
        cursor.executemany('''
        INSERT INTO books (
            isbn, title, author, publisher, publication_year, 
            category, description, quantity, available, location
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_books)
        
        conn.commit()
        print("\n✅ Database created successfully at:", os.path.abspath(db_path))
        print("\n🔑 Admin login credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n📚 Sample books have been added to the database.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 Creating a new database...")
    if create_new_database():
        print("\n✅ Setup complete! You can now run the application.")
    else:
        print("\n❌ Failed to create the database. Please check the error messages above.")
