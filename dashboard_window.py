from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QSizePolicy, QGroupBox, QHeaderView, QApplication, QLineEdit, QListWidget, QListWidgetItem,
    QGridLayout, QSpacerItem, QScrollArea, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor
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
    def __init__(self, icon, text, active=False, parent=None):
        super().__init__(parent)
        self.setText(f"  {text}")
        self.setIcon(icon)
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QSize(20, 20))
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 8px 8px 8px;
                font-size: 15px;
                color: #2c3e50;
                border: none;
                background: transparent;
                border-radius: 6px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
            QPushButton:checked {
                background-color: #dfe6e9;
                font-weight: bold;
            }
        """)

class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)
        self.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 8px;
                border: 1px solid #232b36;
            }
            QLabel {
                border: none;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignVCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Normal))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title_label.setStyleSheet("color: #232b36; border: none;")

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        value_label.setStyleSheet("color: #232b36; border: none;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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

class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setStyleSheet("background: #f7f9fa; border-right: 1px solid #e5e7eb;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 8, 24)
        layout.setSpacing(8)

        logo_label = QLabel("Intelli Libraria")
        logo_label.setFont(QFont("Arial", 18, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: #2c3e50; padding-bottom: 20px;")
        layout.addWidget(logo_label)

        self.buttons = []
        button_definitions = [
            ("Dashboard", "dashboard"),
            ("User Management", "user_management"),
            ("Book Inventory", "book_inventory"),
            ("Borrow & Return", "borrow_return"),
            ("Report Generation", "report_generation"),
            ("Fine Management", "fine_management"),
            ("Notification & Reminder", "notification_reminder"),
            ("Reservation Management", "reservation_management"),
            ("User Feedback", "user_feedback"),
        ]

        for text, page_name in button_definitions:
            icon = QIcon(f'assets/{page_name}.png')
            btn = SidebarButton(icon, text)
            btn.page_name = page_name
            layout.addWidget(btn)
            self.buttons.append(btn)
            btn.clicked.connect(lambda checked, b=btn: self.select_button(b))
        layout.addStretch(1)

    def select_button(self, selected_btn):
        for btn in self.buttons:
            btn.setChecked(btn == selected_btn)

class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intelli Libraria")
        self.resize(1200, 800)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet("QWidget { background-color: #f8f9fa; }")
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

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
        if not sender: return

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

        action = page_map.get(sender.page_name)
        if action:
            action()

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

        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)
        cards_row.addWidget(StatCard("Total Books", 1250))
        cards_row.addWidget(StatCard("Members", 340))
        cards_row.addWidget(StatCard("Books Borrowed", 180))
        cards_row.addWidget(StatCard("Overdue Books", 15))
        dashboard_layout.addLayout(cards_row)

        dashboard_layout.addSpacing(24)
        recent_label = QLabel("Recent Activity")
        recent_label.setStyleSheet("font-size: 18px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 700; margin-bottom: 8px;")
        dashboard_layout.addWidget(recent_label, alignment=Qt.AlignLeft)

        table = QTableWidget(5, 5)
        table.setHorizontalHeaderLabels(["Book Title", "Author", "Borrower", "Due Date", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(54)
        table.setStyleSheet("""
            QTableWidget { background: #fff; border-radius: 16px; font-size: 16px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; border: 1.5px solid #e5e7eb; padding: 0px; alternate-background-color: #f9fafb; }
            QTableWidget::item { border-bottom: 1px solid #e5e7eb; padding: 10px 8px; }
            QHeaderView::section { background: #f9fafb; color: #232b36; font-weight: 700; font-size: 16px; border: none; border-bottom: 1.5px solid #e5e7eb; padding: 18px 8px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; }
        """)
        activity_data = [
            ("The Secret Garden", "Frances Hodgson Burnett", "Emily Carter", "2024-03-15", "Borrowed"),
            ("Pride and Prejudice", "Jane Austen", "David Lee", "2024-03-20", "Available"),
            ("To Kill a Mockingbird", "Harper Lee", "Olivia Brown", "2024-03-10", "Overdue"),
            ("1984", "George Orwell", "Ethan Clark", "2024-03-25", "Borrowed"),
            ("The Great Gatsby", "F. Scott Fitzgerald", "Sophia Green", "2024-03-18", "Available"),
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
        self.pages_stack.setCurrentWidget(self.book_inventory_page)

    def show_borrow_return(self):
        self.pages_stack.setCurrentWidget(self.borrow_return_page)

    def show_report_generation(self):
        self.pages_stack.setCurrentWidget(self.report_generation_page)

    def show_fine_management(self):
        self.pages_stack.setCurrentWidget(self.fine_management_page)

    def show_notification_reminder(self):
        self.pages_stack.setCurrentWidget(self.notification_reminder_page)

    def show_reservation_management(self):
        self.pages_stack.setCurrentWidget(self.reservation_management_page)

    def show_user_feedback(self):
        self.pages_stack.setCurrentWidget(self.user_feedback_page)
 