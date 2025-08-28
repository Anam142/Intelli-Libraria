import sqlite3

def check_and_fix_transactions():
    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()
    
    try:
        # Check if transactions table has issue_date column
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        print("Current transactions table columns:", columns)
        
        # If issue_date column doesn't exist, add it
        if 'issue_date' not in columns:
            print("Adding issue_date column to transactions table...")
            cursor.execute('''
                ALTER TABLE transactions 
                ADD COLUMN issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''')
            print("Added issue_date column successfully!")
        
        # If issue_date exists but is not nullable, modify it
        cursor.execute("PRAGMA table_info(transactions)")
        for col in cursor.fetchall():
            if col[1] == 'issue_date' and col[3] == 0:  # If not nullable
                print("Making issue_date nullable...")
                # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
                cursor.execute('''
                    CREATE TABLE transactions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date TIMESTAMP NOT NULL,
                        return_date TIMESTAMP,
                        status TEXT DEFAULT 'borrowed',
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (book_id) REFERENCES books(id)
                    )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                    INSERT INTO transactions_new 
                    (id, user_id, book_id, issue_date, due_date, return_date, status)
                    SELECT id, user_id, book_id, 
                           COALESCE(issue_date, datetime('now')), 
                           due_date, return_date, status
                    FROM transactions
                ''')
                
                # Drop old table and rename new one
                cursor.execute('DROP TABLE transactions')
                cursor.execute('ALTER TABLE transactions_new RENAME TO transactions')
                print("Successfully updated transactions table structure!")
                break
                
        conn.commit()
        print("Transactions table is ready!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_fix_transactions()
