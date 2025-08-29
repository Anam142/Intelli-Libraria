import sqlite3

def fix_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        print("=== Fixing Transaction Status Values ===")
        
        # 1. First, update all status values to lowercase and trim whitespace
        cursor.execute("""
            UPDATE transactions 
            SET status = LOWER(TRIM(status))
            WHERE status != LOWER(TRIM(status))
        """)
        print(f"Fixed {cursor.rowcount} status values")
        
        # 2. Now update the CHECK constraint
        print("Updating CHECK constraint...")
        
        # Create a new table with the correct constraint
        cursor.execute("""
            CREATE TABLE transactions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)
        
        # Copy data to the new table
        cursor.execute("""
            INSERT INTO transactions_new
            SELECT * FROM transactions
            WHERE status IN ('borrowed', 'returned', 'overdue', 'lost')
        """)
        
        # Drop the old table and rename the new one
        cursor.execute("DROP TABLE transactions")
        cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
        
        # Recreate indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_book_id 
            ON transactions(book_id)
        """)
        
        # Verify
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Final status values: {statuses}")
        
        conn.commit()
        print("\n✅ Database fixed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("This script will fix the status values in your transactions table.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    fix_database()
