import os
import sqlite3

print("=== Simple Database Test ===\n")

try:
    # Check if database exists
    db_path = 'intelli_libraria.db'
    db_exists = os.path.exists(db_path)
    print(f"Database exists: {db_exists}")
    
    if not db_exists:
        print("Creating new database...")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        status TEXT DEFAULT 'Active'
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        available INTEGER DEFAULT 1
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP,
        return_date TIMESTAMP,
        status TEXT DEFAULT 'Borrowed',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )''')
    
    # Add test data if needed
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        print("Adding test user...")
        cursor.execute("INSERT INTO users (id, full_name, email) VALUES (1, 'Test User', 'test@example.com')")
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        print("Adding test book...")
        cursor.execute("INSERT INTO books (id, title, author, available) VALUES (1, 'Test Book', 'Test Author', 1)")
    
    # Test borrow
    print("\nTesting borrow functionality...")
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Check book availability
        cursor.execute("SELECT available FROM books WHERE id = 1")
        available = cursor.fetchone()[0]
        
        if available > 0:
            # Create transaction
            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, due_date)
                VALUES (1, 1, date('now', '+14 days'))
            """)
            
            # Update book availability
            cursor.execute("UPDATE books SET available = 0 WHERE id = 1")
            
            conn.commit()
            print("✓ Book borrowed successfully!")
        else:
            print("Book not available for borrowing")
    
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error: {e}")
    
    # Show current state
    print("\nCurrent state:")
    print("User:", cursor.execute("SELECT * FROM users").fetchone())
    print("Book:", cursor.execute("SELECT * FROM books").fetchone())
    print("Transactions:", cursor.execute("SELECT * FROM transactions").fetchall())
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()

print("\nTest complete!")
