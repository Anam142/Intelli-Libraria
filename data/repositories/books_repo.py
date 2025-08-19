"""
Repository for book-related database operations.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
import sqlite3

from ..models import Book, PaginationParams, FilterParams, SearchResult
from ..errors import NotFoundError, BusinessRuleError
from ..validators import validate
from ..database import get_db
from .base_repository import BaseRepository

class BookRepository(BaseRepository[Book]):
    """
    Repository for book-related database operations.
    """
    
    table_name = 'books'
    model_class = Book
    columns = [
        'book_code', 'title', 'authors', 'isbn', 
        'quantity_total', 'quantity_available', 'branch'
    ]
    
    def __init__(self):
        super().__init__()
    
    def search(
        self, 
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationParams] = None
    ) -> SearchResult:
        """
        Search for books with the given query and filters.
        
        Args:
            query: Search query string
            filters: Additional filters to apply
            pagination: Pagination parameters
            
        Returns:
            SearchResult containing the matching books and total count
        """
        # Start building the query
        count_query = """
            SELECT COUNT(*) as count
            FROM books
            WHERE (title LIKE ? OR authors LIKE ? OR isbn = ?)
        """
        
        select_query = """
            SELECT *
            FROM books
            WHERE (title LIKE ? OR authors LIKE ? OR isbn = ?)
        """
        
        # Add filters if provided
        filter_conditions = []
        params = [f"%{query}%", f"%{query}%", query]
        
        if filters:
            for field, value in filters.items():
                if value is not None:
                    if field == 'available_only' and value:
                        filter_conditions.append("quantity_available > 0")
                    else:
                        filter_conditions.append(f"{field} = ?")
                        params.append(value)
        
        if filter_conditions:
            where_clause = " AND ".join(filter_conditions)
            count_query += f" AND {where_clause}"
            select_query += f" AND {where_clause}"
        
        # Add ordering
        select_query += " ORDER BY title ASC"
        
        # Add pagination if provided
        if pagination:
            select_query += " LIMIT ? OFFSET ?"
            params.extend([pagination.per_page, (pagination.page - 1) * pagination.per_page])
        
        # Execute the count query
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(count_query, tuple(params[:len(params) - (2 if pagination else 0)]))
            total = cursor.fetchone()['count']
            
            # Execute the select query
            cursor.execute(select_query, tuple(params))
            rows = [dict(row) for row in cursor.fetchall()]
        
        # Convert rows to models
        books = [self._row_to_model(row) for row in rows]
        
        return {
            'items': books,
            'total': total,
            'page': pagination.page if pagination else 1,
            'per_page': pagination.per_page if pagination else total,
            'total_pages': (total + pagination.per_page - 1) // pagination.per_page if pagination and pagination.per_page > 0 else 1
        }
    
    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Get a book by ISBN.
        
        Args:
            isbn: The ISBN to search for
            
        Returns:
            The Book instance if found, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE isbn = ?
        """
        
        row = self._execute_query(query, (isbn,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_by_code(self, book_code: str) -> Optional[Book]:
        """
        Get a book by book code.
        
        Args:
            book_code: The book code to search for
            
        Returns:
            The Book instance if found, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE book_code = ?
        """
        
        row = self._execute_query(query, (book_code,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_available_books(self) -> List[Book]:
        """
        Get all available books (quantity_available > 0).
        
        Returns:
            List of available books
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE quantity_available > 0
            ORDER BY title
        """
        
        rows = self._execute_query(query)
        return [self._row_to_model(row) for row in rows]
    
    def update_quantity(
        self, 
        book_id: int, 
        quantity_change: int,
        commit: bool = True
    ) -> bool:
        """
        Update the available quantity of a book.
        
        Args:
            book_id: The ID of the book to update
            quantity_change: The change in quantity (positive or negative)
            commit: Whether to commit the transaction (set to False if called within another transaction)
            
        Returns:
            True if the update was successful, False otherwise
            
        Raises:
            BusinessRuleError: If the update would result in negative available quantity
        """
        # First, get the current quantity
        book = self.get_by_id(book_id)
        if not book:
            return False
        
        new_quantity = book.quantity_available + quantity_change
        
        # Check for negative quantity
        if new_quantity < 0:
            raise BusinessRuleError(
                'insufficient_quantity',
                f"Cannot update quantity. Would result in negative available quantity (current: {book.quantity_available}, change: {quantity_change})"
            )
        
        # Check if we're exceeding total quantity
        if new_quantity > book.quantity_total:
            raise BusinessRuleError(
                'exceeds_total_quantity',
                f"Available quantity ({new_quantity}) cannot exceed total quantity ({book.quantity_total})"
            )
        
        # Update the quantity
        query = f"""
            UPDATE {self.table_name}
            SET quantity_available = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (new_quantity, book_id))
                
                if commit:
                    conn.commit()
                    
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            if commit:
                conn.rollback()
            raise
    
    def get_books_by_author(self, author: str) -> List[Book]:
        """
        Get all books by a specific author.
        
        Args:
            author: The author's name to search for
            
        Returns:
            List of books by the author
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE LOWER(authors) LIKE LOWER(?)
            ORDER BY title
        """
        
        rows = self._execute_query(query, (f"%{author}%",))
        return [self._row_to_model(row) for row in rows]
    
    def get_books_by_branch(self, branch: str) -> List[Book]:
        """
        Get all books in a specific branch.
        
        Args:
            branch: The branch name to filter by
            
        Returns:
            List of books in the branch
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE LOWER(branch) = LOWER(?)
            ORDER BY title
        """
        
        rows = self._execute_query(query, (branch,))
        return [self._row_to_model(row) for row in rows]
    
    def get_book_stats(self) -> Dict[str, Any]:
        """
        Get statistics about books in the library.
        
        Returns:
            Dictionary containing various book statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_books,
                SUM(quantity_total) as total_copies,
                SUM(quantity_available) as available_copies,
                COUNT(DISTINCT authors) as unique_authors,
                COUNT(DISTINCT branch) as branches_with_books
            FROM books
        """
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            stats = dict(cursor.fetchone())
            
            # Add some calculated fields
            stats['checked_out_copies'] = stats['total_copies'] - stats['available_copies']
            stats['utilization_rate'] = (
                (stats['checked_out_copies'] / stats['total_copies']) * 100 
                if stats['total_copies'] > 0 else 0
            )
            
            return stats
