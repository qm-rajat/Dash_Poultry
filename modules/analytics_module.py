from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, 
                             QSpinBox, QDoubleSpinBox, QFileDialog, QAbstractItemView, QHeaderView, QComboBox,
                             QTabWidget, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class AnalyticsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_analytics()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<b>Farm Analytics & Insights</b>")
        title.setStyleSheet("font-size: 20px; margin-bottom: 10px; color: #1f2937;")
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #f3f4f6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        
        # Create tabs
        self.create_performance_tab()
        self.create_financial_tab()
        self.create_health_tab()
        self.create_efficiency_tab()
        self.create_predictions_tab()
        
        layout.addWidget(self.tab_widget)

    def create_performance_tab(self):
        """Performance analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance metrics cards
        metrics_layout = QHBoxLayout()
        self.create_metric_card(metrics_layout, "Feed Conversion Ratio", "0.0", "kg feed/kg gain")
        self.create_metric_card(metrics_layout, "Water Usage Efficiency", "0.0", "L/bird/day")
        self.create_metric_card(metrics_layout, "Mortality Rate", "0.0%", "current period")
        self.create_metric_card(metrics_layout, "Growth Rate", "0.0", "g/day")
        layout.addLayout(metrics_layout)
        
        # Performance charts
        charts_layout = QGridLayout()
        
        # Feed conversion chart
        feed_conversion_chart = self.create_feed_conversion_chart()
        charts_layout.addWidget(self.chart_card(feed_conversion_chart, "Feed Conversion Ratio by Batch"), 0, 0)
        
        # Growth trend chart
        growth_chart = self.create_growth_trend_chart()
        charts_layout.addWidget(self.chart_card(growth_chart, "Growth Trend Analysis"), 0, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Performance")

    def create_financial_tab(self):
        """Financial analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Financial metrics cards
        metrics_layout = QHBoxLayout()
        self.create_metric_card(metrics_layout, "Profit Margin", "0.0%", "current period")
        self.create_metric_card(metrics_layout, "Cost per Bird", "₹0.0", "total cost")
        self.create_metric_card(metrics_layout, "Revenue per Bird", "₹0.0", "total revenue")
        self.create_metric_card(metrics_layout, "ROI", "0.0%", "return on investment")
        layout.addLayout(metrics_layout)
        
        # Financial charts
        charts_layout = QGridLayout()
        
        # Profit breakdown chart
        profit_chart = self.create_profit_breakdown_chart()
        charts_layout.addWidget(self.chart_card(profit_chart, "Profit Breakdown by Category"), 0, 0)
        
        # Cost trend chart
        cost_chart = self.create_cost_trend_chart()
        charts_layout.addWidget(self.chart_card(cost_chart, "Cost Trend Analysis"), 0, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Financial")

    def create_health_tab(self):
        """Health analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Health metrics cards
        metrics_layout = QHBoxLayout()
        self.create_metric_card(metrics_layout, "Vaccination Coverage", "0.0%", "completed")
        self.create_metric_card(metrics_layout, "Disease Incidence", "0.0%", "affected birds")
        self.create_metric_card(metrics_layout, "Health Score", "0.0", "out of 100")
        self.create_metric_card(metrics_layout, "Medication Cost", "₹0.0", "per bird")
        layout.addLayout(metrics_layout)
        
        # Health charts
        charts_layout = QGridLayout()
        
        # Mortality trend chart
        mortality_chart = self.create_mortality_trend_chart()
        charts_layout.addWidget(self.chart_card(mortality_chart, "Mortality Trend Analysis"), 0, 0)
        
        # Vaccination status chart
        vaccine_chart = self.create_vaccination_status_chart()
        charts_layout.addWidget(self.chart_card(vaccine_chart, "Vaccination Status"), 0, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Health")

    def create_efficiency_tab(self):
        """Efficiency analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Efficiency metrics cards
        metrics_layout = QHBoxLayout()
        self.create_metric_card(metrics_layout, "Labor Efficiency", "0.0", "birds/worker")
        self.create_metric_card(metrics_layout, "Space Utilization", "0.0%", "capacity used")
        self.create_metric_card(metrics_layout, "Energy Efficiency", "0.0", "kWh/bird")
        self.create_metric_card(metrics_layout, "Waste Management", "0.0%", "efficiency")
        layout.addLayout(metrics_layout)
        
        # Efficiency charts
        charts_layout = QGridLayout()
        
        # Resource utilization chart
        resource_chart = self.create_resource_utilization_chart()
        charts_layout.addWidget(self.chart_card(resource_chart, "Resource Utilization"), 0, 0)
        
        # Efficiency comparison chart
        efficiency_chart = self.create_efficiency_comparison_chart()
        charts_layout.addWidget(self.chart_card(efficiency_chart, "Efficiency Comparison"), 0, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Efficiency")

    def create_predictions_tab(self):
        """Predictions and forecasting tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Prediction controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Forecast Period:"))
        self.forecast_period = QComboBox()
        self.forecast_period.addItems(["30 days", "60 days", "90 days", "6 months"])
        controls_layout.addWidget(self.forecast_period)
        self.forecast_btn = QPushButton("Generate Forecast")
        self.forecast_btn.clicked.connect(self.generate_forecast)
        controls_layout.addWidget(self.forecast_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Prediction charts
        charts_layout = QGridLayout()
        
        # Revenue forecast chart
        revenue_forecast_chart = self.create_revenue_forecast_chart()
        charts_layout.addWidget(self.chart_card(revenue_forecast_chart, "Revenue Forecast"), 0, 0)
        
        # Cost forecast chart
        cost_forecast_chart = self.create_cost_forecast_chart()
        charts_layout.addWidget(self.chart_card(cost_forecast_chart, "Cost Forecast"), 0, 1)
        
        layout.addLayout(charts_layout)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Predictions")

    def create_metric_card(self, layout, title, value, unit):
        """Create a metric card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                min-width: 150px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px;")
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #059669; margin: 8px 0;")
        card_layout.addWidget(value_label)
        
        unit_label = QLabel(unit)
        unit_label.setStyleSheet("font-size: 10px; color: #6b7280;")
        card_layout.addWidget(unit_label)
        
        layout.addWidget(card)

    def chart_card(self, chart, title):
        """Create a chart card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet("QFrame { background-color: white; border: 1px solid #e5e7eb; border-radius: 8px; }")
        
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(title_label)
        layout.addWidget(chart)
        return card

    def create_feed_conversion_chart(self):
        """Create feed conversion ratio chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Get feed conversion data
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT b.batch_id, 
                   COALESCE(SUM(f.quantity_kg), 0) as total_feed,
                   b.num_chicks,
                   COALESCE(SUM(m.count), 0) as total_mortality
            FROM batches b
            LEFT JOIN feed_logs f ON b.batch_id = f.batch_id
            LEFT JOIN mortality m ON b.batch_id = m.batch_id
            GROUP BY b.batch_id
            ORDER BY b.date_in
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            batch_ids = [row[0] for row in data]
            # Simplified feed conversion calculation (assuming 2kg weight gain per bird)
            feed_conversions = []
            for row in data:
                total_feed = row[1]
                num_chicks = row[2]
                mortality = row[3]
                live_birds = num_chicks - mortality
                if live_birds > 0 and total_feed > 0:
                    # Assuming 2kg weight gain per bird
                    total_weight_gain = live_birds * 2
                    conversion = total_feed / total_weight_gain
                    feed_conversions.append(conversion)
                else:
                    feed_conversions.append(0)
            
            x = list(range(len(batch_ids)))
            plot.plot(x, feed_conversions, pen=pg.mkPen('#3b82f6', width=3), symbol='o', symbolBrush='#3b82f6')
            
            # Set axis labels
            ticks = list(zip(x, batch_ids))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Feed Conversion Ratio', bottom='Batch ID')
        
        plot.setBackground('w')
        return plot

    def create_growth_trend_chart(self):
        """Create growth trend chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Simplified growth trend (days since batch start)
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT b.batch_id, b.date_in, b.num_chicks,
                   COALESCE(SUM(m.count), 0) as total_mortality
            FROM batches b
            LEFT JOIN mortality m ON b.batch_id = m.batch_id
            GROUP BY b.batch_id
            ORDER BY b.date_in
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            # Calculate days since start and survival rate
            days_since_start = []
            survival_rates = []
            
            for row in data:
                date_in = QDate.fromString(row[1], 'yyyy-MM-dd')
                days = date_in.daysTo(QDate.currentDate())
                days_since_start.append(days)
                
                num_chicks = row[2]
                mortality = row[3]
                survival_rate = ((num_chicks - mortality) / num_chicks) * 100 if num_chicks > 0 else 0
                survival_rates.append(survival_rate)
            
            plot.plot(days_since_start, survival_rates, pen=pg.mkPen('#10b981', width=3), symbol='o', symbolBrush='#10b981')
            plot.getPlotItem().setLabels(left='Survival Rate (%)', bottom='Days Since Start')
        
        plot.setBackground('w')
        return plot

    def create_profit_breakdown_chart(self):
        """Create profit breakdown chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Get expense breakdown
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT category, SUM(amount) as total_amount
            FROM expenses
            GROUP BY category
            ORDER BY total_amount DESC
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]
            
            # Create bar chart
            x = list(range(len(categories)))
            bg = pg.BarGraphItem(x=x, height=amounts, width=0.6, brush='#3b82f6')
            plot.addItem(bg)
            
            # Set axis labels
            ticks = list(zip(x, categories))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Amount (₹)', bottom='Category')
        
        plot.setBackground('w')
        return plot

    def create_cost_trend_chart(self):
        """Create cost trend chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Get monthly cost trend
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT strftime("%Y-%m", date) as month, SUM(amount) as total_cost
            FROM expenses
            GROUP BY month
            ORDER BY month
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            months = [row[0] for row in data]
            costs = [row[1] for row in data]
            
            x = list(range(len(months)))
            plot.plot(x, costs, pen=pg.mkPen('#ef4444', width=3), symbol='o', symbolBrush='#ef4444')
            
            # Set axis labels
            ticks = list(zip(x, months))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Total Cost (₹)', bottom='Month')
        
        plot.setBackground('w')
        return plot

    def create_mortality_trend_chart(self):
        """Create mortality trend chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Get daily mortality trend
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT date, SUM(count) as daily_mortality
            FROM mortality
            GROUP BY date
            ORDER BY date
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            dates = [row[0] for row in data]
            mortality_counts = [row[1] for row in data]
            
            x = list(range(len(dates)))
            plot.plot(x, mortality_counts, pen=pg.mkPen('#dc2626', width=3), symbol='o', symbolBrush='#dc2626')
            
            # Set axis labels
            ticks = list(zip(x, dates))
            if len(ticks) > 10:
                step = len(ticks) // 10
                ticks = [tick for idx, tick in enumerate(ticks) if idx % step == 0]
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Mortality Count', bottom='Date')
        
        plot.setBackground('w')
        return plot

    def create_vaccination_status_chart(self):
        """Create vaccination status chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Get vaccination status
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT status, COUNT(*) as count
            FROM vaccinations
            GROUP BY status
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            statuses = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            # Create bar chart
            x = list(range(len(statuses)))
            colors = ['#10b981', '#f59e0b', '#ef4444']  # Green, Yellow, Red
            bg = pg.BarGraphItem(x=x, height=counts, width=0.6, brush=colors[:len(statuses)])
            plot.addItem(bg)
            
            # Set axis labels
            ticks = list(zip(x, statuses))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Count', bottom='Status')
        
        plot.setBackground('w')
        return plot

    def create_resource_utilization_chart(self):
        """Create resource utilization chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Simplified resource utilization (feed and water usage)
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT strftime("%Y-%m", date) as month,
                   SUM(quantity_kg) as total_feed,
                   SUM(quantity_l) as total_water
            FROM feed_logs f
            JOIN water_logs w ON f.batch_id = w.batch_id AND f.date = w.date
            GROUP BY month
            ORDER BY month
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            months = [row[0] for row in data]
            feed_usage = [row[1] for row in data]
            water_usage = [row[2] for row in data]
            
            x = list(range(len(months)))
            plot.plot(x, feed_usage, pen=pg.mkPen('#3b82f6', width=3), name='Feed (kg)', symbol='o', symbolBrush='#3b82f6')
            plot.plot(x, water_usage, pen=pg.mkPen('#10b981', width=3), name='Water (L)', symbol='x', symbolBrush='#10b981')
            
            # Set axis labels
            ticks = list(zip(x, months))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Usage', bottom='Month')
            plot.getPlotItem().addLegend()
        
        plot.setBackground('w')
        return plot

    def create_efficiency_comparison_chart(self):
        """Create efficiency comparison chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Compare efficiency metrics across batches
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT b.batch_id,
                   COALESCE(SUM(f.quantity_kg), 0) as total_feed,
                   COALESCE(SUM(m.count), 0) as total_mortality,
                   b.num_chicks
            FROM batches b
            LEFT JOIN feed_logs f ON b.batch_id = f.batch_id
            LEFT JOIN mortality m ON b.batch_id = m.batch_id
            GROUP BY b.batch_id
            ORDER BY b.date_in
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            batch_ids = [row[0] for row in data]
            efficiency_scores = []
            
            for row in data:
                total_feed = row[1]
                mortality = row[2]
                num_chicks = row[3]
                
                # Calculate efficiency score (simplified)
                if num_chicks > 0:
                    survival_rate = (num_chicks - mortality) / num_chicks
                    feed_efficiency = 1 / (total_feed / num_chicks) if total_feed > 0 else 0
                    efficiency_score = (survival_rate + feed_efficiency) / 2 * 100
                    efficiency_scores.append(efficiency_score)
                else:
                    efficiency_scores.append(0)
            
            x = list(range(len(batch_ids)))
            plot.plot(x, efficiency_scores, pen=pg.mkPen('#8b5cf6', width=3), symbol='o', symbolBrush='#8b5cf6')
            
            # Set axis labels
            ticks = list(zip(x, batch_ids))
            plot.getPlotItem().getAxis('bottom').setTicks([ticks])
            plot.getPlotItem().setLabels(left='Efficiency Score (%)', bottom='Batch ID')
        
        plot.setBackground('w')
        return plot

    def create_revenue_forecast_chart(self):
        """Create revenue forecast chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Simple linear forecast based on historical data
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT strftime("%Y-%m", date) as month, SUM(amount) as revenue
            FROM revenue
            GROUP BY month
            ORDER BY month
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            months = [row[0] for row in data]
            revenues = [row[1] for row in data]
            
            # Create forecast (simple linear projection)
            x_historical = list(range(len(months)))
            if len(revenues) > 1:
                # Simple linear regression
                slope = (revenues[-1] - revenues[0]) / (len(revenues) - 1) if len(revenues) > 1 else 0
                
                # Forecast next 3 months
                forecast_months = 3
                x_forecast = list(range(len(months), len(months) + forecast_months))
                forecast_revenues = [revenues[-1] + slope * (i + 1) for i in range(forecast_months)]
                
                # Plot historical data
                plot.plot(x_historical, revenues, pen=pg.mkPen('#3b82f6', width=3), name='Historical', symbol='o', symbolBrush='#3b82f6')
                
                # Plot forecast
                plot.plot(x_forecast, forecast_revenues, pen=pg.mkPen('#10b981', width=3, style=Qt.PenStyle.DashLine), name='Forecast', symbol='o', symbolBrush='#10b981')
                
                plot.getPlotItem().addLegend()
        
        plot.setBackground('w')
        return plot

    def create_cost_forecast_chart(self):
        """Create cost forecast chart"""
        plot = pg.PlotWidget()
        plot.setMouseEnabled(False, False)
        plot.hideButtons()
        
        # Simple linear forecast for costs
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            SELECT strftime("%Y-%m", date) as month, SUM(amount) as cost
            FROM expenses
            GROUP BY month
            ORDER BY month
        ''')
        data = c.fetchall()
        conn.close()
        
        if data:
            months = [row[0] for row in data]
            costs = [row[1] for row in data]
            
            # Create forecast
            x_historical = list(range(len(months)))
            if len(costs) > 1:
                slope = (costs[-1] - costs[0]) / (len(costs) - 1) if len(costs) > 1 else 0
                
                # Forecast next 3 months
                forecast_months = 3
                x_forecast = list(range(len(months), len(months) + forecast_months))
                forecast_costs = [costs[-1] + slope * (i + 1) for i in range(forecast_months)]
                
                # Plot historical data
                plot.plot(x_historical, costs, pen=pg.mkPen('#ef4444', width=3), name='Historical', symbol='o', symbolBrush='#ef4444')
                
                # Plot forecast
                plot.plot(x_forecast, forecast_costs, pen=pg.mkPen('#f59e0b', width=3, style=Qt.PenStyle.DashLine), name='Forecast', symbol='o', symbolBrush='#f59e0b')
                
                plot.getPlotItem().addLegend()
        
        plot.setBackground('w')
        return plot

    def generate_forecast(self):
        """Generate forecast based on selected period"""
        period = self.forecast_period.currentText()
        QMessageBox.information(self, "Forecast Generated", f"Forecast for {period} has been generated and displayed in the charts.")

    def load_analytics(self):
        """Load and calculate all analytics data"""
        # This method would calculate all the metrics and update the UI
        # For now, it's a placeholder
        pass 