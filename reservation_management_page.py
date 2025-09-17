from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QComboBox, QDateEdit, QMessageBox
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
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

        # Basic validation
        if not user_id_text or book_id == -1:
            QMessageBox.warning(self, "Input Error", "User ID and a valid book selection are required.")
            return

        try:
            user_id = int(user_id_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "User ID must be a valid number.")
            return

        # Disable UI during operation
        self.setEnabled(False)
        
        try:
            # This will be fast due to our optimized database function
            success, message = database.add_reservation(user_id, book_id, reservation_date)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.reservation_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Reservation Failed", message)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")
        finally:
            # Re-enable UI
            self.setEnabled(True)

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
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by book title or user...")
        self.search_bar.textChanged.connect(self.filter_reservations)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #fff;
                border: 1.5px solid #e5e7eb;
                border-radius: 20px;
                padding: 12px 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #1976d2;
                outline: none;
            }
        """)
        main_layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(5) # ID, Book Title, User, Reservation Date, Actions
        self.all_reservations = []  # Store all reservations for filtering
        self.table.setHorizontalHeaderLabels(["ID", "Book Title", "User", "Reservation Date", "Actions"])
        
        # Set column resize modes - let first 3 columns stretch, last column fixed width
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Book Title
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # User
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        
        # Set minimum width for the actions column to prevent cutting off buttons
        header.setMinimumSectionSize(240)  # Increased to accommodate better button spacing
        self.table.setColumnWidth(4, 240)  # Increased fixed width for actions column
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(70)  # Increased row height to prevent button cut-off
        self.table.setColumnHidden(0, True) # Hide ID column
        self.table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1.5px solid #e5e7eb;
                padding: 0px;
                alternate-background-color: #f9fafb;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 6px 8px 8px 8px;
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
            QTableWidget QPushButton {
                border-radius: 16px;
                min-width: 75px;
                min-height: 32px;
                padding: 4px 12px;
                font-size: 13px;
                font-weight: 600;
                margin: 4px 6px;
                border: none;
                background-color: #1976d2;
                color: white;
            }
            QTableWidget QPushButton:hover {
                background-color: #1565c0;
            }
            QTableWidget QPushButton:pressed {
                background-color: #0d47a1;
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
        self.all_reservations = database.get_all_reservations()
        self.filter_reservations()

    def filter_reservations(self):
        """Filter reservations based on search text in book title or username"""
        search_text = self.search_bar.text().lower().strip()

        def _normalize(res):
            # Convert dict rows (from database.get_all_reservations) or tuples into a unified 4-tuple
            try:
                if isinstance(res, dict):
                    return (
                        res.get('reservation_id') or res.get('id'),
                        res.get('book_title', ''),
                        res.get('user_name', ''),
                        str(res.get('reservation_date', ''))
                    )
                # tuple/list fallback: assume order (res_id, book_title, username, res_date, ...)
                return (res[0], res[1], res[2], res[3])
            except Exception:
                return (None, '', '', '')

        normalized = [_normalize(r) for r in (self.all_reservations or [])]

        if not search_text:
            filtered_reservations = normalized
        else:
            filtered_reservations = [
                r for r in normalized
                if (search_text in str(r[1]).lower() or  # Book title
                    search_text in str(r[2]).lower())     # Username
            ]

        # Update the table with filtered results
        self.table.setRowCount(len(filtered_reservations))
        for row, res_data in enumerate(filtered_reservations):
            res_id, book_title, username, res_date = res_data
            self.table.setItem(row, 0, QTableWidgetItem(str(res_id)))
            self.table.setItem(row, 1, QTableWidgetItem(book_title))
            self.table.setItem(row, 2, QTableWidgetItem(username))
            self.table.setItem(row, 3, QTableWidgetItem(res_date))

            # Recreate actions widget for each row
            self._add_action_buttons(row, res_id)

    def _add_action_buttons(self, row, res_id):
        """Helper method to add action buttons to a table row"""
        actions_widget = QWidget()
        actions_widget.setStyleSheet("""
            QWidget {
                background: transparent;
                margin: 2px 0;
                border: none;
                border-radius: 0;
            }
        """)
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 0, 4, 0)  # Reduced side margins
        actions_layout.setSpacing(2)  # Minimal spacing between buttons

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setToolTip("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #1976d2;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 12px;
                min-width: 75px;
                min-height: 32px;
                font-size: 13px;
                font-weight: 600;
                margin-right: 2px;
            }
            QPushButton:hover {
                background: #1565c0;
            }
            QPushButton:pressed {
                background: #0d47a1;
            }
        """)
        edit_btn.clicked.connect(lambda checked, r=row: self.handle_edit_reservation(r))

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setToolTip("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #d32f2f;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 12px;
                min-width: 75px;
                min-height: 32px;
                font-size: 13px;
                font-weight: 600;
                margin-left: 2px;
            }
            QPushButton:hover {
                background: #b71c1c;
            }
            QPushButton:pressed {
                background: #7f0000;
            }
        """)
        delete_btn.clicked.connect(lambda checked, r=row: self.handle_delete_reservation(r))

        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 4, actions_widget)

    def handle_edit_reservation(self, row):
        """Handle edit reservation button click by opening the CreateReservationScreen in edit mode"""
        res_id = self.table.item(row, 0).text()
        book_title = self.table.item(row, 1).text()
        username = self.table.item(row, 2).text()
        res_date = self.table.item(row, 3).text()
        
        # Open the create reservation screen in edit mode
        self.create_reservation_screen = CreateReservationScreen()
        self.create_reservation_screen.setWindowTitle("Edit Reservation")
        
        # Find the book ID from the title
        book_id = None
        for i in range(self.create_reservation_screen.book_search_input.count()):
            if self.create_reservation_screen.book_search_input.itemText(i) == book_title:
                book_id = self.create_reservation_screen.book_search_input.itemData(i)
                break
        
        # Set the fields with the reservation data
        if book_id is not None:
            self.create_reservation_screen.book_search_input.setCurrentIndex(i)
            
        # Set user ID and date
        if username.isdigit():  # If username is actually a user ID
            self.create_reservation_screen.user_id_input.setText(username)
        
        try:
            self.create_reservation_screen.reservation_date_input.setDate(QDate.fromString(res_date, "yyyy-MM-dd"))
        except:
            # If date format is different, just use current date as fallback
            self.create_reservation_screen.reservation_date_input.setDate(QDate.currentDate())
        
        # Connect the save signal to refresh the table
        self.create_reservation_screen.reservation_added.connect(self.load_reservations)
        
        # Show the screen
        self.create_reservation_screen.showMaximized()

    def handle_delete_reservation(self, row):
        res_id = self.table.item(row, 0).text()
        book_title = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            'Delete Reservation', 
            f'Are you sure you want to delete the reservation for "{book_title}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if database.delete_reservation(res_id):
                QMessageBox.information(self, "Success", "Reservation deleted successfully.")
                self.load_reservations()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete reservation.")

    def show_create_reservation_screen(self):
        self.create_reservation_screen = CreateReservationScreen()
        self.create_reservation_screen.reservation_added.connect(self.load_reservations)
        self.create_reservation_screen.showMaximized()