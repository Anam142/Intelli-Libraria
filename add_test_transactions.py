import sqlite3
from datetime import datetime, timedelta

def create_connection():
    """Create a database connection to the SQLite database."""
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def add_test_transactions():
    """Add test transaction records to the database."""
    conn = create_connection()
    if not conn:
        print("Failed to connect to database")
        return

    try:
        cursor = conn.cursor()
        
        # First, check if we have at least one user and one book
        cursor.execute("SELECT id FROM users LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("No users found in the database. Please add users first.")
            return
        
        cursor.execute("SELECT id FROM books LIMIT 1")
        book = cursor.fetchone()
        if not book:
            print("No books found in the database. Please add books first.")
            return
        
        # Get user ID
        user_id = user[0]
        
        # Current date and time
        now = datetime.now()
        
        # First, get or create the specific books
        books = [
            ("Operating System Concepts", "Abraham Silberschatz"),
            ("C++ Programming Language", "Bjarne Stroustrup"),
            ("Database System Concepts", "Abraham Silberschatz"),
            ("Data Structures and Algorithms", "Thomas H. Cormen"),
            ("Modern Operating Systems", "Andrew S. Tanenbaum")
        ]
        
        # Insert books if they don't exist and get their IDs
        book_ids = []
        for title, author in books:
            cursor.execute("SELECT id FROM books WHERE title = ? AND author = ?", (title, author))
            book = cursor.fetchone()
            if book:
                book_ids.append(book[0])
            else:
                cursor.execute(
                    "INSERT INTO books (title, author, isbn, quantity, available) VALUES (?, ?, ?, ?, ?)",
                    (title, author, f"ISBN-{hash(title) % 1000000}", 5, 5)
                )
                book_ids.append(cursor.lastrowid)
        
        # Sample transaction data with the specific books
        transactions = [
            # Operating System book issued today, due in 14 days
            (book_ids[0], user_id, now.strftime('%Y-%m-%d'), 
             (now + timedelta(days=14)).strftime('%Y-%m-%d'), None, 'Borrowed'),
            
            # C++ book issued 5 days ago, due in 9 days
            (book_ids[1], user_id, (now - timedelta(days=5)).strftime('%Y-%m-%d'), 
             (now + timedelta(days=9)).strftime('%Y-%m-%d'), None, 'Borrowed'),
            
            # Database book issued 10 days ago, due in 4 days
            (book_ids[2], user_id, (now - timedelta(days=10)).strftime('%Y-%m-%d'), 
             (now + timedelta(days=4)).strftime('%Y-%m-%d'), None, 'Borrowed'),
            
            # Data Structures book issued 15 days ago, overdue by 1 day
            (book_ids[3], user_id, (now - timedelta(days=15)).strftime('%Y-%m-%d'), 
             (now - timedelta(days=1)).strftime('%Y-%m-%d'), None, 'Borrowed'),
            
            # Modern OS book that was returned
            (book_ids[4], user_id, (now - timedelta(days=20)).strftime('%Y-%m-%d'), 
             (now - timedelta(days=6)).strftime('%Y-%m-%d'), 
             (now - timedelta(days=5)).strftime('%Y-%m-%d'), 'Returned')
        ]
        
        # Insert transactions
        cursor.executemany("""
            INSERT INTO transactions (book_id, user_id, issue_date, due_date, return_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, transactions)
        
        conn.commit()
        print(f"Successfully added {len(transactions)} test transactions.")
        
    except sqlite3.Error as e:
        print(f"Error adding test transactions: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_test_transactions()
