import sqlite3
import os

def migrate_database():
    db_path = 'intelli_libraria.db'
    backup_path = 'intelli_libraria_backup.db'
    
    print("Starting database migration...")
    print(f"Database path: {os.path.abspath(db_path)}")
    
    try:
        # Create a backup of the database
        if os.path.exists(db_path):
            print("Creating backup...")
            with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            print(f"Backup created at: {os.path.abspath(backup_path)}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the transactions table exists and has the borrowed_date column
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'borrowed_date' in columns and 'issue_date' not in columns:
            print("Migrating 'borrowed_date' to 'issue_date'...")
            
            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # Rename the column using a temporary table
                cursor.execute('''
                    CREATE TABLE transactions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        due_date TIMESTAMP,
                        return_date TIMESTAMP,
                        status TEXT DEFAULT 'Borrowed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (book_id) REFERENCES books(id)
                    )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                    INSERT INTO transactions_new 
                    (id, user_id, book_id, issue_date, due_date, return_date, status, created_at)
                    SELECT 
                        id, user_id, book_id, borrowed_date, due_date, return_date, status, created_at
                    FROM transactions
                ''')
                
                # Drop old table and rename new one
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
                
                # Commit the transaction
                conn.commit()
                print("✓ Successfully migrated 'borrowed_date' to 'issue_date'")
                
            except Exception as e:
                conn.rollback()
                print(f"Error during migration: {e}")
                raise
                
        elif 'issue_date' in columns:
            print("✓ Database already uses 'issue_date' column")
        else:
            print("✓ No migration needed - database is up to date")
            
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        print("Please check if the database is not in use and try again.")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("=== Database Migration Tool ===\n")
    if migrate_database():
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✗ Migration failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
