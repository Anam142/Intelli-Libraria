import sqlite3

def fix_books_table():
    db_path = 'intelli_libraria_fresh.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Fixing Books Table ===\n")
        
        # Check if stock column exists
        cursor.execute("PRAGMA table_info(books);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'stock' not in columns:
            print("Adding 'stock' column to books table...")
            cursor.execute("ALTER TABLE books ADD COLUMN stock INTEGER DEFAULT 0;")
            
            # If there's an available_quantity column, copy its values to stock
            if 'available_quantity' in columns:
                print("Copying values from available_quantity to stock...")
                cursor.execute("UPDATE books SET stock = available_quantity;")
            else:
                # Set a default stock value for existing books
                cursor.execute("UPDATE books SET stock = 1 WHERE stock IS NULL OR stock = 0;")
            
            conn.commit()
            print("Successfully added and initialized 'stock' column.")
        else:
            print("'stock' column already exists in books table.")
        
        # Verify the changes
        cursor.execute("SELECT id, title, stock FROM books LIMIT 5;")
        books = cursor.fetchall()
        
        if books:
            print("\nSample book records:")
            for book in books:
                print(f"ID: {book[0]}, Title: {book[1]}, Stock: {book[2]}")
        
        print("\n✅ Books table is ready for borrowing.")
        
    except Exception as e:
        print(f"Error fixing books table: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_books_table()
    input("\nPress Enter to exit...")
