import sqlite3

def fix_transaction_constraint():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("=== Starting Database Fix ===")
        
        # 1. Create a backup of the current table
        print("1. Creating backup of transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions_backup AS 
            SELECT * FROM transactions
        """)
        
        # 2. Create a new table with the correct constraint
        print("2. Creating new transactions table with correct constraint...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)
        
        # 3. Copy data from old table to new table with fixed status values
        print("3. Migrating data with fixed status values...")
        cursor.execute("""
            INSERT INTO transactions_new (
                id, user_id, book_id, issue_date, due_date, 
                return_date, status, created_at, updated_at
            )
            SELECT 
                id, user_id, book_id, issue_date, due_date, 
                return_date, 
                LOWER(TRIM(status)) as status,
                created_at, updated_at
            FROM transactions
        """)
        
        # 4. Drop the old table and rename the new one
        print("4. Replacing old table with new one...")
        cursor.execute("DROP TABLE transactions")
        cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
        
        # 5. Recreate indexes if they existed
        print("5. Recreating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_book_id 
            ON transactions(book_id)
        """)
        
        # 6. Verify the changes
        print("6. Verifying the changes...")
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"Current status values in database: {statuses}")
        
        # Commit the changes
        conn.commit()
        print("\n✅ Database update completed successfully!")
        print("A backup of your original data is available in 'transactions_backup' table.")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Error: {e}")
        print("The database has been rolled back to its original state.")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("This script will fix the status values in your transactions table.")
    print("It will create a backup of your current data before making any changes.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    fix_transaction_constraint()
