from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QScrollArea, 
                            QDialog, QApplication, QMessageBox, 
                            QComboBox, QTextEdit, QDateEdit, QTimeEdit,
                            QFrame, QSizePolicy, QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QSize
from PyQt5.QtGui import QFont


class AddReminderPage(QDialog):
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Reminder")
        self.setWindowModality(Qt.ApplicationModal)  # Make it a modal dialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove help button
        
        # Set size policy to expand
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize UI
        self.setup_ui()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.closed.emit()
        event.accept()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout - using QVBoxLayout for full-screen layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with shadow
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame#header {
                background: #4a6cf7;
                border: none;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 12, 24, 12)
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setObjectName("backButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton#backButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 8px;
            }
            QPushButton#backButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        back_btn.clicked.connect(self.go_back)
        
        # Title
        title = QLabel("Add Reminder")
        title.setObjectName("pageTitle")
        title.setStyleSheet("""
            QLabel#pageTitle {
                font-size: 22px;
                font-weight: 600;
                color: white;
                margin: 0;
                padding: 8px 0;
            }
        """)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f5;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ced4da;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Main content container
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("""
            QWidget#contentWidget {
                background: #ffffff;
                border: none;
            }
        """)
        
        # Form layout with proper spacing
        self.form_layout = QVBoxLayout(content_widget)
        self.form_layout.setContentsMargins(32, 32, 32, 32)
        self.form_layout.setSpacing(24)
        
        # Add content to scroll area
        scroll.setWidget(content_widget)
        
        # Add header and scroll area to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(scroll)
        
        # Add bottom bar with save button
        bottom_bar = QFrame()
        bottom_bar.setObjectName("bottomBar")
        bottom_bar.setFixedHeight(80)
        bottom_bar.setStyleSheet("""
            QFrame#bottomBar {
                background: #ffffff;
                border-top: 1px solid #e9ecef;
                padding: 0 24px;
            }
        """)
        
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch()
        
        # Save button in bottom bar
        self.save_btn = QPushButton("Save Reminder")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setFixedSize(240, 48)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton#saveButton {
                background: #4a6cf7;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton#saveButton:hover {
                background: #3a5bd9;
            }
            QPushButton#saveButton:pressed {
                background: #2e4ab8;
            }
            QPushButton#saveButton:disabled {
                background: #e9ecef;
                color: #adb5bd;
            }
        """)
        self.save_btn.clicked.connect(self.save_reminder)
        
        bottom_layout.addWidget(self.save_btn)
        main_layout.addWidget(bottom_bar)
        
        # Setup form fields
        self.setup_form_fields()
    
    def go_back(self):
        """Handle back button click"""
        self.closed.emit()
    
    def setup_form_fields(self):
        """Set up the form fields for the reminder"""
        # Title Field
        title_label = QLabel("Title")
        title_label.setObjectName("fieldLabel")
        title_label.setStyleSheet("""
            QLabel#fieldLabel {
                font-size: 15px;
                font-weight: 500;
                color: #212529;
                margin-bottom: 8px;
            }
        """)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter reminder title")
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                color: #333;
            }
            QLineEdit:focus {
                border: 1px solid #4a6cf7;
            }
        """)
        
        self.form_layout.addWidget(title_label)
        self.form_layout.addWidget(self.title_edit)
        
        # Description Field
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
            margin-top: 15px;
        """)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter reminder description")
        self.desc_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                min-height: 80px;
                color: #333;
            }
            QTextEdit:focus {
                border: 1px solid #4a6cf7;
            }
        """)
        
        self.form_layout.addWidget(desc_label)
        self.form_layout.addWidget(self.desc_edit)
        
        # Date and Time Row
        datetime_layout = QHBoxLayout()
        datetime_layout.setSpacing(20)
        
        # Date Field
        date_container = QVBoxLayout()
        date_label = QLabel("Date")
        date_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
        """)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("""
            QDateEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                color: #333;
                min-width: 180px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border-left: 1px solid #e0e0e0;
            }
            QDateEdit:focus {
                border: 1px solid #4a6cf7;
            }
        """)
        
        date_container.addWidget(date_label)
        date_container.addWidget(self.date_edit)
        datetime_layout.addLayout(date_container)
        
        # Time Field
        time_container = QVBoxLayout()
        time_label = QLabel("Time")
        time_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
        """)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                color: #333;
                min-width: 120px;
            }
            QTimeEdit:focus {
                border: 1px solid #4a6cf7;
            }
        """)
        
        time_container.addWidget(time_label)
        time_container.addWidget(self.time_edit)
        datetime_layout.addLayout(time_container)
        
        self.form_layout.addLayout(datetime_layout)
        
        # Priority Field
        priority_label = QLabel("Priority")
        priority_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
            margin-top: 15px;
        """)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        self.priority_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                color: #333;
                min-width: 180px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border-left: 1px solid #e0e0e0;
            }
            QComboBox:focus {
                border: 1px solid #4a6cf7;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #f0f4ff;
                selection-color: #4a6cf7;
                outline: none;
            }
        """)
        
        self.form_layout.addWidget(priority_label)
        self.form_layout.addWidget(self.priority_combo)
        
        # Add save button container with proper spacing
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 20)
        
        # Add stretch to center the button
        button_layout.addStretch()
        
        # Create and style the save button
        self.save_button = QPushButton("Save Reminder")
        self.save_button.setObjectName("saveButton")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setFixedSize(200, 50)  # Fixed size for better appearance
        self.save_button.clicked.connect(self.save_reminder)
        
        # Apply styles to the save button
        self.save_button.setStyleSheet("""
            QPushButton#saveButton {
                background-color: #4a6cf7;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                padding: 12px 24px;
                min-width: 180px;
            }
            QPushButton#saveButton:hover {
                background-color: #3a5ce4;
            }
            QPushButton#saveButton:pressed {
                background-color: #2a4cd0;
            }
        """)
        
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        
        # Add button container to form
        self.form_layout.addWidget(button_container)
        
        # Add some spacing at the bottom of the form
        self.form_layout.addStretch()
    
    def save_reminder(self):
        """Handle save reminder button click"""
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("HH:mm")  # 24-hour format for database
        datetime_str = f"{date} {time}"
        priority = self.priority_combo.currentText()
        
        # Validate required fields
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title for the reminder.")
            return
            
        try:
            # Connect to the database
            import sqlite3
            
            conn = sqlite3.connect('library.db')
            cursor = conn.cursor()
            
            # Create reminders table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_datetime TEXT NOT NULL,
                    priority TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_completed BOOLEAN DEFAULT 0
                )
            ''')
            
            # Insert the new reminder
            cursor.execute('''
                INSERT INTO reminders (title, description, due_datetime, priority)
                VALUES (?, ?, ?, ?)
            ''', (title, description if description else None, datetime_str, priority))
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            # Show success message
            QMessageBox.information(self, "Success", "Reminder saved successfully!")
            
            # Clear the form
            self.clear_form()
            
            # Close the dialog
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save reminder: {str(e)}")
    
    def clear_form(self):
        """Clear all input fields"""
        self.title_edit.clear()
        self.desc_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.priority_combo.setCurrentIndex(0)  # Set to default priority
    
    def showEvent(self, event):
        """Center the dialog when shown"""
        if not event.spontaneous():
            screen = QApplication.primaryScreen().geometry()
            size = self.geometry()
            self.move(
                (screen.width() - size.width()) // 2,
                (screen.height() - size.height()) // 2
            )
        super().showEvent(event)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = AddReminderPage()
    window.show()
    sys.exit(app.exec_())
