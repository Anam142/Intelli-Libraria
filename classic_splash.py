import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

class ClassicSplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle("Intelli Libraria Splash")
        self.initUI()
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # 5 seconds for 0-100 (100 steps * 50ms = 5000ms)

    def initUI(self):
        # Set teal background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#00796B"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(0)

        # Title label
        title = QLabel("Welcome to Intelli Libraria", self)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addStretch(2)
        layout.addWidget(title)
        layout.addStretch(3)

        # Bottom area: Loading text and progress bar
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)

        loading_label = QLabel("Loading...", self)
        loading_label.setStyleSheet("color: white; font-size: 14px;")
        bottom_layout.addWidget(loading_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #004D40;
                border: 1px solid #004D40;
                border-radius: 8px;
            }
            QProgressBar::chunk {
                background-color: #B2DFDB;
                border-radius: 8px;
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
            QTimer.singleShot(300, self.close)  # Small delay for effect

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = ClassicSplashScreen()
    splash.show()
    sys.exit(app.exec_()) 