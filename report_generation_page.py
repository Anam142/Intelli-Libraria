from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QGroupBox, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QDateEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class ReportGenerationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 16, 32, 32)  # Reduce top margin from 32 to 16
        main_layout.setSpacing(0)

        # Title
        title = QLabel("Report Generation")
        title.setFont(QFont("Inter", 28, QFont.Bold))
        title.setStyleSheet("color: #232b36; margin-bottom: 8px;")
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Generate and export reports on library operations.")
        subtitle.setFont(QFont("Inter", 12))
        subtitle.setStyleSheet("color: #8a8f98; margin-top: 0px; margin-bottom: 16px;")
        main_layout.addWidget(subtitle)

        # Report Type Section
        report_type_label = QLabel("Report Type")
        report_type_label.setFont(QFont("Inter", 15, QFont.Bold))
        report_type_label.setStyleSheet("margin-bottom: 8px; margin-top: 0px;")  # Remove extra top margin
        main_layout.addWidget(report_type_label)

        report_type_group = QGroupBox()
        report_type_group.setStyleSheet("QGroupBox { border: none; }")
        report_type_layout = QVBoxLayout(report_type_group)
        report_type_layout.setSpacing(0)
        report_type_layout.setContentsMargins(0, 0, 0, 0)
        self.report_buttons = []
        self.button_group = QButtonGroup(self)
        report_types = [
            ("Inventory Status", "Total books, available books, etc."),
            ("Borrowed Books", "Current and historical borrowed books"),
            ("Overdue Books", "Books past their due date"),
            ("User Activity", "User borrowing and return history"),
        ]
        for i, (label, desc) in enumerate(report_types):
            row = QHBoxLayout()
            row.setSpacing(16)
            row.setContentsMargins(24, 0, 24, 0)
            radio = QRadioButton()
            radio.setStyleSheet("margin: 0 0 0 0;")
            self.button_group.addButton(radio, i)
            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            text_col.setContentsMargins(0, 0, 0, 0)
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Inter", 13, QFont.Bold))
            label_widget.setStyleSheet("color: #232b36; background: none; border: none; margin-bottom: 0px; padding-bottom: 0px;")
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Inter", 11))
            desc_label.setStyleSheet("color: #8a8f98; background: none; border: none; margin-top: 0px; padding-top: 0px;")
            text_col.addWidget(label_widget)
            text_col.addWidget(desc_label)
            row.addWidget(radio)
            row.addLayout(text_col)
            row.addStretch(1)
            row_widget = QWidget()
            row_widget.setLayout(row)
            row_widget.setFixedHeight(64)
            row_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row_widget.setStyleSheet(f'''
                QWidget {{
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                    background: #fff;
                    margin-bottom: 1px;
                    padding: 0 0 0 0;
                }}
            ''')
            # Remove centering, restore left alignment
            row.setAlignment(Qt.AlignLeft)
            report_type_layout.addWidget(row_widget)
            self.report_buttons.append(radio)
        main_layout.addWidget(report_type_group)

        # Generate Report Button (top right)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.setStyleSheet("background: #1976d2; color: #fff; font-size: 15px; font-weight: bold; border-radius: 8px; padding: 8px 24px;")
        btn_row.addWidget(self.generate_btn)
        btn_row_widget = QWidget()
        btn_row_widget.setLayout(btn_row)
        btn_row_widget.setStyleSheet("margin-bottom: 16px;")
        main_layout.addWidget(btn_row_widget)

        # Report Preview Table (always visible, full width)
        preview_label = QLabel("Report Preview")
        preview_label.setFont(QFont("Inter", 15, QFont.Bold))
        preview_label.setStyleSheet("margin-bottom: 8px; margin-top: 0px;")  # Remove extra top margin
        main_layout.addWidget(preview_label)

        self.table = QTableWidget(5, 5)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "ISBN", "Available", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border-collapse: separate;
                border-spacing: 0 8px;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 0px 0px;
            }
            QHeaderView::section {
                background: #f5f5f5;
                color: #232b36;
                font-weight: 700;
                font-size: 15px;
                border: none;
                padding: 12px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        main_layout.addWidget(self.table)

        # Example data for preview
        data = [
            ("The Great Adventure", "Alex Turner", "978-0321765723", "15", "20"),
            ("Mystery of the Hidden Key", "Olivia Bennett", "978-0451419439", "8", "10"),
            ("Journey Through Time", "Ethan Carter", "978-0060558123", "12", "15"),
            ("Secrets of the Ancient World", "Sophia Davis", "978-0385534208", "5", "5"),
            ("Echoes of the Past", "Liam Foster", "978-0316037842", "20", "25"),
        ]
        self.table.setRowCount(len(data))
        for row, (title, author, isbn, available, total) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(title))
            author_item = QTableWidgetItem(author)
            author_item.setForeground(QColor("#8a8f98"))
            self.table.setItem(row, 1, author_item)
            self.table.setItem(row, 2, QTableWidgetItem(isbn))
            self.table.setItem(row, 3, QTableWidgetItem(available))
            self.table.setItem(row, 4, QTableWidgetItem(total)) 