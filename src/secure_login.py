import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from db_utils import DatabaseManager

class LoginWindow(QMainWindow):
    """Secure login window with database authentication."""
    login_successful = pyqtSignal(dict)  # Signal emitted with user data on successful login
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Intelli Libraria - Login")
        self.setWindowIcon(QIcon("icons/icon.png"))
        self.setMinimumSize(400, 500)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Logo and title
        title = QLabel("Intelli Libraria")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        
        subtitle = QLabel("Library Management System")
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(40)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        
        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.toggled.connect(self.toggle_password_visibility)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        
        # Add widgets to layout
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        
        form_layout.addWidget(QLabel("Username"))
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(QLabel("Password"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.show_password)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_btn)
        
        layout.addLayout(form_layout)
        layout.addStretch(1)
        
        # Set focus to username field
        self.username_input.setFocus()
        
        # Connect return pressed event
        self.password_input.returnPressed.connect(self.handle_login)
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility."""
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        # Verify credentials
        user = self.db.verify_user(username, password)
        
        if user:
            self.login_successful.emit(dict(user))
            self.close()
        else:
            QMessageBox.warning(
                self, 
                "Login Failed",
                "Invalid username or password. Please try again.",
                QMessageBox.Ok
            )
            self.password_input.clear()
            self.password_input.setFocus()


class DashboardWindow(QMainWindow):
    """Main dashboard window shown after successful login."""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dashboard UI."""
        self.setWindowTitle(f"Intelli Libraria - Welcome {self.user_data['full_name']}")
        self.setMinimumSize(1024, 768)
        
        # Add your dashboard widgets here
        welcome_label = QLabel(f"Welcome, {self.user_data['full_name']} ({self.user_data['role']})")
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # Set the central widget
        self.setCentralWidget(welcome_label)


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show login window
    login_window = LoginWindow()
    login_window.show()
    
    def on_login_success(user_data):
        """Handle successful login by showing the dashboard."""
        dashboard = DashboardWindow(user_data)
        dashboard.show()
    
    # Connect login signal
    login_window.login_successful.connect(on_login_success)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Create default admin user if not exists
    db = DatabaseManager()
    db.create_admin_user()
    
    # Run the application
    main()
