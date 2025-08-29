"""
Borrow Service
---------------
Handles book borrowing operations with proper validation and database interactions.
"""
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
        self.db_path = str(db_path) if db_path else str(DB_PATH)
        success, message = ensure_database()
        if not success:
            error_msg = f"Database initialization failed: {message}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        logger.info("BorrowService initialized successfully")
    
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
    
    @require_database
    def borrow_book(self, user_id: int, book_id: int) -> Tuple[bool, str]:
        """
        Borrow a book for a user with validation.
        
        Args:
            user_id: ID of the user borrowing the book
            book_id: ID of the book to be borrowed
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        logger.info(f"Processing borrow request - User: {user_id}, Book: {book_id}")
        
        # Input validation
        try:
            user_id = int(user_id)
            book_id = int(book_id)
            if user_id <= 0 or book_id <= 0:
                raise ValueError("IDs must be positive")
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid input: {e}")
            return False, "Invalid user ID or book ID"
        
        conn = None
        try:
            conn = get_connection(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # 1. Verify user exists and is active
            cursor.execute("""
                SELECT id, status FROM users 
                WHERE id = ? AND status = 'Active' AND deleted_at IS NULL
            """, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"User {user_id} not found or inactive")
                return False, "User not found or account is inactive"
            
            # 2. Verify book exists and is available
            cursor.execute("""
                SELECT id, title, available_copies 
                FROM books 
                WHERE id = ? AND deleted_at IS NULL
            """, (book_id,))
            book = cursor.fetchone()
            
            if not book:
                logger.warning(f"Book {book_id} not found")
                return False, "Book not found"
                
            if book['available_copies'] <= 0:
                logger.info(f"No available copies of book {book_id}")
                return False, "No available copies of this book"
            
            # 3. Check if user has already borrowed this book
            cursor.execute("""
                SELECT id FROM transactions 
                WHERE user_id = ? AND book_id = ? 
                AND status = 'borrowed' AND return_date IS NULL
            """, (user_id, book_id))
            
            if cursor.fetchone():
                logger.info(f"User {user_id} already borrowed book {book_id}")
                return False, "You have already borrowed this book"
            
            # 4. Begin transaction
            borrow_date = datetime.now().strftime('%Y-%m-%d')
            due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            
            try:
                # Create transaction record
                cursor.execute("""
                    INSERT INTO transactions (
                        user_id, book_id, borrow_date, due_date, status
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    user_id, 
                    book_id, 
                    borrow_date,
                    due_date,
                    'borrowed'
                ))
                
                # Update book available copies
                cursor.execute("""
                    UPDATE books 
                    SET available_copies = available_copies - 1,
                        updated_at = datetime('now')
                    WHERE id = ? AND available_copies > 0
                """, (book_id,))
                
                if cursor.rowcount == 0:
                    raise sqlite3.IntegrityError("Failed to update book availability")
                
                conn.commit()
                logger.info(f"Successfully borrowed book {book_id} for user {user_id}")
                return True, f"Successfully borrowed '{book['title']}'. Due date: {due_date}"
                
            except sqlite3.IntegrityError as e:
                conn.rollback()
                logger.error(f"Integrity error during borrow: {e}")
                return False, "Could not complete the borrowing process. Please try again."
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error during borrow: {e}")
            return False, "A database error occurred. Please try again later."
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error in borrow_book: {e}", exc_info=True)
            return False, "An unexpected error occurred. Please try again."
            
        finally:
            if conn:
                conn.close()

def main():
    """Example usage of the BorrowService."""
    try:
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
