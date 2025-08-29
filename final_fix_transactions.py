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

def fix_transactions():
    try:
        # Create backup first
        backup_file = backup_database()
        if not backup_file:
            print("Cannot proceed without a backup.")
            return
            
        conn = sqlite3.connect('library.db')
        conn.execute("PRAGMA foreign_keys = OFF")
        cursor = conn.cursor()
        
        print("\n=== Fixing Transactions Table ===")
        
        # 1. Get the current table structure
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
        old_table_sql = cursor.fetchone()[0]
        
        # 2. Create a temporary table with the same structure but without constraints
        cursor.execute("DROP TABLE IF EXISTS transactions_temp")
        
        # Create a minimal table with just the columns
        cursor.execute("""
            CREATE TABLE transactions_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_id INTEGER,
                borrow_date TEXT,
                due_date TEXT,
                return_date TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # 3. Copy data to temp table, fixing status values
        print("Fixing status values...")
        cursor.execute("""
            INSERT INTO transactions_temp
            SELECT 
                id, user_id, book_id, borrow_date, due_date, return_date,
                LOWER(TRIM(status)) as status,
                created_at, updated_at
            FROM transactions
        """)
        
        # 4. Drop the old table and rename the temp one
        cursor.execute("DROP TABLE transactions")
        
        # 5. Create the new table with correct constraints
        print("Creating new table with correct constraints...")
        cursor.execute("""
            CREATE TABLE transactions (
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
        
        # 6. Copy data back to the new table
        print("Migrating fixed data...")
        cursor.execute("""
            INSERT INTO transactions
            SELECT * FROM transactions_temp
            WHERE status IN ('borrowed', 'returned', 'overdue', 'lost')
        """)
        
        # 7. Recreate indexes
        print("Recreating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
            ON transactions(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_book_id 
            ON transactions(book_id)
        """)
        
        # 8. Clean up
        cursor.execute("DROP TABLE IF EXISTS transactions_temp")
        
        # 9. Verify
        cursor.execute("SELECT DISTINCT status FROM transactions")
        statuses = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Final status values: {statuses}")
        
        conn.commit()
        print("\n✅ Transaction table has been fixed successfully!")
        print(f"A backup of your original database was saved as: {backup_file}")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        print("The database has been rolled back to its original state.")
    finally:
        if 'conn' in locals():
            conn.execute("PRAGMA foreign_keys = ON")
            conn.close()

if __name__ == "__main__":
    print("This script will fix the transactions table in your database.")
    print("A backup will be created automatically before making any changes.")
    input("Press Enter to continue or Ctrl+C to cancel...")
    fix_transactions()
