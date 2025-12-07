from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, QDoubleSpinBox
from PyQt6.QtCore import Qt, QDate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.data_manager import data_manager

class LogDialog(QDialog):
    def __init__(self, parent=None, batches=None, log=None):
        super().__init__(parent)
        self.setWindowTitle("Feed/Water Log")
        self.setModal(True)
        self.resize(320, 220)
        layout = QFormLayout(self)
        self.batch_id = QComboBox()
        self.batch_id.addItems(batches or [])
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.feed = QDoubleSpinBox()
        self.feed.setRange(0, 10000)
        self.feed.setDecimals(2)
        self.feed.setSuffix(" kg")
        self.water = QDoubleSpinBox()
        self.water.setRange(0, 10000)
        self.water.setDecimals(2)
        self.water.setSuffix(" L")
        layout.addRow("Batch ID", self.batch_id)
        layout.addRow("Date", self.date)
        layout.addRow("Feed (kg)", self.feed)
        layout.addRow("Water (L)", self.water)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        if log:
            self.batch_id.setCurrentText(log[0])
            self.date.setDate(QDate.fromString(log[1], 'yyyy-MM-dd'))
            if log[2]:
                self.feed.setValue(float(log[2]))
            if log[3]:
                self.water.setValue(float(log[3]))

    def get_data(self):
        return {
            'batch_id': self.batch_id.currentText(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'feed': self.feed.value(),
            'water': self.water.value(),
        }

class FeedWaterLogsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_batches()
        try:
            data_manager.batch_data_changed.connect(self.on_batch_data_changed)
        except Exception:
            pass
        self.load_logs()

    def on_batch_data_changed(self):
        self.load_batches()
        self.load_logs()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Feed/Water Logs</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Batch:"))
        self.batch_filter = QComboBox()
        self.batch_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(self.batch_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Date", "Feed (kg)", "Water (L)"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Log")
        self.add_btn.clicked.connect(self.add_log)
        btn_layout.addWidget(self.add_btn)
        self.edit_btn = QPushButton("Edit Log")
        self.edit_btn.clicked.connect(self.edit_log)
        btn_layout.addWidget(self.edit_btn)
        self.del_btn = QPushButton("Delete Log")
        self.del_btn.clicked.connect(self.delete_log)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_batches(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT batch_id FROM batches ORDER BY batch_id')
        self.batches = [row[0] for row in c.fetchall()]
        self.batch_filter.clear()
        self.batch_filter.addItem("All")
        self.batch_filter.addItems(self.batches)
        conn.close()

    def load_logs(self):
        conn = get_connection()
        c = conn.cursor()
        batch = self.batch_filter.currentText()
        if batch == "All":
            c.execute('''
                SELECT DISTINCT batch_id, date FROM (
                    SELECT batch_id, date FROM feed_logs
                    UNION
                    SELECT batch_id, date FROM water_logs
                ) ORDER BY date DESC
            ''')
            pairs = c.fetchall()
        else:
            c.execute('''
                SELECT DISTINCT batch_id, date FROM (
                    SELECT batch_id, date FROM feed_logs WHERE batch_id=?
                    UNION
                    SELECT batch_id, date FROM water_logs WHERE batch_id=?
                ) ORDER BY date DESC
            ''', (batch, batch))
            pairs = c.fetchall()
        rows = []
        for batch_id, date in pairs:
            c.execute('SELECT quantity_kg FROM feed_logs WHERE batch_id=? AND date=?', (batch_id, date))
            feed = c.fetchone()
            c.execute('SELECT quantity_l FROM water_logs WHERE batch_id=? AND date=?', (batch_id, date))
            water = c.fetchone()
            rows.append((batch_id, date, feed[0] if feed else '', water[0] if water else ''))
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.table.setItem(row_idx, col_idx, item)
        conn.close()

    def add_log(self):
        dialog = LogDialog(self, batches=self.batches)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['feed'] == 0 and data['water'] == 0:
                QMessageBox.warning(self, "Validation Error", "Enter feed or water value.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                if data['feed'] > 0:
                    c.execute('INSERT INTO feed_logs (batch_id, date, quantity_kg) VALUES (?, ?, ?)',
                              (data['batch_id'], data['date'], data['feed']))
                if data['water'] > 0:
                    c.execute('INSERT INTO water_logs (batch_id, date, quantity_l) VALUES (?, ?, ?)',
                              (data['batch_id'], data['date'], data['water']))
                conn.commit()
                QMessageBox.information(self, "Success", "Log added successfully.")
                self.load_logs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add log: {e}")
            finally:
                conn.close()

    def edit_log(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Log", "Please select a log to edit.")
            return
        log = [self.table.item(row, i).text() for i in range(4)]
        dialog = LogDialog(self, batches=self.batches, log=log)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                # Delete old log
                if log[2]:
                    c.execute('DELETE FROM feed_logs WHERE batch_id=? AND date=?', (log[0], log[1]))
                if log[3]:
                    c.execute('DELETE FROM water_logs WHERE batch_id=? AND date=?', (log[0], log[1]))
                # Insert new log
                if data['feed'] > 0:
                    c.execute('INSERT INTO feed_logs (batch_id, date, quantity_kg) VALUES (?, ?, ?)',
                              (data['batch_id'], data['date'], data['feed']))
                if data['water'] > 0:
                    c.execute('INSERT INTO water_logs (batch_id, date, quantity_l) VALUES (?, ?, ?)',
                              (data['batch_id'], data['date'], data['water']))
                conn.commit()
                QMessageBox.information(self, "Success", "Log updated successfully.")
                self.load_logs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update log: {e}")
            finally:
                conn.close()

    def delete_log(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Log", "Please select a log to delete.")
            return
        log = [self.table.item(row, i).text() for i in range(4)]
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete log for batch '{log[0]}' on {log[1]}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                if log[2]:
                    c.execute('DELETE FROM feed_logs WHERE batch_id=? AND date=?', (log[0], log[1]))
                if log[3]:
                    c.execute('DELETE FROM water_logs WHERE batch_id=? AND date=?', (log[0], log[1]))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Log deleted.")
                self.load_logs()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete log: {e}")
            finally:
                conn.close() 