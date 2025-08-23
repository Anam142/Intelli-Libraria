import os
import sqlite3
from pathlib import Path

def reset_database():
    # Remove existing database files
    db_files = ['library.db', 'intelli_libraria.db', 'data/intelli_libraria.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                print(f"Removed existing database: {db_file}")
            except Exception as e:
                print(f"Error removing {db_file}: {e}")

def apply_migrations():
    # Get all migration files in order
    migration_dir = Path('data/migrations')
    migration_files = sorted([f for f in migration_dir.glob('*.sql')])
    
    # Connect to the database
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    try:
        # Apply each migration
        for migration_file in migration_files:
            print(f"Applying migration: {migration_file}")
            with open(migration_file, 'r') as f:
                sql_script = f.read()
            
            # Split the script into individual statements
            statements = [s.strip() for s in sql_script.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    cursor.executescript(statement + ';')
                except sqlite3.Error as e:
                    print(f"Error executing statement in {migration_file}: {e}")
                    print(f"Statement: {statement}")
                    # Continue with next statement
            
            conn.commit()
            print(f"Successfully applied migration: {migration_file}")
            
    except Exception as e:
        print(f"Error applying migrations: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Resetting database...")
    reset_database()
    
    print("\nApplying migrations...")
    apply_migrations()
    
    print("\nDatabase reset and initialized successfully!")
