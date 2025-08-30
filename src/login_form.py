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
        """Handle the login button click event with improved error handling."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Disable UI during login attempt
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
            # Validate inputs
            if not username or not password:
                self._show_error("Input Required", "Please enter both username and password.")
                return
            
            try:
                with self.db._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # First check if the username exists
                    cursor.execute(
                        "SELECT id, username, password_hash, status, full_name, role "
                        "FROM users WHERE username = ?", 
                        (username,)
                    )
                    user = cursor.fetchone()
                    
                    if not user:
                        self._show_error(
                            "Login Failed",
                            "Username not found. Please check your username and try again.",
                            focus_widget=self.username_input,
                            select_text=True
                        )
                        return
                    
                    # Check if account is active
                    if user['status'] != 'active':
                        self._show_error(
                            "Account Inactive",
                            "This account is currently inactive.\n\n"
                            "Please contact the administrator for assistance.",
                            focus_widget=self.username_input,
                            clear_password=True
                        )
                        return
                    
                    # Verify password
                    from auth_utils import verify_password
                    if not verify_password(password, user['password_hash']):
                        self._show_error(
                            "Login Failed",
                            "Incorrect password. Please try again.",
                            focus_widget=self.password_input,
                            select_text=True
                        )
                        return
                    
                    # Login successful - redirect to dashboard
                    self.show_dashboard(user)
                    
            except Exception as e:
                self._show_error(
                    "Connection Error",
                    "Unable to connect to the database.\n\n"
                    "Please check your internet connection and try again.",
                    is_critical=True
                )
                print(f"Database error: {str(e)}")  # Log the actual error for debugging
                
        finally:
            # Re-enable UI
            self.setEnabled(True)
            QApplication.restoreOverrideCursor()
    
    def _show_error(self, title, message, focus_widget=None, select_text=False, 
                   clear_password=False, is_critical=False):
        """Helper method to display error messages consistently."""
        if is_critical:
            QMessageBox.critical(self, title, message, QMessageBox.Ok)
        else:
            QMessageBox.warning(self, title, message, QMessageBox.Ok)
        
        # Set focus to the specified widget
        if focus_widget:
            focus_widget.setFocus()
            if select_text:
                focus_widget.selectAll()
        
        # Clear password field if needed
        if clear_password:
            self.password_input.clear()
    
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
