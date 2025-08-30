import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QCheckBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QPainterPath, QIcon, QGraphicsBlurEffect
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
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), BORDER_RADIUS, BORDER_RADIUS)
        
        # Fill with white background
        painter.fillPath(path, QColor(WHITE))
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(SHADOW_BLUR)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        super().paintEvent(event)

class LoginForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 500)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
    
    def init_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(24)
        
        # Logo/Title
        title = QLabel("Admin Login")
        title.setStyleSheet(f"""
            QLabel {
                color: {TEXT_COLOR};
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
                padding: 12px 16px;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border: 2px solid {PRIMARY_COLOR};
                padding: 11px 15px;
            }
        """)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            QLineEdit {
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
                padding: 12px 16px;
                font-size: 14px;
                margin-bottom: 10px;
            }
            QLineEdit:focus {
                border: 2px solid {PRIMARY_COLOR};
                padding: 11px 15px;
            }
        """)
        
        # Remember me checkbox
        self.remember_check = QCheckBox("Remember me")
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(45)
        login_btn.setStyleSheet(f"""
            QPushButton {
                background-color: {PRIMARY_COLOR};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #3a5bd9;
            }
            QPushButton:pressed {
                background-color: #2a4bc4;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.remember_check)
        layout.addWidget(login_btn)
        
        # Connect signals
        login_btn.clicked.connect(self.parent().handle_login)

class AdminLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 600)
        
        # Set window background
        self.setStyleSheet(f"""
            QWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f6f9fc, stop: 1 #eef2f5
                );
            }
        """)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add login form
        self.login_form = LoginForm(self)
        main_layout.addStretch()
        main_layout.addWidget(self.login_form)
        main_layout.addStretch()
        
        # Store the initial position for window dragging
        self.oldPos = None
    
    def handle_login(self):
        """Handle login button click"""
        username = self.login_form.username_input.text()
        password = self.login_form.password_input.text()
        # TODO: Implement actual login logic
        print(f"Login attempt - Username: {username}")
    
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

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show login window
    login_window = AdminLogin()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
