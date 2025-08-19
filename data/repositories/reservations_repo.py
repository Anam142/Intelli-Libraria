"""
Repository for reservation-related database operations.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import sqlite3

from ..models import (
    Reservation, ReservationStatus, 
    PaginationParams, FilterParams, SearchResult
)
from ..errors import (
    NotFoundError, 
    BusinessRuleError,
    ValidationError,
    StateError
)
from ..validators import validate
from ..database import get_db
from .base_repository import BaseRepository

class ReservationRepository(BaseRepository[Reservation]):
    """
    Repository for reservation-related database operations.
    """
    
    table_name = 'reservations'
    model_class = Reservation
    columns = [
        'book_id', 'user_id', 'reserved_at', 'status'
    ]
    
    # Default reservation expiry period in days
    RESERVATION_EXPIRY_DAYS = 3
    
    def __init__(self):
        super().__init__()
    
    def create_reservation(
        self, 
        book_id: int, 
        user_id: int,
        reserved_at: datetime = None,
        commit: bool = True
    ) -> Reservation:
        """
        Create a new book reservation.
        
        Args:
            book_id: The ID of the book to reserve
            user_id: The ID of the user making the reservation
            reserved_at: When the reservation was made (defaults to now)
            commit: Whether to commit the transaction
            
        Returns:
            The created Reservation instance
            
        Raises:
            BusinessRuleError: If the book is available or user already has an active reservation
            NotFoundError: If the book or user is not found
        """
        from .books_repo import BookRepository
        from .users_repo import UserRepository
        from .transactions_repo import TransactionRepository
        
        # Set default timestamp if not provided
        if reserved_at is None:
            reserved_at = datetime.now()
        
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                # Check if book exists
                book_repo = BookRepository()
                book = book_repo.get_by_id(book_id)
                if not book:
                    raise NotFoundError('Book', id=book_id)
                
                # Check if user exists
                user_repo = UserRepository()
                user = user_repo.get_by_id(user_id)
                if not user:
                    raise NotFoundError('User', id=user_id)
                
                # Check if book is available
                if book.quantity_available > 0:
                    raise BusinessRuleError(
                        'book_available',
                        f"Book {book_id} is available for immediate borrowing"
                    )
                
                # Check if user already has an active reservation for this book
                existing_reservation = self.get_active_reservation(book_id, user_id)
                if existing_reservation:
                    raise BusinessRuleError(
                        'duplicate_reservation',
                        f"User {user_id} already has an active reservation for book {book_id}"
                    )
                
                # Check if user already has this book checked out
                transaction_repo = TransactionRepository()
                active_loans = transaction_repo.get_user_transactions(
                    user_id, 
                    status='Issued'
                )
                
                for loan in active_loans:
                    if loan.book_id == book_id:
                        raise BusinessRuleError(
                            'already_borrowed',
                            f"User {user_id} already has this book checked out"
                        )
                
                # Create the reservation
                reservation = Reservation(
                    book_id=book_id,
                    user_id=user_id,
                    reserved_at=reserved_at,
                    status=ReservationStatus.ACTIVE
                )
                
                # Insert the reservation
                reservation_data = self._model_to_dict(reservation, exclude_none=True)
                columns = ', '.join(reservation_data.keys())
                placeholders = ', '.join(['?'] * len(reservation_data))
                
                query = f"""
                    INSERT INTO {self.table_name} ({columns})
                    VALUES ({placeholders})
                """
                
                cursor.execute(query, tuple(reservation_data.values()))
                reservation.id = cursor.lastrowid
                
                if commit:
                    conn.commit()
                
                return reservation
                
            except Exception as e:
                if commit:
                    conn.rollback()
                raise
    
    def get_active_reservation(
        self, 
        book_id: int, 
        user_id: int
    ) -> Optional[Reservation]:
        """
        Get an active reservation for a book and user.
        
        Args:
            book_id: The ID of the book
            user_id: The ID of the user
            
        Returns:
            The active Reservation if found, None otherwise
        """
        query = f"""
            SELECT r.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} r
            JOIN books b ON r.book_id = b.id
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = ? 
              AND r.user_id = ?
              AND r.status = 'Active'
        """
        
        row = self._execute_query(query, (book_id, user_id), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_active_reservations_for_book(
        self, 
        book_id: int,
        limit: int = 10
    ) -> List[Reservation]:
        """
        Get all active reservations for a book, ordered by reservation date.
        
        Args:
            book_id: The ID of the book
            limit: Maximum number of reservations to return
            
        Returns:
            List of active reservations for the book
        """
        query = f"""
            SELECT r.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} r
            JOIN books b ON r.book_id = b.id
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = ? 
              AND r.status = 'Active'
            ORDER BY r.reserved_at
            LIMIT ?
        """
        
        rows = self._execute_query(query, (book_id, limit))
        return [self._row_to_model(row) for row in rows]
    
    def get_user_reservations(
        self, 
        user_id: int,
        status: ReservationStatus = None,
        include_expired: bool = False
    ) -> List[Reservation]:
        """
        Get all reservations for a user.
        
        Args:
            user_id: The ID of the user
            status: Optional status to filter by
            include_expired: Whether to include expired reservations
            
        Returns:
            List of reservations for the user
        """
        query = f"""
            SELECT r.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} r
            JOIN books b ON r.book_id = b.id
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = ?
        """
        
        params = [user_id]
        
        # Add status filter if provided
        if status is not None:
            query += " AND r.status = ?"
            params.append(status.value)
        
        # Filter out expired reservations if needed
        if not include_expired:
            expiry_date = (datetime.now() - timedelta(days=self.RESERVATION_EXPIRY_DAYS)).isoformat()
            query += " AND (r.status != 'Active' OR r.reserved_at > ?)"
            params.append(expiry_date)
        
        query += " ORDER BY r.reserved_at DESC"
        
        rows = self._execute_query(query, tuple(params))
        return [self._row_to_model(row) for row in rows]
    
    def fulfill_reservation(
        self, 
        reservation_id: int,
        commit: bool = True
    ) -> Reservation:
        """
        Mark a reservation as fulfilled.
        
        Args:
            reservation_id: The ID of the reservation to fulfill
            commit: Whether to commit the transaction
            
        Returns:
            The updated Reservation instance
            
        Raises:
            NotFoundError: If the reservation is not found
            StateError: If the reservation is not active
        """
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                # Get the current reservation
                reservation = self.get_by_id(reservation_id)
                if not reservation:
                    raise NotFoundError('Reservation', id=reservation_id)
                
                # Check if reservation is active
                if reservation.status != ReservationStatus.ACTIVE:
                    raise StateError(
                        f"Cannot fulfill a {reservation.status.lower()} reservation"
                    )
                
                # Update the reservation status
                update_query = f"""
                    UPDATE {self.table_name}
                    SET status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                cursor.execute(
                    update_query,
                    (ReservationStatus.FULFILLED.value, reservation_id)
                )
                
                # Update the reservation object
                reservation.status = ReservationStatus.FULFILLED
                
                if commit:
                    conn.commit()
                
                return reservation
                
            except Exception as e:
                if commit:
                    conn.rollback()
                raise
    
    def cancel_reservation(
        self, 
        reservation_id: int,
        commit: bool = True
    ) -> bool:
        """
        Cancel a reservation.
        
        Args:
            reservation_id: The ID of the reservation to cancel
            commit: Whether to commit the transaction
            
        Returns:
            True if the reservation was cancelled, False if not found
            
        Raises:
            StateError: If the reservation is already fulfilled or cancelled
        """
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                # Get the current reservation
                reservation = self.get_by_id(reservation_id)
                if not reservation:
                    return False
                
                # Check if reservation can be cancelled
                if reservation.status != ReservationStatus.ACTIVE:
                    raise StateError(
                        f"Cannot cancel a {reservation.status.lower()} reservation"
                    )
                
                # Update the reservation status
                update_query = f"""
                    UPDATE {self.table_name}
                    SET status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                cursor.execute(
                    update_query,
                    (ReservationStatus.CANCELLED.value, reservation_id)
                )
                
                if commit:
                    conn.commit()
                
                return cursor.rowcount > 0
                
            except Exception as e:
                if commit:
                    conn.rollback()
                raise
    
    def get_expired_reservations(
        self,
        expiry_days: int = None
    ) -> List[Reservation]:
        """
        Get all active reservations that have expired.
        
        Args:
            expiry_days: Number of days after which a reservation expires
                         (defaults to RESERVATION_EXPIRY_DAYS)
            
        Returns:
            List of expired reservations
        """
        if expiry_days is None:
            expiry_days = self.RESERVATION_EXPIRY_DAYS
            
        expiry_date = (datetime.now() - timedelta(days=expiry_days)).isoformat()
        
        query = f"""
            SELECT r.*, 
                   b.title as book_title,
                   u.full_name as user_name
            FROM {self.table_name} r
            JOIN books b ON r.book_id = b.id
            JOIN users u ON r.user_id = u.id
            WHERE r.status = 'Active'
              AND r.reserved_at <= ?
            ORDER BY r.reserved_at
        """
        
        rows = self._execute_query(query, (expiry_date,))
        return [self._row_to_model(row) for row in rows]
    
    def process_expired_reservations(self) -> int:
        """
        Automatically cancel all expired reservations.
        
        Returns:
            Number of reservations cancelled
        """
        expired_reservations = self.get_expired_reservations()
        cancelled_count = 0
        
        with get_db() as conn:
            try:
                cursor = conn.cursor()
                
                for reservation in expired_reservations:
                    update_query = f"""
                        UPDATE {self.table_name}
                        SET status = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """
                    
                    cursor.execute(
                        update_query,
                        (ReservationStatus.CANCELLED.value, reservation.id)
                    )
                    cancelled_count += 1
                
                conn.commit()
                return cancelled_count
                
            except Exception as e:
                conn.rollback()
                raise
