import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
                            QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt
import database

class LibrariaDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria - Dashboard")
        self.setMinimumSize(1000, 600)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.setup_book_inventory_tab()
        self.setup_user_management_tab()
        
        # Load initial data
        self.refresh_book_inventory()
        self.refresh_user_management()
    
    def setup_book_inventory_tab(self):
        """Set up the Book Inventory tab with a table and refresh button."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create refresh button
        btn_refresh = QPushButton("Refresh Book List")
        btn_refresh.clicked.connect(self.refresh_book_inventory)
        btn_refresh.setFixedWidth(150)
        
        # Create table
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(6)
        self.book_table.setHorizontalHeaderLabels([
            "Book ID", "Title", "Author", "Genre", "Quantity", "Available"
        ])
        
        # Configure table properties
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.book_table.verticalHeader().setVisible(False)
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add widgets to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_refresh)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.book_table)
        
        self.tabs.addTab(tab, "Book Inventory")
    
    def setup_user_management_tab(self):
        """Set up the User Management tab with a table and refresh button."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create refresh button
        btn_refresh = QPushButton("Refresh User List")
        btn_refresh.clicked.connect(self.refresh_user_management)
        btn_refresh.setFixedWidth(150)
        
        # Create table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels([
            "User ID", "Username", "Email", "Contact Number"
        ])
        
        # Configure table properties
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().setVisible(False)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add widgets to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_refresh)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.user_table)
        
        self.tabs.addTab(tab, "User Management")
    
    def refresh_book_inventory(self):
        """Refresh the book inventory table with data from the database."""
        try:
            books = database.get_all_books()
            self.book_table.setRowCount(len(books))
            
            for row, book in enumerate(books):
                self.book_table.setItem(row, 0, QTableWidgetItem(str(book.get('id', ''))))
                self.book_table.setItem(row, 1, QTableWidgetItem(book.get('title', '')))
                self.book_table.setItem(row, 2, QTableWidgetItem(book.get('author', '')))
                self.book_table.setItem(row, 3, QTableWidgetItem(book.get('genre', 'N/A')))
                self.book_table.setItem(row, 4, QTableWidgetItem(str(book.get('stock', 0))))
                available = "Yes" if book.get('stock', 0) > 0 else "No"
                self.book_table.setItem(row, 5, QTableWidgetItem(available))
                
                # Center align all cells
                for col in range(self.book_table.columnCount()):
                    item = self.book_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
    
    def refresh_user_management(self):
        """Refresh the user management table with data from the database."""
        try:
            users = database.get_all_users()
            self.user_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.get('id', ''))))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
                self.user_table.setItem(row, 3, QTableWidgetItem(user.get('phone', 'N/A')))
                
                # Center align all cells
                for col in range(self.user_table.columnCount()):
                    item = self.user_table.item(row, col)
                    if item:
                        item.setTextAlignment(Qt.AlignCenter)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = LibrariaDashboard()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
