import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QMessageBox,
                            QGraphicsBlurEffect)
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
        
        # Create a path that only rounds the bottom corners
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        radius = 12.0
        
        # Start from top-left
        path.moveTo(rect.left(), rect.top())
        # Line to top-right (top edge remains straight)
        path.lineTo(rect.right(), rect.top())
        # Line to bottom-right (with curve)
        path.lineTo(rect.right(), rect.bottom() - radius)
        path.arcTo(rect.right() - 2*radius, rect.bottom() - 2*radius, 
                  2*radius, 2*radius, 0.0, 90.0)
        # Line to bottom-left (with curve)
        path.lineTo(rect.left() + radius, rect.bottom())
        path.arcTo(rect.left(), rect.bottom() - 2*radius, 
                  2*radius, 2*radius, 90.0, 90.0)
        # Close the path (back to top-left)
        path.closeSubpath()
        
        painter.setClipPath(path)
        painter.drawPath(path)

class SignupForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        # Set fixed size for the form
        self.setFixedSize(400, 650)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 30)
        main_layout.setSpacing(16)
        
        # Create a scroll area to ensure all content is accessible
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Create a container widget for the scroll area
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Title with improved styling
        title = QLabel("Create Account")
        title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 700;
            color: {PRIMARY};
            margin-bottom: 5px;
            font-family: 'Segoe UI', Arial, sans-serif;
            letter-spacing: 0.5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Subtitle with enhanced styling
        subtitle = QLabel("Join us and start your reading journey")
        subtitle.setStyleSheet(f"""
            color: #555555;
            font-size: 15px;
            font-weight: 400;
            margin-bottom: 25px;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        
        # Add some spacing
        title.setContentsMargins(0, 0, 0, 0)
        subtitle.setContentsMargins(0, 0, 0, 0)
        
        # Input fields
        fields = [
            ("full_name", "Full Name"),
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
        signup_btn = QPushButton("Back to Login")
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
        
        # Enhanced back to login button
        back_to_login_btn = QPushButton("Already have an account? Sign In")
        back_to_login_btn.setCursor(Qt.PointingHandCursor)
        back_to_login_btn.setStyleSheet(f"""
            QPushButton {{
                color: {PRIMARY};
                font-size: 14px;
                font-weight: 500;
                border: 1px solid {PRIMARY};
                background: transparent;
                padding: 10px 24px;
                margin: 15px 0 5px 0;
                text-align: center;
                text-decoration: none;
                border-radius: 6px;
                transition: all 0.2s ease;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton:hover {{
                color: white;
                background-color: {PRIMARY};
                text-decoration: none;
            }}
        """)
        back_to_login_btn.clicked.connect(self.handle_login)
        
        # Add widgets to layout with improved spacing
        layout.addSpacing(20)  # Add some top margin
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        # Add input fields with consistent spacing
        input_widgets = [
            self.full_name_input,
            self.username_input,
            self.email_input,
            self.password_input,
            self.phone_input
        ]
        
        for widget in input_widgets:
            layout.addWidget(widget)
            layout.addSpacing(8)  # Reduced spacing between fields
            
        # Add signup button with proper spacing
        layout.addSpacing(15)
        layout.addWidget(signup_btn)
        
        # Add the back to login button with some spacing
        layout.addSpacing(20)
        
        # Add the back to login button directly to the layout
        back_to_login_btn.setFixedWidth(200)  # Make the button wider
        layout.addWidget(back_to_login_btn, 0, Qt.AlignCenter)
        
        # Add the scroll area to the main layout
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Make sure everything is visible
        self.show()
        scroll.show()
        container.show()
        back_to_login_btn.show()
        back_to_login_btn.raise_()
    
    def handle_signup(self):
        import sqlite3
        import uuid
        from datetime import datetime
        from passlib.hash import bcrypt
        
        # Get form data
        full_name = self.full_name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        phone = self.phone_input.text().strip()
        
        # Validate required fields
        if not all([full_name, username, email, password, phone]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
            
        if len(password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters!")
            return
        
        try:
            # Generate a unique user code (e.g., USR-{timestamp}-{random})
            user_code = f"USR-{int(datetime.now().timestamp())}-{str(uuid.uuid4())[:6].upper()}"
            
            # Hash the password
            password_hash = bcrypt.hash(password)
            
            # Get database path
            try:
                from data.database import DB_PATH
            except Exception:
                import os as _os
                DB_PATH = _os.path.join(_os.path.dirname(__file__), 'intelli_libraria.db')
            
            # Connect to database and insert new user
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (user_code, username, full_name, email, phone, password_hash, role, status)
                VALUES (?, ?, ?, ?, ?, ?, 'member', 'Active')
            """, (user_code, username, full_name, email, phone, password_hash))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.handle_login()
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: users.username" in str(e):
                QMessageBox.warning(self, "Error", "Username already exists!")
            elif "UNIQUE constraint failed: users.email" in str(e):
                QMessageBox.warning(self, "Error", "Email already registered!")
            else:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create account: {str(e)}")
    
    def handle_login(self):
        if self.parent:
            self.parent.show_login_page()  # Updated method name

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.bg_image = os.path.join("assets", "signup_bg.jpg")
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Sign Up - Intelli Libraria")
        self.setFixedSize(1280, 800)
        
        # Create main widget and layout
        main_widget = QWidget(self)
        main_widget.setObjectName("mainWidget")
        main_widget.setGeometry(0, 0, 1280, 800)
        
        # Set the background image or color
        if os.path.exists(self.bg_image):
            main_widget.setStyleSheet(f"""
                #mainWidget {{
                    background-image: url({self.bg_image});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """)
        else:
            main_widget.setStyleSheet("background: #4A6CF7;")

        # Create form container
        form_container = QWidget(main_widget)
        form_container.setFixedSize(450, 650)
        form_container.setAttribute(Qt.WA_StyledBackground, True)
        form_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)

        # Create and add the signup form
        self.form = SignupForm()

        # Add form to container
        layout = QVBoxLayout(form_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.form)
        
        # Center the form container
        form_container.move(
            (self.width() - form_container.width()) // 2,
            (self.height() - form_container.height()) // 2
        )
        
        # Show everything
        main_widget.show()
        form_container.show()
        self.form.show()
        
        # Force update
        self.update()
        form_container.update()
        self.form.update()
    
    def center_form(self):
        # This is now handled in the resizeEvent
        pass
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Center the container
        if hasattr(self, 'form') and self.form.parent():
            container = self.form.parent()
            if container:
                container.move(
                    (self.width() - container.width()) // 2,
                    (self.height() - container.height()) // 2
                )
    
    def show_login(self):
        if self.parent:
            self.parent.show_login_page()  # Updated method name
            self.close()

def main():
    # Set high DPI scaling attributes before creating QApplication
    import os
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set high DPI scaling attributes
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Set application style and font
    app.setStyle('Times new rom')
    font = QFont("Inter", 10)
    app.setFont(font)
    
    try:
        window = SignupPage()
        window.show()
        return app.exec_()
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
