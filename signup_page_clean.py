import sys
import os
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QMessageBox,
                            QGraphicsBlurEffect, QMainWindow)
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPainterPath, QFont, QPalette, QBrush
from PyQt5.QtCore import Qt, QRectF

# Styling
PRIMARY = "#4A6CF7"
WHITE = "#FFFFFF"
TEXT = "#333333"
BORDER = "#E2E8F0"

class CardFrame(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255, 240))
        painter.setPen(Qt.NoPen)
        path = QPainterPath()
        path.addRoundedRect(QRectF(2, 2, self.width()-4, self.height()-4), 12, 12)
        painter.drawPath(path.simplified())

class SignupForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedSize(400, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Card background with reduced height
        self.card = CardFrame(self)
        self.card.setGeometry(0, 0, 400, 520)  # Reduced height from 600 to 520
        
        # Layout with reduced margins and spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)  # Reduced top and bottom margins
        layout.setSpacing(12)  # Reduced spacing between widgets
        
        # Title
        title = QLabel("Sign Up")
        title.setStyleSheet(f"font-size: 26px; font-weight: 600; color: {PRIMARY};")
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle with reduced bottom margin
        subtitle = QLabel("Create your account")
        subtitle.setStyleSheet(f"color: {TEXT}; font-size: 14px; opacity: 0.8; margin-bottom: 4px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Input fields
        fields = [
            ("username", "Username"),
            ("email", "Email"),
            ("password", "Password (min 8 characters)", True),
            ("phone", "Phone")
        ]
        
        for field in fields:
            name, placeholder = field[0], field[1]
            is_password = len(field) > 2 and field[2]
            
            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setEchoMode(QLineEdit.Password if is_password else QLineEdit.Normal)
            input_field.setStyleSheet(f"""
                QLineEdit {{
                    border: 1px solid {BORDER};
                    border-radius: 8px;
                    padding: 14px 16px;
                    font-size: 14px;
                    margin-bottom: 16px;
                    background: {WHITE};
                }}
                QLineEdit:focus {{
                    border: 2px solid {PRIMARY};
                    padding: 13px 15px;
                }}
            """)
            input_field.setMinimumHeight(48)
            setattr(self, f"{name}_input", input_field)
        
        # Sign Up button
        signup_btn = QPushButton("Sign Up")
        signup_btn.setFixedHeight(50)
        signup_btn.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                margin: 10px 0;
            }}
            QPushButton:hover {{ background: #3a5bd9; }}
        """)
        signup_btn.clicked.connect(self.handle_signup)
        
        # Login link removed as requested
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.phone_input)
        layout.addWidget(signup_btn)
        layout.addStretch()
    
    def handle_signup(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        phone = self.phone_input.text().strip()
        
        if not all([username, email, password, phone]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
            
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters!")
            return
        
        # Add user to database
        if self.add_user_to_database(username, email, password, phone):
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.handle_login()
    
    def add_user_to_database(self, username, email, password, phone):
        """Add a new user to the database."""
        print(f"Attempting to add user: {username}, {email}")
        conn = sqlite3.connect("intelli_libraria.db")
        try:
            cursor = conn.cursor()
            
            # Debug: Print all existing users
            cursor.execute("SELECT username, email FROM users")
            print("Existing users in database:")
            for user in cursor.fetchall():
                print(f"- {user[0]} ({user[1]})")
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            existing_user = cursor.fetchone()
            if existing_user is not None:
                print(f"User already exists: {existing_user}")
                QMessageBox.warning(self, "Error", "Username or email already exists!")
                return False
                
            # Insert new user
            print(f"Inserting new user: {username}, {email}")
            cursor.execute("""
                INSERT INTO users (username, email, password, phone, role, status)
                VALUES (?, ?, ?, ?, 'user', 'active')
            """, (username, email, password, phone))
            conn.commit()
            print("User added successfully!")
            
            # Verify the user was added
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            added_user = cursor.fetchone()
            print(f"Added user details: {added_user}")
            
            return True
            
        except sqlite3.Error as e:
            error_msg = f"Database error: {str(e)}"
            print(error_msg)
            QMessageBox.critical(self, "Database Error", error_msg)
            return False
        finally:
            if conn:
                conn.close()
    
    def handle_login(self):
        if self.parent:
            self.parent.show_login_page()

class SignupPage(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.bg_image = os.path.join("assets", "signup_bg.jpg")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sign Up - Intelli Libraria")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                          Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                          Qt.WindowCloseButtonHint)
        self.setFixedSize(1280, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Background
        self.bg_label = QLabel(central_widget)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        
        if os.path.exists(self.bg_image):
            pixmap = QPixmap(self.bg_image)
            self.bg_label.setPixmap(pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            ))
        else:
            self.bg_label.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a6cf7, stop:1 #3b5bdb);")
        
        # Ensure the background stays at the bottom of the stack
        self.bg_label.lower()
        
        # Form
        self.form = SignupForm(self)
        self.form.setParent(central_widget)
        self.center_form()
    
    def center_form(self):
        self.form.move(
            (self.width() - self.form.width()) // 2,
            (self.height() - self.form.height()) // 2
        )
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'bg_label'):
            # Update background size
            self.bg_label.setGeometry(0, 0, self.width(), self.height())
            
            # Update background image if it exists
            if hasattr(self, 'bg_image') and os.path.exists(self.bg_image):
                pixmap = QPixmap(self.bg_image)
                self.bg_label.setPixmap(pixmap.scaled(
                    self.size(), 
                    Qt.KeepAspectRatioByExpanding, 
                    Qt.SmoothTransformation
                ))
            
            # Keep background at the bottom of the stack
            self.bg_label.lower()
        
        # Center the form
        self.center_form()
    
    def show_login(self):
        if self.parent:
            self.parent.show_login()
            self.close()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SignupPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
