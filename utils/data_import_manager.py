import pandas as pd
import csv
import json
import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
                             QMessageBox, QLabel, QProgressBar, QComboBox, QTableWidget, 
                             QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
                             QTextEdit, QCheckBox, QGroupBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.init_db import get_connection
from utils.notification_manager import notification_manager

class ImportWorker(QThread):
    """Background worker for data import"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, file_path, module_type, mapping, options):
        super().__init__()
        self.file_path = file_path
        self.module_type = module_type
        self.mapping = mapping
        self.options = options
    
    def run(self):
        try:
            self.status.emit("Reading file...")
            self.progress.emit(10)
            
            # Read file based on extension
            if self.file_path.endswith('.csv'):
                df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format")
            
            self.status.emit("Processing data...")
            self.progress.emit(30)
            
            # Map columns
            mapped_data = []
            for _, row in df.iterrows():
                mapped_row = {}
                for db_column, file_column in self.mapping.items():
                    if file_column in row:
                        mapped_row[db_column] = row[file_column]
                mapped_data.append(mapped_row)
            
            self.status.emit("Importing to database...")
            self.progress.emit(60)
            
            # Import to database
            conn = get_connection()
            c = conn.cursor()
            
            success_count = 0
            error_count = 0
            
            for row_data in mapped_data:
                try:
                    if self.module_type == 'batches':
                        self.import_batch(c, row_data)
                    elif self.module_type == 'feed_water':
                        self.import_feed_water(c, row_data)
                    elif self.module_type == 'vaccinations':
                        self.import_vaccination(c, row_data)
                    elif self.module_type == 'mortality':
                        self.import_mortality(c, row_data)
                    elif self.module_type == 'workers':
                        self.import_worker(c, row_data)
                    elif self.module_type == 'expenses':
                        self.import_expense(c, row_data)
                    elif self.module_type == 'revenue':
                        self.import_revenue(c, row_data)
                    
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Error importing row: {e}")
            
            conn.commit()
            conn.close()
            
            self.progress.emit(100)
            self.status.emit("Import completed")
            
            result_message = f"Import completed: {success_count} records imported, {error_count} errors"
            self.finished.emit(True, result_message)
            
        except Exception as e:
            self.finished.emit(False, f"Import failed: {str(e)}")
    
    def import_batch(self, cursor, data):
        cursor.execute('''
            INSERT INTO batches (batch_id, num_chicks, breed, date_in, expected_out, mortality_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('batch_id'),
            data.get('num_chicks', 0),
            data.get('breed', ''),
            data.get('date_in', ''),
            data.get('expected_out', ''),
            data.get('mortality_rate', 0.0)
        ))
    
    def import_feed_water(self, cursor, data):
        if data.get('feed_kg', 0) > 0:
            cursor.execute('''
                INSERT INTO feed_logs (batch_id, date, quantity_kg)
                VALUES (?, ?, ?)
            ''', (data.get('batch_id'), data.get('date'), data.get('feed_kg', 0)))
        
        if data.get('water_l', 0) > 0:
            cursor.execute('''
                INSERT INTO water_logs (batch_id, date, quantity_l)
                VALUES (?, ?, ?)
            ''', (data.get('batch_id'), data.get('date'), data.get('water_l', 0)))
    
    def import_vaccination(self, cursor, data):
        cursor.execute('''
            INSERT INTO vaccinations (batch_id, vaccine_type, scheduled_date, status, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('batch_id'),
            data.get('vaccine_type', ''),
            data.get('scheduled_date', ''),
            data.get('status', 'Scheduled'),
            data.get('notes', '')
        ))
    
    def import_mortality(self, cursor, data):
        cursor.execute('''
            INSERT INTO mortality (batch_id, date, count, reason)
            VALUES (?, ?, ?, ?)
        ''', (
            data.get('batch_id'),
            data.get('date', ''),
            data.get('count', 0),
            data.get('reason', '')
        ))
    
    def import_worker(self, cursor, data):
        cursor.execute('''
            INSERT INTO workers (name, role, phone, email, salary, hire_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name', ''),
            data.get('role', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('salary', 0),
            data.get('hire_date', ''),
            data.get('status', 'Active')
        ))
    
    def import_expense(self, cursor, data):
        cursor.execute('''
            INSERT INTO expenses (category, amount, date, description, payment_method)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('category', ''),
            data.get('amount', 0),
            data.get('date', ''),
            data.get('description', ''),
            data.get('payment_method', 'Cash')
        ))
    
    def import_revenue(self, cursor, data):
        cursor.execute('''
            INSERT INTO revenue (batch_id, amount, date, source, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('batch_id', ''),
            data.get('amount', 0),
            data.get('date', ''),
            data.get('source', ''),
            data.get('description', '')
        ))

class ColumnMappingDialog(QDialog):
    """Dialog for mapping CSV/Excel columns to database fields"""
    
    def __init__(self, file_columns, module_type, parent=None):
        super().__init__(parent)
        self.file_columns = file_columns
        self.module_type = module_type
        self.mapping = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Column Mapping")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Map your file columns to database fields:")
        instructions.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Mapping form
        form_layout = QFormLayout()
        
        # Get required fields for the module
        required_fields = self.get_required_fields()
        
        self.mapping_widgets = {}
        for db_field, field_info in required_fields.items():
            combo = QComboBox()
            combo.addItem("-- Select Column --")
            combo.addItems(self.file_columns)
            form_layout.addRow(f"{field_info['label']} ({'Required' if field_info['required'] else 'Optional'})", combo)
            self.mapping_widgets[db_field] = combo
        
        layout.addLayout(form_layout)
        
        # Preview section
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_required_fields(self):
        """Get required fields for the selected module"""
        field_mappings = {
            'batches': {
                'batch_id': {'label': 'Batch ID', 'required': True},
                'num_chicks': {'label': 'Number of Chicks', 'required': True},
                'breed': {'label': 'Breed', 'required': True},
                'date_in': {'label': 'Date In', 'required': True},
                'expected_out': {'label': 'Expected Out', 'required': False},
                'mortality_rate': {'label': 'Mortality Rate', 'required': False}
            },
            'feed_water': {
                'batch_id': {'label': 'Batch ID', 'required': True},
                'date': {'label': 'Date', 'required': True},
                'feed_kg': {'label': 'Feed (kg)', 'required': False},
                'water_l': {'label': 'Water (L)', 'required': False}
            },
            'vaccinations': {
                'batch_id': {'label': 'Batch ID', 'required': True},
                'vaccine_type': {'label': 'Vaccine Type', 'required': True},
                'scheduled_date': {'label': 'Scheduled Date', 'required': True},
                'status': {'label': 'Status', 'required': False},
                'notes': {'label': 'Notes', 'required': False}
            },
            'mortality': {
                'batch_id': {'label': 'Batch ID', 'required': True},
                'date': {'label': 'Date', 'required': True},
                'count': {'label': 'Count', 'required': True},
                'reason': {'label': 'Reason', 'required': False}
            },
            'workers': {
                'name': {'label': 'Name', 'required': True},
                'role': {'label': 'Role', 'required': True},
                'phone': {'label': 'Phone', 'required': False},
                'email': {'label': 'Email', 'required': False},
                'salary': {'label': 'Salary', 'required': True},
                'hire_date': {'label': 'Hire Date', 'required': True},
                'status': {'label': 'Status', 'required': False}
            },
            'expenses': {
                'category': {'label': 'Category', 'required': True},
                'amount': {'label': 'Amount', 'required': True},
                'date': {'label': 'Date', 'required': True},
                'description': {'label': 'Description', 'required': False},
                'payment_method': {'label': 'Payment Method', 'required': False}
            },
            'revenue': {
                'batch_id': {'label': 'Batch ID', 'required': True},
                'amount': {'label': 'Amount', 'required': True},
                'date': {'label': 'Date', 'required': True},
                'source': {'label': 'Source', 'required': False},
                'description': {'label': 'Description', 'required': False}
            }
        }
        
        return field_mappings.get(self.module_type, {})
    
    def get_mapping(self):
        """Get the column mapping"""
        mapping = {}
        for db_field, combo in self.mapping_widgets.items():
            if combo.currentText() != "-- Select Column --":
                mapping[db_field] = combo.currentText()
        return mapping

class DataImportWidget(QWidget):
    """Widget for data import functionality"""
    
    def __init__(self):
        super().__init__()
        self.import_worker = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("<b>Data Import & Sync</b>")
        title.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Import section
        import_group = QGroupBox("Import Data")
        import_layout = QVBoxLayout(import_group)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Select File:"))
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #666; font-style: italic;")
        file_layout.addWidget(self.file_path_label)
        file_layout.addStretch()
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        import_layout.addLayout(file_layout)
        
        # Module selection
        module_layout = QHBoxLayout()
        module_layout.addWidget(QLabel("Import to Module:"))
        self.module_combo = QComboBox()
        self.module_combo.addItems([
            "Batches", "Feed/Water Logs", "Vaccinations", "Mortality", 
            "Workers", "Expenses", "Revenue"
        ])
        module_layout.addWidget(self.module_combo)
        module_layout.addStretch()
        import_layout.addLayout(module_layout)
        
        # Import options
        options_layout = QHBoxLayout()
        self.skip_duplicates = QCheckBox("Skip Duplicates")
        self.skip_duplicates.setChecked(True)
        options_layout.addWidget(self.skip_duplicates)
        
        self.update_existing = QCheckBox("Update Existing Records")
        options_layout.addWidget(self.update_existing)
        options_layout.addStretch()
        import_layout.addLayout(options_layout)
        
        # Import button
        self.import_btn = QPushButton("Start Import")
        self.import_btn.clicked.connect(self.start_import)
        self.import_btn.setEnabled(False)
        import_layout.addWidget(self.import_btn)
        
        layout.addWidget(import_group)
        
        # Progress section
        progress_group = QGroupBox("Import Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to import")
        self.status_label.setStyleSheet("color: #666;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Export section
        export_group = QGroupBox("Export Data")
        export_layout = QVBoxLayout(export_group)
        
        export_btn_layout = QHBoxLayout()
        export_btn_layout.addWidget(QLabel("Export Module:"))
        self.export_module_combo = QComboBox()
        self.export_module_combo.addItems([
            "Batches", "Feed/Water Logs", "Vaccinations", "Mortality", 
            "Workers", "Expenses", "Revenue", "All Data"
        ])
        export_btn_layout.addWidget(self.export_module_combo)
        
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.export_data)
        export_btn_layout.addWidget(self.export_btn)
        export_btn_layout.addStretch()
        export_layout.addLayout(export_btn_layout)
        
        layout.addWidget(export_group)
        
        # Sync section
        sync_group = QGroupBox("Data Sync")
        sync_layout = QVBoxLayout(sync_group)
        
        sync_btn_layout = QHBoxLayout()
        self.backup_btn = QPushButton("Create Backup")
        self.backup_btn.clicked.connect(self.create_backup)
        sync_btn_layout.addWidget(self.backup_btn)
        
        self.restore_btn = QPushButton("Restore from Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        sync_btn_layout.addWidget(self.restore_btn)
        
        self.sync_btn = QPushButton("Sync with Cloud")
        self.sync_btn.clicked.connect(self.sync_with_cloud)
        sync_btn_layout.addWidget(self.sync_btn)
        sync_btn_layout.addStretch()
        sync_layout.addLayout(sync_btn_layout)
        
        layout.addWidget(sync_group)
        layout.addStretch()
    
    def browse_file(self):
        """Browse for import file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Import File", "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path = file_path
            self.import_btn.setEnabled(True)
    
    def start_import(self):
        """Start the import process"""
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, "No File", "Please select a file to import.")
            return
        
        # Get module type
        module_map = {
            "Batches": "batches",
            "Feed/Water Logs": "feed_water",
            "Vaccinations": "vaccinations",
            "Mortality": "mortality",
            "Workers": "workers",
            "Expenses": "expenses",
            "Revenue": "revenue"
        }
        
        module_type = module_map[self.module_combo.currentText()]
        
        # Read file to get columns
        try:
            if self.file_path.endswith('.csv'):
                df = pd.read_csv(self.file_path)
            else:
                df = pd.read_excel(self.file_path)
            
            columns = df.columns.tolist()
            
            # Show mapping dialog
            mapping_dialog = ColumnMappingDialog(columns, module_type, self)
            if mapping_dialog.exec() == QDialog.DialogCode.Accepted:
                mapping = mapping_dialog.get_mapping()
                
                if not mapping:
                    QMessageBox.warning(self, "No Mapping", "Please map at least one column.")
                    return
                
                # Start import
                options = {
                    'skip_duplicates': self.skip_duplicates.isChecked(),
                    'update_existing': self.update_existing.isChecked()
                }
                
                self.import_worker = ImportWorker(self.file_path, module_type, mapping, options)
                self.import_worker.progress.connect(self.progress_bar.setValue)
                self.import_worker.status.connect(self.status_label.setText)
                self.import_worker.finished.connect(self.import_finished)
                
                self.import_btn.setEnabled(False)
                self.browse_btn.setEnabled(False)
                self.import_worker.start()
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file: {str(e)}")
    
    def import_finished(self, success, message):
        """Handle import completion"""
        self.import_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Import Success", message)
            notification_manager.show_success("Import Completed", message)
        else:
            QMessageBox.critical(self, "Import Failed", message)
            notification_manager.show_error("Import Failed", message)
    
    def export_data(self):
        """Export data to CSV"""
        module = self.export_module_combo.currentText()
        
        if module == "All Data":
            self.export_all_data()
        else:
            self.export_module_data(module)
    
    def export_module_data(self, module):
        """Export specific module data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export {module}", f"{module.lower().replace('/', '_')}.csv", 
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            conn = get_connection()
            
            if module == "Batches":
                df = pd.read_sql_query("SELECT * FROM batches", conn)
            elif module == "Feed/Water Logs":
                df = pd.read_sql_query("""
                    SELECT f.batch_id, f.date, f.quantity_kg as feed_kg, w.quantity_l as water_l
                    FROM feed_logs f
                    LEFT JOIN water_logs w ON f.batch_id = w.batch_id AND f.date = w.date
                """, conn)
            elif module == "Vaccinations":
                df = pd.read_sql_query("SELECT * FROM vaccinations", conn)
            elif module == "Mortality":
                df = pd.read_sql_query("SELECT * FROM mortality", conn)
            elif module == "Workers":
                df = pd.read_sql_query("SELECT * FROM workers", conn)
            elif module == "Expenses":
                df = pd.read_sql_query("SELECT * FROM expenses", conn)
            elif module == "Revenue":
                df = pd.read_sql_query("SELECT * FROM revenue", conn)
            
            df.to_csv(file_path, index=False)
            conn.close()
            
            QMessageBox.information(self, "Export Success", f"{module} data exported successfully.")
            notification_manager.show_success("Export Completed", f"{module} data exported to {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def export_all_data(self):
        """Export all data to a zip file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export All Data", "dash_poultry_data.zip", 
            "ZIP Files (*.zip)"
        )
        
        if not file_path:
            return
        
        try:
            import zipfile
            import tempfile
            
            with zipfile.ZipFile(file_path, 'w') as zipf:
                conn = get_connection()
                
                tables = ['batches', 'feed_logs', 'water_logs', 'vaccinations', 
                         'mortality', 'workers', 'expenses', 'revenue']
                
                for table in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    
                    # Create temporary CSV file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
                        df.to_csv(tmp.name, index=False)
                        zipf.write(tmp.name, f"{table}.csv")
                        os.unlink(tmp.name)
                
                conn.close()
            
            QMessageBox.information(self, "Export Success", "All data exported successfully.")
            notification_manager.show_success("Export Completed", "All data exported successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def create_backup(self):
        """Create database backup"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create Backup", "dash_poultry_backup.db", 
            "Database Files (*.db)"
        )
        
        if not file_path:
            return
        
        try:
            import shutil
            shutil.copy2('dash_poultry.db', file_path)
            
            QMessageBox.information(self, "Backup Created", "Database backup created successfully.")
            notification_manager.show_success("Backup Created", "Database backup saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup: {str(e)}")
    
    def restore_backup(self):
        """Restore database from backup"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Backup", "", 
            "Database Files (*.db)"
        )
        
        if not file_path:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Restore", 
            "This will replace all current data. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                shutil.copy2(file_path, 'dash_poultry.db')
                
                QMessageBox.information(self, "Restore Success", "Database restored successfully.")
                notification_manager.show_success("Restore Completed", "Database restored successfully.")
                
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore backup: {str(e)}")
    
    def sync_with_cloud(self):
        """Sync with cloud storage (placeholder)"""
        QMessageBox.information(
            self, "Cloud Sync", 
            "Cloud sync feature is not implemented yet. This would sync data with cloud storage services."
        ) 