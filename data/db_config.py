"""
Database configuration for Intelli-Libraria.
Provides consistent database paths and connection handling.
"""
import os
import sys
import sqlite3
from pathlib import Path
import logging
from typing import Optional, Dict, List, Any, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
PROJECT_ROOT = Path(__file__).parent.absolute()
DB_DIR = PROJECT_ROOT / 'data'
DB_NAME = 'library.db'
DB_PATH = str(DB_DIR / DB_NAME)

# Ensure the data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Required tables and their expected columns
REQUIRED_TABLES = {
    'users': ['id', 'username', 'email', 'password_hash', 'role'],
    'books': ['id', 'title', 'author', 'isbn', 'available_copies', 'total_copies'],
    'transactions': ['id', 'user_id', 'book_id', 'issue_date', 'due_date', 
                    'return_date', 'status', 'created_at', 'updated_at']
}

def ensure_database_path() -> str:
    """Ensure the database directory exists and return the full path."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Get a database connection with proper configuration.
    
    Args:
        db_path: Optional path to the database file. Uses DB_PATH if not provided.
        
    Returns:
        A configured SQLite database connection
        
    Raises:
        sqlite3.Error: If connection cannot be established
    """
    try:
        path = db_path or DB_PATH
        conn = sqlite3.connect(path)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Better transaction handling
        conn.isolation_level = None  # Use autocommit mode
        # Better concurrency
        conn.execute("PRAGMA journal_mode = WAL")
        # Better performance for read-heavy applications
        conn.execute("PRAGMA cache_size = -2000")  # 2MB cache
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database at {db_path or DB_PATH}: {e}")
        raise

def verify_database() -> bool:
    """Verify that the database and all required tables exist."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at: {DB_PATH}")
        return False
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(REQUIRED_TABLES.keys()) - existing_tables
            if missing_tables:
                logger.error(f"Missing required tables: {', '.join(missing_tables)}")
                return False
                
            # Verify table structures
            for table, columns in REQUIRED_TABLES.items():
                cursor.execute(f"PRAGMA table_info({table})")
                table_columns = {row[1] for row in cursor.fetchall()}
                missing_columns = set(columns) - table_columns
                if missing_columns:
                    logger.error(f"Table '{table}' is missing columns: {', '.join(missing_columns)}")
                    return False
            
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Database error during verification: {e}")
        return False

def require_database():
    """Decorator to ensure database is available before running a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not verify_database():
                logger.error("Database verification failed. Cannot proceed.")
                sys.exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Export commonly used items
__all__ = ['get_connection', 'verify_database', 'require_database', 'DB_PATH']
