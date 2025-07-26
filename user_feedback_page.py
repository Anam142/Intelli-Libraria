from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSlider, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt5.QtCore import Qt

class UserFeedbackPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        # Use a scroll area for the whole page
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(32, 24, 32, 24)
        self.layout.setSpacing(0)
        self.initUI()
        self.scroll.setWidget(self.main_widget)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)

    def initUI(self):
        # Heading
        heading = QLabel("User Feedback")
        heading.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36;")
        self.layout.addWidget(heading, alignment=Qt.AlignLeft)
        subtext = QLabel("Collect and manage user feedback to improve our services.")
        subtext.setStyleSheet("font-size: 15px; color: #8a8f98; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 400; margin-bottom: 24px; margin-top: 0px;")
        self.layout.addWidget(subtext, alignment=Qt.AlignLeft)

        # Submit Feedback Section
        form_section = QVBoxLayout()
        form_section.setSpacing(10)
        form_label = QLabel("Submit Feedback")
        form_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #232b36; margin-top: 24px;")
        form_section.addWidget(form_label)

        # Centered form container
        form_container = QWidget()
        form_container.setMaximumWidth(500)
        form_container.setStyleSheet("background: transparent;")
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(0, 0, 0, 0)
        form_container_layout.setSpacing(10)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36;")
        form_container_layout.addWidget(user_id_label)
        self.user_id_input = QLineEdit()
        self.user_id_input.setStyleSheet("background: #fff; border-radius: 10px; border: 1.5px solid #e5e7eb; padding: 12px 16px; font-size: 15px; margin-bottom: 8px;")
        form_container_layout.addWidget(self.user_id_input)

        # Feedback
        feedback_label = QLabel("Feedback")
        feedback_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #232b36;")
        form_container_layout.addWidget(feedback_label)
        self.feedback_input = QTextEdit()
        self.feedback_input.setStyleSheet("background: #fff; border-radius: 10px; border: 1.5px solid #e5e7eb; padding: 12px 16px; font-size: 15px; margin-bottom: 8px;")
        self.feedback_input.setPlaceholderText("Enter your feedback here")
        form_container_layout.addWidget(self.feedback_input)

        form_section.addWidget(form_container)
        self.layout.addLayout(form_section)

        # Feedback List Section
        list_label = QLabel("Feedback List")
        list_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #232b36; margin-top: 32px;")
        self.layout.addWidget(list_label, alignment=Qt.AlignLeft)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search feedback")
        self.search_input.setStyleSheet("background: #f3f4f6; border-radius: 10px; border: none; padding: 14px 16px; font-size: 15px; margin-bottom: 12px; margin-top: 8px;")
        self.layout.addWidget(self.search_input)

        # Feedback Table (wider)
        self.table = QTableWidget(3, 5)
        self.table.setMinimumWidth(1000)
        self.table.setHorizontalHeaderLabels(["Date", "User", "Feedback", "Status", "Actions"])
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
                border-radius: 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1.5px solid #e5e7eb;
                padding: 0px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 0px 0px;
            }
            QHeaderView::section {
                background: #fff;
                color: #232b36;
                font-weight: 700;
                font-size: 15px;
                border: none;
                padding: 12px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        feedback_data = [
            ("2024-03-15", "User A", "More study spaces", "Pending", "Respond"),
            ("2024-03-14", "User B", "Website down", "Reviewed", "Respond"),
            ("2024-03-13", "User C", "Helpful staff", "Resolved", "Respond"),
        ]
        for row, (date, user, feedback, status, action) in enumerate(feedback_data):
            self.table.setItem(row, 0, QTableWidgetItem(date))
            self.table.setItem(row, 1, QTableWidgetItem(user))
            self.table.setItem(row, 2, QTableWidgetItem(feedback))
            status_label = QLabel(status)
            if status == "Pending":
                status_label.setStyleSheet("background: #f3f4f6; color: #232b36; border-radius: 12px; font-weight: 600; padding: 4px 18px;")
            elif status == "Reviewed":
                status_label.setStyleSheet("background: #f3f4f6; color: #1976d2; border-radius: 12px; font-weight: 600; padding: 4px 18px;")
            elif status == "Resolved":
                status_label.setStyleSheet("background: #f3f4f6; color: #059669; border-radius: 12px; font-weight: 600; padding: 4px 18px;")
            status_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 3, status_label)
            action_btn = QPushButton(action)
            action_btn.setStyleSheet("background: #f3f4f6; color: #1976d2; font-size: 14px; font-weight: 600; border-radius: 12px; padding: 4px 18px; border: none;")
            self.table.setCellWidget(row, 4, action_btn)
        self.layout.addWidget(self.table) 