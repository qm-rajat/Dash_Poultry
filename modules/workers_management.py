from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, 
                             QLineEdit, QFileDialog, QAbstractItemView, QHeaderView, QSpinBox, QTextEdit, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class WorkerDialog(QDialog):
    def __init__(self, parent=None, worker=None):
        super().__init__(parent)
        self.setWindowTitle("Worker Details")
        self.setModal(True)
        self.resize(450, 500)
        layout = QFormLayout(self)
        
        self.worker_id = QLineEdit()
        self.worker_id.setPlaceholderText("e.g., W001, W002")
        self.name = QLineEdit()
        self.name.setPlaceholderText("Full name")
        self.role = QComboBox()
        self.role.addItems(["Farm Manager", "Feeder", "Cleaner", "Vaccinator", "Driver", "Maintenance", "Other"])
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Phone number")
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email address")
        self.address = QTextEdit()
        self.address.setMaximumHeight(80)
        self.address.setPlaceholderText("Full address")
        self.salary = QDoubleSpinBox()
        self.salary.setRange(0, 100000)
        self.salary.setDecimals(2)
        self.salary.setSuffix(" ₹")
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        self.status = QComboBox()
        self.status.addItems(["Active", "Inactive", "On Leave", "Terminated"])
        
        layout.addRow("Worker ID", self.worker_id)
        layout.addRow("Name", self.name)
        layout.addRow("Role", self.role)
        layout.addRow("Phone", self.phone)
        layout.addRow("Email", self.email)
        layout.addRow("Address", self.address)
        layout.addRow("Salary (₹)", self.salary)
        layout.addRow("Hire Date", self.hire_date)
        layout.addRow("Status", self.status)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
        if worker:
            self.worker_id.setText(worker[0])
            self.worker_id.setReadOnly(True)  # Don't allow editing ID
            self.name.setText(worker[1])
            self.role.setCurrentText(worker[2])
            self.phone.setText(worker[3])
            self.email.setText(worker[4])
            self.address.setPlainText(worker[5])
            self.salary.setValue(float(worker[6]))
            self.hire_date.setDate(QDate.fromString(worker[7], 'yyyy-MM-dd'))
            self.status.setCurrentText(worker[8])

    def get_data(self):
        return {
            'worker_id': self.worker_id.text().strip(),
            'name': self.name.text().strip(),
            'role': self.role.currentText(),
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip(),
            'address': self.address.toPlainText().strip(),
            'salary': self.salary.value(),
            'hire_date': self.hire_date.date().toString('yyyy-MM-dd'),
            'status': self.status.currentText()
        }

class WorkersManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_rows = []  # Store all rows for filtering
        self.init_ui()
        self.load_workers()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Workers Management</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Search and filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, role, ID, etc...")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Role:"))
        self.role_filter = QComboBox()
        self.role_filter.addItems(["All", "Farm Manager", "Feeder", "Cleaner", "Vaccinator", "Driver", "Maintenance", "Other"])
        self.role_filter.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.role_filter)
        
        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Inactive", "On Leave", "Terminated"])
        self.status_filter.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        self.total_workers_label = QLabel("Total Workers: 0")
        self.total_workers_label.setStyleSheet("font-weight: bold; color: #059669;")
        stats_layout.addWidget(self.total_workers_label)
        
        self.active_workers_label = QLabel("Active: 0")
        self.active_workers_label.setStyleSheet("font-weight: bold; color: #059669;")
        stats_layout.addWidget(self.active_workers_label)
        
        self.total_salary_label = QLabel("Total Salary: ₹0")
        self.total_salary_label.setStyleSheet("font-weight: bold; color: #dc2626;")
        stats_layout.addWidget(self.total_salary_label)
        
        self.avg_salary_label = QLabel("Avg Salary: ₹0")
        self.avg_salary_label.setStyleSheet("font-weight: bold; color: #ea580c;")
        stats_layout.addWidget(self.avg_salary_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["Worker ID", "Name", "Role", "Phone", "Email", "Address", "Salary (₹)", "Hire Date", "Status"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Worker")
        self.add_btn.clicked.connect(self.add_worker)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Worker")
        self.edit_btn.clicked.connect(self.edit_worker)
        btn_layout.addWidget(self.edit_btn)
        
        self.del_btn = QPushButton("Delete Worker")
        self.del_btn.clicked.connect(self.delete_worker)
        btn_layout.addWidget(self.del_btn)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_workers(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT worker_id, name, role, phone, email, address, salary, hire_date, status FROM workers ORDER BY name')
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
                if col_idx == 6:  # Salary column - make it stand out
                    item.setBackground(Qt.GlobalColor.lightGray)
                elif col_idx == 8:  # Status column - color code
                    if value == "Active":
                        item.setBackground(Qt.GlobalColor.green)
                    elif value == "Inactive":
                        item.setBackground(Qt.GlobalColor.lightGray)
                    elif value == "On Leave":
                        item.setBackground(Qt.GlobalColor.yellow)
                    elif value == "Terminated":
                        item.setBackground(Qt.GlobalColor.red)
                self.table.setItem(row_idx, col_idx, item)

    def update_stats(self, rows):
        if not rows:
            self.total_workers_label.setText("Total Workers: 0")
            self.active_workers_label.setText("Active: 0")
            self.total_salary_label.setText("Total Salary: ₹0")
            self.avg_salary_label.setText("Avg Salary: ₹0")
            return
        
        total_workers = len(rows)
        active_workers = len([row for row in rows if row[8] == "Active"])
        total_salary = sum(row[6] for row in rows if row[6] is not None)
        avg_salary = total_salary / total_workers if total_workers > 0 else 0
        
        self.total_workers_label.setText(f"Total Workers: {total_workers}")
        self.active_workers_label.setText(f"Active: {active_workers}")
        self.total_salary_label.setText(f"Total Salary: ₹{total_salary:,.2f}")
        self.avg_salary_label.setText(f"Avg Salary: ₹{avg_salary:,.2f}")

    def filter_table(self):
        text = self.search_input.text().lower()
        role_filter = self.role_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered = []
        for row in self.all_rows:
            # Text search
            text_match = not text or any(text in str(cell).lower() for cell in row)
            # Role filter
            role_match = role_filter == "All" or row[2] == role_filter
            # Status filter
            status_match = status_filter == "All" or row[8] == status_filter
            
            if text_match and role_match and status_match:
                filtered.append(row)
        
        self.populate_table(filtered)
        self.update_stats(filtered)

    def add_worker(self):
        dialog = WorkerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data['worker_id'] or not data['name']:
                QMessageBox.warning(self, "Validation Error", "Worker ID and Name are required.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO workers (worker_id, name, role, phone, email, address, salary, hire_date, status) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (data['worker_id'], data['name'], data['role'], data['phone'], data['email'], 
                     data['address'], data['salary'], data['hire_date'], data['status']))
                conn.commit()
                QMessageBox.information(self, "Success", "Worker added successfully.")
                self.load_workers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add worker: {e}")
            finally:
                conn.close()

    def edit_worker(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Worker", "Please select a worker to edit.")
            return
        worker = [self.table.item(row, i).text() for i in range(9)]
        dialog = WorkerDialog(self, worker=worker)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('''UPDATE workers SET name=?, role=?, phone=?, email=?, address=?, salary=?, hire_date=?, status=? 
                             WHERE worker_id=?''',
                    (data['name'], data['role'], data['phone'], data['email'], data['address'], 
                     data['salary'], data['hire_date'], data['status'], data['worker_id']))
                conn.commit()
                QMessageBox.information(self, "Success", "Worker updated successfully.")
                self.load_workers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update worker: {e}")
            finally:
                conn.close()

    def delete_worker(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Worker", "Please select a worker to delete.")
            return
        worker = [self.table.item(row, i).text() for i in range(9)]
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete this worker?\n\nID: {worker[0]}\nName: {worker[1]}\nRole: {worker[2]}",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM workers WHERE worker_id=?', (worker[0],))
                conn.commit()
                QMessageBox.information(self, "Success", "Worker deleted successfully.")
                self.load_workers()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete worker: {e}")
            finally:
                conn.close()

    def export_csv(self):
        if not self.all_rows:
            QMessageBox.warning(self, "No Data", "No workers to export.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export Workers", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Worker ID", "Name", "Role", "Phone", "Email", "Address", "Salary (₹)", "Hire Date", "Status"])
                    writer.writerows(self.all_rows)
                QMessageBox.information(self, "Success", f"Workers exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}") 