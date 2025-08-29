"""
Database utility functions for Intelli-Libraria.
Ensures consistent database access across all scripts.
"""
import os
import sys
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the correct database path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'library.db')

def get_db_path() -> str:
    """Get the absolute path to the database file."""
    return os.path.abspath(DB_PATH)

def verify_database() -> bool:
    """
    Verify that the database and required tables exist.
    Returns True if all checks pass, False otherwise.
    """
    try:
        # Check if database file exists
        if not os.path.exists(DB_PATH):
            logger.error(f"❌ Database file not found at: {DB_PATH}")
            return False
            
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            required_tables = ['users', 'books', 'transactions']
            missing_tables = []
            
            # Check for required tables
            for table in required_tables:
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                    (table,)
                )
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                logger.error(f"❌ Missing required tables: {', '.join(missing_tables)}")
                return False
                
            logger.info("✅ Database verification successful")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"❌ Database error during verification: {e}")
        return False

def get_connection() -> sqlite3.Connection:
    """
    Get a database connection with proper configuration.
    Exits the program if connection fails.
    """
    try:
        # Ensure the data directory exists
        os.makedirs(DB_DIR, exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        return conn
        
    except sqlite3.Error as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

def check_required_tables():
    """Check if required tables exist and exit if they don't."""
    if not verify_database():
        logger.error("""
        Database verification failed. Please ensure:
        1. The database file exists at: %s
        2. All required tables exist (users, books, transactions)
        """, DB_PATH)
        sys.exit(1)

if __name__ == "__main__":
    print(f"Database path: {get_db_path()}")
    check_required_tables()
