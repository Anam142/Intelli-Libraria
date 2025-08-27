from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                           QDialogButtonBox, QHBoxLayout, QPushButton, QApplication, QDesktopWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

class LogoutConfirmationDialog(QDialog):
    def __init__(self, parent=None):
        print("\n=== Creating LogoutConfirmationDialog ===")
        print(f"Parent: {parent}")
        
        # Initialize the dialog with proper flags
        super().__init__(parent, Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # Basic dialog setup
        self.setWindowTitle("Logout Confirmation")
        self.setFixedSize(400, 280)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(24)
        
        # Header with icon and message
        header = QVBoxLayout()
        header.setSpacing(12)
        
        # Icon container with border
        icon_container = QFrame()
        icon_container.setFixedSize(80, 80)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #fef2f2;
                border-radius: 40px;
                border: 1px solid #fecaca;
            }
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        
        # Add icon using built-in Qt icon
        try:
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            
            # Use a built-in Qt icon for logout
            logout_icon = QApplication.style().standardIcon(QApplication.style().SP_DialogCloseButton)
            icon_pixmap = logout_icon.pixmap(48, 48)
            
            # Apply a color tint to match the logout theme
            from PyQt5.QtGui import QPainter, QColor
            tinted_pixmap = icon_pixmap.copy()
            painter = QPainter(tinted_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted_pixmap.rect(), QColor("#ef4444"))  # Red color for logout action
            painter.end()
            
            icon_label.setPixmap(tinted_pixmap)
            icon_layout.addWidget(icon_label, 0, Qt.AlignCenter)
            
        except Exception as e:
            print(f"Error creating icon: {e}")
            # Fallback to text emoji if icon creation fails
            icon_label = QLabel("🚪")
            icon_label.setStyleSheet("font-size: 32px;")
            icon_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        
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
        message = QLabel(
            "Are you sure you want to log out of your account? "
            "You'll need to sign in again to access your dashboard."
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            font-size: 14px;
            color: #64748b;
            margin: 0;
            padding: 0;
            line-height: 1.5;
            text-align: center;
        """)
        
        # Add header widgets
        header.addWidget(icon_container, 0, Qt.AlignCenter)
        header.addWidget(title_label)
        header.setAlignment(Qt.AlignCenter)
        header.addWidget(message)
        
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
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        logout_btn.clicked.connect(self.accept)
        
        # Add buttons to container with stretch
        button_container.addStretch()
        button_container.addWidget(cancel_btn)
        button_container.addWidget(logout_btn)
        
        # Add to main layout
        layout.addLayout(header)
        layout.addStretch()
        layout.addLayout(button_container)
        
        # Center the dialog initially
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

    def center_on_screen(self):
        """Center the dialog on its parent if available; otherwise center on screen."""
        try:
            if self.parent() and isinstance(self.parent(), QWidget):
                parent_geom = self.parent().frameGeometry()
                center_point = parent_geom.center()
            else:
                screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
                center_point = QDesktopWidget().screenGeometry(screen).center()

            frame_geom = self.frameGeometry()
            frame_geom.moveCenter(center_point)
            self.move(frame_geom.topLeft())
            # Bring to front
            self.setWindowModality(Qt.ApplicationModal)
            self.raise_()
            self.activateWindow()
        except Exception:
            # Fallback to default move
            self.move(200, 150)
