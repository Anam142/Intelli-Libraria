"""
Repository for transaction-related database operations.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import sqlite3
import calendar

from ..models import (
    Transaction, TransactionStatus, 
    PaginationParams, FilterParams, SearchResult
)
from ..errors import (
    NotFoundError, 
    BusinessRuleError,
    ValidationError
)
from ..validators import validate
from ..database import get_db
from .base_repository import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository for transaction-related database operations.
    """
    
    table_name = 'transactions'
    model_class = Transaction
    columns = [
        'book_id', 'user_id', 'issue_date', 'due_date',
        'return_date', 'status'
    ]
    
    # Default lending period in days
    DEFAULT_LENDING_DAYS = 14
    
    def __init__(self):
        super().__init__()
    
    def _calculate_due_date(self, issue_date: date = None) -> date:
        """
        Calculate the due date based on the issue date.
        
        Args:
            issue_date: The issue date (defaults to today)
            
        Returns:
            The calculated due date
        """
        if issue_date is None:
            issue_date = date.today()
            
        # Add the lending period to the issue date
        return issue_date + timedelta(days=self.DEFAULT_LENDING_DAYS)
    
    def issue_book(
        self, 
        book_id: int, 
        user_id: int,
        issue_date: date = None,
        due_date: date = None,
        commit: bool = True
    ) -> Transaction:
        """
        Issue a book to a user.
        
        Args:
            book_id: The ID of the book to issue
            user_id: The ID of the user borrowing the book
            issue_date: The issue date (defaults to today)
            due_date: The due date (defaults to issue_date + DEFAULT_LENDING_DAYS)
            commit: Whether to commit the transaction (set to False if called within another transaction)
            
        Returns:
            The created Transaction instance
            
        Raises:
            BusinessRuleError: If the book is not available or user has reached borrowing limit
            NotFoundError: If the book or user is not found
        """
        from .books_repo import BookRepository
        from .users_repo import UserRepository
        
        # Set default dates if not provided
        if issue_date is None:
            issue_date = date.today()
            
        if due_date is None:
            due_date = self._calculate_due_date(issue_date)
        
        # Validate dates
        if due_date <= issue_date:
            raise ValidationError(
                'due_date',
                "Due date must be after issue date"
            )
        
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                # Check if book exists and is available
                book_repo = BookRepository()
                book = book_repo.get_by_id(book_id)
                if not book:
                    raise NotFoundError('Book', id=book_id)
                    
                if book.quantity_available <= 0:
                    raise BusinessRuleError(
                        'book_unavailable',
                        f"Book {book_id} is not available for borrowing"
                    )
                
                # Check if user exists and can borrow
                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)
                if not user:
                    raise NotFoundError('User', id=user_id)
                    
                if user.status != 'Active':
                    raise BusinessRuleError(
                        'user_inactive',
                        f"User {user_id} is not active and cannot borrow books"
                    )
                
                # Check if user already has this book checked out
                existing_loan_query = """
                    SELECT id FROM transactions
                    WHERE book_id = ? AND user_id = ? AND status = 'Issued'
                """
                cursor.execute(existing_loan_query, (book_id, user_id))
                if cursor.fetchone():
                    raise BusinessRuleError(
                        'duplicate_loan',
                        f"User {user_id} already has this book checked out"
                    )
                
                # Create the transaction
                transaction = Transaction(
                    book_id=book_id,
                    user_id=user_id,
                    issue_date=issue_date,
                    due_date=due_date,
                    status=TransactionStatus.ISSUED
                )
                
                # Insert the transaction
                transaction_data = self._model_to_dict(transaction, exclude_none=True)
                columns = ', '.join(transaction_data.keys())
                placeholders = ', '.join(['?'] * len(transaction_data))
                
                query = f"""
                    INSERT INTO {self.table_name} ({columns})
                    VALUES ({placeholders})
                """
                
                cursor.execute(query, tuple(transaction_data.values()))
                transaction.id = cursor.lastrowid
                
                # Update book available quantity
                update_book_query = """
                    UPDATE books
                    SET quantity_available = quantity_available - 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                cursor.execute(update_book_query, (book_id,))
                
                if commit:
                    conn.commit()
                
                return transaction
                
            except Exception as e:
                if commit:
                    conn.rollback()
                raise
    
    def return_book(
        self, 
        transaction_id: int,
        return_date: date = None,
        commit: bool = True
    ) -> Transaction:
        """
        Return a borrowed book.
        
        Args:
            transaction_id: The ID of the transaction to update
            return_date: The return date (defaults to today)
            commit: Whether to commit the transaction (set to False if called within another transaction)
            
        Returns:
            The updated Transaction instance
            
        Raises:
            NotFoundError: If the transaction is not found
            BusinessRuleError: If the book is already returned
        """
        if return_date is None:
            return_date = date.today()
        
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                # Get the transaction
                transaction = self.get_by_id(transaction_id)
                if not transaction:
                    raise NotFoundError('Transaction', id=transaction_id)
                
                # Check if already returned
                if transaction.status == TransactionStatus.RETURNED:
                    raise BusinessRuleError(
                        'already_returned',
                        f"Book was already returned on {transaction.return_date}"
                    )
                
                # Update the transaction
                update_query = f"""
                    UPDATE {self.table_name}
                    SET return_date = ?,
                        status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                # Determine status (check if overdue)
                status = TransactionStatus.RETURNED
                if return_date > transaction.due_date:
                    status = TransactionStatus.OVERDUE
                
                cursor.execute(
                    update_query,
                    (return_date.isoformat(), status.value, transaction_id)
                )
                
                # Update book available quantity
                update_book_query = """
                    UPDATE books
                    SET quantity_available = quantity_available + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                cursor.execute(update_book_query, (transaction.book_id,))
                
                # Update the transaction object
                transaction.return_date = return_date
                transaction.status = status
                
                if commit:
                    conn.commit()
                
                return transaction
                
            except Exception as e:
                if commit:
                    conn.rollback()
                raise
    
    def get_overdue_transactions(
        self, 
        as_of_date: date = None
    ) -> List[Transaction]:
        """
        Get all overdue transactions as of the given date.
        
        Args:
            as_of_date: The date to check for overdue transactions (defaults to today)
            
        Returns:
            List of overdue transactions
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        query = f"""
            SELECT t.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.due_date < ? 
              AND t.status = 'Issued'
            ORDER BY t.due_date
        """
        
        rows = self._execute_query(query, (as_of_date.isoformat(),))
        return [self._row_to_model(row) for row in rows]
    
    def get_user_transactions(
        self, 
        user_id: int,
        status: TransactionStatus = None,
        include_past: bool = True
    ) -> List[Transaction]:
        """
        Get all transactions for a specific user.
        
        Args:
            user_id: The ID of the user
            status: Optional status to filter by
            include_past: Whether to include past (returned) transactions
            
        Returns:
            List of transactions for the user
        """
        query = f"""
            SELECT t.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.user_id = ?
        """
        
        params = [user_id]
        
        # Add status filter if provided
        if status is not None:
            query += " AND t.status = ?"
            params.append(status.value)
        
        # Filter out past transactions if needed
        if not include_past:
            query += " AND (t.return_date IS NULL OR t.return_date >= ?)"
            params.append(date.today().isoformat())
        
        query += " ORDER BY t.due_date"
        
        rows = self._execute_query(query, tuple(params))
        return [self._row_to_model(row) for row in rows]
    
    def get_book_transactions(
        self, 
        book_id: int,
        limit: int = 10
    ) -> List[Transaction]:
        """
        Get transaction history for a specific book.
        
        Args:
            book_id: The ID of the book
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions for the book
        """
        query = f"""
            SELECT t.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} t
            JOIN books b ON t.book_id = b.id
            JOIN users u ON t.user_id = u.id
            WHERE t.book_id = ?
            ORDER BY t.issue_date DESC
            LIMIT ?
        """
        
        rows = self._execute_query(query, (book_id, limit))
        return [self._row_to_model(row) for row in rows]
    
    def get_active_loans_count(self, user_id: int) -> int:
        """
        Get the number of active loans for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Number of active loans
        """
        query = f"""
            SELECT COUNT(*) as count
            FROM {self.table_name}
            WHERE user_id = ? AND status = 'Issued'
        """
        
        result = self._execute_query(query, (user_id,), fetch_one=True)
        return result['count'] if result else 0
    
    def get_borrowing_stats(
        self, 
        start_date: date = None, 
        end_date: date = None
    ) -> Dict[str, Any]:
        """
        Get borrowing statistics for the given date range.
        
        Args:
            start_date: Start date of the period (defaults to 30 days ago)
            end_date: End date of the period (defaults to today)
            
        Returns:
            Dictionary containing borrowing statistics
        """
        if end_date is None:
            end_date = date.today()
            
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        query = """
            SELECT 
                COUNT(*) as total_loans,
                SUM(CASE WHEN status = 'Returned' THEN 1 ELSE 0 END) as returned_loans,
                SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) as overdue_loans,
                SUM(CASE WHEN status = 'Issued' AND due_date < ? THEN 1 ELSE 0 END) as currently_overdue,
                AVG(julianday(return_date) - julianday(issue_date)) as avg_loan_days
            FROM transactions
            WHERE issue_date BETWEEN ? AND ?
        """
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                query, 
                (end_date.isoformat(), start_date.isoformat(), end_date.isoformat())
            )
            stats = dict(cursor.fetchone())
            
            # Calculate return rate (percentage of returned loans)
            if stats['total_loans'] > 0:
                stats['return_rate'] = (stats['returned_loans'] / stats['total_loans']) * 100
            else:
                stats['return_rate'] = 0
                
            # Convert average loan days to float (it comes as a string from SQLite)
            if stats['avg_loan_days'] is not None:
                stats['avg_loan_days'] = float(stats['avg_loan_days'])
            
            return stats
