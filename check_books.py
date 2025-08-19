import sqlite3

def check_books():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get table info
        print("\n=== Table Structure ===")
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        print("Columns in books table:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Get number of books
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        print(f"\nNumber of books in database: {count}")
        
        # Get sample books if any exist
        if count > 0:
            print("\nSample books (first 5):")
            cursor.execute("SELECT * FROM books LIMIT 5")
            books = cursor.fetchall()
            for book in books:
                print(book)
        
    except Exception as e:
        print(f"Error checking books: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_books()
