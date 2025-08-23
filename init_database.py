import os
import sqlite3
from pathlib import Path

def init_database():
    # Get the database path
    try:
        from data.database import DB_PATH, MIGRATIONS_DIR
    except ImportError:
        # Fallback if the module import fails
        DB_PATH = os.path.join(os.path.dirname(__file__), 'intelli_libraria.db')
        MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), 'data', 'migrations')
    
    print(f"Initializing database at: {DB_PATH}")
    print(f"Migrations directory: {MIGRATIONS_DIR}")
    
    # Create the database directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        print("Removing existing database...")
        os.remove(DB_PATH)
    
    # Connect to the database (this will create it)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Database created successfully!")
    
    # Create migrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Apply migrations in order
    migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) 
                            if f.endswith('.sql') and f != '000_initial.sql'])
    
    for migration_file in migration_files:
        print(f"\nApplying migration: {migration_file}")
        try:
            with open(os.path.join(MIGRATIONS_DIR, migration_file), 'r') as f:
                sql = f.read()
            
            # Execute the migration
            cursor.executescript(sql)
            
            # Record the migration
            cursor.execute("INSERT OR IGNORE INTO migrations (name) VALUES (?)", (migration_file,))
            conn.commit()
            
            print(f"Successfully applied migration: {migration_file}")
            
        except Exception as e:
            conn.rollback()
            print(f"Error applying migration {migration_file}: {str(e)}")
            return False
    
    # Verify the users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(f"\nFound {len(users)} users in the database:")
    for user in users:
        print(f"- {user['username']} ({user['email']}) - {user['role']}")
    
    # Close the connection
    conn.close()
    print("\nDatabase initialization complete!")
    return True

if __name__ == "__main__":
    init_database()
