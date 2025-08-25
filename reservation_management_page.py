from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QComboBox, QDateEdit, QMessageBox
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
import database

class CreateReservationScreen(QWidget):
    reservation_added = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Reservation")
        self.setStyleSheet("background-color: #ffffff;")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Create New Reservation")
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

        # Book ID or Book Title
        book_id_label = QLabel("Book ID or Book Title")
        book_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.book_search_input = QComboBox()
        self.book_search_input.setEditable(True)
        self.book_search_input.setPlaceholderText("Search for a book...")
        self.book_search_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_search_input)
        self.populate_books_dropdown()

        # Reservation Date
        reservation_date_label = QLabel("Reservation Date")
        reservation_date_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.reservation_date_input = QDateEdit()
        self.reservation_date_input.setDate(QDate.currentDate())
        self.reservation_date_input.setCalendarPopup(True)
        self.reservation_date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(reservation_date_label)
        layout.addWidget(self.reservation_date_input)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
        """)
        button_layout.addWidget(self.cancel_button)

        self.create_reservation_button = QPushButton("Create Reservation")
        self.create_reservation_button.setCursor(Qt.PointingHandCursor)
        self.create_reservation_button.clicked.connect(self.create_reservation_action)
        self.create_reservation_button.setStyleSheet("""
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
        button_layout.addWidget(self.create_reservation_button)
        layout.addLayout(button_layout)

    def populate_books_dropdown(self):
        self.book_search_input.addItem("Select a Book", -1)
        # Use live book titles and IDs from the database; ensure dropdown is enabled
        try:
            books = database.get_all_books()
            if books:
                for book in books:
                    self.book_search_input.addItem(book[1], book[0]) # Display title, store ID
        except Exception:
            pass

    def create_reservation_action(self):
        user_id_text = self.user_id_input.text().strip()
        book_index = self.book_search_input.currentIndex()
        book_id = self.book_search_input.itemData(book_index)
        reservation_date = self.reservation_date_input.date().toString("yyyy-MM-dd")

        if not user_id_text or book_id == -1:
            QMessageBox.warning(self, "Input Error", "User ID and a valid book selection are required.")
            return

        try:
            user_id = int(user_id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "User ID must be a valid number.")
            return

        if database.add_reservation(user_id, book_id, reservation_date):
            QMessageBox.information(self, "Success", "Reservation created successfully.")
            self.reservation_added.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to create reservation. Please verify User ID and Book selection.")

class ReservationManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.create_reservation_screen = None
        self.setStyleSheet("background: #f4f5f7;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 32, 40, 32)
        main_layout.setSpacing(18)

        # Header
        header = QLabel("Reservation Management")
        header.setStyleSheet("font-size: 28px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36;")
        main_layout.addWidget(header)

        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search by book title or user...")
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #fff;
                border: 1.5px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 12px;
            }
        """)
        main_layout.addWidget(search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(5) # ID, Book Title, User, Reservation Date, Actions
        self.table.setHorizontalHeaderLabels(["ID", "Book Title", "User", "Reservation Date", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(54)
        self.table.setColumnHidden(0, True) # Hide ID column
        self.table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 16px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1.5px solid #e5e7eb;
                padding: 0px;
                alternate-background-color: #f9fafb;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 10px 8px;
            }
            QHeaderView::section {
                background: #f9fafb;
                color: #232b36;
                font-weight: 700;
                font-size: 16px;
                border: none;
                border-bottom: 1.5px solid #e5e7eb;
                padding: 16px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        main_layout.addWidget(self.table)
        self.load_reservations()

        # Create New Reservation button (bottom right)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        create_btn = QPushButton("Create New Reservation")
        create_btn.clicked.connect(self.show_create_reservation_screen)
        create_btn.setStyleSheet("background: #1976d2; color: #fff; font-size: 16px; font-weight: 700; border-radius: 24px; padding: 14px 36px; border: none; margin-top: 24px;")
        btn_row.addWidget(create_btn)
        main_layout.addLayout(btn_row)

    def load_reservations(self):
        reservations = database.get_all_reservations()
        self.table.setRowCount(len(reservations))

        for row, res_data in enumerate(reservations):
            res_id, book_title, username, res_date = res_data
            self.table.setItem(row, 0, QTableWidgetItem(str(res_id)))
            self.table.setItem(row, 1, QTableWidgetItem(book_title))
            self.table.setItem(row, 2, QTableWidgetItem(username))
            self.table.setItem(row, 3, QTableWidgetItem(res_date))

            # Actions button
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.setStyleSheet("background: #ef4444; color: #fff; font-size: 14px; font-weight: 600; border-radius: 8px; padding: 6px 16px; border: none;")
            cancel_btn.clicked.connect(lambda ch, r=row: self.handle_cancel_reservation(r))
            self.table.setCellWidget(row, 4, cancel_btn)

    def handle_cancel_reservation(self, row):
        res_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, 'Cancel Reservation', 'Are you sure you want to cancel this reservation?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if database.delete_reservation(res_id):
                QMessageBox.information(self, "Success", "Reservation canceled successfully.")
                self.load_reservations()
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel reservation.")

    def show_create_reservation_screen(self):
        self.create_reservation_screen = CreateReservationScreen()
        self.create_reservation_screen.reservation_added.connect(self.load_reservations)
        self.create_reservation_screen.showMaximized()