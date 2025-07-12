from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QFileDialog, QAbstractItemView, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class BatchDialog(QDialog):
    def __init__(self, parent=None, batch=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Details")
        self.setModal(True)
        self.resize(350, 320)
        layout = QFormLayout(self)
        self.batch_id = QLineEdit()
        self.num_chicks = QSpinBox()
        self.num_chicks.setRange(1, 100000)
        self.breed = QLineEdit()
        self.date_in = QDateEdit()
        self.date_in.setCalendarPopup(True)
        self.date_in.setDate(QDate.currentDate())
        self.expected_out = QDateEdit()
        self.expected_out.setCalendarPopup(True)
        self.expected_out.setDate(QDate.currentDate().addDays(60))
        self.mortality_rate = QDoubleSpinBox()
        self.mortality_rate.setRange(0, 1)
        self.mortality_rate.setSingleStep(0.01)
        self.mortality_rate.setSuffix(" (0-1)")
        layout.addRow("Batch ID", self.batch_id)
        layout.addRow("# Chicks", self.num_chicks)
        layout.addRow("Breed", self.breed)
        layout.addRow("Date In", self.date_in)
        layout.addRow("Expected Out", self.expected_out)
        layout.addRow("Mortality Rate", self.mortality_rate)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        if batch:
            self.batch_id.setText(batch[0])
            self.batch_id.setReadOnly(True)
            self.num_chicks.setValue(int(batch[1]))
            self.breed.setText(batch[2])
            self.date_in.setDate(QDate.fromString(batch[3], 'yyyy-MM-dd'))
            self.expected_out.setDate(QDate.fromString(batch[4], 'yyyy-MM-dd'))
            self.mortality_rate.setValue(float(batch[5]))

    def get_data(self):
        return {
            'batch_id': self.batch_id.text().strip(),
            'num_chicks': self.num_chicks.value(),
            'breed': self.breed.text().strip(),
            'date_in': self.date_in.date().toString('yyyy-MM-dd'),
            'expected_out': self.expected_out.date().toString('yyyy-MM-dd'),
            'mortality_rate': self.mortality_rate.value(),
        }

class BatchManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_rows = []  # Store all rows for filtering
        self.init_ui()
        self.load_batches()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Chick Batch Management</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Batch ID, Breed, etc...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Batch ID", "# Chicks", "Breed", "Date In", "Expected Out", "Mortality Rate"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Batch")
        self.add_btn.clicked.connect(self.add_batch)
        btn_layout.addWidget(self.add_btn)
        self.edit_btn = QPushButton("Edit Batch")
        self.edit_btn.clicked.connect(self.edit_batch)
        btn_layout.addWidget(self.edit_btn)
        self.del_btn = QPushButton("Delete Batch")
        self.del_btn.clicked.connect(self.delete_batch)
        btn_layout.addWidget(self.del_btn)
        
        # Cross-module action buttons
        self.feed_btn = QPushButton("Log Feed/Water")
        self.feed_btn.setStyleSheet("background-color: #3b82f6; color: white;")
        self.feed_btn.clicked.connect(lambda: self.parent().parent().parent().switch_module(2))
        btn_layout.addWidget(self.feed_btn)
        
        self.vaccine_btn = QPushButton("Record Vaccination")
        self.vaccine_btn.setStyleSheet("background-color: #10b981; color: white;")
        self.vaccine_btn.clicked.connect(lambda: self.parent().parent().parent().switch_module(3))
        btn_layout.addWidget(self.vaccine_btn)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        self.print_btn = QPushButton("Print Table")
        self.print_btn.clicked.connect(self.print_table)
        btn_layout.addWidget(self.print_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_batches(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT batch_id, num_chicks, breed, date_in, expected_out, mortality_rate FROM batches ORDER BY date_in DESC')
        rows = c.fetchall()
        self.all_rows = rows
        self.populate_table(rows)
        conn.close()

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

    def filter_table(self):
        text = self.search_input.text().lower()
        if not text:
            self.populate_table(self.all_rows)
            return
        filtered = [row for row in self.all_rows if any(text in str(cell).lower() for cell in row)]
        self.populate_table(filtered)

    def add_batch(self):
        dialog = BatchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['batch_id'] or not data['breed']:
                QMessageBox.warning(self, "Validation Error", "Batch ID and Breed are required.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('INSERT INTO batches (batch_id, num_chicks, breed, date_in, expected_out, mortality_rate) VALUES (?, ?, ?, ?, ?, ?)',
                    (data['batch_id'], data['num_chicks'], data['breed'], data['date_in'], data['expected_out'], data['mortality_rate']))
                conn.commit()
                QMessageBox.information(self, "Success", "Batch added successfully.")
                self.load_batches()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add batch: {e}")
            finally:
                conn.close()

    def edit_batch(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Batch", "Please select a batch to edit.")
            return
        batch = [self.table.item(row, i).text() for i in range(6)]
        dialog = BatchDialog(self, batch=batch)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('UPDATE batches SET num_chicks=?, breed=?, date_in=?, expected_out=?, mortality_rate=? WHERE batch_id=?',
                    (data['num_chicks'], data['breed'], data['date_in'], data['expected_out'], data['mortality_rate'], data['batch_id']))
                conn.commit()
                QMessageBox.information(self, "Success", "Batch updated successfully.")
                self.load_batches()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update batch: {e}")
            finally:
                conn.close()

    def delete_batch(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Batch", "Please select a batch to delete.")
            return
        batch_id = self.table.item(row, 0).text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete batch '{batch_id}'? This cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM batches WHERE batch_id=?', (batch_id,))
                conn.commit()
                QMessageBox.information(self, "Deleted", "Batch deleted.")
                self.load_batches()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete batch: {e}")
            finally:
                conn.close()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "batches.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())])
                for row in range(self.table.rowCount()):
                    writer.writerow([self.table.item(row, col).text() if self.table.item(row, col) else '' for col in range(self.table.columnCount())])
            QMessageBox.information(self, "Exported", f"Batches exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def print_table(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Print the table as plain text (for simplicity)
            doc = ''
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            doc += '\t'.join(headers) + '\n'
            for row in range(self.table.rowCount()):
                doc += '\t'.join([self.table.item(row, col).text() if self.table.item(row, col) else '' for col in range(self.table.columnCount())]) + '\n'
            from PyQt6.QtGui import QTextDocument
            text_doc = QTextDocument(doc)
            text_doc.print(printer) 