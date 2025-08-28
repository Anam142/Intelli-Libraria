from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QDateTimeEdit, QTextEdit, QComboBox,
                           QFrame, QSizePolicy, QScrollArea, QToolButton, QLineEdit,
                           QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QStackedWidget,
                           QDialogButtonBox)
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
        # Initialize reminders list
        self.reminders = [
            {"id": 1, "title": "Return 'The Great Gatsby'", "datetime": "2024-08-20 11:00 AM", "description": "Return the book to the library.", "completed": False},
            {"id": 2, "title": "Renew 'To Kill a Mockingbird'", "datetime": "2024-08-22 02:30 PM", "description": "Renew the book if needed.", "completed": False},
            {"id": 3, "title": "Pick up 'The Lost City'", "datetime": "2024-08-25 04:00 PM", "description": "Pick up the reserved book.", "completed": False},
            {"id": 4, "title": "Pay fines", "datetime": "2024-08-30 11:00 AM", "description": "Pay outstanding fines.", "completed": False},
            {"id": 5, "title": "Attend book club meeting", "datetime": "2024-09-05 07:00 PM", "description": "Attend the monthly book club meeting.", "completed": False},
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
        
        # Set different background colors based on the button text
        if text == 'All':
            bg_color = "#ef4444"  # Red
            hover_color = "#dc2626"
            text_color = "white"
        elif text == 'Due Date':
            bg_color = "#3b82f6"  # Blue
            hover_color = "#2563eb"
            text_color = "white"
        elif text == 'Reservation':
            bg_color = "#10b981"  # Green
            hover_color = "#059669"
            text_color = "white"
        else:
            bg_color = "#f3f4f6"  # Default gray
            hover_color = "#e5e7eb"
            text_color = "#374151"
            
        # Create style string with f-strings for dynamic colors
        style = f"""
            QPushButton {{
                background: {bg_color};
                color: {text_color};
                border: 1px solid {bg_color};
                border-radius: 20px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 600;
                min-width: 100px;
                margin: 4px;
            }}
            QPushButton:hover {{
                background: {hover_color};
                border-color: {hover_color};
            }}
            QPushButton:checked {{
                background: {bg_color};
                color: {text_color};
                border: 1px solid {bg_color};
            }}
            QPushButton:checked:hover {{
                background: {hover_color};
                border-color: {hover_color};
            }}
        """
        btn.setStyleSheet(style)
        return btn

    def on_chip_clicked(self, label):
        if self.active_filter != label:
            self.active_filter = label
            self.render()  # re-render with new filter

    def on_search_changed(self, text):
        self.search_query = text
        # Re-render notifications live
        self.render()
        
    def filter_reminders(self, search_text):
        """Filter reminders based on search text in title or description"""
        if not hasattr(self, 'reminders_table') or not self.reminders_table:
            return
            
        search_text = search_text.lower().strip()
        
        # Reset to show all reminders if search is empty
        if not search_text:
            self.reminders = self.all_reminders.copy()
        else:
            # Filter reminders based on search text
            self.reminders = [
                r for r in self.all_reminders 
                if (search_text in r['title'].lower() or 
                    (r['description'] and search_text in r['description'].lower()))
            ]
        
        # Update the table with filtered results
        if hasattr(self, 'reminders_table'):
            self.populate_reminders_table(self.reminders_table)

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
                background-color: #1e90ff;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1c86ee;
            }
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
        search_bar.setPlaceholderText("Search reminders by title or description")
        search_bar.textChanged.connect(self.filter_reminders)
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1.5px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                color: #1f2937;
                margin-bottom: 16px;
            }
            QLineEdit:focus {
                border: 1.5px solid #3b82f6;
                outline: none;
                background: #ffffff;
            }
        """)
        self.search_bar = search_bar  # Store reference for filtering
        self.main_layout.addWidget(search_bar)
        
        # Table
        self.reminders_table = QTableWidget(len(self.reminders), 4)
        table = self.reminders_table  # Store reference for filtering
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
        
        # Populate the table with reminders
        self.populate_reminders_table(table)
        
        self.main_layout.addWidget(table)

        # Store original reminders for filtering
        self.all_reminders = self.reminders.copy()

    def switch_tab(self, tab):
        """Switch between tabs with complete interface recreation"""
        if self.current_tab != tab:  # Only switch if different tab
            self.current_tab = tab
            # Force complete recreation to prevent any dual effects
            self.render()

    def show_add_reminder_form(self, edit_mode=False, reminder=None):
        """Show the Add/Edit Reminder form
        
        Args:
            edit_mode (bool): Whether the form is in edit mode
            reminder (dict, optional): The reminder data to edit
        """
        # Clear the main layout to show the form
        self.clear_main_layout()
        
        # Main heading
        heading = QLabel("Edit Reminder" if edit_mode else "Add Reminder")
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
        
        # Date and Time input with calendar button
        datetime_widget = QWidget()
        datetime_layout = QHBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(0, 0, 0, 0)
        datetime_layout.setSpacing(10)
        
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
            }
            QLineEdit:focus {
                border: 1.5px solid #4f46e5;
            }
        """)
        
        # Calendar button with text
        calendar_btn = QPushButton("Select")
        calendar_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 16px 24px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        calendar_btn.setCursor(Qt.PointingHandCursor)
        calendar_btn.clicked.connect(self.show_date_picker)
        
        datetime_layout.addWidget(datetime_input, 1)
        datetime_layout.addWidget(calendar_btn)
        
        # Add some bottom margin to the container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 24)  # Bottom margin
        container_layout.addWidget(datetime_widget)
        
        self.main_layout.addWidget(container)
        
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
        
        # Set initial values if in edit mode
        if edit_mode and reminder:
            title_input.setText(reminder.get('title', ''))
            notes_input.setPlainText(reminder.get('description', ''))
            
            # Set the datetime string directly to the input field
            datetime_input.setText(reminder.get('datetime', ''))
        
        # Save button
        save_btn = QPushButton("Update" if edit_mode else "Save")
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

    def populate_reminders_table(self, table):
        """Populate the reminders table with current reminders data"""
        table.setRowCount(len(self.reminders))
        
        for row, reminder in enumerate(self.reminders):
            # Set title with strikethrough if completed
            title_item = QTableWidgetItem(reminder["title"])
            if reminder["completed"]:
                title_item.setFlags(title_item.flags() & ~Qt.ItemIsEnabled)
                title_item.setData(Qt.TextColorRole, QColor("#6b7280"))
                title_item.setText(title_item.text() + " ✓")
            
            table.setItem(row, 0, title_item)
            table.setItem(row, 1, QTableWidgetItem(reminder["datetime"]))
            
            # Set description with strikethrough if completed
            desc_item = QTableWidgetItem(reminder["description"])
            if reminder["completed"]:
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEnabled)
                desc_item.setData(Qt.TextColorRole, QColor("#6b7280"))
            table.setItem(row, 2, desc_item)
            
            # Create action buttons
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            
            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    min-width: 60px;
                    min-height: 28px;
                    font-size: 12px;
                    font-weight: 500;
                    margin-right: 6px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
                QPushButton:pressed {
                    background: #1d4ed8;
                }
                QPushButton:disabled {
                    background: #94a3b8;
                }
            """)
            edit_btn.clicked.connect(lambda _, r=row: self.edit_reminder(r))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    min-width: 60px;
                    min-height: 28px;
                    font-size: 12px;
                    font-weight: 500;
                    margin-right: 6px;
                }
                QPushButton:hover {
                    background: #dc2626;
                }
                QPushButton:pressed {
                    background: #b91c1c;
                }
            """)
            delete_btn.clicked.connect(lambda _, r=row: self.delete_reminder(r))
            
            # Complete/Undo button
            complete_text = "Undo" if reminder["completed"] else "Complete"
            complete_btn = QPushButton(complete_text)
            complete_btn.setCursor(Qt.PointingHandCursor)
            complete_btn.setStyleSheet("""
                QPushButton {
                    background: #10b981;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    min-width: 70px;
                    padding: 2px 8px;
                    min-height: 28px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #059669;
                }
                QPushButton:pressed {
                    background: #047857;
                }
            """)
            complete_btn.clicked.connect(lambda _, r=row: self.toggle_reminder_completion(r))
            
            if reminder["completed"]:
                edit_btn.setEnabled(False)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addWidget(complete_btn)
            table.setCellWidget(row, 3, actions_widget)
            # Set minimum width for the actions column
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            table.horizontalHeader().setMinimumSectionSize(240)  # Ensure enough width for all buttons
    
    def edit_reminder(self, row):
        """Handle edit reminder action by navigating to Add Reminder screen"""
        if 0 <= row < len(self.reminders):
            self.reminder_to_edit = row
            self.show_add_reminder_form(edit_mode=True, reminder=self.reminders[row])
    
    def delete_reminder(self, row):
        """Handle delete reminder action"""
        if 0 <= row < len(self.reminders):
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Delete Reminder')
            msg_box.setText('Are you sure you want to delete this reminder')
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setWindowFlags(msg_box.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            reply = msg_box.exec_()
            
            if reply == QMessageBox.Yes:
                del self.reminders[row]
                # Find the table in the current layout and update it
                for i in range(self.main_layout.count()):
                    widget = self.main_layout.itemAt(i).widget()
                    if isinstance(widget, QTableWidget):
                        self.populate_reminders_table(widget)
                        break
                        
                QMessageBox.information(self, "Success", "Reminder deleted successfully!")
    
    def toggle_reminder_completion(self, row):
        """Toggle reminder completion status"""
        if 0 <= row < len(self.reminders):
            self.reminders[row]["completed"] = not self.reminders[row]["completed"]
            
            # Find the table in the current layout and update it
            for i in range(self.main_layout.count()):
                widget = self.main_layout.itemAt(i).widget()
                if isinstance(widget, QTableWidget):
                    self.populate_reminders_table(widget)
                    break
            
            status = "completed" if self.reminders[row]["completed"] else "marked as incomplete"
            QMessageBox.information(self, "Success", f"Reminder {status} successfully!")
    
    def show_reminders_tab(self):
        """Switch to the reminders tab"""
        self.current_tab = 'reminders'
        # Force a complete re-render to ensure the table is refreshed
        self.clear_main_layout()
        self.render()

    def save_reminder(self):
        """Save the reminder and go back to reminders tab"""

        # Get all input fields from the form
        title_input = None
        notes_input = None
        datetime_input = None
        
        # Find form inputs
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            if not widget:
                continue
                
            if isinstance(widget, QLineEdit):
                if widget.placeholderText() == "Enter reminder title":
                    title_input = widget
                elif widget.placeholderText() == "Select date and time":
                    datetime_input = widget
            elif isinstance(widget, QTextEdit) and widget.placeholderText() == "Add detailed notes about the reminder":
                notes_input = widget
            
            # Also check child widgets
            for child in widget.findChildren((QLineEdit, QTextEdit)):
                if isinstance(child, QLineEdit):
                    if child.placeholderText() == "Enter reminder title":
                        title_input = child
                    elif child.placeholderText() == "Select date and time":
                        datetime_input = child
                elif isinstance(child, QTextEdit) and child.placeholderText() == "Add detailed notes about the reminder":
                    notes_input = child
        
        if not all([title_input, notes_input, datetime_input]):
            QMessageBox.warning(self, "Error", "Could not find all required form fields.")
            return
        
        title = title_input.text().strip()
        description = notes_input.toPlainText().strip()
        selected_datetime = datetime_input.text().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title for the reminder.")
            return
            
        if not selected_datetime:
            QMessageBox.warning(self, "Error", "Please select a date and time for the reminder.")
            return
        
        if hasattr(self, 'reminder_to_edit') and self.reminder_to_edit is not None:
            # Update existing reminder
            reminder = self.reminders[self.reminder_to_edit]
            reminder.update({
                "title": title,
                "datetime": selected_datetime,
                "description": description
            })
            message = "Reminder updated successfully!"
            delattr(self, 'reminder_to_edit')
        else:
            # Create new reminder
            new_reminder = {
                "id": max([r.get("id", 0) for r in self.reminders], default=0) + 1,
                "title": title,
                "datetime": selected_datetime,
                "description": description,
                "completed": False
            }
            self.reminders.append(new_reminder)
            message = "Reminder saved successfully!"
        
        # Show success message and go back to reminders tab
        QMessageBox.information(self, "Success", message)
        self.show_reminders_tab()

    def show_date_picker(self):
        """Show date picker when calendar icon is clicked"""
        from PyQt5.QtWidgets import (QDateEdit, QTimeEdit, QDialog, QVBoxLayout, 
                                  QHBoxLayout, QPushButton, QLabel)
        from PyQt5.QtCore import QDate, QTime, Qt
        
        # Find the datetime input field first
        datetime_input = None
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            if isinstance(widget, QLineEdit) and widget.placeholderText() == "Select date and time":
                datetime_input = widget
                break
        
        # If not found in main layout, search in child widgets
        if not datetime_input:
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), QWidget):
                    for child in item.widget().findChildren(QLineEdit, None, Qt.FindChildrenRecursively):
                        if child.placeholderText() == "Select date and time":
                            datetime_input = child
                            break
                    if datetime_input:
                        break
        
        if not datetime_input:
            QMessageBox.warning(self, "Error", "Could not find the date/time input field.")
            return
        
        # Create a simple date/time picker dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date and Time")
        dialog.setFixedSize(350, 250)
        # Remove question mark from the title bar
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet("""
            QDialog {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
                margin-bottom: 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        
        # Date picker
        date_label = QLabel("Select Date:")
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Time picker
        time_label = QLabel("Select Time:")
        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        time_edit.setStyleSheet("""
            QTimeEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Buttons
        button_box = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        ok_btn = QPushButton("OK")
        
        # Style buttons
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #4b5563;
                border: 1px solid #d1d5db;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(date_label)
        layout.addWidget(date_edit)
        layout.addWidget(time_label)
        layout.addWidget(time_edit)
        
        # Add buttons to button box
        button_box.addStretch()
        button_box.addWidget(cancel_btn)
        button_box.addWidget(ok_btn)
        
        layout.addLayout(button_box)
        
        # Connect buttons
        def on_accept():
            selected_date = date_edit.date().toString("yyyy-MM-dd")
            selected_time = time_edit.time().toString("hh:mm AP")
            datetime_input.setText(f"{selected_date} {selected_time}")
            dialog.accept()
        
        ok_btn.clicked.connect(on_accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Show dialog
        dialog.exec_()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = NotificationReminderPage()
    window.show()
    sys.exit(app.exec_())
