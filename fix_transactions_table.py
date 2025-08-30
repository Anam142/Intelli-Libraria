import sqlite3
import os

def fix_transactions_table():
    # Backup existing database
    if os.path.exists('intelli_libraria.db'):
        backup_count = 1
        while os.path.exists(f'intelli_libraria_backup_{backup_count}.db'):
            backup_count += 1
        os.rename('intelli_libraria.db', f'intelli_libraria_backup_{backup_count}.db')
        print(f"Created backup: intelli_libraria_backup_{backup_count}.db")
    
    # Create new database with correct schema
    conn = sqlite3.connect('intelli_libraria.db')
    cursor = conn.cursor()
    
    # Create transactions table with correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP NOT NULL,
        return_date TIMESTAMP,
        status TEXT DEFAULT 'Borrowed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (book_id) REFERENCES books (id)
    )
    ''')
    
    # Create triggers to update updated_at
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_transactions_timestamp
    AFTER UPDATE ON transactions
    BEGIN
        UPDATE transactions 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE id = NEW.id;
    END;
    ''')
    
    print("✅ Created transactions table with correct schema")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("\nPlease restart your application. The 'updated' column error should be resolved.")

if __name__ == "__main__":
    print("Fixing transactions table...")
    fix_transactions_table()
    input("\nPress Enter to exit...")
