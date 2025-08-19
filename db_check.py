import sqlite3

def check_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Check if books table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
        if not cursor.fetchone():
            print("Error: 'books' table does not exist in the database.")
            return
        
        # Get table structure
        cursor.execute('PRAGMA table_info(books)')
        columns = cursor.fetchall()
        print("\nBooks table structure:")
        print("ID | Name             | Type    | Not Null | Default | PK")
        print("-" * 60)
        for col in columns:
            cid = col['cid']
            name = col['name']
            col_type = col['type']
            not_null = bool(col['notnull'])
            default = str(col['dflt_value'] or 'NULL')
            pk = col['pk']
            print(f"{cid:2} | {name:15} | {col_type:7} | {not_null:8} | {default:7} | {pk}")
        
        # Count books
        cursor.execute("SELECT COUNT(*) as count FROM books")
        count = cursor.fetchone()['count']
        print(f"\nTotal books in database: {count}")
        
        if count > 0:
            # Get all books
            cursor.execute("SELECT * FROM books")
            print("\nFirst 10 books:")
            print("ID | Title                                 | Author                    | ISBN           | Edition | Stock")
            print("-" * 100)
            
            for row in cursor.fetchmany(10):
                book_id = row['id']
                title = (row['title'][:35] + '..') if 'title' in row and row['title'] and len(row['title']) > 35 else (row['title'] if 'title' in row and row['title'] else '').ljust(37)
                author = (row['author'][:25] + '..') if 'author' in row and row['author'] and len(row['author']) > 25 else (row['author'] if 'author' in row and row['author'] else '').ljust(27)
                authors = (row['authors'][:25] + '..') if 'authors' in row and row['authors'] and len(row['authors']) > 25 else (row['authors'] if 'authors' in row and row['authors'] else '').ljust(27)
                isbn = row.get('isbn', '').ljust(15) if 'isbn' in row and row['isbn'] else 'N/A'.ljust(15)
                edition = row.get('edition', 'N/A').ljust(7) if 'edition' in row else 'N/A'.ljust(7)
                stock = str(row.get('stock', 'N/A')).ljust(5) if 'stock' in row else 'N/A'.ljust(5)
                
                print(f"{str(book_id).ljust(2)} | {title} | {author or authors} | {isbn} | {edition} | {stock}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
