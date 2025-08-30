import sqlite3
import os

def fix_borrowed_date_issue():
    db_path = 'intelli_libraria.db'
    backup_path = 'intelli_libraria_backup_before_fix.db'
    
    # Create backup of current database
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup at: {backup_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if transactions table exists and has the correct columns
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # If issue_date doesn't exist but borrowed_date does, rename it
        if 'borrowed_date' in columns and 'issue_date' not in columns:
            print("Fixing column name from 'borrowed_date' to 'issue_date'...")
            
            # Get the current schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
            schema = cursor.fetchone()[0]
            
            # Create new table with correct column name
            new_schema = schema.replace('borrowed_date', 'issue_date')
            
            # Create a new table with the correct schema
            cursor.execute("PRAGMA foreign_keys=off")
            cursor.execute("ALTER TABLE transactions RENAME TO transactions_old")
            cursor.execute(new_schema)
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO transactions 
                SELECT * FROM transactions_old
            ''')
            
            # Drop the old table
            cursor.execute("DROP TABLE transactions_old")
            cursor.execute("PRAGMA foreign_keys=on")
            print("✓ Successfully renamed 'borrowed_date' to 'issue_date'")
        
        # Update any triggers that might reference the old column name
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
        for trigger_name, trigger_sql in cursor.fetchall():
            if 'borrowed_date' in trigger_sql:
                cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                new_trigger_sql = trigger_sql.replace('borrowed_date', 'issue_date')
                cursor.execute(new_trigger_sql)
                print(f"✓ Updated trigger: {trigger_name}")
        
        # Commit changes
        conn.commit()
        print("✅ Database schema has been fixed successfully!")
        
        # Verify the fix
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        print("\nCurrent transactions table columns:", ", ".join(columns))
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== Fixing 'borrowed_date' column issue ===\n")
    fix_borrowed_date_issue()
    input("\nPress Enter to exit...")
