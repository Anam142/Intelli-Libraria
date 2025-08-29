"""
Database migration script for Intelli-Libraria.
Ensures all data is in the correct location (data/library.db).
"""
import os
import shutil
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log')
    ]
)
logger = logging.getLogger(__name__)

# Paths
OLD_DB = Path('library.db')
NEW_DB_DIR = Path('data')
NEW_DB = NEW_DB_DIR / 'library.db'

def ensure_data_directory():
    """Ensure the data directory exists."""
    try:
        NEW_DB_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {NEW_DB_DIR.absolute()}")
        return True
    except Exception as e:
        logger.error(f"Failed to create data directory: {e}")
        return False

def needs_migration() -> bool:
    """Check if migration is needed."""
    # If new database exists and is valid, no migration needed
    if NEW_DB.exists() and os.path.getsize(NEW_DB) > 0:
        logger.info("Valid database found at target location")
        return False
    
    # If old database exists, migration is needed
    if OLD_DB.exists() and os.path.getsize(OLD_DB) > 0:
        logger.info(f"Old database found at {OLD_DB}, migration needed")
        return True
    
    logger.warning("No existing database found. A new one will be created.")
    return False

def migrate_database() -> bool:
    """Migrate database from old location to new location if needed."""
    if not needs_migration():
        logger.info("No migration needed")
        return True
    
    try:
        # Ensure data directory exists
        if not ensure_data_directory():
            return False
        
        logger.info(f"Migrating database from {OLD_DB} to {NEW_DB}")
        
        # Copy the database file
        shutil.copy2(OLD_DB, NEW_DB)
        
        # Verify the new database
        try:
            with sqlite3.connect(NEW_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                logger.info(f"Found {len(tables)} tables in the new database")
                
                # Optional: Verify transactions table
                if 'transactions' in tables:
                    cursor.execute("SELECT COUNT(*) FROM transactions")
                    count = cursor.fetchone()[0]
                    logger.info(f"Found {count} transactions in the database")
        except sqlite3.Error as e:
            logger.error(f"Error verifying migrated database: {e}")
            return False
        
        logger.info("✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False

def main():
    """Main function to handle database migration."""
    print("=== Intelli-Libraria Database Migration ===\n")
    
    if migrate_database():
        print("\n✅ Migration completed successfully!")
        print(f"Database is now available at: {NEW_DB.absolute()}")
    else:
        print("\n❌ Migration failed. Please check the migration.log for details.")

if __name__ == "__main__":
    main()
