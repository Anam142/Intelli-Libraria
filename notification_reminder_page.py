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
        # Tighter margins to widen content and reduce bottom whitespace
        self.main_layout.setContentsMargins(24, 16, 24, 10)
        self.main_layout.setSpacing(0)
        self.current_tab = 'notifications'  # Default tab
        # State for the Notifications screen
        self.active_filter = 'All'
        self.search_query = ''
        self.notifications_data = [
            {
                'title': 'Due Date Reminder',
                'description': "The book 'The Secret Garden' is due in 2 days.",
                'date': '2024-03-15',
                'category': 'Due Date',
            },
            {
                'title': 'Reservation Update',
                'description': "Your reservation for 'The Great Gatsby' is now available.",
                'date': '2024-03-14',
                'category': 'Reservation',
            },
            {
                'title': 'Return Confirmation',
                'description': "The book 'To Kill a Mockingbird' has been returned successfully.",
                'date': '2024-03-12',
                'category': 'Reservation',
            },
            {
                'title': 'Overdue Notice',
                'description': "The book '1984' is overdue by 1 day.",
                'date': '2024-03-10',
                'category': 'Due Date',
            },
            {
                'title': 'Reservation Cancellation',
                'description': "Your reservation for 'Pride and Prejudice' has been cancelled.",
                'date': '2024-03-08',
                'category': 'Reservation',
            },
        ]
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
        
        # Title (always shown)
        title_label = QLabel("Notifications & Reminders")
        title_label.setStyleSheet("font-size: 28px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 6px; margin-top: 0px;")
        self.main_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        
        # Tabs always below the heading
        tab_row = QHBoxLayout()
        tab_row.setContentsMargins(0, 0, 0, 12)
        tab_row.setSpacing(16)
        
        notif_tab = QLabel('Notifications')
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
        
        # Search bar (below tabs when on notifications), otherwise simple spacing
        if self.current_tab == 'notifications':
            self.add_notifications_search_and_filters()
            self.render_notifications_content()
        elif self.current_tab == 'reminders':
            self.render_reminders_content()

    def add_notifications_search_and_filters(self):
        # Search bar
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search notifications")
        search_input.setText(self.search_query)
        search_input.textChanged.connect(self.on_search_changed)
        search_input.setStyleSheet(
            """
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 10px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin: 8px 0 12px 0;
            }
            QLineEdit:focus {
                border: 1.5px solid #3b82f6;
            }
            """
        )
        self.main_layout.addWidget(search_input)

        # Filter chips row
        chips_container = QWidget()
        chips_layout = QHBoxLayout(chips_container)
        chips_layout.setContentsMargins(0, 0, 0, 10)
        chips_layout.setSpacing(10)

        for label in ["All", "Due Date", "Reservation"]:
            chip = self.build_chip(label, selected=(label == self.active_filter))
            chips_layout.addWidget(chip)

        chips_layout.addStretch(1)
        self.main_layout.addWidget(chips_container)

    def build_chip(self, text, selected=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setCheckable(True)
        btn.setChecked(selected)
        btn.clicked.connect(lambda: self.on_chip_clicked(text))
        btn.setStyleSheet(
            """
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #e5e7eb;
                border-radius: 18px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:checked {
                background: #e0e7ff;
                color: #3730a3;
                border-color: #c7d2fe;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
            """
        )
        return btn

    def on_chip_clicked(self, label):
        if self.active_filter != label:
            self.active_filter = label
            self.render()  # re-render with new filter

    def on_search_changed(self, text):
        self.search_query = text
        # Re-render live for simplicity
        self.render()

    def render_notifications_content(self):
        """Render the notifications tab content matching the reference layout."""
        # Filtered data
        filtered = []
        for item in self.notifications_data:
            if self.active_filter != 'All' and item['category'] != self.active_filter:
                continue
            if self.search_query:
                q = self.search_query.lower()
                if q not in item['title'].lower() and q not in item['description'].lower():
                    continue
            filtered.append(item)

        # List container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)

        for item in filtered:
            row = QWidget()
            # Borderless row to match the reference image
            row.setStyleSheet(
                """
                QWidget {
                    background: transparent;
                    border: none;
                    border-radius: 0px;
                }
                """
            )
            row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row.setMinimumHeight(64)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(14, 12, 14, 12)
            row_layout.setSpacing(12)

            # Icon using Unicode code point (ASCII-style literal escapes)
            icon = QLabel(self.get_icon_for_item(item))
            icon.setFixedSize(36, 36)
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("background: #f3f4f6; border: none; border-radius: 8px;")
            try:
                icon.setFont(QFont("Segoe UI Emoji", 20))
            except Exception:
                icon.setFont(QFont("Arial", 18))

            # Texts
            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)

            title = QLabel(item['title'])
            title.setStyleSheet("font-size: 15px; font-weight: 700; color: #111827; background: transparent;")
            desc = QLabel(item['description'])
            desc.setWordWrap(True)
            desc.setStyleSheet("font-size: 13px; color: #6b7280; background: transparent;")

            text_layout.addWidget(title)
            text_layout.addWidget(desc)

            # Right aligned date only (no ellipsis), per reference image
            right = QWidget()
            right_layout = QVBoxLayout(right)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(6)
            right_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

            date_label = QLabel(item['date'])
            date_label.setStyleSheet("font-size: 14px; font-weight: 700; color: #64748b; background: transparent;")

            right_layout.addWidget(date_label)
            # Spacer to keep minimal vertical size
            right_layout.addStretch(1)

            row_layout.addWidget(icon)
            row_layout.addWidget(text_widget, 1)
            row_layout.addWidget(right)

            container_layout.addWidget(row)

        # Keep a tiny spacer so the footer is closer to the list
        container_layout.addSpacing(6)
        self.main_layout.addWidget(container, 1)

        # Footer with Mark all as read button aligned right
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 6, 0, 0)
        footer.addStretch(1)
        mark_all = QPushButton("Mark all as read")
        mark_all.clicked.connect(self.on_mark_all_read)
        mark_all.setStyleSheet(
            """
            QPushButton {
                background: #f3f4f6;
                color: #111827;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background: #e5e7eb; }
            """
        )
        footer.addWidget(mark_all)
        # Reduce space below the footer by adding a small stretch with low factor
        wrapper = QWidget()
        wrapper.setLayout(footer)
        self.main_layout.addWidget(wrapper)

    def on_mark_all_read(self):
        QMessageBox.information(self, "Notifications", "All notifications marked as read.")

    def get_icon_for_item(self, item):
        """Return a Unicode icon character (specified via code point) for a notification item."""
        title = item.get('title', '')
        category = item.get('category', '')
        # Icons via Unicode escapes:
        # Calendar: \U0001F4C5, Bell: \U0001F514, Check: \u2705, Alarm: \u23F0, Cross: \u274C
        if 'Due Date' in title or category == 'Due Date':
            return "\U0001F4C5"  # 📅
        if 'Reservation Update' in title:
            return "\U0001F514"  # 🔔
        if 'Return' in title:
            return "\u2705"      # ✅
        if 'Overdue' in title:
            return "\u23F0"      # ⏰
        if 'Cancellation' in title:
            return "\u274C"      # ❌
        if category == 'Reservation':
            return "\U0001F4E6"  # 📦 as a generic reservation/package icon
        return "\u25CF"          # ● default bullet

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
