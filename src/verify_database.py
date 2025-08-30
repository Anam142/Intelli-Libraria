"""
Database verification script for Intelli-Libraria.
Checks if the database exists and has the required tables.
"""
import os
import sys
import sqlite3
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'database_verification.log')
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_DIR = PROJECT_ROOT / 'data'
DB_NAME = 'library.db'
DB_PATH = DB_DIR / DB_NAME
REQUIRED_TABLES = ['users', 'books', 'transactions']

# Ensure logs directory exists
(DB_DIR.parent / 'logs').mkdir(exist_ok=True)

def check_database_exists() -> Tuple[bool, Optional[sqlite3.Connection]]:
    """
    Check if the database file exists and can be connected to.
    
    Returns:
        Tuple of (exists: bool, connection: Optional[sqlite3.Connection])
    """
    try:
        # Ensure the data directory exists
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and is a valid SQLite database
        if not DB_PATH.exists():
            logger.error(f"Database file not found at: {DB_PATH}")
            return False, None
            
        # Try to connect to verify it's a valid SQLite database
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=rw', uri=True)
        logger.info(f"✅ Database found and accessible at: {DB_PATH}")
        return True, conn
        
    except sqlite3.Error as e:
        logger.error(f"❌ Error accessing database at {DB_PATH}: {e}")
        return False, None
    except Exception as e:
        logger.error(f"❌ Unexpected error checking database: {e}")
        return False, None

def check_table_exists(cursor, table_name: str) -> bool:
    """Check if a specific table exists in the database."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None

def verify_database_structure() -> bool:
    """
    Verify that all required tables exist in the database.
    
    Returns:
        bool: True if all tables exist and are accessible, False otherwise
    """
    db_exists, conn = check_database_exists()
    if not db_exists or not conn:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        # Check for missing tables
        missing_tables = [tbl for tbl in REQUIRED_TABLES if tbl not in existing_tables]
        
        if missing_tables:
            logger.error(f"❌ Missing required tables: {', '.join(missing_tables)}")
            return False
            
        logger.info("✅ All required tables exist in the database")
        
        # Get table info for debugging
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        logger.info("\n=== Database Schema ===")
        for table_name, table_sql in cursor.fetchall():
            logger.info(f"\nTable: {table_name}")
            logger.info(f"SQL: {table_sql}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            logger.info(f"Columns: {', '.join(columns)}")
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"❌ Error verifying database structure: {e}")
        return False
    finally:
        if conn:
            conn.close()
            logger.error(f"❌ Missing required tables: {', '.join(missing_tables)}")
            return False
            
        logger.info("✅ All required tables exist")
        
        # Check transactions table structure
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info("\nTransactions table structure:")
        logger.info("\n".join([f"  - {col}" for col in columns]))
        
        # Check status values in transactions if the table exists
        if 'transactions' in existing_tables:
            try:
                cursor.execute("SELECT DISTINCT status FROM transactions")
                statuses = [row[0] for row in cursor.fetchall()]
                logger.info(f"\nCurrent status values in transactions: {statuses}")
            except sqlite3.Error as e:
                logger.warning(f"Could not check transaction statuses: {e}")
        
        return True
        
    except sqlite3.Error as e:

def main() -> None:
    """
    Main function to run database verification.
    
    This script can be run directly to check the database status.
    Returns True if verification passes, False otherwise.
    """
    print("=== Database Verification ===")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Checking database at: {DB_PATH}")
    
    # Ensure the data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    if verify_database_structure():
        print("\n✅ Database verification successful!")
        return True
    else:
        print("\n❌ Database verification failed. Please check the logs.")
        print(f"Log file: {PROJECT_ROOT / 'logs' / 'database_verification.log'}")
        return False

if __name__ == "__main__":
    main()
