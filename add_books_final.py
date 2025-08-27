"""
Script to add books directly to the SQLite database.
"""
import sqlite3
from datetime import datetime

def add_books():
    # Connect to the database
    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()
    
    try:
        # Create books table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
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
        ''')
        
        # List of books to add
        books = [
            ('BK-01234561', 'Digital Fundamentals', 'Thomas C. Floyd', '012345613135', 5, 5, 'Main Library'),
            ('BK-01234566', 'Digital Design', 'M. Morris Mano', '012345661754', 5, 5, 'Main Library'),
            ('BK-01234560', 'The 8051', 'J. Scott', '012345606021', 5, 5, 'Main Library'),
            ('BK-NONE-001', 'Microcontrollers', 'Mackenzie', None, 5, 5, 'Main Library'),
            ('BK-01234561-2', 'C Programming How to C++', 'Paul Reidel', '012345612053', 5, 5, 'Main Library'),
            ('BK-01234561-3', 'C++', 'D.S. Malhi', '012345616051', 5, 5, 'Main Library'),
            ('BK-00722242', 'Java 2', 'Herbert Schildt', '0072224207', 1, 1, 'Main Library'),
            ('BK-2572301', 'Digital Logic and Computer Design', 'M. Morris Mano', '257230133', 2, 2, 'Main Library'),
            ('BK-81203205', 'Digital Design', 'M. Morris Mano', '8120320516', 1, 1, 'Main Library'),
            ('BK-81317071', 'Database System', 'Thomas Connolly', '8131707164', 1, 1, 'Main Library'),
            ('BK-97801321', 'Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 3, 3, 'Main Library'),
            ('BK-97811180', 'Operating System Concepts', 'Abraham Silberschatz', '9781118063330', 4, 4, 'Main Library'),
            ('BK-97801360', 'Artificial Intelligence: A Modern Approach', 'Stuart Russell', '9780136042594', 2, 2, 'Main Library'),
            ('BK-00704280', 'Machine Learning', 'Tom M. Mitchell', '0070428077', 3, 3, 'Main Library'),
            ('BK-97802620', 'Deep Learning', 'Ian Goodfellow', '9780262035613', 2, 2, 'Main Library'),
            ('BK-97815932', 'Python Crash Course', 'Eric Matthes', '9781593279288', 4, 4, 'Main Library'),
            ('BK-97805965', 'Learning SQL', 'Alan Beaulieu', '9780596520830', 3, 3, 'Main Library'),
            ('BK-97801323', 'Clean Code', 'Robert C. Martin', '9780132350884', 2, 2, 'Main Library'),
            ('BK-97802016', 'Design Patterns', 'Erich Gamma', '9780201633610', 3, 3, 'Main Library'),
            ('BK-97802016-2', 'The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', 2, 2, 'Main Library'),
            ('BK-97801240', 'Computer Organization and Design', 'David A. Patterson', '9780124077263', 2, 2, 'Main Library'),
            ('BK-97803214', 'Compilers: Principles, Techniques, and Tools', 'Alfred V. Aho', '9780321486813', 1, 1, 'Main Library'),
            ('BK-97811331', 'Introduction to the Theory of Computation', 'Michael Sipser', '9781133187790', 2, 2, 'Main Library'),
            ('BK-97806723', 'Data Structures and Algorithms in Java', 'Robert Lafore', '9780672324536', 2, 2, 'Main Library'),
            ('BK-97805960', 'Head First Java', 'Kathy Sierra', '9780596009205', 3, 3, 'Main Library'),
            ('BK-97801359', 'Agile Software Development', 'Robert C. Martin', '9780135974445', 2, 2, 'Main Library'),
            ('BK-97801339', 'Software Engineering', 'Ian Sommerville', '9780133943030', 3, 3, 'Main Library'),
            ('BK-97802016-3', 'Programming Pearls', 'Jon Bentley', '9780201657883', 1, 1, 'Main Library'),
            ('BK-97807356', 'Code Complete', 'Steve McConnell', '9780735619678', 2, 2, 'Main Library')
        ]
        
        # Add books to the database
        added = 0
        for book in books:
            try:
                cursor.execute('''
                INSERT INTO books 
                (book_code, title, authors, isbn, quantity_total, quantity_available, branch)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', book)
                added += 1
                print(f"Added: {book[1]} by {book[2]}")
            except sqlite3.IntegrityError:
                print(f"Skipping existing book: {book[1]}")
                continue
        
        # Commit the transaction
        conn.commit()
        print(f"\nSuccessfully added {added} books to the database.")
        
        # Count total books
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        print(f"Total books in database: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_books()
