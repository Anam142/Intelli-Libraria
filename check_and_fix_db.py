"""
Check and fix database structure for Intelli-Libraria.
"""
import os
import sqlite3
from datetime import datetime

def check_database():
    """Check the database structure and create tables if needed."""
    db_path = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
    print(f"Checking database at: {db_path}")
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print("Database file not found. Creating a new database...")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    try:
        # Check if books table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='books'
        """)
        
        if not cursor.fetchone():
            print("Creating 'books' table...")
            cursor.execute("""
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                authors TEXT,
                isbn TEXT,
                quantity_total INTEGER NOT NULL DEFAULT 1,
                quantity_available INTEGER NOT NULL DEFAULT 1,
                branch TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            print("'books' table created successfully.")
        else:
            print("'books' table already exists.")
            
        # Show current books count
        cursor.execute("SELECT COUNT(*) as count FROM books")
        count = cursor.fetchone()['count']
        print(f"Current number of books in database: {count}")
        
        # Show table structure
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        print("-" * 50)
        for col in columns:
            print(f"{col['name']} ({col['type']}) {'PRIMARY KEY' if col['pk'] else ''}")
        
        # List first few books if any
        if count > 0:
            print("\nFirst 5 books in the database:")
            print("-" * 50)
            cursor.execute("""
            SELECT id, book_code, title, authors, quantity_total, quantity_available 
            FROM books 
            LIMIT 5
            """)
            for row in cursor.fetchall():
                print(f"ID: {row['id']}, Code: {row['book_code']}, Title: {row['title']}, Available: {row['quantity_available']}/{row['quantity_total']}")
        
        return True
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return False
    finally:
        conn.close()

def add_sample_books():
    """Add sample books to the database."""
    db_path = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Sample books data
        books = [
            ('Digital Fundamentals', 'Thomas C. Floyd', '012345613135', '11th', 5, 'Main Library'),
            ('Digital Design', 'M. Morris Mano', '012345661754', '6th', 5, 'Main Library'),
            ('The 8051', 'J. Scott', '012345606021', '4th', 5, 'Main Library'),
            ('Clean Code', 'Robert C. Martin', '9780132350884', '1st', 3, 'Main Library'),
            ('Design Patterns', 'Erich Gamma', '9780201633610', '1st', 3, 'Main Library')
        ]
        
        added = 0
        
        for title, authors, isbn, edition, quantity, branch in books:
            try:
                # Generate book code
                book_code = f"BK-{isbn[:8] if isbn else 'NONE'}-{abs(hash(title)) % 10000:04d}"
                
                # Insert book
                cursor.execute("""
                INSERT INTO books 
                (book_code, title, authors, isbn, quantity_total, quantity_available, branch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (book_code, title, authors, isbn, quantity, quantity, branch))
                
                added += 1
                print(f"Added: {title} by {authors}")
                
            except sqlite3.IntegrityError:
                print(f"Skipping existing book: {title} by {authors}")
                continue
            except Exception as e:
                print(f"Error adding {title}: {str(e)}")
                continue
        
        conn.commit()
        print(f"\nSuccessfully added {added} books to the database.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Database Check ===\n")
    if check_database():
        print("\n=== Adding Sample Books ===\n")
        add_sample_books()
        
        # Show updated count
        db_path = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM books")
        count = cursor.fetchone()[0]
        print(f"\nTotal books in database: {count}")
        conn.close()
