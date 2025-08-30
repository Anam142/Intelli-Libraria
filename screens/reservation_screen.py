"""
Reservation Management Screen
Demonstrates robust database operations in a PyQt5 UI.
"""

import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QLineEdit,
    QDateEdit, QComboBox, QMessageBox, QFormLayout, QGroupBox,
    QStatusBar, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# Import our database utilities
from db_operations import db_ops
from db_ui_utils import db_ui

class ReservationScreen(QMainWindow):
    """Main reservation management screen."""
    
    def __init__(self, user_id: int = None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_reservations = []
        self.available_books = []
        
        self.setWindowTitle("Reservation Management")
        self.setMinimumSize(1000, 600)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Initialize the UI components."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create tabs
        self._create_reservation_tab(tabs)
        self._create_my_reservations_tab(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_reservation_tab(self, tabs):
        """Create the 'New Reservation' tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search group
        search_group = QGroupBox("Search Books")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, or ISBN...")
        self.search_input.returnPressed.connect(self._search_books)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._search_books)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_group.setLayout(search_layout)
        
        # Results table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(["ID", "Title", "Author", "ISBN", "Available"])
        self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Reservation form
        form_group = QGroupBox("Create Reservation")
        form_layout = QFormLayout()
        
        self.user_id_input = QLineEdit(str(self.user_id) if self.user_id else "")
        self.user_id_input.setReadOnly(bool(self.user_id))
        
        self.book_id_input = QLineEdit()
        self.book_id_input.setReadOnly(True)
        
        self.book_title_input = QLineEdit()
        self.book_title_input.setReadOnly(True)
        
        self.reservation_date = QDateEdit()
        self.reservation_date.setDate(QDate.currentDate())
        self.reservation_date.setCalendarPopup(True)
        
        form_layout.addRow("User ID:", self.user_id_input)
        form_layout.addRow("Book ID:", self.book_id_input)
        form_layout.addRow("Title:", self.book_title_input)
        form_layout.addRow("Reservation Date:", self.reservation_date)
        
        reserve_btn = QPushButton("Create Reservation")
        reserve_btn.clicked.connect(self._create_reservation)
        
        form_layout.addRow(reserve_btn)
        form_group.setLayout(form_layout)
        
        # Connect row selection
        self.books_table.itemSelectionChanged.connect(self._on_book_selected)
        
        # Add widgets to tab layout
        layout.addWidget(search_group)
        layout.addWidget(self.books_table)
        layout.addWidget(form_group)
        
        # Add tab
        tabs.addTab(tab, "New Reservation")
    
    def _create_my_reservations_tab(self, tabs):
        """Create the 'My Reservations' tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Reservations table
        self.reservations_table = QTableWidget()
        self.reservations_table.setColumnCount(6)
        self.reservations_table.setHorizontalHeaderLabels([
            "ID", "Book", "Reservation Date", "Status", "Expiry Date", "Actions"
        ])
        self.reservations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.reservations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.reservations_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._load_my_reservations)
        
        # Add widgets to layout
        layout.addWidget(self.reservations_table)
        layout.addWidget(refresh_btn)
        
        # Add tab
        tabs.addTab(tab, "My Reservations")
    
    def _load_data(self):
        """Load initial data."""
        if self.user_id:
            self._load_my_reservations()
    
    def _search_books(self):
        """Search for books based on user input."""
        query = self.search_input.text().strip()
        
        def search():
            self.available_books = db_ops.search_books(
                query=query,
                available_only=True,
                limit=50
            )
            self._update_books_table()
        
        db_ui.safe_db_operation(
            search,
            error_msg="Failed to search books",
            parent=self
        )
    
    def _update_books_table(self):
        """Update the books table with search results."""
        try:
            self.books_table.setRowCount(0)
            
            for book in self.available_books:
                row = self.books_table.rowCount()
                self.books_table.insertRow(row)
                
                self.books_table.setItem(row, 0, QTableWidgetItem(str(book.get('id', ''))))
                self.books_table.setItem(row, 1, QTableWidgetItem(book.get('title', '')))
                self.books_table.setItem(row, 2, QTableWidgetItem(book.get('author', '')))
                self.books_table.setItem(row, 3, QTableWidgetItem(book.get('isbn', '')))
                self.books_table.setItem(row, 4, QTableWidgetItem(str(book.get('available', 0))))
                
        except Exception as e:
            logger.error(f"Error updating books table: {e}")
            QMessageBox.critical(self, "Error", "Failed to update books list.")
    
    def _on_book_selected(self):
        """Handle book selection from the table."""
        selected = self.books_table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        book_id = self.books_table.item(row, 0).text()
        book_title = self.books_table.item(row, 1).text()
        
        self.book_id_input.setText(book_id)
        self.book_title_input.setText(book_title)
    
    def _create_reservation(self):
        """Create a new reservation."""
        try:
            user_id = int(self.user_id_input.text())
            book_id = int(self.book_id_input.text())
            reservation_date = self.reservation_date.date().toString("yyyy-MM-dd")
            
            # Validate inputs
            if not book_id:
                QMessageBox.warning(self, "Validation Error", "Please select a book first.")
                return
                
            # Create reservation using our safe operation
            def reserve():
                result = db_ops.create_reservation(user_id, book_id)
                if result.get('success'):
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Reservation created successfully!\n"
                        f"Reservation ID: {result.get('reservation_id')}"
                    )
                    self._clear_form()
                    self._load_my_reservations()
                else:
                    QMessageBox.warning(
                        self,
                        "Reservation Failed",
                        result.get('message', 'Failed to create reservation.')
                    )
            
            db_ui.safe_db_operation(
                reserve,
                error_msg="Failed to create reservation",
                parent=self,
                show_error=False  # We handle errors in the reserve() function
            )
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", "Please check your inputs and try again.")
        except Exception as e:
            logger.error(f"Error creating reservation: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                "An unexpected error occurred while creating the reservation."
            )
    
    def _load_my_reservations(self):
        """Load the current user's reservations."""
        if not self.user_id:
            return
            
        def load():
            self.current_reservations = db_ops.get_user_reservations(self.user_id)
            self._update_reservations_table()
        
        db_ui.safe_db_operation(
            load,
            error_msg="Failed to load reservations",
            parent=self
        )
    
    def _update_reservations_table(self):
        """Update the reservations table with user's reservations."""
        try:
            self.reservations_table.setRowCount(0)
            
            for res in self.current_reservations:
                row = self.reservations_table.rowCount()
                self.reservations_table.insertRow(row)
                
                # Add data to columns
                self.reservations_table.setItem(row, 0, QTableWidgetItem(str(res.get('id', ''))))
                self.reservations_table.setItem(row, 1, QTableWidgetItem(res.get('title', '')))
                self.reservations_table.setItem(row, 2, QTableWidgetItem(res.get('reservation_date', '')))
                
                # Status with color coding
                status_item = QTableWidgetItem(res.get('status', '').capitalize())
                status = res.get('status', '').lower()
                if status == 'approved':
                    status_item.setForeground(Qt.darkGreen)
                elif status == 'pending':
                    status_item.setForeground(Qt.darkBlue)
                elif status in ['rejected', 'cancelled']:
                    status_item.setForeground(Qt.red)
                self.reservations_table.setItem(row, 3, status_item)
                
                self.reservations_table.setItem(row, 4, QTableWidgetItem(res.get('expiry_date', '')))
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(5, 2, 5, 2)
                
                if status == 'pending':
                    cancel_btn = QPushButton("Cancel")
                    cancel_btn.clicked.connect(lambda _, r=row: self._cancel_reservation(r))
                    action_layout.addWidget(cancel_btn)
                
                action_widget.setLayout(action_layout)
                self.reservations_table.setCellWidget(row, 5, action_widget)
            
            # Resize columns to fit content
            self.reservations_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error updating reservations table: {e}")
            QMessageBox.critical(self, "Error", "Failed to update reservations list.")
    
    def _cancel_reservation(self, row: int):
        """Cancel the selected reservation."""
        try:
            reservation_id = int(self.reservations_table.item(row, 0).text())
            
            reply = QMessageBox.question(
                self,
                'Confirm Cancellation',
                'Are you sure you want to cancel this reservation?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                def cancel():
                    result = db_ops.cancel_reservation(reservation_id)
                    if result.get('success'):
                        QMessageBox.information(
                            self,
                            "Success",
                            "The reservation has been cancelled."
                        )
                        self._load_my_reservations()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            result.get('message', 'Failed to cancel reservation.')
                        )
                
                db_ui.safe_db_operation(
                    cancel,
                    error_msg="Failed to cancel reservation",
                    parent=self,
                    show_error=False  # We handle errors in the cancel() function
                )
                
        except Exception as e:
            logger.error(f"Error cancelling reservation: {e}")
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred while cancelling the reservation."
            )
    
    def _clear_form(self):
        """Clear the reservation form."""
        self.book_id_input.clear()
        self.book_title_input.clear()
        self.reservation_date.setDate(QDate.currentDate())
        self.books_table.clearSelection()


def main():
    """Run the reservation screen as a standalone application."""
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show the main window
    window = ReservationScreen(user_id=1)  # Example user ID
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
