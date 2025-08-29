from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QSizePolicy, QGroupBox, QHeaderView, QApplication, QLineEdit, QListWidget, QListWidgetItem,
    QGridLayout, QSpacerItem, QScrollArea, QStackedWidget, QMenu, QAction, QDialog, QMessageBox, QDesktopWidget
)
from logout_dialog import LogoutConfirmationDialog
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from book_inventory_page import BookInventoryPage
from user_management_page import UserManagementPage
from add_user_page import AddUserPage
from borrow_return_page import BorrowReturnPage
from report_generation_page import ReportGenerationPage
from fine_management_page import FineManagementPage
from notification_reminder_page import NotificationReminderPage
from reservation_management_page import ReservationManagementPage
from user_feedback_page import UserFeedbackPage

class SidebarButton(QPushButton):
    def __init__(self, text, active=False, parent=None):
        super().__init__(parent)
        self.setText(f"  {text}")
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(Qt.PointingHandCursor)
        # Set fixed height for consistent button sizing
        self.setMinimumHeight(48)
        self.setMaximumHeight(48)
        # Set up the base styles
        self.update_styles()
        
    def update_styles(self):
        base_style = """
            QPushButton {
                text-align: left;
                padding: 10px 16px;
                margin: 0;
                font-size: 15px;
                color: #1e293b;
                border: none;
                background: #f8fafc;
                border-radius: 10px;
                font-family: 'Segoe UI', -apple-system, sans-serif;
                font-weight: 600;
                letter-spacing: 0.3px;
                min-width: 200px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: #f1f5f9;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
            QPushButton:checked {
                background: #4f46e5;
                color: white;
                font-weight: 700;
                letter-spacing: 0.4px;
                border-left: 3px solid #ffffff;
            }
            QPushButton:checked:hover {
                background: #4338ca;
            }
        """
        self.setStyleSheet(base_style)

