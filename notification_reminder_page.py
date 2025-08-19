from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QDateTimeEdit, QTextEdit, QComboBox,
                           QFrame, QSizePolicy, QScrollArea, QToolButton, QLineEdit,
                           QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QStackedWidget)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QPainterPath, QCursor

class NotificationReminderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 24, 16, 24)  # Reduced right margin from 32 to 16
        self.main_layout.setSpacing(0)
        self.current_tab = 'notifications'  # Default tab
        self.render()

    def clear_main_layout(self):
        """Clear all widgets from the main layout to prevent duplication"""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            # Also clear any layouts
            if item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        """Recursively clear a layout and its widgets"""
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                if item.layout():
                    self.clear_layout(item.layout())

    def render(self):
        self.clear_main_layout()
        
        if self.current_tab == 'notifications':
            # Header row with title, search bar, and button on same line (for notifications)
            header_container = QWidget()
            header_layout = QHBoxLayout(header_container)
            header_layout.setContentsMargins(0, 0, 0, 24)
            header_layout.setSpacing(16)
            
            # Title on the left
            title_label = QLabel("Notification & Reminders")
            title_label.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 0px; margin-top: 0px;")
            
            # Search bar in center
            search_input = QLineEdit()
            search_input.setPlaceholderText("Search notifications...")
            search_input.setStyleSheet("""
                QLineEdit {
                    background: #fff;
                    border: 1.5px solid #e5e7eb;
                    border-radius: 10px;
                    padding: 16px 20px;
                    font-size: 16px;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                    color: #232b36;
                    min-width: 300px;
                }
                QLineEdit:focus {
                    border: 1.5px solid #4f46e5;
                }
            """)
            
            # Mark all as read button on the right
            mark_read_btn = QPushButton("Mark all as read")
            mark_read_btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: 500;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            """)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch(1)
            header_layout.addWidget(search_input)
            header_layout.addWidget(mark_read_btn)
            
            self.main_layout.addWidget(header_container)
        else:
            # For reminders tab - only show the title
            title_label = QLabel("Notification & Reminders")
            title_label.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 24px; margin-top: 0px;")
            self.main_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        
        # Tabs always below the heading
        tab_row = QHBoxLayout()
        tab_row.setContentsMargins(0, 0, 0, 24)  # Restored to 24 for proper spacing
        tab_row.setSpacing(16)
        
        notif_tab = QLabel('Notification')  # Changed to singular
        remind_tab = QLabel('Reminders')
        
        # Clear any previous styling and set clean states
        if self.current_tab == 'notifications':
            notif_tab.setStyleSheet('font-size: 18px; color: #232b36; margin-right: 16px; border-bottom: 2px solid #3b82f6; padding-bottom: 2px; background: none; font-weight: bold;')
            remind_tab.setStyleSheet('font-size: 18px; color: #9ca3af; margin-right: 16px; padding-bottom: 2px; background: none; font-weight: normal; border-bottom: none;')
        else:
            notif_tab.setStyleSheet('font-size: 18px; color: #9ca3af; margin-right: 16px; padding-bottom: 2px; background: none; font-weight: normal; border-bottom: none;')
            remind_tab.setStyleSheet('font-size: 18px; color: #232b36; margin-right: 16px; border-bottom: 2px solid #3b82f6; padding-bottom: 2px; background: none; font-weight: bold;')
        
        notif_tab.setCursor(Qt.PointingHandCursor)
        remind_tab.setCursor(Qt.PointingHandCursor)
        notif_tab.mousePressEvent = lambda e: self.switch_tab('notifications')
        remind_tab.mousePressEvent = lambda e: self.switch_tab('reminders')
        
        tab_row.addWidget(notif_tab)
        tab_row.addWidget(remind_tab)
        
        # Add Add Reminder button to the right corner with minimal spacing
        if self.current_tab == 'reminders':
            add_btn = QPushButton("Add Reminder")
            add_btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    border-radius: 12px;
                    padding: 10px 28px;
                    border: none;
                    margin: 0px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            """)
            add_btn.clicked.connect(self.show_add_reminder_form)  # Connect button click
            tab_row.addStretch(1)  # This pushes the button to the right corner
            tab_row.addWidget(add_btn, alignment=Qt.AlignRight)
        else:
            tab_row.addStretch(1)
        
        self.main_layout.addLayout(tab_row)
        
        # Render content for the active tab
        if self.current_tab == 'notifications':
            self.render_notifications_content()
        elif self.current_tab == 'reminders':
            self.render_reminders_content()

    def render_notifications_content(self):
        """Render the notifications tab content"""
        # Filter placeholders (4 empty squares as shown in image)
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 24)
        filter_layout.setSpacing(8)
        
        for i in range(4):
            placeholder = QWidget()
            placeholder.setFixedSize(24, 24)
            placeholder.setStyleSheet("background: #dbeafe; border-radius: 4px;")
            filter_layout.addWidget(placeholder)
        
        filter_layout.addStretch(1)
        self.main_layout.addWidget(filter_container)
        
        # Notifications list - exactly 3 items as shown in image
        notifications_container = QWidget()
        notifications_layout = QVBoxLayout(notifications_container)
        notifications_layout.setContentsMargins(0, 0, 0, 0)
        notifications_layout.setSpacing(16)
        
        # Notification items - exactly as shown in the reference image
        notifications_data = [
            {
                "title": "New Book Arrival",
                "description": "The book 'Python Programming' you requested is now available for borrowing.",
                "timestamp": "2 hours ago"
            },
            {
                "title": "Due Date Reminder",
                "description": "Your borrowed book 'Clean Code' is due in 2 days.",
                "timestamp": "1 day ago"
            },
            {
                "title": "Library Event",
                "description": "Join our weekly book club meeting this Friday at 5 PM.",
                "timestamp": "2 days ago"
            }
        ]
        
        for notification in notifications_data:
            notification_item = QWidget()
            notification_item.setStyleSheet("""
                QWidget {
                    background: #fff;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 0px;
                }
            """)
            
            item_layout = QHBoxLayout(notification_item)
            item_layout.setContentsMargins(20, 16, 20, 16)
            item_layout.setSpacing(16)
            
            # Icon (light gray square placeholder as shown in image)
            icon_label = QWidget()
            icon_label.setFixedSize(24, 24)
            icon_label.setStyleSheet("background: #f3f4f6; border-radius: 4px;")
            
            # Content
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(4)
            
            title_label = QLabel(notification["title"])
            title_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    font-weight: 700;
                    color: #232b36;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                }
            """)
            
            desc_label = QLabel(notification["description"])
            desc_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    color: #6b7280;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                }
            """)
            desc_label.setWordWrap(True)
            
            content_layout.addWidget(title_label)
            content_layout.addWidget(desc_label)
            
            # Right side with timestamp and ellipsis
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(8)
            right_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
            
            timestamp_label = QLabel(notification["timestamp"])
            timestamp_label.setStyleSheet("""
                QLabel {
                    background: transparent;
                    border: none;
                    font-size: 12px;
                    color: #9ca3af;
                    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                }
            """)
            
            # Ellipsis button (...)
            ellipsis_btn = QPushButton("...")
            ellipsis_btn.setFixedSize(20, 20)
            ellipsis_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #9ca3af;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #6b7280;
                }
            """)
            
            right_layout.addWidget(timestamp_label)
            right_layout.addWidget(ellipsis_btn)
            
            item_layout.addWidget(icon_label)
            item_layout.addWidget(content_widget, 1)
            item_layout.addWidget(right_widget)
            
            notifications_layout.addWidget(notification_item)
        
        # Add stretch to push notifications to top
        notifications_layout.addStretch(1)
        
        # Add notifications container to main layout
        self.main_layout.addWidget(notifications_container, 1)

    def render_reminders_content(self):
        """Render the reminders tab content"""
        # Full-width search bar below
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search reminders")
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 10px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin: 18px 0 18px 0;
            }
            QLineEdit:focus {
                border: 1.5px solid #4f46e5;
                background: #ffffff;
            }
        """)
        self.main_layout.addWidget(search_bar)
        
        # Table
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["Title", "Date & Time", "Description", "Actions"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(54)
        table.setStyleSheet("""
            QTableWidget {
                background: #fff;
                border-radius: 16px;
                font-size: 16px;
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
                font-size: 16px;
                border: none;
                padding: 16px 8px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        reminders = [
            ("Return 'The Silent Observer'", "2024-08-15 10:00 AM", "Return the book to avoid late fees."),
            ("Renew 'Echoes of the Past'", "2024-08-20 02:00 PM", "Renew the book to keep it longer."),
            ("Pick up 'The Lost City'", "2024-08-25 04:00 PM", "Pick up the reserved book."),
            ("Pay fines", "2024-08-30 11:00 AM", "Pay outstanding fines."),
            ("Attend book club meeting", "2024-09-05 07:00 PM", "Attend the monthly book club meeting."),
        ]
        
        for row, (title, dt, desc) in enumerate(reminders):
            table.setItem(row, 0, QTableWidgetItem(title))
            table.setItem(row, 1, QTableWidgetItem(dt))
            table.setItem(row, 2, QTableWidgetItem(desc))
            actions = QLabel("<a href='#' style='color:#2563eb;text-decoration:none; font-weight:700;'>Edit</a> | <a href='#' style='color:#f87171;text-decoration:none; font-weight:700;'>Delete</a> | <a href='#' style='color:#059669;text-decoration:none; font-weight:700;'>Complete</a>")
            actions.setTextFormat(Qt.RichText)
            actions.setOpenExternalLinks(False)
            actions.setAlignment(Qt.AlignCenter)
            actions.setStyleSheet("font-size: 16px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: none; border: none;")
            table.setCellWidget(row, 3, actions)
        
        self.main_layout.addWidget(table)

    def switch_tab(self, tab):
        """Switch between tabs with complete interface recreation"""
        if self.current_tab != tab:  # Only switch if different tab
            self.current_tab = tab
            # Force complete recreation to prevent any dual effects
            self.render()

    def show_add_reminder_form(self):
        """Show the Add Reminder form"""
        # Clear the main layout to show the form
        self.clear_main_layout()
        
        # Main heading
        heading = QLabel("Add Reminder")
        heading.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 32px; margin-top: 0px;")
        self.main_layout.addWidget(heading, alignment=Qt.AlignLeft)
        
        # Title input
        title_label = QLabel("Title")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #232b36; margin-bottom: 8px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;")
        self.main_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        
        title_input = QLineEdit()
        title_input.setPlaceholderText("Enter reminder title")
        title_input.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 24px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4f46e5;
            }
        """)
        self.main_layout.addWidget(title_input)
        
        # Date and Time input
        datetime_label = QLabel("Date and Time")
        datetime_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #232b36; margin-bottom: 8px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;")
        self.main_layout.addWidget(datetime_label, alignment=Qt.AlignLeft)
        
        # Date and Time input
        datetime_input = QLineEdit()
        datetime_input.setPlaceholderText("Select date and time")
        datetime_input.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 24px;
            }
            QLineEdit:focus {
                border: 1.5px solid #4f46e5;
            }
        """)
        self.main_layout.addWidget(datetime_input)
        
        # Notes input
        notes_label = QLabel("Notes")
        notes_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #232b36; margin-bottom: 8px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif;")
        self.main_layout.addWidget(notes_label, alignment=Qt.AlignLeft)
        
        notes_input = QTextEdit()
        notes_input.setPlaceholderText("Add detailed notes about the reminder")
        notes_input.setStyleSheet("""
            QTextEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin-bottom: 32px;
                min-height: 120px;
            }
            QTextEdit:focus {
                border: 1.5px solid #4f46e5;
            }
        """)
        self.main_layout.addWidget(notes_input)
        
        # Buttons row
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(16)
        button_row.addStretch(1)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        cancel_btn.clicked.connect(self.show_reminders_tab)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        save_btn.clicked.connect(self.save_reminder)
        
        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        
        self.main_layout.addLayout(button_row)
        self.main_layout.addStretch(1)

    def show_reminders_tab(self):
        """Go back to reminders tab"""
        self.current_tab = 'reminders'
        self.render()

    def save_reminder(self):
        """Save the reminder and go back to reminders tab"""
        QMessageBox.information(self, "Success", "Reminder saved successfully!")
        self.show_reminders_tab()

    def show_date_picker(self):
        """Show date picker when calendar icon is clicked"""
        from PyQt5.QtWidgets import QDateEdit, QTimeEdit, QDialog, QVBoxLayout, QHBoxLayout, QPushButton
        from PyQt5.QtCore import QDate, QTime
        
        # Create a simple date/time picker dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date and Time")
        dialog.setFixedSize(300, 200)
        dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Date picker
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setStyleSheet("""
            QDateEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Time picker
        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        time_edit.setStyleSheet("""
            QTimeEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addWidget(date_edit)
        layout.addWidget(time_edit)
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Update the datetime input with selected values
            selected_date = date_edit.date().toString("yyyy-MM-dd")
            selected_time = time_edit.time().toString("hh:mm AP")
            datetime_text = f"{selected_date} {selected_time}"
            
            # Find the datetime input and update it
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QWidget):
                    for child in item.widget().findChildren(QLineEdit):
                        if child.placeholderText() == "Select date and time":
                            child.setText(datetime_text)
                            break

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = NotificationReminderPage()
    window.show()
    sys.exit(app.exec_())
