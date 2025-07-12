import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database.init_db import init_db

def main():
    print("🚀 Starting Dash Poultry Application...")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        print("Initializing database...")
        init_db()
        print("Database initialized successfully")
        
        print("Creating QApplication...")
        app = QApplication(sys.argv)
        print("QApplication created successfully")
        
        print("Creating login window...")
        window = LoginWindow()
        print("Login window created successfully")
        
        print("Showing login window...")
        window.show()
        print("Login window should now be visible")
        
        print("Starting application event loop...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 