from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QGroupBox, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import database

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
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: #1976d2;
                color: #fff;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 24px;
                min-width: 180px;
            }
            QPushButton:hover {
                background: #1565c0;
            }
            QPushButton:pressed {
                background: #0d47a1;
            }
            QPushButton:disabled {
                background: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
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
                border-collapse: collapse;
                margin-top: 0px;
                margin-bottom: 0px;
            }
            QTableWidget::item {
                border-bottom: 1px solid #e5e7eb;
                padding: 12px 8px;
            }
            QTableWidget::item:first-child {
                padding-left: 16px;
            }
            QTableWidget::item:last-child {
                padding-right: 16px;
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
            
    def generate_report(self):
        """Generate report based on selected report type"""
        # Get the selected report type
        selected_id = self.button_group.checkedId()
        if selected_id == -1:
            QMessageBox.warning(self, "No Selection", "Please select a report type first.")
            return
            
        # Get the selected report type text
        selected_report = self.report_buttons[selected_id].parent().findChild(QLabel).text()
        
        # Show loading state
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        
        # Simulate report generation delay
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self._show_report_preview(selected_report))
    
    def _show_report_preview(self, report_type):
        """Show the preview of the generated report"""
        # Reset button state
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Report")
        
        # Update the preview based on report type
        if report_type == "Inventory Status":
            self._show_inventory_report()
        elif report_type == "Borrowed Books":
            self._show_borrowed_books_report()
        elif report_type == "Overdue Books":
            self._show_overdue_books_report()
        elif report_type == "User Activity":
            self._show_user_activity_report()
    
    def _show_inventory_report(self):
        """Show inventory status report"""
        # Set table headers
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "ISBN", "Available", "Total"])
        
        # Live data from database
        try:
            rows = database.execute_query(
                "SELECT title, author, COALESCE(isbn,'') AS isbn, COALESCE(stock,0) AS stock FROM books ORDER BY title"
            )
            data = [(r["title"], r["author"], r["isbn"], str(r["stock"]), str(r["stock"])) for r in rows]
        except Exception:
            data = []
        
        self._populate_table(data)
    
    def _show_borrowed_books_report(self):
        """Show borrowed books report"""
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Title", "Borrower", "Borrow Date", "Due Date", "Days Left", "Status"])
        
        # Try to load from transactions if available
        data = []
        try:
            # Check if transactions exists
            rows = database.execute_query(
                """
                SELECT b.title AS title,
                       u.full_name AS borrower,
                       t.issue_date AS borrow_date,
                       t.due_date AS due_date,
                       t.status AS status
                FROM transactions t
                JOIN books b ON b.id = t.book_id
                JOIN users u ON u.id = t.user_id
                WHERE LOWER(t.status) IN ('issued','borrowed')
                ORDER BY t.issue_date DESC
                """
            )
            from datetime import date
        today = date.today()
            for r in rows:
                due = r.get("due_date") or ""
                # Days left calculation best-effort
                try:
                    from datetime import datetime
                    days_left = (datetime.strptime(due, "%Y-%m-%d").date() - today).days
                except Exception:
                    days_left = ""
                data.append((r["title"], r.get("borrower", ""), r.get("borrow_date", ""), due, str(days_left), r.get("status", "")))
        except Exception:
            data = []
        
        self._populate_table(data)
    
    def _show_overdue_books_report(self):
        """Show overdue books report"""
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Borrower", "Due Date", "Days Overdue", "Fine"])
        
        data = []
        try:
            rows = database.execute_query(
                """
                SELECT b.title AS title,
                       u.full_name AS borrower,
                       t.due_date AS due_date
                FROM transactions t
                JOIN books b ON b.id = t.book_id
                JOIN users u ON u.id = t.user_id
                WHERE LOWER(t.status) = 'overdue'
                ORDER BY t.due_date DESC
                """
            )
            from datetime import date, datetime
        today = date.today()
            for r in rows:
                due = r.get("due_date") or ""
                try:
                    days_over = (today - datetime.strptime(due, "%Y-%m-%d").date()).days
                except Exception:
                    days_over = ""
                data.append((r["title"], r.get("borrower", ""), due, str(days_over), ""))
        except Exception:
            data = []
        
        self._populate_table(data)
    
    def _show_user_activity_report(self):
        """Show user activity report"""
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["User", "Books Borrowed", "Books Returned", "Overdue Books", "Total Fines"])
        
        # Sample data
        data = [
            ("John Doe", "12", "10", "2", "$5.00"),
            ("Jane Smith", "8", "7", "1", "$2.50"),
            ("Bob Johnson", "15", "14", "0", "$0.00"),
        ]
        
        self._populate_table(data)
    
    def _populate_table(self, data):
        """Populate the table with data"""
        self.table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                # Style overdue items in red
                if value in ["Overdue", "Due Today"] or (isinstance(value, str) and value.startswith("-")):
                    item.setForeground(QColor("#d32f2f"))
                self.table.setItem(row, col, item)