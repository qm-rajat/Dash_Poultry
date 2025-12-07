# Dash Poultry - Farm Management System

A comprehensive desktop application for managing poultry farm operations, including batch management, feed/water logging, health tracking, worker management, financial analysis, and more.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Database Schema](#database-schema)
- [Module Documentation](#module-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

---

## Overview

**Dash Poultry** is a Python-based GUI application built with PyQt6 that provides an integrated solution for poultry farm management. It helps farmers and farm managers track:

- Chicken batches and their lifecycle
- Feed and water consumption
- Vaccination schedules and health records
- Mortality tracking and cause analysis
- Worker management and payroll
- Expense tracking and financial reporting
- Revenue and profit/loss analysis
- Data export and reporting capabilities

The application features a modern, user-friendly interface with real-time data updates, comprehensive analytics, and detailed financial reports.

---

## Features

### Core Modules

#### 1. **Dashboard**
- Real-time overview of farm performance
- Summary cards showing:
  - Total active batches
  - Feed and water usage
  - Profit and loss metrics
  - Quick action buttons for common tasks
- Live charts showing:
  - Feed/water usage trends
  - Profit/loss trends over time
- One-click access to key modules

#### 2. **Batch Management**
- **Add Batches**: Create new batches with details
  - Batch ID (unique identifier)
  - Number of chicks
  - Breed type (Broiler, Layer, etc.)
  - Date in and expected completion date
  - Mortality rate tracking
- **Edit Batches**: Modify batch information and ID (all related records update automatically)
- **Delete Batches**: Remove batches with confirmation
- **Search & Filter**: Search by batch ID, breed, or other criteria
- **Export**: Download batch data as CSV
- **Print**: Print batch table for records

#### 3. **Feed/Water Logs**
- Log daily feed consumption (in kg)
- Log daily water usage (in liters)
- Track consumption by batch
- View historical logs with date filters
- Edit or delete log entries
- Generate reports for analysis

#### 4. **Vaccination Tracker**
- Schedule and record vaccinations
- Track vaccination status (Scheduled, Completed, Cancelled, Postponed)
- Record vaccine types and dates
- Filter by batch or vaccination status
- Maintain vaccination history for audit trails
- Export vaccination records

#### 5. **Mortality Tracker**
- Record mortality events with:
  - Date and batch ID
  - Number of birds lost
  - Reason for mortality (disease, accident, natural causes, etc.)
- Track mortality trends and patterns
- Calculate mortality statistics and averages
- Analyze mortality by cause
- Export mortality data for analysis

#### 6. **Worker Management**
- Maintain employee database with:
  - Worker ID and name
  - Role/position (Farm Manager, Feeder, Cleaner, etc.)
  - Contact information (phone, email, address)
  - Salary and hire date
  - Employment status (Active, Inactive)
- Track active workers and total payroll
- Manage worker assignments
- Update worker information

#### 7. **Expenses Management**
- Record all farm expenses:
  - Date, category, and amount
  - Description and payment method
  - Payment tracking (Cash, Bank Transfer, UPI, etc.)
- Expense categories:
  - Feed, Medicine, Electricity, Water, Fuel
  - Equipment, Labor, Transport, Maintenance, Other
- Real-time expense summaries:
  - Total expenses
  - Monthly expenses
  - Average expense per record
- Filter by category and payment method
- Export expense records

#### 8. **Profit/Loss Analysis**
- Comprehensive financial dashboard showing:
  - Total revenue and expenses
  - Net profit calculation
  - Profit margin percentage
- **Charts & Visualizations**:
  - Revenue vs. Expenses trend chart
  - Monthly profit trend with color-coded bars
  - Expense breakdown by category
  - Revenue analysis by batch
- **Detailed Financial Breakdown**:
  - Category-wise revenue and expenses
  - Profit/loss per category
  - Color-coded profit indicators (green/red)
- Real-time updates when expense or revenue data changes

#### 9. **Export Module**
- Generate comprehensive reports
- Export data in multiple formats:
  - CSV files for spreadsheet analysis
  - PDF reports for documentation
  - Excel files for detailed analysis
- Customizable date ranges
- Multi-module data consolidation

#### 10. **Settings Module**
- Application preferences and configuration
- Theme selection (Light/Dark mode)
- Data backup and restore options
- Database maintenance utilities
- System information and logs

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 7 or later, macOS 10.12+, or Linux (Ubuntu 16.04+)
- **Python**: 3.8 or higher
- **RAM**: 2 GB minimum
- **Disk Space**: 500 MB for application and database
- **Display**: 1280x720 resolution or higher

### Recommended Requirements
- **OS**: Windows 10+, macOS 11+, or Ubuntu 20.04+
- **Python**: 3.10 or higher
- **RAM**: 4 GB or more
- **Disk Space**: 1 GB
- **Display**: 1920x1080 or higher

---

## Installation

### Step 1: Clone or Download Repository

```bash
git clone https://github.com/qm-rajat/Dash_Poultry.git
cd Dash_Poultry
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `PyQt6>=6.0` - GUI framework
- `bcrypt>=4.0` - Password hashing
- `pyqtgraph>=0.13` - Chart and graph plotting
- `matplotlib>=3.0` - Advanced plotting
- `reportlab>=4.0` - PDF generation
- `python-pptx>=0.6` - PowerPoint reports
- `openpyxl>=3.0` - Excel file handling
- `PyInstaller>=6.0` - Executable creation (optional)

### Step 4: Initialize Database

The database initializes automatically on first run. Sample data is included for testing.

```bash
python -c "from database.init_db import init_db; init_db()"
```

### Step 5: Run Application

```bash
python main.py
```

---

## Project Structure

```
Dash_Poultry/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── LICENSE                          # License file
│
├── database/
│   ├── __init__.py
│   ├── init_db.py                  # Database initialization & schema
│   ├── dash_poultry.db             # SQLite database file
│   └── __pycache__/
│
├── ui/
│   ├── __init__.py
│   ├── login_window.py             # Login interface
│   ├── main_window.py              # Main application window
│   └── __pycache__/
│
├── modules/
│   ├── __init__.py
│   ├── dashboard.py                # Dashboard module
│   ├── batch_management.py         # Batch management module
│   ├── feed_water_logs.py          # Feed/Water logging module
│   ├── vaccination_tracker.py      # Vaccination tracking module
│   ├── mortality_tracker.py        # Mortality tracking module
│   ├── workers_management.py       # Worker management module
│   ├── expenses_management.py      # Expense tracking module
│   ├── profit_loss_analysis.py     # Financial analysis module
│   ├── export_module.py            # Data export module
│   ├── settings_module.py          # Settings module
│   └── __pycache__/
│
├── ui/
│   ├── __init__.py
│   ├── notification_manager.py     # Notification system
│   └── __pycache__/
│
├── utils/
│   ├── __init__.py
│   ├── data_manager.py             # Global data communication
│   ├── notification_manager.py     # Notification handling
│   └── __pycache__/
│
└── resources/
    ├── __init__.py
    ├── logo.png                    # Application logo
    ├── icons.qrc                   # Icon resources
    ├── theme_light.qss             # Light theme stylesheet
    └── theme_dark.qss              # Dark theme stylesheet
```

---

## Usage Guide

### Getting Started

1. **Login**
   - Default username: `a`
   - Default password: `a`
   - Change password after first login (recommended)

2. **Navigate Modules**
   - Use sidebar to switch between modules
   - Click module name or icon to access
   - Dashboard provides quick access buttons

### Common Workflows

#### Adding a New Batch

1. Go to **Batches** module
2. Click **"Add Batch"** button
3. Fill in batch details:
   - Unique Batch ID (e.g., B001)
   - Number of chicks
   - Breed type
   - Date received
   - Expected completion date
   - Initial mortality rate estimate
4. Click **OK** to save

#### Logging Feed/Water

1. Go to **Feed/Water** module
2. Click **"Add Log"** button
3. Select batch ID
4. Choose date
5. Enter feed quantity (kg) and/or water (liters)
6. Click **OK** to save

#### Recording Expenses

1. Go to **Expenses** module
2. Click **"Add Expense"** button
3. Select date and category
4. Enter amount and description
5. Choose payment method
6. Click **OK** to save
7. Profit/Loss page updates automatically

#### Tracking Vaccination

1. Go to **Vaccination** module
2. Click **"Add Vaccination"** button
3. Select batch
4. Enter vaccine name
5. Set status (Scheduled/Completed)
6. Click **OK** to save

#### Viewing Financial Reports

1. Go to **Profit/Loss Analysis** module
2. View summary cards with totals
3. Analyze charts showing trends
4. Review detailed breakdown table
5. Make decisions based on data

### Data Management

#### Editing Records
1. Select the record from table
2. Click **"Edit"** button
3. Modify details
4. Click **OK** to save

#### Deleting Records
1. Select the record
2. Click **"Delete"** button
3. Confirm deletion when prompted

#### Exporting Data
1. In any module, click **"Export CSV"**
2. Choose file location and name
3. File saves with timestamp

#### Searching Records
1. Use search box (if available in module)
2. Type keywords to filter
3. Results update in real-time

---

## Database Schema

### Tables Overview

#### `admin`
```
id (INT, PK) | username (TEXT) | password (TEXT, hashed)
```
- Stores admin login credentials
- Password hashed using bcrypt

#### `batches`
```
id (INT, PK) | batch_id (TEXT, UNIQUE) | num_chicks (INT) | breed (TEXT)
| date_in (TEXT) | expected_out (TEXT) | mortality_rate (REAL)
```
- Core batch information
- Linked to all operational records

#### `feed_logs`
```
id (INT, PK) | batch_id (TEXT, FK) | date (TEXT) | quantity_kg (REAL)
```
- Daily feed consumption per batch
- Used for trend analysis

#### `water_logs`
```
id (INT, PK) | batch_id (TEXT, FK) | date (TEXT) | quantity_l (REAL)
```
- Daily water usage per batch

#### `vaccinations`
```
id (INT, PK) | batch_id (TEXT, FK) | date (TEXT) | vaccine (TEXT) | status (TEXT)
```
- Vaccination records and schedules
- Statuses: Scheduled, Completed, Cancelled, Postponed

#### `mortality`
```
id (INT, PK) | batch_id (TEXT, FK) | date (TEXT) | count (INT) | reason (TEXT)
```
- Mortality events with reason tracking
- Used for trend and cause analysis

#### `expenses`
```
id (INT, PK) | date (TEXT) | category (TEXT) | amount (REAL)
| description (TEXT) | payment_method (TEXT)
```
- All expense records
- Category and payment method tracking

#### `revenue`
```
id (INT, PK) | date (TEXT) | batch_id (TEXT) | amount (REAL)
```
- Revenue from batch sales
- Linked to batch for profitability analysis

#### `workers`
```
id (INT, PK) | worker_id (TEXT, UNIQUE) | name (TEXT) | role (TEXT)
| phone (TEXT) | email (TEXT) | address (TEXT) | salary (REAL)
| hire_date (TEXT) | status (TEXT)
```
- Employee database with compensation

---

## Module Documentation

### Core Module: Data Manager (`utils/data_manager.py`)

Central hub for cross-module communication using PyQt6 signals.

**Available Signals:**
- `batch_data_changed` - Emitted when batch data is modified
- `feed_water_data_changed` - Emitted when feed/water logs change
- `vaccination_data_changed` - Emitted when vaccinations change
- `mortality_data_changed` - Emitted when mortality records change
- `worker_data_changed` - Emitted when worker data changes
- `expense_data_changed` - Emitted when expenses change
- `revenue_data_changed` - Emitted when revenue changes
- `data_refresh_needed` - General refresh signal

**Usage Example:**
```python
from utils.data_manager import data_manager

# Connect to signal
data_manager.batch_data_changed.connect(my_refresh_method)

# Emit signal
data_manager.notify_batch_change()
```

### Authentication

**Login Mechanism:**
- Bcrypt password hashing (salted)
- Session-based access control
- Default credentials provided for setup

**Security Features:**
- Password validation on login
- Encrypted password storage
- Optional: Database encryption with SQLCipher

### Theming

**Available Themes:**
- Light mode (default)
- Dark mode

**Theme Files:**
- `resources/theme_light.qss` - Light theme stylesheet
- `resources/theme_dark.qss` - Dark theme stylesheet

**Toggle Theme:**
- Click "Toggle Theme" button in top-right corner
- Settings persist across sessions

---

## Configuration

### Database Configuration

Edit `database/init_db.py`:

```python
DB_PATH = os.path.join(os.path.dirname(__file__), 'dash_poultry.db')
ADMIN_USERNAME = 'a'
ADMIN_PASSWORD = 'a'
```

### Application Settings

Edit `ui/main_window.py` for:
- Default window size (1280x720)
- Module order in sidebar
- Notification settings

### Data Manager Configuration

Edit `utils/data_manager.py` to add:
- Custom signals
- New data retrieval methods
- Cache management

---

## Troubleshooting

### Common Issues

#### **Issue: "No module named 'PyQt6'"**
```bash
# Solution: Install PyQt6
pip install PyQt6
```

#### **Issue: Database locked**
- Ensure only one instance of application is running
- Check for corrupted database file
- Delete `dash_poultry.db` and restart (loses data)

#### **Issue: Charts not displaying**
- Verify `pyqtgraph` installation: `pip install pyqtgraph`
- Check for sufficient data in database
- Ensure date formats are correct

#### **Issue: Profit/Loss not updating**
- Ensure expense and revenue records have valid dates
- Check that data_manager signals are connected
- Verify notification methods are being called
- Dates must be in `YYYY-MM-DD` format

#### **Issue: Application crashes on startup**
- Clear `__pycache__` directories:
  ```bash
  find . -type d -name __pycache__ -exec rm -r {} +
  ```
- Reinstall dependencies:
  ```bash
  pip install --force-reinstall -r requirements.txt
  ```

#### **Issue: SQLite database errors**
- Run database check:
  ```python
  python -c "from database.init_db import get_connection; conn = get_connection(); print('Database OK')"
  ```
- Backup existing database before repair attempts

### Debugging Tips

1. **Enable Debug Mode** - Check terminal output for error messages
2. **Check Database Directly** - Use SQLite browser to inspect tables
3. **Monitor Signals** - Add debug prints in data_manager connections
4. **Verify Paths** - Ensure all file paths are correct and accessible

---

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Predictive mortality analysis using machine learning
   - Feed efficiency optimization recommendations
   - Seasonal trend analysis

2. **Mobile App**
   - Mobile interface for field logging
   - Real-time notifications
   - Offline mode with sync

3. **Cloud Integration**
   - Cloud backup and sync
   - Multi-user collaboration
   - Remote access

4. **Integration Capabilities**
   - API for third-party apps
   - IoT sensor integration
   - Automated data collection from sensors

5. **Enhanced Reporting**
   - Custom report generation
   - Email report scheduling
   - Multi-farm support

6. **Role-Based Access**
   - Multiple user types (Admin, Manager, Worker)
   - Granular permission controls
   - Activity audit logs

7. **Compliance & Certification**
   - Organic farming compliance tracking
   - Certification readiness reports
   - Regulatory requirement checklists

### Known Limitations

- Single-farm support (no multi-farm management yet)
- Single-user session at a time
- Limited mobile support
- Manual revenue entry (auto-calculation not yet implemented)
- Reports export limited to CSV and basic PDF

---

## Performance Optimization

### Database Optimization

```sql
-- Run periodically to optimize database
VACUUM;
ANALYZE;
```

### Recommended Practices

1. **Regular Backups**
   - Backup database weekly
   - Store backups in multiple locations
   - Test restore procedures

2. **Data Cleanup**
   - Archive old records annually
   - Delete test data before production use
   - Monitor database file size

3. **Cache Management**
   - Clear application cache monthly
   - Restart application weekly
   - Monitor memory usage during long sessions

---

## Support & Contact

### Getting Help

- **Documentation**: Refer to module-specific guides above
- **Troubleshooting**: See Troubleshooting section
- **Bug Reports**: File issues with details and screenshots
- **Feature Requests**: Suggest enhancements via issue tracker

### License

This project is licensed under the MIT License - see LICENSE file for details.

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes and test thoroughly
4. Submit pull request with description

---

## Additional Resources

- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **SQLite Documentation**: https://www.sqlite.org/docs.html
- **Python Best Practices**: https://pep8.org/
- **Git Workflow Guide**: https://git-scm.com/book/en/v2

---

## Version History

### v1.0.0 (Current)
- Initial release
- All core modules functional
- Basic reporting and export
- Light/Dark theme support
- Database initialization and sample data

### Upcoming
- v1.1.0 - Enhanced charts and analytics
- v1.2.0 - Mobile app integration
- v2.0.0 - Multi-farm support

---

**Last Updated**: December 2024
**Maintained By**: Development Team
**Status**: Active Development
