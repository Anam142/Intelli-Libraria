import sqlite3
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QSizePolicy, QTabWidget, QMessageBox, QVBoxLayout,
                            QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QImage, QPixmap
import cv2
try:
    from pyzbar.pyzbar import decode as zbar_decode
    PYZBAR_AVAILABLE = True
except Exception as _zbar_err:
    PYZBAR_AVAILABLE = False
    ZBAR_IMPORT_ERROR = _zbar_err
import numpy as np
import database
from library_backend import LibraryBackend

class BorrowBookScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borrow Book")
        self.setStyleSheet("background-color: #ffffff;")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Borrow Book")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #000000; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-bottom: 5px;")
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter User ID")
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(user_id_label)
        layout.addWidget(self.user_id_input)

        # Book ID
        book_id_label = QLabel("Book ID")
        book_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter Book ID")
        self.book_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_id_input)

        layout.addStretch()

        # Borrow Button
        self.borrow_button = QPushButton("Borrow Book")
        self.borrow_button.setCursor(Qt.PointingHandCursor)
        self.borrow_button.clicked.connect(self.borrow_book_action)
        self.borrow_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.borrow_button)
        layout.addLayout(button_layout)

    def borrow_book_action(self):
        user_id = self.user_id_input.text().strip()
        book_id = self.book_id_input.text().strip()
        
        # Input validation
        if not user_id or not book_id:
            QMessageBox.warning(self, "Missing Information", 
                             "Please enter both User ID and Book ID.")
            return
            
        try:
            # Initialize the borrow service
            from services.borrow_service import BorrowService
            borrow_service = BorrowService()
            
            # Try to borrow the book
            success, message = borrow_service.borrow_book(user_id, book_id)
            
            # Always show the message to the user
            msg_box = QMessageBox(self)
            
            if success:
                # Set success styling and title
                msg_box.setWindowTitle("Borrowing Successful")
                msg_box.setIcon(QMessageBox.Information)
                
                # Parse the success message
                import re
                match = re.search(r"Successfully borrowed '(.+?)'\. Due date: (.+)", message)
                if match:
                    book_title = match.group(1)
                    due_date = match.group(2)
                    message = (
                        f"<h3>Book Successfully Borrowed</h3>"
                        f"<p>The book <b>'{book_title}'</b> has been successfully issued.</p>"
                        f"<p><b>Due Date:</b> {due_date}</p>"
                        f"<p>Please return the book by the due date to avoid late fees.</p>"
                    )
                else:
                    # Fallback if message format doesn't match
                    message = f"<h3>Success</h3><p>{message}</p>"
            else:
                # Error case
                msg_box.setWindowTitle("Borrowing Failed")
                msg_box.setIcon(QMessageBox.Warning)
                
                # Show specific error messages based on the error type
                if "User not found or account is inactive" in message:
                    message = "The user ID is invalid or the account is inactive."
                elif "Book not found" in message:
                    message = "The book ID is invalid or the book does not exist."
                elif "No available copies of this book" in message:
                    message = "This book is currently not available for borrowing."
                elif "already borrowed this book" in message:
                    message = "This book has already been borrowed by the same user."
                elif "Invalid user ID or book ID" in message:
                    message = "Please enter valid numeric IDs for both user and book."
                else:
                    message = f"An error occurred: {message}"
                
                message = f"<h3>Could Not Borrow Book</h3><p>{message}</p>"
            
            # Set message and show the dialog
            msg_box.setText(message)
            msg_box.setTextFormat(Qt.RichText)
            
            # Style the message box
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #f8f9fa;
                    min-width: 400px;
                    font-family: Arial;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
            # Add OK button
            ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
            ok_button.setCursor(Qt.PointingHandCursor)
            
            # Show the message box and wait for it to be closed
            msg_box.exec_()
            
            # Clear the input fields if the operation was successful
            if success:
                self.user_id_input.clear()
                self.book_id_input.clear()
                
        except Exception as e:
            error_msg = str(e)
            # If the error is about missing attribute, provide a more helpful message
            if "no attribute 'borrow_book'" in error_msg:
                error_msg = "Error: The borrowing functionality is not properly configured. Please contact support."
            QMessageBox.critical(self, "Error", 
                              f"An error occurred while processing the borrowing: {error_msg}")
            print(f"Error in borrow_book: {error_msg}")
                
    def borrow_book_action_old(self):
        user_id = self.user_id_input.text().strip()
        book_id = self.book_id_input.text().strip()
        
        # Input validation
        if not user_id or not book_id:
            QMessageBox.warning(self, "Missing Information", 
                             "Please enter both User ID and Book ID.")
            return
            
        if not user_id.isdigit() or not book_id.isdigit():
            QMessageBox.warning(self, "Invalid Input", 
                             "User ID and Book ID must be numbers.")
            return
            
        try:
            # Convert to integers after validation
            user_id = int(user_id)
            book_id = int(book_id)
            
            # Check if user exists
            user = database.get_user_by_id(user_id)
            if not user:
                QMessageBox.warning(self, "User Not Found", 
                                 f"No user found with ID: {user_id}")
                return
                
            # Check if book exists and is available
            book = database.get_book_by_id(book_id)
            if not book:
                QMessageBox.warning(self, "Book Not Found", 
                                 f"No book found with ID: {book_id}")
                return
                
            available = book.get('stock', 0)
            if available <= 0:
                QMessageBox.warning(self, "Book Not Available", 
                                 f"The book '{book.get('title', '')}' is currently not available for borrowing.\n\n"
                                 f"Book ID: {book_id}\n"
                                 f"Current Stock: {available}")
                return
                
            # Check if user has reached maximum borrow limit
            borrowed_count = database.get_borrowed_books_count(user_id)
            max_borrow_limit = 5  # You can adjust this value as needed
            
            if borrowed_count >= max_borrow_limit:
                QMessageBox.warning(self, "Borrowing Limit Reached",
                                 f"You have reached the maximum borrowing limit of {max_borrow_limit} books.")
                return
                
            try:
                # Create library backend instance and proceed with borrowing
                library = LibraryBackend()
                success, message = library.borrow_book(user_id, book_id)
                
                if success:
                    # Clear the input fields
                    self.user_id_input.clear()
                    self.book_id_input.clear()
                    # Create a custom styled message box
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Borrowing Successful")
                    msg_box.setIcon(QMessageBox.Information)
                    
                    # Set message with better formatting
                    book_title = book.get('title', 'the selected book')
                    user_name = user.get('full_name', 'the user')
                    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
                    
                    message = (
                        f"<h3>Book Successfully Borrowed</h3>"
                        f"<p>The book <b>'{book_title}'</b> has been successfully issued to <b>{user_name}</b>.</p>"
                        f"<p><b>Due Date:</b> {due_date}</p>"
                        f"<p>Please return the book by the due date to avoid late fees.</p>"
                    )
                    
                    msg_box.setText(message)
                    msg_box.setTextFormat(Qt.RichText)
                    
                    # Style the message box
                    msg_box.setStyleSheet("""
                        QMessageBox {
                            background-color: #f8f9fa;
                            min-width: 400px;
                        }
                        QLabel {
                            color: #2c3e50;
                            font-size: 14px;
                        }
                        QPushButton {
                            background-color: #28a745;
                            color: white;
                            border: none;
                            padding: 8px 16px;
                            border-radius: 4px;
                            font-weight: bold;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                        }
                    """)
                    
                    # Add OK button
                    ok_button = msg_box.addButton("OK", QMessageBox.AcceptRole)
                    ok_button.setCursor(Qt.PointingHandCursor)
                    
                    # Show the message box
                    msg_box.exec_()
                    
                    # Clear the input fields and close the window
                    self.user_id_input.clear()
                    self.book_id_input.clear()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", 
                                       "Failed to process the borrowing. The book may not be available or there was a database error.")
            except Exception as e:
                error_msg = str(e)
                # If the error is about missing attribute, provide a more helpful message
                if "no attribute 'borrow_book'" in error_msg:
                    error_msg = "Error: The borrowing functionality is not properly configured. Please contact support."
                QMessageBox.critical(self, "Error", 
                                 f"An error occurred while processing the borrowing: {error_msg}")
                print(f"Error in borrow_book: {str(e)}")
                
        except ValueError as e:
            QMessageBox.critical(self, "Error", 
                               f"Invalid input: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"An error occurred: {str(e)}")
            print(f"Error in borrow_book_action: {str(e)}")

class ReturnBookScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Return Book")
        self.setStyleSheet("background-color: #ffffff;")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Return Book")
        title_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label.setStyleSheet("color: #000000; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-bottom: 5px;")
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter User ID or Scan Barcode")
        self.user_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(user_id_label)
        layout.addWidget(self.user_id_input)

        # Book ID
        book_id_label = QLabel("Book ID")
        book_id_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333; margin-top: 10px; margin-bottom: 5px;")
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("Enter Book ID or Scan Barcode")
        self.book_id_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        layout.addWidget(book_id_label)
        layout.addWidget(self.book_id_input)

        layout.addStretch()

        # Return Button
        self.return_button = QPushButton("Return Book")
        self.return_button.setCursor(Qt.PointingHandCursor)
        self.return_button.clicked.connect(self.return_book_action)
        self.return_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.return_button)
        layout.addLayout(button_layout)

    def return_book_action(self):
        user_id = self.user_id_input.text().strip()
        book_id = self.book_id_input.text().strip()
        
        # Input validation
        if not user_id or not book_id:
            QMessageBox.warning(self, "Missing Information", 
                             "Please enter both User ID and Book ID.")
            return
            
        conn = None
        try:
            # Convert inputs to integers
            user_id = int(user_id)
            book_id = int(book_id)
            
            # Get database connection with timeout and check_same_thread=False
            conn = sqlite3.connect('intelli_libraria.db', timeout=30, check_same_thread=False)
            conn.execute('PRAGMA busy_timeout = 30000')  # 30 seconds timeout
            conn.execute('PRAGMA journal_mode=WAL')  # Enable Write-Ahead Logging
            
            with conn:
                cursor = conn.cursor()
                
                # Check if the book is actually borrowed by this user
                cursor.execute("""
                    SELECT t.id, b.title 
                    FROM transactions t
                    JOIN books b ON t.book_id = b.id
                    WHERE t.user_id = ? 
                    AND t.book_id = ? 
                    AND t.status = 'Issued'
                    AND t.return_date IS NULL
                    LIMIT 1
                """, (user_id, book_id))
                
                transaction = cursor.fetchone()
                
                if not transaction:
                    QMessageBox.warning(
                        self, 
                        "No Active Borrowing Found",
                        "No active borrowing record found for this user and book.\n\n"
                        "Please check the User ID and Book ID and try again."
                    )
                    return
                    
                transaction_id, book_title = transaction
                
                # Update the transaction record
                cursor.execute("""
                    UPDATE transactions 
                    SET return_date = DATE('now'),
                        status = 'Returned',
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (transaction_id,))
                
                # Update book availability
                cursor.execute("""
                    UPDATE books 
                    SET stock = stock + 1,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (book_id,))
                
                # Commit is handled by the context manager
            
            # Show success message
            success_msg = QMessageBox()
            success_msg.setWindowTitle("Book Returned Successfully")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setTextFormat(Qt.RichText)
            success_msg.setText(
                f"<h3>Book Successfully Returned</h3>"
                f"<p>The book <b>'{book_title}'</b> has been successfully returned.</p>"
                f"<p>Thank you for returning the book on time!</p>"
            )
            
            # Style the message box
            success_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f8f9fa;
                    min-width: 400px;
                    font-family: Arial;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
            # Add OK button
            ok_button = success_msg.addButton("OK", QMessageBox.AcceptRole)
            ok_button.setCursor(Qt.PointingHandCursor)
            
            # Show the message box
            success_msg.exec_()
            
            # Clear the input fields
            self.user_id_input.clear()
            self.book_id_input.clear()
            
        except ValueError:
            QMessageBox.warning(
                self, 
                "Invalid Input", 
                "Please enter valid numeric IDs for both User ID and Book ID."
            )
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(
                self, 
                "Database Error", 
                f"An error occurred while processing the return.\n\nError: {str(e)}\n\nPlease try again."
            )
            print(f"Database error in return_book_action: {str(e)}")
        except Exception as e:
            if conn:
                conn.rollback()
            QMessageBox.critical(
                self, 
                "Error", 
                f"An unexpected error occurred.\n\nError: {str(e)}\n\nPlease try again."
            )
            print(f"Error in return_book_action: {str(e)}")
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

