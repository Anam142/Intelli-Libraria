import sqlite3

def fix_updated_column():
    db_path = 'intelli_libraria.db'
    conn = None
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Fixing 'updated' column in transactions table ===\n")
        
        # Check if 'updated' column exists in transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'updated' not in columns and 'updated_at' not in columns:
            print("Adding 'updated_at' column to transactions table...")
            try:
                cursor.execute("ALTER TABLE transactions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("Added 'updated_at' column to transactions table")
            except sqlite3.OperationalError as e:
                print(f"Error adding column: {e}")
        
        # Check if 'updated' column exists and needs to be renamed
        if 'updated' in columns and 'updated_at' not in columns:
            print("Renaming 'updated' column to 'updated_at'...")
            try:
                # SQLite doesn't support RENAME COLUMN directly, so we need to recreate the table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date TIMESTAMP NOT NULL,
                        return_date TIMESTAMP,
                        status TEXT DEFAULT 'Borrowed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (book_id) REFERENCES books (id)
                    )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                    INSERT INTO transactions_new 
                    (id, user_id, book_id, issue_date, due_date, return_date, status, created_at, updated_at)
                    SELECT id, user_id, book_id, issue_date, due_date, return_date, status, created_at, 
                           COALESCE(updated, CURRENT_TIMESTAMP) 
                    FROM transactions
                ''')
                
                # Drop old table and rename new one
                cursor.execute("DROP TABLE transactions")
                cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
                print("Successfully renamed 'updated' to 'updated_at'")
                
            except sqlite3.Error as e:
                print(f"Error renaming column: {e}")
                conn.rollback()
                return
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(transactions)")
        print("\n=== Current transactions table columns ===")
        for col in cursor.fetchall():
            print(f"{col[1]} ({col[2]}) - Default: {col[4]}")
        
        conn.commit()
        print("\n✅ Database schema is now up to date")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_updated_column()
    input("\nPress Enter to exit...")
