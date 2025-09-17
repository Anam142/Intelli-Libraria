import sqlite3
import os

def recreate_books_table():
    """Recreate the books table with correct schema."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Recreating Books Table ===")
        
        # Disable foreign key constraints
        print("1. Disabling foreign key constraints...")
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Backup existing data
        print("2. Backing up existing books data...")
        cursor.execute("SELECT * FROM books")
        existing_books = cursor.fetchall()
        print(f"Backed up {len(existing_books)} books")
        
        # Drop the existing table
        print("3. Dropping existing books table...")
        cursor.execute("DROP TABLE IF EXISTS books")
        
        # Create new books table with correct schema
        print("4. Creating new books table...")
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT NOT NULL,
            edition TEXT,
            stock INTEGER NOT NULL,
            available INTEGER NOT NULL DEFAULT 0
        )
        ''')
        
        # Restore the data with correct available values
        print("5. Restoring books data...")
        for book in existing_books:
            # book structure: (id, title, author, isbn, edition, stock, available)
            if len(book) == 7:  # Has available column
                cursor.execute('''
                INSERT INTO books (id, title, author, isbn, edition, stock, available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (book[0], book[1], book[2], book[3], book[4], book[5], book[5]))  # available = stock
            else:  # Old format without available
                cursor.execute('''
                INSERT INTO books (id, title, author, isbn, edition, stock, available)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (book[0], book[1], book[2], book[3], book[4], book[5], book[5]))  # available = stock
        
        # Verify the new table
        print("6. Verifying new table...")
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 3")
        books = cursor.fetchall()
        print("Sample books in new table:")
        for book in books:
            print(f"  ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        # Re-enable foreign key constraints
        print("7. Re-enabling foreign key constraints...")
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        print("\n✅ Books table recreated successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    recreate_books_table()
