"""
Database Handler Module for Intelli Libraria
Handles all database operations with error handling and automatic schema management.
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Tuple

# Configure logging
LOG_FILE = 'library_management.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class DatabaseHandler:
    """
    A robust database handler that provides safe database operations
    with automatic error handling and schema management.
    """
    
    def __init__(self, db_path: str = 'intelli_libraria.db'):
        """Initialize the database handler with the given database path."""
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Create and return a new database connection with error handling."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('PRAGMA foreign_keys = ON')
            conn.row_factory = sqlite3.Row  # Enable dictionary-like access
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError("Unable to connect to the database.")
    
    def _init_database(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Enable foreign keys
                cursor.execute('PRAGMA foreign_keys = ON')
                
                # Create tables if they don't exist
                self._create_tables(cursor)
                
                # Apply any pending migrations
                self._apply_migrations(cursor)
                
                conn.commit()
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError("Failed to initialize database.")
    
    def _create_tables(self, cursor: sqlite3.Cursor) -> None:
        """Create database tables if they don't exist."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'librarian', 'member')),
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended')),
                contact TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publisher TEXT,
                publication_year INTEGER,
                category TEXT,
                description TEXT,
                stock INTEGER NOT NULL DEFAULT 1,
                available INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                reservation_date DATE NOT NULL,
                expiry_date DATE,
                status TEXT NOT NULL DEFAULT 'pending' 
                    CHECK(status IN ('pending', 'approved', 'rejected', 'fulfilled', 'cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status TEXT NOT NULL DEFAULT 'borrowed' 
                    CHECK(status IN ('borrowed', 'returned', 'overdue', 'lost')),
                fine_amount REAL DEFAULT 0.0,
                fine_paid BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS fines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'unpaid' 
                    CHECK(status IN ('unpaid', 'paid', 'waived')),
                due_date DATE NOT NULL,
                paid_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        try:
            for table_sql in tables:
                cursor.execute(table_sql)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_reservations_user_id 
                ON reservations(user_id, status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
                ON transactions(user_id, status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fines_user_id 
                ON fines(user_id, status)
            """)
            
            # Insert default admin user if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO users 
                (username, password, full_name, email, role, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', 'admin123', 'Administrator', 'admin@library.com', 'admin', 'active'))
            
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise DatabaseError("Failed to initialize database tables.")
    
    def _apply_migrations(self, cursor: sqlite3.Cursor) -> None:
        """Apply any pending database migrations."""
        try:
            # Check if migrations table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='migrations'
            """)
            if not cursor.fetchone():
                return
                
            # Get applied migrations
            cursor.execute("SELECT migration_name FROM migrations")
            applied_migrations = {row[0] for row in cursor.fetchall()}
            
            # Example migration (add more as needed)
            if 'add_phone_to_users' not in applied_migrations:
                try:
                    cursor.execute("""
                        ALTER TABLE users ADD COLUMN phone TEXT
                    """)
                    cursor.execute("""
                        INSERT INTO migrations (migration_name) 
                        VALUES ('add_phone_to_users')
                    """)
                except sqlite3.OperationalError:
                    # Column might already exist
                    pass
            
        except sqlite3.Error as e:
            logger.error(f"Error applying migrations: {e}")
            raise DatabaseError("Failed to apply database migrations.")
    
    def execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        fetch: bool = False,
        many: bool = False,
        commit: bool = True
    ) -> Union[None, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Execute a database query safely.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            many: Whether to fetch multiple rows
            commit: Whether to commit the transaction
            
        Returns:
            - None for non-fetch queries
            - Single row as dict if fetch=True and many=False
            - List of rows if fetch=True and many=True
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Execute the query
            cursor.execute(query, params)
            
            # Handle fetch if needed
            if fetch:
                if many:
                    result = [dict(row) for row in cursor.fetchall()]
                else:
                    row = cursor.fetchone()
                    result = dict(row) if row else None
            else:
                result = None
            
            # Commit if needed
            if commit:
                conn.commit()
                
            return result
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Query failed: {query}\nParams: {params}\nError: {e}")
            if fetch:
                return [] if many else None
            return None
            
        finally:
            if conn:
                conn.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """Execute a query multiple times with different parameter sets."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Batch query failed: {query}\nError: {e}")
            return False
            
        finally:
            if conn:
                conn.close()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
                fetch=True
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if table exists: {e}")
            return False
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table."""
        try:
            result = self.execute_query(
                f"PRAGMA table_info({table_name})",
                fetch=True,
                many=True
            )
            if not result:
                return False
            return any(col['name'] == column_name for col in result)
        except Exception as e:
            logger.error(f"Error checking if column exists: {e}")
            return False
    
    def get_last_insert_id(self) -> Optional[int]:
        """Get the ID of the last inserted row."""
        try:
            result = self.execute_query(
                "SELECT last_insert_rowid() as id",
                fetch=True
            )
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error getting last insert ID: {e}")
            return None

# Singleton instance
db = DatabaseHandler()
