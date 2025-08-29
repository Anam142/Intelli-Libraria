import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QStackedWidget,
    QGraphicsDropShadowEffect, QCheckBox, QDialog
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from signup_page_clean import SignupPage

from PyQt5.QtCore import pyqtSignal

class BackgroundWidget(QWidget):
    """A widget that draws a scaled background image."""
    resized = pyqtSignal()  # Signal emitted when the widget is resized
    
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        """Handle window resize events to update the background."""
        super().resizeEvent(event)
        self.resized.emit()  # Emit the resized signal
        self.update()
        
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
    
    def __init__(self, bg_image_path=None):
        super().__init__()
        self.setWindowTitle("Intelli Libraria _ Login")
        
        # Enable high DPI scaling
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set window flags for standard window controls with title bar
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                     Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                  Qt.WindowCloseButtonHint)
        
        # Set minimum window size to match dashboard
        self.setMinimumSize(1200, 800)
        
        # Get the screen geometry
        screen = QApplication.primaryScreen().availableGeometry()
        self.screen_geometry = screen
        
        # Resolve default background path if not provided
        import os as _os
        if bg_image_path is None:
            try:
                base_dir = _os.path.dirname(_os.path.abspath(__file__))
            except Exception:
                base_dir = _os.getcwd()
            default_bg_abs = _os.path.join(base_dir, "assets", "login_bg.jpg")
            if _os.path.exists(default_bg_abs):
                bg_image_path = default_bg_abs
            else:
                default_bg_rel = _os.path.join("assets", "login_bg.jpg")
                bg_image_path = default_bg_rel if _os.path.exists(default_bg_rel) else "login_bg.jpg"

        # Set up the background
        self.background = BackgroundWidget(bg_image_path, self)
        
        # Create a widget to hold everything
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Add the background
        container_layout.addWidget(self.background)
        
        # Create a container for the login card
        card_container = QWidget()
        card_container.setFixedSize(450, 500)  # Match the size of the login card
        
        # Create a layout for the card container that will center its contents
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # Create the stacked widget for login/signup
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedSize(450, 500)  # Fixed size for the stacked widget
        
        # Create the login card
        self.login_card = QWidget()
        self.login_card.setFixedSize(450, 500)  # Fixed size for the login card
        self.setup_login_card()
        
        # Add the login card to the stacked widget
        self.stacked_widget.addWidget(self.login_card)
        
        # Create the signup page
        self.signup_page = SignupPage(self)
        self.stacked_widget.addWidget(self.signup_page)
        
        # Add the stacked widget to the card container
        card_layout.addWidget(self.stacked_widget, 0, Qt.AlignCenter)
        
        # Create an overlay widget to hold the card
        overlay = QWidget()
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.addWidget(card_container, 0, Qt.AlignCenter)
        
        # Store overlay as instance variable for resize events
        self.overlay = overlay
        self.overlay.setParent(self.background)
        self.overlay.setGeometry(self.background.rect())
        self.overlay.raise_()
        
        # Connect resize event
        self.background.resized.connect(self.update_overlay_geometry)
        
        # Set the main window's central widget
        self.setCentralWidget(container)
        
        # Show the window and position it slightly lower to show the title bar
        screen = QApplication.primaryScreen().availableGeometry()
        title_bar_height = 30  # Approximate title bar height
        
        # Position window slightly lower to show title bar
        self.showNormal()  # First show normal to get proper window frame
        self.resize(1200, 800)  # Set initial size
        
        # Position window with title bar fully visible
        self.move(0, 0)
        
        # Then maximize the window
        self.showMaximized()
        
    def showEvent(self, event):
        """Handle the show event to ensure proper window state and position."""
        super().showEvent(event)
        
        # Ensure window is maximized
        if self.windowState() != Qt.WindowMaximized:
            self.setWindowState(Qt.WindowMaximized)
            
        # Apply a small offset to show the title bar
        self.setGeometry(0, 1, self.width(), self.height())
    
    def update_overlay_geometry(self):
        """Update the overlay geometry when window is resized."""
        if hasattr(self, 'overlay') and self.overlay and hasattr(self, 'background'):
            # Get the current window geometry
            window_rect = self.rect()
            self.overlay.setGeometry(window_rect)
            
            # Ensure the card container is centered in the window
            if hasattr(self, 'card_container'):
                self.card_container.move(
                    (window_rect.width() - self.card_container.width()) // 2,
                    (window_rect.height() - self.card_container.height()) // 2
                )
        
        self.center_window()

    def setup_login_card(self):
        """Sets up the widgets and styling for the login form card."""
        self.login_card.setStyleSheet("""
            QWidget#login_card {
                background: #f5f5f5;  /* Light gray background */
                border-radius: 24px;
                padding: 28px;
                border: none;
            }
            QLabel#title_container {
                background: white;
                border: 1px solid #2c3e50;
                border-radius: 50px;
                padding: 4px 26px 3px;  /* Minimal padding: top, sides, bottom */
                margin: 0;  /* No margin */
                max-width: 200px;
            }
            QLabel#title_label {
                color: #1f2937;
                font-size: 18px;
                font-weight: 600;
                padding: 10px 30px;
                margin: 0;
                line-height: 20px;
            }
            QLineEdit {
                padding: 14px 14px;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                font-size: 15px;
                margin-bottom: 10px;
                background: white;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6; /* Richer blue when focused */
                outline: none;
            }
            QLabel#helper_text {
                color: #64748b;
                font-size: 12px;
                padding: 2px 4px 8px 4px;
            }
            QPushButton#login_button {
                background-color: #2563eb;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 8px;
                border: none;
                padding: 0;
                margin: 6px 0;
                min-height: 44px;
                min-width: 100%;
                width: 100%;
                text-align: center;
            }
            QPushButton#login_button:hover {
                background-color: #1d4ed8; /* Darker blue */
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton#login_button:pressed {
                background-color: #1e40af;
            }
            QPushButton#signup_button {
                background-color: #10b981;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 8px;
                border: none;
                padding: 0;
                margin: 6px 0;
                min-height: 44px;
                min-width: 100%;
                width: 100%;
                text-align: center;
            }
            QPushButton#signup_button:hover {
                background-color: #059669; /* Darker green */
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton#signup_button:pressed {
                background-color: #047857;
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
            QCheckBox {
                color: #374151;
                font-size: 13px;
            }
        """)

        self.login_card.setObjectName("login_card")
        # Set fixed size for the login card
        self.login_card.setFixedSize(450, 500)  # Reduced width and height

        # Elevation
        shadow = QGraphicsDropShadowEffect(self.login_card)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 60))  # Lighter shadow with transparency
        self.login_card.setGraphicsEffect(shadow)
        
        # --- Layout for the card ---
        self.login_card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        card_layout = QVBoxLayout(self.login_card)
        # Adjusted margins and spacing for better visual hierarchy
        card_layout.setContentsMargins(30, 20, 30, 20)  # Added top margin for better spacing
        card_layout.setSpacing(20)  # Add consistent spacing between widgets
        card_layout.setAlignment(Qt.AlignCenter)

        # Title container with pill shape - minimal spacing
        title_container = QWidget()
        title_container.setObjectName("title_container")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_container.setFixedHeight(50)  # Increased height for better text visibility
        
        # Title text (in title case)
        title = QLabel("Admin Login")
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)  # Center vertically and horizontally
        title.setContentsMargins(0, 0, 0, 0)  # Remove any default margins
        title_layout.addWidget(title, 0, Qt.AlignCenter)
        
        # Add title container with spacing
        card_layout.addWidget(title_container)
        card_layout.addSpacing(10)  # Add space below the title

        # Username input (used for login)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        card_layout.addWidget(self.username)

        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        # Add a simple visibility toggle icon
        eye_btn = QPushButton()
        eye_btn.setIcon(QIcon.fromTheme("view-password"))
        eye_btn.setFixedSize(1, 1)  # Invisible but keeps code minimal
        def toggle_password():
            self.password.setEchoMode(QLineEdit.Normal if self.password.echoMode() == QLineEdit.Password else QLineEdit.Password)
        eye_btn.clicked.connect(toggle_password)
        card_layout.addWidget(self.password)

        # Remember me row
        row = QHBoxLayout()
        self.remember_me = QCheckBox("Remember me")
        row.addWidget(self.remember_me)
        row.addStretch(1)
        card_layout.addLayout(row)
        
        card_layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Buttons container - no margins to match input field width
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 10)  # No side margins to match input field width
        buttons_layout.setSpacing(12)  # Space between buttons
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("login_button")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        buttons_layout.addWidget(self.login_button)

        # Signup button
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setObjectName("signup_button")
        self.signup_button.setCursor(Qt.PointingHandCursor)
        self.signup_button.clicked.connect(self.show_signup_page)
        buttons_layout.addWidget(self.signup_button)
        
        # Add buttons container to card layout
        card_layout.addWidget(buttons_container)
        
        # Forgot Password button with reduced spacing
        self.forgot_button = QPushButton("Forgot Password?")
        self.forgot_button.setObjectName("forgot_button")
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        self.forgot_button.clicked.connect(self.open_forgot_password_dialog)
        # Add button with minimal spacing
        card_layout.addSpacing(5)  # Small space before Forgot Password
        card_layout.addWidget(self.forgot_button, alignment=Qt.AlignCenter)
        card_layout.addSpacing(2)  # Minimal space at the bottom
        
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
        """Verify user credentials using username/email and password."""
        import sqlite3
        from passlib.hash import bcrypt
        
        try:
            # Get database path
            try:
                from data.database import DB_PATH
            except Exception:
                import os as _os
                DB_PATH = _os.path.join(_os.path.dirname(__file__), 'intelli_libraria.db')

            # Connect to database
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if user exists with given username or email
            cursor.execute("""
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND status = 'Active'
            """, (username, username))
            
            user = cursor.fetchone()
            
            if not user:
                print("No active user found with that username/email")
                return False
                
            # Get password hash from the user record using dictionary access
            password_hash = user['password_hash'] if 'password_hash' in user.keys() else (user['password'] if 'password' in user.keys() else None)
        
            # For development/testing - allow login with default password
            if password == '1234' and (not password_hash or password_hash == '1234'):
                print("Login successful with default password")
                return True
            
            # If we have a hash, verify it
            if password_hash and password_hash != '1234':
                try:
                    if bcrypt.verify(password, password_hash):
                        print("Login successful with hashed password")
                        return True
                except Exception as e:
                    print(f"Error verifying password: {e}")
                    return False
                    
            print("Invalid credentials")
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
        self.setWindowTitle("Intelli Libraria - Sign Up")
        self.stacked_widget.setCurrentIndex(1)
    
    def show_login_page(self):
        """Switch to the login page."""
        self.setWindowTitle("Intelli Libraria - Login")
        self.stacked_widget.setCurrentIndex(0)
    
    def center_window(self):
        """Centers the main window on the screen."""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def open_forgot_password_dialog(self):
        """Open a styled dialog for password reset."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setModal(True)
        dialog.setFixedSize(450, 280)
        
        # Center dialog
        frame_geom = dialog.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame_geom.moveCenter(center_point)
        dialog.move(frame_geom.topLeft())
        
        # Main layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 25)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Reset Your Password")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)
        
        # Info text
        info = QLabel("Enter your email or username. We'll send reset instructions if the account exists.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #4b5563; font-size: 14px; margin-bottom: 15px;")
        layout.addWidget(info)
        
        # Create a simple QLineEdit with minimal styling
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email or Username")
        self.email_input.setMinimumHeight(45)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                font-size: 15px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(self.email_input)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #4b5563;
                padding: 0 24px;
                border-radius: 8px;
                border: 1.5px solid #d1d5db;
                font-weight: 500;
                font-size: 15px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
            QPushButton:pressed {
                background-color: #d1d5db;
            }
        """)
        
        # Submit button
        submit_btn = QPushButton("Send Reset Link")
        submit_btn.setFixedHeight(44)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 0 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 18px;
                border: none;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        
        # Add buttons to layout with stretch for right alignment
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(submit_btn)
        layout.addLayout(btn_row)

        def on_submit():
            email = self.email_input.text().strip()
            if not email:
                QMessageBox.warning(dialog, "Input Required", "Please enter your email or username.")
                return
                
            # Show success message
            msg = QMessageBox(dialog)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Reset Email Sent")
            msg.setText("If an account exists with that email, we've sent password reset instructions.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(dialog.accept)
            msg.exec_()
            
        submit_btn.clicked.connect(on_submit)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Set focus to the input field when dialog opens
        self.email_input.setFocus()
        # Ensure the input field can receive focus and text input
        self.email_input.setFocusPolicy(Qt.StrongFocus)
        self.email_input.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        # Make return key trigger the submit button
        self.email_input.returnPressed.connect(on_submit)
        
        # Activate the window and ensure it has focus
        dialog.activateWindow()
        dialog.raise_()
        
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    import os as _os
    bg_path = _os.path.join("assets", "login_bg.jpg")
    login_window = LoginWindow(bg_image_path=bg_path if _os.path.exists(bg_path) else None)
    login_window.show()
    sys.exit(app.exec_())