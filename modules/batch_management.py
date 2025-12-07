from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QDialog, QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QFileDialog, QAbstractItemView, QHeaderView, QToolTip)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.data_manager import data_manager
from PyQt6.QtGui import QKeySequence, QShortcut, QTextDocument

class BatchDialog(QDialog):
    def __init__(self, parent=None, batch=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Details")
        self.setModal(True)
        self.resize(350, 320)
        layout = QFormLayout(self)
        self.batch_id = QLineEdit()
        self.batch_id.setToolTip("Unique identifier for the batch. Cannot be changed after creation.")
        self.num_chicks = QSpinBox()
        self.num_chicks.setRange(1, 100000)
        self.num_chicks.setToolTip("Total number of chicks in this batch.")
        self.breed = QLineEdit()
        self.breed.setToolTip("Breed of the chicks (e.g., Broiler, Layer, etc.)")
        self.date_in = QDateEdit()
        self.date_in.setCalendarPopup(True)
        self.date_in.setDate(QDate.currentDate())
        self.date_in.setToolTip("Date when the batch was brought in.")
        self.expected_out = QDateEdit()
        self.expected_out.setCalendarPopup(True)
        self.expected_out.setDate(QDate.currentDate().addDays(60))
        self.expected_out.setToolTip("Expected date for batch completion or sale.")
        self.mortality_rate = QDoubleSpinBox()
        self.mortality_rate.setRange(0, 1)
        self.mortality_rate.setSingleStep(0.01)
        self.mortality_rate.setSuffix(" (0-1)")
        self.mortality_rate.setToolTip("Mortality rate as a decimal (e.g., 0.05 for 5%).")
        layout.addRow("Batch ID", self.batch_id)
        layout.addRow("# Chicks", self.num_chicks)
        layout.addRow("Breed", self.breed)
        layout.addRow("Date In", self.date_in)
        layout.addRow("Expected Out", self.expected_out)
        layout.addRow("Mortality Rate", self.mortality_rate)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setToolTip("Save batch details.")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setToolTip("Cancel and close this dialog.")
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
        # Center dialog on parent
        if parent:
            geo = parent.frameGeometry()
            self.move(geo.center() - self.rect().center())
        # Set tab order
        self.setTabOrder(self.batch_id, self.num_chicks)
        self.setTabOrder(self.num_chicks, self.breed)
        self.setTabOrder(self.breed, self.date_in)
        self.setTabOrder(self.date_in, self.expected_out)
        self.setTabOrder(self.expected_out, self.mortality_rate)
        self.setTabOrder(self.mortality_rate, self.buttons)

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
        self.search_input.setToolTip("Type to filter batches by ID, breed, etc.")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Batch ID", "# Chicks", "Breed", "Date In", "Expected Out", "Mortality Rate"
        ])
        for i, header in enumerate(["Batch ID", "# Chicks", "Breed", "Date In", "Expected Out", "Mortality Rate"]):
            self.table.horizontalHeaderItem(i).setToolTip(header)
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
        self.add_btn.setToolTip("Add a new batch record (Ctrl+N)")
        self.add_btn.clicked.connect(self.add_batch)
        btn_layout.addWidget(self.add_btn)
        self.edit_btn = QPushButton("Edit Batch")
        self.edit_btn.setToolTip("Edit the selected batch (Ctrl+E)")
        self.edit_btn.clicked.connect(self.edit_batch)
        btn_layout.addWidget(self.edit_btn)
        self.del_btn = QPushButton("Delete Batch")
        self.del_btn.setToolTip("Delete the selected batch (Del)")
        self.del_btn.clicked.connect(self.delete_batch)
        btn_layout.addWidget(self.del_btn)
        # Cross-module action buttons
        self.feed_btn = QPushButton("Log Feed/Water")
        self.feed_btn.setStyleSheet("background-color: #3b82f6; color: white;")
        self.feed_btn.setToolTip("Log feed and water usage for the selected batch.")
        self.feed_btn.clicked.connect(lambda: self.parent().parent().parent().switch_module(2))
        btn_layout.addWidget(self.feed_btn)
        self.vaccine_btn = QPushButton("Record Vaccination")
        self.vaccine_btn.setStyleSheet("background-color: #10b981; color: white;")
        self.vaccine_btn.setToolTip("Record a vaccination for the selected batch.")
        self.vaccine_btn.clicked.connect(lambda: self.parent().parent().parent().switch_module(3))
        btn_layout.addWidget(self.vaccine_btn)
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setToolTip("Export batch data to CSV file.")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        self.print_btn = QPushButton("Print Table")
        self.print_btn.setToolTip("Print the batch table.")
        self.print_btn.clicked.connect(self.print_table)
        btn_layout.addWidget(self.print_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, self.add_batch)
        QShortcut(QKeySequence("Ctrl+E"), self, self.edit_batch)
        QShortcut(QKeySequence("Delete"), self, self.delete_batch)

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
            batch_id = data.get('batch_id', '').strip()
            if not batch_id:
                QMessageBox.warning(self, "Validation Error", "Batch ID cannot be empty.")
                return
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute('SELECT 1 FROM batches WHERE batch_id = ?', (batch_id,))
                if c.fetchone():
                    QMessageBox.warning(self, "Duplicate Batch", f"Batch ID '{batch_id}' already exists.")
                    conn.close()
                    return
                c.execute(
                    'INSERT INTO batches (batch_id, num_chicks, breed, date_in, expected_out, mortality_rate) VALUES (?,?,?,?,?,?)',
                    (batch_id, data.get('num_chicks'), data.get('breed'), data.get('date_in'), data.get('expected_out'), data.get('mortality_rate'))
                )
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"Batch '{batch_id}' added successfully.")
                self.load_batches()
                # Notify other modules that batches changed
                try:
                    data_manager.notify_batch_change()
                except Exception:
                    pass
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add batch: {e}")
                try:
                    conn.close()
                except:
                    pass

    def edit_batch(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a batch to edit.")
            return
        batch = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
        dialog = BatchDialog(self, batch=batch)
        # Allow editing batch_id here (override dialog default)
        try:
            dialog.batch_id.setReadOnly(False)
            dialog.batch_id.setToolTip("You may change the Batch ID. Related records will be updated.")
        except Exception:
            pass

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            old_id = batch[0]
            new_id = data.get('batch_id', '').strip()
            if not new_id:
                QMessageBox.warning(self, "Validation Error", "Batch ID cannot be empty.")
                return
            try:
                conn = get_connection()
                c = conn.cursor()
                # If ID changed, ensure new ID isn't already used
                if new_id != old_id:
                    c.execute('SELECT 1 FROM batches WHERE batch_id=?', (new_id,))
                    if c.fetchone():
                        QMessageBox.warning(self, "Duplicate Batch", f"Batch ID '{new_id}' already exists.")
                        conn.close()
                        return
                # Begin update within a transaction
                # Update batches table (may change primary key value)
                c.execute(
                    'UPDATE batches SET batch_id=?, num_chicks=?, breed=?, date_in=?, expected_out=?, mortality_rate=? WHERE batch_id=?',
                    (new_id, data.get('num_chicks'), data.get('breed'), data.get('date_in'), data.get('expected_out'), data.get('mortality_rate'), old_id)
                )
                # Update references in other tables that use batch_id
                related_tables = ['feed_logs', 'water_logs', 'revenue', 'mortality', 'vaccinations']
                for tbl in related_tables:
                    try:
                        c.execute(f'UPDATE {tbl} SET batch_id=? WHERE batch_id=?', (new_id, old_id))
                    except Exception:
                        # If table doesn't exist or another issue, skip but continue
                        pass
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", f"Batch '{old_id}' updated to '{new_id}' successfully.")
                self.load_batches()
                try:
                    data_manager.notify_batch_change()
                except Exception:
                    pass
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to update batch: {e}")
                try:
                    conn.close()
                except:
                    pass

    def delete_batch(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a batch to delete.")
            return
        batch_id = self.table.item(row, 0).text()
        resp = QMessageBox.question(self, "Confirm Delete", f"Delete batch '{batch_id}'? This cannot be undone.")
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute('DELETE FROM batches WHERE batch_id=?', (batch_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Deleted", f"Batch '{batch_id}' deleted.")
            self.load_batches()
            try:
                data_manager.notify_batch_change()
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to delete batch: {e}")
            try:
                conn.close()
            except:
                pass

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "batches.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)
                for r in range(self.table.rowCount()):
                    row = [self.table.item(r, c).text() if self.table.item(r, c) else '' for c in range(self.table.columnCount())]
                    writer.writerow(row)
            QMessageBox.information(self, "Exported", f"Batches exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV: {e}")

    def print_table(self):
        try:
            # Build simple HTML table from current view
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            html = '<html><head><meta charset="utf-8"></head><body><table border="1" cellspacing="0" cellpadding="4">'
            html += '<tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr>'
            for r in range(self.table.rowCount()):
                html += '<tr>' + ''.join([f'<td>{(self.table.item(r, c).text() if self.table.item(r, c) else "")}</td>' for c in range(self.table.columnCount())]) + '</tr>'
            html += '</table></body></html>'
            doc = QTextDocument()
            doc.setHtml(html)
            printer = QPrinter()
            dlg = QPrintDialog(printer, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                doc.print(printer)
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print table: {e}")