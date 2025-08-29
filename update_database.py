import sqlite3
import os
from pathlib import Path

def apply_migrations():
    # Get the database path
    db_path = Path(__file__).parent / "data" / "library.db"
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Check if the transactions table exists and its current structure
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # If the table doesn't exist, create it with the new schema
        if not columns:
            print("Creating new transactions table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP NOT NULL,
                    return_date TIMESTAMP,
                    status TEXT CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')) DEFAULT 'borrowed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
            ''')
            print("Created new transactions table with updated schema.")
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);")
            print("Created indexes for better performance.")
            
        else:
            # Table exists, check if we need to migrate
            if 'borrow_date' not in columns:
                print("Updating existing transactions table...")
                
                # Rename old table
                cursor.execute("ALTER TABLE transactions RENAME TO transactions_old;")
                
                # Create new table with updated schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        book_id INTEGER NOT NULL,
                        borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                    INSERT INTO transactions 
                    (id, user_id, book_id, borrow_date, due_date, return_date, status, created_at, updated_at)
                    SELECT 
                        id, 
                        user_id, 
                        book_id,
                        COALESCE(issue_date, datetime('now')),  -- Use issue_date if exists, otherwise current time
                        due_date,
                        return_date,
                        CASE 
                            WHEN return_date IS NOT NULL THEN 'returned'
                            WHEN due_date < date('now') AND status != 'returned' THEN 'overdue'
                            ELSE COALESCE(status, 'borrowed')
                        END,
                        COALESCE(created_at, datetime('now')),
                        COALESCE(updated_at, datetime('now'))
                    FROM transactions_old
                ''')
                
                # Drop the old table
                cursor.execute("DROP TABLE IF EXISTS transactions_old;")
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);")
                
                print("Successfully migrated transactions table to the new schema.")
            else:
                print("Transactions table is already up to date.")
        
        # Commit changes
        conn.commit()
        print("Database update completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Updating database schema...")
    if apply_migrations():
        print("Database update completed successfully!")
    else:
        print("Failed to update database. Please check the error messages above.")
        exit(1)
