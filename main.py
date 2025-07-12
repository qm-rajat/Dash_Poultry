import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database.init_db import init_db

def main():
    init_db()
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 