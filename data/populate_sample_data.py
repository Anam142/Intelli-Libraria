import os
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()

def create_connection(db_file):
    """ Create a database connection to the SQLite database """
    return sqlite3.connect(db_file)

def create_tables(conn):
    """ Create database tables if they don't exist """
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_code TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        role TEXT CHECK(role IN ('admin','member')) DEFAULT 'member',
        status TEXT CHECK(status IN ('Active','Inactive')) DEFAULT 'Active',
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        password TEXT DEFAULT '1234',
        contact TEXT,
        address TEXT
    )''')
    
    # Categories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Publishers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS publishers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        address TEXT,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Authors Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        bio TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(name)
    )''')
    
    # Books Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT NOT NULL,
        edition TEXT,
        stock INTEGER NOT NULL
    )''')
    
    # Book-Author Relationship
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_authors (
        book_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        PRIMARY KEY (book_id, author_id),
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
        FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
    )''')
    
    # Book Copies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS book_copies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        barcode TEXT UNIQUE NOT NULL,
        status TEXT CHECK(status IN ('available', 'checked_out', 'reserved', 'lost', 'damaged')) NOT NULL DEFAULT 'available',
        purchase_date DATE,
        price DECIMAL(10, 2),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
    )''')
    
    # Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        issue_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        status TEXT CHECK(status IN ('Issued', 'Returned', 'Overdue')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
    )''')
    
    conn.commit()

def populate_tables(conn):
    """ Populate all tables with sample data """
    cursor = conn.cursor()
    
    # Users (1 admin + 30 members)
    # Admin user
    cursor.execute("""
        INSERT OR IGNORE INTO users (
            user_code, username, full_name, email, phone, 
            role, status, password_hash, contact, address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'ADM-000001', 'admin', 'Admin User', 'admin@library.com', '1234567890',
        'admin', 'Active', 'pbkdf2:sha256:260000$abc123$def456789', '123 Admin St', '123 Admin St, Admin City'
    ))
    
    # Member users
    for i in range(1, 31):
        address = fake.address().replace('\n', ', ')
        cursor.execute("""
            INSERT OR IGNORE INTO users (
                user_code, username, full_name, email, phone, 
                role, status, password_hash, contact, address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f'USR-{i:06d}',
            f'member{i}',
            fake.name(),
            f'member{i}@example.com',
            f'+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}',
            'member',
            random.choice(['Active', 'Active', 'Active', 'Inactive']),  # 75% active
            'pbkdf2:sha256:260000$abc123$def456789',  # Hashed 'password123'
            f'Contact for {fake.name()}',
            address
        ))
    
    # Insert sample books
    books = []
    for i in range(1, 51):
        book = (
            f'Book Title {i}',
            fake.name(),  # author
            f'978-{random.randint(100, 999)}-{random.randint(10000, 99999)}-{random.randint(0, 9)}',  # ISBN
            f'{random.randint(1, 10)}th Edition',  # edition
            random.randint(1, 10)  # stock
        )
        books.append(book)
    
    # Insert books
    cursor.executemany('''
        INSERT INTO books (title, author, isbn, edition, stock)
        VALUES (?, ?, ?, ?, ?)
    ''', books)
    
    # Get all user and book IDs for transactions
    cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id FROM books")
    book_ids = [row[0] for row in cursor.fetchall()]
    
    # Generate transactions
    transactions = []
    for _ in range(100):  # 100 transactions
        user_id = random.choice(user_ids)
        book_id = random.choice(book_ids)
        issue_date = datetime.now() - timedelta(days=random.randint(0, 180))
        due_date = issue_date + timedelta(days=14)
        
        # 70% chance book is returned, 30% still issued (could be overdue)
        if random.random() < 0.7:  # Returned
            return_date = issue_date + timedelta(days=random.randint(1, 21))
            status = 'Returned'
            
            # If returned after due date, mark as Overdue
            if return_date > due_date:
                status = 'Overdue'
        else:  # Still issued
            return_date = None
            status = 'Issued'
            
            # If due date has passed, mark as Overdue
            if datetime.now() > due_date:
                status = 'Overdue'
        
        transaction = (
            book_id,
            user_id,
            issue_date.strftime('%Y-%m-%d'),
            due_date.strftime('%Y-%m-%d'),
            return_date.strftime('%Y-%m-%d') if return_date else None,
            status
        )
        transactions.append(transaction)
    
    # Insert transactions
    cursor.executemany('''
        INSERT INTO transactions (book_id, user_id, issue_date, due_date, 
                               return_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', transactions)
    
    conn.commit()

def main():
    # Path to your SQLite database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'intelli_libraria.db')
    
    # Create a database connection
    conn = create_connection(db_path)
    
    try:
        # Create tables if they don't exist
        create_tables(conn)
        
        # Populate tables with sample data
        populate_tables(conn)
        print("Successfully populated database with sample data!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main()
