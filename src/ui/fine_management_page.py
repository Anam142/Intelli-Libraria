from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QLineEdit, QHBoxLayout, QSizePolicy, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import database
from datetime import datetime, timedelta

class FineManagementPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_data = []
        self.setup_ui()

    def setup_ui(self):
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
        self.table = QTableWidget(0, 7)
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
        main_layout.addWidget(self.table)

    def showEvent(self, event):
        """Handle show event - load fines only when the page is shown"""
        super().showEvent(event)
        if not self.table_data:  # Only load if not already loaded
            self.load_fine_records()

    def load_fine_records(self):
        """Load fine records from the database"""
        if not hasattr(self, 'table'):
            return  # Table not initialized yet
            
        try:
            # Check if required columns exist first
            conn = sqlite3.connect('intelli_libraria.db')
            cursor = conn.cursor()
            
            # Verify required columns exist in transactions table
            cursor.execute("PRAGMA table_info(transactions)")
            columns = [col[1].lower() for col in cursor.fetchall()]  # Convert to lowercase for case-insensitive check
            
            # Map column names to standard names
            column_mapping = {
                'issue_date': 'issue_date',
                'due_date': 'due_date',
                'fine_amount': 'fine_amount',
                'fine_paid': 'fine_paid',
                'status': 'status' if 'status' in columns else None
            }
            
            # Check for any missing critical columns
            missing_columns = [col for col, val in column_mapping.items() if val is None]
            
            if missing_columns:
                self.table.setRowCount(1)
                self.table.setColumnCount(1)
                self.table.setItem(0, 0, QTableWidgetItem(
                    f"Fine management not available. Missing required database columns: {', '.join(missing_columns)}"
                ))
                return
                
            # If we get here, all required columns exist
            self.table.setRowCount(0)  # Clear existing rows
            
            # Fetch overdue transactions with fine information
            conn = database.create_connection()
            cursor = conn.cursor()
            
            # Build the query using the mapped column names
            query = f'''
                SELECT 
                    '#' || t.id as transaction_id,
                    COALESCE(b.title, 'Unknown Book') as book_title,
                    t.{column_mapping['issue_date']} as issue_date,
                    t.{column_mapping['due_date']} as due_date,
                    CASE 
                        WHEN t.{column_mapping['due_date']} IS NOT NULL 
                        THEN (julianday('now') - julianday(t.{column_mapping['due_date']}))
                        ELSE 0 
                    END as days_overdue,
                    COALESCE(t.{column_mapping['fine_amount']}, 0) as fine_amount,
                    CASE 
                        WHEN t.{column_mapping['fine_paid']} = 1 THEN 'Paid'
                        WHEN t.{column_mapping['status']} = 'returned' AND COALESCE(t.{column_mapping['fine_amount']}, 0) > 0 AND t.{column_mapping['fine_paid']} = 0 THEN 'Unpaid (Returned)'
                        WHEN t.{column_mapping['status']} = 'overdue' AND COALESCE(t.{column_mapping['fine_amount']}, 0) > 0 AND t.{column_mapping['fine_paid']} = 0 THEN 'Unpaid (Overdue)'
                        WHEN t.{column_mapping['status']} = 'lost' AND COALESCE(t.{column_mapping['fine_amount']}, 0) > 0 THEN 'Unpaid (Lost Book)'
                        ELSE 'No Fine'
                    END as payment_status,
                    COALESCE(u.full_name, 'Unknown User') as user_name,
                    COALESCE(u.email, 'N/A') as user_email
                FROM transactions t
                LEFT JOIN book_copies bc ON t.book_copy_id = bc.id
                LEFT JOIN books b ON bc.book_id = b.id
                LEFT JOIN users u ON t.user_id = u.id
                WHERE (COALESCE(t.{column_mapping['fine_amount']}, 0) > 0 OR t.{column_mapping['status']} IN ('overdue', 'lost'))
                AND t.{column_mapping['issue_date']} IS NOT NULL
                ORDER BY t.{column_mapping['due_date']} DESC
                LIMIT 100
            '''
            cursor.execute(query)
            
            # Store the data for searching and display
            self.table_data = []
            rows = cursor.fetchall()
            
            if not rows:
                self.table.setRowCount(1)
                self.table.setColumnCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No fine records found"))
                return
                
            for row in rows:
                try:
                    self.table_data.append({
                        'transaction_id': row[0] if len(row) > 0 else 'N/A',
                        'book_title': row[1] if len(row) > 1 else 'Unknown',
                        'issue_date': row[2] if len(row) > 2 else 'N/A',
                        'due_date': row[3] if len(row) > 3 else 'N/A',
                        'days_overdue': int(float(row[4])) if len(row) > 4 and row[4] is not None else 0,
                        'fine_amount': float(row[5]) if len(row) > 5 and row[5] is not None else 0.0,
                        'payment_status': row[6] if len(row) > 6 else 'Unknown',
                        'user_name': row[7] if len(row) > 7 else 'Unknown',
                        'user_email': row[8] if len(row) > 8 else 'N/A'
                    })
                except (ValueError, IndexError, TypeError) as e:
                    print(f"Error processing row: {e}")
                    continue
                    
            # Update the table with the fetched data
            self.populate_table(self.table_data)
            
        except Exception as e:
            print(f"Error loading fine records: {str(e)}")
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Error loading fine records. Please try again later."))
        finally:
            if 'conn' in locals():
                conn.close()

    def populate_table(self, data):
        """Populate the table with the provided data"""
        try:
            if not data:
                self.table.setRowCount(1)
                self.table.setColumnCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No fine records found"))
                return
            
            self.table.setRowCount(len(data))
            self.table.setColumnCount(7)  # Ensure we have the right number of columns
            
            for row, item in enumerate(data):
                try:
                    # Set transaction ID
                    transaction_id = str(item.get('transaction_id', 'N/A'))
                    id_item = QTableWidgetItem(transaction_id)
                    if transaction_id.startswith('#'):
                        try:
                            id_item.setData(Qt.UserRole, int(transaction_id[1:]))
                        except (ValueError, IndexError):
                            pass
                    self.table.setItem(row, 0, id_item)
                    
                    # Set book title
                    book_title = str(item.get('book_title', 'Unknown'))
                    self.table.setItem(row, 1, QTableWidgetItem(book_title))
                    
                    # Set dates
                    issue_date = str(item.get('issue_date', 'N/A'))
                    due_date = str(item.get('due_date', 'N/A'))
                    self.table.setItem(row, 2, QTableWidgetItem(issue_date))
                    self.table.setItem(row, 3, QTableWidgetItem(due_date))
                    
                    # Set days overdue
                    days_overdue = str(int(float(item.get('days_overdue', 0))))  # Convert to float first, then int
                    days_item = QTableWidgetItem(days_overdue)
                    days_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 4, days_item)
                    
                    # Set fine amount
                    try:
                        fine_amount = float(item.get('fine_amount', 0))
                        fine_text = f"${fine_amount:,.2f}" if fine_amount > 0 else "$0.00"
                    except (ValueError, TypeError):
                        fine_text = "$0.00"
                        
                    fine_item = QTableWidgetItem(fine_text)
                    fine_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, 5, fine_item)
                    
                    # Set payment status with color coding
                    payment_status = str(item.get('payment_status', 'Unknown'))
                    status_item = QTableWidgetItem(payment_status)
                    status_item.setTextAlignment(Qt.AlignCenter)
                    
                    # Color code based on status
                    if 'Paid' in payment_status:
                        status_item.setBackground(QColor(220, 252, 231))  # Light green
                    elif 'Unpaid' in payment_status:
                        status_item.setBackground(QColor(254, 226, 226))  # Light red
                    
                    self.table.setItem(row, 6, status_item)
                    
                    # Set row height
                    self.table.setRowHeight(row, 50)
                    
                except Exception as e:
                    print(f"Error populating row {row}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in populate_table: {str(e)}")
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Error displaying data: {str(e)}"))
    
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