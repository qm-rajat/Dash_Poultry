from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import pyqtgraph as pg
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

CARD_ICONS = [
    'dashboard', 'feed', 'water', 'profit', 'loss'
]
CARD_ICON_MAP = {
    'dashboard': 'dashboard.svg',
    'feed': 'feed.svg',
    'water': 'water.svg',
    'profit': 'profit.svg',
    'loss': 'expenses.svg',
}

class DashboardWidget(QWidget):
    # Signal to notify main window to switch modules
    module_switch_requested = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Reuse existing layout if present to avoid adding multiple layouts to the same widget
        existing = self.layout()
        if existing is None:
            main_layout = QVBoxLayout(self)
        else:
            main_layout = existing
            # Clear any existing items/widgets from the layout
            while main_layout.count():
                item = main_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        # Dashboard title
        title = QLabel("<b style='font-size:28px;'>Dashboard Overview</b>")
        subtitle = QLabel("<span style='color:#888;font-size:15px;'>Farm performance at a glance</span>")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)
        
        # Summary cards
        card_layout = QHBoxLayout()
        card_layout.setSpacing(24)
        data = self.get_summary_data()
        cards = [
            ("Total Batches", str(data['batches']), 'dashboard', 1),  # Index 1 for Batches module
            ("Feed Used (kg)", str(data['feed']), 'feed', 2),         # Index 2 for Feed/Water module
            ("Water Used (L)", str(data['water']), 'water', 2),       # Index 2 for Feed/Water module
            ("Profit (₹)", f"₹{data['profit']:.2f}", 'profit', 7),    # Index 7 for Profit/Loss module
            ("Loss (₹)", f"₹{data['loss']:.2f}", 'loss', 6),          # Index 6 for Expenses module
        ]
        for title, value, icon, module_index in cards:
            card = self.create_card(title, value, icon, module_index)
            card_layout.addWidget(card)
        main_layout.addLayout(card_layout)
        main_layout.addSpacing(18)
        
        # Quick Actions
        actions_layout = QHBoxLayout()
        actions_title = QLabel("<b>Quick Actions</b>")
        actions_title.setStyleSheet("font-size: 16px; margin-bottom: 8px;")
        actions_layout.addWidget(actions_title)
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)
        
        quick_actions_layout = QHBoxLayout()
        quick_actions = [
            ("Add New Batch", 1),
            ("Log Feed/Water", 2),
            ("Record Vaccination", 3),
            ("Add Worker", 5),
            ("Record Expense", 6),
            ("View Reports", 8)
        ]
        
        for action_text, module_index in quick_actions:
            action_btn = QPushButton(action_text)
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #059669;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #047857;
                }
            """)
            action_btn.clicked.connect(lambda checked, idx=module_index: self.module_switch_requested.emit(idx))
            quick_actions_layout.addWidget(action_btn)
        
        quick_actions_layout.addStretch()
        main_layout.addLayout(quick_actions_layout)
        main_layout.addSpacing(18)
        
        # Chart area
        chart_grid = QGridLayout()
        chart_grid.setSpacing(24)
        chart_grid.addWidget(self.chart_card(self.create_feed_water_chart(), "Feed/Water Usage Over Time"), 0, 0)
        chart_grid.addWidget(self.chart_card(self.create_profit_loss_chart(), "Profit/Loss Trend (₹)"), 0, 1)
        chart_grid_widget = QWidget()
        chart_grid_widget.setLayout(chart_grid)
        main_layout.addWidget(chart_grid_widget)
        main_layout.addStretch()

    def create_card(self, title, value, icon, module_index):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
            QFrame:hover {
                border: 2px solid #059669;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0fdf4, stop:1 #ecfdf5);
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Icon and title
        header_layout = QHBoxLayout()
        icon_label = QLabel("📊")  # Using emoji as placeholder
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 14px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #059669; margin-top: 8px;")
        layout.addWidget(value_label)
        
        # Click indicator
        click_label = QLabel("Click to view details →")
        click_label.setStyleSheet("font-size: 11px; color: #6b7280; margin-top: 4px;")
        layout.addWidget(click_label)
        
        # Make card clickable
        card.mousePressEvent = lambda event, idx=module_index: self.module_switch_requested.emit(idx)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        return card

    def get_summary_data(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM batches')
        batches = c.fetchone()[0]
        c.execute('SELECT SUM(quantity_kg) FROM feed_logs')
        feed = c.fetchone()[0] or 0
        c.execute('SELECT SUM(quantity_l) FROM water_logs')
        water = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM revenue')
        revenue = c.fetchone()[0] or 0
        c.execute('SELECT SUM(amount) FROM expenses')
        expenses = c.fetchone()[0] or 0
        c.execute('SELECT SUM(count) FROM mortality')
        mortality = c.fetchone()[0] or 0
        loss = expenses + (mortality * 5)
        profit = revenue - loss
        conn.close()
        return {
            'batches': batches,
            'feed': feed,
            'water': water,
            'profit': profit,
            'loss': loss,
        }

    def chart_card(self, chart, title):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("QFrame { background-color: white; border: 1px solid #e5e7eb; border-radius: 8px; }")
        
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(title_label)
        layout.addWidget(chart)
        return card

    def create_feed_water_chart(self):
        plot = pg.PlotWidget(title="Feed/Water Usage Over Time")
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT date, SUM(quantity_kg) FROM feed_logs GROUP BY date ORDER BY date')
        feed_data = c.fetchall()
        feed_dates = [row[0] for row in feed_data]
        feed_vals = [row[1] for row in feed_data]
        c.execute('SELECT date, SUM(quantity_l) FROM water_logs GROUP BY date ORDER BY date')
        water_data = c.fetchall()
        water_dates = [row[0] for row in water_data]
        water_vals = [row[1] for row in water_data]
        conn.close()
        x_feed = list(range(len(feed_dates)))
        x_water = list(range(len(water_dates)))
        plot.plot(x_feed, feed_vals, pen=pg.mkPen('#3b82f6', width=2), name='Feed (kg)', symbol='o', symbolBrush='#3b82f6')
        plot.plot(x_water, water_vals, pen=pg.mkPen('#10b981', width=2), name='Water (L)', symbol='x', symbolBrush='#10b981')
        ticks = list(zip(x_feed, feed_dates))
        if len(ticks) > 10:
            step = 2 if len(ticks) < 20 else 3
            ticks = [tick for idx, tick in enumerate(ticks) if idx % step == 0]
        plot.getPlotItem().getAxis('bottom').setTicks([ticks])
        plot.getPlotItem().setLabels(left='Quantity', bottom='Date')
        plot.getPlotItem().addLegend()
        plot.setBackground('w')
        return plot

    def create_profit_loss_chart(self):
        plot = pg.PlotWidget(title="Profit/Loss Trend (₹)")
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT strftime("%Y-%m", date) as month, SUM(amount) FROM revenue GROUP BY month ORDER BY month')
        revenue_data = c.fetchall()
        c.execute('SELECT strftime("%Y-%m", date) as month, SUM(amount) FROM expenses GROUP BY month ORDER BY month')
        expenses_data = c.fetchall()
        conn.close()
        
        if revenue_data or expenses_data:
            # Create combined months set
            all_months = set()
            revenue_dict = {}
            expenses_dict = {}
            
            for month, amount in revenue_data:
                all_months.add(month)
                revenue_dict[month] = amount
            
            for month, amount in expenses_data:
                all_months.add(month)
                expenses_dict[month] = amount
            
            months = sorted(list(all_months))
            x = list(range(len(months)))
            revenue_vals = [revenue_dict.get(month, 0) for month in months]
            expenses_vals = [expenses_dict.get(month, 0) for month in months]
            profit_vals = [rev - exp for rev, exp in zip(revenue_vals, expenses_vals)]
            
            plot.plot(x, profit_vals, pen=pg.mkPen('#059669', width=3), name='Net Profit', symbol='o', symbolBrush='#059669')
            
            ticks = list(zip(x, months))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Profit (₹)', bottom='Month')
            plot.getPlotItem().addLegend()
        
        plot.setBackground('w')
        return plot 

    def refresh_data(self):
        """Refresh dashboard data"""
        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        # Reinitialize UI with fresh data
        self.init_ui() 