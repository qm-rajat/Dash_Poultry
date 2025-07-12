from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, 
                             QLineEdit, QFileDialog, QAbstractItemView, QHeaderView, QSpinBox, QTextEdit)
from PyQt6.QtCore import Qt, QDate
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class MortalityDialog(QDialog):
    def __init__(self, parent=None, batches=None, mortality=None):
        super().__init__(parent)
        self.setWindowTitle("Mortality Record")
        self.setModal(True)
        self.resize(400, 350)
        layout = QFormLayout(self)
        
        self.batch_id = QComboBox()
        self.batch_id.addItems(batches or [])
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.count = QSpinBox()
        self.count.setRange(1, 10000)
        self.count.setSuffix(" birds")
        self.reason = QTextEdit()
        self.reason.setMaximumHeight(80)
        self.reason.setPlaceholderText("Enter reason for mortality (e.g., disease, accident, natural causes)")
        
        layout.addRow("Batch ID", self.batch_id)
        layout.addRow("Date", self.date)
        layout.addRow("Count", self.count)
        layout.addRow("Reason", self.reason)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
        if mortality:
            self.batch_id.setCurrentText(mortality[0])
            self.date.setDate(QDate.fromString(mortality[1], 'yyyy-MM-dd'))
            self.count.setValue(int(mortality[2]))
            self.reason.setPlainText(mortality[3])

    def get_data(self):
        return {
            'batch_id': self.batch_id.currentText(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'count': self.count.value(),
            'reason': self.reason.toPlainText().strip()
        }

class MortalityTrackerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_rows = []  # Store all rows for filtering
        self.init_ui()
        self.load_batches()
        self.load_mortality()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Mortality Tracker</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Search and filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by reason, batch, etc...")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Batch:"))
        self.batch_filter = QComboBox()
        self.batch_filter.currentIndexChanged.connect(self.load_mortality)
        filter_layout.addWidget(self.batch_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        self.total_mortality_label = QLabel("Total Mortality: 0")
        self.total_mortality_label.setStyleSheet("font-weight: bold; color: #dc2626;")
        stats_layout.addWidget(self.total_mortality_label)
        
        self.avg_mortality_label = QLabel("Avg per Record: 0")
        self.avg_mortality_label.setStyleSheet("font-weight: bold; color: #ea580c;")
        stats_layout.addWidget(self.avg_mortality_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Date", "Count", "Reason"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Mortality Record")
        self.add_btn.clicked.connect(self.add_mortality)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Record")
        self.edit_btn.clicked.connect(self.edit_mortality)
        btn_layout.addWidget(self.edit_btn)
        
        self.del_btn = QPushButton("Delete Record")
        self.del_btn.clicked.connect(self.delete_mortality)
        btn_layout.addWidget(self.del_btn)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        
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

    def load_mortality(self):
        conn = get_connection()
        c = conn.cursor()
        batch = self.batch_filter.currentText()
        if batch == "All":
            c.execute('SELECT batch_id, date, count, reason FROM mortality ORDER BY date DESC')
        else:
            c.execute('SELECT batch_id, date, count, reason FROM mortality WHERE batch_id=? ORDER BY date DESC', (batch,))
        rows = c.fetchall()
        self.all_rows = rows
        self.populate_table(rows)
        self.update_stats(rows)
        conn.close()

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else "")
                if col_idx == 2:  # Count column - make it stand out
                    item.setBackground(Qt.GlobalColor.lightGray)
                self.table.setItem(row_idx, col_idx, item)

    def update_stats(self, rows):
        if not rows:
            self.total_mortality_label.setText("Total Mortality: 0")
            self.avg_mortality_label.setText("Avg per Record: 0")
            return
        
        total = sum(row[2] for row in rows)
        avg = total / len(rows)
        self.total_mortality_label.setText(f"Total Mortality: {total}")
        self.avg_mortality_label.setText(f"Avg per Record: {avg:.1f}")

    def filter_table(self):
        text = self.search_input.text().lower()
        if not text:
            self.populate_table(self.all_rows)
            self.update_stats(self.all_rows)
            return
        filtered = [row for row in self.all_rows if any(text in str(cell).lower() for cell in row)]
        self.populate_table(filtered)
        self.update_stats(filtered)

    def add_mortality(self):
        dialog = MortalityDialog(self, batches=self.batches)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['reason']:
                QMessageBox.warning(self, "Validation Error", "Reason is required.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('INSERT INTO mortality (batch_id, date, count, reason) VALUES (?, ?, ?, ?)',
                    (data['batch_id'], data['date'], data['count'], data['reason']))
                conn.commit()
                QMessageBox.information(self, "Success", "Mortality record added successfully.")
                self.load_mortality()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add mortality record: {e}")
            finally:
                conn.close()

    def edit_mortality(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Record", "Please select a mortality record to edit.")
            return
        mortality = [self.table.item(row, i).text() for i in range(4)]
        dialog = MortalityDialog(self, batches=self.batches, mortality=mortality)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('UPDATE mortality SET date=?, count=?, reason=? WHERE batch_id=? AND date=? AND count=? AND reason=?',
                    (data['date'], data['count'], data['reason'], mortality[0], mortality[1], mortality[2], mortality[3]))
                conn.commit()
                QMessageBox.information(self, "Success", "Mortality record updated successfully.")
                self.load_mortality()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update mortality record: {e}")
            finally:
                conn.close()

    def delete_mortality(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Record", "Please select a mortality record to delete.")
            return
        mortality = [self.table.item(row, i).text() for i in range(4)]
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete this mortality record?\n\nBatch: {mortality[0]}\nDate: {mortality[1]}\nCount: {mortality[2]}\nReason: {mortality[3]}",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM mortality WHERE batch_id=? AND date=? AND count=? AND reason=?',
                    (mortality[0], mortality[1], mortality[2], mortality[3]))
                conn.commit()
                QMessageBox.information(self, "Success", "Mortality record deleted successfully.")
                self.load_mortality()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete mortality record: {e}")
            finally:
                conn.close()

    def export_csv(self):
        if not self.all_rows:
            QMessageBox.warning(self, "No Data", "No mortality records to export.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export Mortality Records", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Batch ID", "Date", "Count", "Reason"])
                    writer.writerows(self.all_rows)
                QMessageBox.information(self, "Success", f"Mortality records exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}") 