from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QListWidget, QListWidgetItem, QFrame)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_manager import data_manager
from utils.notification_manager import NotificationManager
from modules.dashboard import DashboardWidget
from modules.batch_management import BatchManagementWidget
from modules.feed_water_logs import FeedWaterLogsWidget
from modules.vaccination_tracker import VaccinationTrackerWidget
from modules.mortality_tracker import MortalityTrackerWidget
from modules.workers_management import WorkersManagementWidget
from modules.expenses_management import ExpensesManagementWidget
from modules.profit_loss_analysis import ProfitLossAnalysisWidget
from modules.export_module import ExportModuleWidget
from modules.settings_module import SettingsModuleWidget

MODULES = [
    ("Dashboard", "dashboard"),
    ("Batches", "batches"),
    ("Feed/Water", "feed"),
    ("Vaccination", "vaccine"),
    ("Mortality", "mortality"),
    ("Workers", "workers"),
    ("Expenses", "expenses"),
    ("Profit/Loss", "profit"),
    ("Export", "export"),
    ("Settings", "settings"),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dash Poultry")
        self.setMinimumSize(1280, 720)
        self.setWindowIcon(QIcon(os.path.join('resources', 'logo.png')))
        self.theme = 'light'
        
        # Initialize notification manager
        global notification_manager
        notification_manager = NotificationManager(self)
        
        self.init_ui()
        self.setup_data_connections()
        self.showMaximized()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(180)
        self.sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar.setStyleSheet('''
            QListWidget {
                background: #f5f6fa;
                border: none;
                padding: 12px 0;
            }
            QListWidget::item {
                height: 44px;
                padding-left: 18px;
                margin-bottom: 4px;
                border-radius: 8px;
                color: #444;
                font-size: 15px;
            }
            QListWidget::item:selected {
                background: #e0e7ff;
                color: #2a3cff;
            }
            QListWidget::item:hover {
                background: #e9ecef;
            }
        ''')
        for i, (label, icon) in enumerate(MODULES):
            item = QListWidgetItem(label)
            icon_path = os.path.join('resources', f'{icon}.svg')
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.sidebar.addItem(item)
        self.sidebar.setIconSize(QSize(22, 22))
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.switch_module)
        main_layout.addWidget(self.sidebar)

        # Central area
        central_layout = QVBoxLayout()
        # Top bar
        top_bar = QHBoxLayout()
        app_label = QLabel("<b>Dash Poultry</b>")
        app_label.setStyleSheet("font-size: 20px;")
        top_bar.addWidget(app_label)
        top_bar.addStretch()
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_btn)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(self.logout_btn)
        central_layout.addLayout(top_bar)

        # Stacked widget for modules
        self.stack = QStackedWidget()
        # Create widgets and store references
        self.dashboard_widget = DashboardWidget()
        self.batch_widget = BatchManagementWidget()
        self.feed_water_widget = FeedWaterLogsWidget()
        self.vaccination_widget = VaccinationTrackerWidget()
        self.mortality_widget = MortalityTrackerWidget()
        self.workers_widget = WorkersManagementWidget()
        self.expenses_widget = ExpensesManagementWidget()
        self.profit_loss_widget = ProfitLossAnalysisWidget()
        self.export_widget = ExportModuleWidget()
        self.settings_widget = SettingsModuleWidget(self)
        
        # Add widgets to stack
        self.stack.addWidget(self.dashboard_widget)
        self.stack.addWidget(self.batch_widget)
        self.stack.addWidget(self.feed_water_widget)
        self.stack.addWidget(self.vaccination_widget)
        self.stack.addWidget(self.mortality_widget)
        self.stack.addWidget(self.workers_widget)
        self.stack.addWidget(self.expenses_widget)
        self.stack.addWidget(self.profit_loss_widget)
        self.stack.addWidget(self.export_widget)
        self.stack.addWidget(self.settings_widget)
        
        # Connect dashboard signals
        self.dashboard_widget.module_switch_requested.connect(self.switch_module)
        central_layout.addWidget(self.stack)
        
        # Add notification area
        notification_layout = QHBoxLayout()
        notification_layout.addStretch()
        notification_layout.addWidget(notification_manager)
        central_layout.addLayout(notification_layout)

        main_layout.addLayout(central_layout)
        self.setCentralWidget(main_widget)
        self.load_theme()

    def switch_module(self, idx):
        self.stack.setCurrentIndex(idx)

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.load_theme()
        self.update_sidebar_theme()

    def load_theme(self):
        qss_file = os.path.join('resources', f'theme_{self.theme}.qss')
        if os.path.exists(qss_file):
            with open(qss_file, 'r') as f:
                self.setStyleSheet(f.read())
        self.update_sidebar_theme()

    def update_sidebar_theme(self):
        if self.theme == 'dark':
            self.sidebar.setStyleSheet('''
                QListWidget {
                    background: #23272e;
                    border: none;
                    padding: 12px 0;
                }
                QListWidget::item {
                    height: 44px;
                    padding-left: 18px;
                    margin-bottom: 4px;
                    border-radius: 8px;
                    color: #eee;
                    font-size: 15px;
                }
                QListWidget::item:selected {
                    background: #2a3cff;
                    color: #fff;
                }
                QListWidget::item:hover {
                    background: #2d323b;
                }
            ''')
        else:
            self.sidebar.setStyleSheet('''
                QListWidget {
                    background: #f5f6fa;
                    border: none;
                    padding: 12px 0;
                }
                QListWidget::item {
                    height: 44px;
                    padding-left: 18px;
                    margin-bottom: 4px;
                    border-radius: 8px;
                    color: #444;
                    font-size: 15px;
                }
                QListWidget::item:selected {
                    background: #e0e7ff;
                    color: #2a3cff;
                }
                QListWidget::item:hover {
                    background: #e9ecef;
                }
            ''')

    def setup_data_connections(self):
        """Setup connections to data manager signals"""
        data_manager.batch_data_changed.connect(self.on_batch_data_changed)
        data_manager.feed_water_data_changed.connect(self.on_feed_water_data_changed)
        data_manager.vaccination_data_changed.connect(self.on_vaccination_data_changed)
        data_manager.mortality_data_changed.connect(self.on_mortality_data_changed)
        data_manager.worker_data_changed.connect(self.on_worker_data_changed)
        data_manager.expense_data_changed.connect(self.on_expense_data_changed)
        data_manager.revenue_data_changed.connect(self.on_revenue_data_changed)
    
    def on_batch_data_changed(self):
        """Handle batch data changes"""
        notification_manager.show_success("Batch Updated", "Batch information has been updated successfully.")
        self.dashboard_widget.refresh_data()
    
    def on_feed_water_data_changed(self):
        """Handle feed/water data changes"""
        notification_manager.show_info("Feed/Water Logged", "Feed and water consumption has been recorded.")
        self.dashboard_widget.refresh_data()
    
    def on_vaccination_data_changed(self):
        """Handle vaccination data changes"""
        notification_manager.show_success("Vaccination Recorded", "Vaccination information has been saved.")
        self.dashboard_widget.refresh_data()
    
    def on_mortality_data_changed(self):
        """Handle mortality data changes"""
        notification_manager.show_warning("Mortality Recorded", "Mortality data has been updated.")
        self.dashboard_widget.refresh_data()
    
    def on_worker_data_changed(self):
        """Handle worker data changes"""
        notification_manager.show_info("Worker Updated", "Worker information has been modified.")
        self.dashboard_widget.refresh_data()
    
    def on_expense_data_changed(self):
        """Handle expense data changes"""
        notification_manager.show_info("Expense Recorded", "New expense has been added to the system.")
        self.dashboard_widget.refresh_data()
    
    def on_revenue_data_changed(self):
        """Handle revenue data changes"""
        notification_manager.show_success("Revenue Recorded", "Revenue information has been updated.")
        self.dashboard_widget.refresh_data()

    def logout(self):
        self.close()
        # Optionally, show login window again (handled in main.py) 