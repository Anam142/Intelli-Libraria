import database
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QDialog, QFormLayout, QFrame, QHBoxLayout, 
                            QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, 
                            QScrollArea, QTableWidget, QTableWidgetItem, QTextEdit, 
                            QVBoxLayout, QWidget)


class UserDialog(QDialog):
    user_changed = pyqtSignal()

    def __init__(self, user_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle(f"{'Edit' if user_id else 'Add New'} User")
        self.setModal(True)
        self.setStyleSheet("background: #f4f5f7;")
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.showMaximized()
        self.init_ui()
        if self.user_id:
            self.load_user_data()
        else:
            self.generate_user_id()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(18)

        heading = QLabel(f"{'Edit' if self.user_id else 'Add New'} User")
        heading.setStyleSheet("font-size: 28px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36;")
        layout.addWidget(heading, alignment=Qt.AlignLeft)

        # Create a scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        # Container for the form
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(18)

        # User ID field (read-only)
        user_id_container = QVBoxLayout()
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36;")
        
        self.user_id_field = QLineEdit()
        self.user_id_field.setPlaceholderText("Enter User ID")
        self.user_id_field.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 10px;
                padding: 12px 16px;
                color: #1a1a1a;
                font-size: 15px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4f46e5;
                outline: none;
            }
        """)
        
        user_id_container.addWidget(user_id_label)
        user_id_container.addWidget(self.user_id_field)
        form_layout.addLayout(user_id_container)

        # Form fields
        fields = {
            "Full Name": ("Enter full name", QLineEdit),
            "Email Address": ("Enter email address", QLineEdit),
            "Contact Number": ("Enter contact number", QLineEdit),
            "Address": ("Enter address", QTextEdit),
        }

        self.inputs = {}
        for label_text, (placeholder, widget_type) in fields.items():
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36;")
            form_layout.addWidget(label)

            input_widget = widget_type()
            input_widget.setPlaceholderText(placeholder)
            input_widget.setStyleSheet("""
                background: #fff;
                border-radius: 10px;
                border: 1.5px solid #e5e7eb;
                padding: 12px 16px;
                font-size: 15px;
                min-height: 40px;
            """)
            if isinstance(input_widget, QTextEdit):
                input_widget.setFixedHeight(120)
            form_layout.addWidget(input_widget)
            self.inputs[label_text] = input_widget

        # Role and Status combo boxes
        self.role_input = self.add_combo_box(form_layout, "Role", ["Admin", "Librarian", "Member"])
        self.status_input = self.add_combo_box(form_layout, "Status", ["Active", "Inactive", "Suspended"])

        form_layout.addStretch(1)
        
        # Set the scroll area's widget
        scroll.setWidget(form_container)
        layout.addWidget(scroll, 1)  # Add stretch to take remaining space

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background: #f3f4f6; color: #232b36; font-size: 15px; font-weight: 600; border-radius: 12px; padding: 8px 24px; border: none;")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Changes" if self.user_id else "Add User")
        save_btn.setStyleSheet("background: #1976d2; color: #fff; font-size: 15px; font-weight: 700; border-radius: 12px; padding: 8px 24px; border: none;")
        save_btn.clicked.connect(self.save_user)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def add_combo_box(self, layout, label_text, items):
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36;")
        layout.addWidget(label)
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setStyleSheet("background: #fff; border-radius: 10px; border: 1.5px solid #e5e7eb; padding: 12px 16px; font-size: 15px;")
        layout.addWidget(combo_box)
        return combo_box

    def generate_user_id(self):
        """Generate a new user ID in the format USR-XXXXXX"""
        import random
        import string
        # Generate a random 6-digit number
        random_digits = ''.join(random.choices(string.digits, k=6))
        user_id = f"USR-{random_digits}"
        # Set the generated ID in the User ID field
        if hasattr(self, 'user_id_field') and self.user_id_field:
            self.user_id_field.setText(user_id)
        return user_id

    def load_user_data(self):
        user = database.get_user_by_id(self.user_id)
        if user:
            user_id, name, email, role, status, contact, address = user
            # Set the existing user ID
            if hasattr(self, 'user_id_field') and self.user_id_field:
                self.user_id_field.setText(str(user_id))
            self.inputs["Full Name"].setText(name)
            self.inputs["Email Address"].setText(email)
            self.inputs["Contact Number"].setText(contact or "")
            self.inputs["Address"].setPlainText(address or "")
            if self.user_id:
                self.role_input.setCurrentText(role)
                self.status_input.setCurrentText(status)

    def save_user(self):
        name = self.inputs["Full Name"].text().strip()
        email = self.inputs["Email Address"].text().strip()
        contact = self.inputs["Contact Number"].text().strip()
        address = self.inputs["Address"].toPlainText().strip()
        
        role = self.role_input.currentText() if self.user_id else 'Member'
        status = self.status_input.currentText() if self.user_id else 'Active'

        if not name or not email:
            QMessageBox.warning(self, "Input Error", "Name and email cannot be empty.")
            return

        if self.user_id:
            if database.update_user(self.user_id, name, email, role, status, contact, address):
                QMessageBox.information(self, "Success", "User updated successfully.")
                self.user_changed.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update user.")
        else:
            # For new users, a default password is used as the form doesn't include a password field.
            # The role and status parameters are now correctly ordered
            if database.add_user(name, email, role, status, contact, address):
                QMessageBox.information(self, "Success", "User added successfully.")
                self.user_changed.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to add user.")


class UserManagementPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.user_dialog = None  # Add this line to store a reference
        self.setStyleSheet("background-color: #ffffff;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)

        # Search Bar
        search_layout = self.create_search_bar()
        main_layout.addLayout(search_layout)

        # User Table
        self.table = self.create_table()
        main_layout.addWidget(self.table)
        self.load_users()


    def create_header(self):
        header_layout = QHBoxLayout()
        title = QLabel("User Management")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_user_btn = QPushButton("Add User")
        add_user_btn.setFont(QFont("Arial", 12))
        add_user_btn.setCursor(Qt.PointingHandCursor)
        
        # Set button styles
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: 1px solid #4338ca;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        add_user_btn.clicked.connect(self.open_add_user_dialog)
        header_layout.addWidget(add_user_btn)
        return header_layout

    def create_search_bar(self):
        search_layout = QHBoxLayout()
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0; 
                border-radius: 5px; 
                background-color: #ffffff; 
            }
        """)
        search_frame_layout = QHBoxLayout(search_frame)
        search_frame_layout.setContentsMargins(10, 5, 10, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name, User ID, Email, Role")
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setStyleSheet("border: none; background-color: transparent;")
        self.search_input.textChanged.connect(self.load_users)
        search_frame_layout.addWidget(self.search_input)
        search_layout.addWidget(search_frame)
        return search_layout

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["User ID", "Full Name", "Email", "Role", "Status", "Actions"])
        # Configure table properties
        table.setColumnWidth(0, 100)  # User ID
        table.setColumnWidth(1, 200)  # Full Name
        table.setColumnWidth(2, 250)  # Email
        table.setColumnWidth(3, 100)  # Role
        table.setColumnWidth(4, 100)  # Status
        table.setColumnWidth(5, 200)  # Increased width for Actions column
        
        # Set row height and other table properties
        table.verticalHeader().setDefaultSectionSize(60)  # Increased row height
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Only make name column stretchable
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(False)
        table.setFont(QFont("Inter", 10))
        
        # Make header text bold
        header = table.horizontalHeader()
        header_font = header.font()
        header_font.setBold(True)
        header_font.setPointSize(11)  # Slightly larger font for headers
        header.setFont(header_font)
        
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                outline: none;
                gridline-color: #f0f2f5;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 700;
                font-size: 12px;
                color: #334155;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                text-align: left;
                margin: 0;
            }
            QHeaderView::section:first {
                padding-left: 20px;  /* Add more left padding to first column */
            }
            QTableWidget::item {
                padding: 16px 20px;
                border-bottom: 1px solid #f1f5f9;
                color: #334155;
                min-height: 60px;
                margin: 0 8px;  /* Add horizontal margin */
            }
            QTableWidget::item:selected {
                background-color: #f1f5ff;
                color: #1e40af;
            }
            QTableWidget::item:hover {
                background-color: #f8fafc;
            }
            QScrollBar:vertical {
                border: none;
                background: #ffffff;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        return table

    def load_users(self):
        search_term = self.search_input.text().lower()
        users = database.get_all_users()
        
        if search_term:
            filtered_users = [
                u for u in users if (search_term in str(u[0]).lower() or 
                                    search_term in u[1].lower() or 
                                    search_term in u[2].lower() or 
                                    search_term in u[3].lower())
            ]
        else:
            filtered_users = users

        # Set alternating row colors
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8fafc;
                selection-background-color: #e0f2fe;
                selection-color: #0369a1;
                gridline-color: #f1f5f9;
            }
        """)
        
        # Disable sorting while updating
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered_users))
        
        # Populate table with user data
        for i, user in enumerate(filtered_users):
            self.populate_table_row(i, user)
            
        # Re-enable sorting
        self.table.setSortingEnabled(True)
        
        # Sort by first column (User ID) by default
        self.table.sortByColumn(0, Qt.AscendingOrder)

    def populate_table_row(self, row, user):
        user_id, name, email, role, status, contact, address = user
        
        # Set row height
        self.table.setRowHeight(row, 60)  # Explicitly set row height
        
        # Create and set items with proper alignment and margins
        for col, (text, alignment) in enumerate([
            (str(user_id), Qt.AlignVCenter | Qt.AlignLeft),  # User ID
            (name, Qt.AlignVCenter | Qt.AlignLeft),          # Name
            (email, Qt.AlignVCenter | Qt.AlignLeft)          # Email
        ]):
            item = QTableWidgetItem(text)
            item.setTextAlignment(alignment)
            item.setData(Qt.UserRole, text)  # Store original text for sorting
            self.table.setItem(row, col, item)
            
        # Add widgets to cells
        self.table.setCellWidget(row, 3, self.create_role_widget(role))
        self.table.setCellWidget(row, 4, self.create_status_widget(status))
        self.table.setCellWidget(row, 5, self.create_actions_widget(user_id))

    def create_role_widget(self, role):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setAlignment(Qt.AlignCenter)
        
        role_label = QLabel(role.title())
        role_label.setFont(QFont("Inter", 10, QFont.Medium))
        
        # Enhanced role styling with better visual hierarchy
        if role.lower() == 'admin':
            style = """
                background-color: #e0f2fe;
                color: #0369a1;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: 500;
                border: 1px solid #bae6fd;
            """
        else:  # member
            style = """
                background-color: #f1f5f9;
                color: #475569;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: 500;
                border: 1px solid #e2e8f0;
            """
            
        role_label.setStyleSheet(style)
        layout.addWidget(role_label)
        return widget

    def create_status_widget(self, status):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setAlignment(Qt.AlignCenter)
        
        status_label = QLabel(status)
        status_label.setFont(QFont("Inter", 10, QFont.Medium))
        
        # Enhanced status styling with better visual indicators
        if status.lower() == 'active':
            bg_color = '#dcfce7'
            text_color = '#166534'
            border_color = '#86efac'
        else:
            bg_color = '#fee2e2'
            text_color = '#991b1b'
            border_color = '#fca5a5'
            
        style = f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 6px;
            padding: 4px 12px;
            font-weight: 500;
            border: 1px solid {border_color};
        """
        status_label.setStyleSheet(style)
        layout.addWidget(status_label)
        return widget

    def create_actions_widget(self, user_id):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        layout.setSpacing(6)  # Reduced spacing between buttons
        layout.setAlignment(Qt.AlignCenter)
        
        # Edit button with hover effect - enhanced visibility
        edit_btn = QPushButton("Edit")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                color: #1e40af;
                background-color: #dbeafe;
                border: 1px solid #93c5fd;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 13px;
                min-width: 70px;
                max-width: 70px;
                margin: 0 2px;
            }
            QPushButton:hover {
                background-color: #bfdbfe;
                border-color: #60a5fa;
            }
            QPushButton:pressed {
                background-color: #93c5fd;
            }
        """)
        edit_btn.clicked.connect(lambda: self.open_edit_user_dialog(user_id))
        
        # Delete button with hover effect - enhanced visibility
        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                color: #991b1b;
                background-color: #fee2e2;
                border: 1px solid #fecaca;
                border-radius: 12px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 13px;
                min-width: 70px;
                max-width: 70px;
                margin: 0 2px;
            }
            QPushButton:hover {
                background-color: #fecaca;
                border-color: #fca5a5;
            }
            QPushButton:pressed {
                background-color: #fca5a5;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_user(user_id))
        
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        return widget

    def open_add_user_dialog(self):
        self.user_dialog = UserDialog(parent=self)
        self.user_dialog.user_changed.connect(self.load_users)
        self.user_dialog.show()

    def open_edit_user_dialog(self, user_id):
        self.user_dialog = UserDialog(user_id=user_id, parent=self)
        self.user_dialog.user_changed.connect(self.load_users)
        self.user_dialog.show()

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, 'Delete User', 
                                     'Are you sure you want to delete this user?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if database.delete_user(user_id):
                QMessageBox.information(self, "Success", "User deleted successfully.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete user.")