"""
Database utility functions for Intelli-Libraria.
Provides consistent database connections and verification.
"""
import os
import sqlite3
from pathlib import Path
import logging
from typing import Optional, Dict, List, Any, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DB_DIR = PROJECT_ROOT / 'data'
DB_NAME = 'library.db'
DB_PATH = str(DB_DIR / DB_NAME)

# Required tables and their expected columns
REQUIRED_TABLES = {
    'users': ['id', 'username', 'email', 'password_hash', 'role'],
    'books': ['id', 'title', 'author', 'isbn', 'available_copies', 'total_copies'],
    'transactions': ['id', 'user_id', 'book_id', 'borrow_date', 'due_date', 
                    'return_date', 'status', 'created_at', 'updated_at']
}

def get_db_path() -> str:
    """Get the absolute path to the database file."""
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

def verify_database() -> tuple[bool, str]:
    """
    Verify that the database and all required tables exist with correct schema.
    
    Returns:
        tuple[bool, str]: (is_valid, message) where:
            - is_valid: True if database is valid, False otherwise
            - message: Detailed status message
    """
    # Check if database directory exists
    if not DB_DIR.exists():
        return False, f"Database directory not found: {DB_DIR}"
    
    # Check if database file exists
    if not os.path.exists(DB_PATH):
        return False, f"Database file not found: {DB_PATH}"
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            missing_tables = set(REQUIRED_TABLES.keys()) - existing_tables
            if missing_tables:
                return False, f"Missing required tables: {', '.join(missing_tables)}"
            
            # Verify table structures
            for table, required_columns in REQUIRED_TABLES.items():
                cursor.execute(f"PRAGMA table_info({table})")
                table_columns = {row[1] for row in cursor.fetchall()}
                missing_columns = set(required_columns) - table_columns
                if missing_columns:
                    return False, f"Table '{table}' is missing columns: {', '.join(missing_columns)}"
            
            return True, "Database verification successful"
            
    except sqlite3.Error as e:
        error_msg = f"Database error during verification: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def create_database() -> bool:
    """
    Create a new database with all required tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Remove existing database if it exists
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except OSError as e:
                logger.error(f"Failed to remove existing database: {e}")
                return False
        
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create users table with all required fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'member',
                    full_name TEXT,
                    phone TEXT,
                    contact TEXT,
                    address TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL DEFAULT NULL
                )
            ''')
            
            # Create books table with all required fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    edition TEXT,
                    available_copies INTEGER DEFAULT 0,
                    total_copies INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL DEFAULT NULL
                )
            ''')
            
            # Create transactions table with all required fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    borrow_date TIMESTAMP NOT NULL,
                    due_date TIMESTAMP NOT NULL,
                    return_date TIMESTAMP NULL DEFAULT NULL,
                    status TEXT NOT NULL DEFAULT 'borrowed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                    CHECK (status IN ('borrowed', 'returned', 'overdue', 'lost'))
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_book_id ON transactions(book_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)')
            
            # Verify the database was created correctly
            conn.commit()
            is_valid, message = verify_database()
            if not is_valid:
                logger.error(f"Database verification failed after creation: {message}")
                return False
                
            logger.info("Successfully created new database with all required tables")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Error creating database: {e}")
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except OSError:
                pass
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating database: {e}")
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except OSError:
                pass
        return False

def ensure_database() -> tuple[bool, str]:
    """
    Ensure the database exists and is properly structured.
    Creates a new database if it doesn't exist.
    
    Returns:
        tuple[bool, str]: (success, message) where:
            - success: True if database is ready, False otherwise
            - message: Detailed status or error message
    """
    # Ensure data directory exists
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        error_msg = f"Failed to create database directory: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    
    # Check if database exists and is valid
    if os.path.exists(DB_PATH):
        is_valid, message = verify_database()
        if is_valid:
            return True, "Database is valid and ready"
        
        logger.warning(f"Database verification failed: {message}")
        # Try to repair the database
        try:
            backup_path = f"{DB_PATH}.bak"
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            logger.info(f"Created backup of existing database at {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup database before repair: {str(e)}")
    
    # Create new database if it doesn't exist or is invalid
    logger.info("Creating new database...")
    if create_database():
        return True, "Successfully created new database"
    return False, "Failed to create new database"

def require_database(func):
    """
    Decorator to ensure database is available before running a function.
    
    Args:
        func: The function to wrap
        
    Returns:
        The wrapped function that includes database verification
        
    Raises:
        RuntimeError: If database verification fails
    """
    def wrapper(*args, **kwargs):
        success, message = ensure_database()
        if not success:
            error_msg = f"Database verification failed: {message}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        return func(*args, **kwargs)
    
    # Preserve the original function's docstring and metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    
    return wrapper
