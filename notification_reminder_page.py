from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class NotificationReminderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #f4f5f7;")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 24, 32, 24)
        self.main_layout.setSpacing(0)
        self.current_tab = 'notifications'
        self.render()

    def clear_main_layout(self):
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    clear_layout(item.layout())
        clear_layout(self.main_layout)

    def render(self):
        self.clear_main_layout()
        # Main heading at the very top (only once)
        heading = QLabel("Notifications & Reminders" if self.current_tab == 'notifications' else "Reminders")
        heading.setStyleSheet("font-size: 32px; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; font-weight: 800; color: #232b36; margin-bottom: 0px; margin-top: 0px;")
        self.main_layout.addWidget(heading, alignment=Qt.AlignLeft)
        # Tabs always below the heading
        tab_row = QHBoxLayout()
        notif_tab = QLabel('<b>Notifications</b>')
        remind_tab = QLabel('Reminders')
        if self.current_tab == 'notifications':
            notif_tab.setStyleSheet('font-size: 18px; color: #232b36; margin-right: 16px; border-bottom: 2px solid #232b36; padding-bottom: 2px; background: none;')
            remind_tab.setStyleSheet('font-size: 18px; color: #a0aec0; margin-right: 16px; padding-bottom: 2px; background: none;')
        else:
            notif_tab.setStyleSheet('font-size: 18px; color: #a0aec0; margin-right: 16px; padding-bottom: 2px; background: none;')
            remind_tab.setStyleSheet('font-size: 18px; color: #232b36; margin-right: 16px; border-bottom: 2px solid #232b36; padding-bottom: 2px; background: none;')
        notif_tab.setCursor(Qt.PointingHandCursor)
        remind_tab.setCursor(Qt.PointingHandCursor)
        notif_tab.mousePressEvent = lambda e: self.switch_tab('notifications')
        remind_tab.mousePressEvent = lambda e: self.switch_tab('reminders')
        tab_row.addWidget(notif_tab)
        tab_row.addWidget(remind_tab)
        tab_row.addStretch(1)
        self.main_layout.addLayout(tab_row)
        # Render content for the active tab
        if self.current_tab == 'notifications':
            self.render_notifications_content()
        elif self.current_tab == 'reminders':
            self.render_reminders_content()

    def render_notifications_content(self):
        # Search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search notifications")
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #f6f7fa;
                border: none;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin: 20px 0 12px 0;
            }
        """)
        self.main_layout.addWidget(search_bar)
        # Filter chips (only for notifications)
        chip_row = QHBoxLayout()
        for i, label in enumerate(["All", "Due Date", "Reservation"]):
            chip = QLabel(label)
            if i == 0:
                chip.setStyleSheet("background: #232b36; color: #fff; border-radius: 8px; font-size: 15px; font-weight: 600; padding: 4px 16px; margin-right: 8px;")
            else:
                chip.setStyleSheet("background: #f3f4f6; color: #232b36; border-radius: 8px; font-size: 15px; font-weight: 600; padding: 4px 16px; margin-right: 8px;")
            chip_row.addWidget(chip)
        chip_row.addStretch(1)
        self.main_layout.addLayout(chip_row)
        # Notification list (compact)
        notifications = [
            ("calendar", "Due Date Reminder", "The book 'The Secret Garden' is due in 2 days.", "2024-03-15"),
            ("bell", "Reservation Update", "Your reservation for 'The Great Gatsby' is now available.", "2024-03-14"),
            ("check", "Return Confirmation", "The book 'To Kill a Mockingbird' has been returned successfully.", "2024-03-12"),
            ("clock", "Overdue Notice", "The book '1984' is overdue by 1 day.", "2024-03-10"),
            ("cancel", "Reservation Cancellation", "Your reservation for 'Pride and Prejudice' has been cancelled.", "2024-03-08"),
        ]
        for icon_type, title, desc, date in notifications:
            row = QHBoxLayout()
            row.setSpacing(0)
            icon_label = QLabel()
            if icon_type == "calendar":
                icon_label.setText("🗓️")
            elif icon_type == "bell":
                icon_label.setText("🔔")
            elif icon_type == "check":
                icon_label.setText("✅")
            elif icon_type == "clock":
                icon_label.setText("⏰")
            elif icon_type == "cancel":
                icon_label.setText("❌")
            icon_label.setStyleSheet("font-size: 14px; background: #f4f5f7; border-radius: 8px; min-width: 22px; min-height: 22px; max-width: 22px; max-height: 22px; border: 1px solid #e5e7eb; text-align: center; margin-right: 6px;")
            icon_label.setAlignment(Qt.AlignCenter)
            row.addWidget(icon_label)
            text_col = QVBoxLayout()
            title_label = QLabel(f"<b>{title}</b>")
            title_label.setStyleSheet("font-size: 15px; color: #232b36; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; margin-bottom: 1px;")
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("font-size: 14px; color: #94a3b8; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; margin-bottom: 0px;")
            text_col.addWidget(title_label)
            text_col.addWidget(desc_label)
            row.addLayout(text_col)
            row.addStretch(1)
            date_label = QLabel(date)
            date_label.setStyleSheet("font-size: 14px; color: #94a3b8; font-family: 'Inter', 'Segoe UI', Arial, sans-serif; margin-left: 12px;")
            row.addWidget(date_label)
            notif_frame = QFrame()
            notif_frame.setLayout(row)
            notif_frame.setStyleSheet("background: #fff; border-radius: 10px; margin-top: 4px; margin-bottom: 0px; padding: 4px 6px 4px 0px;")
            self.main_layout.addWidget(notif_frame)
        # Mark all as read button
        mark_all_btn = QPushButton("Mark all as read")
        mark_all_btn.setStyleSheet("background: #f3f4f6; color: #232b36; font-size: 14px; font-weight: 600; border-radius: 12px; padding: 6px 18px; border: none; margin-top: 10px;")
        self.main_layout.addWidget(mark_all_btn, alignment=Qt.AlignLeft)

    def render_reminders_content(self):
        # Only add the Add Reminder button in the reminders tab
        heading_row = QHBoxLayout()
        heading_row.addStretch(1)
        add_btn = QPushButton("Add Reminder")
        add_btn.setStyleSheet("background: #fff; color: #232b36; font-size: 15px; font-weight: 600; border-radius: 12px; padding: 10px 28px; border: 1.5px solid #e5e7eb; margin: 0px 0px 0px 0px;")
        heading_row.addWidget(add_btn, alignment=Qt.AlignRight)
        self.main_layout.addLayout(heading_row)
        # Full-width search bar below
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search reminders")
        search_bar.setStyleSheet("""
            QLineEdit {
                background: #fff;
                border: 1.5px solid #e5e7eb;
                border-radius: 10px;
                padding: 16px 20px;
                font-size: 16px;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                color: #232b36;
                margin: 18px 0 18px 0;
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
        self.current_tab = tab
        self.render() 