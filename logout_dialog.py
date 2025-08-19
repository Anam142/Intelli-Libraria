from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QGraphicsDropShadowEffect, 
                           QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor

class LogoutConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        print("LogoutConfirmationDialog.__init__ called")  # Debug
        super().__init__(parent)
        print("1. Parent set:", parent)  # Debug
        
        self.setWindowTitle("Logout Confirmation")
        self.setFixedSize(400, 240)
        print("2. Window size and title set")  # Debug
        
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        print("3. Window flags set")  # Debug
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(24)
        
        # Header
        header = QVBoxLayout()
        header.setSpacing(12)
        
        # Icon
        icon_label = QLabel("🚪")
        icon_label.setStyleSheet("""
            font-size: 40px;
            padding: 0;
            margin: 0;
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel("Confirm Log Out")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0;
            padding: 0;
            text-align: center;
        """)
        
        # Message
        message_label = QLabel(
            "Are you sure you want to log out of your account? "
            "You'll need to sign in again to access your dashboard."
        )
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            font-size: 14px;
            color: #64748b;
            margin: 0;
            padding: 0;
            line-height: 1.5;
            text-align: center;
        """)
        
        # Add header widgets
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addWidget(message_label)
        
        # Button container
        button_container = QHBoxLayout()
        button_container.setSpacing(12)
        button_container.setContentsMargins(0, 8, 0, 0)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #334155;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton:pressed {
                background-color: #cbd5e1;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Logout button
        logout_btn = QPushButton("Log Out")
        logout_btn.setFixedHeight(44)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        logout_btn.clicked.connect(self.accept)
        
        # Add buttons to container
        button_container.addStretch(1)
        button_container.addWidget(cancel_btn)
        button_container.addWidget(logout_btn)
        
        # Add widgets to main layout
        layout.addLayout(header)
        layout.addStretch(1)
        layout.addLayout(button_container)
        
        # Center the dialog on the screen
        self.center_on_screen()
        
        # Debug
        print("LogoutConfirmationDialog initialized")
    
    def showEvent(self, event):
        # Center the dialog on the screen
        frame_geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        
        super().showEvent(event)
        print("Logout dialog shown")
