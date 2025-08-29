import sqlite3
import os
from datetime import datetime

def backup_database():
    """Create a timestamped backup of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"library_backup_{timestamp}.db"
    
    try:
        with sqlite3.connect('library.db') as src:
            with sqlite3.connect(backup_file) as dst:
                src.backup(dst)
        print(f"✅ Database backed up to: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return None

def check_and_fix():
    try:
        # Create backup first
        backup_file = backup_database()
        if not backup_file:
            print("Cannot proceed without a backup.")
            return
            
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        print("\n=== Checking Database Status ===")
        
        # 1. Check current table structure
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        table_sql = cursor.fetchone()
        if table_sql:
            print("\nCurrent table definition:")
            print(table_sql[0])
        
        # 2. Check current status values
        cursor.execute("SELECT DISTINCT status, LENGTH(status) as len FROM transactions")
        statuses = cursor.fetchall()
        print("\nCurrent status values:")
        for status, length in statuses:
            print(f"  - '{status}' (length: {length})")
        
        # 3. Fix the table if needed
        print("\n=== Fixing Transactions Table ===")
        
        # Create a new table with correct constraints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions_new (
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
        
        # Copy data with fixed status values
        cursor.execute("""
            INSERT INTO transactions_new
            SELECT 
                id, user_id, book_id, borrow_date, due_date, return_date,
                LOWER(TRIM(status)) as status,
                created_at, updated_at
            FROM transactions
            WHERE LOWER(TRIM(status)) IN ('borrowed', 'returned', 'overdue', 'lost')
        """)
        
        # Count rows processed
        rows_processed = cursor.rowcount
        print(f"Processed {rows_processed} rows")
        
        # Verify the new table
        cursor.execute("SELECT COUNT(*) FROM transactions_new")
        new_count = cursor.fetchone()[0]
        print(f"New table has {new_count} rows")
        
        if rows_processed == new_count:
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
            
            # Verify final status values
            cursor.execute("SELECT DISTINCT status FROM transactions")
            final_statuses = [row[0] for row in cursor.fetchall()]
            print(f"\n✅ Final status values: {final_statuses}")
            
            conn.commit()
            print("\n✅ Database fixed successfully!")
            print(f"A backup of your original database was saved as: {backup_file}")
        else:
            print("\n❌ Row count mismatch. Rolling back changes...")
            conn.rollback()
            
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("This script will check and fix the transactions table in your database.")
    print("A backup will be created automatically before making any changes.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    check_and_fix()
