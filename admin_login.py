import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFrame, QCheckBox, QGraphicsBlurEffect
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QPainter, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QSize, QRectF

# Constants for styling
PRIMARY_COLOR = "#4A6CF7"  # Blue
SECONDARY_COLOR = "#4CAF50"  # Green
TEXT_COLOR = "#333333"
WHITE = "#FFFFFF"
BORDER_COLOR = "#E2E8F0"

class TransparentFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 220))  # Semi-transparent white
        painter.setPen(Qt.NoPen)
        
        # Draw rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 15, 15)
        painter.drawPath(path.simplified())

class LoginForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 380)  # Further reduced size
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        
    def init_ui(self):
        # Create a transparent frame for the form background
        self.frame = TransparentFrame(self)
        self.frame.setGeometry(0, 0, 300, 380)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 30, 25, 25)  # Further reduced margins
        layout.setSpacing(16)  # Consistent spacing
        
        # Title
        title = QLabel("Welcome Back")
        title.setStyleSheet(f"""
            QLabel {{
                color: {PRIMARY_COLOR};
                font-size: 22px;
                font-weight: 600;
                margin-bottom: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setAttribute(Qt.WA_TranslucentBackground)
        
        # Subtitle
        subtitle = QLabel("Sign in to continue")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                margin-bottom: 25px;
                opacity: 0.8;
            }}
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setAttribute(Qt.WA_TranslucentBackground)
        
        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 13px;
                margin-bottom: 6px;
                font-weight: 500;
            }}
        """)
        username_label.setAttribute(Qt.WA_TranslucentBackground)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                margin-bottom: 16px;
                background: {WHITE};
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                background: {WHITE};
                padding: 9px 13px;  # Adjust for border width
            }}
        """)
        
        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 13px;
                margin-bottom: 6px;
                font-weight: 500;
            }}
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                margin-bottom: 20px;
                background: {LIGHT_GRAY};
            }}
            QLineEdit:focus {{
                border: 1px solid {PRIMARY_COLOR};
                background: {WHITE};
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
        bg_path = os.path.join("assets", "login_bg.jpg")
        if os.path.exists(bg_path):
            self.bg_pixmap = QPixmap(bg_path).scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            self.background_label.setPixmap(self.bg_pixmap)
            
            # Add blur effect to background
            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(5)
            self.background_label.setGraphicsEffect(blur)
        else:
            # Fallback to solid color if no image found
            palette = self.palette()
            palette.setColor(QPalette.Window, QColor(240, 240, 240))
            self.setPalette(palette)
        
        # Initialize UI
        self.init_ui()
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
            
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # TODO: Implement login logic
        print(f"Login attempt - Username: {username}")
        
    def handle_signup(self):
        # TODO: Implement signup logic
        print("Signup clicked")
        
    def handle_forgot_password(self):
        # TODO: Implement forgot password logic
        print("Forgot password clicked")
    
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a container for the login form
        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        
        # Center the login form
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        
        # Add the login form
        login_form = LoginForm(self)
        layout.addWidget(login_form, 0, Qt.AlignCenter)
        layout.addStretch()
        
        # Add container to main layout
        main_layout.addWidget(container)

    def setup_right_panel(self, panel):
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
    
    # Set application style
    app.setStyle('Fusion')
    
    # Set default font
    font = QFont("Inter", 10)
    app.setFont(font)
    
    # Create and show the login window
    login = AdminLogin()
    login.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
