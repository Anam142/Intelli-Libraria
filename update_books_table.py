import sqlite3

def update_books_table():
    try:
        # Connect to the database
        conn = sqlite3.connect('intelli_libraria.db')
        cursor = conn.cursor()
        
        # Check if available_quantity column exists
        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'available_quantity' not in columns:
            print("Adding 'available_quantity' column to 'books' table...")
            # Add the column with a default value of the current quantity
            cursor.execute('''
                ALTER TABLE books 
                ADD COLUMN available_quantity INTEGER DEFAULT 0
            ''')
            
            # Initialize available_quantity with the current quantity for existing books
            cursor.execute('''
                UPDATE books 
                SET available_quantity = quantity 
                WHERE available_quantity IS NULL OR available_quantity = 0
            ''')
            
            conn.commit()
            print("Successfully updated 'books' table.")
        else:
            print("'available_quantity' column already exists in 'books' table.")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_books_table()
    print("Database update complete. You can now run the application again.")
