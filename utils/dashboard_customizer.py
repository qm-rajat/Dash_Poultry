from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QDragEnterEvent, QDropEvent, QScrollArea, QGridLayout, QDialog,
                             QListWidget, QListWidgetItem, QDialogButtonBox, QCheckBox, QSpinBox,
                             QComboBox, QFormLayout, QGroupBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class DraggableWidget(QFrame):
    """Base class for draggable dashboard widgets"""
    
    def __init__(self, widget_type, title, parent=None):
        super().__init__(parent)
        self.widget_type = widget_type
        self.title = title
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #3b82f6;
            }
        """)
        
        self.setAcceptDrops(True)
        self.setMinimumSize(200, 150)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
            self.is_dragging = True
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not self.is_dragging:
            return
        
        if ((event.pos() - self.drag_start_pos).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.widget_type)
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()
        drag.setPixmap(pixmap)
        
        self.is_dragging = False
        drag.exec(Qt.DropAction.MoveAction)
    
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        super().mouseReleaseEvent(event)

class MetricWidget(DraggableWidget):
    """Metric card widget"""
    
    def __init__(self, title, value, unit, color="#059669", parent=None):
        super().__init__("metric", title, parent)
        self.value = value
        self.unit = unit
        self.color = color
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 12px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(str(self.value))
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.color}; margin: 8px 0;")
        layout.addWidget(value_label)
        
        unit_label = QLabel(self.unit)
        unit_label.setStyleSheet("font-size: 10px; color: #6b7280;")
        layout.addWidget(unit_label)
        
        layout.addStretch()

class ChartWidget(DraggableWidget):
    """Chart widget placeholder"""
    
    def __init__(self, title, chart_type, parent=None):
        super().__init__("chart", title, parent)
        self.chart_type = chart_type
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Placeholder for chart
        chart_placeholder = QLabel(f"[{self.chart_type} Chart]")
        chart_placeholder.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                border: 2px dashed #d1d5db;
                border-radius: 4px;
                padding: 40px;
                color: #6b7280;
                font-style: italic;
            }
        """)
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(chart_placeholder)

class DropZone(QFrame):
    """Drop zone for dashboard widgets"""
    
    widget_dropped = pyqtSignal(str, QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 2px dashed #d1d5db;
                border-radius: 8px;
                min-height: 200px;
            }
            QFrame:hover {
                border: 2px dashed #3b82f6;
                background-color: #eff6ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        placeholder = QLabel("Drop widgets here to customize your dashboard")
        placeholder.setStyleSheet("color: #6b7280; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        widget_type = event.mimeData().text()
        drop_pos = event.pos()
        self.widget_dropped.emit(widget_type, drop_pos)
        event.acceptProposedAction()

class WidgetPalette(QWidget):
    """Widget palette for available widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Available Widgets")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Metric widgets
        metrics_group = QGroupBox("Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        metric_widgets = [
            ("Total Batches", "0", "batches"),
            ("Feed Used", "0 kg", "feed"),
            ("Water Used", "0 L", "water"),
            ("Profit", "₹0", "profit"),
            ("Active Workers", "0", "workers"),
            ("Mortality Rate", "0%", "mortality")
        ]
        
        for title, value, unit in metric_widgets:
            widget = MetricWidget(title, value, unit)
            metrics_layout.addWidget(widget)
        
        layout.addWidget(metrics_group)
        
        # Chart widgets
        charts_group = QGroupBox("Charts")
        charts_layout = QVBoxLayout(charts_group)
        
        chart_widgets = [
            ("Feed/Water Usage", "line"),
            ("Profit/Loss Trend", "line"),
            ("Batch Distribution", "bar"),
            ("Expense Breakdown", "pie"),
            ("Mortality Trend", "line"),
            ("Worker Performance", "bar")
        ]
        
        for title, chart_type in chart_widgets:
            widget = ChartWidget(title, chart_type)
            charts_layout.addWidget(widget)
        
        layout.addWidget(charts_group)
        layout.addStretch()

class DashboardCustomizer(QWidget):
    """Main dashboard customizer widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = []
        self.init_ui()
        self.load_layout()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel - Widget palette
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        palette = WidgetPalette()
        left_layout.addWidget(palette)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Layout")
        self.save_btn.clicked.connect(self.save_layout)
        controls_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_layout)
        controls_layout.addWidget(self.reset_btn)
        
        left_layout.addLayout(controls_layout)
        layout.addWidget(left_panel)
        
        # Right panel - Dashboard area
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        title = QLabel("Customize Dashboard")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        right_layout.addWidget(title)
        
        # Dashboard drop zone
        self.drop_zone = DropZone()
        self.drop_zone.widget_dropped.connect(self.add_widget)
        right_layout.addWidget(self.drop_zone)
        
        layout.addWidget(right_panel)
    
    def add_widget(self, widget_type, position):
        """Add a widget to the dashboard"""
        if widget_type == "metric":
            # Create metric widget with sample data
            widget = MetricWidget("Sample Metric", "0", "units")
        elif widget_type == "chart":
            # Create chart widget
            widget = ChartWidget("Sample Chart", "line")
        else:
            return
        
        # Position the widget
        widget.move(position)
        widget.setParent(self.drop_zone)
        widget.show()
        
        self.widgets.append(widget)
    
    def save_layout(self):
        """Save the current dashboard layout"""
        layout_data = []
        for widget in self.widgets:
            widget_data = {
                'type': widget.widget_type,
                'title': widget.title,
                'x': widget.x(),
                'y': widget.y(),
                'width': widget.width(),
                'height': widget.height()
            }
            layout_data.append(widget_data)
        
        # Save to file
        try:
            with open('dashboard_layout.json', 'w') as f:
                json.dump(layout_data, f)
            
            QMessageBox.information(self, "Success", "Dashboard layout saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save layout: {str(e)}")
    
    def load_layout(self):
        """Load saved dashboard layout"""
        try:
            if os.path.exists('dashboard_layout.json'):
                with open('dashboard_layout.json', 'r') as f:
                    layout_data = json.load(f)
                
                for widget_data in layout_data:
                    if widget_data['type'] == 'metric':
                        widget = MetricWidget(widget_data['title'], "0", "units")
                    elif widget_data['type'] == 'chart':
                        widget = ChartWidget(widget_data['title'], "line")
                    else:
                        continue
                    
                    widget.setParent(self.drop_zone)
                    widget.move(widget_data['x'], widget_data['y'])
                    widget.resize(widget_data['width'], widget_data['height'])
                    widget.show()
                    
                    self.widgets.append(widget)
        except Exception as e:
            print(f"Failed to load layout: {e}")
    
    def reset_layout(self):
        """Reset dashboard layout"""
        reply = QMessageBox.question(
            self, "Reset Layout", 
            "Are you sure you want to reset the dashboard layout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove all widgets
            for widget in self.widgets:
                widget.deleteLater()
            self.widgets.clear()
            
            # Remove layout file
            if os.path.exists('dashboard_layout.json'):
                os.remove('dashboard_layout.json')

class DashboardCustomizerDialog(QDialog):
    """Dialog for dashboard customization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Dashboard")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Add customizer
        self.customizer = DashboardCustomizer()
        layout.addWidget(self.customizer)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

# Global customizer instance
dashboard_customizer = None 