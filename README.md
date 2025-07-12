# 🐔 Dash Poultry - Farm Management System

A comprehensive, modern desktop application for poultry farm management built with PyQt6 and SQLite.

## ✨ Features

### 🏠 **Core Modules**
- **Dashboard** - Real-time overview with customizable widgets
- **Batch Management** - Complete lifecycle tracking
- **Feed/Water Logs** - Consumption monitoring and analysis
- **Vaccination Tracker** - Health management and scheduling
- **Mortality Tracker** - Loss monitoring and analysis
- **Workers Management** - Employee and payroll management
- **Expenses Management** - Financial tracking and budgeting
- **Profit/Loss Analysis** - Financial insights and reporting
- **Analytics** - Cross-module insights and predictions
- **Export Module** - Data export in multiple formats
- **Settings** - Application configuration and customization

### 🚀 **Advanced Features**
- **Contextual Navigation** - Smart cross-module data sharing
- **Real-time Analytics** - Performance metrics and insights
- **Automated Alerts** - Intelligent monitoring and notifications
- **Data Import/Export** - CSV/Excel support with mapping
- **Customizable Dashboard** - Drag-and-drop widget system
- **System Tray Integration** - Background notifications
- **Encrypted Database** - Secure data storage
- **Theme Support** - Light and dark modes

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Dash_Poultry
   ```

2. **Run the installation script**
   ```bash
   python install.py
   ```

3. **Or install manually**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📋 Requirements

```
PyQt6>=6.4.0
pyqtgraph>=0.13.0
pandas>=1.5.0
numpy>=1.24.0
sqlcipher3-binary>=0.4.0
openpyxl>=3.0.0
reportlab>=3.6.0
```

## 🏗️ Project Structure

```
Dash_Poultry/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── install.py             # Installation script
├── README.md              # This file
├── modules/               # Application modules
│   ├── dashboard.py       # Dashboard with analytics
│   ├── batch_management.py
│   ├── feed_water_logs.py
│   ├── vaccination_tracker.py
│   ├── mortality_tracker.py
│   ├── workers_management.py
│   ├── expenses_management.py
│   ├── profit_loss_analysis.py
│   ├── analytics_module.py
│   ├── export_module.py
│   └── settings_module.py
├── ui/                    # User interface
│   ├── login_window.py
│   └── main_window.py
├── utils/                 # Utility functions
│   ├── data_manager.py
│   ├── notification_manager.py
│   ├── alert_manager.py
│   ├── context_manager.py
│   ├── data_import_manager.py
│   └── dashboard_customizer.py
├── database/              # Database management
│   └── init_db.py
├── resources/             # Application resources
│   ├── theme_light.qss
│   ├── theme_dark.qss
│   └── icons/
├── exports/               # Exported data
├── backups/               # Database backups
└── logs/                  # Application logs
```

## 🎯 Key Features Explained

### 📊 **Smart Analytics**
- **Performance Metrics**: Feed conversion ratios, growth trends
- **Financial Insights**: Profit margins, cost analysis, ROI
- **Health Monitoring**: Vaccination coverage, mortality trends
- **Efficiency Analysis**: Resource utilization, labor efficiency
- **Predictions**: Revenue forecasting, trend analysis

### 🔄 **Contextual Navigation**
- Click on any batch to navigate to related modules
- Smart prefill of forms based on context
- Cross-module data sharing and synchronization
- Visual feedback and notifications

### ⚡ **Automated Monitoring**
- Real-time alerts every 5 minutes
- System tray notifications
- Multiple alert types:
  - High mortality rates
  - Low feed/water consumption
  - Upcoming vaccinations
  - Batch end dates
  - High expenses
  - Salary payments

### 📥 **Data Management**
- **Import**: CSV/Excel files with column mapping
- **Export**: Multiple formats (CSV, PDF, Excel)
- **Backup**: Automated database backups
- **Sync**: Cloud integration (placeholder)

### 🎨 **Customization**
- **Dashboard**: Drag-and-drop widgets
- **Themes**: Light and dark modes
- **Layout**: Persistent user preferences
- **Widgets**: Customizable metrics and charts

## 🔐 Security

- **Encrypted Database**: SQLCipher encryption
- **Secure Login**: Password hashing with bcrypt
- **Data Protection**: Local storage with encryption
- **Access Control**: User authentication system

## 🎨 User Interface

- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Adapts to different screen sizes
- **Intuitive Navigation**: Easy-to-use sidebar navigation
- **Visual Feedback**: Hover effects and animations
- **Accessibility**: High contrast themes and clear typography

## 📈 Business Benefits

- **Increased Efficiency**: Streamlined farm operations
- **Better Decision Making**: Data-driven insights
- **Cost Reduction**: Optimized resource management
- **Improved Health**: Proactive health monitoring
- **Financial Control**: Comprehensive financial tracking
- **Compliance**: Detailed record keeping

## 🚀 Getting Started

1. **First Launch**
   - Default admin credentials: `admin` / `admin123`
   - Change password in Settings after first login

2. **Add Your Data**
   - Start with Batch Management
   - Add workers and expenses
   - Log daily feed/water consumption
   - Record vaccinations and mortality

3. **Customize Dashboard**
   - Click "Customize Dashboard" button
   - Drag widgets to preferred positions
   - Save your layout

4. **Set Up Alerts**
   - Configure alert thresholds in Settings
   - Enable system tray notifications
   - Monitor automated alerts

## 🔧 Configuration

### Database Settings
- Location: `dash_poultry.db`
- Encryption: Enabled by default
- Backup: Automatic (Settings → Database)

### Theme Settings
- Light/Dark mode toggle
- Font size adjustment
- Auto-theme based on system

### Export Settings
- Default format selection
- Currency preferences
- Date format options

## 📞 Support

For issues and questions:
1. Check the documentation
2. Review error logs in `logs/` directory
3. Ensure all dependencies are installed
4. Verify database file permissions

## 🔄 Updates

The application supports:
- Database schema updates
- Configuration migrations
- Backup and restore functionality
- Data import/export for upgrades

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Dash Poultry** - Professional farm management made simple! 🐔✨

