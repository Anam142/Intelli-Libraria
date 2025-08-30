from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QLineEdit, QHBoxLayout, QSizePolicy, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import database
from datetime import datetime, timedelta

class FineManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(0)

        # Heading
        heading = QLabel("Fine Management")
        heading.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 0px; margin-top: 0px; background: none; border: none;")
        main_layout.addWidget(heading, alignment=Qt.AlignLeft)

        # Subtitle
        subtitle = QLabel("Manage and oversee all fine records within the library system.")
        subtitle.setStyleSheet("font-size: 16px; color: #6b7280; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 400; margin-bottom: 24px; margin-top: 0px; background: none; border: none;")
        main_layout.addWidget(subtitle, alignment=Qt.AlignLeft)

        # Initialize empty table data
        self.table_data = []
        self.load_fine_records()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search fines by user, book, or date")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 24px;
            }
            QLineEdit:focus {
                border: 1px solid #1976d2;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)
        main_layout.addWidget(self.search_bar)

        # Create table
        self.table = QTableWidget(len(self.table_data), 7)
        self.table.setHorizontalHeaderLabels([
            "User ID", "Book Title", "Issue Date", "Return Date", "Overdue Days", "Fine Amount", "Payment Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 16px;
                font-size: 15px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                border: 1px solid #e5e7eb;
                padding: 0px;
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
                padding: 14px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Initial table population
        self.populate_table(self.table_data)
        main_layout.addWidget(self.table)

    def load_fine_records(self):
        """Load fine records from the database"""
        try:
            # Fetch overdue transactions with fine information
            conn = database.create_connection()
            cursor = conn.cursor()
            
            # Query to get all transactions with fines (both paid and unpaid)
            cursor.execute('''
                SELECT 
                    '#' || t.id as transaction_id,
                    b.title as book_title,
                    t.borrowed_date,
                    t.due_date,
                    (julianday('now') - julianday(t.due_date)) as days_overdue,
                    t.fine_amount,
                    CASE 
                        WHEN t.fine_paid = 1 THEN 'Paid'
                        WHEN t.status = 'returned' AND t.fine_amount > 0 AND t.fine_paid = 0 THEN 'Unpaid (Returned)'
                        WHEN t.status = 'overdue' AND t.fine_amount > 0 AND t.fine_paid = 0 THEN 'Unpaid (Overdue)'
                        WHEN t.status = 'lost' THEN 'Unpaid (Lost Book)'
                        ELSE 'No Fine'
                    END as payment_status,
                    u.full_name as user_name
                FROM transactions t
                JOIN books b ON t.book_copy_id = b.id
                JOIN users u ON t.user_id = u.id
                WHERE (t.fine_amount > 0 OR t.status IN ('overdue', 'lost'))
                  AND t.borrowed_date IS NOT NULL
                ORDER BY t.due_date DESC
            ''')
            
            # Store the data for searching and display
            self.table_data = []
            for row in cursor.fetchall():
                transaction_id = row[0]
                book_title = row[1]
                borrowed_date = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                due_date = datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                days_overdue = max(0, int(float(row[4]))) if row[4] else 0
                fine_amount = f"${row[5]:.2f}" if row[5] else "$0.00"
                payment_status = row[6]
                
                self.table_data.append((
                    transaction_id,
                    book_title,
                    borrowed_date,
                    due_date,
                    str(days_overdue),
                    fine_amount,
                    payment_status
                ))
                
            conn.close()
            
            # Update the table with the fetched data
            self.populate_table(self.table_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load fine records: {str(e)}")
            print(f"Error loading fine records: {str(e)}")
    
    def populate_table(self, data):
        """Populate the table with the provided data"""
        try:
            self.table.setRowCount(len(data))
            for row, (transaction_id, book_title, borrowed_date, due_date, days_overdue, fine_amount, status) in enumerate(data):
                # Set transaction ID
                id_item = QTableWidgetItem(transaction_id)
                id_item.setData(Qt.UserRole, int(transaction_id[1:]))  # Store the actual ID without the #
                self.table.setItem(row, 0, id_item)
                
                # Set book title
                self.table.setItem(row, 1, QTableWidgetItem(book_title))
                
                # Set dates
                self.table.setItem(row, 2, QTableWidgetItem(borrowed_date))
                self.table.setItem(row, 3, QTableWidgetItem(due_date))
                
                # Set days overdue
                days_item = QTableWidgetItem(days_overdue)
                days_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 4, days_item)
                
                # Set fine amount
                fine_item = QTableWidgetItem(fine_amount)
                fine_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 5, fine_item)
                
                # Set status with appropriate styling
                pill = QLabel(status)
                pill.setAlignment(Qt.AlignCenter)
                pill.setFixedHeight(32)
                if status == "Paid":
                    pill.setStyleSheet("""
                        background: #e8f5e9;
                        color: #2e7d32;
                        border-radius: 16px;
                        font-size: 15px;
                        font-weight: 700;
                        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                        padding: 0 24px;
                    """)
                else:
                    pill.setStyleSheet("""
                        background: #ffebee;
                        color: #c62828;
                        border-radius: 16px;
                        font-size: 15px;
                        font-weight: 700;
                        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                        padding: 0 24px;
                    """)
                pill.setText(status)
                self.table.setCellWidget(row, 6, pill)
                
        except Exception as e:
            print(f"Error populating table: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to update the fines table: {str(e)}")
    
    def filter_table(self, text):
        """Filter the table based on the search text"""
        if not text:
            self.populate_table(self.table_data)
            return
            
        search_text = text.lower()
        filtered_data = []
        for row in self.table_data:
            # Search in all columns except fine amount (remove $ for better search)
            row_text = ' '.join([str(cell).lower() for i, cell in enumerate(row) if i != 5])  # Skip fine amount column
            if (search_text in row[1].lower() or  # Book Title
                search_text in row[2].lower() or  # Issue Date
                search_text in row[3].lower() or  # Return Date
                search_text in row[4].lower() or  # Overdue Days
                search_text in row[5].lower().replace('$', '') or  # Fine Amount (without $)
                search_text in row[6].lower()):   # Payment Status
                filtered_data.append(row)
                
        self.populate_table(filtered_data)