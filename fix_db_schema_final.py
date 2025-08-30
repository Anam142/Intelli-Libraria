import sqlite3
import os

def fix_database():
    # Backup existing database
    if os.path.exists('intelli_libraria.db'):
        backup_count = 1
        while os.path.exists(f'intelli_libraria_backup_{backup_count}.db'):
            backup_count += 1
        os.rename('intelli_libraria.db', f'intelli_libraria_backup_{backup_count}.db')
        print(f"Created backup: intelli_libraria_backup_{backup_count}.db")
    
    # Create new database
    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create users table
    cursor.execute('''
    CREATE TABLE users (
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
    
    # Create books table
    cursor.execute('''
    CREATE TABLE books (
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
    
    # Create transactions table
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
    
    # Create triggers for timestamps
    cursor.execute('''
    CREATE TRIGGER update_users_timestamp
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    ''')
    
    cursor.execute('''
    CREATE TRIGGER update_books_timestamp
    AFTER UPDATE ON books
    BEGIN
        UPDATE books SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    ''')
    
    cursor.execute('''
    CREATE TRIGGER update_transactions_timestamp
    AFTER UPDATE ON transactions
    BEGIN
        UPDATE transactions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
    ''')
    
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
    
    # Add sample books
    sample_books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'First Edition', 5, 5),
        ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', '50th Anniversary', 3, 3),
        ('1984', 'George Orwell', '9780451524935', 'Signet Classics', 2, 2),
        ('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Penguin Classics', 4, 4),
        ('The Hobbit', 'J.R.R. Tolkien', '9780547928227', '70th Anniversary', 3, 3)
    ]
    
    cursor.executemany('''
    INSERT INTO books (title, author, isbn, edition, stock, available)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_books)
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Fresh database created successfully!")
    print("\nDefault login credentials:")
    print("Admin: username='admin', password='admin123'")
    print("Member: username='member1', password='member123'")
    print("\nPlease restart your application.")

if __name__ == "__main__":
    print("Creating fresh database with correct schema...")
    fix_database()
    input("\nPress Enter to exit...")
