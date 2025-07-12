from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import os
import bcrypt
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import init_db
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("🔐 Initializing Login Window...")
        self.setWindowTitle("Dash Poultry - Login")
        self.setFixedSize(400, 420)
        
        # Try to set window icon, but don't fail if it doesn't exist
        try:
            icon_path = os.path.join('resources', 'logo.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                print("✅ Window icon set successfully")
            else:
                print("⚠️ Logo file not found, using default icon")
        except Exception as e:
            print(f"⚠️ Could not set window icon: {e}")
        
        self.theme = 'light'
        self.setup_ui()
        self.load_theme()
        print("✅ Login Window initialized successfully")

    def setup_ui(self):
        layout = QVBoxLayout()
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Try multiple possible logo paths
        logo_paths = [
            os.path.join(os.path.dirname(__file__), '../Logo.png'),
            os.path.join('resources', 'logo.png'),
            os.path.join('Logo.png')
        ]
        
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                try:
                    logo.setPixmap(QPixmap(logo_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    print(f"✅ Logo loaded from: {logo_path}")
                    logo_loaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Could not load logo from {logo_path}: {e}")
        
        if not logo_loaded:
            print("⚠️ No logo found, using text placeholder")
            logo.setText("🐔")
            logo.setStyleSheet("font-size: 48px; color: #059669;")
        
        layout.addWidget(logo)

        title = QLabel("<b>Dash Poultry</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; margin-bottom: 16px;")
        layout.addWidget(title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.remember = QCheckBox("Remember me")
        layout.addWidget(self.remember)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        self.setLayout(layout)

    def load_theme(self):
        qss_file = os.path.join('resources', f'theme_{self.theme}.qss')
        if os.path.exists(qss_file):
            with open(qss_file, 'r') as f:
                self.setStyleSheet(f.read())

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.load_theme()

    def handle_login(self):
        from database.init_db import get_connection
        username = self.user_input.text().strip()
        password = self.pass_input.text().encode()
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT password FROM admin WHERE username=?', (username,))
        row = c.fetchone()
        conn.close()
        if row and bcrypt.checkpw(password, row[0]):
            self.open_main_window()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")

    def open_main_window(self):
        print("Opening main window...")
        self.main_window = MainWindow()
        self.main_window.show()
        self.close() 