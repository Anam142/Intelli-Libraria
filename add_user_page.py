import database
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget
)

class AddUserPage(QWidget):
    """A full-screen page for adding a new user."""

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            background-color: #ffffff;
            color: #333;
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignTop)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Add New User")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Form
        form_widget = QWidget()
        form_widget.setMaximumWidth(600)
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        # Styling for labels and inputs
        label_style = "font-size: 16px; font-weight: bold;"
        input_style = """
            padding: 12px;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            font-size: 14px;
        """

        self.user_id_input = QLineEdit("Auto-generated")
        self.user_id_input.setReadOnly(True)
        self.user_id_input.setStyleSheet(input_style + "background-color: #f0f0f0;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        self.name_input.setStyleSheet(input_style)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        self.email_input.setStyleSheet(input_style)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter contact number")
        self.contact_input.setStyleSheet(input_style)

        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter address")
        self.address_input.setStyleSheet(input_style)
        self.address_input.setFixedHeight(120)

        # Add rows to form
        name_label = QLabel("Full Name")
        name_label.setStyleSheet(label_style)
        email_label = QLabel("Email Address")
        email_label.setStyleSheet(label_style)
        contact_label = QLabel("Contact Number (Optional)")
        contact_label.setStyleSheet(label_style)
        address_label = QLabel("Address (Optional)")
        address_label.setStyleSheet(label_style)

        form_layout.addRow(name_label, self.name_input)
        form_layout.addRow(email_label, self.email_input)
        form_layout.addRow(contact_label, self.contact_input)
        form_layout.addRow(address_label, self.address_input)

        main_layout.addWidget(form_widget)
        main_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumSize(120, 45)
        self.cancel_btn.setStyleSheet("""
            background-color: #f0f0f0; 
            color: #333; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 5px;
        """)
        self.cancel_btn.clicked.connect(self.cancel_action)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Add User")
        self.save_btn.setMinimumSize(120, 45)
        self.save_btn.setStyleSheet("""
            background-color: #007bff; 
            color: white; 
            font-size: 16px; 
            font-weight: bold; 
            border-radius: 5px;
        """)
        self.save_btn.clicked.connect(self.save_user)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

    def save_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()
        address = self.address_input.toPlainText().strip()
        role = 'Member'  # Default role
        status = 'Active' # Default status

        if not name or not email:
            QMessageBox.warning(self, "Input Error", "Name and email cannot be empty.")
            return

        if database.add_user(name, email, role, status, contact, address):
            QMessageBox.information(self, "Success", "User added successfully.")
            self.clear_form()
            if self.main_window:
                self.main_window.show_user_management()
        else:
            QMessageBox.warning(self, "Error", "Failed to add user. Email may already exist.")

    def cancel_action(self):
        if self.main_window:
            self.main_window.show_user_management()

    def clear_form(self):
        self.name_input.clear()
        self.email_input.clear()
        self.contact_input.clear()
        self.address_input.clear()

# To run as a standalone app for testing:
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = AddUserPage()
    win.show()
    sys.exit(app.exec_())
