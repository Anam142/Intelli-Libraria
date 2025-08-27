from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, 
                           QFrame, QSizePolicy, QDialog, QMessageBox, QScrollArea,
                            QGraphicsDropShadowEffect, QSpacerItem, QComboBox, QStyledItemDelegate, 
                            QApplication, QStackedWidget, QGridLayout, QSizeGrip, QTabWidget, 
                            QTextEdit, QSpinBox, QDialogButtonBox, QStyle)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QMargins, QRect, QPoint, QTimer
from PyQt5.QtGui import QFont, QColor, QIntValidator, QPainter, QPalette, QPixmap, QFontDatabase
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
        # Load books after the widget is constructed (next event loop cycle)
        QTimer.singleShot(0, self.load_books)

    def showEvent(self, event):
        """Ensure books are refreshed whenever the page becomes visible."""
        try:
            self.load_books()
        finally:
            return super().showEvent(event)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Header section
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Book Inventory")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
            margin: 0;
            padding: 0;
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add Book button
        self.add_book_btn = QPushButton("Add Book")
        self.add_book_btn.clicked.connect(self.add_book_action)
        self.add_book_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                margin-right: 12px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        self.add_book_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.add_book_btn)
        
        # Search bar
        search_container = QWidget()
        search_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 2px;
                border: 1px solid #e2e8f0;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 4, 12, 4)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 6px 0;
                font-size: 14px;
                background: transparent;
                color: #1e293b;
                min-width: 300px;
            }
            QLineEdit:focus {
                outline: none;
            }
        """)
        self.search_input.textChanged.connect(self.search_books)
        
        search_layout.addWidget(self.search_input)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 16px;
                color: #6b7280;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #4f46e5;
                border-bottom: 2px solid #4f46e5;
            }
        """)
        
        # All Books tab
        all_books_tab = QWidget()
        tab_layout = QVBoxLayout(all_books_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table for books
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(7)
        self.books_table.setHorizontalHeaderLabels(["ID", "Title", "Author", "ISBN", "Edition", "Stock", "Actions"])
        
        # Set column widths - ID and Actions columns have fixed width, others will stretch
        self.books_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        self.books_table.setColumnWidth(0, 50)   # ID column
        self.books_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)  # Actions
        self.books_table.setColumnWidth(6, 160)  # Actions column
        
        # Make other columns stretch to fill available space
        for col in [1, 2, 3, 4, 5]:  # Title, Author, ISBN, Edition, Stock
            self.books_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setShowGrid(False)
        self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: white;
                gridline-color: #f3f4f6;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                padding: 12px 16px;
                border: none;
                font-weight: 600;
                color: #4b5563;
                border-bottom: 1px solid #e5e7eb;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #e0e7ff;
                color: #1e40af;
            }
        """)
        
        # Set up table properties
        self.books_table.setWordWrap(False)
        self.books_table.setTextElideMode(Qt.ElideRight)
        self.books_table.setSortingEnabled(True)
        self.books_table.setShowGrid(False)
        
        # Set header properties
        header = self.books_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        
        # Set column resize modes
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID column
        self.books_table.setColumnWidth(0, 50)
        
        # Set Actions column to fixed width
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.books_table.setColumnWidth(6, 180)  # Width for action buttons
        
        # Make other columns stretch
        for col in range(1, 6):  # Title, Author, ISBN, Edition, Stock
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        
        # Set fixed row height
        self.books_table.verticalHeader().setDefaultSectionSize(48)
        self.books_table.verticalHeader().setVisible(False)
        
        # Apply consistent styling
        self.books_table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                gridline-color: #e5e7eb;
                outline: none;
            }
            QTableWidget::item {
                padding: 12px 16px;
                border: none;
                border-right: 1px solid #e5e7eb;
                border-bottom: 1px solid #e5e7eb;
                color: #1f2937;
            }
            QTableWidget::item:first {
                border-left: 1px solid #e5e7eb;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 12px 16px;
                border: none;
                border-right: 1px solid #d1d5db;
                border-bottom: 2px solid #d1d5db;
                font-weight: 600;
                color: #374151;
                text-align: left;
            }
            QHeaderView::section:first {
                border-left: 1px solid #d1d5db;
            }
            QTableWidget::item:selected {
                background-color: #e0e7ff;
                color: #1e40af;
            }
        """)
        
        tab_layout.addWidget(self.books_table)
        
        # Add tabs
        self.tabs.addTab(all_books_tab, "All Books")
        
        # Add widgets to main layout
        main_layout.addWidget(header_widget)
        main_layout.addWidget(search_container)
        main_layout.addWidget(self.tabs, 1)  # 1 is stretch factor to make it take remaining space
        
        # Set the main layout
        self.setLayout(main_layout)
        
    def add_book_action(self):
        """Handle the add book button click."""
        dialog = AddBookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            book_data = dialog.get_book_data()
            
            # Validate required fields
            if not book_data['title'] or not book_data['author']:
                QMessageBox.warning(self, "Input Error", "Title and Author are required fields.")
                return
                
            try:
                # Add book to database
                if database.add_book(
                    book_data['title'],
                    book_data['author'],
                    book_data['isbn'],
                    book_data['edition'],
                    book_data['stock']
                ):
                    QMessageBox.information(self, "Success", "Book added successfully!")
                    self.load_books()
                    # Notify dashboard to refresh total book count if available
                    try:
                        main = self.window()
                        if hasattr(main, 'refresh_total_books'):
                            main.refresh_total_books()
                    except Exception:
                        pass
                else:
                    QMessageBox.warning(self, "Database Error", "Failed to add book. The ISBN might already be in use.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
    
    def load_fonts(self):
        # Load Inter font if available
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(('.ttf', '.otf')):
                    font_path = os.path.join(font_dir, font_file)
                    QFontDatabase.addApplicationFont(font_path)
        
    def populate_books(self, books=None):
        """Populate the books table with the provided list of books.
        
        Args:
            books (list, optional): List of book tuples. If None, fetches all books.
        """
        try:
            # Clear existing rows
            self.books_table.setRowCount(0)
            
            if books is None:
                books = database.get_all_books()
            
            if not books:
                # Show an empty table without interrupting the user
                self.books_table.setRowCount(0)
                return
            
            print(f"Found {len(books)} books to display")
            
            # Set row count
            self.books_table.setRowCount(len(books))

            # Avoid layout glitches while inserting (sorting moves rows during setItem)
            prev_sorting = self.books_table.isSortingEnabled()
            self.books_table.setSortingEnabled(False)

            # Populate table (supports tuple rows and dict rows)
            for row, book in enumerate(books):
                try:
                    # Normalize row to fields
                    if isinstance(book, dict):
                        bid = book.get('id')
                        title_val = book.get('title', '') or ''
                        author_val = book.get('author', '') or ''
                        isbn_val = book.get('isbn', '') or ''
                        edition_val = book.get('edition') if 'edition' in book else book.get('publication_year')
                        stock_val = book.get('stock') if 'stock' in book else book.get('quantity', 0)
                    else:
                        # Assume positional tuple: id, title, author, isbn, edition, stock, ...
                        bid = book[0] if len(book) > 0 else ''
                        title_val = book[1] if len(book) > 1 else ''
                        author_val = book[2] if len(book) > 2 else ''
                        isbn_val = book[3] if len(book) > 3 else ''
                        edition_val = book[4] if len(book) > 4 else None
                        stock_val = book[5] if len(book) > 5 else 0

                    edition_val = edition_val if edition_val is not None else 'N/A'
                    stock_val = stock_val if stock_val is not None else 0

                    # Create items for each column
                    id_item = QTableWidgetItem(str(bid))
                    title_item = QTableWidgetItem(str(title_val))
                    author_item = QTableWidgetItem(str(author_val))
                    isbn_item = QTableWidgetItem(str(isbn_val))
                    edition_item = QTableWidgetItem(str(edition_val))
                    stock_item = QTableWidgetItem(str(stock_val))
                    
                    # Set items in the table
                    self.books_table.setItem(row, 0, id_item)
                    self.books_table.setItem(row, 1, title_item)
                    self.books_table.setItem(row, 2, author_item)
                    self.books_table.setItem(row, 3, isbn_item)
                    self.books_table.setItem(row, 4, edition_item)
                    self.books_table.setItem(row, 5, stock_item)
                    
                    # Add action buttons
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)
                    action_layout.setSpacing(5)
                    
                    # Edit button
                    edit_btn = QPushButton("Edit")
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 4px;
                            min-width: 60px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
                    edit_btn.clicked.connect(lambda _, bid=bid: self.edit_book(bid))
                    
                    # Delete button
                    delete_btn = QPushButton("Delete")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            padding: 4px 8px;
                            border-radius: 4px;
                            min-width: 60px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                    delete_btn.clicked.connect(lambda _, bid=bid: self.delete_book(bid))
                    
                    action_layout.addWidget(edit_btn)
                    action_layout.addWidget(delete_btn)
                    action_widget.setLayout(action_layout)
                    
                    self.books_table.setCellWidget(row, 6, action_widget)
                    
                    # Center align all cells
                    for col in range(self.books_table.columnCount() - 1):
                        item = self.books_table.item(row, col)
                        if item:
                            item.setTextAlignment(Qt.AlignCenter)
                except Exception as e:
                    print(f"Error processing book {book}: {str(e)}")
            
            # Restore sorting and re-apply stretch so the table keeps full width
            self.books_table.setSortingEnabled(prev_sorting)
            self.books_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
            print(f"Error in populate_books: {str(e)}")
            import traceback
            traceback.print_exc()

    def search_books(self, text):
        if not text.strip():
            self.load_books()
            return

        search_text = f"%{text.lower()}%"
        try:
            # First try searching with LIKE for partial matches
            query = """
                SELECT * FROM books 
                WHERE LOWER(title) LIKE ? 
                   OR LOWER(author) LIKE ?
                ORDER BY title
            """
            books = database.execute_query(query, (search_text, search_text))

            if not books:  # If no results, try a more flexible search
                query = """
                    SELECT * FROM books 
                    WHERE LOWER(title) LIKE ? 
                       OR LOWER(author) LIKE ?
                       OR LOWER(edition) LIKE ?
                       OR LOWER(isbn) LIKE ?
                    ORDER BY title
                """
                books = database.execute_query(query, 
                    (search_text, search_text, search_text, search_text))
            
            if books:
                self.populate_books(books)
            else:
                QMessageBox.information(self, "No Results", "No books found matching your search.")
                self.load_books()
                
        except Exception as e:
            print(f"Error searching books: {str(e)}")
            # Try to get more detailed error information
            try:
                import traceback
                error_details = traceback.format_exc()
                print(f"Full error details: {error_details}")
                
                # Check if database is accessible
                conn = database.create_connection()
                if conn is None:
                    QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
                else:
                    conn.close()
                    QMessageBox.critical(self, "Search Error", 
                        f"An error occurred while searching: {str(e)}\n\nPlease try again.")
            except Exception as inner_e:
                print(f"Error getting error details: {inner_e}")
                QMessageBox.critical(self, "Error", "An unknown error occurred.")
            
            self.load_books()  # Fallback to loading all books on error
    
    
    def load_books(self):
        """Load all books from the database and populate the table."""
        try:
            books = database.get_all_books()
            if not books:
                # Keep the table empty silently when there are no books
                self.books_table.setRowCount(0)
                return
            self.populate_books(books)
        except Exception as e:
            print(f"Error loading books: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
            self.books_table.setRowCount(0)
    
    def edit_book(self, book_id):
        """Handle edit book button click."""
        try:
            # Get book data from database
            conn = database.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            book = cursor.fetchone()
            
            if not book:
                QMessageBox.warning(self, "Error", "Book not found!")
                return
                
            # Show the edit dialog with book data
            dialog = AddBookDialog(self)
            dialog.setWindowTitle("Edit Book")
            
            # Fill the form with existing book data (book is a tuple: id, title, author, isbn, edition, stock)
            dialog.title_input.setText(book[1] if len(book) > 1 else '')  # title
            dialog.author_input.setText(book[2] if len(book) > 2 else '')  # author
            dialog.isbn_input.setText(book[3] if len(book) > 3 else '')  # isbn
            dialog.edition_input.setText(book[4] if len(book) > 4 else '')  # edition
            dialog.stock_input.setValue(int(book[5]) if len(book) > 5 else 0)  # stock
            
            if dialog.exec_() == QDialog.Accepted:
                # Update book in database
                book_data = dialog.get_book_data()
                if database.update_book(
                    book_id,
                    book_data['title'],
                    book_data['author'],
                    book_data['isbn'],
                    book_data['edition'],
                    book_data['stock']
                ):
                    QMessageBox.information(self, "Success", "Book updated successfully!")
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update book.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
                
    def delete_book(self, book_id):
        """Handle delete book button click."""
        try:
            # Ask for confirmation
            reply = QMessageBox.question(
                self, 
                'Delete Book',
                'Are you sure you want to delete this book?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if database.delete_book(book_id):
                    QMessageBox.information(self, "Success", "Book deleted successfully!")
                    self.load_books()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete book.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        
    def delete_book_action(self):
        """Handle delete book button click."""
        button = self.sender()
        if not button:
            return
                
        book_id = button.property('book_id')
        if not book_id:
            return
                
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            'Delete Book',
            'Are you sure you want to delete this book?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
            
        if reply == QMessageBox.Yes:
            try:
                if database.delete_book(book_id):
                    QMessageBox.information(self, "Success", "Book deleted successfully!")
                    self.load_books()  # Refresh the book list
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete book.")
            except Exception as e:
                print(f"Error deleting book: {e}")
                QMessageBox.critical(self, "Error", "An error occurred while deleting the book.")
            
            # Action buttons
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            edit_btn.clicked.connect(lambda _, bid=book_id: self.edit_book(bid))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            delete_btn.clicked.connect(lambda _, bid=book_id: self.delete_book(bid))
            
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addStretch()
            
            self.books_table.setCellWidget(row, 6, btn_widget)
            
            # Set row height
            self.books_table.setRowHeight(row, 60)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)
        
        # Add form title
        form_title = QLabel("Book Information")
        form_title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 8px;
        """)
        form_layout.addWidget(form_title)
        
        # Add form description
        form_desc = QLabel("Please fill in the book details below")
        form_desc.setStyleSheet("""
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 24px;
        """)
        form_layout.addWidget(form_desc)
        
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("border: 1px solid #e5e7eb;")
        form_layout.addWidget(line)
        
        # Add form fields
        self.setup_form_fields(form_layout)
        
        # Add stretch to push content to top
        form_layout.addStretch()
        
        # Add a bottom container for buttons with a top border
        bottom_container = QWidget()
        bottom_container.setStyleSheet("""
            QWidget {
                background: white;
                border-top: 1px solid #e5e7eb;
                padding: 16px 0 0 0;
            }
        """)
        
        # Create buttons layout
        button_layout = QHBoxLayout(bottom_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(self.reject)
        
        # Save button
        save_btn = QPushButton("Add Book")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.add_book_action)
        
        # Add buttons to layout
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        # Add bottom container to form
        form_layout.addWidget(bottom_container)
        
        # Set the form container as the scroll area's widget
        scroll.setWidget(form_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll, 1)  # Make scroll area take remaining space
        
        # Connect the cancel button
        cancel_btn.clicked.connect(self.reject)
        
        # Save button
        save_btn = QPushButton("Add Book")
        save_btn.setFixedSize(200, 44)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
            QPushButton:disabled {
                background-color: #c7d2fe;
            }
        """)
        save_btn.clicked.connect(self.save_book)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        # Add bottom container to main layout
        main_layout = self.layout()
        main_layout.addWidget(bottom_container)  # Add bottom container at the bottom
        
        # Set minimum size for better usability
        self.setMinimumSize(800, 600)
        
        # Connect signals
        self.finished.connect(self.on_dialog_closed)
        
    def load_book_data(self):
        """Load book data if in edit mode"""
        if not self.book_id:
            return
            
        # TODO: Load book data from database
        book_data = database.get_book_by_id(self.book_id)
        if book_data:
            self.id_input.setText(str(book_data['id']))
            self.title_input.setText(book_data['title'])
            self.author_input.setText(book_data['author'])
            self.isbn_input.setText(book_data['isbn'])
            self.edition_input.setText(book_data['edition'])
            self.stock_input.setValue(int(book_data['stock']))
            
            # Set category if it exists in the book data
            if 'category' in book_data:
                index = self.category_combo.findText(book_data['category'])
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
    
    def save_book(self):
        """Save book data to database"""
        try:
            # Get values from form
            book_data = {
                'id': int(self.id_input.text().strip()) if self.id_input.text().strip() else None,
                'title': self.title_input.text().strip(),
                'author': self.author_input.text().strip(),
                'isbn': self.isbn_input.text().strip(),
                'edition': self.edition_input.text().strip(),
                'stock': self.stock_input.value(),
            }
            
            # Validate required fields
            if not book_data['title'] or not book_data['author']:
                QMessageBox.warning(self, "Validation Error", "Title and Author are required fields.")
                return
                
            if book_data['stock'] < 0:
                QMessageBox.warning(self, "Validation Error", "Stock cannot be negative.")
                return
            
            # Save to database
            if self.book_id:
                # Update existing book
                if database.update_book(book_data):
                    QMessageBox.information(self, "Success", "Book updated successfully!")
                    self.book_added.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update book.")
            else:
                # Add new book
                if database.add_book(
                    book_data['title'],
                    book_data['author'],
                    book_data['isbn'],
                    book_data['edition'],
                    book_data['stock'],                 
                ):
                    QMessageBox.information(self, "Success", "Book added successfully!")
                    self.book_added.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add book. The ISBN might already exist.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def on_dialog_closed(self):
        """Handle dialog close event"""
        self.dialog_closed.emit()

    def setup_form_fields(self, form_layout):
        """Set up the form fields with proper styling."""
        # Form fields setup with proper styling
        fields = [
            ("Book ID", "id_input", "Enter book ID"),
            ("Title", "title_input", "Enter book title"),
            ("Author(s)", "author_input", "Enter author name"),
            ("ISBN", "isbn_input", "Enter ISBN number"),
            ("Edition", "edition_input", "Enter edition number"),
            ("Stock Count", "stock_input", "Enter number of copies")
        ]
        
        for label_text, attr_name, placeholder in fields:
            # Create container for label and input field
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(8)
            
            # Create label
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 500;
                    color: #475569;
                }
            """)
            
            # Create input field based on type
            if attr_name == 'stock_input':
                input_field = QSpinBox()
                input_field.setMinimum(0)
                input_field.setMaximum(9999)
                input_field.setFixedHeight(44)
            elif attr_name == 'edition_input':
                input_field = QLineEdit()
                input_field.setPlaceholderText(placeholder)
                input_field.setFixedHeight(44)
                input_field.setValidator(QIntValidator())
            else:
                input_field = QLineEdit()
                input_field.setPlaceholderText(placeholder)
                input_field.setFixedHeight(44)
                
                # Set input validation for numeric fields
                if attr_name == 'id_input':
                    input_field.setValidator(QIntValidator())
            
            # Style the input field
            input_field.setStyleSheet("""
                QLineEdit, QSpinBox {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 0 16px;
                    font-size: 14px;
                    color: #1e293b;
                    background: #ffffff;
                }
                QLineEdit:focus, QSpinBox:focus {
                    border: 1px solid #4f46e5;
                    outline: none;
                }
                QLineEdit:disabled, QSpinBox:disabled {
                    background: #f8fafc;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    width: 20px;
                    border: none;
                    background: #f1f5f9;
                    border-radius: 4px;
                    margin: 2px;
                }
                QSpinBox::up-arrow, QSpinBox::down-arrow {
                    width: 10px;
                    height: 10px;
                }
            """)
            
            # Auto-generate book ID
            if label_text == "Book ID":
                input_field.setText(str(database.get_next_book_id()))
                input_field.setReadOnly(True)
                input_field.setStyleSheet(input_field.styleSheet() + """
                    QLineEdit {
                        background: #f8fafc;
                        color: #94a3b8;
                    }
                """)
            
            # Add label and input field to container
            field_layout.addWidget(label)
            field_layout.addWidget(input_field)
            
            # Add to form layout
            form_layout.addWidget(field_container)
            
            # Save reference to the input field
            setattr(self, attr_name, input_field)
    
class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Book")
        self.setWindowModality(Qt.ApplicationModal)
        
        # Set window flags to remove context help button and add minimize/maximize buttons
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set window to full screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        self.showMaximized()
        
        # Store references to widgets that need to persist
        self.scroll = None
        self.container = None
        self.form_container = None
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        # Clear any existing layout
        if self.layout():
            QWidget().setLayout(self.layout())
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        try:
            # Create a scroll area
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            # Create a container widget for the scroll area
            self.container = QWidget()
            container_layout = QVBoxLayout(self.container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(0)
            
            # Title label with top margin
            title = QLabel("Add New Book")
            title.setStyleSheet("""
                font-size: 24px;
                font-weight: 600;
                color: #1a1a1a;
                padding: 25px 0 15px 0;
                margin-left: 30px;
            """)
            container_layout.addWidget(title, 0, Qt.AlignLeft | Qt.AlignTop)
            
            # Form container
            self.form_container = QWidget()
            self.form_container.setStyleSheet("background-color: #f8fafc;")
            
            form_layout = QVBoxLayout(self.form_container)
            form_layout.setContentsMargins(30, 30, 30, 30)
            form_layout.setSpacing(25)
            
            # Form fields
            fields = [
                ("Book ID", "Book ID will be auto-generated"),
                ("Title", "Enter book title"),
                ("Author", "Enter author name"),
                ("ISBN", "Enter ISBN number"),
                ("Edition", "e.g. First Edition, 2023"),
                ("Stock", "Enter available quantity"),
            ]
            
            self.inputs = {}
            
            for i, (label_text, placeholder) in enumerate(fields):
                label = QLabel(label_text)
                label.setStyleSheet("""
                    font-size: 14px;
                    font-weight: 500;
                    color: #475569;
                    margin-bottom: 5px;
                """)
                
                # Create input field based on type
                if label_text == "Stock":
                    input_field = QSpinBox()
                    input_field.setMinimum(0)
                    input_field.setMaximum(1000)
                    input_field.setValue(1)
                elif label_text == "Book ID":
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(placeholder)
                    input_field.setReadOnly(True)
                    input_field.setStyleSheet("""
                        QLineEdit {
                            background: #f8fafc;
                            color: #94a3b8;
                        }
                    """)
                    input_field.setText(str(database.get_next_book_id()))
                else:
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(placeholder)
                
                # Set common styles for input fields
                input_field.setFixedHeight(45)
                input_field.setStyleSheet("""
                    QLineEdit, QSpinBox {
                        padding: 0 15px;
                        font-size: 14px;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        background-color: white;
                    }
                    QLineEdit:focus, QSpinBox:focus {
                        border: 1px solid #4f46e5;
                        outline: none;
                    }
                """)
                
                # Add to form layout
                form_layout.addWidget(label)
                form_layout.addWidget(input_field)
                
                # Store reference in inputs dictionary using lowercase key
                field_key = label_text.lower().replace(' ', '_')
                self.inputs[field_key] = input_field
            
            # Add buttons container
            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            button_layout.setContentsMargins(0, 20, 0, 0)
            button_layout.setSpacing(15)
            
            # Cancel button
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setFixedSize(120, 45)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1f5f9;
                    color: #64748b;
                    border: 1px solid #cbd5e1;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
                QPushButton:pressed {
                    background-color: #cbd5e1;
                }
            """)
            cancel_btn.clicked.connect(self.reject)
            
            # Save button
            save_btn = QPushButton("Save")
            save_btn.setFixedSize(120, 45)
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4f46e5;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4338ca;
                }
                QPushButton:pressed {
                    background-color: #3730a3;
                }
                QPushButton:disabled {
                    background-color: #c7d2fe;
                }
            """)
            save_btn.clicked.connect(self.accept)
            
            button_layout.addStretch()
            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(save_btn)
            
            form_layout.addWidget(button_container)
            
            # Add form container to container layout
            container_layout.addWidget(self.form_container)
            
            # Set container as the scroll area's widget
            self.scroll.setWidget(self.container)
            
            # Add scroll area to main layout
            main_layout.addWidget(self.scroll)
            
            # Store references to input fields
            self.title_input = self.inputs['title']
            self.author_input = self.inputs['author']
            self.isbn_input = self.inputs['isbn']
            self.edition_input = self.inputs['edition']
            self.stock_input = self.inputs['stock']
            
        except Exception as e:
            print(f"Error initializing UI: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize dialog: {str(e)}")
            self.reject()
    
    def closeEvent(self, event):
        # Clean up resources
        if hasattr(self, 'scroll') and self.scroll:
            self.scroll.setParent(None)
            self.scroll.deleteLater()
        super().closeEvent(event)
    
    def get_book_data(self):
        """Return the book data entered in the form."""
        return {
            'title': self.title_input.text().strip(),
            'author': self.author_input.text().strip(),
            'isbn': self.isbn_input.text().strip(),
            'edition': self.edition_input.text().strip(),
            'stock': self.stock_input.value()
        }