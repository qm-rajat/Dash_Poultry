from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QLabel, QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox, 
                             QLineEdit, QFileDialog, QAbstractItemView, QHeaderView, QTextEdit, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection

class ExpenseDialog(QDialog):
    def __init__(self, parent=None, expense=None):
        super().__init__(parent)
        self.setWindowTitle("Expense Details")
        self.setModal(True)
        self.resize(400, 350)
        layout = QFormLayout(self)
        
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())
        self.category = QComboBox()
        self.category.addItems(["Feed", "Medicine", "Electricity", "Water", "Fuel", "Equipment", "Labor", "Transport", "Maintenance", "Other"])
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0, 1000000)
        self.amount.setDecimals(2)
        self.amount.setSuffix(" ₹")
        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        self.description.setPlaceholderText("Enter detailed description of the expense")
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card", "Other"])
        
        layout.addRow("Date", self.date)
        layout.addRow("Category", self.category)
        layout.addRow("Amount (₹)", self.amount)
        layout.addRow("Description", self.description)
        layout.addRow("Payment Method", self.payment_method)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
        if expense:
            self.date.setDate(QDate.fromString(expense[0], 'yyyy-MM-dd'))
            self.category.setCurrentText(expense[1])
            self.amount.setValue(float(expense[2]))
            self.description.setPlainText(expense[3])
            self.payment_method.setCurrentText(expense[4])

    def get_data(self):
        return {
            'date': self.date.date().toString('yyyy-MM-dd'),
            'category': self.category.currentText(),
            'amount': self.amount.value(),
            'description': self.description.toPlainText().strip(),
            'payment_method': self.payment_method.currentText()
        }

class ExpensesManagementWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.all_rows = []  # Store all rows for filtering
        self.init_ui()
        self.load_expenses()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("<b>Expenses Management</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Search and filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by description, category, etc...")
        self.search_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "Feed", "Medicine", "Electricity", "Water", "Fuel", "Equipment", "Labor", "Transport", "Maintenance", "Other"])
        self.category_filter.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.category_filter)
        
        filter_layout.addWidget(QLabel("Payment:"))
        self.payment_filter = QComboBox()
        self.payment_filter.addItems(["All", "Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card", "Other"])
        self.payment_filter.currentIndexChanged.connect(self.filter_table)
        filter_layout.addWidget(self.payment_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        self.total_expenses_label = QLabel("Total Expenses: ₹0")
        self.total_expenses_label.setStyleSheet("font-weight: bold; color: #dc2626;")
        stats_layout.addWidget(self.total_expenses_label)
        
        self.monthly_expenses_label = QLabel("This Month: ₹0")
        self.monthly_expenses_label.setStyleSheet("font-weight: bold; color: #ea580c;")
        stats_layout.addWidget(self.monthly_expenses_label)
        
        self.avg_expense_label = QLabel("Avg per Record: ₹0")
        self.avg_expense_label.setStyleSheet("font-weight: bold; color: #059669;")
        stats_layout.addWidget(self.avg_expense_label)
        
        self.total_records_label = QLabel("Total Records: 0")
        self.total_records_label.setStyleSheet("font-weight: bold; color: #059669;")
        stats_layout.addWidget(self.total_records_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Amount (₹)", "Description", "Payment Method"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Expense")
        self.add_btn.clicked.connect(self.add_expense)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Expense")
        self.edit_btn.clicked.connect(self.edit_expense)
        btn_layout.addWidget(self.edit_btn)
        
        self.del_btn = QPushButton("Delete Expense")
        self.del_btn.clicked.connect(self.delete_expense)
        btn_layout.addWidget(self.del_btn)
        
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def load_expenses(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT date, category, amount, description, payment_method FROM expenses ORDER BY date DESC')
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
                if col_idx == 2:  # Amount column - make it stand out
                    item.setBackground(Qt.GlobalColor.lightGray)
                elif col_idx == 1:  # Category column - color code
                    if value == "Feed":
                        item.setBackground(Qt.GlobalColor.green)
                    elif value == "Medicine":
                        item.setBackground(Qt.GlobalColor.red)
                    elif value == "Electricity":
                        item.setBackground(Qt.GlobalColor.yellow)
                    elif value == "Labor":
                        item.setBackground(Qt.GlobalColor.blue)
                self.table.setItem(row_idx, col_idx, item)

    def update_stats(self, rows):
        if not rows:
            self.total_expenses_label.setText("Total Expenses: ₹0")
            self.monthly_expenses_label.setText("This Month: ₹0")
            self.avg_expense_label.setText("Avg per Record: ₹0")
            self.total_records_label.setText("Total Records: 0")
            return
        
        total_expenses = sum(row[2] for row in rows if row[2] is not None)
        total_records = len(rows)
        avg_expense = total_expenses / total_records if total_records > 0 else 0
        
        # Calculate monthly expenses
        current_month = QDate.currentDate().toString('yyyy-MM')
        monthly_expenses = sum(row[2] for row in rows if row[2] is not None and row[0].startswith(current_month))
        
        self.total_expenses_label.setText(f"Total Expenses: ₹{total_expenses:,.2f}")
        self.monthly_expenses_label.setText(f"This Month: ₹{monthly_expenses:,.2f}")
        self.avg_expense_label.setText(f"Avg per Record: ₹{avg_expense:,.2f}")
        self.total_records_label.setText(f"Total Records: {total_records}")

    def filter_table(self):
        text = self.search_input.text().lower()
        category_filter = self.category_filter.currentText()
        payment_filter = self.payment_filter.currentText()
        
        filtered = []
        for row in self.all_rows:
            # Text search
            text_match = not text or any(text in str(cell).lower() for cell in row)
            # Category filter
            category_match = category_filter == "All" or row[1] == category_filter
            # Payment method filter
            payment_match = payment_filter == "All" or row[4] == payment_filter
            
            if text_match and category_match and payment_match:
                filtered.append(row)
        
        self.populate_table(filtered)
        self.update_stats(filtered)

    def add_expense(self):
        dialog = ExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['amount'] <= 0:
                QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0.")
                return
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO expenses (date, category, amount, description, payment_method) 
                             VALUES (?, ?, ?, ?, ?)''',
                    (data['date'], data['category'], data['amount'], data['description'], data['payment_method']))
                conn.commit()
                QMessageBox.information(self, "Success", "Expense added successfully.")
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add expense: {e}")
            finally:
                conn.close()

    def edit_expense(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Expense", "Please select an expense to edit.")
            return
        expense = [self.table.item(row, i).text() for i in range(5)]
        dialog = ExpenseDialog(self, expense=expense)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('''UPDATE expenses SET category=?, amount=?, description=?, payment_method=? 
                             WHERE date=? AND category=? AND amount=? AND description=? AND payment_method=?''',
                    (data['category'], data['amount'], data['description'], data['payment_method'],
                     expense[0], expense[1], expense[2], expense[3], expense[4]))
                conn.commit()
                QMessageBox.information(self, "Success", "Expense updated successfully.")
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update expense: {e}")
            finally:
                conn.close()

    def delete_expense(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Expense", "Please select an expense to delete.")
            return
        expense = [self.table.item(row, i).text() for i in range(5)]
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete this expense?\n\nDate: {expense[0]}\nCategory: {expense[1]}\nAmount: ₹{expense[2]}\nDescription: {expense[3]}",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            c = conn.cursor()
            try:
                c.execute('DELETE FROM expenses WHERE date=? AND category=? AND amount=? AND description=? AND payment_method=?',
                    (expense[0], expense[1], expense[2], expense[3], expense[4]))
                conn.commit()
                QMessageBox.information(self, "Success", "Expense deleted successfully.")
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete expense: {e}")
            finally:
                conn.close()

    def export_csv(self):
        if not self.all_rows:
            QMessageBox.warning(self, "No Data", "No expenses to export.")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Export Expenses", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Date", "Category", "Amount (₹)", "Description", "Payment Method"])
                    writer.writerows(self.all_rows)
                QMessageBox.information(self, "Success", f"Expenses exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}") 