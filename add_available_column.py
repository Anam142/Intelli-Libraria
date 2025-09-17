import sqlite3
import os

def add_available_column():
    """Add available column to books table and populate it with stock values."""
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking if 'available' column exists in books table...")
        
        # Check if available column already exists
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'available' in columns:
            print("'available' column already exists in books table.")
        else:
            print("Adding 'available' column to books table...")
            cursor.execute("ALTER TABLE books ADD COLUMN available INTEGER NOT NULL DEFAULT 0")
            print("'available' column added successfully.")
        
        # Update available column with current stock values for existing books
        print("Updating 'available' column with current stock values...")
        cursor.execute("UPDATE books SET available = stock WHERE available = 0 OR available IS NULL")
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} books with stock values.")
        
        # Verify the update
        cursor.execute("SELECT id, title, stock, available FROM books LIMIT 5")
        books = cursor.fetchall()
        print("\nSample books after update:")
        for book in books:
            print(f"ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}, Available: {book[3]}")
        
        conn.commit()
        print("\nMigration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_available_column()
