import sqlite3
import os

def check_database():
    db_path = 'intelli_libraria.db'
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found!")
        return
    
    print(f"Found database: {os.path.abspath(db_path)}")
    print(f"Size: {os.path.getsize(db_path) / 1024:.2f} KB\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database!")
            return
            
        print("Tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\n=== {table_name} ===")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows: {count}")
            
            # Display first few rows if any
            if count > 0:
                print("\nFirst 5 rows:")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                rows = cursor.fetchall()
                for row in rows:
                    print(f"  {row}")
        
        # Check if books table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books';")
        if not cursor.fetchone():
            print("\nERROR: 'books' table not found in the database!")
        else:
            # Check if there are any books
            cursor.execute("SELECT COUNT(*) FROM books;")
            book_count = cursor.fetchone()[0]
            print(f"\nTotal books in database: {book_count}")
            
            if book_count > 0:
                print("\nSample books:")
                cursor.execute("SELECT id, title, author, isbn FROM books LIMIT 5;")
                for book in cursor.fetchall():
                    print(f"  ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, ISBN: {book[3]}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database()
