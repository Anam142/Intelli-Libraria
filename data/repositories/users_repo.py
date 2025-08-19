"""
Repository for user-related database operations.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
import sqlite3
import random
import string

from ..models import User, PaginationParams, FilterParams, SearchResult, UserRole, UserStatus
from ..errors import (
    NotFoundError, 
    UniquenessError, 
    BusinessRuleError,
    ValidationError
)
from ..validators import validate
from ..database import get_db
from .base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    Repository for user-related database operations.
    """
    
    table_name = 'users'
    model_class = User
    columns = [
        'user_code', 'full_name', 'email', 'phone',
        'role', 'status'
    ]
    
    def __init__(self):
        super().__init__()
    
    def search(
        self, 
        query: str = None,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationParams] = None
    ) -> SearchResult:
        """
        Search for users with the given query and filters.
        
        Args:
            query: Search query string (searches user_code, full_name, email, phone)
            filters: Additional filters to apply
            pagination: Pagination parameters
            
        Returns:
            SearchResult containing the matching users and total count
        """
        # Start building the query
        count_query = """
            SELECT COUNT(*) as count
            FROM users
            WHERE 1=1
        """
        
        select_query = """
            SELECT *
            FROM users
            WHERE 1=1
        """
        
        # Add search conditions if query is provided
        params = []
        if query:
            search_condition = """
                AND (user_code LIKE ? 
                     OR full_name LIKE ? 
                     OR email LIKE ? 
                     OR phone LIKE ?)
            """
            search_param = f"%{query}%"
            params.extend([search_param] * 4)
            
            count_query += search_condition
            select_query += search_condition
        
        # Add filters if provided
        if filters:
            filter_conditions = []
            for field, value in filters.items():
                if value is not None:
                    if field == 'status' and isinstance(value, list):
                        placeholders = ','.join(['?'] * len(value))
                        filter_conditions.append(f"{field} IN ({placeholders})")
                        params.extend(value)
                    else:
                        filter_conditions.append(f"{field} = ?")
                        params.append(value)
            
            if filter_conditions:
                where_clause = " AND ".join(filter_conditions)
                count_query += f" AND {where_clause}"
                select_query += f" AND {where_clause}"
        
        # Add ordering
        select_query += " ORDER BY full_name"
        
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
        users = [self._row_to_model(row) for row in rows]
        
        return {
            'items': users,
            'total': total,
            'page': pagination.page if pagination else 1,
            'per_page': pagination.per_page if pagination else total,
            'total_pages': (total + pagination.per_page - 1) // pagination.per_page if pagination and pagination.per_page > 0 else 1
        }
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: The email address to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE LOWER(email) = LOWER(?)
        """
        
        row = self._execute_query(query, (email,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """
        Get a user by phone number.
        
        Args:
            phone: The phone number to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        # Normalize phone number by removing non-digit characters
        normalized_phone = ''.join(c for c in phone if c.isdigit())
        
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '+', '') = ?
        """
        
        row = self._execute_query(query, (normalized_phone,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_by_code(self, user_code: str) -> Optional[User]:
        """
        Get a user by user code.
        
        Args:
            user_code: The user code to search for
            
        Returns:
            The User instance if found, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE user_code = ?
        """
        
        row = self._execute_query(query, (user_code,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def generate_user_code(self, full_name: str, max_attempts: int = 10) -> str:
        """
        Generate a unique user code based on the user's name.
        
        Format: First letter of first name + up to 3 letters of last name + random 4 digits
        Example: John Smith -> JSMI1234
        
        Args:
            full_name: The user's full name
            max_attempts: Maximum number of attempts to generate a unique code
            
        Returns:
            A unique user code
            
        Raises:
            BusinessRuleError: If unable to generate a unique code after max_attempts
        """
        # Split name into parts
        name_parts = full_name.strip().split()
        
        if not name_parts:
            raise ValidationError('full_name', 'Full name is required')
        
        # Get first letter of first name
        first_initial = name_parts[0][0].upper() if name_parts[0] else 'U'
        
        # Get up to 3 letters of last name (or first name if no last name)
        last_name = name_parts[-1] if len(name_parts) > 1 else name_parts[0]
        last_part = last_name[:3].upper() if last_name else 'USR'
        
        base_code = f"{first_initial}{last_part}"
        
        # Try to generate a unique code
        for _ in range(max_attempts):
            # Generate random 4-digit number
            random_digits = ''.join(random.choices(string.digits, k=4))
            user_code = f"{base_code}{random_digits}"
            
            # Check if code already exists
            if not self.get_by_code(user_code):
                return user_code
        
        raise BusinessRuleError(
            'user_code_generation',
            f"Failed to generate a unique user code after {max_attempts} attempts"
        )
    
    def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List of active users
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE status = ?
            ORDER BY full_name
        """
        
        rows = self._execute_query(query, (UserStatus.ACTIVE.value,))
        return [self._row_to_model(row) for row in rows]
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """
        Get all users with the specified role.
        
        Args:
            role: The user role to filter by
            
        Returns:
            List of users with the specified role
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE role = ?
            ORDER BY full_name
        """
        
        rows = self._execute_query(query, (role.value,))
        return [self._row_to_model(row) for row in rows]
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: The ID of the user to deactivate
            
        Returns:
            True if the user was deactivated, False if not found
            
        Raises:
            BusinessRuleError: If the user is the last active admin
        """
        # Check if this is the last active admin
        admin_count_query = """
            SELECT COUNT(*) as count
            FROM users
            WHERE role = ? AND status = ?
        """
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get the user to check their role
            user = self.get_by_id(user_id)
            if not user:
                return False
                
            # If user is an admin, check if they're the last one
            if user.role == UserRole.ADMIN:
                cursor.execute(
                    admin_count_query,
                    (UserRole.ADMIN.value, UserStatus.ACTIVE.value)
                )
                admin_count = cursor.fetchone()['count']
                
                if admin_count <= 1:
                    raise BusinessRuleError(
                        'last_admin',
                        "Cannot deactivate the last active admin account"
                    )
            
            # Deactivate the user
            query = f"""
                UPDATE {self.table_name}
                SET status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            cursor.execute(query, (UserStatus.INACTIVE.value, user_id))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get statistics about users in the system.
        
        Returns:
            Dictionary containing various user statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_users,
                SUM(CASE WHEN role = 'Admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'Member' THEN 1 ELSE 0 END) as member_count,
                COUNT(DISTINCT strftime('%Y', created_at)) as years_active
            FROM users
        """
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            stats = dict(cursor.fetchone())
            
            # Add some calculated fields
            stats['inactive_users'] = stats['total_users'] - stats['active_users']
            stats['active_percentage'] = (
                (stats['active_users'] / stats['total_users']) * 100 
                if stats['total_users'] > 0 else 0
            )
            
            return stats
