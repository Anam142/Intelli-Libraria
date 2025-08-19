from PyQt5 import QtCore, QtGui, QtWidgets

def get_icon(name):
    """Get an icon from the icons directory by name (without .svg extension)"""
    import os
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QPixmap, QIcon, QPainter
    from PyQt5.QtCore import Qt
    
    # Path to the icons directory
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
    icon_path = os.path.join(icons_dir, f"{name}.svg")
    
    if not os.path.exists(icon_path):
        print(f"Warning: Icon not found: {icon_path}")
        return QIcon()
    
    # Create a pixmap and render the SVG into it
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    
    renderer = QSvgRenderer(icon_path)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)

# Create shortcut functions for commonly used icons
def get_book_icon():
    return get_icon("book")

def get_home_icon():
    return get_icon("home")

def get_users_icon():
    return get_icon("users")

def get_refresh_icon():
    return get_icon("refresh-cw")

def get_file_text_icon():
    return get_icon("file-text")

def get_dollar_icon():
    return get_icon("dollar-sign")

def get_bell_icon():
    return get_icon("bell")

def get_calendar_icon():
    return get_icon("calendar")

def get_message_icon():
    return get_icon("message-square")

def get_user_icon():
    return get_icon("user")

def get_edit_icon():
    return get_icon("edit")

def get_trash_icon():
    return get_icon("trash")
