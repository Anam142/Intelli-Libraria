import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget,
                            QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from logout_dialog import LogoutConfirmationDialog

class SidebarButton(QPushButton):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                border-radius: 8px;
                margin: 2px 8px;
                font-size: 14px;
                color: #2c3e50;
                background: transparent;
            }
            QPushButton:hover {
                background: #e9ecef;
            }
            QPushButton:checked {
                background: #e3f2fd;
                color: #1976d2;
                font-weight: 500;
            }
            QPushButton:pressed {
                background: #d1e7ff;
            }
        """)
        
        # Create layout for icon and text
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 15, 0)
        layout.setSpacing(12)
        
        # Add icon
        icon_label = QLabel()
        icon_label.setFixedSize(20, 20)
        if icon_path:
            icon_label.setPixmap(QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(icon_label)
        
        # Add text
        text_label = QLabel(text)
        text_label.setStyleSheet("background: transparent;")
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Store the icon path for reference
        self.icon_path = icon_path

class MainWindow(QMainWindow):
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
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area
        self.content_area = QFrame()
        self.content_area.setStyleSheet("background-color: #f8f9fa;")
        self.content_area.setFrameShape(QFrame.StyledPanel)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.stacked_widget)
        
        # Add some example pages
        self.add_example_pages()
        
        main_layout.addWidget(self.content_area, 1)  # 1 is stretch factor
        
    def handle_logout(self):
        """Handle the logout button click event."""
        print("\n=== Logout button clicked ===")
        try:
            print("Creating logout dialog...")
            dialog = LogoutConfirmationDialog(self)
            print("Setting dialog properties...")
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.setAttribute(Qt.WA_DeleteOnClose)
            
            # Show the dialog explicitly
            print("Showing dialog...")
            result = dialog.exec_()
            print(f"Dialog closed with result: {result}")
            
            if result == QDialog.Accepted:
                print("Logout confirmed - closing application")
                self.close()
            else:
                print("Logout cancelled")
                
        except Exception as e:
            print(f"ERROR in handle_logout: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-right: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 20, 8, 20)
        layout.setSpacing(5)
        
        # Logo area
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(15, 0, 15, 20)
        
        # Add your logo here (replace with actual logo path)
        logo = QLabel()
        logo.setFixedSize(32, 32)
        logo.setStyleSheet("""
            QLabel {
                background-color: #1976d2;
                border-radius: 8px;
            }
        """)
        
        app_name = QLabel("LIBRARIA")
        app_name.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #2c3e50;
                margin-left: 10px;
            }
        """)
        
        logo_layout.addWidget(logo)
        logo_layout.addWidget(app_name)
        logo_layout.addStretch()
        
        layout.addLayout(logo_layout)
        
        # Navigation buttons
        nav_buttons = [
            ("📚", "Manage Books"),
            ("👥", "User Management"),
            ("📅", "Borrow/Return"),
            ("📊", "Reports"),
            ("⚙️", "Settings"),
            ("❓", "Help & Support")
        ]
        
        self.button_group = []
        
        for icon, text in nav_buttons:
            btn = SidebarButton("", f"{icon} {text}")
            btn.clicked.connect(lambda checked, idx=len(self.button_group): self.on_nav_clicked(idx))
            layout.addWidget(btn)
            self.button_group.append(btn)
        
        # Add stretch to push everything up
        layout.addStretch()
        
        # User profile section
        user_container = QFrame()
        user_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 12px;
                margin: 15px 8px 0 8px;
            }
        """)
        
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        
        # User info
        user_info_layout = QHBoxLayout()
        user_info_layout.setContentsMargins(5, 0, 0, 0)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 20px; margin-right: 10px;")
        
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
        
        user_info_layout.addWidget(user_icon)
        user_info_layout.addLayout(user_info)
        user_info_layout.addStretch()
        
        # Create logout button
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setIcon(QIcon("icons/logout.png"))
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                padding: 8px 15px;
                text-align: left;
            }
            QPushButton:hover {
                background: #f1f5f9;
                border-color: #cbd5e1;
            }
            QPushButton:pressed {
                background: #e2e8f0;
            }
        """)
        self.logout_btn.clicked.connect(self.handle_logout)
        
        # Add user info and logout button to layout
        user_layout.addLayout(user_info_layout, 1)
        user_layout.addWidget(self.logout_btn, 0, Qt.AlignRight)
        
        layout.addWidget(user_container)
        
        return sidebar
    
    def add_example_pages(self):
        # Add some example pages
        pages = [
            ("Manage Books", "Manage your library's book collection"),
            ("User Management", "Manage library users and permissions"),
            ("Borrow/Return", "Handle book checkouts and returns"),
            ("Reports", "View library statistics and reports"),
            ("Settings", "Configure application settings"),
            ("Help & Support", "Get help and support")
        ]
        
        for title, description in pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 10px;
            """)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                font-size: 14px;
                color: #666;
                margin-bottom: 20px;
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
