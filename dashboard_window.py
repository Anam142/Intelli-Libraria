from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System - Dashboard")
        self.showMaximized()
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top header bar
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #3f51b5;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(0)
        title = QLabel(" Intelli Libraria")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        header_layout.addWidget(title, alignment=Qt.AlignVCenter)
        header_layout.addStretch(1)
        user_label = QLabel("Welcome Admin   ")
        user_label.setStyleSheet("color: white; font-size: 14px;")
        header_layout.addWidget(user_label, alignment=Qt.AlignVCenter)
        main_layout.addWidget(header)

        # Main content area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("background-color: #23272e;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        # Sidebar buttons
        nav_buttons = [
            ("Home Page", "#e53935"),
            ("LMS Dashboard", "#23272e"),
            ("Manage Book", "#23272e"),
            ("Manage Students", "#23272e"),
            ("Issue Book", "#23272e"),
            ("Return Book", "#23272e"),
            ("View Record", "#23272e"),
            ("View Issued Book", "#23272e"),
            ("Defaulter List", "#23272e"),
            ("Logout", "#3949ab")
        ]
        for text, color in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background-color: {color}; color: white; border: none; font-size: 15px; padding: 12px; text-align: left;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch(1)
        content_layout.addWidget(sidebar)

        # Main dashboard area
        dashboard_area = QVBoxLayout()
        dashboard_area.setContentsMargins(20, 20, 20, 20)
        dashboard_area.setSpacing(15)

        # Summary cards
        cards_layout = QHBoxLayout()
        card_data = [
            ("No. of Books", "4", "#e53935"),
            ("No. of Students", "3", "#8e24aa"),
            ("Issued Books", "3", "#3949ab"),
            ("Defaulter List", "1", "#c62828")
        ]
        for label, value, color in card_data:
            card = QFrame()
            card.setFixedSize(180, 70)
            card.setStyleSheet(f"background: {color}; border-radius: 8px;")
            v = QVBoxLayout(card)
            v.setContentsMargins(10, 5, 10, 5)
            v.setSpacing(0)
            l1 = QLabel(label)
            l1.setStyleSheet("color: white; font-size: 13px;")
            l2 = QLabel(value)
            l2.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
            v.addWidget(l1)
            v.addWidget(l2)
            cards_layout.addWidget(card)
        cards_layout.addStretch(1)
        dashboard_area.addLayout(cards_layout)

        # Lower area: tables and chart
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(20)

        # Student Details Table
        student_table = QTableWidget(3, 4)
        student_table.setHorizontalHeaderLabels(["Student Id", "Name", "Course", "Branch"])
        student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        student_table.setSelectionMode(QTableWidget.NoSelection)
        student_table.setFixedSize(340, 120)
        student_table.verticalHeader().setVisible(False)
        student_table.horizontalHeader().setStyleSheet("font-weight: bold; background: #e3e3e3;")
        students = [
            ("1", "Priyam", "B.TECH", "ECE"),
            ("2", "Bikash", "B.TECH", "ECE"),
            ("3", "Aditya", "B.TECH", "CSE")
        ]
        for row, data in enumerate(students):
            for col, val in enumerate(data):
                student_table.setItem(row, col, QTableWidgetItem(val))
        lower_layout.addWidget(student_table)

        # Book Details Table
        book_table = QTableWidget(4, 4)
        book_table.setHorizontalHeaderLabels(["Book Id", "Book Name", "Author", "Quantity"])
        book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        book_table.setSelectionMode(QTableWidget.NoSelection)
        book_table.setFixedSize(340, 140)
        book_table.verticalHeader().setVisible(False)
        book_table.horizontalHeader().setStyleSheet("font-weight: bold; background: #e3e3e3;")
        books = [
            ("1", "Java", "Author name 1", "2"),
            ("2", "Python", "Author name 2", "3"),
            ("3", "PHP", "phpauthor", "4"),
            ("4", "C Language", "C author", "6")
        ]
        for row, data in enumerate(books):
            for col, val in enumerate(data):
                book_table.setItem(row, col, QTableWidgetItem(val))
        lower_layout.addWidget(book_table)

        # Pie Chart (matplotlib)
        chart_frame = QFrame()
        chart_frame.setFixedSize(300, 180)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        fig = Figure(figsize=(3, 2))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        labels = ['Java', 'Python', 'PHP', 'C Language']
        sizes = [2, 3, 4, 6]
        colors = ['#e53935', '#8e24aa', '#3949ab', '#c62828']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.0f', startangle=90)
        ax.set_title('Issue Book Details', fontsize=10)
        chart_layout.addWidget(canvas)
        lower_layout.addWidget(chart_frame)

        dashboard_area.addLayout(lower_layout)
        content_layout.addLayout(dashboard_area)
        main_layout.addLayout(content_layout) 