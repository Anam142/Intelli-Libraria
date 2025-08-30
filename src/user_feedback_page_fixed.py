from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, 
    QSlider, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QMessageBox,
    QStyle, QSizePolicy, QStyleOptionSlider
)
from PyQt5.QtCore import Qt

class UserFeedbackPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        self.initUI()

    def initUI(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 24, 32, 24)
        self.layout.setSpacing(0)

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
        self.layout.addLayout(form_section)

    def submit_feedback(self):
        """Handle feedback form submission"""
        user_id = self.user_id_input.text().strip()
        feedback = self.feedback_input.toPlainText().strip()
        rating = self.rating_slider.value()

        if not user_id or not feedback:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        # Here you would typically save the feedback to a database
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

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = UserFeedbackPage()
    window.setWindowTitle("User Feedback")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
