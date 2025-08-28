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
        
        # Back to Login link below the Sign Up button
        self.back_btn = QPushButton("Back to Login")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setFlat(True)
        self.back_btn.setStyleSheet(
            "QPushButton { color: #2563eb; background: transparent; border: none; font-size: 13px; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        self.back_btn.clicked.connect(self.handle_login)
        
        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.username_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.phone_input)
        layout.addWidget(signup_btn)
        layout.addWidget(self.back_btn, 0, Qt.AlignCenter)
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
        """Add a new user to the database.

        This implementation is schema-aware: it inspects the existing
        `users` table and dynamically includes columns such as
        `user_code`, `password_hash`, `role`, and `status` when present.
        """
        print(f"Attempting to add user: {username}, {email}")
        # Use centralized DB path
        try:
            from data.database import DB_PATH
        except Exception:
            import os as _os
            DB_PATH = _os.path.join(_os.path.dirname(__file__), 'intelli_libraria.db')
        conn = sqlite3.connect(DB_PATH)
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
                
            # Discover users table columns
            cursor.execute("PRAGMA table_info(users)")
            user_columns = {row[1] for row in cursor.fetchall()}

            # Generate a user code if supported
            import uuid as _uuid
            user_code = f"USR-{str(_uuid.uuid4())[:8].upper()}"

            # Hash password if a password_hash column exists
            hashed = None
            if 'password_hash' in user_columns:
                try:
                    from auth_utils import get_password_hash
                    hashed = get_password_hash(password)
                except Exception:
                    hashed = password

            # Determine allowed role/status values if checks exist
            allowed_roles = None
            allowed_statuses = None
            try:
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
                row = cursor.fetchone()
                ddl = row[0] if row and row[0] else ''
                import re as _re
                rm = _re.search(r"role\s+TEXT\s+CHECK\(\s*role\s+IN\s*\(([^\)]*)\)\)", ddl, _re.IGNORECASE)
                sm = _re.search(r"status\s+TEXT\s+CHECK\(\s*status\s+IN\s*\(([^\)]*)\)\)", ddl, _re.IGNORECASE)
                if rm:
                    allowed_roles = [v.strip().strip("'\"") for v in rm.group(1).split(',')]
                if sm:
                    allowed_statuses = [v.strip().strip("'\"") for v in sm.group(1).split(',')]
            except Exception:
                pass

            # Choose defaults compatible with the schema
            role_value = 'member'
            status_value = 'Active'
            if allowed_roles:
                role_value = next((r for r in allowed_roles if r.lower() == 'member'), allowed_roles[0])
            if allowed_statuses:
                # Prefer Active if present, else first allowed
                status_value = next((s for s in allowed_statuses if s.lower() == 'active'), allowed_statuses[0])

            # Build INSERT dynamically
            fields = []
            values = []
            def add(col, val):
                fields.append(col)
                values.append(val)

            if 'user_code' in user_columns:
                add('user_code', user_code)
            if 'username' in user_columns:
                add('username', username)
            if 'full_name' in user_columns and 'full_name' not in fields:
                # fallback: use username as full_name if required
                add('full_name', username)
            if 'email' in user_columns:
                add('email', email)
            if 'phone' in user_columns:
                add('phone', phone)
            if 'password_hash' in user_columns:
                add('password_hash', hashed or password)
            elif 'password' in user_columns:
                add('password', password)
            if 'role' in user_columns:
                add('role', role_value)
            if 'status' in user_columns:
                add('status', status_value)

            placeholders = ', '.join(['?'] * len(fields))
            sql = f"INSERT INTO users ({', '.join(fields)}) VALUES ({placeholders})"
            print(f"Inserting new user with fields: {fields}")
            cursor.execute(sql, tuple(values))
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
            # Delegate to the containing SignupPage, which routes back to LoginWindow
            self.parent.show_login()

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.bg_image = os.path.join("assets", "signup_bg.jpg")
        self.init_ui()
    
    def init_ui(self):
        self.setFixedSize(450, 500)  # Match the login card size
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Background
        self.bg_label = QLabel(self)
        
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
        layout.addWidget(self.form)
        
        # Connect back to login
        if hasattr(self.form, 'back_btn'):
            self.form.back_btn.clicked.connect(self.show_login)
    
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
    
    def show_login(self):
        if self.parent:
            # Call back into the login window to show the login form
            try:
                if hasattr(self.parent, 'show_login_page'):
                    self.parent.show_login_page()
                elif hasattr(self.parent, 'show_login'):
                    self.parent.show_login()
            finally:
                self.close()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SignupPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
