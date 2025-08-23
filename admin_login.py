import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QCheckBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QPainter, QPainterPath, QIcon
from PyQt5.QtCore import Qt, QSize, QRectF, QPropertyAnimation, QEasingCurve

# Modern color scheme
PRIMARY_COLOR = "#4361EE"  # Modern blue
SECONDARY_COLOR = "#7209B7"  # Modern purple
TEXT_COLOR = "#2B2D42"
WHITE = "#FFFFFF"
BORDER_COLOR = "#E9ECEF"
ACCENT_COLOR = "#F72585"  # Pink accent
LIGHT_GRAY = "#F8F9FA"
DARK_GRAY = "#495057"
BORDER_RADIUS = 10
SHADOW_BLUR = 25

class CardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(SHADOW_BLUR)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Draw card background
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        
        # Draw rounded rectangle with a slight offset for the shadow
        path = QPainterPath()
        path.addRoundedRect(QRectF(5, 5, self.width() - 10, self.height() - 10), 
                          BORDER_RADIUS, BORDER_RADIUS)
        painter.drawPath(path.simplified())

class LoginForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 500)  # Slightly larger for better spacing
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create a container widget for centering
        self.container = QWidget()
        self.container.setFixedSize(400, 500)
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        
        # Add container to main layout with center alignment
        self.main_layout.addWidget(self.container, 0, Qt.AlignCenter)
        
        # Initialize UI components
        self.init_ui()
        
    def showEvent(self, event):
        # Center the form when shown
        self.center_on_parent()
        super().showEvent(event)
    
    def center_on_parent(self):
        """Position the login form on its parent widget, shifted to the right"""
        if self.parent():
            parent_rect = self.parent().geometry()
            # Move 150px to the right from center
            x = (parent_rect.width() - self.width()) // 2 + 150
            y = (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
    def init_ui(self):
        # Create card widget for the form background
        self.card = CardWidget(self.container)
        self.card.setFixedSize(400, 500)
        
        # Create layout for the container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.card)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 40, 30, 30)
        main_layout.setSpacing(24)
        
        # Logo/Icon (you can replace with your logo)
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(80, 80)
        self.logo_label.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY_COLOR};
                border-radius: 40px;
                margin: 0 auto 10px auto;
            }}
        """)
        
        # Title
        title = QLabel("Admin Portal")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 24px;
                font-weight: 600;
                margin: 0;
                padding: 0;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Sign in to your account")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {DARK_GRAY};
                font-size: 14px;
                margin: 0 0 30px 0;
                padding: 0;
                opacity: 0.8;
            }}
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Add logo, title, and subtitle to layout
        main_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        
        # Form layout for inputs
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Username field
        username_label = QLabel("Email Address")
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 13px;
                margin-bottom: 8px;
                font-weight: 500;
            }}
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your email")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS - 2}px;
                padding: 12px 16px;
                font-size: 14px;
                margin-bottom: 5px;
                background: {WHITE};
                color: {TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                padding: 11px 15px;
                background: {WHITE};
                padding: 9px 13px;  # Adjust for border width
            }}
        """)
        
        # Add username field to form
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 13px;
                margin: 15px 0 8px 0;
                font-weight: 500;
            }}
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS - 2}px;
                padding: 12px 16px;
                font-size: 14px;
                margin-bottom: 5px;
                background: {WHITE};
                color: {TEXT_COLOR};
                letter-spacing: 1px;
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                padding: 11px 15px;
            }}
        """)
        
        # Remember me checkbox
        remember_layout = QHBoxLayout()
        self.remember_check = QCheckBox("Remember me")
        self.remember_check.setAttribute(Qt.WA_TranslucentBackground)
        self.remember_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_COLOR};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {PRIMARY_COLOR};
                border: 2px solid {PRIMARY_COLOR};
                image: url();
            }}
        """)
        
        # Forgot password button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PRIMARY_COLOR};
                font-size: 14px;
                font-weight: 500;
                border: none;
                background: transparent;
                text-align: right;
                padding: 0;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        
        remember_layout.addWidget(self.remember_check)
        remember_layout.addStretch()
        remember_layout.addWidget(forgot_btn)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                margin: 10px 0 15px 0;
            }}
            QPushButton:hover {{
                background-color: #3a5bd9;
            }}
            QPushButton:pressed {{
                background-color: #2a4bc4;
            }}
        """)
        
        # Sign up button
        signup_btn = QPushButton("Signup")
        signup_btn.setFixedHeight(45)
        signup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {SECONDARY_COLOR};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                margin-bottom: 10px;
            }}
            QPushButton:hover {{
                background-color: #3e8e41;
            }}
            QPushButton:pressed {{
                background-color: #2e7d32;
            }}
        """)
        
        # Forgot password link
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PRIMARY_COLOR};
                font-size: 14px;
                border: none;
                background: transparent;
                text-align: center;
                padding: 5px;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        
        # Add widgets to layout
        layout.addWidget(title, 0, Qt.AlignCenter)
        layout.addWidget(username_label, 0, Qt.AlignLeft)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label, 0, Qt.AlignLeft)
        layout.addWidget(self.password_input)
        layout.addLayout(remember_layout)
        layout.addWidget(login_btn)
        layout.addWidget(signup_btn)
        layout.addWidget(forgot_btn, 0, Qt.AlignCenter)
        
        # Connect signals
        login_btn.clicked.connect(self.parent().handle_login)
        signup_btn.clicked.connect(self.parent().handle_signup)
        forgot_btn.clicked.connect(self.parent().handle_forgot_password)

class AdminLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(1280, 800)
        
        # Set window background
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setScaledContents(True)
        
        # Try to load background image, fallback to solid color
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
            
        # Try multiple possible paths for the background image
        bg_paths = [
            os.path.join(base_dir, "assets", "login_bg.jpg"),
            os.path.join("assets", "login_bg.jpg"),
            os.path.join("Intelli-Libraria", "assets", "login_bg.jpg")
        ]
        
        bg_found = False
        for bg_path in bg_paths:
            if os.path.exists(bg_path):
                self.bg_pixmap = QPixmap(bg_path).scaled(
                    self.size(), 
                    Qt.KeepAspectRatioByExpanding, 
                    Qt.SmoothTransformation
                )
                self.background_label.setPixmap(self.bg_pixmap)
                
                # Add blur effect to background
                blur = QGraphicsBlurEffect()
                blur.setBlurRadius(8)
                self.background_label.setGraphicsEffect(blur)
                bg_found = True
                break
                
        if not bg_found:
            # Fallback to gradient background
            self.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #f6f9fc, stop: 1 #eef2f5
                    );
                }}
            """)
        
        # Initialize UI
        self.init_ui()
        
        # Center window on screen
        self.center_window()
        
        # Store the initial position for window dragging
        self.oldPos = None
        
    def center_window(self):
        # Center the window on the screen
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        """Reset old position when mouse is released"""
        self.oldPos = None
            
    def handle_login(self):
        """Handle login button click"""
        username = self.login_form.username_input.text()
        password = self.login_form.password_input.text()
        # TODO: Implement login logic
        print(f"Login attempt - Username: {username}")
        
    def handle_signup(self):
        """Handle signup button click"""
        print("Signup clicked")
        # TODO: Implement signup logic
        
    def handle_forgot_password(self):
        """Handle forgot password click"""
        print("Forgot password clicked")
        # TODO: Implement forgot password logic
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a container for the login form
        self.container = QWidget(self)
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout for the container
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add the login form
        self.login_form = LoginForm(self.container)
        layout.addWidget(self.login_form, 0, Qt.AlignCenter)
        
        # Set the container as the central widget
        self.setCentralWidget(self.container)
        
        # Center the window on the screen
        self.center_window()
        
    def resizeEvent(self, event):
        # Keep the background image scaled correctly
        if hasattr(self, 'bg_pixmap'):
            self.background_label.setPixmap(
                self.bg_pixmap.scaled(
                    self.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )
        
        # Ensure the login form stays centered
        if hasattr(self, 'login_form'):
            self.login_form.center_on_parent()
            
        super().resizeEvent(event)
        
    def add_window_controls(self):
        """Add minimize and close buttons"""
        # Create control container
        control_container = QWidget(self)
        control_container.setFixedSize(100, 40)
        control_container.move(self.width() - 110, 10)
        control_container.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout for controls
        layout = QHBoxLayout(control_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Minimize button
        min_btn = QPushButton("−")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 95, 87, 0.8);
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 95, 87, 1);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # Add buttons to layout
        layout.addWidget(min_btn)
        layout.addWidget(close_btn)
        
class LoginForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 500)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create card widget for the form background
        self.card = CardWidget(self)
        self.card.setFixedSize(400, 500)
        
        # Create layout for the card content
        self.card_layout = QVBoxLayout()
        self.card_layout.setContentsMargins(30, 40, 30, 30)
        self.card_layout.setSpacing(24)
        
        # Add card to main layout
        self.main_layout.addWidget(self.card)
        
        # Initialize UI components
        self.init_ui()
        
    def showEvent(self, event):
        # Center the form when shown
        self.center_on_parent()
        super().showEvent(event)
    
    def center_on_parent(self):
        """Position the login form on its parent widget, shifted to the right"""
        if self.parent():
            parent_rect = self.parent().geometry()
            # Move 150px to the right from center
            x = (parent_rect.width() - self.width()) // 2 + 150
            y = (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        
    def init_ui(self):
        """Initialize the UI components"""
        # Logo/Icon (you can replace with your logo)
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(80, 80)
        self.logo_label.setStyleSheet(f"""
            QLabel {{
                background-color: {PRIMARY_COLOR};
                border-radius: 40px;
                margin: 0 auto 10px auto;
            }}
        """)
        
        # Title
        title = QLabel("Admin Portal")
        title.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 24px;
                font-weight: 600;
                margin: 0;
                padding: 0;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle
        subtitle = QLabel("Sign in to your account")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {DARK_GRAY};
                font-size: 14px;
                margin: 0 0 30px 0;
                padding: 0;
                opacity: 0.8;
            }}
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Add widgets to card layout
        self.card_layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        self.card_layout.addWidget(title)
        self.card_layout.addWidget(subtitle)
        
        # Set the card layout
        self.card.setLayout(self.card_layout)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(0)
        
        # Close button (top right)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666;
                font-size: 18px;
                font-weight: normal;
                border-radius: 16px;
                padding: 0;
            }
            QPushButton:hover {
                background: #f0f0f0;
                color: #333;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # Add close button to top right
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # Add top spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Title
        title_label = QLabel("Sign In")
        title_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 5px;
            }
        """)
        
        # Subtitle
        subtitle_label = QLabel("Sign in to access your dashboard")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 14px;
                margin-bottom: 30px;
            }
        """)
        
        # Add title and subtitle to layout
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        
        # Email input
        email_label = QLabel("Email Address")
        email_label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFixedHeight(48)
        
        # Password input
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                color: #4a5568;
                font-size: 14px;
                font-weight: 600;
                margin-top: 20px;
                margin-bottom: 8px;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(48)
        
        # Remember me and forgot password
        bottom_row = QHBoxLayout()
        
        self.remember_me = QCheckBox("Remember me")
        self.remember_me.setStyleSheet(f"""
            QCheckBox {{
                color: #4a5568;
                font-size: 12px;
                spacing: 6px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid #cbd5e0;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: #4a6cf7;
                border: 1px solid #4a6cf7;
            }}
        """)
        
        self.forgot_password = QPushButton("Forgot Password?")
        self.forgot_password.setStyleSheet(f"""
            QPushButton {{
                color: #4a6cf7;
                font-size: 12px;
                border: none;
                background: transparent;
                text-align: right;
                padding: 0;
                font-weight: 500;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        self.forgot_password.setCursor(Qt.PointingHandCursor)
        
        bottom_row.addWidget(self.remember_me)
        bottom_row.addStretch(1)
        bottom_row.addWidget(self.forgot_password)
        
        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #4a6cf7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
                margin: 18px 0 12px;
                height: 40px;
            }}
            QPushButton:hover {{
                background-color: #3a5bd9;
            }}
            QPushButton:pressed {{
                background-color: #2e4ec7;
            }}
        """)
        self.login_button.setCursor(Qt.PointingHandCursor)
        
        # Add widgets to layout with proper spacing
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)  # Reduced spacing
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        layout.addSpacing(5)   # Reduced spacing
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(5)   # Reduced spacing
        layout.addLayout(bottom_row)
        layout.addWidget(self.login_button)
        layout.addStretch(1)
        # Sign up link
        signup_layout = QHBoxLayout()
        signup_layout.setAlignment(Qt.AlignCenter)
        signup_layout.setSpacing(5)
        
        no_account = QLabel("Don't have an account?")
        no_account.setStyleSheet("color: #718096; font-size: 14px;")
        
        signup_btn = QPushButton("Sign up")
        signup_btn.setStyleSheet("""
            QPushButton {
                color: #4a6cf7;
                font-size: 14px;
                font-weight: 600;
                padding: 0;
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        signup_layout.addWidget(no_account)
        signup_layout.addWidget(signup_btn)
        
        layout.addStretch()
        layout.addLayout(signup_layout)
        
        # Header
        header = QLabel("Admin Login")
        header.setStyleSheet("""
            color: #1a237e;
            font-size: 28px;
            font-weight: bold;
            margin: 20px 0 40px 0;
        """)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            color: #333333;
            font-size: 14px;
            font-weight: 500;
        """)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setFixedHeight(45)
        self.username.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 0 15px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                outline: none;
            }
        """)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            color: #333333;
            font-size: 14px;
            font-weight: 500;
            margin-top: 15px;
        """)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(45)
        self.password.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 0 15px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                outline: none;
            }
        """)
        
        # Forgot password link
        forgot_pwd = QLabel("<a href='#' style='color: #1a73e8; text-decoration: none;'>Forgot Password?</a>")
        forgot_pwd.setStyleSheet("font-size: 13px;")
        forgot_pwd.setOpenExternalLinks(False)
        forgot_pwd.linkActivated.connect(self.on_forgot_password)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 500;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        login_btn.clicked.connect(self.on_login_clicked)
        
        # Add widgets to form layout
        form_layout.addWidget(logo_label)
        form_layout.addWidget(header)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password)
        form_layout.addWidget(forgot_pwd, 0, Qt.AlignRight)
        form_layout.addWidget(login_btn)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add bottom spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add form to main layout
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def on_login_clicked(self):
        username = self.username.text()
        password = self.password.text()
        
        # Add your authentication logic here
        if username and password:
            QMessageBox.information(self, "Success", "Login successful!")
            # TODO: Open admin dashboard
        else:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
    
    def on_forgot_password(self):
        QMessageBox.information(self, "Forgot Password", "Please contact the system administrator.")

def main():
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Set application stylesheet
    app.setStyleSheet(f"""
        QLineEdit, QPushButton, QCheckBox {{
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        QLineEdit {{
            border: 1px solid #e0e0e0;
            padding: 10px 14px;
        }}
        QPushButton {{
            background-color: #1a73e8;
            color: white;
            font-weight: 500;
            min-width: 100px;
            padding: 10px 20px;
        }}
        QPushButton:hover {{
            background-color: #3a5bd9;
        }}
    """)
    
    # Create and show login window
    login_window = AdminLogin()
    
    # Center window on screen
    screen = QApplication.primaryScreen().availableGeometry()
    x = (screen.width() - login_window.width()) // 2
    y = (screen.height() - login_window.height()) // 2
    login_window.move(x, y)
    
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
