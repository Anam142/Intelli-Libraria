import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
                margin: 2px 10px;
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria")
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
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background-color: #ffffff;")
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.addWidget(self.stacked_widget)
        
        # Add example pages
        self.add_example_pages()
        
        main_layout.addWidget(self.content_area, 1)
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)
        
        # App title
        app_title = QLabel("Intelli Libraria")
        app_title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #2d3748;
            padding: 0 12px 20px 12px;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 10px;
        """)
        layout.addWidget(app_title)
        
        # Navigation buttons
        nav_items = [
            ("📊", "Dashboard"),
            ("👥", "User Management"),
            ("📚", "Book Inventory"),
            ("↩️", "Borrow/Return"),
            ("📈", "Report Generation"),
        ]
        
        self.button_group = []
        for icon, text in nav_items:
            btn = SidebarButton(icon, text)
            btn.clicked.connect(lambda checked, idx=len(self.button_group): self.on_nav_clicked(idx))
            layout.addWidget(btn)
            self.button_group.append(btn)
        
        layout.addStretch()
        
        # User info at bottom
        user_widget = QFrame()
        user_widget.setStyleSheet("""
            QFrame {
                background-color: #edf2f7;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(8, 8, 8, 8)
        user_layout.setSpacing(12)
        
        # User icon
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 20px;")
        
        # User info
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        
        user_name = QLabel("Admin User")
        user_name.setStyleSheet("""
            font-weight: 600;
            font-size: 13px;
            color: #2d3748;
        """)
        
        user_role = QLabel("Administrator")
        user_role.setStyleSheet("""
            font-size: 12px;
            color: #718096;
        """)
        
        user_info.addWidget(user_name)
        user_info.addWidget(user_role)
        
        user_layout.addWidget(user_icon)
        user_layout.addLayout(user_info)
        
        layout.addWidget(user_widget)
        
        return sidebar
    
    def add_example_pages(self):
        # Add some example pages
        pages = [
            ("Dashboard", "Welcome to the Library Management System"),
            ("Books", "Manage your book collection"),
            ("Users", "Manage library users and permissions"),
            ("Borrow", "Handle book checkouts"),
            ("Return", "Process book returns"),
            ("Transactions", "View transaction history"),
            ("Reports", "Generate and view reports"),
            ("Settings", "Configure application settings")
        ]
        
        for title, description in pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 10px;
            """)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #718096;
            """)
            
            layout.addWidget(title_label)
            layout.addWidget(desc_label)
            layout.addStretch()
            
            self.stacked_widget.addWidget(page)
        
        # Set first button as active by default
        if self.button_group:
            self.button_group[0].setChecked(True)
    
    def on_nav_clicked(self, index):
        # Uncheck all buttons
        for btn in self.button_group:
            btn.setChecked(False)
        
        # Check the clicked button
        self.button_group[index].setChecked(True)
        
        # Switch to the corresponding page
        self.stacked_widget.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
