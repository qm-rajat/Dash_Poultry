from PyQt6.QtCore import QObject, pyqtSignal
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class DataManager(QObject):
    """Central data manager for cross-module communication"""
    
    # Signals for data updates
    batch_data_changed = pyqtSignal()
    feed_water_data_changed = pyqtSignal()
    vaccination_data_changed = pyqtSignal()
    mortality_data_changed = pyqtSignal()
    worker_data_changed = pyqtSignal()
    expense_data_changed = pyqtSignal()
    revenue_data_changed = pyqtSignal()
    
    # General data refresh signal
    data_refresh_needed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._cache = {}
    
    def get_batch_summary(self):
        """Get summary data for batches"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM batches')
        total_batches = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM batches WHERE date_in >= date("now", "-30 days")')
        recent_batches = c.fetchone()[0]
        conn.close()
        return {
            'total': total_batches,
            'recent': recent_batches
        }
    
    def get_financial_summary(self):
        """Get financial summary data"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM revenue')
        total_revenue = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM expenses')
        total_expenses = c.fetchone()[0] or 0
        c.execute('SELECT SUM(count) FROM mortality')
        total_mortality = c.fetchone()[0] or 0
        conn.close()
        
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'revenue': total_revenue,
            'expenses': total_expenses,
            'profit': net_profit,
            'margin': profit_margin,
            'mortality_cost': total_mortality * 5  # Estimated cost per bird
        }
    
    def get_worker_summary(self):
        """Get worker summary data"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM workers')
        total_workers = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM workers WHERE status = "Active"')
        active_workers = c.fetchone()[0]
        c.execute('SELECT SUM(salary) FROM workers WHERE status = "Active"')
        total_salary = c.fetchone()[0] or 0
        conn.close()
        
        return {
            'total': total_workers,
            'active': active_workers,
            'total_salary': total_salary
        }
    
    def get_health_summary(self):
        """Get health-related summary data"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM vaccinations WHERE status = "Scheduled"')
        scheduled_vaccinations = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM vaccinations WHERE status = "Completed"')
        completed_vaccinations = c.fetchone()[0]
        c.execute('SELECT SUM(count) FROM mortality')
        total_mortality = c.fetchone()[0] or 0
        conn.close()
        
        return {
            'scheduled_vaccinations': scheduled_vaccinations,
            'completed_vaccinations': completed_vaccinations,
            'total_mortality': total_mortality
        }
    
    def notify_batch_change(self):
        """Notify that batch data has changed"""
        self.batch_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_feed_water_change(self):
        """Notify that feed/water data has changed"""
        self.feed_water_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_vaccination_change(self):
        """Notify that vaccination data has changed"""
        self.vaccination_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_mortality_change(self):
        """Notify that mortality data has changed"""
        self.mortality_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_worker_change(self):
        """Notify that worker data has changed"""
        self.worker_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_expense_change(self):
        """Notify that expense data has changed"""
        self.expense_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def notify_revenue_change(self):
        """Notify that revenue data has changed"""
        self.revenue_data_changed.emit()
        self.data_refresh_needed.emit()
    
    def get_batch_list(self):
        """Get list of all batches for dropdowns"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT batch_id FROM batches ORDER BY batch_id')
        batches = [row[0] for row in c.fetchall()]
        conn.close()
        return batches
    
    def get_worker_list(self):
        """Get list of all workers for dropdowns"""
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT worker_id, name FROM workers WHERE status = "Active" ORDER BY name')
        workers = [(row[0], row[1]) for row in c.fetchall()]
        conn.close()
        return workers
    
    def get_expense_categories(self):
        """Get list of expense categories"""
        return ["Feed", "Medicine", "Electricity", "Water", "Fuel", "Equipment", "Labor", "Transport", "Maintenance", "Other"]
    
    def get_vaccine_types(self):
        """Get list of common vaccine types"""
        return ["Newcastle Disease", "Marek Disease", "Infectious Bronchitis", "Gumboro Disease", "Fowl Pox", "Avian Influenza", "Other"]
    
    def get_worker_roles(self):
        """Get list of worker roles"""
        return ["Farm Manager", "Feeder", "Cleaner", "Vaccinator", "Driver", "Maintenance", "Other"]
    
    def get_payment_methods(self):
        """Get list of payment methods"""
        return ["Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card", "Other"]

# Global data manager instance
data_manager = DataManager() 