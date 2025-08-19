import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QStackedWidget,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QPainter
from PyQt5.QtCore import Qt, pyqtSignal
from signup_page_clean import SignupPage

class BackgroundWidget(QWidget):
    """A widget that draws a scaled background image."""
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)

    def resizeEvent(self, event):
        """Handle window resize events to update the background."""
        self.update()
        super().resizeEvent(event)
        
    def paintEvent(self, event):
        """Paints the background image, scaled to cover the entire widget."""
        if not self.pixmap.isNull():
            # Get the current window size
            window_size = self.size()
            # Calculate the scaled size that covers the window while maintaining aspect ratio
            scaled_pixmap = self.pixmap.scaled(
                window_size, 
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            # Calculate the position to center the pixmap
            x = (scaled_pixmap.width() - window_size.width()) // 2
            y = (scaled_pixmap.height() - window_size.height()) // 2
            
            # Create a painter and draw the pixmap
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            painter.drawPixmap(0, 0, scaled_pixmap, x, y, window_size.width(), window_size.height())
            painter.end()
            
        super().paintEvent(event)

class LoginWindow(QMainWindow):
    """The main login window, combining the background and the login form."""
    login_successful = pyqtSignal()
    
    def __init__(self, bg_image_path):
        super().__init__()
        self.setWindowTitle("Intelli Libraria _ Login")
        
        # Enable high DPI scaling
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window flags for standard window controls
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                     Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                  Qt.WindowCloseButtonHint)
        
        # Get the screen geometry
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Set window size to 90% of screen size, but not smaller than minimum
        min_width = 1200
        min_height = 800
        width = max(min_width, int(screen.width() * 0.9))
        height = max(min_height, int(screen.height() * 0.9))
        
        # Center the window
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        
        # Set window geometry
        self.setGeometry(x, y, width, height)
        
        # Show the window
        self.show()

        # Set up the background
        self.background = BackgroundWidget(bg_image_path, self)
        self.setCentralWidget(self.background)
        
        # Create main layout for the background
        main_layout = QVBoxLayout(self.background)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add vertical stretch to push content to middle
        main_layout.addStretch()
        
        # Create a horizontal container for the form
        form_container = QWidget()
        h_layout = QHBoxLayout(form_container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add horizontal stretches to center the form
        h_layout.addStretch()
        
        # Create the stacked widget for login/signup
        self.stacked_widget = QStackedWidget()
        
        # Create the login card
        self.login_card = QWidget()
        self.setup_login_card()
        self.stacked_widget.addWidget(self.login_card)
        
        # Add stacked widget to horizontal layout
        h_layout.addWidget(self.stacked_widget)
        h_layout.addStretch()
        
        # Add form container to main layout
        main_layout.addWidget(form_container)
        
        # Add bottom vertical stretch
        main_layout.addStretch()
        
        # Create the signup page
        self.signup_page = SignupPage(self)
        self.stacked_widget.addWidget(self.signup_page)
        self.center_window()

    def setup_login_card(self):
        """Sets up the widgets and styling for the login form card."""
        self.login_card.setStyleSheet("""
            QWidget#login_card {
                background: rgba(255, 255, 255, 0.95); /* Semi-transparent white */
                border-radius: 24px;  /* More rounded corners */
                padding: 20px;
            }
            QLabel#title_container {
                background: white;
                border: 1px solid #2c3e50;  /* Dark border */
                border-radius: 50px;  /* Pill shape */
                padding: 8px 24px;
                margin-bottom: 20px;
                max-width: 200px;
                margin-left: auto;
                margin-right: auto;
            }
            QLabel#title_label {
                font-family: Arial;
                font-size: 22px;  /* Increased from 18px */
                font-weight: 700;  /* Made bolder (700 is bold) */
                color: #2c3e50; /* Dark text */
                text-align: center;
            }
            QLineEdit {
                padding: 14px;
                border: 1px solid #d1d5db; /* Light gray border */
                border-radius: 8px;  /* More rounded corners */
                font-size: 14px;
                margin-bottom: 12px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6; /* Richer blue when focused */
                outline: none;
            }
            QPushButton#login_button {
                background-color: #2563eb; /* Richer blue */
                color: white;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;  /* More rounded corners */
                border: none;
                padding: 14px;
                margin-top: 10px;
            }
            QPushButton#login_button:hover {
                background-color: #1d4ed8; /* Darker blue */
            }
            QPushButton#signup_button {
                background-color: #10b981; /* Richer green */
                color: white;
                font-size: 16px;
                font-weight: 600;
                border-radius: 8px;  /* More rounded corners */
                border: none;
                padding: 14px;
                margin-top: 8px;
            }
            QPushButton#signup_button:hover {
                background-color: #059669; /* Darker green */
            }
            QPushButton#forgot_button {
                background: transparent;
                border: none;
                color: #3b82f6; /* Richer blue link color */
                font-size: 13px;
                text-decoration: none;
                margin-top: 5px;
            }
            QPushButton#forgot_button:hover {
                text-decoration: underline;
            }
        """)

        self.login_card.setObjectName("login_card")
        # Set fixed size for the login card
        self.login_card.setFixedSize(480, 520)
        
        # --- Layout for the card ---
        card_layout = QVBoxLayout(self.login_card)
        # Reduced bottom margin to make it more compact
        card_layout.setContentsMargins(40, 40, 40, 30)
        card_layout.setSpacing(15)
        card_layout.setAlignment(Qt.AlignCenter)

        # Title container with pill shape
        title_container = QWidget()
        title_container.setObjectName("title_container")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title text (in title case)
        title = QLabel("Admin Login")
        title.setObjectName("title_label")
        title_layout.addWidget(title, 0, Qt.AlignCenter)
        
        card_layout.addWidget(title_container)
        
        card_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        card_layout.addWidget(self.username)

        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.password)
        
        card_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("login_button")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        # Signup button
        self.signup_button = QPushButton("Signup")
        self.signup_button.setObjectName("signup_button")
        self.signup_button.setCursor(Qt.PointingHandCursor)
        self.signup_button.clicked.connect(self.show_signup_page)
        card_layout.addWidget(self.signup_button)
        
        # Forgot Password button
        self.forgot_button = QPushButton("Forgot Password?")
        self.forgot_button.setObjectName("forgot_button")
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(self.forgot_button, alignment=Qt.AlignCenter)
        
        # Removed the extra stretch that was adding space at the bottom

    def handle_login(self):
        """Handle login button click."""
        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        # Check credentials against database
        if self.verify_credentials(username, password):
            self.login_successful.emit()  # Emit signal on successful login
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")
    
    def verify_credentials(self, username, password):
        """Verify user credentials against the database (case-insensitive)."""
        import sqlite3
        try:
            conn = sqlite3.connect("intelli_libraria.db")
            cursor = conn.cursor()
            
            # First, check if user exists (case-insensitive)
            cursor.execute("SELECT id, username, password FROM users WHERE LOWER(username) = LOWER(?)", (username,))
            user = cursor.fetchone()
            
            if user is None:
                print(f"No user found with username: {username}")
                return False
                
            # Get the stored username and password
            user_id = user[0]
            actual_username = user[1]  # Get the actual username from the database
            stored_password = user[2] if len(user) > 2 else '1234'  # Default to '1234' if password is None
            
            # Debug output
            print(f"Login attempt - Username: {username}")
            print(f"Actual username in DB: {actual_username}")
            print(f"Stored password: {stored_password}")
            print(f"Provided password: {password}")
            
            # Check if password matches (case-sensitive for password)
            if password == stored_password:
                print("Login successful!")
                return True
                
            # Also check against default password '1234' for backward compatibility
            if password == '1234' and stored_password == '1234':
                print("Login successful with default password!")
                return True
                
            print("Incorrect password")
            return False
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
            print(f"Database error: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def show_signup_page(self):
        """Switch to the signup page."""
        self.stacked_widget.setCurrentIndex(1)
    
    def show_login_page(self):
        """Switch to the login page."""
        self.stacked_widget.setCurrentIndex(0)
    
    def center_window(self):
        """Centers the main window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # The image file 'library_bg.jpg' must be in the same directory as the script
    login_window = LoginWindow(bg_image_path="library_bg.jpg")
    login_window.show()
    sys.exit(app.exec_())