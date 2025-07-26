from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from database import add_user, get_all_users

class AddUserDialog(QDialog):
    user_added = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
        """)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Add New User")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(title_label)

        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # User ID
        self.user_id_field = self.create_form_field("User ID", "Auto-generated", disabled=True)
        form_layout.addLayout(self.user_id_field['layout'])

        # Full Name
        self.full_name_field = self.create_form_field("Full Name", "Enter full name")
        form_layout.addLayout(self.full_name_field['layout'])

        # Email Address
        self.email_field = self.create_form_field("Email Address", "Enter email address")
        form_layout.addLayout(self.email_field['layout'])

        # Contact Number
        self.contact_field = self.create_form_field("Contact Number (Optional)", "Enter contact number")
        form_layout.addLayout(self.contact_field['layout'])

        # Address
        self.address_field = self.create_form_field("Address (Optional)", "Enter address", is_text_edit=True)
        form_layout.addLayout(self.address_field['layout'])

        main_layout.addLayout(form_layout)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignRight)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(QFont("Segoe UI", 10))
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #bdc3c7; }
        """)
        self.cancel_button.clicked.connect(self.reject)

        self.add_user_button = QPushButton("Add User")
        self.add_user_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.add_user_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.add_user_button.clicked.connect(self.accept_user)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_user_button)
        main_layout.addLayout(button_layout)

    def create_form_field(self, label_text, placeholder, disabled=False, is_text_edit=False):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        label.setStyleSheet("color: #34495e;")
        layout.addWidget(label)

        if is_text_edit:
            field = QTextEdit()
            field.setPlaceholderText(placeholder)
            field.setMinimumHeight(80)
        else:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setDisabled(disabled)
        
        field.setFont(QFont("Segoe UI", 10))
        field.setStyleSheet("""
            QLineEdit, QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QLineEdit:disabled {
                background-color: #f4f6f7;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(field)
        return {"layout": layout, "field": field}

    def accept_user(self):
        full_name = self.full_name_field['field'].text().strip()
        email = self.email_field['field'].text().strip()
        contact = self.contact_field['field'].text().strip()
        address = self.address_field['field'].toPlainText().strip()

        if not full_name or not email:
            # Basic validation
            return

        # Default role and status for new users
        add_user(full_name, email, 'Member', 'Active', contact, address)
        self.user_added.emit()
        self.accept()
