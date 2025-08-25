"""
Bulk insert canonical book list into the single SQLite database used by
Intelli Libraria. The script makes sure the Books table has the required
schema and constraints, then inserts the provided records.

Run with Python 3.12:
  python import_books.py
"""
import sqlite3
import os
from datetime import datetime

try:
    from data.database import DB_PATH
except Exception:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')


BOOKS = [
    ('Digital Fundamentals', 'Thomas C. Floyd', '012345613135', '11th', 5),
    ('Digital Design', 'M. Morris Mano', '012345661754', '6th', 5),
    ('The 8051', 'J. Scott', '012345606021', '4th', 5),
    ('Microcontrollers', 'Mackenzie', None, '9th', 5),
    ('C Programming How to C++', 'Paul Reidel', '012345612053', '9th', 5),
    ('C++', 'D.S. Malhi', '012345616051', '8th', 5),
    ('Java 2', 'Herbert Schildt', '0072224207', '5th', 1),
    ('Digital Logic and Computer Design', 'M. Morris Mano', '257230133', '2nd', 2),
    ('Digital Design', 'M. Morris Mano', '8120320516', '3rd', 1),
    ('Database System', 'Thomas Connolly', '8131707164', '3rd', 1),
    ('Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', '5th', 3),
    ('Operating System Concepts', 'Abraham Silberschatz', '9781118063330', '9th', 4),
    ('Artificial Intelligence: A Modern Approach', 'Stuart Russell', '9780136042594', '3rd', 2),
    ('Machine Learning', 'Tom M. Mitchell', '0070428077', '1st', 3),
    ('Deep Learning', 'Ian Goodfellow', '9780262035613', '1st', 2),
    ('Python Crash Course', 'Eric Matthes', '9781593279288', '2nd', 4),
    ('Learning SQL', 'Alan Beaulieu', '9780596520830', '2nd', 3),
    ('Clean Code', 'Robert C. Martin', '9780132350884', '1st', 2),
    ('Design Patterns', 'Erich Gamma', '9780201633610', '1st', 3),
    ('The Pragmatic Programmer', 'Andrew Hunt', '9780201616224', '1st', 2),
    ('Computer Organization and Design', 'David A. Patterson', '9780124077263', '5th', 2),
    ('Compilers: Principles, Techniques, and Tools', 'Alfred V. Aho', '9780321486813', '2nd', 1),
    ('Introduction to the Theory of Computation', 'Michael Sipser', '9781133187790', '3rd', 2),
    ('Data Structures and Algorithms in Java', 'Robert Lafore', '9780672324536', '2nd', 2),
    ('Head First Java', 'Kathy Sierra', '9780596009205', '2nd', 3),
    ('Agile Software Development', 'Robert C. Martin', '9780135974445', '1st', 2),
    ('Software Engineering', 'Ian Sommerville', '9780133943030', '10th', 3),
    ('Programming Pearls', 'Jon Bentley', '9780201657883', '2nd', 1),
    ('Code Complete', 'Steve McConnell', '9780735619678', '2nd', 2),
]


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    # Create or align Books table
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS books (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               author TEXT,
               isbn TEXT,
               edition TEXT,
               stock INTEGER NOT NULL DEFAULT 0,
               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )'''
    )

    # Add missing columns if table already existed without them
    cur.execute("PRAGMA table_info(books)")
    cols = {r[1] for r in cur.fetchall()}
    # Add created_at/updated_at. Some SQLite builds disallow CURRENT_TIMESTAMP as
    # default in ALTER TABLE; fall back to nullable column + backfill and triggers.
    if 'created_at' not in cols:
        try:
            cur.execute("ALTER TABLE books ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            cur.execute("ALTER TABLE books ADD COLUMN created_at TEXT")
            cur.execute("UPDATE books SET created_at = COALESCE(created_at, datetime('now'))")
    if 'updated_at' not in cols:
        try:
            cur.execute("ALTER TABLE books ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            cur.execute("ALTER TABLE books ADD COLUMN updated_at TEXT")
            cur.execute("UPDATE books SET updated_at = COALESCE(updated_at, datetime('now'))")

    # Trigger to keep updated_at fresh
    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS trg_books_updated_at
        AFTER UPDATE ON books
        BEGIN
            UPDATE books SET updated_at = datetime('now') WHERE id = NEW.id;
        END;
    ''')

    # Enforce uniqueness on ISBN only when it is not NULL (partial index)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_books_isbn_unique
        ON books(isbn) WHERE isbn IS NOT NULL
    """)


def bulk_insert(conn: sqlite3.Connection, rows) -> int:
    cur = conn.cursor()
    # Use INSERT OR IGNORE to respect the unique index on non-NULL ISBN
    cur.executemany(
        'INSERT OR IGNORE INTO books (title, author, isbn, edition, stock) VALUES (?,?,?,?,?)',
        rows,
    )
    return cur.rowcount


def main():
    print('Using database:', DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        ensure_schema(conn)
        inserted = bulk_insert(conn, BOOKS)
        conn.commit()
        print(f'Inserted {inserted} book(s).')
    finally:
        conn.close()


if __name__ == '__main__':
    main()


