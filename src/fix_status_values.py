import sqlite3

def fix_status_values():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('library.db')
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        print("=== Fixing Status Values ===")
        
        # 1. First, fix any existing status values
        print("Fixing existing status values...")
        cursor.execute("""
            UPDATE transactions 
            SET status = LOWER(TRIM(status))
            WHERE status != LOWER(TRIM(status))
        """)
        print(f"Updated {cursor.rowcount} rows with inconsistent status values")
        
        # 2. Now update the CHECK constraint
        print("Updating CHECK constraint...")
        
        # Create a new table with the correct constraint
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
        
        # Copy data to the new table
        cursor.execute("""
            INSERT INTO transactions_new
            SELECT * FROM transactions
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
        
        # Verify the changes
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"\nCurrent status values: {statuses}")
        
        conn.commit()
        print("\n✅ Status values and constraints have been fixed!")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_status_values()
