from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QPushButton, QFrame, QSpacerItem, QSizePolicy, QFileDialog, QComboBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from database import add_user, get_all_users
import os

class AddUserDialog(QDialog):
    user_added = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setModal(True)
        self.setMinimumSize(800, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                border: none;
                border-radius: 12px;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
                font-weight: 500;
            }
            QLineEdit, QComboBox, QTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: white;
                min-height: 40px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #3b82f6;
                outline: none;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 14px;
                border: none;
                cursor: pointer;
            }
            QPushButton#primaryBtn {
                background-color: #3b82f6;
                color: white;
            }
            QPushButton#primaryBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#secondaryBtn {
                background-color: #f1f5f9;
                color: #64748b;
            }
            QPushButton#secondaryBtn:hover {
                background-color: #e2e8f0;
            }
        """)
        self.profile_image_path = None
        self.initUI()
        
        # Generate and set User ID
        self.generate_user_id()

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # Header with back button and title
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("icons/arrow-left.svg"))
        back_btn.setIconSize(QSize(24, 24))
        back_btn.setStyleSheet("background: transparent; border: none;")
        back_btn.clicked.connect(self.reject)
        
        # Title
        title_label = QLabel("Add New User")
        title_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #0f172a;")
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # Scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        # Container for scroll area
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(24)
        
        # Profile picture section
        profile_section = QVBoxLayout()
        profile_section.setAlignment(Qt.AlignCenter)
        
        # Profile image container
        self.profile_container = QLabel()
        self.profile_container.setFixedSize(120, 120)
        self.profile_container.setStyleSheet("""
            background-color: #f1f5f9;
            border: 2px dashed #cbd5e1;
            border-radius: 60px;
        """)
        
        # Default profile icon
        self.profile_icon = QLabel()
        self.profile_icon.setPixmap(QPixmap("icons/user.svg").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.profile_icon.setAlignment(Qt.AlignCenter)
        
        # Upload button
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setObjectName("secondaryBtn")
        self.upload_btn.setIcon(QIcon("icons/upload.svg"))
        self.upload_btn.clicked.connect(self.upload_image)
        
        profile_section.addWidget(self.profile_container, 0, Qt.AlignCenter)
        profile_section.addWidget(self.profile_icon, 0, Qt.AlignCenter)
        profile_section.addWidget(self.upload_btn, 0, Qt.AlignCenter)
        container_layout.addLayout(profile_section)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(16)
        
        # Two-column layout for form fields
        form_grid = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        # User ID (read-only, auto-generated)
        user_id_container = QVBoxLayout()
        user_id_label = QLabel("User ID")
        user_id_label.setStyleSheet("color: #475569; font-weight: 500;")
        
        self.user_id_field = QLineEdit()
        self.user_id_field.setReadOnly(True)
        self.user_id_field.setPlaceholderText("Auto-generated")
        self.user_id_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                background-color: #f8fafc;
                color: #94a3b8;
                font-size: 14px;
                min-height: 40px;
                margin-bottom: 16px;
            }
        """)
        
        user_id_container.addWidget(user_id_label)
        user_id_container.addWidget(self.user_id_field)
        left_column.addLayout(user_id_container)
        
        # Full Name
        self.full_name_field = self.create_form_field("Full Name", "Enter full name")
        left_column.addLayout(self.full_name_field['layout'])
        
        # Email
        self.email_field = self.create_form_field("Email Address", "Enter email address")
        left_column.addLayout(self.email_field['layout'])
        
        # Contact Number
        self.contact_field = self.create_form_field("Contact Number", "Enter contact number")
        left_column.addLayout(self.contact_field['layout'])
        
        # User Type (Role)
        self.role_field = QVBoxLayout()
        role_label = QLabel("Role")
        role_label.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 500;")
        self.role_combo = QComboBox()
        self.role_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: white;
                min-height: 40px;
            }
            QComboBox:focus {
                border: 1px solid #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        self.role_combo.addItems(["Admin", "Librarian", "Member"])
        self.role_field.addWidget(role_label)
        self.role_field.addWidget(self.role_combo)
        right_column.addLayout(self.role_field)
        right_column.addSpacing(16)  # Add spacing between fields
        
        # Status
        self.status_field = QVBoxLayout()
        status_label = QLabel("Status")
        status_label.setStyleSheet("color: #1e293b; font-size: 14px; font-weight: 500;")
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                background-color: white;
                min-height: 40px;
            }
            QComboBox:focus {
                border: 1px solid #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        self.status_combo.addItems(["Active", "Inactive", "Suspended"])
        self.status_field.addWidget(status_label)
        self.status_field.addWidget(self.status_combo)
        right_column.addLayout(self.status_field)
        
        # Add columns to form grid
        form_grid.addLayout(left_column, 1)
        form_grid.addSpacing(20)
        form_grid.addLayout(right_column, 1)
        form_layout.addLayout(form_grid)
        
        # Address (full width)
        self.address_field = self.create_form_field("Address", "Enter address", is_text_edit=True)
        form_layout.addLayout(self.address_field['layout'])
        
        container_layout.addLayout(form_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)  # Takes remaining space
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryBtn")
        self.cancel_button.clicked.connect(self.reject)
        
        # Add User button
        self.add_user_button = QPushButton("Add User")
        self.add_user_button.setObjectName("primaryBtn")
        self.add_user_button.clicked.connect(self.accept_user)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.add_user_button)
        main_layout.addLayout(button_layout)

    def create_form_field(self, label_text, placeholder, disabled=False, is_text_edit=False, is_readonly=False):
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("color: #475569; font-weight: 500;")
        layout.addWidget(label)
        
        # Field
        if is_text_edit:
            field = QTextEdit()
            field.setPlaceholderText(placeholder)
            field.setMinimumHeight(100)
            field.setReadOnly(is_readonly)
            field.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 10px 12px;
                    background-color: %s;
                    color: %s;
                    font-size: 14px;
                }
                QTextEdit:focus {
                    border: 1px solid #3b82f6;
                    outline: none;
                }
            """ % ("#f8fafc" if is_readonly else "white", 
                  "#94a3b8" if is_readonly else "#1e293b"))
        else:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            field.setReadOnly(is_readonly)
            field.setDisabled(disabled)
            field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 10px 12px;
                    background-color: %s;
                    color: %s;
                    font-size: 14px;
                    min-height: 40px;
                }
                QLineEdit:focus {
                    border: 1px solid #3b82f6;
                    outline: none;
                }
                QLineEdit:disabled, QLineEdit:read-only {
                    background-color: #f8fafc;
                    color: #94a3b8;
                    border: 1px solid #e2e8f0;
                }
            """ % ("#f8fafc" if is_readonly else "white", 
                  "#94a3b8" if is_readonly else "#1e293b"))
        
        layout.addWidget(field)
        return {"layout": layout, "field": field}
        
    def upload_image(self):
        """Handle image upload for profile picture"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.profile_image_path = file_path
            
            # Update profile picture
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale the image to fit the container while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.profile_container.width() - 10, 
                    self.profile_container.height() - 10,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Create a circular mask
                mask = QPixmap(scaled_pixmap.size())
                mask.fill(Qt.transparent)
                
                from PyQt5.QtGui import QPainter, QPainterPath
                painter = QPainter(mask)
                painter.setRenderHint(QPainter.Antialiasing)
                
                path = QPainterPath()
                path.addEllipse(0, 0, scaled_pixmap.width(), scaled_pixmap.height())
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()
                
                # Set the circular image
                self.profile_container.setPixmap(mask)
                self.profile_container.setAlignment(Qt.AlignCenter)
                
                # Hide the default user icon
                self.profile_icon.hide()

    def accept_user(self):
        # Get field values
        full_name = self.full_name_field['field'].text().strip()
        email = self.email_field['field'].text().strip()
        contact = self.contact_field['field'].text().strip()
        address = self.address_field['field'].toPlainText().strip()
        role = self.role_combo.currentText()
        status = self.status_combo.currentText()
        
        # Basic validation
        if not full_name or not email:
            self.show_error_message("Validation Error", "Please fill in all required fields.")
            return
            
        # Email validation
        if "@" not in email or "." not in email:
            self.show_error_message("Validation Error", "Please enter a valid email address.")
            return
            
        try:
            # Add user to database
            add_user(
                full_name=full_name,
                email=email,
                role=role,
                status=status,
                contact=contact if contact else None,
                address=address if address else None,
                profile_image=self.profile_image_path  # Save the image path to database
            )
            
            # Emit signal and close dialog
            self.user_added.emit()
            self.accept()
            
        except Exception as e:
            self.show_error_message("Error", f"Failed to add user: {str(e)}")
    
    def generate_user_id(self):
        """Generate a new user ID in the format USR-XXXXXX"""
        import random
        import string
        # Generate a random 6-digit number
        random_digits = ''.join(random.choices(string.digits, k=6))
        user_id = f"USR-{random_digits}"
        # Set the generated ID in the User ID field
        if hasattr(self, 'user_id_field') and self.user_id_field:
            self.user_id_field.setText(user_id)
        return user_id
        
    def show_error_message(self, title, message):
        """Show an error message dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #1e293b;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
        """)
        msg.exec_()
