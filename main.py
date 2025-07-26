import sys
from PyQt5.QtWidgets import QApplication
from classic_splash import ClassicSplashScreen
from login_window import LoginWindow
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    def show_login():
        app.login = LoginWindow()
        app.login.showMaximized()
    splash = ClassicSplashScreen(on_finished_callback=show_login)
    splash.showFullScreen()
    sys.exit(app.exec_()) 

if __name__ == "__main__":
    main() 

    