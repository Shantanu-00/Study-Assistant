import os
import json
import cv2
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QScrollArea, QGroupBox, QRadioButton, QButtonGroup, QDialog, QFrame, QSizePolicy,
                             QTextEdit, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QTime
from PyQt5.QtGui import QImage, QPixmap, QFont
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from detection_thread import DetectionThread
import google.generativeai as genai
from config import GOOGLE_API_KEY
from profile_manager import ProfileManager

class StudyAssistantWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Study Buddy - {self.username}")
        self.setFixedSize(1200, 800)
        self.init_ui()
        self.setup_detection_thread()
        self.setup_styles()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar_layout.setSpacing(10)

        self.focus_btn = QPushButton("📹 Focus Zone")
        self.focus_btn.clicked.connect(lambda: self.show_content("focus"))
        self.notes_btn = QPushButton("📝 Notes")
        self.notes_btn.clicked.connect(lambda: self.show_content("notes"))
        self.quiz_btn = QPushButton("🎯 Quiz")
        self.quiz_btn.clicked.connect(lambda: self.show_content("quiz"))
        self.profile_btn = QPushButton("👤 Profile")
        self.profile_btn.clicked.connect(lambda: self.show_content("profile"))
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.clicked.connect(self.logout)

        for btn in [self.focus_btn, self.notes_btn, self.quiz_btn, self.profile_btn, self.logout_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.sidebar_layout.addWidget(btn)
        self.sidebar_layout.addStretch()

        self.main_layout.addWidget(self.sidebar)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(self.content_widget)

        # Content pages
        self.content_pages = {
            "focus": QWidget(),
            "notes": QWidget(),
            "quiz": QWidget(),
            "profile": QWidget()
        }

        # Focus Zone
        self.focus_layout = QVBoxLayout(self.content_pages["focus"])
        self.video_label = QLabel("Starting camera...")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(800, 600)
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.focus_layout.addWidget(self.video_label, stretch=1, alignment=Qt.AlignCenter)
        self.alert_label = QLabel("Keeping you on track...")
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.focus_layout.addWidget(self.alert_label, stretch=0)
        self.log_label = QLabel("Distraction Log:\nNo distractions yet.")
        self.log_label.setWordWrap(True)
        self.focus_layout.addWidget(self.log_label, stretch=0)
        self.focus_layout.addStretch()

        # Notes
        self.notes_layout = QVBoxLayout(self.content_pages["notes"])
        self.upload_btn = QPushButton("📤 Upload Notes")
        self.upload_btn.clicked.connect(self.upload_pdf)
        self.notes_layout.addWidget(self.upload_btn, stretch=0)
        self.notes_layout.addWidget(self.output_scroll, stretch=4)
        self.output_scroll.setMinimumHeight(600)
        self.summary_btn = QPushButton("✨ Generate Summary")
        self.summary_btn.clicked.connect(self.generate_summary)
        self.notes_layout.addWidget(self.summary_btn, stretch=0)
        self.quiz_gen_btn = QPushButton("🎯 Generate Quiz for Quiz Tab")
        self.quiz_gen_btn.clicked.connect(self.generate_quiz)
        self.notes_layout.addWidget(self.quiz_gen_btn, stretch=0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.notes_layout.addWidget(self.progress_bar, stretch=0)
        self.output_scroll = QScrollArea()
        self.output_widget = QWidget()
        self.output_layout = QVBoxLayout(self.output_widget)
        self.output_layout.setContentsMargins(10, 10, 10, 10)
        self.output_scroll.setWidget(self.output_widget)
        self.output_scroll.setWidgetResizable(True)
        self.notes_layout.addStretch()

        # Quiz
        self.quiz_layout = QVBoxLayout(self.content_pages["quiz"])
        self.quiz_scroll = QScrollArea()
        self.quiz_scroll.setWidgetResizable(True)
        self.quiz_content = QWidget()
        self.quiz_content_layout = QVBoxLayout(self.quiz_content)
        self.quiz_content_layout.setContentsMargins(10, 10, 10, 10)
        self.quiz_content_layout.setSpacing(15)
        self.quiz_scroll.setWidget(self.quiz_content)
        self.quiz_layout.addWidget(self.quiz_scroll)
        self.quiz_scroll.setMinimumHeight(600)
        self.quiz_placeholder = QLabel("Generate a quiz from Notes to start!")
        self.quiz_placeholder.setAlignment(Qt.AlignCenter)
        self.quiz_placeholder.setMinimumHeight(400)
        self.quiz_content_layout.addWidget(self.quiz_placeholder)
        self.quiz_content_layout.addStretch()

        # Profile
        self.profile_layout = QVBoxLayout(self.content_pages["profile"])
        self.profile_manager = ProfileManager(self.username)
        self.profile_layout.addWidget(self.profile_manager)
        self.profile_layout.addStretch()

        # Stack content pages
        self.current_content = "focus"
        for key, widget in self.content_pages.items():
            widget.setVisible(key == self.current_content)
            self.content_layout.addWidget(widget)
        self.content_layout.addStretch()

    def show_content(self, page):
        self.content_pages[self.current_content].setVisible(False)
        self.content_pages[page].setVisible(True)
        self.current_content = page

    def setup_detection_thread(self):
        from models import model, face_mesh, engine
        self.detection_thread = DetectionThread(model, face_mesh, self.username)
        self.detection_thread.frame_signal.connect(self.update_frame)
        self.detection_thread.alert_signal.connect(self.show_alert)
        self.detection_thread.start()

        self.alert_animation = QPropertyAnimation(self.alert_label, b"geometry")
        self.alert_animation.setDuration(300)
        self.alert_animation.setStartValue(QRect(0, 0, self.alert_label.width(), self.alert_label.height()))
        self.alert_animation.setEndValue(QRect(0, -5, self.alert_label.width(), self.alert_label.height()))
        self.alert_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.alert_animation.setLoopCount(2)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E293B; /* Slate-800 */
            }
            QFrame {
                background-color: #2D3748; /* Slate-700 */
                border-radius: 12px;
            }
            QPushButton {
                background-color: #3B82F6; /* Blue-500 */
                color: #F1F5F9;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
                transition: background-color 0.2s ease, transform 0.1s ease;
            }
            QPushButton:hover {
                background-color: #60A5FA; /* Blue-400 */
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #2563EB; /* Blue-600 */
                transform: scale(0.98);
            }
            QPushButton:disabled {
                background-color: #6B7280; /* Slate-500 */
                color: #D1D5DB;
            }
            QLabel {
                color: #F1F5F9; /* Slate-100 */
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
            }
            QTextEdit {
                background-color: #4B5563; /* Slate-600 */
                color: #F1F5F9;
                border: none;
                padding: 20px;
                border-radius: 10px;
                font-size: 18px;
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
            }
            QProgressBar {
                border: 2px solid #3B82F6;
                border-radius: 6px;
                background-color: #2D3748;
                color: #F1F5F9;
                font-family: 'Roboto', sans-serif;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
            QScrollArea {
                border: none;
                background-color: #1E293B;
            }
            QScrollArea QWidget {
                background-color: #1E293B;
            }
            QGroupBox {
                background-color: #2D3748;
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                color: #F1F5F9;
                font-size: 20px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QRadioButton {
                color: #F1F5F9;
                font-size: 18px;
                font-family: 'Roboto', sans-serif;
                padding: 12px;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 24px;
                height: 24px;
                border-radius: 12px;
                border: 2px solid #3B82F6;
                background-color: #1E293B;
            }
            QRadioButton::indicator:checked {
                background-color: #3B82F6;
                border: 2px solid #60A5FA;
            }
            QRadioButton:hover {
                background-color: #4B5563;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2D3748;
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3B82F6;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        self.alert_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #F59E0B; /* Amber-500 */
                background-color: rgba(45, 55, 72, 0.9); /* Slate-700 semi-transparent */
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #F59E0B;
            }
        """)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #111827; /* Slate-900 */
                border-radius: 12px;
                border: 2px solid #475569; /* Slate-600 */
                padding: 10px;
            }
        """)
        self.log_label.setStyleSheet("""
            QLabel {
                background-color: #2D3748;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                color: #D1D5DB; /* Slate-300 */
            }
        """)

    def closeEvent(self, event):
        self.detection_thread.stop()
        event.accept()

    def logout(self):
        self.detection_thread.stop()
        self.close()
        from auth import LoginDialog
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            new_window = StudyAssistantWindow(login_dialog.current_user)
            new_window.show()

    def update_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    def show_alert(self, message, frame):
        from models import engine
        self.alert_label.setText(f"⚡ {message}")
        self.alert_animation.start()
        engine.say(message)
        engine.runAndWait()
        print(f"[DEBUG] Speaking: {message}")
        self.log_label.setText(f"Distraction Log:\n{message} at {QTime.currentTime().toString()}")
        QTimer.singleShot(5000, lambda: self.alert_label.setText("Keeping you on track..."))

    def upload_pdf(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if pdf_path:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    self.pdf_text = text
                    self.clear_output()
                    label = QLabel("✅ Notes uploaded successfully!")
                    label.setStyleSheet("font-size: 16px; color: #3B82F6; background-color: #2D3748; padding: 12px; border-radius: 8px;")
                    self.output_layout.addWidget(label)
            except Exception as e:
                self.clear_output()
                label = QLabel(f"❌ Error: {e}")
                label.setStyleSheet("font-size: 16px; color: #EF4444; background-color: #2D3748; padding: 12px; border-radius: 8px;")
                self.output_layout.addWidget(label)
        self.progress_bar.setVisible(False)

    def generate_summary(self):
        if not hasattr(self, 'pdf_text'):
            self.clear_output()
            label = QLabel("⚠️ Upload notes first!")
            label.setStyleSheet("font-size: 16px; color: #F59E0B; background-color: #2D3748; padding: 12px; border-radius: 8px;")
            self.output_layout.addWidget(label)
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Summarize this text:\n\n{self.pdf_text}"
            response = model.generate_content(prompt)
            self.summary = response.text
            self.display_summary()
        except Exception as e:
            self.clear_output()
            label = QLabel(f"❌ Error: {e}")
            label.setStyleSheet("font-size: 16px; color: #EF4444; background-color: #2D3748; padding: 12px; border-radius: 8px;")
            self.output_layout.addWidget(label)
        self.progress_bar.setVisible(False)

    def display_summary(self):
        self.clear_output()
        summary_group = QGroupBox("Summary")
        summary_group.setStyleSheet("""
            QGroupBox {
                background-color: #2D3748; /* Slate-800 */
                border: none;
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                color: #F1F5F9;
                font-size: 22px;
                font-family: 'Roboto', sans-serif;
                font-weight: 700;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """)
        summary_layout = QVBoxLayout()
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        summary_text.setText(self.summary)
        summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #4B5563; /* Slate-600 */
                color: #F1F5F9;
                border: none;
                padding: 20px;
                border-radius: 10px;
                font-size: 18px;
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                border: none;
                background: #2D3748;
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3B82F6;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        summary_text.setMinimumHeight(700)  # Increased size
        summary_layout.addWidget(summary_text)
        summary_group.setLayout(summary_layout)
        self.output_layout.addWidget(summary_group)

        download_btn = QPushButton("⬇ Download Summary as PDF")
        download_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F1F5F9;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
                transition: background-color 0.2s ease;
            }
            QPushButton:hover {
                background-color: #60A5FA;
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        download_btn.clicked.connect(self.download_summary)
        self.output_layout.addWidget(download_btn)
        self.output_layout.addStretch()

    def generate_quiz(self):
        if not hasattr(self, 'pdf_text'):
            self.clear_output()
            label = QLabel("⚠️ Upload notes first!")
            label.setStyleSheet("font-size: 16px; color: #F59E0B; background-color: #2D3748; padding: 12px; border-radius: 8px;")
            self.output_layout.addWidget(label)
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""Create 5 multiple-choice questions based on this text in JSON format:
            Format: 
            [
                {{
                    "question": "Question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A"
                }}
            ]
            Text:\n\n{self.pdf_text}"""
            response = model.generate_content(prompt)
            quiz_text = response.text.strip()
            if quiz_text.startswith("```json"):
                quiz_text = quiz_text[7:-3].strip()
            self.quiz_data = json.loads(quiz_text)
            self.display_quiz()
            self.show_content("quiz")  # Switch to Quiz tab
        except Exception as e:
            self.clear_output()
            label = QLabel(f"❌ Error: {e}")
            label.setStyleSheet("font-size: 16px; color: #EF4444; background-color: #2D3748; padding: 12px; border-radius: 8px;")
            self.output_layout.addWidget(label)
        self.progress_bar.setVisible(False)

    def display_quiz(self):
        # Clear existing quiz content
        while self.quiz_content_layout.count():
            child = self.quiz_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.button_groups = []
        for i, q in enumerate(self.quiz_data, 1):
            question_group = QGroupBox(f"Question {i}: {q['question']}")
            question_group.setStyleSheet("""
                QGroupBox {
                    background-color: #2D3748;
                    border: none;
                    border-radius: 12px;
                    margin-top: 20px;
                    padding: 25px;
                    color: #F1F5F9;
                    font-size: 20px;
                    font-family: 'Roboto', sans-serif;
                    font-weight: 600;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
            """)
            question_layout = QVBoxLayout()
            question_layout.setSpacing(15)  # More spacing between options
            button_group = QButtonGroup()
            button_group.setExclusive(True)
            self.button_groups.append((button_group, q['correct_answer']))
            for option in q['options']:
                radio = QRadioButton(option)
                radio.setStyleSheet("""
                    QRadioButton {
                        color: #F1F5F9;
                        font-size: 18px;
                        font-family: 'Roboto', sans-serif;
                        padding: 12px;
                        spacing: 10px;
                        background-color: transparent;
                    }
                    QRadioButton::indicator {
                        width: 24px;
                        height: 24px;
                        border-radius: 12px;
                        border: 2px solid #3B82F6;
                        background-color: #1E293B;
                    }
                    QRadioButton::indicator:checked {
                        background-color: #3B82F6;
                        border: 2px solid #60A5FA;
                    }
                    QRadioButton:hover {
                        background-color: #4B5563;
                        border-radius: 8px;
                    }
                """)
                question_layout.addWidget(radio)
                button_group.addButton(radio)
            question_group.setLayout(question_layout)
            self.quiz_content_layout.addWidget(question_group)

        evaluate_btn = QPushButton("📊 Evaluate Score")
        evaluate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #F1F5F9;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                font-weight: 600;
                transition: background-color 0.2s ease;
            }
            QPushButton:hover {
                background-color: #60A5FA;
            }
            QPushButton:pressed {
                background-color: #2563EB;
            }
        """)
        evaluate_btn.clicked.connect(self.evaluate_quiz_score)
        self.quiz_content_layout.addWidget(evaluate_btn)
        self.quiz_content_layout.addStretch()

        self.quiz_placeholder.setVisible(False)

    def evaluate_quiz_score(self):
        score = 0
        total_questions = len(self.quiz_data)
        for button_group, correct_answer in self.button_groups:
            selected_button = button_group.checkedButton()
            if selected_button and selected_button.text() == correct_answer:
                score += 1

        score_text = f"Score: {score}/{total_questions} ({(score/total_questions)*100:.1f}%)"
        score_label = QLabel(score_text)
        score_label.setStyleSheet("font-size: 20px; color: #3B82F6; background-color: #2D3748; padding: 12px; border-radius: 8px; font-weight: 600;")
        self.quiz_content_layout.addWidget(score_label)
        self.quiz_content_layout.addStretch()

    def download_summary(self):
        if not hasattr(self, 'summary'):
            return
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Save Summary", "summary.pdf", "PDF Files (*.pdf)")
        if pdf_path:
            try:
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                story.append(Paragraph("Summary", styles['Title']))
                story.append(Paragraph(self.summary, styles['Normal']))
                doc.build(story)
                print(f"[DEBUG] Summary saved to {pdf_path}")
            except Exception as e:
                print(f"[ERROR] Failed to save summary: {e}")

    def clear_output(self):
        while self.output_layout.count():
            child = self.output_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()