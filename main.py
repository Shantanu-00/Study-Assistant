import sys
import os
import mediapipe as mp
from PyQt5.QtWidgets import QApplication, QDialog  # Added QDialog import
from gui import StudyAssistantWindow
from auth import LoginDialog

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    
    # Show login/signup dialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        window = StudyAssistantWindow(login_dialog.current_user)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()