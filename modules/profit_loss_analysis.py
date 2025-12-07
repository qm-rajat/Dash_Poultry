from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QComboBox, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QDate
import pyqtgraph as pg
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.data_manager import data_manager

class ProfitLossAnalysisWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # Connect to data manager signals so charts/labels update live
        try:
            data_manager.revenue_data_changed.connect(self.on_financial_data_changed)
            data_manager.expense_data_changed.connect(self.on_financial_data_changed)
            data_manager.revenue_data_changed.connect(self.load_data)
            data_manager.expense_data_changed.connect(self.load_data)
        except Exception:
            pass
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<b>Profit/Loss Analysis</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        self.total_revenue_label = QLabel("Total Revenue: ₹0")
        self.total_revenue_label.setStyleSheet("font-weight: bold; color: #059669; font-size: 14px; padding: 10px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 5px;")
        summary_layout.addWidget(self.total_revenue_label)
        
        self.total_expenses_label = QLabel("Total Expenses: ₹0")
        self.total_expenses_label.setStyleSheet("font-weight: bold; color: #dc2626; font-size: 14px; padding: 10px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 5px;")
        summary_layout.addWidget(self.total_expenses_label)
        
        self.net_profit_label = QLabel("Net Profit: ₹0")
        self.net_profit_label.setStyleSheet("font-weight: bold; color: #059669; font-size: 14px; padding: 10px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 5px;")
        summary_layout.addWidget(self.net_profit_label)
        
        self.profit_margin_label = QLabel("Profit Margin: 0%")
        self.profit_margin_label.setStyleSheet("font-weight: bold; color: #059669; font-size: 14px; padding: 10px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 5px;")
        summary_layout.addWidget(self.profit_margin_label)
        
        summary_layout.addStretch()
        layout.addLayout(summary_layout)
        
        # Charts area
        charts_layout = QGridLayout()
        
        # Revenue vs Expenses chart
        self.revenue_expenses_chart = self.create_revenue_expenses_chart()
        self.revenue_card = self.chart_card(self.revenue_expenses_chart, "Revenue vs Expenses")
        charts_layout.addWidget(self.revenue_card, 0, 0)
        
        # Monthly profit trend
        self.monthly_profit_chart = self.create_monthly_profit_chart()
        self.monthly_card = self.chart_card(self.monthly_profit_chart, "Monthly Profit Trend")
        charts_layout.addWidget(self.monthly_card, 0, 1)
        
        # Expense breakdown pie chart
        self.expense_breakdown_chart = self.create_expense_breakdown_chart()
        self.expense_card = self.chart_card(self.expense_breakdown_chart, "Expense Breakdown")
        charts_layout.addWidget(self.expense_card, 1, 0)
        
        # Revenue by batch
        self.revenue_by_batch_chart = self.create_revenue_by_batch_chart()
        self.revenue_by_batch_card = self.chart_card(self.revenue_by_batch_chart, "Revenue by Batch")
        charts_layout.addWidget(self.revenue_by_batch_card, 1, 1)
        
        charts_widget = QWidget()
        charts_widget.setLayout(charts_layout)
        layout.addWidget(charts_widget)
        
        # Detailed breakdown table
        breakdown_label = QLabel("<b>Detailed Financial Breakdown</b>")
        breakdown_label.setStyleSheet("font-size: 16px; margin: 10px 0;")
        layout.addWidget(breakdown_label)
        
        self.breakdown_table = QTableWidget()
        self.breakdown_table.setColumnCount(4)
        self.breakdown_table.setHorizontalHeaderLabels(["Category", "Revenue (₹)", "Expenses (₹)", "Profit (₹)"])
        self.breakdown_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.breakdown_table.verticalHeader().setVisible(False)
        self.breakdown_table.setAlternatingRowColors(True)
        layout.addWidget(self.breakdown_table)

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

    def load_data(self):
        conn = get_connection()
        c = conn.cursor()
        
        # Get revenue data
        c.execute('SELECT SUM(amount) FROM revenue')
        total_revenue = c.fetchone()[0] or 0
        
        # Get expenses data
        c.execute('SELECT SUM(amount) FROM expenses')
        total_expenses = c.fetchone()[0] or 0
        
        # Calculate net profit and margin
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Update summary labels
        self.total_revenue_label.setText(f"Total Revenue: ₹{total_revenue:,.2f}")
        self.total_expenses_label.setText(f"Total Expenses: ₹{total_expenses:,.2f}")
        self.net_profit_label.setText(f"Net Profit: ₹{net_profit:,.2f}")
        self.profit_margin_label.setText(f"Profit Margin: {profit_margin:.1f}%")
        
        # Load breakdown data
        self.load_breakdown_data()
        
        conn.close()

    def on_financial_data_changed(self):
        """Refresh charts when revenue/expense data changes."""
        try:
            # Recreate and replace each chart widget inside its card
            new_rev_exp = self.create_revenue_expenses_chart()
            rev_layout = self.revenue_card.layout()
            # replace old chart (assumed at index 1)
            old_widget = rev_layout.itemAt(1).widget()
            if old_widget:
                old_widget.deleteLater()
            rev_layout.insertWidget(1, new_rev_exp)
            self.revenue_expenses_chart = new_rev_exp

            new_monthly = self.create_monthly_profit_chart()
            mon_layout = self.monthly_card.layout()
            old_widget = mon_layout.itemAt(1).widget()
            if old_widget:
                old_widget.deleteLater()
            mon_layout.insertWidget(1, new_monthly)
            self.monthly_profit_chart = new_monthly

            new_expense = self.create_expense_breakdown_chart()
            exp_layout = self.expense_card.layout()
            old_widget = exp_layout.itemAt(1).widget()
            if old_widget:
                old_widget.deleteLater()
            exp_layout.insertWidget(1, new_expense)
            self.expense_breakdown_chart = new_expense

            new_rev_by_batch = self.create_revenue_by_batch_chart()
            rb_layout = self.revenue_by_batch_card.layout()
            old_widget = rb_layout.itemAt(1).widget()
            if old_widget:
                old_widget.deleteLater()
            rb_layout.insertWidget(1, new_rev_by_batch)
            self.revenue_by_batch_chart = new_rev_by_batch

            # Update breakdown table/labels as well
            self.load_data()
        except Exception:
            # Non-fatal: ignore errors during UI refresh
            pass

    def load_breakdown_data(self):
        conn = get_connection()
        c = conn.cursor()
        
        # Get revenue by batch
        c.execute('SELECT batch_id, SUM(amount) FROM revenue GROUP BY batch_id')
        revenue_by_batch = dict(c.fetchall())
        
        # Get expenses by category
        c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        expenses_by_category = dict(c.fetchall())
        
        # Create breakdown table
        categories = list(set(list(revenue_by_batch.keys()) + list(expenses_by_category.keys())))
        categories.sort()
        
        self.breakdown_table.setRowCount(len(categories))
        for i, category in enumerate(categories):
            revenue = revenue_by_batch.get(category, 0)
            expenses = expenses_by_category.get(category, 0)
            profit = revenue - expenses
            
            self.breakdown_table.setItem(i, 0, QTableWidgetItem(category))
            self.breakdown_table.setItem(i, 1, QTableWidgetItem(f"₹{revenue:,.2f}"))
            self.breakdown_table.setItem(i, 2, QTableWidgetItem(f"₹{expenses:,.2f}"))
            
            profit_item = QTableWidgetItem(f"₹{profit:,.2f}")
            if profit > 0:
                profit_item.setBackground(Qt.GlobalColor.green)
            elif profit < 0:
                profit_item.setBackground(Qt.GlobalColor.red)
            self.breakdown_table.setItem(i, 3, profit_item)
        
        conn.close()

    def create_revenue_expenses_chart(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        conn = get_connection()
        c = conn.cursor()
        
        # Get monthly data
        c.execute('SELECT strftime("%Y-%m", date) as month, SUM(amount) FROM revenue GROUP BY month ORDER BY month')
        revenue_data = c.fetchall()
        
        c.execute('SELECT strftime("%Y-%m", date) as month, SUM(amount) FROM expenses GROUP BY month ORDER BY month')
        expenses_data = c.fetchall()
        
        conn.close()
        
        if revenue_data or expenses_data:
            # Create a combined set of all months
            all_months = set()
            revenue_dict = {}
            expenses_dict = {}
            
            for month, amount in revenue_data:
                all_months.add(month)
                revenue_dict[month] = amount
            
            for month, amount in expenses_data:
                all_months.add(month)
                expenses_dict[month] = amount
            
            # Sort months
            months = sorted(list(all_months))
            x = list(range(len(months)))
            
            # Get values for each month, defaulting to 0 if no data
            revenue_vals = [revenue_dict.get(month, 0) for month in months]
            expenses_vals = [expenses_dict.get(month, 0) for month in months]
            
            # Only plot if we have data
            if any(revenue_vals):
                plot.plot(x, revenue_vals, pen=pg.mkPen('#059669', width=3), name='Revenue', symbol='o', symbolBrush='#059669')
            if any(expenses_vals):
                plot.plot(x, expenses_vals, pen=pg.mkPen('#dc2626', width=3), name='Expenses', symbol='s', symbolBrush='#dc2626')
            
            if months:
                ticks = list(zip(x, months))
                plot.getPlotItem().getAxis('bottom').setTicks([ticks])
                plot.getPlotItem().setLabels(left='Amount (₹)', bottom='Month')
                plot.getPlotItem().addLegend()
        
        plot.setBackground('w')
        return plot

    def create_monthly_profit_chart(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        conn = get_connection()
        c = conn.cursor()
        
        # Get all months from both revenue and expenses
        c.execute('''
            SELECT DISTINCT month FROM (
                SELECT strftime("%Y-%m", date) as month FROM revenue
                UNION
                SELECT strftime("%Y-%m", date) as month FROM expenses
            ) ORDER BY month
        ''')
        all_months = [row[0] for row in c.fetchall()]
        
        if all_months:
            profits = []
            for month in all_months:
                # Get revenue for this month
                c.execute('SELECT SUM(amount) FROM revenue WHERE strftime("%Y-%m", date) = ?', (month,))
                revenue = c.fetchone()[0] or 0
                
                # Get expenses for this month
                c.execute('SELECT SUM(amount) FROM expenses WHERE strftime("%Y-%m", date) = ?', (month,))
                expenses = c.fetchone()[0] or 0
                
                profit = revenue - expenses
                profits.append(profit)
            
            x = list(range(len(all_months)))
            # Use single color for all bars or create proper color array
            if all(p >= 0 for p in profits):
                bars = pg.BarGraphItem(x0=x, height=profits, brush='g', width=0.8)
            elif all(p < 0 for p in profits):
                bars = pg.BarGraphItem(x0=x, height=profits, brush='r', width=0.8)
            else:
                # Mixed positive and negative - use green for positive, red for negative
                positive_bars = [(i, p) for i, p in enumerate(profits) if p >= 0]
                negative_bars = [(i, p) for i, p in enumerate(profits) if p < 0]
                
                if positive_bars:
                    pos_x = [x[i] for i, _ in positive_bars]
                    pos_heights = [p for _, p in positive_bars]
                    pos_bars = pg.BarGraphItem(x0=pos_x, height=pos_heights, brush='g', width=0.8)
                    plot.addItem(pos_bars)
                
                if negative_bars:
                    neg_x = [x[i] for i, _ in negative_bars]
                    neg_heights = [p for _, p in negative_bars]
                    neg_bars = pg.BarGraphItem(x0=neg_x, height=neg_heights, brush='r', width=0.8)
                    plot.addItem(neg_bars)
                
                # Skip the single bars addition since we added them separately
                if positive_bars or negative_bars:
                    ticks = list(zip(x, all_months))
                    plot.getPlotItem().getAxis('bottom').setTicks([ticks])
                    plot.getPlotItem().setLabels(left='Profit (₹)', bottom='Month')
                    conn.close()
                    plot.setBackground('w')
                    return plot
            
            plot.addItem(bars)
            
            ticks = list(zip(x, all_months))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Profit (₹)', bottom='Month')
        
        conn.close()
        plot.setBackground('w')
        return plot

    def create_expense_breakdown_chart(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC')
        expense_data = c.fetchall()
        conn.close()
        
        if expense_data:
            categories = [row[0] for row in expense_data]
            amounts = [row[1] for row in expense_data]
            
            # Create pie chart using bar chart (PyQtGraph doesn't have built-in pie charts)
            x = list(range(len(categories)))
            # Use a single color for all bars to avoid color array issues
            bars = pg.BarGraphItem(x0=x, height=amounts, brush='b', width=0.8)
            plot.addItem(bars)
            
            ticks = list(zip(x, categories))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Amount (₹)', bottom='Category')
        
        plot.setBackground('w')
        return plot

    def create_revenue_by_batch_chart(self):
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT batch_id, SUM(amount) FROM revenue GROUP BY batch_id ORDER BY SUM(amount) DESC')
        revenue_data = c.fetchall()
        conn.close()
        
        if revenue_data:
            batches = [row[0] for row in revenue_data]
            amounts = [row[1] for row in revenue_data]
            
            x = list(range(len(batches)))
            bars = pg.BarGraphItem(x0=x, height=amounts, brush='#059669', width=0.8)
            plot.addItem(bars)
            
            ticks = list(zip(x, batches))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Revenue (₹)', bottom='Batch ID')
        
        plot.setBackground('w')
        return plot 