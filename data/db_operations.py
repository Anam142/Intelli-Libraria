"""
Database Operations Module
Provides high-level database operations using the DatabaseHandler.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from db_handler import db
import logging

logger = logging.getLogger(__name__)

class DBOperations:
    """High-level database operations for the library management system."""
    
    # User Operations
    @staticmethod
    def get_user(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID with error handling."""
        try:
            return db.execute_query(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
                fetch=True
            )
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password."""
        try:
            user = db.execute_query(
                "SELECT * FROM users WHERE username = ? AND status = 'active'",
                (username,),
                fetch=True
            )
            if user and user['password'] == password:  # In production, use proper password hashing
                return user
            return None
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            return None
    
    # Book Operations
    @staticmethod
    def get_book(book_id: int) -> Optional[Dict[str, Any]]:
        """Get book by ID with error handling."""
        try:
            return db.execute_query(
                "SELECT * FROM books WHERE id = ?",
                (book_id,),
                fetch=True
            )
        except Exception as e:
            logger.error(f"Error getting book {book_id}: {e}")
            return None
    
    @staticmethod
    def search_books(
        query: str = "", 
        available_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for books with optional filters."""
        try:
            sql = """
                SELECT * FROM books 
                WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            
            if available_only:
                sql += " AND available > 0"
                
            sql += " ORDER BY title LIMIT ?"
            params.append(limit)
            
            return db.execute_query(
                sql,
                tuple(params),
                fetch=True,
                many=True
            ) or []
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return []
    
    # Reservation Operations
    @staticmethod
    def create_reservation(
        user_id: int, 
        book_id: int,
        days_valid: int = 7
    ) -> Dict[str, Any]:
        """Create a new reservation with validation."""
        try:
            # Check if book is available
            book = DBOperations.get_book(book_id)
            if not book or book.get('available', 0) < 1:
                return {
                    'success': False,
                    'message': 'Book is not available for reservation.'
                }
            
            # Check if user has reached reservation limit
            user_reservations = db.execute_query(
                """
                SELECT COUNT(*) as count FROM reservations 
                WHERE user_id = ? AND status IN ('pending', 'approved')
                """,
                (user_id,),
                fetch=True
            )
            
            if user_reservations and user_reservations.get('count', 0) >= 5:  # Max 5 active reservations
                return {
                    'success': False,
                    'message': 'You have reached the maximum number of active reservations.'
                }
            
            # Create reservation
            reservation_date = datetime.now().strftime('%Y-%m-%d')
            expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d')
            
            db.execute_query(
                """
                INSERT INTO reservations 
                (user_id, book_id, reservation_date, expiry_date, status)
                VALUES (?, ?, ?, ?, 'pending')
                """,
                (user_id, book_id, reservation_date, expiry_date),
                commit=True
            )
            
            # Update book availability
            db.execute_query(
                "UPDATE books SET available = available - 1 WHERE id = ?",
                (book_id,),
                commit=True
            )
            
            return {
                'success': True,
                'message': 'Reservation created successfully.',
                'reservation_id': db.get_last_insert_id()
            }
            
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            return {
                'success': False,
                'message': 'Failed to create reservation. Please try again.'
            }
    
    @staticmethod
    def get_user_reservations(user_id: int) -> List[Dict[str, Any]]:
        """Get all reservations for a user with book details."""
        try:
            return db.execute_query(
                """
                SELECT r.*, b.title, b.author, b.isbn
                FROM reservations r
                JOIN books b ON r.book_id = b.id
                WHERE r.user_id = ?
                ORDER BY r.created_at DESC
                """,
                (user_id,),
                fetch=True,
                many=True
            ) or []
        except Exception as e:
            logger.error(f"Error getting reservations for user {user_id}: {e}")
            return []
    
    # Transaction Operations
    @staticmethod
    def create_transaction(
        user_id: int,
        book_id: int,
        borrow_days: int = 14
    ) -> Dict[str, Any]:
        """Create a new borrow transaction."""
        try:
            issue_date = datetime.now().strftime('%Y-%m-%d')
            due_date = (datetime.now() + timedelta(days=borrow_days)).strftime('%Y-%m-%d')
            
            # Start transaction
            db.execute_query("BEGIN TRANSACTION")
            
            # Create transaction
            db.execute_query(
                """
                INSERT INTO transactions 
                (user_id, book_id, issue_date, due_date, status)
                VALUES (?, ?, ?, ?, 'borrowed')
                """,
                (user_id, book_id, issue_date, due_date),
                commit=False
            )
            
            # Update book availability
            db.execute_query(
                "UPDATE books SET available = available - 1 WHERE id = ?",
                (book_id,),
                commit=False
            )
            
            # Complete transaction
            db.execute_query("COMMIT")
            
            return {
                'success': True,
                'message': 'Book borrowed successfully.',
                'transaction_id': db.get_last_insert_id()
            }
            
        except Exception as e:
            db.execute_query("ROLLBACK")
            logger.error(f"Error creating transaction: {e}")
            return {
                'success': False,
                'message': 'Failed to process borrowing. Please try again.'
            }
    
    # Fine Operations
    @staticmethod
    def calculate_fine(transaction_id: int) -> float:
        """Calculate fine for an overdue transaction."""
        try:
            transaction = db.execute_query(
                """
                SELECT t.*, b.title 
                FROM transactions t
                JOIN books b ON t.book_id = b.id
                WHERE t.id = ?
                """,
                (transaction_id,),
                fetch=True
            )
            
            if not transaction:
                return 0.0
                
            if transaction['status'] != 'overdue':
                return 0.0
                
            due_date = datetime.strptime(transaction['due_date'], '%Y-%m-%d').date()
            days_overdue = (datetime.now().date() - due_date).days
            
            if days_overdue <= 0:
                return 0.0
                
            # Calculate fine (example: $0.50 per day, max $10.00)
            fine_per_day = 0.50
            max_fine = 10.00
            fine = min(days_overdue * fine_per_day, max_fine)
            
            return round(fine, 2)
            
        except Exception as e:
            logger.error(f"Error calculating fine: {e}")
            return 0.0
    
    # Report Generation
    @staticmethod
    def generate_report(
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate various reports."""
        try:
            if report_type == 'overdue_books':
                return db.execute_query(
                    """
                    SELECT t.*, u.full_name, b.title, b.author
                    FROM transactions t
                    JOIN users u ON t.user_id = u.id
                    JOIN books b ON t.book_id = b.id
                    WHERE t.status = 'overdue'
                    ORDER BY t.due_date
                    """,
                    fetch=True,
                    many=True
                ) or []
                
            elif report_type == 'popular_books':
                return db.execute_query(
                    """
                    SELECT b.*, COUNT(t.id) as borrow_count
                    FROM books b
                    LEFT JOIN transactions t ON b.id = t.book_id
                    GROUP BY b.id
                    ORDER BY borrow_count DESC
                    LIMIT 10
                    """,
                    fetch=True,
                    many=True
                ) or []
                
            elif report_type == 'user_activity':
                date_filter = ""
                params = []
                
                if start_date and end_date:
                    date_filter = "AND t.issue_date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                
                return db.execute_query(
                    f"""
                    SELECT u.id, u.full_name, u.email,
                           COUNT(t.id) as transactions_count,
                           SUM(CASE WHEN t.status = 'overdue' THEN 1 ELSE 0 END) as overdue_count,
                           COALESCE(SUM(f.amount), 0) as total_fines
                    FROM users u
                    LEFT JOIN transactions t ON u.id = t.user_id
                    LEFT JOIN fines f ON u.id = f.user_id
                    WHERE u.role = 'member' {date_filter}
                    GROUP BY u.id
                    ORDER BY transactions_count DESC
                    """,
                    tuple(params),
                    fetch=True,
                    many=True
                ) or []
                
            return []
            
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {e}")
            return []

# Singleton instance
db_ops = DBOperations()
