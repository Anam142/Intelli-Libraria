import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt

class SidebarButton(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 0 20px;
                border: none;
                border-radius: 6px;
                margin: 4px 12px;
                font-size: 14px;
                color: #2d3748;
                background: transparent;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #edf2f7;
            }
            QPushButton:checked {
                background: #ebf8ff;
                color: #2b6cb0;
                font-weight: 500;
            }
        """)
        self.setText(f"{icon}  {text}")

class ModernSidebarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setMinimumSize(1200, 700)
        self.setup_ui()
    
    def setup_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        content = QFrame()
        content.setStyleSheet("background: #ffffff;")
        content_layout = QVBoxLayout(content)
        
        # Add a welcome message
        welcome = QLabel("Welcome to Library Management System")
        welcome.setStyleSheet("""
            font-size: 24px;
            color: #2d3748;
            padding: 40px;
            font-weight: 500;
        """)
        content_layout.addWidget(welcome)
        
        main_layout.addWidget(content, 1)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)
        
        # App title
        title = QLabel("LIBRARIA")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #2d3748;
            padding: 0 12px 20px 12px;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Navigation items
        nav_items = [
            ("📊", "Dashboard"),
            ("📚", "Books"),
            ("👥", "Members"),
            ("📝", "Borrow"),
            ("↩️", "Return"),
            ("📈", "Reports"),
            ("⚙️", "Settings"),
            ("❓", "Help")
        ]
        
        for icon, text in nav_items:
            btn = SidebarButton(icon, text)
            layout.addWidget(btn)
        
        # Add spacer to push user info to bottom
        layout.addStretch()
        
        # User info at bottom
        user = QFrame()
        user.setStyleSheet("""
            QFrame {
                background: #edf2f7;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        user_layout = QHBoxLayout(user)
        user_layout.setContentsMargins(8, 8, 8, 8)
        
        # User icon
        icon = QLabel("👤")
        icon.setStyleSheet("font-size: 20px;")
        
        # User details
        details = QVBoxLayout()
        details.setSpacing(2)
        
        name = QLabel("Admin User")
        name.setStyleSheet("font-weight: 500; font-size: 13px;")
        
        role = QLabel("Administrator")
        role.setStyleSheet("color: #4a5568; font-size: 12px;")
        
        details.addWidget(name)
        details.addWidget(role)
        
        user_layout.addWidget(icon)
        user_layout.addLayout(details)
        user_layout.addStretch()
        
        layout.addWidget(user)
        
        return sidebar

def main():
    app = QApplication(sys.argv)
    window = ModernSidebarApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
