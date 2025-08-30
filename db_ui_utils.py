"""
Database UI Utilities for PyQt5
Provides helper functions for database operations in the UI layer.
"""

from PyQt5.QtWidgets import QMessageBox, QTableWidget, QTableWidgetItem, QComboBox
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import logging
from db_operations import db_ops

logger = logging.getLogger(__name__)

class DBUIUtils:
    """Utility class for database-related UI operations."""
    
    @staticmethod
    def safe_db_operation(
        operation: Callable,
        success_msg: str = "",
        error_msg: str = "An error occurred",
        parent=None,
        show_error: bool = True
    ) -> Any:
        """
        Safely execute a database operation with error handling.
        
        Args:
            operation: The database operation function to call
            success_msg: Message to show on success (empty for no message)
            error_msg: Base error message to show on failure
            parent: Parent widget for message boxes
            show_error: Whether to show error messages to the user
            
        Returns:
            The result of the operation or None if failed
        """
        try:
            result = operation()
            if success_msg:
                QMessageBox.information(parent, "Success", success_msg)
            return result
        except Exception as e:
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            if show_error:
                QMessageBox.critical(
                    parent, 
                    "Error", 
                    f"{error_msg}: {str(e)}"
                )
            return None
    
    @staticmethod
    def populate_table(
        table: QTableWidget,
        data: List[Dict[str, Any]],
        headers: List[str],
        column_keys: List[str],
        row_formatter: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    ) -> None:
        """
        Populate a QTableWidget with data from a list of dictionaries.
        
        Args:
            table: The QTableWidget to populate
            data: List of dictionaries containing the data
            headers: List of column headers
            column_keys: List of dictionary keys to use for each column
            row_formatter: Optional function to format each row's data
        """
        try:
            table.setRowCount(0)  # Clear existing rows
            
            if not data:
                return
                
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            for row_idx, row_data in enumerate(data):
                if row_formatter:
                    row_data = row_formatter(row_data)
                
                table.insertRow(row_idx)
                
                for col_idx, key in enumerate(column_keys):
                    value = row_data.get(key, "")
                    
                    # Handle different data types
                    if isinstance(value, (int, float)):
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, value)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    elif isinstance(value, bool):
                        item = QTableWidgetItem()
                        item.setData(Qt.DisplayRole, "Yes" if value else "No")
                        item.setTextAlignment(Qt.AlignCenter)
                    elif isinstance(value, datetime):
                        item = QTableWidgetItem(value.strftime("%Y-%m-%d %H:%M"))
                    else:
                        item = QTableWidgetItem(str(value) if value is not None else "")
                    
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    table.setItem(row_idx, col_idx, item)
            
            # Resize columns to contents
            table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error populating table: {e}")
    
    @staticmethod
    def populate_combo(
        combo: QComboBox,
        data: List[Dict[str, Any]],
        display_key: str,
        value_key: str,
        placeholder: str = "-- Select --",
        add_placeholder: bool = True
    ) -> None:
        """
        Populate a QComboBox with data.
        
        Args:
            combo: The QComboBox to populate
            data: List of dictionaries containing the data
            display_key: Dictionary key to use for display text
            value_key: Dictionary key to use for item data
            placeholder: Placeholder text for the first item
            add_placeholder: Whether to add a placeholder as the first item
        """
        try:
            combo.clear()
            
            if add_placeholder:
                combo.addItem(placeholder, None)
            
            for item in data:
                display_text = str(item.get(display_key, ""))
                value = item.get(value_key)
                combo.addItem(display_text, value)
                
        except Exception as e:
            logger.error(f"Error populating combo box: {e}")
    
    @staticmethod
    def get_selected_row_data(
        table: QTableWidget,
        data: List[Dict[str, Any]],
        id_column: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Get the selected row's data from a table.
        
        Args:
            table: The QTableWidget
            data: The original data list used to populate the table
            id_column: The column index containing the ID
            
        Returns:
            The selected row's data or None if no row is selected
        """
        try:
            selected_rows = table.selectionModel().selectedRows()
            if not selected_rows:
                return None
                
            row = selected_rows[0].row()
            item = table.item(row, id_column)
            if not item:
                return None
                
            item_id = item.data(Qt.DisplayRole)
            return next((item for item in data if str(item.get('id')) == str(item_id)), None)
            
        except Exception as e:
            logger.error(f"Error getting selected row data: {e}")
            return None
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format a number as currency."""
        try:
            return f"${amount:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
    
    @staticmethod
    def format_date(date_str: str, input_format: str = "%Y-%m-%d") -> str:
        """Format a date string to a more readable format."""
        try:
            date = datetime.strptime(date_str, input_format)
            return date.strftime("%b %d, %Y")
        except (ValueError, TypeError):
            return ""
    
    @staticmethod
    def get_date_range(
        days_back: int = 30,
        end_date: Optional[QDate] = None
    ) -> tuple:
        """
        Get a date range for reports.
        
        Args:
            days_back: Number of days to go back from end_date
            end_date: End date (defaults to today)
            
        Returns:
            Tuple of (start_date, end_date) as strings in 'YYYY-MM-DD' format
        """
        end = end_date.toPyDate() if end_date else datetime.now().date()
        start = end - datetime.timedelta(days=days_back)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

# Singleton instance
db_ui = DBUIUtils()
