"""
Set up a fresh library database with all books.
"""
import sqlite3
import os

def create_database():
    """Create a new SQLite database with all required tables."""
    db_path = 'library_new.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create books table
    cursor.execute('''
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_code TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        authors TEXT NOT NULL,
        isbn TEXT,
        quantity_total INTEGER NOT NULL DEFAULT 1,
        quantity_available INTEGER NOT NULL DEFAULT 1,
        branch TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_books_title ON books(title)')
    cursor.execute('CREATE INDEX idx_books_author ON books(authors)')
    
    conn.commit()
    return conn

def add_books(conn):
    """Add all books to the database."""
    books = [
        # Existing books with updated quantities
        ('Digital Fundamentals', 'Thomas C. Floyd', '012345613135', 7, 7, 'Main Library'),
        ('Digital Design', 'M. Morris Mano', '012345661754', 8, 8, 'Main Library'),
        ('The 8051', 'J. Scott', '012345606021', 7, 7, 'Main Library'),
        ('C Programming How to C++', 'Paul Reidel', '012345678901', 6, 6, 'Main Library'),
        ('Java 2', 'Herbert Schildt', '012345678902', 7, 7, 'Main Library'),
        ('Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 6, 6, 'Main Library'),
        ('Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 7, 7, 'Main Library'),
        ('Clean Code', 'Robert C. Martin', '9780132350884', 8, 8, 'Main Library'),
        ('Design Patterns', 'Erich Gamma', '9780201633610', 7, 7, 'Main Library'),
        ('Python Crash Course', 'Eric Matthes', '9781593279288', 6, 6, 'Main Library'),
        
        # New recommended books
        ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 3, 3, 'Main Library'),
        ('The Pragmatic Programmer', 'David Thomas', '9780135957059', 4, 4, 'Main Library'),
        ('Clean Architecture', 'Robert C. Martin', '9780134494166', 3, 3, 'Main Library'),
        ('Eloquent JavaScript', 'Marijn Haverbeke', '9781593279509', 3, 3, 'Main Library'),
        ('Python for Data Analysis', 'Wes McKinney', '9781098104030', 3, 3, 'Main Library'),
        ('Effective Java', 'Joshua Bloch', '9780134685991', 2, 2, 'Main Library'),
        ('You Don\'t Know JS', 'Kyle Simpson', '9781491904428', 2, 2, 'Main Library'),
        ('Learning React', 'Alex Banks', '9781492051725', 3, 3, 'Main Library'),
        ('The Hundred-Page Machine Learning Book', 'Andriy Burkov', '9781999579500', 2, 2, 'Main Library'),
        ('Python Data Science Handbook', 'Jake VanderPlas', '9781491912058', 3, 3, 'Main Library'),
        ('Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', 2, 2, 'Main Library'),
        ('System Design Interview', 'Alex Xu', '9781736049112', 3, 3, 'Main Library'),
        ('Atomic Habits', 'James Clear', '9780735211292', 5, 5, 'Main Library'),
        ('Deep Work', 'Cal Newport', '9781455586691', 3, 3, 'Main Library'),
        ('The Art of Computer Programming', 'Donald Knuth', '9780321751041', 1, 1, 'Reference Section'),
        ('Grokking Algorithms', 'Aditya Bhargava', '9781617292231', 4, 4, 'Main Library'),
        ('The Clean Coder', 'Robert C. Martin', '9780137081073', 3, 3, 'Main Library'),
        ('Refactoring', 'Martin Fowler', '9780134757599', 2, 2, 'Main Library'),
        ('The Mythical Man-Month', 'Fred Brooks', '9780201835953', 2, 2, 'Reference Section'),
        ('Code Complete', 'Steve McConnell', '9780735619678', 3, 3, 'Main Library'),
        ('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', 3, 3, 'Main Library'),
        ('Designing Distributed Systems', 'Brendan Burns', '9781491983645', 2, 2, 'Main Library'),
        ('Site Reliability Engineering', 'Betsy Beyer', '9781491929124', 2, 2, 'Main Library'),
        ('The DevOps Handbook', 'Gene Kim', '9781942788003', 2, 2, 'Main Library'),
        ('Accelerate', 'Nicole Forsgren', '9781942788331', 2, 2, 'Main Library'),
        ('The Phoenix Project', 'Gene Kim', '9781942788294', 3, 3, 'Main Library'),
        ('The Unicorn Project', 'Gene Kim', '9781942788768', 2, 2, 'Main Library')
    ]
    
    cursor = conn.cursor()
    added = 0
    
    for title, author, isbn, quantity, available, branch in books:
        try:
            # Generate book code
            book_code = f"BK-{isbn[:8] if isbn else 'NONE'}-{abs(hash(title)) % 10000:04d}"
            
            # Insert book
            cursor.execute('''
            INSERT INTO books 
            (book_code, title, authors, isbn, quantity_total, quantity_available, branch)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (book_code, title, author, isbn, quantity, available, branch))
            
            added += 1
            print(f"Added: {title} by {author}")
            
        except sqlite3.IntegrityError as e:
            print(f"Skipping duplicate: {title} by {author} - {e}")
            continue
        except Exception as e:
            print(f"Error adding {title}: {str(e)}")
            continue
    
    conn.commit()
    return added

def list_books(conn):
    """List all books in the database."""
    cursor = conn.cursor()
    cursor.execute('''
    SELECT book_code, title, authors, quantity_available, quantity_total, branch 
    FROM books 
    ORDER BY branch, title
    ''')
    
    books = cursor.fetchall()
    print("\nCurrent Books in Database:")
    print("=" * 120)
    current_branch = None
    
    for book in books:
        if book[5] != current_branch:
            current_branch = book[5]
            print(f"\n{current_branch}:")
            print("-" * 120)
        
        print(f"{book[0]} | {book[1][:60]:<60} | {book[2][:25]:<25} | Avail: {book[3]}/{book[4]}")
    
    return len(books)

if __name__ == "__main__":
    print("Creating new library database...")
    conn = create_database()
    
    print("\nAdding books to the database...")
    added = add_books(conn)
    print(f"\nSuccessfully added {added} books.")
    
    total = list_books(conn)
    print(f"\nTotal books in database: {total}")
    
    conn.close()
