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

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search fines by user, book, or date")
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #f6f7fa;
                border: none;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 24px;
            }
        """)
        main_layout.addWidget(search_bar)

        # Table data
        data = [
            ("#12345", "The Secret Garden", "2024-01-15", "2024-02-15", "10", "$5.00", "Unpaid"),
            ("#67890", "Pride and Prejudice", "2024-02-01", "2024-03-01", "5", "$2.50", "Paid"),
            ("#24680", "To Kill a Mockingbird", "2024-03-10", "2024-04-10", "15", "$7.50", "Unpaid"),
            ("#13579", "The Great Gatsby", "2024-04-05", "2024-05-05", "2", "$1.00", "Paid"),
            ("#97531", "1984", "2024-05-20", "2024-06-20", "8", "$4.00", "Unpaid"),
            ("#86420", "The Catcher in the Rye", "2024-06-12", "2024-07-12", "12", "$6.00", "Paid"),
            ("#75309", "Moby Dick", "2024-07-01", "2024-08-01", "3", "$1.50", "Unpaid"),
        ]
        table = QTableWidget(len(data), 7)
        table.setHorizontalHeaderLabels([
            "User ID", "Book Title", "Issue Date", "Return Date", "Overdue Days", "Fine Amount", "Payment Status"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(48)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setStyleSheet("""
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
        for row, (user_id, book, issue, ret, days, fine, status) in enumerate(data):
            table.setItem(row, 0, QTableWidgetItem(user_id))
            table.setItem(row, 1, QTableWidgetItem(book))
            table.setItem(row, 2, QTableWidgetItem(issue))
            table.setItem(row, 3, QTableWidgetItem(ret))
            table.setItem(row, 4, QTableWidgetItem(days))
            table.setItem(row, 5, QTableWidgetItem(fine))
            # Payment Status pill
            pill = QLabel(status)
            pill.setAlignment(Qt.AlignCenter)
            pill.setFixedHeight(32)
            if status == "Paid":
                pill.setStyleSheet("background: #f3f4f6; color: #232b36; border-radius: 16px; font-size: 15px; font-weight: 700; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; padding: 0 24px;")
            else:
                pill.setStyleSheet("background: #f3f4f6; color: #232b36; border-radius: 16px; font-size: 15px; font-weight: 700; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; padding: 0 24px;")
            pill.setText(status)
            table.setCellWidget(row, 6, pill)
        main_layout.addWidget(table) 