class StatCard(QFrame):
    def __init__(self, title, value, color=None):
        super().__init__()
        self.setMinimumWidth(180)  # Increased from 150
        self.setMaximumWidth(240)  # Increased from 220
        self.setFixedHeight(140)  # Set a fixed height for all cards
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        
        # Store title and value for later use
        self.title = title
        self.value = value
        
        # Set all cards to use the same color
        color_map = {
            'books': '#F0D2DA',
            'users': '#F0D2DA',
            'borrowed': '#F0D2DA',
            'overdue': '#F0D2DA',
            'default': '#F0D2DA'
        }
        
        # Get the appropriate color based on the title
        if 'book' in title.lower() and 'overdue' not in title.lower():
            card_color = color_map['books']
        elif 'member' in title.lower() or 'user' in title.lower():
            card_color = color_map['users']
        elif 'borrow' in title.lower():
            card_color = color_map['borrowed']
        elif 'overdue' in title.lower():
            card_color = color_map['overdue']
        else:
            card_color = color or color_map['default']
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {card_color};
                border-radius: 10px;
                border: 1px solid #e5e7eb;
                padding: 12px 10px;
                margin: 0 4px;
            }}
            QLabel {{
                border: none;
            }}
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        # Create and configure title label
        title_label = QLabel(title.upper())
        title_label.setWordWrap(True)
        
        # Set font to Times New Roman and adjust size based on card type
        font_size = 14 if 'member' in title.lower() else 12  # Larger font for members
        title_label.setFont(QFont("Times New Roman", font_size, QFont.Bold))
        
        title_label.setStyleSheet("""
            color: #111827; 
            font-weight: 800; 
            letter-spacing: 0.5px;
            padding: 2px 0;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        # Create and configure value label
        value_label = QLabel(str(value))
        value_font_size = 36 if 'member' in title.lower() else 32  # Larger font for members
        value_label.setFont(QFont("Times New Roman", value_font_size, QFont.Bold))
        value_label.setStyleSheet("""
            color: #111827; 
            font-weight: 800;
            padding: 2px 0;
            text-align: center;
        """)
        value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)

class StatusBadge(QLabel):
    def __init__(self, status):
        super().__init__(status)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(28)
        if status == "Borrowed":
            self.setStyleSheet("background: #f3f4f6; color: #232b36; border-radius: 8px; font-weight: bold; padding: 2px 16px;")
        elif status == "Available":
            self.setStyleSheet("background: #e6f4ea; color: #388e3c; border-radius: 8px; font-weight: bold; padding: 2px 16px;")
        elif status == "Overdue":
            self.setStyleSheet("background: #fff4e5; color: #f57c00; border-radius: 8px; font-weight: bold; padding: 2px 16px;")

class Sidebar(QWidget):
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
        """)
        
        # Main layout with proper spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title section with improved typography
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 12, 0, 12)  # Add vertical padding
        
        logo_label = QLabel("INTELLI LIBRARIA")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Black))  # Increased size and weight
        logo_label.setStyleSheet("""
            color: #1e293b;  /* Dark gray color for better contrast */
            padding: 12px 0;
            margin: 0;
            letter-spacing: 0.5px;
        """)
        
        title_layout.addWidget(logo_label)
        layout.addWidget(title_widget)

        # Menu items container with perfect spacing
        menu_widget = QWidget()
        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(0, 8, 0, 0)  # No side margins
        menu_layout.setSpacing(0)  # No spacing between items
        
        self.buttons = []
        menu_items = [
            ("📊  Dashboard", "dashboard"),
            ("👥  User Management", "user_management"),
            ("📚  Book Inventory", "book_inventory"),
            ("🔄  Borrow && Return", "borrow_return"),
            ("📈  Report Generation", "report_generation"),
            ("💰  Fine Management", "fine_management"),
            ("🔔  Notification && Reminder", "notification_reminder"),
            ("📅  Reservation Management", "reservation_management"),
            ("💬  User Feedback", "user_feedback"),
        ]

        self.active_button = None
        for text, page_name in menu_items:
            btn = SidebarButton(text, active=False)
            btn.page_name = page_name
            btn.setCheckable(True)
            
            menu_layout.addWidget(btn)
            self.buttons.append(btn)
            btn.clicked.connect(lambda checked, b=btn: self.select_button(b))
        
        # Add menu widget to layout
        layout.addWidget(menu_widget)
        
        # Add stretch to push logout to bottom
        layout.addStretch(1)
        
        # Bottom section with logout button
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 8, 0, 8)  # No side margins, only top and bottom
        
        # Logout button with consistent styling
        print("Creating logout button...")  # Debug
        self.logout_btn = SidebarButton("🚪  Logout")
        self.logout_btn.setCheckable(True)
        print(f"Logout button created: {self.logout_btn}")  # Debug
        
        # Connect the click event with debupyg prints
        def on_logout_clicked():
            print("Logout button clicked!")  # Debug
            # Always show the custom logout confirmation dialog
            self.show_logout_confirmation()
            
        self.logout_btn.clicked.connect(on_logout_clicked)
        print(f"Logout button connected: {self.logout_btn.signalsBlocked()}")  # Debug
        bottom_layout.addWidget(self.logout_btn)
        print("Logout button added to layout")  # Debug
        
        # Add to main layout with stretch to push to bottom
        layout.addStretch(1)  # This will push the bottom widget down
        layout.addWidget(bottom_widget)

    def show_logout_confirmation(self):
        print("show_logout_confirmation called")  # Debug
        try:
            dialog = LogoutConfirmationDialog(self)
            dialog.setWindowModality(Qt.ApplicationModal)
            
            # Center the dialog on the screen
            screen = QDesktopWidget().screenGeometry()
            x = (screen.width() - dialog.width()) // 2
            y = (screen.height() - dialog.height()) // 2
            dialog.move(x, y)
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                print("User confirmed logout")  # Debug
                self.logout_requested.emit()
            else:
                print("User cancelled logout")  # Debug
                
        except Exception as e:
            print(f"Error in show_logout_confirmation: {e}")  # Debug
            import traceback
            traceback.print_exc()

    def select_button(self, selected_btn):
        # Only allow one button to be active at a time
        for btn in self.buttons + [self.logout_btn]:
            btn.setChecked(btn is selected_btn)
        self.active_button = selected_btn
        
    def handle_logout(self):
        try:
            # Show the logout confirmation dialog
            dialog = LogoutConfirmationDialog(self)
            dialog.setWindowModality(Qt.ApplicationModal)
            
            # Center the dialog on the screen
            screen = QDesktopWidget().screenGeometry()
            x = (screen.width() - dialog.width()) // 2
            y = (screen.height() - dialog.height()) // 2
            dialog.move(x, y)
            
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                print("User confirmed logout")  # Debug
                self.logout_requested.emit()
            else:
                print("User cancelled logout")  # Debug
                
        except Exception as e:
            print(f"Error in handle_logout: {e}")  # Debug
            import traceback
            traceback.print_exc()


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria - Dashboard")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                          Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                          Qt.WindowCloseButtonHint)
        self.setMinimumSize(1200, 800)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel, QPushButton, QLineEdit, QTableWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.initUI()
        self.showMaximized()  # Show maximized with title bar
    
    def logout(self):
        print("DashboardWindow.logout() called")  # Debug
        # Emit the close event which will be caught by main.py
        self.close()
        print("DashboardWindow closed")  # Debug

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # Connect the logout signal from sidebar after it's created
        if hasattr(self.sidebar, 'logout_requested'):
            self.sidebar.logout_requested.connect(self.logout)

        self.dashboard_content = self.create_dashboard_content()
        self.user_management_page = UserManagementPage(main_window=self)
        self.add_user_page = AddUserPage(main_window=self)
        self.book_inventory_page = BookInventoryPage()
        self.borrow_return_page = BorrowReturnPage()
        self.report_generation_page = ReportGenerationPage()
        self.fine_management_page = FineManagementPage()
        self.notification_reminder_page = NotificationReminderPage()
        self.reservation_management_page = ReservationManagementPage()
        self.user_feedback_page = UserFeedbackPage()

        self.pages_stack = QStackedWidget()
        self.pages_stack.addWidget(self.dashboard_content)
        self.pages_stack.addWidget(self.user_management_page)
        self.pages_stack.addWidget(self.add_user_page)
        self.pages_stack.addWidget(self.book_inventory_page)
        self.pages_stack.addWidget(self.borrow_return_page)
        self.pages_stack.addWidget(self.report_generation_page)
        self.pages_stack.addWidget(self.fine_management_page)
        self.pages_stack.addWidget(self.notification_reminder_page)
        self.pages_stack.addWidget(self.reservation_management_page)
        self.pages_stack.addWidget(self.user_feedback_page)

        main_layout.addWidget(self.pages_stack)

        for btn in self.sidebar.buttons:
            btn.clicked.connect(self.switch_page)

        self.sidebar.buttons[0].setChecked(True)
        self.pages_stack.setCurrentWidget(self.dashboard_content)

    def switch_page(self):
        sender = self.sender()
        if not sender: 
            return

        # Map page names to their corresponding methods
        page_map = {
            "dashboard": self.show_dashboard,
            "user_management": self.show_user_management,
            "book_inventory": self.show_book_inventory,
            "borrow_return": self.show_borrow_return,
            "report_generation": self.show_report_generation,
            "fine_management": self.show_fine_management,
            "notification_reminder": self.show_notification_reminder,
            "reservation_management": self.show_reservation_management,
            "user_feedback": self.show_user_feedback,
        }

        # Get the action using the page_name from the button
        action = page_map.get(sender.page_name)
        if action:
            # Call the corresponding method
            action()
            
            # Debug output to help identify issues
            print(f"Switching to page: {sender.page_name}")
            print(f"Available pages: {list(page_map.keys())}")
        else:
            print(f"No action found for page: {sender.page_name}")
            print(f"Available pages: {list(page_map.keys())}")

    def create_dashboard_content(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        dashboard_content = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_content)
        dashboard_layout.setContentsMargins(24, 24, 24, 24)
        dashboard_layout.setSpacing(16)
        dashboard_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(dashboard_content)

        header_label = QLabel("Welcome back, Admin!")
        header_label.setFont(QFont("Arial", 24, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50;")
        dashboard_layout.addWidget(header_label)

        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setContentsMargins(4, 0, 4, 0)  
        cards_layout.setSpacing(6)  
        
        # Total Books from database
        try:
            import database
            total_books = database.get_books_count()
        except Exception:
            total_books = 0
        self.total_books_card = StatCard("Total Books", total_books)
        cards_layout.addWidget(self.total_books_card, 1)

        # Live Members
        try:
            members_count = database.get_members_count()
        except Exception:
            members_count = 0
        self.members_card = StatCard("Members", members_count)
        cards_layout.addWidget(self.members_card, 1)

        # Live Borrowed
        try:
            borrowed_count = database.get_borrowed_count()
        except Exception:
            borrowed_count = 0
        self.borrowed_card = StatCard("Books Borrowed", borrowed_count)
        cards_layout.addWidget(self.borrowed_card, 1)

        # Live Overdue
        try:
            overdue_count = database.get_overdue_count()
        except Exception:
            overdue_count = 0
        self.overdue_card = StatCard("Overdue Books", overdue_count)
        cards_layout.addWidget(self.overdue_card, 1)
        
        dashboard_layout.addWidget(cards_container)

        dashboard_layout.addSpacing(24)
        recent_label = QLabel("Recent Activity")
        recent_label.setStyleSheet("font-size: 24px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 700; margin-bottom: 8px;")
        dashboard_layout.addWidget(recent_label, alignment=Qt.AlignLeft)

        # Create the table with 5 columns
        table = QTableWidget(0, 5)  # Start with 0 rows, we'll add them dynamically
        table.setHorizontalHeaderLabels(["Book Title", "Author", "Borrower", "Due Date", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(48)
        table.setMinimumHeight(400)
        
        # Function to load and refresh table data
        def load_table_data():
            try:
                # Clear existing data
                table.setRowCount(0)
                
                # Fetch recent transactions from database
                from database import get_recent_transactions
                transactions = get_recent_transactions(limit=10)  # Get up to 10 recent transactions
                
                if not transactions:
                    # If no transactions, show a message
                    table.setRowCount(1)
                    no_data_item = QTableWidgetItem("No recent activity found")
                    no_data_item.setTextAlignment(Qt.AlignCenter)
                    table.setSpan(0, 0, 1, 5)  # Span all columns
                    table.setItem(0, 0, no_data_item)
                    return
                
                # Set row count based on actual data
                table.setRowCount(len(transactions))
                
                # Populate the table with transaction data
                for row, (title, author, user_name, due_date, status) in enumerate(transactions):
                    # Create table items for each column
                    title_item = QTableWidgetItem(title or "N/A")
                    author_item = QTableWidgetItem(author or "N/A")
                    user_item = QTableWidgetItem(user_name or "N/A")
                    due_date_item = QTableWidgetItem(str(due_date) if due_date else "N/A")
                    status_item = QTableWidgetItem(status or "N/A")
                    
                    # Set text alignment
                    for item in [title_item, author_item, user_item, due_date_item, status_item]:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    
                    # Add items to the table
                    table.setItem(row, 0, title_item)
                    table.setItem(row, 1, author_item)
                    table.setItem(row, 2, user_item)
                    table.setItem(row, 3, due_date_item)
                    table.setItem(row, 4, status_item)
                    
                    # Color code status
                    status_text = status.lower() if status else ""
                    if 'overdue' in status_text:
                        status_item.setForeground(QColor('#ef4444'))  # Red for overdue
                        status_item.setFont(QFont('Arial', 9, QFont.Bold))
                    elif 'issue' in status_text:
                        status_item.setForeground(QColor('#f59e0b'))  # Yellow for issued
                    elif 'return' in status_text:
                        status_item.setForeground(QColor('#10b981'))  # Green for returned
                        
                    # Make the status text more readable
                    if status:
                        status_item.setText(status.capitalize())
                        
            except Exception as e:
                print(f"Error loading recent transactions: {e}")
                # Add a single row with error message if loading fails
                table.setRowCount(1)
                error_item = QTableWidgetItem(f"Error loading recent activity: {str(e)}")
                error_item.setTextAlignment(Qt.AlignCenter)
                table.setSpan(0, 0, 1, 5)  # Span all columns
                table.setItem(0, 0, error_item)
        
        # Initial load of data
        load_table_data()
        
        # Store the load function for later refresh
        self.load_table_data = load_table_data
        
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 16px; 
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1.5px solid #e5e7eb; 
                padding: 0px; 
                alternate-background-color: #f9fafb; 
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 10px 8px; 
            }
            QHeaderView::section {
                background: #f9fafb; 
                color: #232b36;
                font-weight: 700;
                font-size: 15px;
                border: none;
                border-bottom: 1.5px solid #e5e7eb; 
                padding: 18px 8px; 
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Add the table to the layout
        dashboard_layout.addWidget(table)
        dashboard_layout.addStretch()
        return scroll

    def show_dashboard(self):
        # Set window title
        self.setWindowTitle("Intelli Libraria - Dashboard")
        
        # Refresh all dashboard data
        self.refresh_total_books()
        
        try:
            import database
            # Total books
            tb = database.get_books_count()
            tb_label = self.total_books_card.findChildren(QLabel)[1]
            tb_label.setText(str(tb))

            # Members
            mb = database.get_members_count()
            mb_label = self.members_card.findChildren(QLabel)[1]
            mb_label.setText(str(mb))

            # Borrowed
            br = database.get_borrowed_count()
            br_label = self.borrowed_card.findChildren(QLabel)[1]
            br_label.setText(str(br))

            # Overdue
            od = database.get_overdue_count()
            od_label = self.overdue_card.findChildren(QLabel)[1]
            od_label.setText(str(od))
            
            # Refresh the recent activity table
            if hasattr(self, 'load_table_data'):
                self.load_table_data()
                
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
            
        self.pages_stack.setCurrentWidget(self.dashboard_content)

    def show_user_management(self):
        self.setWindowTitle("Intelli Libraria - User Management")
        self.user_management_page.load_users()
        self.pages_stack.setCurrentWidget(self.user_management_page)

    def show_add_user_page(self):
        self.pages_stack.setCurrentWidget(self.add_user_page)

    def refresh_total_books(self):
        try:
            import database
            count = database.get_books_count()
            # Update the displayed value on the StatCard
            value_label = self.total_books_card.findChildren(QLabel)[1]
            value_label.setText(str(count))
        except Exception as e:
            print(f"Failed to refresh total books: {e}")

    def show_book_inventory(self):
        self.setWindowTitle("Intelli Libraria - Book Inventory")
        # Load books when navigating to the page to ensure fresh data and avoid early popups
        try:
            if hasattr(self.book_inventory_page, 'load_books'):
                self.book_inventory_page.load_books()
                self.refresh_total_books()
        except Exception as e:
            print(f"Error loading books on navigation: {e}")
        self.pages_stack.setCurrentWidget(self.book_inventory_page)

    def show_borrow_return(self):
        self.setWindowTitle("Intelli Libraria - Borrow Books")
        self.pages_stack.setCurrentWidget(self.borrow_return_page)

    def show_report_generation(self):
        self.setWindowTitle("Intelli Libraria - Reports")
        self.pages_stack.setCurrentWidget(self.report_generation_page)

    def show_fine_management(self):
        self.setWindowTitle("Intelli Libraria - Fine Management")
        self.pages_stack.setCurrentWidget(self.fine_management_page)
        
    def show_notification_reminder(self):
        """Switch to the notification and reminder page"""
        self.pages_stack.setCurrentWidget(self.notification_reminder_page)
        self.setWindowTitle("Notification & Reminders - Intelli Libraria")
        
    def show_reservation_management(self):
        """Switch to the reservation management page"""
        self.setWindowTitle("Intelli Libraria - Reservations")
        self.pages_stack.setCurrentWidget(self.reservation_management_page)

    def show_user_feedback(self):
        self.setWindowTitle("Intelli Libraria - User Feedback")
        self.pages_stack.setCurrentWidget(self.user_feedback_page)