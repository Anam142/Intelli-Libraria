from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QSizePolicy, QGroupBox, QHeaderView, QApplication, QLineEdit, QListWidget, QListWidgetItem,
    QGridLayout, QSpacerItem, QScrollArea, QStackedWidget, QMenu, QAction, QDialog
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
        self.setMinimumWidth(150)  
        self.setMaximumWidth(220)  
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Default colors for different card types
        color_map = {
            'books': '#4f46e5',
            'users': '#10b981',
            'borrowed': '#f59e0b',
            'overdue': '#ef4444',
            'default': '#3b82f6'
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
                background-color: #ffffff;
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
        
        # Title and value
        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Segoe UI", 9, QFont.Bold))  
        title_label.setStyleSheet(f"color: #111827; font-weight: 700; letter-spacing: 0.5px;")  
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setStyleSheet(f"color: #111827; font-weight: 700;")  
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Add a small colored line at the bottom
        line = QFrame()
        line.setFixedHeight(3)
        line.setStyleSheet(f"background-color: {card_color}; border-radius: 2px;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(line)

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
        
        # Connect the click event with debug prints
        def on_logout_clicked():
            print("Logout button clicked!")  # Debug
            self.show_logout_confirmation()
            
        self.logout_btn.clicked.connect(on_logout_clicked)
        print(f"Logout button connected: {self.logout_btn.signalsBlocked()}")  # Debug
        bottom_layout.addWidget(self.logout_btn)
        print("Logout button added to layout")  # Debug
        
        # Add to main layout with stretch to push to bottom
        layout.addStretch(1)  # This will push the bottom widget down
        layout.addWidget(bottom_widget)

    def show_user_menu(self):
        # Show the user menu below the logout button
        self.user_menu.exec_(self.logout_btn.mapToGlobal(
            self.logout_btn.rect().bottomLeft()
        ))
        
        # Alternatively, you can directly show the logout confirmation
        # by uncommenting the line below and removing the menu code above
        # self.show_logout_confirmation()
        
    def show_logout_confirmation(self):
        print("1. show_logout_confirmation called")  # Debug
        try:
            # Get the main window
            main_window = self.window()
            print(f"2. Main window: {main_window}")  # Debug
            
            # Create the dialog with the main window as parent
            print("3. Creating dialog...")  # Debug
            dialog = LogoutConfirmationDialog(main_window)
            print("4. Dialog created")  # Debug
            
            # Set the dialog as modal
            dialog.setModal(True)
            print("5. Dialog set as modal")  # Debug
            
            # Show the dialog and wait for user response
            print("6. Showing dialog...")  # Debug
            result = dialog.exec_()
            print(f"7. Dialog result: {result}")  # Debug
            
            # Uncheck the logout button regardless of the result
            self.logout_btn.setChecked(False)
            
            if result == QDialog.Accepted:
                print("8. User confirmed logout")  # Debug
                # Emit the logout signal if user confirmed
                self.logout_requested.emit()
            else:
                print("8. User cancelled logout")  # Debug
                
        except Exception as e:
            print(f"ERROR in show_logout_confirmation: {str(e)}")
            import traceback
            traceback.print_exc()
            self.logout_btn.setChecked(False)  # Ensure button is unchecked on error

    def select_button(self, selected_btn):
        # Only allow one button to be active at a time
        for btn in self.buttons + [self.logout_btn]:
            btn.setChecked(btn is selected_btn)
        self.active_button = selected_btn
        
    def handle_logout(self):
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 'Logout', 'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get the main window and close it
            main_window = self.window()
            if main_window:
                from main import LoginWindow  # Import here to avoid circular import
                login_window = LoginWindow()
                login_window.show()
                main_window.close()


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria")
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
        
        cards_layout.addWidget(StatCard("Total Books", 1250), 1)
        cards_layout.addWidget(StatCard("Members", 340), 1)
        cards_layout.addWidget(StatCard("Books Borrowed", 180), 1)
        cards_layout.addWidget(StatCard("Overdue Books", 15), 1)
        
        dashboard_layout.addWidget(cards_container)

        dashboard_layout.addSpacing(24)
        recent_label = QLabel("Recent Activity")
        recent_label.setStyleSheet("font-size: 18px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 700; margin-bottom: 8px;")
        dashboard_layout.addWidget(recent_label, alignment=Qt.AlignLeft)

        table = QTableWidget(8, 5)  
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
        activity_data = [
            ("The Secret Garden", "Frances Hodgson Burnett", "Emily Carter", "2024-03-15", "Borrowed"),
            ("Pride and Prejudice", "Jane Austen", "David Lee", "2024-03-20", "Available"),
            ("To Kill a Mockingbird", "Harper Lee", "Olivia Brown", "2024-03-10", "Overdue"),
            ("1984", "George Orwell", "Ethan Clark", "2024-03-25", "Borrowed"),
            ("The Great Gatsby", "F. Scott Fitzgerald", "Sophia Green", "2024-03-18", "Available"),
            ("The Catcher in the Rye", "J.D. Salinger", "Mia Davis", "2024-03-22", "Borrowed"),
            ("The Hunger Games", "Suzanne Collins", "Julia Martin", "2024-03-12", "Overdue"),
            ("The Fault in Our Stars", "John Green", "Noah Hall", "2024-03-28", "Available"),
        ]
        for row, (title, author, borrower, due_date, status) in enumerate(activity_data):
            table.setItem(row, 0, QTableWidgetItem(title))
            table.setItem(row, 1, QTableWidgetItem(author))
            table.setItem(row, 2, QTableWidgetItem(borrower))
            table.setItem(row, 3, QTableWidgetItem(due_date))
            status_badge = StatusBadge(status)
            wrapper = QWidget()
            layout = QHBoxLayout(wrapper)
            layout.addWidget(status_badge)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            wrapper.setLayout(layout)
            table.setCellWidget(row, 4, wrapper)
        dashboard_layout.addWidget(table)
    
    # Removed IT Semesters section as requested
        dashboard_layout.addStretch()
        return scroll

    def show_dashboard(self):
        self.pages_stack.setCurrentWidget(self.dashboard_content)

    def show_user_management(self):
        self.user_management_page.load_users()
        self.pages_stack.setCurrentWidget(self.user_management_page)

    def show_add_user_page(self):
        self.pages_stack.setCurrentWidget(self.add_user_page)

    def show_book_inventory(self):
        # Load books when navigating to the page to ensure fresh data and avoid early popups
        try:
            if hasattr(self.book_inventory_page, 'load_books'):
                self.book_inventory_page.load_books()
        except Exception as e:
            print(f"Error loading books on navigation: {e}")
        self.pages_stack.setCurrentWidget(self.book_inventory_page)

    def show_borrow_return(self):
        self.pages_stack.setCurrentWidget(self.borrow_return_page)

    def show_report_generation(self):
        self.pages_stack.setCurrentWidget(self.report_generation_page)

    def show_fine_management(self):
        self.pages_stack.setCurrentWidget(self.fine_management_page)
        
    def show_notification_reminder(self):
        """Switch to the notification and reminder page"""
        self.pages_stack.setCurrentWidget(self.notification_reminder_page)
        self.setWindowTitle("Notification & Reminders - Intelli Libraria")
        
    def show_reservation_management(self):
        """Switch to the reservation management page"""
        self.pages_stack.setCurrentWidget(self.reservation_management_page)

    def show_user_feedback(self):
        self.pages_stack.setCurrentWidget(self.user_feedback_page)