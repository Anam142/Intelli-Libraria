import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from classic_splash import ClassicSplashScreen
from login_window import LoginWindow
from dashboard_window import DashboardWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class Application(QObject):
    logout_requested = pyqtSignal()
    login_successful = pyqtSignal()

def main():
    if __name__ == "__main__":
        # Enable high DPI scaling
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application style and palette
    app.setStyle("Fusion")
    
    # Set high DPI scale factor (you can adjust this value as needed)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # Create application instance
    app_instance = Application()
    
    def show_login():
        # Close any existing windows
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                widget.close()
        
        # Create and show login window
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_candidate = os.path.join(base_dir, "assets", "login_bg.jpg")
        bg_path = bg_candidate if os.path.exists(bg_candidate) else "assets/login_bg.jpg"
        login_window = LoginWindow(bg_image_path=bg_path)
        # The window is already shown in its __init__ method
        
        def on_login_success():
            # When login is successful, show dashboard
            dashboard = DashboardWindow()
            dashboard.setWindowTitle("Intelli Libraria")
            dashboard.showMaximized()  # Show maximized with title bar
            login_window.close()
            
            # Connect logout signal
            def on_logout():
                print("on_logout() called in main.py")  # Debug
                dashboard.close()
                print("Dashboard closed, showing login")  # Debug
                show_login()
                
            # Find the logout button in the sidebar and connect it
            if hasattr(dashboard, 'sidebar'):
                # Connect the logout_requested signal from sidebar
                try:
                    dashboard.sidebar.logout_requested.disconnect()
                except:
                    pass
                dashboard.sidebar.logout_requested.connect(on_logout)
                
                # Also connect the logout button's menu action if it exists
                if hasattr(dashboard.sidebar, 'logout_btn'):
                    try:
                        dashboard.sidebar.logout_btn.clicked.disconnect()
                    except:
                        pass
                    # The menu action is already connected to logout() in the Sidebar class
        
        # Connect login success signal
        try:
            login_window.login_successful.disconnect()
        except:
            pass
        login_window.login_successful.connect(on_login_success)
    
    # Initial show of login screen
    splash = ClassicSplashScreen(on_finished_callback=show_login)
    splash.showFullScreen()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()