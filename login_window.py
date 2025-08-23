import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSpacerItem, QSizePolicy, QStackedWidget,
    QGraphicsDropShadowEffect, QCheckBox
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QIcon
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
    
    def __init__(self, bg_image_path=None):
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
                background: rgba(255, 255, 255, 0.92);
                border-radius: 24px;
                padding: 28px;
            }
            QLabel#title_container {
                background: white;
                border: 1px solid #2c3e50;  /* Dark border */
                border-radius: 50px;
                padding: 10px 26px;
                margin-bottom: 16px;
                max-width: 200px;
                margin-left: auto;
                margin-right: auto;
            }
            QLabel#title_label {
                font-family: Arial;
                font-size: 24px;
                font-weight: 800;
                color: #2c3e50; /* Dark text */
                text-align: center;
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
                background-color: #2563eb; /* Richer blue */
                color: white;
                font-size: 16px;
                font-weight: 700;
                border-radius: 10px;
                border: none;
                padding: 14px;
                margin-top: 14px;
            }
            QPushButton#login_button:hover {
                background-color: #1d4ed8; /* Darker blue */
            }
            QPushButton#signup_button {
                background-color: #10b981; /* Richer green */
                color: white;
                font-size: 16px;
                font-weight: 700;
                border-radius: 10px;
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
            QCheckBox {
                color: #374151;
                font-size: 13px;
            }
        """)

        self.login_card.setObjectName("login_card")
        # Set fixed size for the login card
        self.login_card.setFixedSize(520, 560)

        # Elevation
        shadow = QGraphicsDropShadowEffect(self.login_card)
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(18)
        shadow.setColor(Qt.black)
        self.login_card.setGraphicsEffect(shadow)
        
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

        # Username input (used for login)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        card_layout.addWidget(self.username)
        email_hint = QLabel("Use your username")
        email_hint.setObjectName("helper_text")
        card_layout.addWidget(email_hint)

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
        """Verify user credentials using a username-like field and password hash.

        This checks common username columns in priority order: 'username', 'user_code',
        'full_name', then falls back to 'email' if none exist.
        """
        import sqlite3
        from passlib.hash import bcrypt
        
        try:
            try:
                from data.database import DB_PATH
            except Exception:
                import os as _os
                DB_PATH = _os.path.join(_os.path.dirname(__file__), 'intelli_libraria.db')
                
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # First, check if the password column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1].lower() for row in cursor.fetchall()]
            
            if 'password' not in columns:
                # If no password column, use default password '1234' for backward compatibility
                cursor.execute("SELECT id, email FROM users WHERE LOWER(email) = LOWER(?)", (username,))
                user = cursor.fetchone()
                if user and password == '1234':
                    return True
                return False
                
            # Password column exists, check with bcrypt
            username_columns = ['username', 'user_code', 'full_name', 'email']
            query_parts = []
            params = []
            
            # Build the query to check all possible username columns
            for col in username_columns:
                query_parts.append(f"{col} = ?")
                params.append(username)
            
            # First try with password_hash column
            query = f"""
                SELECT id, password_hash, password, role, full_name 
                FROM users 
                WHERE ({" OR ".join(query_parts)})
            """
            
            cursor.execute(query, params)
            user = cursor.fetchone()
            
            if not user:
                print("No user found with that username/email")
                return False
                
            # Try password_hash column first, then fall back to password
            stored_hash = None
            if len(user) > 1 and user[1]:  # Check password_hash column
                stored_hash = user[1]
            elif len(user) > 2 and user[2]:  # Fall back to password column
                stored_hash = user[2]
            
            # First try bcrypt verification if we have a hash
            if stored_hash and bcrypt.verify(password, stored_hash):
                print("Login successful with bcrypt hash!")
                return True
                
            # For backward compatibility, check if password is '1234' and the hash matches
            if password == '1234' and stored_hash == '1234':
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
    import os as _os
    bg_path = _os.path.join("assets", "login_bg.jpg")
    login_window = LoginWindow(bg_image_path=bg_path if _os.path.exists(bg_path) else None)
    login_window.show()
    sys.exit(app.exec_())