import sqlite3

def check_books():
    db_path = 'intelli_libraria.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if books table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books';")
        if not cursor.fetchone():
            print("ERROR: 'books' table not found in the database!")
            return
            
        # Count books
        cursor.execute("SELECT COUNT(*) FROM books;")
        count = cursor.fetchone()[0]
        print(f"Found {count} books in the database.")
        
        # Show first 5 books
        if count > 0:
            print("\nSample books:")
            cursor.execute("SELECT id, title, author, isbn FROM books LIMIT 5;")
            for book in cursor.fetchall():
                print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, ISBN: {book[3]}")
        
        # Check if transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        if not cursor.fetchone():
            print("\nWARNING: 'transactions' table not found!")
        else:
            # Count transactions
            cursor.execute("SELECT COUNT(*) FROM transactions;")
            tx_count = cursor.fetchone()[0]
            print(f"\nFound {tx_count} transactions in the database.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_books()
