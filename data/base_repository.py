"""
Base repository class with common CRUD operations.
"""
from typing import Type, TypeVar, Generic, List, Dict, Any, Optional, Tuple
import sqlite3
from datetime import datetime
from dataclasses import fields, is_dataclass
import json

from .database import get_db
from .errors import (
    NotFoundError, 
    UniquenessError, 
    ForeignKeyError,
    StateError
)
from .validators import validate

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations.
    
    Subclasses should define:
    - table_name: str - The database table name
    - model_class: Type[T] - The model class this repository handles
    - columns: List[str] - List of column names (excluding id)
    """
    
    table_name: str
    model_class: Type[T]
    columns: List[str] = []
    
    def __init__(self):
        if not hasattr(self, 'table_name') or not self.table_name:
            raise NotImplementedError("Subclasses must define 'table_name' class variable")
        if not hasattr(self, 'model_class') or not self.model_class:
            raise NotImplementedError("Subclasses must define 'model_class' class variable")
        if not self.columns:
            raise NotImplementedError("Subclasses must define 'columns' class variable")
    
    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """Convert a database row to a model instance."""
        if not row:
            raise ValueError("Cannot convert None or empty row to model")
            
        # Convert datetime strings to datetime objects
        for field in fields(self.model_class):
            if field.name in row and row[field.name] is not None:
                if field.type == datetime and isinstance(row[field.name], str):
                    row[field.name] = datetime.fromisoformat(row[field.name])
                elif field.type == date and isinstance(row[field.name], str):
                    row[field.name] = date.fromisoformat(row[field.name])
                
        return self.model_class.from_dict(row)
    
    def _model_to_dict(self, model: T, exclude_none: bool = False) -> Dict[str, Any]:
        """Convert a model instance to a dictionary for database operations."""
        if not is_dataclass(model):
            raise ValueError("Model must be a dataclass instance")
            
        result = {}
        for field in fields(model):
            value = getattr(model, field.name)
            
            # Skip None values if exclude_none is True
            if exclude_none and value is None:
                continue
                
            # Convert datetime/date to ISO format strings
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
                
            result[field.name] = value
            
        return result
    
    def _get_placeholders(self, data: Dict[str, Any]) -> str:
        """Generate placeholders for SQL queries."""
        return ', '.join(['?'] * len(data))
    
    def _get_set_clause(self, data: Dict[str, Any]) -> str:
        """Generate SET clause for UPDATE queries."""
        return ', '.join([f"{col} = ?" for col in data.keys()])
    
    def _execute_query(
        self, 
        query: str, 
        params: Tuple[Any, ...] = (), 
        fetch_one: bool = False,
        lastrowid: bool = False
    ) -> Any:
        """
        Execute a query and return the result.
        
        Args:
            query: The SQL query to execute
            params: Parameters for the query
            fetch_one: If True, fetch only one row
            lastrowid: If True, return the last inserted row ID
            
        Returns:
            The query result (row(s), rowcount, or lastrowid)
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # For INSERT/UPDATE/DELETE, return the rowcount
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()  # Ensure changes are committed
                return cursor.rowcount
                
            if lastrowid:
                conn.commit()  # Ensure changes are committed
                return cursor.lastrowid
                
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
                
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def create(self, model: T) -> T:
        """
        Create a new record in the database.
        
        Args:
            model: The model instance to create
            
        Returns:
            The created model with ID set
            
        Raises:
            UniquenessError: If a unique constraint is violated
            ForeignKeyError: If a foreign key constraint is violated
            ValidationError: If model validation fails
        """
        # Validate the model before saving
        validate(model)
        
        # Convert model to dict and remove None values
        data = self._model_to_dict(model, exclude_none=True)
        
        # Remove ID if it's None or 0 (new record)
        data.pop('id', None)
        
        # Prepare the query
        columns = ', '.join(data.keys())
        placeholders = self._get_placeholders(data)
        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
        """
        
        try:
            # Execute the query and get the new ID
            model_id = self._execute_query(
                query, 
                tuple(data.values()),
                lastrowid=True
            )
            
            # Set the ID on the model and return it
            if hasattr(model, 'id') and model_id:
                model.id = model_id
                
            return model
            
        except sqlite3.IntegrityError as e:
            # Handle unique constraint violations
            if 'UNIQUE constraint failed' in str(e):
                # Extract the column name from the error message
                # Format: "UNIQUE constraint failed: table.column"
                parts = str(e).split(':')
                if len(parts) > 1:
                    column = parts[1].strip().split('.')[-1]
                    value = data.get(column, 'unknown')
                    raise UniquenessError(column, value) from e
            
            # Handle foreign key violations
            if 'FOREIGN KEY constraint failed' in str(e):
                # Extract the table and column from the error message
                # This is a bit fragile but SQLite doesn't provide better error details
                for col in data.keys():
                    if col.endswith('_id'):
                        table = col[:-3] + 's'  # Simple pluralization
                        raise ForeignKeyError(table, col, data[col]) from e
            
            # Re-raise other integrity errors
            raise
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            id: The ID of the record to retrieve
            
        Returns:
            The model instance, or None if not found
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE id = ?
        """
        
        row = self._execute_query(query, (id,), fetch_one=True)
        return self._row_to_model(row) if row else None
    
    def get_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Get all records matching the given filters.
        
        Args:
            filters: Dictionary of column-value pairs to filter by
            order_by: Column to order by (e.g., 'name DESC')
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        query_parts = [f"SELECT * FROM {self.table_name}"]
        params = []
        
        # Add WHERE clause if filters are provided
        if filters:
            conditions = []
            for col, value in filters.items():
                if value is None:
                    conditions.append(f"{col} IS NULL")
                else:
                    conditions.append(f"{col} = ?")
                    params.append(value)
            
            query_parts.append("WHERE " + " AND ".join(conditions))
        
        # Add ORDER BY clause if specified
        if order_by:
            query_parts.append(f"ORDER BY {order_by}")
        
        # Add LIMIT and OFFSET if specified
        if limit is not None:
            query_parts.append("LIMIT ?")
            params.append(limit)
            
            if offset is not None:
                query_parts.append("OFFSET ?")
                params.append(offset)
        
        # Execute the query
        rows = self._execute_query("\n".join(query_parts), tuple(params))
        return [self._row_to_model(row) for row in rows]
    
    def update(self, model: T) -> bool:
        """
        Update an existing record.
        
        Args:
            model: The model instance with updated values
            
        Returns:
            True if the record was updated, False if not found
            
        Raises:
            ValueError: If the model has no ID
            UniquenessError: If a unique constraint is violated
            ForeignKeyError: If a foreign key constraint is violated
            ValidationError: If model validation fails
        """
        if not hasattr(model, 'id') or not model.id:
            raise ValueError("Cannot update model without an ID")
        
        # Validate the model before updating
        validate(model)
        
        # Convert model to dict and remove None values
        data = self._model_to_dict(model, exclude_none=True)
        
        # Remove ID from the data to update
        data.pop('id', None)
        
        if not data:
            return False  # Nothing to update
        
        # Prepare the query
        set_clause = self._get_set_clause(data)
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        try:
            # Add the ID to the parameters for the WHERE clause
            params = list(data.values()) + [model.id]
            
            # Execute the query
            rowcount = self._execute_query(query, tuple(params))
            return rowcount > 0
            
        except sqlite3.IntegrityError as e:
            # Handle unique constraint violations
            if 'UNIQUE constraint failed' in str(e):
                # Extract the column name from the error message
                parts = str(e).split(':')
                if len(parts) > 1:
                    column = parts[1].strip().split('.')[-1]
                    value = data.get(column, 'unknown')
                    raise UniquenessError(column, value) from e
            
            # Handle foreign key violations
            if 'FOREIGN KEY constraint failed' in str(e):
                # Extract the table and column from the error message
                for col in data.keys():
                    if col.endswith('_id'):
                        table = col[:-3] + 's'  # Simple pluralization
                        raise ForeignKeyError(table, col, data[col]) from e
            
            # Re-raise other integrity errors
            raise
    
    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: The ID of the record to delete
            
        Returns:
            True if the record was deleted, False if not found
        """
        query = f"""
            DELETE FROM {self.table_name}
            WHERE id = ?
        """
        
        cursor = self._execute_query(query, (id,))
        return cursor.rowcount > 0
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records matching the given filters.
        
        Args:
            filters: Dictionary of column-value pairs to filter by
            
        Returns:
            The number of matching records
        """
        query_parts = [f"SELECT COUNT(*) as count FROM {self.table_name}"]
        params = []
        
        # Add WHERE clause if filters are provided
        if filters:
            conditions = []
            for col, value in filters.items():
                if value is None:
                    conditions.append(f"{col} IS NULL")
                else:
                    conditions.append(f"{col} = ?")
                    params.append(value)
            
            query_parts.append("WHERE " + " AND ".join(conditions))
        
        # Execute the query
        row = self._execute_query("\n".join(query_parts), tuple(params), fetch_one=True)
        return row['count'] if row else 0
