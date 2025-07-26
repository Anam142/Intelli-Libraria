from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, 
                            QFrame, QSizePolicy, QDialog, QMessageBox, QScrollArea,
                            QGraphicsDropShadowEffect, QSpacerItem, QComboBox, QStyledItemDelegate, 
                            QApplication, QStackedWidget, QGridLayout, QScrollArea, QSizeGrip)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QMargins, QRect, QPoint
from PyQt5.QtGui import (QFont, QColor, QIcon, QIntValidator, QPainter, 
                         QPalette, QLinearGradient, QPixmap, QFontDatabase)
import database
import sys
import random
import os

class BookCard(QFrame):
    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.book_data = book_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        self.setFixedSize(200, 320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Book cover (placeholder)
        cover = QLabel()
        cover.setFixedSize(168, 200)
        cover.setStyleSheet("""
            QLabel {
                background: #f1f5f9;
                border-radius: 8px;
            }
        """)
        
        # Title
        title = QLabel(self.book_data.get('title', 'Book Title'))
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
            }
        """)
        title.setWordWrap(True)
        
        # Author
        author = QLabel(f"by {self.book_data.get('author', 'Author')}")
        author.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #64748b;
            }
        """)
        
        # Price
        price = QLabel(self.book_data.get('price', '$0.00'))
        price.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #3b82f6;
            }
        """)
        
        layout.addWidget(cover)
        layout.addWidget(title)
        layout.addWidget(author)
        layout.addWidget(price)
        layout.addStretch()


class BookInventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Set window properties
        self.setWindowTitle("Book Inventory")
        self.setMinimumSize(1200, 800)
        
        # Load fonts
        self.load_fonts()
        
        # Main widget styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                background-color: #f8fafc;
            }
            QLabel {
                color: #1e293b;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 14px;
                border: none;
                cursor: pointer;
                transition: all 0.2s;
            }
            QLineEdit {
                padding: 10px 16px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                min-height: 40px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # Header section
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)
        
        # Page title
        title = QLabel("Book Inventory")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
            padding: 0;
        """)
        
        # Search bar container
        search_container = QFrame()
        search_container.setFixedHeight(44)
        search_container.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                min-width: 400px;
            }
        """)
        
        # Search bar layout
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(12)
        
        # Search icon
        search_icon = QLabel()
        search_icon.setPixmap(QPixmap("icons/search.svg").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                font-size: 14px;
                color: #1e293b;
                padding: 0;
                background: transparent;
                min-width: 300px;
            }
            QLineEdit:focus {
                outline: none;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
            }
        """)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        # Add Book button
        self.add_btn = QPushButton("Add Book")
        self.add_btn.setFixedSize(120, 44)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
        """)
        
        # Assemble header
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_container)
        header_layout.addWidget(self.add_btn)
        
        # Stats cards section
        stats_container = QWidget()
        stats_container.setStyleSheet("background: transparent;")
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 24)  # Add bottom margin
        stats_layout.setSpacing(16)
        
        # Stats data - Only Total Books and Available
        stats_data = [
            {
                "title": "Total Books",
                "value": "1,234",
                "icon": "books",
                "color": "#3b82f6",
                "bg_color": "#e0f2fe"
            },
            {
                "title": "Available",
                "value": "876",
                "icon": "check-circle",
                "color": "#10b981",
                "bg_color": "#d1fae5"
            }
        ]
        
        for stat in stats_data:
            card = QFrame()
            card.setFixedSize(280, 120)
            card.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                }}
            """)
            
            # Add shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 5))
            shadow.setOffset(0, 2)
            card.setGraphicsEffect(shadow)
            
            # Main layout
            layout = QVBoxLayout(card)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(12)
            
            # Top row with icon and title
            top_row = QWidget()
            top_row.setStyleSheet("background: transparent;")
            top_row_layout = QHBoxLayout(top_row)
            top_row_layout.setContentsMargins(0, 0, 0, 0)
            top_row_layout.setSpacing(8)
            
            # Icon with background
            icon_bg = QLabel()
            icon_bg.setFixedSize(40, 40)
            icon_bg.setStyleSheet(f"""
                QLabel {{
                    background: {stat['bg_color']};
                    border-radius: 8px;
                }}
            """)
            
            icon_layout = QHBoxLayout(icon_bg)
            icon = QLabel()
            icon.setPixmap(QPixmap(f"icons/{stat['icon']}.svg").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_layout.addWidget(icon, alignment=Qt.AlignCenter)
            
            # Title
            title = QLabel(stat["title"])
            title.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #64748b;
                    font-weight: 500;
                }
            """)
            
            top_row_layout.addWidget(icon_bg)
            top_row_layout.addWidget(title)
            top_row_layout.addStretch()
            
            # Value
            value = QLabel(stat["value"])
            value.setStyleSheet(f"""
                QLabel {{
                    font-size: 28px;
                    font-weight: 700;
                    color: {stat['color']};
                }}
            """)
            
            layout.addWidget(top_row)
            layout.addWidget(value)
            layout.addStretch()
            
            stats_layout.addWidget(card)
        
        # Add stretch to push cards to the left
        stats_layout.addStretch()
        
        # Table view
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table header
        table_header = QWidget()
        table_header_layout = QHBoxLayout(table_header)
        table_header_layout.setContentsMargins(0, 0, 0, 12)
        
        table_title = QLabel("Recent Books")
        table_title.setStyleSheet("font-size: 16px; font-weight: 600;")
        
        view_all_btn = QPushButton("View All")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #4299e1;
                padding: 4px 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        table_header_layout.addWidget(table_title)
        table_header_layout.addStretch()
        table_header_layout.addWidget(view_all_btn)
        
        # Table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(["BOOK TITLE", "AUTHOR", "CATEGORY", "STATUS", "ACTIONS"])
        self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setShowGrid(False)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setStyleSheet("""
            QTableWidget {
                border-radius: 8px;
                padding: 0;
                selection-background-color: #ebf8ff;
            }
            QTableWidget::item {
                padding: 16px;
                border-bottom: 1px solid #edf2f7;
            }
            QTableWidget::item:selected {
                background: #ebf8ff;
                color: inherit;
            }
        """)
        
        # Add sample data (replace with actual data from database)
        self.populate_sample_data()
        
        # Add widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(stats_container)
        main_layout.addWidget(table_container)
        table_layout.addWidget(table_header)
        table_layout.addWidget(self.books_table)
        
        # Connect signals
        self.add_btn.clicked.connect(self.show_add_book_form)
    
    def create_stat_card(self, title, value, icon_name, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                border: 1px solid #e2e8f0;
            }}
            QLabel#stat_value {{
                font-size: 24px;
                font-weight: 700;
                color: #1a202c;
                margin: 4px 0;
            }}
            QLabel#stat_title {{
                font-size: 14px;
                color: #718096;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Icon
        icon = QLabel()
        icon_pixmap = QPixmap(f":/icons/{icon_name}.svg")
        icon_pixmap = icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon.setPixmap(icon_pixmap)
        icon.setStyleSheet(f"color: {color};")
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("stat_value")
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("stat_title")
        
        layout.addWidget(icon)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        return card
        
    def load_fonts(self):
        # Load Inter font if available
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_path = os.path.join(font_dir, font_file)
                    QFontDatabase.addApplicationFont(font_path)
        
    def populate_books(self, books=None):
        # Clear existing books
        for i in reversed(range(self.books_layout.count())): 
            self.books_layout.itemAt(i).widget().setParent(None)
        
        # Use sample books if none provided
        books = books or self.sample_books
        
        # Add books to the grid
        row, col = 0, 0
        max_cols = 5  # Number of columns in the grid
        
        for book in books:
            book_card = BookCard(book, self)
            self.books_layout.addWidget(book_card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def search_books(self, text):
        if not text.strip():
            self.populate_books()
            return
            
        search_text = text.lower()
        filtered_books = [
            book for book in self.sample_books 
            if (search_text in book['title'].lower() or 
                search_text in book['author'].lower())
        ]
        self.populate_books(filtered_books)
    
    def show_add_book_form(self):
        # Create and show the add book form
        self.add_book_form = AddBookForm(self)
        self.add_book_form.book_added.connect(self.refresh_books)
        self.add_book_form.show()
    
    def refresh_books(self):
        # Refresh the book list
        # In a real app, you would fetch from the database here
        self.populate_books()
        
    def create_stat_card(self, title, value, icon_name, color):
        # Create a stat card widget
        card = QFrame()
        card.setFixedSize(200, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }}
            QLabel#value {{
                font-size: 28px;
                font-weight: 700;
                color: {color};
            }}
            QLabel#title {{
                font-size: 14px;
                color: #64748b;
                margin-top: 4px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon
        icon = QLabel()
        icon.setPixmap(QPixmap(f"icons/{icon_name}.svg").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value")
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("title")
        
        layout.addWidget(icon)
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 5))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        return card
        
        return card
    
    def populate_sample_data(self):
        # Sample data (replace with actual database query)
        books = [
            ["The Great Gatsby", "F. Scott Fitzgerald", "Classic", "Available"],
            ["To Kill a Mockingbird", "Harper Lee", "Fiction", "Borrowed"],
            ["1984", "George Orwell", "Dystopian", "Available"],
            ["Pride and Prejudice", "Jane Austen", "Romance", "Available"],
            ["The Hobbit", "J.R.R. Tolkien", "Fantasy", "Borrowed"]
        ]
        
        self.books_table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            for col, data in enumerate(book):
                item = QTableWidgetItem(data)
                if col == 3:  # Status column
                    if data == "Available":
                        item.setForeground(QColor("#48bb78"))
                    else:
                        item.setForeground(QColor("#e53e3e"))
                self.books_table.setItem(row, col, item)
            
            # Add action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(8)
            
            view_btn = QPushButton()
            view_btn.setIcon(QIcon(":/icons/eye.svg"))
            view_btn.setStyleSheet("""
                QPushButton {
                    background: #ebf8ff;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background: #bee3f8;
                }
            """)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon(":/icons/edit.svg"))
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #ebf8ff;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background: #bee3f8;
                }
            """)
            
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon(":/icons/trash-2.svg"))
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #fff5f5;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background: #fed7d7;
                }
                QPushButton::icon {
                    color: #f56565;
                }
            """)
            
            action_layout.addWidget(view_btn)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            self.books_table.setCellWidget(row, 4, action_widget)
        
        # Resize rows to fit content
        self.books_table.resizeRowsToContents()
    
    def show_add_book_form(self):
        self.add_book_form = AddBookForm(self)
        self.add_book_form.book_added.connect(self.refresh_books)
        self.add_book_form.show()
    
    def refresh_books(self):
        # Refresh the books table
        pass

class AddBookForm(QDialog):
    book_added = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setWindowTitle("Add New Book")
        self.setModal(True)
        
        # Set window to be full screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(screen.width(), screen.height())
        
        # Main widget and layout
        main_widget = QWidget()
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
        """)
        
        # Main layout with header, form, and buttons
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(0)
        
        # Header with title and close button
        header = QWidget()
        header.setStyleSheet("""
            background: transparent;
            padding: 0;
            margin: 0;
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        title = QLabel("Add New Book")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
            padding: 0;
        """)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: none;
                border-radius: 8px;
                color: #64748b;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        # Scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        """)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)
        
        # Setup form fields
        self.setup_form_fields(form_layout)
        
        # Set the form container as the scroll area's widget
        scroll.setWidget(form_container)
        
        # Buttons at the bottom
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(120, 44)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        save_btn = QPushButton("Save Book")
        save_btn.setFixedSize(200, 44)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:disabled {
                background: #bfdbfe;
            }
        """)
        save_btn.clicked.connect(self.add_book_action)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        # Add all widgets to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(scroll, 1)  # Takes remaining space
        main_layout.addWidget(button_container)
        
        # Set the main widget as the central widget
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(main_widget)
        
        # Center the window on the screen
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def setup_form_fields(self, layout):
        """Set up the form fields with proper styling."""
        # Form fields setup with proper styling
        fields = [
            ("Book ID", "id_input", "Enter book ID"),
            ("Title", "title_input", "Enter book title"),
            ("Author", "author_input", "Enter author name"),
            ("ISBN", "isbn_input", "Enter ISBN number"),
            ("Edition", "edition_input", "Enter edition number"),
            ("Stock", "stock_input", "Enter number of copies")
        ]
        
        for label_text, attr_name, placeholder in fields:
            # Create container for each field
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(8)
            
            # Field label
            label = QLabel(label_text)
            label.setStyleSheet("""
                font-size: 14px;
                font-weight: 600;
                color: #334155;
                margin: 0;
                padding: 0;
            """)
            
            # Create input field based on type
            if label_text == "Stock" or label_text == "Book ID":
                input_field = QLineEdit()
                input_field.setValidator(QIntValidator(1, 10000))
                if label_text == "Book ID":
                    # Auto-generate next available ID
                    input_field.setText(str(database.get_next_book_id()))
                    input_field.setReadOnly(True)
                    input_field.setStyleSheet("""
                        background: #f8fafc;
                        color: #64748b;
                    """)
            else:
                input_field = QLineEdit()
            
            # Common input field styling
            input_field.setPlaceholderText(placeholder)
            input_field.setFixedHeight(48)
            input_field.setStyleSheet("""
                QLineEdit {
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 14px;
                    color: #1e293b;
                }
                QLineEdit:focus {
                    border: 1px solid #3b82f6;
                    outline: none;
                }
                QLineEdit:disabled {
                    background: #f8fafc;
                }
            """)
            
            # Add label and input to container
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            
            # Add to layout
            layout.addWidget(field_container)
            
            # Save reference to the input field
            setattr(self, attr_name, input_field)
    
    def add_book_action(self):
        """Handle the save book button click."""
        try:
            book_id = int(self.id_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid Book ID.")
            return
            
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        edition = self.edition_input.text().strip()
        stock_text = self.stock_input.text().strip()

        # Validate required fields
        if not title or not author or not stock_text:
            QMessageBox.warning(self, "Input Error", "Title, Author, and Stock are required fields.")
            return

        # Validate stock is a positive number
        try:
            stock = int(stock_text)
            if stock < 0:
                raise ValueError("Stock cannot be negative")
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", "Stock must be a valid non-negative number.")
            return

        # Prepare book data
        book_data = {
            'id': book_id,
            'title': title,
            'author': author,
            'isbn': isbn,
            'edition': edition,
            'stock': stock
        }

        try:
            # Add book to database
            if database.add_book_with_id(book_id, title, author, isbn, edition, stock):
                QMessageBox.information(self, "Success", "Book added successfully!")
                self.book_added.emit()
                self.close()
            else:
                QMessageBox.warning(self, "Database Error", "Failed to add book. The ID might already be in use.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")