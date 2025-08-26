from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, 
    QSlider, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QMessageBox,
    QStyle, QSizePolicy, QStyleOptionSlider
)
from PyQt5.QtCore import Qt
import database

class UserFeedbackPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        
        # Create main widget and scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create a container widget and layout
        self.container = QWidget()
        self.container.setStyleSheet("background: #f4f5f7;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(32, 24, 32, 24)
        self.layout.setSpacing(20)
        
        # Set the container as the scroll area's widget
        self.scroll.setWidget(self.container)
        
        # Set the scroll area as the main widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)
        
        self.initUI()

    def initUI(self):
        # Clear any existing items in the layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Set layout properties
        self.layout.setContentsMargins(32, 24, 32, 24)
        self.layout.setSpacing(20)

        # Heading
        heading = QLabel("User Feedback")
        heading.setStyleSheet("""
            font-size: 32px; 
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif; 
            font-weight: 800; 
            color: #232b36;
        """)
        self.layout.addWidget(heading, alignment=Qt.AlignLeft)

        # Subtext
        subtext = QLabel("Collect and manage user feedback to improve our services.")
        subtext.setStyleSheet("""
            font-size: 15px; 
            color: #8a8f98; 
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif; 
            font-weight: 400; 
            margin-bottom: 24px; 
            margin-top: 0px;
        """)
        self.layout.addWidget(subtext, alignment=Qt.AlignLeft)

        # Form section
        form_section = QVBoxLayout()
        form_section.setSpacing(10)
        
        # Form label
        form_label = QLabel("Submit Feedback")
        form_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #232b36; 
            margin-top: 24px;
        """)
        form_section.addWidget(form_label)

        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("background: transparent;")
        form_container_layout = QVBoxLayout(form_container)
        form_container_layout.setContentsMargins(0, 0, 0, 0)
        form_container_layout.setSpacing(10)

        # User ID
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("""
            font-size: 15px; 
            font-weight: 600; 
            color: #232b36;
        """)
        self.user_id_input = QLineEdit()
        self.user_id_input.setStyleSheet("""
            background: #fff; 
            border-radius: 10px; 
            border: 1.5px solid #e5e7eb; 
            padding: 12px 16px; 
            font-size: 15px; 
            margin-bottom: 8px;
        """)
        form_container_layout.addWidget(user_id_label)
        form_container_layout.addWidget(self.user_id_input)

        # Feedback
        feedback_label = QLabel("Feedback")
        feedback_label.setStyleSheet("""
            font-size: 15px; 
            font-weight: 600; 
            color: #232b36;
        """)
        self.feedback_input = QTextEdit()
        self.feedback_input.setStyleSheet("""
            QTextEdit {
                background: #fff; 
                border-radius: 10px; 
                border: 1.5px solid #e5e7eb; 
                padding: 12px 16px; 
                font-size: 15px; 
                margin-bottom: 8px;
                min-height: 100px;
            }
            QTextEdit:focus {
                border: 1.5px solid #4f46e5;
            }
        """)
        self.feedback_input.setPlaceholderText("Enter your feedback here")
        form_container_layout.addWidget(feedback_label)
        form_container_layout.addWidget(self.feedback_input)

        # Rating
        rating_label = QLabel("Satisfaction Score (1-5)")
        rating_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: 500; 
            color: #374151; 
            margin-top: 16px;
        """)
        form_container_layout.addWidget(rating_label)

        # Slider container
        slider_container = QWidget()
        slider_layout = QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 4, 0, 0)
        slider_layout.setSpacing(16)

        # Slider
        self.rating_slider = QSlider(Qt.Horizontal)
        self.rating_slider.setMinimum(1)
        self.rating_slider.setMaximum(5)
        self.rating_slider.setValue(3)
        self.rating_slider.setTickPosition(QSlider.TicksBelow)
        self.rating_slider.setTickInterval(1)
        self.rating_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #e5e7eb;
                margin: 0px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #000000;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #f3f4f6;
            }
            QSlider::sub-page:horizontal {
                background: #000000;
                border-radius: 2px;
            }
            QSlider::add-page:horizontal {
                background: #e5e7eb;
                border-radius: 2px;
            }
            QSlider::tick:horizontal {
                background: #9ca3af;
                width: 1px;
                height: 4px;
                margin-top: 8px;
            }
        """)

        # Rating value display
        self.rating_value = QLabel("3")
        self.rating_value.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                min-width: 20px;
                text-align: right;
                padding-right: 4px;
            }
        """)

        # Connect slider to update the value display
        self.rating_slider.valueChanged.connect(lambda value: self.rating_value.setText(str(value)))
        
        slider_layout.addWidget(self.rating_slider)
        slider_layout.addWidget(self.rating_value)
        form_container_layout.addWidget(slider_container)

        # Submit button
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 24, 0, 0)
        button_layout.addStretch(1)  # Push button to the right

        submit_btn = QPushButton("Submit Feedback")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 32px;
                font-size: 15px;
                font-weight: 600;
                min-width: 160px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
                padding: 12px 34px;
                margin-right: -2px;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.submit_feedback)
        button_layout.addWidget(submit_btn)

        form_container_layout.addWidget(button_container)
        form_section.addWidget(form_container)
        
        # Add form section to main layout
        self.layout.addLayout(form_section)

        # Feedback Table Section
        table_section = QVBoxLayout()
        table_section.setContentsMargins(0, 32, 0, 0)
        
        # Add table section to main layout
        
        # Table Header
        table_header = QHBoxLayout()
        table_label = QLabel("Feedback History")
        table_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #232b36;
            margin-bottom: 16px;
        """)
        table_header.addWidget(table_label)
        table_header.addStretch()
        table_section.addLayout(table_header)
        
        # Create a simple container for the table
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add table container to the table section
        table_section.addWidget(table_container)
        
        # Add the table section to the main layout
        self.layout.addLayout(table_section)
        
        # Create table widget with styling
        self.feedback_table = QTableWidget()
        self.feedback_table.setColumnCount(4)
        self.feedback_table.setHorizontalHeaderLabels(["Date", "User ID", "Feedback", "Rating"])
        
        # Set column resize modes
        header = self.feedback_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # User ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Feedback
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Rating
        
        # Set size policy
        self.feedback_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style the table
        self.feedback_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                font-size: 13px;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-weight: 600;
                color: #333;
            }
            QTableCornerButton::section {
                background: #f5f5f5;
                border-bottom: 2px solid #e0e0e0;
            }
        """)
        
        # Set selection behavior
        self.feedback_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.feedback_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add table to layout with stretch
        table_layout.addWidget(self.feedback_table)
        
        # Add table container to main layout with stretch
        self.layout.addWidget(table_container, 1)  # Stretch factor of 1
        
        # Set size constraints
        self.feedback_table.setMinimumHeight(300)
        self.feedback_table.setMinimumWidth(800)
        
        # Add stretch to push content up and ensure proper spacing
        self.layout.addStretch()
        
        # Ensure the table is visible
        self.feedback_table.show()
        
        # Load from database books to show context in feedback table header
        try:
            rows = database.execute_query("SELECT COUNT(*) as n FROM books")
            n = rows[0]["n"] if rows else 0
            table_label.setText(f"Feedback History • {n} book(s) in catalog")
        except Exception:
            pass

    def load_sample_data(self):
        """Load sample feedback data into the table"""
        try:
            # Sample data - in a real app, this would come from a database
            sample_data = [
                ("2024-08-17", "user123", "Great service, very helpful staff!", "5/5"),
                ("2024-08-16", "user456", "The website could be faster. The interface is a bit slow when loading large catalogs.", "3/5"),
                ("2024-08-15", "user789", "Excellent selection of books and very easy to use interface.", "5/5"),
                ("2024-08-14", "user101", "The mobile app needs some improvements, but the website works great.", "4/5"),
                ("2024-08-13", "user202", "Very satisfied with the service. Quick response to queries.", "5/5"),
            ]
            
            # Clear existing data
            self.feedback_table.setRowCount(0)
            
            # Populate the table with sample data
            for row, (date, user_id, feedback, rating) in enumerate(sample_data):
                # Insert new row
                row_position = self.feedback_table.rowCount()
                self.feedback_table.insertRow(row_position)
                
                # Set items for each column
                self.feedback_table.setItem(row_position, 0, QTableWidgetItem(str(date)))
                self.feedback_table.setItem(row_position, 1, QTableWidgetItem(str(user_id)))
                self.feedback_table.setItem(row_position, 2, QTableWidgetItem(str(feedback)))
                self.feedback_table.setItem(row_position, 3, QTableWidgetItem(str(rating)))
                
                # Make sure the cells are selectable and enabled
                for col in range(4):
                    item = self.feedback_table.item(row_position, col)
                    if item:
                        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            
            # Resize columns to fit content with minimum widths
            self.feedback_table.resizeColumnsToContents()
            
            # Set minimum column widths to ensure headers are fully visible
            self.feedback_table.setColumnWidth(0, 100)  # Date
            self.feedback_table.setColumnWidth(1, 100)  # User ID
            self.feedback_table.setColumnWidth(3, 80)   # Rating
            
            # Make the feedback column take remaining space
            self.feedback_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
            
            # Force update the table
            self.feedback_table.viewport().update()
            
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")
    
    # Removed check_table_visibility method as it's no longer needed
    
    def submit_feedback(self):
        """Handle feedback form submission"""
        user_id = self.user_id_input.text().strip()
        feedback = self.feedback_input.toPlainText().strip()
        rating = self.rating_slider.value()

        if not user_id or not feedback:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        # Add to the table
        row_position = self.feedback_table.rowCount()
        self.feedback_table.insertRow(row_position)
        from datetime import datetime
        self.feedback_table.setItem(row_position, 0, QTableWidgetItem(datetime.now().strftime("%Y-%m-%d")))
        self.feedback_table.setItem(row_position, 1, QTableWidgetItem(user_id))
        self.feedback_table.setItem(row_position, 2, QTableWidgetItem(feedback))
        self.feedback_table.setItem(row_position, 3, QTableWidgetItem(f"{rating}/5"))

        # Show success message
        QMessageBox.information(
            self, 
            "Feedback Submitted", 
            f"Thank you for your feedback!\n\n"
            f"User ID: {user_id}\n"
            f"Rating: {rating}/5\n"
            f"Feedback: {feedback[:100]}{'...' if len(feedback) > 100 else ''}"
        )
        
        # Clear the form
        self.user_id_input.clear()
        self.feedback_input.clear()
        self.rating_slider.setValue(3)
        
        # Scroll to show the new feedback
        self.feedback_table.scrollToBottom()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = UserFeedbackPage()
    window.setWindowTitle("User Feedback")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
