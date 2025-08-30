from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QDateTimeEdit, QTextEdit, QMessageBox, 
                            QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont, QIcon

class AddReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Reminder")
        self.setFixedSize(400, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 8px;
            }
            QLabel {
                color: #4b5563;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 6px;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                margin-bottom: 20px;
                background-color: #f9fafb;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 1px solid #4a6cf7;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                border: 1px solid #d1d5db;
                min-width: 100px;
            }
            #saveBtn {
                background-color: #4a6cf7;
                color: white;
                border: none;
            }
            #saveBtn:hover {
                background-color: #3a5bd9;
            }
            #cancelBtn {
                background-color: #ffffff;
                color: #4b5563;
                border: 1px solid #d1d5db;
                color: #333333;
                margin-right: 12px;
            }
            #cancelBtn:hover {
                background-color: #e2e8f0;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Add Reminder")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #111827; margin: 0 0 10px 0;")
        layout.addWidget(title)
        
        # Divider line
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e5e7eb;")
        layout.addWidget(divider)
        
        # Add spacer
        layout.addSpacing(10)
        
        # Title Field
        title_label = QLabel("Title")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter reminder title")
        layout.addWidget(title_label)
        layout.addWidget(self.title_input)
        
        # Date and Time Field
        datetime_label = QLabel("Date and Time")
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setDisplayFormat("MMM d, yyyy hh:mm AP")
        self.datetime_input.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default to 1 hour from now
        self.datetime_input.setCalendarPopup(False)
        self.datetime_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.datetime_input.setStyleSheet("""
            QDateTimeEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                min-width: 200px;
            }
        """)
        layout.addWidget(datetime_label)
        layout.addWidget(self.datetime_input)
        
        # Notes Field
        notes_label = QLabel("Notes")
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add any notes...")
        self.notes_input.setFixedHeight(100)
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("saveBtn")
        self.save_btn.setStyleSheet("""
            QPushButton#saveBtn {
                background-color: #2563eb;
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: 500;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background-color: #1d4ed8;
            }
            QPushButton#saveBtn:pressed {
                background-color: #1e40af;
            }
        """)
        self.save_btn.clicked.connect(self.validate_and_save)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        # Set focus to title field by default
        self.title_input.setFocus()
        layout.addLayout(button_layout)
    
    def validate_and_save(self):
        """Validate and save the reminder to the database"""
        title = self.title_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        due_date = self.datetime_input.dateTime().toPyDateTime()
        
        # Input validation
        if not title:
            QMessageBox.warning(self, "Validation Error", "Please enter a title for the reminder.")
            self.title_input.setFocus()
            return
            
        if due_date <= datetime.now():
            reply = QMessageBox.question(
                self,
                'Past Date',
                'The selected date is in the past. Do you want to continue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                self.datetime_input.setFocus()
                return
        
        try:
            # Save to database
            from db_handler import db
            
            conn = db._get_connection()
            cursor = conn.cursor()
            
            # Create reminders table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    notes TEXT,
                    due_date TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert the new reminder
            cursor.execute('''
                INSERT INTO reminders (title, notes, due_date)
                VALUES (?, ?, ?)
            ''', (
                title,
                notes if notes else None,
                due_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            conn.commit()
            
            # Show success message
            QMessageBox.information(
                self, 
                "Success", 
                "Reminder saved successfully!"
            )
            
            # Emit signal if parent has a refresh_reminders method
            if hasattr(self.parent(), 'refresh_reminders'):
                self.parent().refresh_reminders()
                
            self.accept()
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving reminder: {str(e)}", exc_info=True)
            
            QMessageBox.critical(
                self, 
                "Error", 
                "Failed to save reminder. Please try again."
            )
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def get_reminder(parent=None):
        """Static method to create the dialog and return the result"""
        dialog = AddReminderDialog(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return {
                'title': dialog.title_input.text().strip(),
                'notes': dialog.notes_input.toPlainText().strip(),
                'due_date': dialog.datetime_input.dateTime().toString("yyyy-MM-dd hh:mm AP")
            }
        return None
