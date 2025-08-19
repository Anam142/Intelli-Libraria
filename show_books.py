import sqlite3

def show_books():
    try:
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Get column names
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get all books
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        
        # Print header
        print("\nAll Books in Database:")
        print("-" * 120)
        print("ID  | Title                                     | Authors                    | ISBN           | Edition | Stock")
        print("-" * 120)
        
        # Print each book
        for book in books:
            book_id = str(book[0])
            title = (book[2][:40] + '..') if len(book[2]) > 40 else book[2].ljust(42)  # title is at index 2
            authors = (book[3][:25] + '..') if len(book[3]) > 25 else book[3].ljust(27)  # authors at index 3
            isbn = book[4][:15].ljust(15) if book[4] else 'N/A'.ljust(15)  # isbn at index 4
            # Add empty strings for edition and stock since they don't exist in the database
            edition = 'N/A'.ljust(8)
            stock = 'N/A'.ljust(5)
            
            print(f"{book_id.ljust(3)} | {title} | {authors} | {isbn} | {edition} | {stock}")
        
        print("-" * 120)
        print(f"Total books: {len(books)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    show_books()
