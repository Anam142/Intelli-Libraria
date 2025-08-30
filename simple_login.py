import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton)
from PyQt5.QtCore import Qt

class SimpleLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Login Test")
        self.setFixedSize(400, 300)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add widgets
        self.title = QLabel("Admin Login")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        
        # Add widgets to layout
        layout.addWidget(self.title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        
        # Set the layout
        self.setLayout(layout)
    
    def handle_login(self):
        print(f"Login attempt - Username: {self.username.text()}")

def main():
    app = QApplication(sys.argv)
    window = SimpleLogin()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
