import sqlite3
import os

def migrate():
    db_path = 'intelli_libraria.db'
    backup_path = 'intelli_libraria_backup_before_rename.db'
    
    print("=== Starting migration: Rename borrowed_date to issue_date ===")
    print(f"Database: {os.path.abspath(db_path)}")
    
    try:
        # Create a backup of the database
        if os.path.exists(db_path):
            print("Creating backup...")
            with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            print(f"Backup created at: {os.path.abspath(backup_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'borrowed_date' in columns and 'issue_date' not in columns:
            print("\nStep 1: Creating new transactions table with issue_date column...")
            
            # Get the current schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
            schema = cursor.fetchone()[0]
            
            # Create new schema with issue_date instead of borrowed_date
            new_schema = schema.replace('borrowed_date', 'issue_date')
            
            # Create a temporary table with the new schema
            cursor.execute("PRAGMA foreign_keys=off")
            cursor.execute("BEGIN TRANSACTION")
            
            # Create new table with the updated schema
            cursor.execute(new_schema.replace('CREATE TABLE transactions', 'CREATE TABLE transactions_new'))
            
            # Copy data from old table to new table
            print("Step 2: Migrating data to new schema...")
            cursor.execute('''
                INSERT INTO transactions_new 
                SELECT 
                    id, user_id, book_id, borrowed_date, due_date, 
                    return_date, status, fine_amount, fine_paid, created_at, updated_at
                FROM transactions
            ''')
            
            # Drop old table and rename new one
            print("Step 3: Updating database schema...")
            cursor.execute("DROP TABLE transactions")
            cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
            
            # Recreate indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
                ON transactions(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_book_id 
                ON transactions(book_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_status 
                ON transactions(status)
            ''')
            
            conn.commit()
            cursor.execute("PRAGMA foreign_keys=on")
            
            print("\n✓ Successfully renamed 'borrowed_date' to 'issue_date'")
            
        elif 'issue_date' in columns:
            print("\n✓ 'issue_date' column already exists")
        else:
            print("\n✗ Neither 'borrowed_date' nor 'issue_date' column found in transactions table")
            return False
            
        # Verify the changes
        cursor.execute("PRAGMA table_info(transactions)")
        print("\nUpdated transactions table schema:")
        for col in cursor.fetchall():
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Migration Tool ===\n")
    if migrate():
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✗ Migration failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
