"""
Standalone repair script to ensure the 'books' table allows duplicate ISBNs
and contains required columns (author, edition, stock). It operates only on
intelli_libraria.db using the centralized DB_PATH from data.database.

Run with Python 3.12:
    python fix_isbn_constraint.py
"""
import sqlite3
import os

try:
    from data.database import DB_PATH
except Exception:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')


def ensure_columns(cur):
    cur.execute("PRAGMA table_info(books)")
    cols = {r[1] for r in cur.fetchall()}
    if 'title' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN title TEXT")
    if 'author' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN author TEXT")
    if 'isbn' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN isbn TEXT")
    if 'edition' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN edition TEXT")
    if 'stock' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0")


def has_unique_on_isbn(cur) -> bool:
    # Check index-based uniqueness
    try:
        cur.execute("PRAGMA index_list(books)")
        for idx in cur.fetchall():
            # (seq, name, unique, origin, partial)
            if idx[2] == 1:
                cur.execute(f"PRAGMA index_info({idx[1]})")
                cols = [r[2] for r in cur.fetchall()]
                if cols == ['isbn'] or 'isbn' in cols:
                    return True
    except Exception:
        pass

    # Check table-level UNIQUE constraint in CREATE TABLE SQL
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='books'")
    row = cur.fetchone()
    if row and row[0] and 'UNIQUE' in row[0].upper() and 'ISBN' in row[0].upper():
        return True
    return False


def relax_unique_isbn(cur):
    # Rebuild table without UNIQUE constraint
    # Make author nullable to tolerate legacy rows with NULL authors
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS books__tmp_migrate (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               author TEXT,
               isbn TEXT NOT NULL,
               edition TEXT,
               stock INTEGER NOT NULL DEFAULT 0
           )'''
    )
    cur.execute(
        'INSERT INTO books__tmp_migrate (id, title, author, isbn, edition, stock) '
        "SELECT id, title, COALESCE(author, ''), isbn, COALESCE(edition, ''), COALESCE(stock, 0) FROM books"
    )
    cur.execute('DROP TABLE books')
    cur.execute('ALTER TABLE books__tmp_migrate RENAME TO books')


def main():
    print('Repairing DB at:', DB_PATH)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    try:
        ensure_columns(cur)
        if has_unique_on_isbn(cur):
            print('Found UNIQUE on isbn. Relaxing constraint...')
            relax_unique_isbn(cur)
        con.commit()
        print('Repair completed successfully.')
    except Exception as e:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == '__main__':
    main()