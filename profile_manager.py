import sqlite3
import bcrypt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_PATH = "users.db"

class ProfileManager(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()
        self.load_user_data()
        self.setStyleSheet("""
            QWidget {
                background-color: #1E293B; /* Slate-800 */
            }
            QFrame {
                background-color: #334155; /* Slate-700 */
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #F1F5F9; /* Slate-100 */
                font-size: 18px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #475569; /* Slate-600 */
                color: #F1F5F9;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6; /* Blue-500 */
            }
            QLineEdit:disabled {
                background-color: #64748B; /* Slate-500 */
                color: #D1D5DB;
            }
            QPushButton {
                background-color: #3B82F6; /* Blue-500 */
                color: #F1F5F9;
                border: 2px solid #3B82F6;
                padding: 14px;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #60A5FA; /* Blue-400 */
                border: 2px solid #60A5FA;
            }
            QPushButton:pressed {
                background-color: #2563EB; /* Blue-600 */
                border: 2px solid #2563EB;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # User Info Card
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)

        self.username_label = QLabel(f"Username: {self.username}")
        self.username_label.setStyleSheet("font-size: 22px; font-weight: 700;")
        info_layout.addWidget(self.username_label)

        name_label = QLabel("Full Name")
        info_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(True)
        self.name_input.setDisabled(True)
        info_layout.addWidget(self.name_input)

        phone_label = QLabel("Phone Number")
        info_layout.addWidget(phone_label)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")
        info_layout.addWidget(self.phone_input)

        guardian_name_label = QLabel("Guardian Name")
        info_layout.addWidget(guardian_name_label)
        self.guardian_name_input = QLineEdit()
        self.guardian_name_input.setPlaceholderText("Enter guardian name")
        info_layout.addWidget(self.guardian_name_input)

        guardian_phone_label = QLabel("Guardian WhatsApp Number")
        info_layout.addWidget(guardian_phone_label)
        self.guardian_phone_input = QLineEdit()
        self.guardian_phone_input.setPlaceholderText("Enter guardian WhatsApp")
        info_layout.addWidget(self.guardian_phone_input)

        layout.addWidget(info_frame)

        # Password Change Card
        password_frame = QFrame()
        password_layout = QVBoxLayout(password_frame)
        password_layout.setSpacing(15)

        password_label = QLabel("Change Password")
        password_label.setStyleSheet("font-size: 20px; font-weight: 700;")
        password_layout.addWidget(password_label)

        new_password_label = QLabel("New Password")
        password_layout.addWidget(new_password_label)
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.new_password_input)

        confirm_password_label = QLabel("Confirm Password")
        password_layout.addWidget(confirm_password_label)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.confirm_password_input)

        layout.addWidget(password_frame)

        # Save Button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def load_user_data(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name, phone, guardian_name, guardian_phone FROM users WHERE username = ?", (self.username,))
        result = c.fetchone()
        conn.close()

        if result:
            self.name_input.setText(result[0])
            self.phone_input.setText(result[1])
            self.guardian_name_input.setText(result[2])
            self.guardian_phone_input.setText(result[3])

    def save_changes(self):
        phone = self.phone_input.text()
        guardian_name = self.guardian_name_input.text()
        guardian_phone = self.guardian_phone_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validate inputs
        if not phone or not guardian_name or not guardian_phone:
            QMessageBox.warning(self, "Error", "Phone, guardian name, and guardian phone are required")
            return

        if not phone.isdigit() or len(phone) != 10:
            QMessageBox.warning(self, "Error", "Phone number must be 10 digits")
            return

        if not guardian_phone.isdigit() or len(guardian_phone) != 10:
            QMessageBox.warning(self, "Error", "Guardian phone must be 10 digits")
            return

        if new_password or confirm_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "Error", "Passwords do not match")
                return
            if len(new_password) < 6:
                QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
                return

        # Update database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            if new_password:
                hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                c.execute("UPDATE users SET phone = ?, guardian_name = ?, guardian_phone = ?, password = ? WHERE username = ?",
                          (phone, guardian_name, guardian_phone, hashed_pw.decode('utf-8'), self.username))
            else:
                c.execute("UPDATE users SET phone = ?, guardian_name = ?, guardian_phone = ? WHERE username = ?",
                          (phone, guardian_name, guardian_phone, self.username))
            conn.commit()
            QMessageBox.information(self, "Success", "Profile updated successfully")
            self.new_password_input.clear()
            self.confirm_password_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update profile: {e}")
        finally:
            conn.close()