class BorrowReturnPage(QWidget):
    def __init__(self):
        super().__init__()
        self.borrow_book_screen = None
        self.return_book_screen = None
        self.setStyleSheet("background: #f8fafc;")
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        
        # Left Panel - Details
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Right Panel - Quick Actions
        right_panel = QFrame()
        right_panel.setFixedWidth(400)
        right_panel.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(20)

        # Title
        title = QLabel("Quick Actions")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 10px;
            }
        """)
        right_layout.addWidget(title, alignment=Qt.AlignLeft)

        # Scan Buttons
        scan_btn = QPushButton("📱 Scan Barcode")
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #334155;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
                padding: 15px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        right_layout.addWidget(scan_btn)

        # Input Fields
        input_style = """
            QLineEdit {
                background: #f8fafc;
                border: 1.5px solid #e2e8f0;
                border-radius: 10px;
                padding: 14px 16px;
                font-size: 15px;
                color: #1e293b;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border: 1.5px solid #3b82f6;
            }
        """

        # User ID
        user_id = QLineEdit()
        user_id.setPlaceholderText("Enter User ID")
        user_id.setStyleSheet(input_style)
        right_layout.addWidget(user_id)

        # Book ID
        book_id = QLineEdit()
        book_id.setPlaceholderText("Enter Book ID")
        book_id.setStyleSheet(input_style)
        right_layout.addWidget(book_id)

        # Action Buttons
        btn_style = """
            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 15px;
                font-weight: 600;
                margin-top: 10px;
            }
        """

        borrow_btn = QPushButton("Borrow Book")
        borrow_btn.setStyleSheet(f"""
            {btn_style}
            QPushButton {{
                background: #3b82f6;
                color: white;
            }}
            QPushButton:hover {{
                background: #2563eb;
            }}
        """)
        borrow_btn.setCursor(Qt.PointingHandCursor)

        return_btn = QPushButton("Return Book")
        return_btn.setStyleSheet(f"""
            {btn_style}
            QPushButton {{
                background: #10b981;
                color: white;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """)
        return_btn.setCursor(Qt.PointingHandCursor)

        right_layout.addWidget(borrow_btn)
        right_layout.addWidget(return_btn)
        right_layout.addStretch()

        # Left Panel - Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-top: none;
                border-radius: 0 0 8px 8px;
                background: white;
                padding: 0;
                margin: 0;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #475569;
                padding: 12px 24px;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                border-radius: 8px 8px 0 0;
                margin-right: 6px;
                font-size: 15px;
                font-weight: 600;
                min-width: 120px;
                text-align: center;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
                font-weight: 700;
                margin-bottom: -1px;
            }
            QTabBar::tab:!selected {
                margin-top: 4px;
                padding-bottom: 8px;
            }
            QTabBar::tab:!selected:hover {
                background: #f1f5f9;
                color: #334155;
            }
            QTabBar {
                background: white;
                border: none;
                margin: 0;
                padding: 0 15px;
                border-radius: 8px 8px 0 0;
            }
        """)

        # Book Details Tab
        book_tab = QWidget()
        book_tab_layout = QVBoxLayout(book_tab)
        book_tab_layout.setContentsMargins(15, 10, 15, 15)
        book_tab_layout.setSpacing(15)

        # Book Info Card
        book_card = QFrame()
        book_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        book_card_layout = QVBoxLayout(book_card)
        book_card_layout.setContentsMargins(20, 20, 20, 20)
        
        book_title = QLabel("Book Details")
        book_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 15px;
            }
        """)
        book_card_layout.addWidget(book_title)

        # Book Details Grid
        book_grid = QGridLayout()
        book_grid.setVerticalSpacing(12)
        book_grid.setHorizontalSpacing(20)
        
        # Attempt to show the most recently added book as an example
        book_fields = []
        try:
            rows = database.execute_query(
                "SELECT title, author, COALESCE(isbn,'') AS isbn, COALESCE(stock,0) AS stock FROM books ORDER BY id DESC LIMIT 1"
            )
            if rows:
                r = rows[0]
                status = "Available" if (r.get("stock", 0) or 0) > 0 else "Out of Stock"
                book_fields = [
                    ("Title:", r.get("title", "")),
                    ("Author:", r.get("author", "")),
                    ("ISBN:", r.get("isbn", "")),
                    ("Status:", status),
                    ("Due Date:", "N/A")
                ]
        except Exception as e:
            print(f"Error fetching book details: {e}")
        
        if not book_fields:
            book_fields = [
                ("Title:", ""),
                ("Author:", ""),
                ("ISBN:", ""),
                ("Status:", ""),
                ("Due Date:", "")
            ]
        
        for i, (label, value) in enumerate(book_fields):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #64748b; font-size: 14px;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 500;")
            book_grid.addWidget(label_widget, i, 0, Qt.AlignLeft)
            book_grid.addWidget(value_widget, i, 1, Qt.AlignLeft)
        
        book_card_layout.addLayout(book_grid)
        book_tab_layout.addWidget(book_card)

        # User Info Card
        user_card = QFrame()
        user_card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        user_card_layout = QVBoxLayout(user_card)
        user_card_layout.setContentsMargins(20, 20, 20, 20)
        
        user_title = QLabel("User Details")
        user_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 15px;
            }
        """)
        user_card_layout.addWidget(user_title)

        # User Details Grid
        user_grid = QGridLayout()
        user_grid.setVerticalSpacing(12)
        user_grid.setHorizontalSpacing(20)
        
        user_fields = [
            ("Name:", "John Doe"),
            ("Email:", "john.doe@example.com"),
            ("User ID:", "USR-00123"),
            ("Membership:", "Premium"),
            ("Borrowed Books:", "2/5")
        ]
        
        for i, (label, value) in enumerate(user_fields):
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #64748b; font-size: 14px;")
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 500;")
            user_grid.addWidget(label_widget, i, 0, Qt.AlignLeft)
            user_grid.addWidget(value_widget, i, 1, Qt.AlignLeft)
        
        user_card_layout.addLayout(user_grid)
        book_tab_layout.addWidget(user_card)
        
        # Add stretch to push content to top
        book_tab_layout.addStretch()

        # Recent Transactions Tab
        trans_tab = QWidget()
        trans_tab_layout = QVBoxLayout(trans_tab)
        trans_tab_layout.setContentsMargins(15, 10, 15, 15)
        
        # Recent Transactions Table
        transactions_table = QTableWidget()
        transactions_table.setColumnCount(4)
        transactions_table.setHorizontalHeaderLabels(["Date", "User", "Book", "Action"])
        transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        transactions_table.verticalHeader().setVisible(False)
        transactions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        transactions_table.setShowGrid(False)
        transactions_table.setAlternatingRowColors(True)
        transactions_table.verticalHeader().setDefaultSectionSize(50)
        transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                alternate-background-color: #f8fafc;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 12px;
                border: none;
                font-size: 13px;
                font-weight: 600;
                color: #475569;
            }
            QTableWidget::item {
                padding: 12px;
                color: #334155;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #e0f2fe;
                color: #0369a1;
            }
        """)
        
        # Sample data
        transactions = [
            ("2024-01-15", "Emily Carter", "The Great Adventure", "Borrowed"),
            ("2024-01-10", "David Lee", "Mystery of the Lost City", "Returned"),
            ("2024-01-05", "Emily Carter", "The Secret Garden", "Borrowed"),
            ("2024-01-02", "John Smith", "Python Programming", "Returned"),
            ("2023-12-28", "Sarah Johnson", "Data Science 101", "Returned")
        ]
        
        transactions_table.setRowCount(len(transactions))
        for row, (date, user, book, action) in enumerate(transactions):
            transactions_table.setItem(row, 0, QTableWidgetItem(date))
            transactions_table.setItem(row, 1, QTableWidgetItem(user))
            transactions_table.setItem(row, 2, QTableWidgetItem(book))
            
            action_item = QTableWidgetItem(action)
            if action == "Borrowed":
                action_item.setForeground(QColor("#3b82f6"))
            else:
                action_item.setForeground(QColor("#10b981"))
            transactions_table.setItem(row, 3, action_item)
        
        trans_tab_layout.addWidget(transactions_table)
        
        # Add tabs
        tabs.addTab(book_tab, "Details")
        tabs.addTab(trans_tab, "Transactions")
        
        # Add tabs to left panel
        left_layout.addWidget(tabs)
        
        # Add panels to main layout with spacing
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)  # Right panel takes remaining space
        
        # Connect buttons
        borrow_btn.clicked.connect(self.show_borrow_screen)
        return_btn.clicked.connect(self.show_return_screen)
        scan_btn.clicked.connect(self.scan_barcode)

    def scan_barcode(self):
        """Handle barcode scanning functionality"""
        if not PYZBAR_AVAILABLE:
            QMessageBox.critical(
                self,
                "Barcode Scanner Unavailable",
                "Barcode scanning requires ZBar (pyzbar). The library failed to load on this system.\n\n"
                "You can still use manual entry."
            )
            return
        # Create a dialog for the camera feed
        self.scan_dialog = QWidget()
        self.scan_dialog.setWindowTitle("Barcode Scanner - Press ESC to exit full screen")
        self.scan_dialog.setWindowModality(Qt.ApplicationModal)
        
        # Set window to full screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.scan_dialog.setGeometry(screen_geometry)
        self.scan_dialog.setWindowState(Qt.WindowFullScreen)
        
        # Make sure the window is on top
        self.scan_dialog.setWindowFlags(self.scan_dialog.windowFlags() | 
                                      Qt.WindowStaysOnTopHint | 
                                      Qt.FramelessWindowHint)
        
        # Main layout
        layout = QVBoxLayout(self.scan_dialog)
        
        # Label to display camera feed
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #000;")
        layout.addWidget(self.camera_label)
        
        # Status label
        self.status_label = QLabel("Position barcode in front of the camera")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; padding: 10px;")
        layout.addWidget(self.status_label)
        
        # Button to close the dialog
        close_btn = QPushButton("Close Scanner")
        close_btn.clicked.connect(self.stop_scanning)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        layout.addWidget(close_btn)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open camera")
            return
            
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Start the timer to update the camera feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms
        
        self.scan_dialog.show()
    
    def stop_scanning(self):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'scan_dialog'):
            self.scan_dialog.close()
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # Convert frame to RGB for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Decode barcodes
        barcodes = zbar_decode(frame) if PYZBAR_AVAILABLE else []
        
        # Process each barcode found
        for barcode in barcodes:
            # Extract barcode data
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            
            # Draw rectangle around the barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw barcode data and type on the frame
            text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame_rgb, text, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Update the status label with the scanned barcode
            self.status_label.setText(f"Scanned: {barcode_data}")
            self.status_label.setStyleSheet("color: #10b981; font-size: 16px; padding: 10px;")
            
            # Update the book ID field with the scanned barcode
            if hasattr(self, 'book_id_input'):
                self.book_id_input.setText(barcode_data)
            
            # Stop scanning after successful scan
            self.timer.singleShot(2000, self.stop_scanning)
            break
        
        # Convert the frame to QImage
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Display the frame in the QLabel, scaled to fit while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(q_img).scaled(
            self.camera_label.size(), 
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled_pixmap)
        
        # Center the camera feed in the label
        self.camera_label.setAlignment(Qt.AlignCenter)

    def show_borrow_screen(self):
        if not self.borrow_book_screen:
            self.borrow_book_screen = BorrowBookScreen()
        self.borrow_book_screen.showMaximized()



    def show_return_screen(self):
        if not self.return_book_screen:
            self.return_book_screen = ReturnBookScreen()
        self.return_book_screen.showMaximized()