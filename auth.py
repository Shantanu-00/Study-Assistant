import sqlite3
import bcrypt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, name TEXT, phone TEXT, 
                  guardian_name TEXT, guardian_phone TEXT)''')
    conn.commit()
    conn.close()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Buddy - Login / Signup")
        self.setFixedSize(700, 500)  # Larger for balance
        self.setup_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #1E293B; /* Slate-800 */
            }
            QFrame {
                background-color: #334155; /* Slate-700 */
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #F1F5F9; /* Slate-100 */
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #475569; /* Slate-600 */
                color: #F1F5F9;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Roboto', sans-serif;
                width: 250px;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6; /* Blue-500 */
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

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Login Section
        login_frame = QFrame()
        login_layout = QVBoxLayout(login_frame)
        login_layout.setSpacing(15)
        login_label = QLabel("Login")
        login_label.setStyleSheet("font-size: 22px; font-weight: 700;")
        login_layout.addWidget(login_label, alignment=Qt.AlignCenter)

        username_label = QLabel("Username")
        login_layout.addWidget(username_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        login_layout.addWidget(self.username_input)

        password_label = QLabel("Password")
        login_layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        login_layout.addWidget(self.login_btn)
        login_layout.addStretch()

        main_layout.addWidget(login_frame)

        # Signup Section
        signup_frame = QFrame()
        signup_layout = QVBoxLayout(signup_frame)
        signup_layout.setSpacing(15)
        signup_label = QLabel("Signup")
        signup_label.setStyleSheet("font-size: 22px; font-weight: 700;")
        signup_layout.addWidget(signup_label, alignment=Qt.AlignCenter)

        name_label = QLabel("Full Name")
        signup_layout.addWidget(name_label)
        self.signup_name_input = QLineEdit()
        self.signup_name_input.setPlaceholderText("Enter full name")
        signup_layout.addWidget(self.signup_name_input)

        phone_label = QLabel("Phone Number")
        signup_layout.addWidget(phone_label)
        self.signup_phone_input = QLineEdit()
        self.signup_phone_input.setPlaceholderText("Enter phone number")
        signup_layout.addWidget(self.signup_phone_input)

        username_label = QLabel("Username")
        signup_layout.addWidget(username_label)
        self.signup_username_input = QLineEdit()
        self.signup_username_input.setPlaceholderText("Choose a username")
        signup_layout.addWidget(self.signup_username_input)

        password_label = QLabel("Password")
        signup_layout.addWidget(password_label)
        self.signup_password_input = QLineEdit()
        self.signup_password_input.setPlaceholderText("Choose a password")
        self.signup_password_input.setEchoMode(QLineEdit.Password)
        signup_layout.addWidget(self.signup_password_input)

        guardian_name_label = QLabel("Guardian Name")
        signup_layout.addWidget(guardian_name_label)
        self.guardian_name_input = QLineEdit()
        self.guardian_name_input.setPlaceholderText("Enter guardian name")
        signup_layout.addWidget(self.guardian_name_input)

        guardian_phone_label = QLabel("Guardian WhatsApp Number")
        signup_layout.addWidget(guardian_phone_label)
        self.guardian_phone_input = QLineEdit()
        self.guardian_phone_input.setPlaceholderText("Enter guardian WhatsApp")
        signup_layout.addWidget(self.guardian_phone_input)

        self.signup_btn = QPushButton("Signup")
        self.signup_btn.clicked.connect(self.signup)
        signup_layout.addWidget(self.signup_btn)
        signup_layout.addStretch()

        main_layout.addWidget(signup_frame)
        self.setLayout(main_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text().encode('utf-8')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password, result[0].encode('utf-8')):
            self.current_user = username
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def signup(self):
        username = self.signup_username_input.text()
        password = self.signup_password_input.text().encode('utf-8')
        name = self.signup_name_input.text()
        phone = self.signup_phone_input.text()
        guardian_name = self.guardian_name_input.text()
        guardian_phone = self.guardian_phone_input.text()

        if not all([username, password, name, phone, guardian_name, guardian_phone]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                      (username, hashed_pw.decode('utf-8'), name, phone, guardian_name, guardian_phone))
            conn.commit()
            QMessageBox.information(self, "Success", "Signup successful! Please login.")
            self.signup_username_input.clear()
            self.signup_password_input.clear()
            self.signup_name_input.clear()
            self.signup_phone_input.clear()
            self.guardian_name_input.clear()
            self.guardian_phone_input.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists")
        finally:
            conn.close()

init_db()