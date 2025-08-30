from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup, QGroupBox, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QDateEdit, 
    QMessageBox, QFileDialog, QSpinBox, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QBrush
import database
import csv
import os
from datetime import datetime

class ReportGenerationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_report_type = None
        self.current_report_data = None
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

        # Report Controls
        controls_row = QHBoxLayout()
        
        # Days filter (for User Activity report)
        self.days_filter = QSpinBox()
        self.days_filter.setRange(1, 365)
        self.days_filter.setValue(30)
        self.days_filter.setMaximumWidth(80)
        self.days_filter.setVisible(False)  # Hidden by default
        
        days_label = QLabel("Days:")
        days_label.setVisible(False)
        
        # Generate Report Button
        self.generate_btn = QPushButton("Generate Report")
        
        # Export Button
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.setVisible(False)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #4caf50;
                color: #fff;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 24px;
                min-width: 150px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: #43a047;
            }
            QPushButton:disabled {
                background: #e0e0e0;
                color: #9e9e9e;
            }
        """)
        self.export_btn.clicked.connect(self.export_to_csv)
        
        # Add controls to layout
        controls_row.addStretch(1)
        controls_row.addWidget(days_label)
        controls_row.addWidget(self.days_filter)
        controls_row.addWidget(self.generate_btn)
        controls_row.addWidget(self.export_btn)
        controls_row_widget = QWidget()
        controls_row_widget.setLayout(controls_row)
        controls_row_widget.setStyleSheet("margin-bottom: 16px;")
        
        # Connect report type change to update UI
        self.button_group.buttonClicked.connect(self.on_report_type_changed)
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
        
        # Add controls to main layout
        main_layout.addWidget(controls_row_widget)

        # Report Preview Table (always visible, full width)
        preview_label = QLabel("Report Preview")
        preview_label.setFont(QFont("Inter", 15, QFont.Bold))
        preview_label.setStyleSheet("margin-bottom: 8px; margin-top: 0px;")  # Remove extra top margin
        main_layout.addWidget(preview_label)

        # Initialize table with 6 columns (Actions column will contain the Delete button)
        self.table = QTableWidget(5, 6)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "ISBN", "Available", "Total", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        # Increase row height to ensure buttons are fully visible
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.verticalHeader().setMinimumSectionSize(48)
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
                padding: 4px 8px;  /* Reduced vertical padding to give more space for the button */
                margin: 0;
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

        # Clear the table initially
        self.table.setRowCount(0)

    def on_report_type_changed(self):
        selected_index = self.button_group.checkedId()
        if selected_index == 3:  # User Activity
            self.days_filter.setVisible(True)
            self.days_filter.parent().findChild(QLabel).setVisible(True)
            self.export_btn.setVisible(True)
        else:
            self.days_filter.setVisible(False)
            self.days_filter.parent().findChild(QLabel).setVisible(False)
            self.export_btn.setVisible(False)

    def generate_report(self):
        """Generate report based on selected report type"""
        selected_index = self.button_group.checkedId()
        if selected_index == -1:
            QMessageBox.warning(self, "No Selection", "Please select a report type.")
            return
            
        report_types = [
            "Inventory Status",
            "Borrowed Books",
            "Overdue Books",
            "User Activity"
        ]
        
        self.current_report_type = report_types[selected_index]
        
        try:
            if selected_index == 2:  # Overdue Books
                self.generate_overdue_books_report()
            elif selected_index == 3:  # User Activity
                self.generate_user_activity_report()
            else:
                QMessageBox.information(self, "Report Generated", 
                                     f"{self.current_report_type} report will be implemented soon!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def generate_overdue_books_report(self):
        """Generate and display the overdue books report"""
        try:
            # Clear existing data
            self.table.setRowCount(0)
            
            # Set table headers
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels(["Title", "Borrower", "Borrow Date", "Due Date", "Days Overdue", "Actions"])
            
            # Fetch data from database
            rows = database.get_overdue_books()
            
            if not rows:
                QMessageBox.information(self, "No Overdue Books", "There are currently no overdue books.")
                return
            
            # Populate table with data
            self.table.setRowCount(len(rows))
            for row, record in enumerate(rows):
                self.table.setItem(row, 0, QTableWidgetItem(record['book_title']))
                self.table.setItem(row, 1, QTableWidgetItem(record['user_name']))
                self.table.setItem(row, 2, QTableWidgetItem(record['issue_date']))
                self.table.setItem(row, 3, QTableWidgetItem(record['due_date']))
                
                # Calculate and format days overdue
                days_overdue = record.get('days_overdue', 0)
                days_item = QTableWidgetItem(str(days_overdue))
                if days_overdue > 30:
                    days_item.setForeground(QColor('#ef4444'))  # Red for very overdue
                elif days_overdue > 14:
                    days_item.setForeground(QColor('#f59e0b'))  # Orange for moderately overdue
                self.table.setItem(row, 4, days_item)
                
                # Add action buttons
                action_buttons = QWidget()
                layout = QHBoxLayout(action_buttons)
                layout.setContentsMargins(5, 0, 5, 0)
                
                # Send Reminder button
                remind_btn = QPushButton("Remind")
                remind_btn.setFixedSize(80, 28)
                remind_btn.setProperty('transaction_id', record['transaction_id'])
                remind_btn.setStyleSheet("""
                    QPushButton {
                        background: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background: #2563eb;
                    }
                """)
                remind_btn.clicked.connect(self._on_send_reminder)
                
                layout.addWidget(remind_btn)
                layout.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(row, 5, action_buttons)
                
            # Adjust column widths
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            
            # Enable export button
            self.export_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load overdue books report: {str(e)}")

    def generate_user_activity_report(self):
        """Generate and display the user activity report"""
        try:
            # Clear existing data
            self.table.setRowCount(0)
            
            # Set table headers
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "User", "Email", "Role", "Books Borrowed", "Overdue Books", "Last Activity"
            ])
            
            # Fetch data from database
            days = self.days_filter.value()
            rows = database.get_user_activity(days)
            
            if not rows:
                QMessageBox.information(self, "No Activity", 
                                     f"No user activity found in the last {days} days.")
                return
            
            # Populate table with data
            self.table.setRowCount(len(rows))
            for row, record in enumerate(rows):
                self.table.setItem(row, 0, QTableWidgetItem(record['user_name']))
                self.table.setItem(row, 1, QTableWidgetItem(record['user_email']))
                self.table.setItem(row, 2, QTableWidgetItem(record['user_role']))
                
                # Format books borrowed
                total_borrowed = record.get('total_borrowed', 0)
                total_returned = record.get('books_returned', 0)
                overdue_count = record.get('overdue_books', 0)
                
                borrowed_text = f"{total_returned} returned"
                if total_borrowed > total_returned:
                    borrowed_text = f"{total_borrowed} ({total_returned} returned)"
                
                self.table.setItem(row, 3, QTableWidgetItem(borrowed_text))
                
                # Format overdue books with color coding
                overdue_item = QTableWidgetItem(str(overdue_count))
                if overdue_count > 0:
                    overdue_item.setForeground(QColor('#ef4444'))  # Red for overdue
                self.table.setItem(row, 4, overdue_item)
                
                # Format last activity date
                last_activity = record.get('last_activity', '')
                if last_activity:
                    try:
                        # Format date if it's in ISO format
                        from datetime import datetime
                        last_activity = datetime.strptime(last_activity, '%Y-%m-%d').strftime('%b %d, %Y')
                    except:
                        pass
                self.table.setItem(row, 5, QTableWidgetItem(last_activity or 'N/A'))
                
            # Adjust column widths
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
            
            # Enable export button
            self.export_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user activity report: {str(e)}")
            import traceback
            traceback.print_exc()

    def export_to_csv(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "No Data", "No data to export. Please generate a report first.")
            return
            
        # Get suggested filename based on report type
        default_name = f"{self.current_report_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Report", 
            os.path.join(os.path.expanduser("~"), "Downloads", default_name),
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = []
                for col in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Write data rows
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            # Check for widget in cell (like buttons)
                            widget = self.table.cellWidget(row, col)
                            if widget is not None:
                                row_data.append("")
                            else:
                                row_data.append("")
                    writer.writerow(row_data)
                    
            QMessageBox.information(self, "Export Successful", 
                                 f"Report has been exported to:\n{filename}")
                                  
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                              f"Failed to export report: {str(e)}")

    def _on_send_reminder(self):
        """Handle send reminder button click"""
        button = self.sender()
        if not button:
            return
            
        transaction_id = button.property('transaction_id')
        if not transaction_id:
            return
            
        # Get the row that contains this button
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 5) and self.table.cellWidget(row, 5).findChild(QPushButton) == button:
                user_name = self.table.item(row, 1).text()
                book_title = self.table.item(row, 0).text()
                due_date = self.table.item(row, 3).text()
                days_overdue = self.table.item(row, 4).text()
                
                # In a real app, this would send an email or notification
                QMessageBox.information(
                    self, 
                    "Reminder Sent", 
                    f"Reminder sent to {user_name} about overdue book:\n"
                    f"Title: {book_title}\n"
                    f"Due Date: {due_date}\n"
                    f"Days Overdue: {days_overdue}"
                )
                break
        
        # Set table headers
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Title", "Author", "ISBN", "Available", "Total", "Actions"])
        
        try:
            # Fetch data from database
            rows = database.execute_query(
                """
                SELECT title, author, isbn, stock as available, 
                       (SELECT COUNT(*) FROM books b2 WHERE b2.isbn = b1.isbn) as total
                FROM books b1
                GROUP BY isbn
                ORDER BY title
                """
            )
            
            # Populate table with data
            self.table.setRowCount(len(rows))
            for row, book in enumerate(rows):
                self.table.setItem(row, 0, QTableWidgetItem(book['title']))
                self.table.setItem(row, 1, QTableWidgetItem(book['author']))
                self.table.setItem(row, 2, QTableWidgetItem(book['isbn']))
                self.table.setItem(row, 3, QTableWidgetItem(str(book['available'])))
                self.table.setItem(row, 4, QTableWidgetItem(str(book['total'])))

                # Add delete button
                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(80, 32)  # Fixed size for consistency
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background: #ef4444;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 13px;
                        font-weight: 500;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background: #dc2626;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    }
                    QPushButton:pressed {
                        background: #b91c1c;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=row: self._on_delete_clicked(r))
                # Create a container widget for proper centering
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.addWidget(delete_btn)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)
                self.table.setCellWidget(row, 5, container)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory report: {str(e)}")

    def _show_borrowed_books_report(self):
        """Show borrowed books report"""
        # Clear existing data
        self.table.setRowCount(0)
        
        # Set table headers
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Title", "Borrower", "Borrow Date", "Due Date", "Days Left", "Status", "Actions"])
        
        try:
            # Fetch data from database
            rows = database.execute_query(
                """
                SELECT b.title, u.full_name as borrower, t.issue_date, t.due_date, t.status
                FROM transactions t
                JOIN books b ON t.book_id = b.id
                JOIN users u ON t.user_id = u.id
                WHERE t.status IN ('Borrowed', 'Overdue')
                ORDER BY t.due_date
                """
            )
            
            # Populate table with data
            self.table.setRowCount(len(rows))
            for row, record in enumerate(rows):
                self.table.setItem(row, 0, QTableWidgetItem(record['title']))
                self.table.setItem(row, 1, QTableWidgetItem(record['borrower']))
                self.table.setItem(row, 2, QTableWidgetItem(record['issue_date']))
                self.table.setItem(row, 3, QTableWidgetItem(record['due_date']))
                
                # Calculate days left
                from datetime import datetime
                try:
                    due_date = datetime.strptime(record['due_date'], '%Y-%m-%d').date()
                    today = datetime.now().date()
                    days_left = (due_date - today).days
                    status = "Overdue" if days_left < 0 else "Borrowed"
                    self.table.setItem(row, 4, QTableWidgetItem(str(abs(days_left))))
                    self.table.setItem(row, 5, QTableWidgetItem(status))
                except Exception as e:
                    self.table.setItem(row, 4, QTableWidgetItem("N/A"))
                    self.table.setItem(row, 5, QTableWidgetItem(record['status']))
                
                # Add delete button with consistent styling
                delete_btn = QPushButton("Delete")
                delete_btn.setFixedSize(80, 32)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background: #ef4444;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 13px;
                        font-weight: 500;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background: #dc2626;
                        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    }
                    QPushButton:pressed {
                        background: #b91c1c;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, r=row: self._on_delete_clicked(r))
                
                # Create a container widget for proper centering
                container = QWidget()
                layout = QHBoxLayout(container)
                layout.addWidget(delete_btn)
                layout.setAlignment(Qt.AlignCenter)
                layout.setContentsMargins(0, 0, 0, 0)
                container.setLayout(layout)
                self.table.setCellWidget(row, 6, container)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load borrowed books report: {str(e)}")

    def _show_report_preview(self, report_type):
        # Reset button state
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate Report")
        
        # Update the preview based on report type
        if report_type == "Inventory Status":
            self._show_inventory_report()
        elif report_type == "Borrowed Books":
            self._show_borrowed_books_report()
        # No else needed as we want to keep the default table state with Delete in Actions column