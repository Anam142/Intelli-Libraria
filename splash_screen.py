import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QColor, QFont, QLinearGradient
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # Try to set background image
        bg_path = os.path.join('assets', 'splash_bg.jpg')
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            if not pixmap.isNull():
                # Scale pixmap to fit screen
                screen_rect = QApplication.primaryScreen().geometry()
                scaled_pixmap = pixmap.scaled(
                    screen_rect.width(), screen_rect.height(),
                    Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
                palette = QPalette()
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                self.setPalette(palette)
                self.setAutoFillBackground(True)
            else:
                self.set_gradient_background()
        else:
            self.set_gradient_background()

        # Centered label
        label = QLabel("Welcome to Intelli Libraria", self)
        label.setStyleSheet("color: white;")
        font = QFont()
        font.setPointSize(40)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)
        self.setLayout(layout)

        # QTimer to close after 5 seconds
        QTimer.singleShot(5000, self.close)

    def set_dark_blue_background(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0a3d62"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_gradient_background(self):
        # Soft sky-blue linear gradient fallback
        screen_rect = QApplication.primaryScreen().geometry()
        gradient = QLinearGradient(0, 0, 0, screen_rect.height())
        gradient.setColorAt(0, QColor("#dff3ff"))
        gradient.setColorAt(1, QColor("#a2d4f4"))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    sys.exit(app.exec_()) 