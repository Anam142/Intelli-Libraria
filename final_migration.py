import sqlite3
import os
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"intelli_libraria_backup_{timestamp}.db"
    
    try:
        # Create a backup of the database
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print(f"✅ Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create database backup: {e}")
        return False

def run_migration():
    db_path = 'intelli_libraria.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file '{db_path}' not found!")
        return False
    
    print("=== Starting Database Migration ===\n")
    
    # Create backup first
    if not backup_database(db_path):
        print("\n❌ Migration aborted due to backup failure")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if transactions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
        if not cursor.fetchone():
            print("❌ Error: 'transactions' table not found!")
            return False
        
        # Get current columns
        cursor.execute("PRAGMA table_info(transactions);")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Check if we need to migrate
        if 'issue_date' in columns and 'borrow_date' not in columns:
            print("✅ Database already uses 'issue_date' column")
            return True
            
        if 'borrow_date' in columns:
            print("🔍 Found 'borrow_date' column, migrating to 'issue_date'...")
            
            # Create a new temporary table with the correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP NOT NULL,
                    return_date TIMESTAMP,
                    status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) DEFAULT 'borrowed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO transactions_new 
                (id, user_id, book_id, issue_date, due_date, return_date, status, created_at, updated_at)
                SELECT 
                    id, 
                    user_id, 
                    book_id,
                    borrow_date as issue_date,
                    due_date,
                    return_date,
                    status,
                    created_at,
                    updated_at
                FROM transactions
            ''')
            
            # Drop the old table
            cursor.execute("DROP TABLE transactions;")
            
            # Rename new table to original name
            cursor.execute("ALTER TABLE transactions_new RENAME TO transactions;")
            
            # Recreate indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);")
            
            print("✅ Successfully migrated 'borrow_date' to 'issue_date'")
            
        # Verify the migration
        cursor.execute("PRAGMA table_info(transactions);")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'issue_date' in columns and 'borrow_date' not in columns:
            print("✅ Verification: Database now uses 'issue_date' column")
            
            # Check for any views or triggers that might reference borrow_date
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type IN ('view', 'trigger') AND sql LIKE '%borrow_date%';")
            problematic_objects = cursor.fetchall()
            
            if problematic_objects:
                print("\n⚠️  Found views or triggers that reference 'borrow_date':")
                for obj in problematic_objects:
                    print(f"  - {obj['name']} (type: {obj['type']})")
                print("\nYou may need to manually update these objects to use 'issue_date'.")
            
            conn.commit()
            return True
        else:
            print("❌ Verification failed: 'issue_date' column not found after migration")
            return False
            
    except sqlite3.Error as e:
        print(f"\n❌ Database error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Intelli Libraria Database Migration Tool ===\n")
    
    if run_migration():
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
