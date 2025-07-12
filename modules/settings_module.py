from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QFrame, QGridLayout, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
                             QMessageBox, QCheckBox, QSpinBox, QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QIcon
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.data_import_manager import DataImportWidget

class SettingsModuleWidget(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings('DashPoultry', 'DashPoultryApp')
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<b>Settings</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "Appearance")
        
        # Database tab
        self.database_tab = self.create_database_tab()
        self.tab_widget.addTab(self.database_tab, "Database")
        
        # Application tab
        self.application_tab = self.create_application_tab()
        self.tab_widget.addTab(self.application_tab, "Application")
        
        # Data Import/Export tab
        self.import_export_tab = self.create_import_export_tab()
        self.tab_widget.addTab(self.import_export_tab, "Data Import/Export")
        
        # About tab
        self.about_tab = self.create_about_tab()
        self.tab_widget.addTab(self.about_tab, "About")
        
        layout.addWidget(self.tab_widget)
        
        # Save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

    def create_appearance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme settings
        theme_frame = QFrame()
        theme_frame.setFrameStyle(QFrame.Shape.Box)
        theme_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        theme_layout = QFormLayout(theme_frame)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.auto_theme_checkbox = QCheckBox("Automatically switch theme based on system")
        theme_layout.addRow("", self.auto_theme_checkbox)
        
        layout.addWidget(theme_frame)
        
        # Font settings
        font_frame = QFrame()
        font_frame.setFrameStyle(QFrame.Shape.Box)
        font_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        font_layout = QFormLayout(font_frame)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addRow("Font Size:", self.font_size_spin)
        
        layout.addWidget(font_frame)
        
        layout.addStretch()
        return widget

    def create_database_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Database info
        db_frame = QFrame()
        db_frame.setFrameStyle(QFrame.Shape.Box)
        db_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        db_layout = QFormLayout(db_frame)
        
        self.db_path_label = QLabel("Database path will be shown here")
        self.db_path_label.setWordWrap(True)
        db_layout.addRow("Database Path:", self.db_path_label)
        
        self.db_size_label = QLabel("Database size will be shown here")
        db_layout.addRow("Database Size:", self.db_size_label)
        
        layout.addWidget(db_frame)
        
        # Database actions
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Shape.Box)
        actions_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        actions_layout = QVBoxLayout(actions_frame)
        
        self.backup_btn = QPushButton("Backup Database")
        self.backup_btn.clicked.connect(self.backup_database)
        actions_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton("Restore Database")
        self.restore_btn.clicked.connect(self.restore_database)
        actions_layout.addWidget(self.restore_btn)
        
        self.reset_btn = QPushButton("Reset Database (Clear All Data)")
        self.reset_btn.setStyleSheet("QPushButton { background-color: #dc2626; color: white; }")
        self.reset_btn.clicked.connect(self.reset_database)
        actions_layout.addWidget(self.reset_btn)
        
        layout.addWidget(actions_frame)
        
        layout.addStretch()
        return widget

    def create_application_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # General settings
        general_frame = QFrame()
        general_frame.setFrameStyle(QFrame.Shape.Box)
        general_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        general_layout = QFormLayout(general_frame)
        
        self.auto_save_checkbox = QCheckBox("Auto-save data every 5 minutes")
        general_layout.addRow("Auto Save:", self.auto_save_checkbox)
        
        self.startup_checkbox = QCheckBox("Show dashboard on startup")
        general_layout.addRow("Startup:", self.startup_checkbox)
        
        self.notifications_checkbox = QCheckBox("Enable notifications")
        general_layout.addRow("Notifications:", self.notifications_checkbox)
        
        layout.addWidget(general_frame)
        
        # Currency settings
        currency_frame = QFrame()
        currency_frame.setFrameStyle(QFrame.Shape.Box)
        currency_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        currency_layout = QFormLayout(currency_frame)
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"])
        currency_layout.addRow("Currency:", self.currency_combo)
        
        layout.addWidget(currency_frame)
        
        # Export settings
        export_frame = QFrame()
        export_frame.setFrameStyle(QFrame.Shape.Box)
        export_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        export_layout = QFormLayout(export_frame)
        
        self.default_export_format = QComboBox()
        self.default_export_format.addItems(["CSV", "PDF", "Excel"])
        export_layout.addRow("Default Export Format:", self.default_export_format)
        
        layout.addWidget(export_frame)
        
        layout.addStretch()
        return widget

    def create_import_export_tab(self):
        """Create data import/export tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add the data import widget
        import_widget = DataImportWidget()
        layout.addWidget(import_widget)
        
        return widget

    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # App info
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.Box)
        info_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        info_layout = QVBoxLayout(info_frame)
        
        app_title = QLabel("Dash Poultry")
        app_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #059669;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(app_title)
        
        app_version = QLabel("Version 1.0.0")
        app_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(app_version)
        
        app_description = QLabel("A comprehensive poultry farm management system built with PyQt6 and SQLite.")
        app_description.setWordWrap(True)
        app_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(app_description)
        
        layout.addWidget(info_frame)
        
        # Features
        features_frame = QFrame()
        features_frame.setFrameStyle(QFrame.Shape.Box)
        features_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        features_layout = QVBoxLayout(features_frame)
        
        features_title = QLabel("Features:")
        features_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        features_layout.addWidget(features_title)
        
        features = [
            "• Batch Management",
            "• Feed & Water Tracking",
            "• Vaccination Management",
            "• Mortality Tracking",
            "• Worker Management",
            "• Expense Management",
            "• Profit/Loss Analysis",
            "• Data Export (CSV, PDF, Excel)",
            "• Secure Database with Encryption",
            "• Light/Dark Theme Support"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            features_layout.addWidget(feature_label)
        
        layout.addWidget(features_frame)
        
        # System info
        system_frame = QFrame()
        system_frame.setFrameStyle(QFrame.Shape.Box)
        system_frame.setStyleSheet("QFrame { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; }")
        system_layout = QFormLayout(system_frame)
        
        system_layout.addRow("Python Version:", QLabel(sys.version.split()[0]))
        system_layout.addRow("PyQt6 Version:", QLabel("6.0+"))
        system_layout.addRow("Database:", QLabel("SQLite with SQLCipher"))
        
        layout.addWidget(system_frame)
        
        layout.addStretch()
        return widget

    def load_settings(self):
        # Load theme
        theme = self.settings.value('theme', 'Light')
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Load other settings
        self.auto_theme_checkbox.setChecked(self.settings.value('auto_theme', False, type=bool))
        self.font_size_spin.setValue(self.settings.value('font_size', 12, type=int))
        self.auto_save_checkbox.setChecked(self.settings.value('auto_save', True, type=bool))
        self.startup_checkbox.setChecked(self.settings.value('startup_dashboard', True, type=bool))
        self.notifications_checkbox.setChecked(self.settings.value('notifications', True, type=bool))
        
        currency = self.settings.value('currency', '₹ (INR)')
        index = self.currency_combo.findText(currency)
        if index >= 0:
            self.currency_combo.setCurrentIndex(index)
        
        export_format = self.settings.value('default_export_format', 'CSV')
        index = self.default_export_format.findText(export_format)
        if index >= 0:
            self.default_export_format.setCurrentIndex(index)
        
        # Load database info
        self.load_database_info()

    def load_database_info(self):
        try:
            from database.init_db import DB_PATH
            self.db_path_label.setText(DB_PATH)
            
            if os.path.exists(DB_PATH):
                size = os.path.getsize(DB_PATH)
                size_mb = size / (1024 * 1024)
                self.db_size_label.setText(f"{size_mb:.2f} MB")
            else:
                self.db_size_label.setText("Database not found")
        except Exception as e:
            self.db_path_label.setText("Error loading database info")
            self.db_size_label.setText("Unknown")

    def save_settings(self):
        # Save theme
        self.settings.setValue('theme', self.theme_combo.currentText())
        self.settings.setValue('auto_theme', self.auto_theme_checkbox.isChecked())
        self.settings.setValue('font_size', self.font_size_spin.value())
        self.settings.setValue('auto_save', self.auto_save_checkbox.isChecked())
        self.settings.setValue('startup_dashboard', self.startup_checkbox.isChecked())
        self.settings.setValue('notifications', self.notifications_checkbox.isChecked())
        self.settings.setValue('currency', self.currency_combo.currentText())
        self.settings.setValue('default_export_format', self.default_export_format.currentText())
        
        # Apply theme if main window exists
        if self.main_window:
            theme = self.theme_combo.currentText()
            if theme == "Light":
                self.main_window.theme = 'light'
            elif theme == "Dark":
                self.main_window.theme = 'dark'
            self.main_window.load_theme()
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")

    def backup_database(self):
        try:
            from database.init_db import DB_PATH
            filename, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Files (*.db);;All Files (*)")
            if filename:
                import shutil
                shutil.copy2(DB_PATH, filename)
                QMessageBox.information(self, "Backup Complete", f"Database backed up to: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to backup database: {str(e)}")

    def restore_database(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Files (*.db);;All Files (*)")
            if filename:
                reply = QMessageBox.question(self, "Confirm Restore", 
                                           "This will replace the current database. Are you sure?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    from database.init_db import DB_PATH
                    import shutil
                    shutil.copy2(filename, DB_PATH)
                    QMessageBox.information(self, "Restore Complete", "Database restored successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Failed to restore database: {str(e)}")

    def reset_database(self):
        reply = QMessageBox.question(self, "Confirm Reset", 
                                   "This will delete ALL data in the database. This action cannot be undone!\n\nAre you absolutely sure?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from database.init_db import DB_PATH
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                from database.init_db import init_db
                init_db()
                QMessageBox.information(self, "Reset Complete", "Database has been reset to default state!")
            except Exception as e:
                QMessageBox.critical(self, "Reset Error", f"Failed to reset database: {str(e)}") 