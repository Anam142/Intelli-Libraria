import sqlite3

def check_transaction_status():
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # Get the table creation SQL to see the CHECK constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()
        
        if table_sql:
            print("\n=== Transactions Table Schema ===")
            print(table_sql[0])
        
        # Try to insert test records with different status values
        test_statuses = [
            'borrowed',  # lowercase
            'Borrowed',  # title case
            'BORROWED',  # uppercase
            'issued',    # alternative
            'Issued',
            'ISSUED'
        ]
        
        print("\n=== Testing Status Values ===")
        
        for status in test_statuses:
            try:
                cursor.execute("""
                    INSERT INTO transactions 
                    (user_id, book_id, borrow_date, due_date, status, created_at, updated_at)
                    VALUES (1, 1, '2023-01-01', '2023-01-15', ?, '2023-01-01', '2023-01-01')
                """, (status,))
                
                # If we get here, the insert was successful
                print(f"✅ Success with status: {status!r}")
                
                # Clean up
                cursor.execute("DELETE FROM transactions WHERE user_id = 1 AND book_id = 1")
                conn.commit()
                
            except sqlite3.IntegrityError as e:
                print(f"❌ Failed with status {status!r}: {str(e)}")
                conn.rollback()
        
        # Check existing status values in the database
        cursor.execute("SELECT DISTINCT status FROM transactions")
        existing_statuses = cursor.fetchall()
        
        print("\n=== Existing Status Values in Database ===")
        if existing_statuses:
            for status in existing_statuses:
                print(f"- {status[0]!r} (type: {type(status[0]).__name__})")
        else:
            print("No transactions found in the database.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_transaction_status()
