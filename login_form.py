import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from db_utils import DatabaseManager

class LoginForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria - Login")
        self.setFixedSize(400, 300)
        
        # Initialize database connection
        self.db = DatabaseManager()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create form layout
        self.form_layout = QFormLayout()
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.form_layout.addRow("Username:", self.username_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.form_layout.addRow("Password:", self.password_input)
        
        # Add form to main layout
        self.layout.addLayout(self.form_layout)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.layout.addWidget(self.login_button)
        
        # Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Set focus to username field by default
        self.username_input.setFocus()
    
    def handle_login(self):
        """Handle the login button click event."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                # First check if the username exists
                cursor.execute("SELECT id, username, password_hash, status FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                
                if not user:
                    QMessageBox.warning(
                        self,
                        "Login Failed",
                        "Username not found. Please check your username and try again.",
                        QMessageBox.Ok
                    )
                    self.username_input.selectAll()
                    self.username_input.setFocus()
                    return
                
                # Check if account is active
                if user['status'] != 'active':
                    QMessageBox.warning(
                        self,
                        "Account Inactive",
                        "This account is currently inactive. Please contact the administrator.",
                        QMessageBox.Ok
                    )
                    self.username_input.selectAll()
                    self.password_input.clear()
                    self.username_input.setFocus()
                    return
                
                # Verify password
                from auth_utils import verify_password
                if not verify_password(password, user['password_hash']):
                    QMessageBox.warning(
                        self,
                        "Login Failed",
                        "Incorrect password. Please try again.",
                        QMessageBox.Ok
                    )
                    self.password_input.selectAll()
                    self.password_input.setFocus()
                    return
                
                # Login successful - redirect to dashboard
                self.show_dashboard(user)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def show_dashboard(self, user):
        """Show the dashboard window."""
        # Import here to avoid circular imports
        from dashboard_window import DashboardWindow
        
        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Show the login form
    login = LoginForm()
    login.show()
    
    sys.exit(app.exec_())
