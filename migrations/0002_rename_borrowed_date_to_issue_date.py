import os
import sqlite3

def migrate():
    db_path = 'intelli_libraria.db'
    print(f"Running migration: Rename borrowed_date to issue_date in transactions table")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if borrowed_date column exists
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'borrowed_date' in columns and 'issue_date' not in columns:
            print("Renaming borrowed_date to issue_date...")
            # SQLite doesn't support RENAME COLUMN directly, so we need to:
            # 1. Create a new table with the correct schema
            # 2. Copy data from old table to new table
            # 3. Drop old table
            # 4. Rename new table to old table name
            
            # Get the current schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
            schema = cursor.fetchone()[0]
            
            # Create new schema with issue_date instead of borrowed_date
            new_schema = schema.replace('borrowed_date', 'issue_date')
            
            # Create a temporary table with the new schema
            cursor.execute("PRAGMA foreign_keys=off")
            cursor.execute("BEGIN TRANSACTION")
            
            # Create new table with _new suffix
            cursor.execute(new_schema.replace('CREATE TABLE transactions', 'CREATE TABLE transactions_new'))
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO transactions_new (
                    id, user_id, book_copy_id, issue_date, due_date, 
                    returned_date, fine_amount, status, created_at, updated_at
                )
                SELECT 
                    id, user_id, book_copy_id, borrowed_date, due_date, 
                    returned_date, fine_amount, status, created_at, updated_at
                FROM transactions
            ''')
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE transactions")
            cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
            
            # Recreate indexes and triggers if any
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
                CREATE INDEX IF NOT EXISTS idx_transactions_book_copy_id ON transactions(book_copy_id);
                CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
            """)
            
            conn.commit()
            cursor.execute("PRAGMA foreign_keys=on")
            print("✓ Successfully renamed borrowed_date to issue_date")
            
        elif 'issue_date' in columns:
            print("✓ issue_date column already exists, no migration needed")
        else:
            print("✓ No borrowed_date column found, assuming schema is up to date")
            
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if migrate():
        print("Migration completed successfully")
    else:
        print("Migration failed")
