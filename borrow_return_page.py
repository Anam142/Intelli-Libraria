from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BorrowBookScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borrow Book")
        self.setStyleSheet("background-color: #ffffff;")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Borrow Book")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #000000; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-bottom: 5px;")
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter User ID")
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(user_id_label)
        layout.addWidget(self.user_id_input)

        # Book ID
        book_id_label = QLabel("Book ID")
        book_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter Book ID")
        self.book_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_id_input)

        layout.addStretch()

        # Borrow Button
        self.borrow_button = QPushButton("Borrow Book")
        self.borrow_button.setCursor(Qt.PointingHandCursor)
        self.borrow_button.clicked.connect(self.borrow_book_action)
        self.borrow_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.borrow_button)
        layout.addLayout(button_layout)

    def borrow_book_action(self):
        user_id = self.user_id_input.text()
        book_id = self.book_id_input.text()
        if user_id and book_id:
            print(f"Borrowing book... User ID: {user_id}, Book ID: {book_id}")
            # Here you would add your database logic to borrow the book
            self.close()
        else:
            print("User ID and Book ID are required.")

class ReturnBookScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Return Book")
        self.setStyleSheet("background-color: #ffffff;")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Return Book")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #000000; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-bottom: 5px;")
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter User ID or Scan Barcode")
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(user_id_label)
        layout.addWidget(self.user_id_input)

        # Book ID
        book_id_label = QLabel("Book ID")
        book_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter Book ID or Scan Barcode")
        self.book_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_id_input)

        layout.addStretch()

        # Return Button
        self.return_button = QPushButton("Return Book")
        self.return_button.setCursor(Qt.PointingHandCursor)
        self.return_button.clicked.connect(self.return_book_action)
        self.return_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.return_button)
        layout.addLayout(button_layout)

    def return_book_action(self):
        user_id = self.user_id_input.text()
        book_id = self.book_id_input.text()
        if user_id and book_id:
            print(f"Returning book... User ID: {user_id}, Book ID: {book_id}")
            # Here you would add your database logic to return the book
            self.close()
        else:
            print("User ID and Book ID are required.")

