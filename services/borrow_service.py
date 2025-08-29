"""
Borrow Service
---------------
Handles book borrowing operations with proper validation and database interactions.
"""
import os
import traceback
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import logging
import sys
import sqlite3
from pathlib import Path

# Add project root to path to allow absolute imports
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import database utilities
from utils.database_utils import get_connection, ensure_database, require_database, DB_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('borrow_service.log')
    ]
)
logger = logging.getLogger(__name__)

class BorrowService:
    """
    Service for handling book borrowing operations.
    Uses the centralized database configuration.
    """
    
    # Define valid status values according to the database schema
    VALID_STATUSES = ['borrowed', 'returned', 'overdue', 'lost']
    DEFAULT_STATUS = 'borrowed'
    MAX_BOOKS_PER_USER = 5  # Maximum number of books a user can borrow at once
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the BorrowService with database verification.
        
        Args:
            db_path: Optional path to the database file. If not provided, uses the default.
            
        Raises:
            RuntimeError: If database verification fails
        """
        # Use the provided path or default to intelli_libraria.db in the project root
        self.db_path = str(db_path) if db_path else os.path.abspath('intelli_libraria.db')
        logger.info(f"Using database at: {self.db_path}")
        
        # Verify the database file exists
        if not os.path.exists(self.db_path):
            error_msg = f"Database file not found at: {self.db_path}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        # Test the database connection
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                logger.info(f"Connected to database. Found tables: {', '.join(tables)}")
        except sqlite3.Error as e:
            error_msg = f"Failed to connect to database at {self.db_path}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        logger.info("BorrowService initialized successfully with database connection")
    
    def _get_valid_status(self, status: Optional[str] = None) -> str:
        """
        Validate and return a status value that matches the database constraints.
        
        Args:
            status: Optional status to validate
            
        Returns:
            str: A valid status value
        """
        if status and status.lower() in self.VALID_STATUSES:
            return status.lower()
            
        logger.warning(f"Invalid status '{status}'. Using default: {self.DEFAULT_STATUS}")
        return self.DEFAULT_STATUS
    
    def log_database_error(self, context: str, error: Exception, cursor=None, **extra):
        """Helper to log detailed database errors"""
        error_info = {
            'context': context,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            **extra
        }
        
        if cursor and hasattr(cursor, '_last_executed'):
            error_info['last_sql'] = cursor._last_executed
        
        logger.error(f"Database Error: {error_info}", exc_info=True)
        return error_info

    @require_database
    def borrow_book(self, user_id: int, book_id: int) -> Tuple[bool, str]:
        """
        Borrow a book for a user with validation.
        
        Args:
            user_id: ID of the user borrowing the book
            book_id: ID of the book to be borrowed
            
        Returns:
            Tuple[bool, str]: (success, message) with detailed error message on failure
        """
        def log_error(context: str, error: Exception, details: dict = None):
            """Helper function to log errors with context and details"""
            error_details = {
                'context': context,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'user_id': user_id,
                'book_id': book_id,
                'timestamp': datetime.now().isoformat(),
                **(details or {})
            }
            logger.error(f"Error in borrow_book: {error_details}", exc_info=True)
            return error_details

        logger.info(f"Processing borrow request - User: {user_id}, Book: {book_id}")
        
        # Store the original error for detailed reporting
        original_error = None
        
        # Input validation
        try:
            logger.info(f"Starting borrow process - User: {user_id}, Book: {book_id}")
            user_id = int(user_id)
            book_id = int(book_id)
            if user_id <= 0 or book_id <= 0:
                error_msg = f"Invalid IDs - User: {user_id}, Book: {book_id}"
                logger.error(error_msg)
                return False, "Error: IDs must be positive numbers"
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid input - User ID: {user_id}, Book ID: {book_id}, Error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, f"Error: Invalid input - {str(e)}"
        
        conn = None
        try:
            conn = get_connection(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # 1. Verify user exists and is active
            try:
                logger.info(f"Checking user {user_id} status...")
                cursor.execute("SELECT id, status, full_name, username FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    error_msg = f"User {user_id} not found in database"
                    logger.warning(error_msg)
                    return False, f"Error: User ID {user_id} not found"
                    
                # Convert row to dictionary for easier access
                user_dict = {
                    'id': user[0],
                    'status': user[1],
                    'full_name': user[2],
                    'username': user[3]
                }
                logger.info(f"Found user: ID={user_dict['id']}, Name={user_dict.get('full_name', 'N/A')}, Username={user_dict.get('username', 'N/A')}, Status={user_dict['status']}")
                
                if user_dict['status'].lower() != 'active':
                    error_msg = f"User {user_id} is not active. Status: {user_dict['status']}"
                    logger.warning(error_msg)
                    return False, f"Error: Your account is {user_dict['status'].lower()}. Please contact the administrator."
                    
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                error_details = f"{error_type}: {error_msg}"
                if hasattr(e, 'sqlite_errorcode'):
                    error_details += f" (SQLite error {e.sqlite_errorcode}: {e.sqlite_errorname})"
                if hasattr(cursor, '_last_executed'):
                    error_details += f"\nSQL Query: {cursor._last_executed}"
                logger.error(f"Error in borrow_book: {error_details}", exc_info=True)
                return False, f"Error: {error_details}"
            
            # 2. Verify book exists and is available
            try:
                logger.info(f"Checking book {book_id} availability...")
                cursor.execute("""
                    SELECT id, title, stock 
                    FROM books 
                    WHERE id = ?
                """, (book_id,))
                book = cursor.fetchone()
                
                if not book:
                    error_msg = f"Book with ID {book_id} not found"
                    logger.warning(error_msg)
                    return False, error_msg
                    
                if book['stock'] <= 0:
                    error_msg = f"No available copies of book {book_id}"
                    logger.warning(error_msg)
                    return False, error_msg
                
            except sqlite3.Error as e:
                error_info = self.log_database_error(
                    "Database error in borrow_book",
                    e,
                    cursor if 'cursor' in locals() else None,
                    user_id=user_id,
                    book_id=book_id
                )
                return False, f"Database error: {str(e)}"
            
            # 3. Check if user has already borrowed this book
            try:
                logger.info("Checking for existing loans...")
                cursor.execute("""
                    SELECT t.id, b.title, t.issue_date, t.due_date
                    FROM transactions t
                    JOIN books b ON t.book_id = b.id
                    WHERE t.user_id = ? 
                    AND t.book_id = ? 
                    AND t.return_date IS NULL
                """, (user_id, book_id))
                
                existing_loan = cursor.fetchone()
                if existing_loan:
                    error_msg = f"User {user_id} has already borrowed book {book_id}"
                    logger.warning(error_msg)
                    try:
                        due_date = datetime.strptime(existing_loan['due_date'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y')
                    except (ValueError, TypeError):
                        due_date = str(existing_loan['due_date'])
                    return False, f"You have already borrowed '{existing_loan['title']}'. Due date: {due_date}"
                logger.info("No existing active loans found for this book and user")
                    
                # 4. Begin transaction
                logger.info("Starting database transaction...")
                issue_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Issue date: {issue_date}, Due date: {due_date}")
                
                # Create transaction record
                try:
                    logger.info("Creating transaction record...")
                    # Verify the user is still active (in case status changed)
                    cursor.execute("SELECT id, status FROM users WHERE id = ?", (user_id,))
                    user = cursor.fetchone()
                    if not user or user['status'].lower() != 'active':
                        error_msg = f"User {user_id} is no longer active or does not exist"
                        logger.error(error_msg)
                        return False, "Error: Your account is no longer active. Please contact the administrator."

                    # Verify the book is still available
                    cursor.execute("SELECT id, title, stock FROM books WHERE id = ?", (book_id,))
                    book = cursor.fetchone()
                    if not book:
                        error_msg = f"Book {book_id} no longer exists in the database"
                        logger.error(error_msg)
                        return False, "Error: The requested book is no longer available."
                        
                    if book['stock'] <= 0:
                        error_msg = f"Book '{book['title']}' (ID: {book_id}) is no longer available. Current stock: {book['stock']}"
                        logger.warning(error_msg)
                        return False, f"Error: '{book['title']}' is no longer available for borrowing."
                    
                    # Insert the transaction
                    try:
                        logger.info("Executing transaction insert...")
                        # First insert the transaction
                        cursor.execute("""
                            INSERT INTO transactions (
                                user_id, 
                                book_id, 
                                issue_date, 
                                due_date, 
                                return_date,
                                status,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?, NULL, 'Issued', datetime('now'), datetime('now'))
                        """, (user_id, book_id, issue_date, due_date))
                        
                        # Then update the book stock
                        cursor.execute("""
                            UPDATE books 
                            SET stock = stock - 1 
                            WHERE id = ? AND stock > 0
                        """, (book_id,))
                        if cursor.rowcount == 0:
                            error_msg = f"Failed to update available copies for book {book_id}"
                            logger.error(error_msg)
                            return False, "Error: Could not update book availability. Please try again."
                            
                        logger.info(f"Updated available copies for book {book_id}")
                        
                    except sqlite3.Error as e:
                        error_info = self.log_database_error(
                            "Failed to update book quantity",
                            e,
                            cursor,
                            book_id=book_id
                        )
                        return False, f"Database error: {str(e)}"
                        
                    # Commit the transaction
                    try:
                        conn.commit()
                        logger.info(f"Transaction committed successfully. Book {book_id} borrowed by user {user_id}")
                        
                        # Format the due date for display
                        try:
                            display_due_date = datetime.strptime(due_date, '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
                        except:
                            display_due_date = due_date
                            
                        return True, f"Book successfully borrowed. Due date: {display_due_date}"
                        
                    except sqlite3.Error as e:
                        error_info = self.log_database_error(
                            "Failed to commit transaction",
                            e,
                            cursor
                        )
                        return False, f"Error finalizing the transaction: {str(e)}"
                        
                except Exception as e:
                    error_info = {
                        'context': 'Unexpected error in borrow_book',
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'traceback': traceback.format_exc(),
                        'python_version': sys.version,
                        'timestamp': datetime.now().isoformat()
                    }
                    logger.error(f"Unexpected error: {error_info}", exc_info=True)
                    return False, f"An unexpected error occurred: {str(e)}"
                    
            except Exception as e:
                if conn:
                    try:
                        conn.rollback()
                        logger.info("Transaction rolled back due to error")
                    except Exception as rollback_error:
                        logger.error(f"Error during rollback: {str(rollback_error)}")
                error_msg = f"Unexpected error in transaction processing: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return False, f"An unexpected error occurred: {str(e)}"
                
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error in borrow_book: {e}", exc_info=True)
            return False, f"An unexpected error occurred: {str(e)}"
            
        finally:
            if conn:
                conn.close()

def test_database_connection():
    """Test database connection and table structure."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("\n=== Database Tables ===")
        for table in tables:
            print(f"Table: {table[0]}")
        
        # Check transactions table structure
        print("\n=== Transactions Table Structure ===")
        cursor.execute("PRAGMA table_info(transactions)")
        for column in cursor.fetchall():
            print(f"Column: {column[1]} ({column[2]}) {'NOT NULL' if not column[3] else ''}")
        
        # Check foreign key constraints
        print("\n=== Foreign Key Constraints ===")
        cursor.execute("PRAGMA foreign_key_list(transactions)")
        for fk in cursor.fetchall():
            print(f"FK: {fk[3]} references {fk[2]}({fk[4]})")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Database test failed: {str(e)}")
        return False

def main():
    """Example usage of the BorrowService."""
    try:
        # First test the database connection
        if not test_database_connection():
            print("\nDatabase test failed. Please check the database configuration.")
            return
        print("=== Library Book Borrowing System ===\n")
        
        # Get user input
        try:
            user_id = int(input("Enter User ID: ").strip())
            book_id = int(input("Enter Book ID: ").strip())
        except ValueError:
            print("\nError: User ID and Book ID must be numbers")
            return
            
        # Initialize service and attempt to borrow
        try:
            service = BorrowService()
            success, message = service.borrow_book(user_id, book_id)
            
            # Display result
            print("\n" + "=" * 50)
            print("Borrowing Status:")
            print("-" * 50)
            print(f"User ID:    {user_id}")
            print(f"Book ID:    {book_id}")
            print(f"Success:    {'✅ Yes' if success else '❌ No'}")
            print(f"Message:    {message}")
            print("=" * 50)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
