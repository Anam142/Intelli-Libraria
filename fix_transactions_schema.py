import sqlite3
import os

def fix_transactions():
    # Create a backup of the current database
    if os.path.exists('intelli_libraria.db'):
        backup_count = 1
        while os.path.exists(f'intelli_libraria_backup_{backup_count}.db'):
            backup_count += 1
        os.rename('intelli_libraria.db', f'intelli_libraria_backup_{backup_count}.db')
        print(f"Created backup: intelli_libraria_backup_{backup_count}.db")
    
    # Create a new database with correct schema
    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create users table if not exists
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
    
    # Create books table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE,
        edition TEXT,
        stock INTEGER DEFAULT 1,
        available INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Drop existing transactions table if it exists
    cursor.execute("DROP TABLE IF EXISTS transactions")
    
    # Create new transactions table with correct schema
    cursor.execute('''
    CREATE TABLE transactions (
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
    
    # Create trigger to update timestamps
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
    AFTER UPDATE ON transactions
    BEGIN
        UPDATE transactions 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
    ''')
    
    # Add sample data if needed
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Add admin user
        cursor.execute('''
        INSERT INTO users (username, email, password, full_name, role, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', 'admin123', 'Admin User', 'admin', 'Active'))
        
        # Add sample member
        cursor.execute('''
        INSERT INTO users (username, email, password, full_name, role, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('member1', 'member@example.com', 'member123', 'Test Member', 'member', 'Active'))
    
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        # Add sample books
        sample_books = [
            ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'First Edition', 5, 5),
            ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', '50th Anniversary', 3, 3),
            ('1984', 'George Orwell', '9780451524935', 'Signet Classics', 2, 2)
        ]
        cursor.executemany('''
        INSERT INTO books (title, author, isbn, edition, stock, available)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_books)
    
    conn.commit()
    conn.close()
    
    print("✅ Database schema has been fixed successfully!")
    print("\nDefault login credentials:")
    print("Admin: username='admin', password='admin123'")
    print("Member: username='member1', password='member123'")
    print("\nPlease restart your application.")

if __name__ == "__main__":
    print("Fixing database schema...")
    fix_transactions()
    input("\nPress Enter to exit...")