class BorrowReturnPage(QWidget):
    def __init__(self):
        super().__init__()
        self.borrow_book_screen = None
        self.return_book_screen = None
        self.setStyleSheet("background: #f4f5f7;")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Centered, wide card with less horizontal margin
        card = QFrame()
        card.setMinimumWidth(0)  # Remove minimum width
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet("""
            QFrame {
                background: #fff;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
                padding: 0px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)  # Add small side margins back
        card_layout.setSpacing(10)  # More compact vertical spacing

        # Header (left-aligned, no pill)
        header = QLabel("Borrow / Return Books")
        header.setStyleSheet("font-size: 28px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 700; color: #232b36; background: none; border: none; margin-bottom: 8px;")
        card_layout.addWidget(header, alignment=Qt.AlignLeft)

        # Input fields (full width, left-aligned)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        # User ID label
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 16px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: bold; margin-bottom: 2px; background: none; border: none;")
        input_layout.addWidget(user_id_label)
        user_id = QLineEdit()
        user_id.setPlaceholderText("Enter User ID or Scan Barcode")
        user_id.setFixedWidth(400)
        user_id.setStyleSheet("""
            QLineEdit {
                background: #f9fafb;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
            }
        """)
        input_layout.addWidget(user_id)
        # Book ID label
        book_id_label = QLabel("Book ID")
        book_id_label.setStyleSheet("font-size: 16px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: bold; margin-top: 8px; margin-bottom: 2px; background: none; border: none;")
        input_layout.addWidget(book_id_label)
        book_id = QLineEdit()
        book_id.setPlaceholderText("Enter Book ID or Scan Barcode")
        book_id.setFixedWidth(400)
        book_id.setStyleSheet("""
            QLineEdit {
                background: #f9fafb;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
            }
        """)
        input_layout.addWidget(book_id)
        card_layout.addLayout(input_layout)

        # Book Details section
        book_details_label = QLabel("Book Details")
        book_details_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none;")
        card_layout.addWidget(book_details_label, alignment=Qt.AlignLeft)
        book_details = QFrame()
        book_details.setStyleSheet("border: none;")
        book_grid = QGridLayout(book_details)
        book_grid.setContentsMargins(0, 0, 0, 0)
        book_grid.setSpacing(0)
        book_labels = ["Title", "Author", "ISBN"]
        for i, label_text in enumerate(book_labels):
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 13px; color: #6b7280; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none; padding: 4px 0;")
            value = QLabel("N/A")
            value.setStyleSheet("font-size: 13px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none; padding: 4px 0;")
            book_grid.addWidget(label, i, 0)
            book_grid.addWidget(value, i, 1)
        card_layout.addWidget(book_details)

        # User Details section
        user_details_label = QLabel("User Details")
        user_details_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none;")
        card_layout.addWidget(user_details_label, alignment=Qt.AlignLeft)
        user_details = QFrame()
        user_details.setStyleSheet("border: none;")
        user_grid = QGridLayout(user_details)
        user_grid.setContentsMargins(0, 0, 0, 0)
        user_grid.setSpacing(0)
        user_labels = ["Name", "Email", "Membership ID"]
        for i, label_text in enumerate(user_labels):
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 13px; color: #6b7280; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none; padding: 4px 0;")
            value = QLabel("N/A")
            value.setStyleSheet("font-size: 13px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none; padding: 4px 0;")
            user_grid.addWidget(label, i, 0)
            user_grid.addWidget(value, i, 1)
        card_layout.addWidget(user_details)

        # Buttons (Borrow and Return)
        btn_row = QHBoxLayout()
        borrow_btn = QPushButton("Borrow Book")
        borrow_btn.setCursor(Qt.PointingHandCursor)
        borrow_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: #fff;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px 32px;
                margin-right: 16px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        borrow_btn.clicked.connect(self.show_borrow_screen)

        return_btn = QPushButton("Return Book")
        return_btn.clicked.connect(self.show_return_screen)
        return_btn.setCursor(Qt.PointingHandCursor)
        return_btn.setStyleSheet("""
            QPushButton {
                background: #f4f5f7;
                color: #232b36;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px 32px;
                border: 1.5px solid #e5e7eb;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        btn_row.addWidget(borrow_btn, alignment=Qt.AlignLeft)
        btn_row.addStretch(1)
        btn_row.addWidget(return_btn, alignment=Qt.AlignRight)
        card_layout.addLayout(btn_row)

        # Recent Transactions section
        recent_label = QLabel("Recent Transactions")
        recent_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none; margin-bottom: 4px;")
        card_layout.addWidget(recent_label, alignment=Qt.AlignLeft)
        transactions = [
            ("2024-01-15", "Emily Carter", "The Great Adventure", "Borrowed"),
            ("2024-01-10", "David Lee", "Mystery of the Lost City", "Returned"),
            ("2024-01-05", "Emily Carter", "The Secret Garden", "Borrowed"),
        ]
        table = QTableWidget(len(transactions), 4)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        table.setHorizontalHeaderLabels(["Date", "User", "Book", "Action"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(38)
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 8px;
                font-size: 13px;
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
                font-weight: 600;
                font-size: 13px;
                border: none;
                padding: 8px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        for row, (date, user, book, action) in enumerate(transactions):
            item_date = QTableWidgetItem(date)
            item_date.setFont(QFont("Inter", 13))
            table.setItem(row, 0, item_date)
            item_user = QTableWidgetItem(user)
            item_user.setFont(QFont("Inter", 13))
            table.setItem(row, 1, item_user)
            item_book = QTableWidgetItem(book)
            item_book.setFont(QFont("Inter", 13))
            table.setItem(row, 2, item_book)
            item_action = QTableWidgetItem(action)
            item_action.setFont(QFont("Inter", 13))
            table.setItem(row, 3, item_action)
        card_layout.addWidget(table)

        outer_layout.addWidget(card)  # No alignment, so it fills width

    def show_borrow_screen(self):
        if not self.borrow_book_screen:
            self.borrow_book_screen = BorrowBookScreen()
        self.borrow_book_screen.showMaximized()

    def show_return_screen(self):
        if not self.return_book_screen:
            self.return_book_screen = ReturnBookScreen()
        self.return_book_screen.showMaximized()