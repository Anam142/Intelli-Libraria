"""
Simple script to add books to the database.
"""
import sqlite3
import os

def setup_database():
    """Set up the database and return a connection."""
    db_path = 'intelli_libraria.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create books table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT,
        quantity INTEGER DEFAULT 1,
        available INTEGER DEFAULT 1,
        branch TEXT DEFAULT 'Main Library'
    )
    ''')
    
    conn.commit()
    return conn

def add_books(conn):
    """Add sample books to the database."""
    books = [
        ('Digital Fundamentals', 'Thomas C. Floyd', '012345613135', 5, 5, 'Main Library'),
        ('Digital Design', 'M. Morris Mano', '012345661754', 5, 5, 'Main Library'),
        ('The 8051', 'J. Scott', '012345606021', 5, 5, 'Main Library'),
        ('Clean Code', 'Robert C. Martin', '9780132350884', 3, 3, 'Main Library'),
        ('Design Patterns', 'Erich Gamma', '9780201633610', 3, 3, 'Main Library'),
        ('Python Crash Course', 'Eric Matthes', '9781593279288', 4, 4, 'Main Library'),
        ('Learning SQL', 'Alan Beaulieu', '9780596520830', 3, 3, 'Main Library'),
        ('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', 2, 2, 'Main Library'),
        ('Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 3, 3, 'Main Library'),
        ('Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 4, 4, 'Main Library')
    ]
    
    cursor = conn.cursor()
    added = 0
    
    for title, author, isbn, quantity, available, branch in books:
        try:
            cursor.execute('''
            INSERT INTO books (title, author, isbn, quantity, available, branch)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, author, isbn, quantity, available, branch))
            added += 1
            print(f"Added: {title} by {author}")
        except sqlite3.IntegrityError:
            print(f"Skipping duplicate: {title} by {author}")
            continue
    
    conn.commit()
    return added

def list_books(conn):
    """List all books in the database."""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, author, available, quantity, branch 
    FROM books 
    ORDER BY title
    ''')
    
    books = cursor.fetchall()
    print("\nCurrent Books in Database:")
    print("-" * 80)
    for book in books:
        print(f"ID: {book[0]}, Title: {book[1]}, Available: {book[3]}/{book[4]}, Branch: {book[5]}")
    
    return len(books)

if __name__ == "__main__":
    print("Setting up database...")
    conn = setup_database()
    
    print("\nAdding books to the database...")
    added = add_books(conn)
    print(f"\nSuccessfully added {added} books.")
    
    total = list_books(conn)
    print(f"\nTotal books in database: {total}")
    
    conn.close()
