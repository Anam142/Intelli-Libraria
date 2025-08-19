from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QScrollArea, 
                            QDialog, QApplication, QMessageBox, 
                            QComboBox, QTextEdit, QDateEdit, QTimeEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime


class AddReminderPage(QDialog):
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Reminder")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(600, 500)
        
        # Initialize UI
        self.setup_ui()
        
        # Center the dialog
        self.center()
    
    def center(self):
        """Center the dialog on the screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.closed.emit()
        event.accept()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background: #4a6cf7;")
        header.setFixedHeight(60)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Back button
        back_btn = QPushButton("←")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        back_btn.clicked.connect(self.reject)
        
        # Title
        title = QLabel("Add Reminder")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: white;
            margin: 0;
        """)
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Create scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #f5f7fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f2f5;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("background: white;")
        self.form_layout = QVBoxLayout(form_container)
        self.form_layout.setContentsMargins(30, 30, 30, 30)
        self.form_layout.setSpacing(25)
        
        # Add form container to scroll area
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll)
        
        # Setup form fields
        self.setup_form_fields()
        
    def setup_form_fields(self):
        """Set up the form fields for the reminder"""
        # Title Field
        title_label = QLabel("Title")
        title_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
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
                min-height: 120px;
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
        
        # Add save button
        button_container = QHBoxLayout()
        button_container.addStretch()
        
        self.save_btn = QPushButton("Save Reminder")
        self.save_btn.setFixedSize(200, 50)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #4a6cf7;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background: #3a5bd9;
            }
            QPushButton:pressed {
                background: #2e4ab8;
            }
            QPushButton:disabled {
                background: #cccccc;
            }
        """)
        self.save_btn.clicked.connect(self.save_reminder)
        
        button_container.addWidget(self.save_btn)
        self.form_layout.addLayout(button_container)
        
        # Add stretch to push everything to the top
        self.form_layout.addStretch()
    
    def save_reminder(self):
        """Handle save reminder button click"""
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("hh:mm AP")
        priority = self.priority_combo.currentText()
        
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title for the reminder.")
            return
            
        # TODO: Save the reminder to the database
        print(f"Saving reminder: {title}, {description}, {date} {time}, {priority}")
        
        # Show success message
        QMessageBox.information(self, "Success", "Reminder saved successfully!")
        
        # Close the dialog
        self.accept()
    
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
