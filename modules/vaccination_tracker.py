from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, 
                             QLineEdit, QFileDialog, QAbstractItemView, QHeaderView)
from PyQt6.QtCore import Qt, QDate
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class VaccinationDialog(QDialog):
    def __init__(self, parent=None, batches=None, vaccination=None):
        super().__init__(parent)
        self.setWindowTitle("Vaccination Details")
        self.setModal(True)
        self.resize(350, 280)
        layout = QFormLayout(self)
        
        self.batch_id = QComboBox()
        self.batch_id.addItems(batches or [])
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.vaccine = QLineEdit()
        self.vaccine.setPlaceholderText("e.g., Newcastle Disease, Marek Disease")
        self.status = QComboBox()
        self.status.addItems(["Scheduled", "Completed", "Cancelled", "Postponed"])
        
        layout.addRow("Batch ID", self.batch_id)
        layout.addRow("Date", self.date)
        layout.addRow("Vaccine", self.vaccine)
        layout.addRow("Status", self.status)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
        if vaccination:
            self.batch_id.setCurrentText(vaccination[0])
            self.date.setDate(QDate.fromString(vaccination[1], 'yyyy-MM-dd'))
            self.vaccine.setText(vaccination[2])
            self.status.setCurrentText(vaccination[3])

    def get_data(self):
        return {
            'batch_id': self.batch_id.currentText(),
            'date': self.date.date().toString('yyyy-MM-dd'),
            'vaccine': self.vaccine.text().strip(),
            'status': self.status.currentText()
        }

class VaccinationTrackerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_rows = []  # Store all rows for filtering
        self.init_ui()
        self.load_batches()
        self.load_vaccinations()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Vaccination Tracker</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Search and filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by vaccine, status, etc...")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Batch:"))
        self.batch_filter = QComboBox()
        self.batch_filter.currentIndexChanged.connect(self.load_vaccinations)
        filter_layout.addWidget(self.batch_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Date", "Vaccine", "Status"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Vaccination")
        self.add_btn.clicked.connect(self.add_vaccination)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Vaccination")
        self.edit_btn.clicked.connect(self.edit_vaccination)
        btn_layout.addWidget(self.edit_btn)
        
        self.del_btn = QPushButton("Delete Vaccination")
        self.del_btn.clicked.connect(self.delete_vaccination)
        btn_layout.addWidget(self.del_btn)
        
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
        c.execute('SELECT batch_id FROM batches ORDER BY batch_id')
        self.batches = [row[0] for row in c.fetchall()]
        self.batch_filter.clear()
        self.batch_filter.addItem("All")
        self.batch_filter.addItems(self.batches)
        conn.close()

    def load_vaccinations(self):
        conn = get_connection()
        c = conn.cursor()
        batch = self.batch_filter.currentText()
        if batch == "All":
            c.execute('SELECT batch_id, date, vaccine, status FROM vaccinations ORDER BY date DESC')
        else:
            c.execute('SELECT batch_id, date, vaccine, status FROM vaccinations WHERE batch_id=? ORDER BY date DESC', (batch,))
        rows = c.fetchall()
        self.all_rows = rows
        self.populate_table(rows)
        conn.close()

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if value is not None else "")
                self.table.setItem(row_idx, col_idx, item)

    def filter_table(self):
        text = self.search_input.text().lower()
        if not text:
            self.populate_table(self.all_rows)
            return
        filtered = [row for row in self.all_rows if any(text in str(cell).lower() for cell in row)]
        self.populate_table(filtered)

    def add_vaccination(self):
        dialog = VaccinationDialog(self, batches=self.batches)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['vaccine']:
                QMessageBox.warning(self, "Validation Error", "Vaccine name is required.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('INSERT INTO vaccinations (batch_id, date, vaccine, status) VALUES (?, ?, ?, ?)',
                    (data['batch_id'], data['date'], data['vaccine'], data['status']))
                conn.commit()
                QMessageBox.information(self, "Success", "Vaccination added successfully.")
                self.load_vaccinations()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add vaccination: {e}")
            finally:
                conn.close()

    def edit_vaccination(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Vaccination", "Please select a vaccination to edit.")
            return
        vaccination = [self.table.item(row, i).text() for i in range(4)]
        dialog = VaccinationDialog(self, batches=self.batches, vaccination=vaccination)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('UPDATE vaccinations SET date=?, vaccine=?, status=? WHERE batch_id=? AND date=? AND vaccine=?',
                    (data['date'], data['vaccine'], data['status'], vaccination[0], vaccination[1], vaccination[2]))
                conn.commit()
                QMessageBox.information(self, "Success", "Vaccination updated successfully.")
                self.load_vaccinations()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update vaccination: {e}")
            finally:
                conn.close()

    def delete_vaccination(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Vaccination", "Please select a vaccination to delete.")
            return
        vaccination = [self.table.item(row, i).text() for i in range(4)]
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete this vaccination?\n\nBatch: {vaccination[0]}\nDate: {vaccination[1]}\nVaccine: {vaccination[2]}",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM vaccinations WHERE batch_id=? AND date=? AND vaccine=?',
                    (vaccination[0], vaccination[1], vaccination[2]))
                conn.commit()
                QMessageBox.information(self, "Success", "Vaccination deleted successfully.")
                self.load_vaccinations()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete vaccination: {e}")
            finally:
                conn.close()

    def export_csv(self):
        if not self.all_rows:
            QMessageBox.warning(self, "No Data", "No vaccinations to export.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export Vaccinations", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Batch ID", "Date", "Vaccine", "Status"])
                    writer.writerows(self.all_rows)
                QMessageBox.information(self, "Success", f"Vaccinations exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def print_table(self):
        if not self.all_rows:
            QMessageBox.warning(self, "No Data", "No vaccinations to print.")
            return
        
        try:
            # Try to import printing components
            try:
                from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
                from PyQt6.QtGui import QTextDocument, QTextCursor, QTextTableFormat
            except ImportError:
                QMessageBox.warning(self, "Print Error", "Printing is not available on this system.")
                return
            
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Create document
                doc = QTextDocument()
                cursor = QTextCursor(doc)
                
                # Add title
                cursor.insertText("Vaccination Tracker Report\n")
                cursor.insertText("=" * 50 + "\n\n")
                
                # Create table
                table_format = QTextTableFormat()
                table_format.setHeaderRowCount(1)
                table_format.setBorder(1)
                table = cursor.insertTable(len(self.all_rows) + 1, 4, table_format)
                
                # Headers
                headers = ["Batch ID", "Date", "Vaccine", "Status"]
                for i, header in enumerate(headers):
                    cell = table.cellAt(0, i)
                    cell_cursor = cell.firstCursorPosition()
                    cell_cursor.insertText(header)
                
                # Data
                for row_idx, row in enumerate(self.all_rows):
                    for col_idx, value in enumerate(row):
                        cell = table.cellAt(row_idx + 1, col_idx)
                        cell_cursor = cell.firstCursorPosition()
                        cell_cursor.insertText(str(value))
                
                # Print
                doc.print_(printer)
                QMessageBox.information(self, "Success", "Table printed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to print: {e}")
            # Fallback: Save as text file
            try:
                filename, _ = QFileDialog.getSaveFileName(self, "Save Report as Text", "", "Text Files (*.txt)")
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Vaccination Tracker Report\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"{'Batch ID':<15} {'Date':<12} {'Vaccine':<25} {'Status':<15}\n")
                        f.write("-" * 70 + "\n")
                        for row in self.all_rows:
                            f.write(f"{row[0]:<15} {row[1]:<12} {row[2]:<25} {row[3]:<15}\n")
                    QMessageBox.information(self, "Success", f"Report saved as text file: {filename}")
            except Exception as save_error:
                QMessageBox.critical(self, "Error", f"Failed to save report: {save_error}") 