import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QFont, QCursor
from PyQt5.QtCore import Qt
import sqlite3
from dashboard_window import DashboardWindow

class RegistrationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register - Intelli Libraria")
        self.resize(600, 500)
        self.setMinimumSize(400, 400)
        # Center the window on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        reg_box = QFrame()
        reg_box.setFixedSize(400, 420)
        reg_box.setStyleSheet('''
            QFrame {
                background: white;
                border-radius: 18px;
            }
        ''')
        reg_box_layout = QVBoxLayout(reg_box)
        reg_box_layout.setContentsMargins(32, 32, 32, 32)
        reg_box_layout.setSpacing(22)

        title = QLabel("Register - Intelli Libraria")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #0a3d62;")
        reg_box_layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(38)
        reg_box_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(38)
        reg_box_layout.addWidget(self.password_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(38)
        reg_box_layout.addWidget(self.email_input)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact No")
        self.contact_input.setFixedHeight(38)
        reg_box_layout.addWidget(self.contact_input)

        signup_btn = QPushButton("Signup")
        signup_btn.setFixedHeight(38)
        signup_btn.setStyleSheet('''
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        ''')
        signup_btn.clicked.connect(self.signup_clicked)
        reg_box_layout.addWidget(signup_btn)

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(38)
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        ''')
        login_btn.clicked.connect(self.login_clicked)
        reg_box_layout.addWidget(login_btn)

        reg_box_layout.addStretch(1)
        hbox.addWidget(reg_box)
        hbox.addStretch(1)
        main_layout.addLayout(hbox)
        main_layout.addStretch(1)

    def signup_clicked(self):
        QMessageBox.information(self, "Signup", "Signup form submitted (not implemented)")

    def login_clicked(self):
        self.close()
        if self.parent() is not None:
            self.parent().show()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Intelli Libraria")
        self.resize(900, 700)
        self.setMinimumSize(600, 500)
        # Center the window on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Add background QLabel
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()  # Send to back
        self.bg_path = os.path.join('assets', 'login_bg.jpg')
        self.set_login_background()

        # Main layout to center the login box
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        # Login box
        login_box = QFrame()
        login_box.setFixedSize(450, 500)
        login_box.setStyleSheet('''
            QFrame {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
            }
        ''')
        login_box_layout = QVBoxLayout(login_box)
        login_box_layout.setContentsMargins(40, 40, 40, 40)
        login_box_layout.setSpacing(30)

        # Title
        title = QLabel("Admin Login")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #0a3d62;")
        login_box_layout.addWidget(title)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet('''
            QLineEdit {
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding-left: 14px;
                font-size: 16px;
                background: #f5f6fa;
            }
            QLineEdit:focus {
                border: 2px solid #0a3d62;
                background: #fff;
            }
        ''')
        login_box_layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet('''
            QLineEdit {
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding-left: 14px;
                font-size: 16px;
                background: #f5f6fa;
            }
            QLineEdit:focus {
                border: 2px solid #0a3d62;
                background: #fff;
            }
        ''')
        login_box_layout.addWidget(self.password_input)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.setFixedHeight(44)
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        ''')
        login_btn.clicked.connect(self.login_clicked)
        login_box_layout.addWidget(login_btn)

        # Signup button
        signup_btn = QPushButton("Signup")
        signup_btn.setCursor(QCursor(Qt.PointingHandCursor))
        signup_btn.setFixedHeight(44)
        signup_btn.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        ''')
        signup_btn.clicked.connect(self.signup_clicked)
        login_box_layout.addWidget(signup_btn)

        # Forgot password link
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setCursor(QCursor(Qt.PointingHandCursor))
        forgot_btn.setFlat(True)
        forgot_btn.setStyleSheet('''
            QPushButton {
                color: #1976d2;
                background: transparent;
                border: none;
                font-size: 15px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #0a3d62;
            }
        ''')
        login_box_layout.addWidget(forgot_btn, alignment=Qt.AlignCenter)

        login_box_layout.addStretch(1)

        hbox.addWidget(login_box)
        hbox.addStretch(1)
        main_layout.addLayout(hbox)
        main_layout.addStretch(1)

    def set_dark_gray_background(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#23272e"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_login_background(self):
        if os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.bg_label.setPixmap(scaled_pixmap)
                self.bg_label.setStyleSheet("")
                return
        # Fallback color if image missing
        self.bg_label.setPixmap(QPixmap())
        self.bg_label.setStyleSheet("background-color: #1e1e1e;")

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.set_login_background()
        super().resizeEvent(event)

    def login_clicked(self):
        from PyQt5.QtWidgets import QMessageBox
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password")
            return
        QMessageBox.information(self, "Login", "Login Successful")

    def signup_clicked(self):
        self.hide()
        self.signup_window = SignupWindow(login_window=self)
        self.signup_window.showMaximized()

class SignupWindow(QWidget):
    def __init__(self, login_window=None):
        super().__init__()
        self.login_window = login_window
        self.setWindowTitle("Signup - Intelli Libraria")
        self.resize(900, 700)
        self.setMinimumSize(600, 500)
        # Center the window on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # Add background QLabel
        self.bg_path = os.path.join('assets', 'signup_bg.jpg')
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()
        self.set_signup_background()
        self.initUI()

    def initUI(self):
        # Background color or image (modern look)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        signup_box = QFrame()
        signup_box.setFixedSize(450, 520)
        signup_box.setStyleSheet('''
            QFrame {
                background: white;
                border-radius: 20px;
            }
        ''')
        signup_box_layout = QVBoxLayout(signup_box)
        signup_box_layout.setContentsMargins(40, 40, 40, 40)
        signup_box_layout.setSpacing(28)

        title = QLabel("Signup Page")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #0a3d62;")
        signup_box_layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(44)
        signup_box_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        signup_box_layout.addWidget(self.password_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(44)
        signup_box_layout.addWidget(self.email_input)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact No")
        self.contact_input.setFixedHeight(44)
        signup_box_layout.addWidget(self.contact_input)

        signup_btn = QPushButton("Signup")
        signup_btn.setFixedHeight(44)
        signup_btn.setStyleSheet('''
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        ''')
        signup_btn.clicked.connect(self.signup_clicked)
        signup_box_layout.addWidget(signup_btn)

        login_btn = QPushButton("Login")
        login_btn.setFixedHeight(44)
        login_btn.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        ''')
        login_btn.clicked.connect(self.login_clicked)
        signup_box_layout.addWidget(login_btn)

        signup_box_layout.addStretch(1)
        hbox.addWidget(signup_box)
        hbox.addStretch(1)
        main_layout.addLayout(hbox)
        main_layout.addStretch(1)

    def set_signup_background(self):
        if os.path.exists(self.bg_path):
            pixmap = QPixmap(self.bg_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.bg_label.setPixmap(scaled_pixmap)
                self.bg_label.setStyleSheet("")
                return
        self.bg_label.setPixmap(QPixmap())
        self.bg_label.setStyleSheet("background-color: #1e1e1e;")

    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.set_signup_background()
        super().resizeEvent(event)

    def signup_clicked(self):
        from PyQt5.QtWidgets import QMessageBox
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        contact = self.contact_input.text().strip()

        if not username or not password or not email or not contact:
            QMessageBox.warning(self, "Signup Failed", "All fields are required.")
            return

        try:
            conn = sqlite3.connect("intelli_libraria.db")
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT NOT NULL,
                    contact_no TEXT NOT NULL
                )
            ''')
            c.execute("INSERT INTO users (username, password, email, contact_no) VALUES (?, ?, ?, ?)",
                      (username, password, email, contact))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Signup", "Signup successful!")
            self.close()
            self.dashboard = DashboardWindow()
            self.dashboard.showMaximized()
        except Exception as e:
            QMessageBox.critical(self, "Signup Failed", f"Error: {str(e)}")

    def login_clicked(self):
        self.close()
        if self.login_window is not None:
            self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    splash = SplashScreen(on_finished_callback=None)
    splash.show()

    def show_login():
        # Show login window first, then close splash
        login_window.showMaximized()
        splash.close()

    # Connect the splash finish to show_login
    splash.on_finished_callback = show_login

    sys.exit(app.exec_()) 