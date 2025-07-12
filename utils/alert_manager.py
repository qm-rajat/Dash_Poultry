from PyQt6.QtCore import QObject, QTimer, QDateTime, pyqtSignal
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.notification_manager import notification_manager

class AlertManager(QObject):
    """Manages automated alerts and reminders"""
    
    alert_triggered = pyqtSignal(str, str, str)  # title, message, alert_type
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alerts)
        
        # Initialize system tray icon
        self.setup_system_tray()
        
        # Alert thresholds
        self.thresholds = {
            'mortality_rate': 0.05,  # 5% mortality rate threshold
            'feed_low': 100,  # kg
            'water_low': 500,  # L
            'vaccination_due': 7,  # days
            'batch_end': 3,  # days
            'expense_high': 10000,  # ₹
        }
    
    def start_monitoring(self):
        """Start the alert monitoring timer"""
        self.timer.start(300000)  # Check every 5 minutes
    
    def setup_system_tray(self):
        """Setup system tray icon for notifications"""
        try:
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(QIcon(os.path.join('resources', 'logo.png')))
            self.tray_icon.setToolTip("Dash Poultry - Farm Management")
            
            # Create context menu
            menu = QMenu()
            show_action = QAction("Show Dashboard", self)
            show_action.triggered.connect(self.show_dashboard)
            menu.addAction(show_action)
            
            menu.addSeparator()
            
            check_alerts_action = QAction("Check Alerts Now", self)
            check_alerts_action.triggered.connect(self.check_alerts)
            menu.addAction(check_alerts_action)
            
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()
        except Exception as e:
            print(f"System tray setup failed: {e}")
    
    def show_dashboard(self):
        """Show the main application window"""
        # This will be connected to the main window
        pass
    
    def check_alerts(self):
        """Check for various alerts and triggers"""
        self.check_mortality_alerts()
        self.check_feed_water_alerts()
        self.check_vaccination_alerts()
        self.check_batch_alerts()
        self.check_expense_alerts()
        self.check_worker_alerts()
    
    def check_mortality_alerts(self):
        """Check for high mortality rates"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check recent mortality (last 7 days)
        c.execute('''
            SELECT b.batch_id, b.num_chicks, COALESCE(SUM(m.count), 0) as total_mortality
            FROM batches b
            LEFT JOIN mortality m ON b.batch_id = m.batch_id 
                AND m.date >= date('now', '-7 days')
            GROUP BY b.batch_id, b.num_chicks
            HAVING total_mortality > 0
        ''')
        
        high_mortality_batches = []
        for row in c.fetchall():
            batch_id, num_chicks, mortality = row
            mortality_rate = mortality / num_chicks if num_chicks > 0 else 0
            
            if mortality_rate > self.thresholds['mortality_rate']:
                high_mortality_batches.append({
                    'batch_id': batch_id,
                    'rate': mortality_rate,
                    'count': mortality
                })
        
        if high_mortality_batches:
            for batch in high_mortality_batches:
                self.trigger_alert(
                    "High Mortality Alert",
                    f"Batch {batch['batch_id']} has {batch['rate']:.1%} mortality rate ({batch['count']} birds). Please investigate immediately.",
                    "critical"
                )
        
        conn.close()
    
    def check_feed_water_alerts(self):
        """Check for low feed/water levels"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check feed levels (last 3 days average)
        c.execute('''
            SELECT SUM(quantity_kg) as total_feed
            FROM feed_logs
            WHERE date >= date('now', '-3 days')
        ''')
        feed_result = c.fetchone()
        total_feed = feed_result[0] if feed_result[0] else 0
        
        if total_feed < self.thresholds['feed_low']:
            self.trigger_alert(
                "Low Feed Alert",
                f"Feed consumption is low ({total_feed}kg in last 3 days). Check feed supply and bird health.",
                "warning"
            )
        
        # Check water levels
        c.execute('''
            SELECT SUM(quantity_l) as total_water
            FROM water_logs
            WHERE date >= date('now', '-3 days')
        ''')
        water_result = c.fetchone()
        total_water = water_result[0] if water_result[0] else 0
        
        if total_water < self.thresholds['water_low']:
            self.trigger_alert(
                "Low Water Alert",
                f"Water consumption is low ({total_water}L in last 3 days). Check water supply and bird health.",
                "warning"
            )
        
        conn.close()
    
    def check_vaccination_alerts(self):
        """Check for upcoming vaccinations"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check scheduled vaccinations due soon
        c.execute('''
            SELECT batch_id, vaccine_type, scheduled_date
            FROM vaccinations
            WHERE status = 'Scheduled'
            AND scheduled_date BETWEEN date('now') AND date('now', '+7 days')
            ORDER BY scheduled_date
        ''')
        
        upcoming_vaccinations = c.fetchall()
        for row in upcoming_vaccinations:
            batch_id, vaccine_type, scheduled_date = row
            days_until = (QDateTime.fromString(scheduled_date, 'yyyy-MM-dd').date().daysTo(QDateTime.currentDateTime().date()))
            
            if days_until <= self.thresholds['vaccination_due']:
                self.trigger_alert(
                    "Vaccination Due",
                    f"Vaccination for batch {batch_id} ({vaccine_type}) is due on {scheduled_date}.",
                    "info"
                )
        
        conn.close()
    
    def check_batch_alerts(self):
        """Check for batch end dates"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check batches ending soon
        c.execute('''
            SELECT batch_id, expected_out, num_chicks
            FROM batches
            WHERE expected_out BETWEEN date('now') AND date('now', '+3 days')
        ''')
        
        ending_batches = c.fetchall()
        for row in ending_batches:
            batch_id, expected_out, num_chicks = row
            days_until = (QDateTime.fromString(expected_out, 'yyyy-MM-dd').date().daysTo(QDateTime.currentDateTime().date()))
            
            if days_until <= self.thresholds['batch_end']:
                self.trigger_alert(
                    "Batch Ending Soon",
                    f"Batch {batch_id} ({num_chicks} birds) is expected to end on {expected_out}. Prepare for processing.",
                    "info"
                )
        
        conn.close()
    
    def check_expense_alerts(self):
        """Check for high expenses"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check high expenses in last 30 days
        c.execute('''
            SELECT category, SUM(amount) as total_amount
            FROM expenses
            WHERE date >= date('now', '-30 days')
            GROUP BY category
            HAVING total_amount > ?
        ''', (self.thresholds['expense_high'],))
        
        high_expenses = c.fetchall()
        for row in high_expenses:
            category, amount = row
            self.trigger_alert(
                "High Expense Alert",
                f"High expenses in {category}: ₹{amount:,.2f} in last 30 days. Review budget.",
                "warning"
            )
        
        conn.close()
    
    def check_worker_alerts(self):
        """Check for worker-related alerts"""
        conn = get_connection()
        c = conn.cursor()
        
        # Check for workers with upcoming salary payments
        c.execute('''
            SELECT name, salary, hire_date
            FROM workers
            WHERE status = 'Active'
        ''')
        
        workers = c.fetchall()
        for row in workers:
            name, salary, hire_date = row
            # Simple check: if worker has been employed for 30 days, salary is due
            days_employed = QDateTime.fromString(hire_date, 'yyyy-MM-dd').date().daysTo(QDateTime.currentDateTime().date())
            
            if days_employed % 30 == 0 and days_employed > 0:
                self.trigger_alert(
                    "Salary Payment Due",
                    f"Salary payment of ₹{salary:,.2f} is due for worker {name}.",
                    "info"
                )
        
        conn.close()
    
    def trigger_alert(self, title, message, alert_type):
        """Trigger an alert"""
        # Emit signal for main window
        self.alert_triggered.emit(title, message, alert_type)
        
        # Show notification
        if alert_type == "critical":
            notification_manager.show_error(title, message)
        elif alert_type == "warning":
            notification_manager.show_warning(title, message)
        else:
            notification_manager.show_info(title, message)
        
        # Show system tray notification
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon.isSystemTrayAvailable():
                icon_type = QSystemTrayIcon.MessageIcon.Critical if alert_type == "critical" else \
                           QSystemTrayIcon.MessageIcon.Warning if alert_type == "warning" else \
                           QSystemTrayIcon.MessageIcon.Information
                self.tray_icon.showMessage(title, message, icon_type, 5000)
        except Exception as e:
            print(f"System tray notification failed: {e}")
    
    def set_threshold(self, alert_type, value):
        """Set alert threshold"""
        if alert_type in self.thresholds:
            self.thresholds[alert_type] = value
    
    def get_thresholds(self):
        """Get current alert thresholds"""
        return self.thresholds.copy()
    
    def manual_check(self):
        """Manually trigger alert check"""
        self.check_alerts()

# Global alert manager instance
alert_manager = AlertManager() 