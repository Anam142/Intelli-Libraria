import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from login_window import LoginWindow
import sqlite3

def get_connection():
    return sqlite3.connect("library.db")

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Example: Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Add more tables for books, transactions, etc.
    conn.commit()
    conn.close()

class SplashScreen(QWidget):
    def __init__(self, on_finished_callback=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle("Intelli Libraria Splash")
        self.showFullScreen()
        self.on_finished_callback = on_finished_callback
        self.initUI()
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # 5 seconds for 0-100 (100 steps * 50ms = 5000ms)

    def initUI(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#00796B"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 100, 100, 60)
        layout.setSpacing(0)

        title = QLabel("Welcome to Intelli Libraria", self)
        title_font = QFont()
        title_font.setPointSize(40)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addStretch(2)
        layout.addWidget(title)
        layout.addStretch(3)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(20)

        loading_label = QLabel("Loading...", self)
        loading_label.setStyleSheet("color: white; font-size: 22px;")
        bottom_layout.addWidget(loading_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #004D40;
                border: 1px solid #004D40;
                border-radius: 15px;
            }
            QProgressBar::chunk {
                background-color: #B2DFDB;
                border-radius: 15px;
            }
        ''')
        bottom_layout.addWidget(self.progress_bar, stretch=1)

        layout.addLayout(bottom_layout)

    def update_progress(self):
        self.progress += 2
        if self.progress > 100:
            self.progress = 100
        self.progress_bar.setValue(self.progress)
        if self.progress >= 100:
            self.timer.stop()
            QTimer.singleShot(300, self.finish)

    def finish(self):
        self.close()
        if self.on_finished_callback:
            self.on_finished_callback()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    def show_login():
        login_window.showMaximized()
        app.processEvents()
        splash.close()
    splash = SplashScreen(on_finished_callback=show_login)
    splash.show()
    sys.exit(app.exec_()) 