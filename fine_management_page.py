from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout, QSizePolicy, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class FineManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(0)

        # Heading
        heading = QLabel("Fine Management")
        heading.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 0px; margin-top: 0px; background: none; border: none;")
        main_layout.addWidget(heading, alignment=Qt.AlignLeft)

        # Subtitle
        subtitle = QLabel("Manage and oversee all fine records within the library system.")
        subtitle.setStyleSheet("font-size: 16px; color: #6b7280; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 400; margin-bottom: 24px; margin-top: 0px; background: none; border: none;")
        main_layout.addWidget(subtitle, alignment=Qt.AlignLeft)

        # Store the table data as instance variable for searching
        self.table_data = [
            ("#12345", "The Secret Garden", "2024-01-15", "2024-02-15", "10", "$5.00", "Unpaid"),
            ("#67890", "Pride and Prejudice", "2024-02-01", "2024-03-01", "5", "$2.50", "Paid"),
            ("#24680", "To Kill a Mockingbird", "2024-03-10", "2024-04-10", "15", "$7.50", "Unpaid"),
            ("#13579", "The Great Gatsby", "2024-04-05", "2024-05-05", "2", "$1.00", "Paid"),
            ("#97531", "1984", "2024-05-20", "2024-06-20", "8", "$4.00", "Unpaid"),
            ("#86420", "The Catcher in the Rye", "2024-06-12", "2024-07-12", "12", "$6.00", "Paid"),
            ("#75309", "Moby Dick", "2024-07-01", "2024-08-01", "3", "$1.50", "Unpaid"),
        ]
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search fines by user, book, or date")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #1976d2;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)
        main_layout.addWidget(self.search_bar)

        # Create table
        self.table = QTableWidget(len(self.table_data), 7)
        self.table.setHorizontalHeaderLabels([
            "User ID", "Book Title", "Issue Date", "Return Date", "Overdue Days", "Fine Amount", "Payment Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1px solid #e5e7eb;
                padding: 0px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 0px 0px;
            }
            QHeaderView::section {
                background: #f5f5f5;
                color: #232b36;
                font-weight: 700;
                font-size: 15px;
                border: none;
                padding: 14px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Initial table population
        self.populate_table(self.table_data)
        main_layout.addWidget(self.table)

    def populate_table(self, data):
        """Populate the table with the provided data"""
        self.table.setRowCount(len(data))
        for row, (user_id, book, issue, ret, days, fine, status) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(user_id))
            self.table.setItem(row, 1, QTableWidgetItem(book))
            self.table.setItem(row, 2, QTableWidgetItem(issue))
            self.table.setItem(row, 3, QTableWidgetItem(ret))
            self.table.setItem(row, 4, QTableWidgetItem(days))
            self.table.setItem(row, 5, QTableWidgetItem(fine))
            
            # Payment Status pill
            pill = QLabel(status)
            pill.setAlignment(Qt.AlignCenter)
            pill.setFixedHeight(32)
            if status == "Paid":
                pill.setStyleSheet("""
                    background: #e8f5e9;
                    color: #2e7d32;
                    border-radius: 16px;
                    font-size: 15px;
                    font-weight: 700;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    padding: 0 24px;
                """)
            else:
                pill.setStyleSheet("""
                    background: #ffebee;
                    color: #c62828;
                    border-radius: 16px;
                    font-size: 15px;
                    font-weight: 700;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    padding: 0 24px;
                """)
            pill.setText(status)
            self.table.setCellWidget(row, 6, pill)
    
    def filter_table(self):
        """Filter the table based on search text"""
        search_text = self.search_bar.text().lower()
        if not search_text:
            self.populate_table(self.table_data)
            return
            
        filtered_data = []
        for row in self.table_data:
            # Check if search text exists in any of the columns
            if (search_text in row[0].lower() or  # User ID
                search_text in row[1].lower() or  # Book Title
                search_text in row[2].lower() or  # Issue Date
                search_text in row[3].lower() or  # Return Date
                search_text in row[4].lower() or  # Overdue Days
                search_text in row[5].lower() or  # Fine Amount
                search_text in row[6].lower()):   # Payment Status
                filtered_data.append(row)
                
        self.populate_table(filtered_data)