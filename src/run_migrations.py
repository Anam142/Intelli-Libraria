import os
import sqlite3
from pathlib import Path

def run_migrations():
    # Get the database path
    try:
        from data.database import DB_PATH, MIGRATIONS_DIR
    except ImportError:
        # Fallback if the module import fails
        DB_PATH = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
        MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'data', 'migrations')
    
    print(f"Using database: {DB_PATH}")
    print(f"Migrations directory: {MIGRATIONS_DIR}")
    
    # Create the database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create migrations table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Get already applied migrations
    cursor.execute("SELECT name FROM migrations")
    applied_migrations = {row['name'] for row in cursor.fetchall()}
    
    # Get all migration files
    migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) 
                            if f.endswith('.sql') and f != '000_initial.sql'])
    
    # Apply migrations
    for migration_file in migration_files:
        if migration_file not in applied_migrations:
            print(f"\nApplying migration: {migration_file}")
            
            try:
                # Read the migration file
                with open(os.path.join(MIGRATIONS_DIR, migration_file), 'r') as f:
                    sql = f.read()
                
                # Execute the migration
                cursor.executescript(sql)
                
                # Record the migration
                cursor.execute("INSERT INTO migrations (name) VALUES (?)", (migration_file,))
                conn.commit()
                
                print(f"Successfully applied migration: {migration_file}")
                
            except Exception as e:
                conn.rollback()
                print(f"Error applying migration {migration_file}: {str(e)}")
                return False
        else:
            print(f"Skipping already applied migration: {migration_file}")
    
    # Close the connection
    conn.close()
    print("\nAll migrations applied successfully!")
    return True

if __name__ == "__main__":
    run_migrations()
