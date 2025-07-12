from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class NotificationWidget(QWidget):
    """Individual notification widget"""
    closed = pyqtSignal()
    
    def __init__(self, title, message, notification_type="info", parent=None):
        super().__init__(parent)
        self.notification_type = notification_type
        self.init_ui(title, message)
        
        # Auto-close timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.close_notification)
        self.timer.start(5000)  # 5 seconds
    
    def init_ui(self, title, message):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Style based on notification type
        if self.notification_type == "success":
            bg_color = "#d1fae5"
            border_color = "#10b981"
            text_color = "#065f46"
        elif self.notification_type == "warning":
            bg_color = "#fef3c7"
            border_color = "#f59e0b"
            text_color = "#92400e"
        elif self.notification_type == "error":
            bg_color = "#fee2e2"
            border_color = "#ef4444"
            text_color = "#991b1b"
        else:  # info
            bg_color = "#dbeafe"
            border_color = "#3b82f6"
            text_color = "#1e40af"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                color: {text_color};
            }}
        """)
        
        # Header with title and close button
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {border_color};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {text_color};
            }}
        """)
        close_btn.clicked.connect(self.close_notification)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 9))
        layout.addWidget(message_label)
    
    def close_notification(self):
        self.timer.stop()
        self.closed.emit()
        self.deleteLater()

class NotificationManager(QWidget):
    """Manages notification display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.layout.addStretch()
    
    def show_notification(self, title, message, notification_type="info"):
        """Show a new notification"""
        notification = NotificationWidget(title, message, notification_type, self)
        notification.closed.connect(lambda: self.remove_notification(notification))
        
        # Insert at the top (before the stretch)
        self.layout.insertWidget(len(self.notifications), notification)
        self.notifications.append(notification)
        
        # Show the notification manager if it's not visible
        if not self.isVisible():
            self.show()
    
    def remove_notification(self, notification):
        """Remove a notification"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.layout.removeWidget(notification)
            
            # Hide the manager if no notifications left
            if not self.notifications:
                self.hide()
    
    def show_success(self, title, message):
        """Show success notification"""
        self.show_notification(title, message, "success")
    
    def show_warning(self, title, message):
        """Show warning notification"""
        self.show_notification(title, message, "warning")
    
    def show_error(self, title, message):
        """Show error notification"""
        self.show_notification(title, message, "error")
    
    def show_info(self, title, message):
        """Show info notification"""
        self.show_notification(title, message, "info")

# Global notification manager instance
notification_manager = None 