# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Import Errors

#### `ImportError: cannot import name 'QAction' from 'PyQt6.QtWidgets'`
**Solution**: QAction is in `PyQt6.QtGui`, not `PyQt6.QtWidgets`
```python
# ❌ Wrong
from PyQt6.QtWidgets import QAction

# ✅ Correct
from PyQt6.QtGui import QAction
```

#### `ModuleNotFoundError: No module named 'pyqtgraph'`
**Solution**: Install missing dependencies
```bash
pip install pyqtgraph pandas numpy
```

#### `ImportError: No module named 'sqlcipher3'`
**Solution**: Install SQLCipher
```bash
pip install sqlcipher3-binary
```

### Runtime Errors

#### `Database is locked`
**Solution**: 
1. Close any other instances of the application
2. Check if database file is read-only
3. Restart the application

#### `Permission denied` when accessing database
**Solution**:
1. Check file permissions
2. Run as administrator (Windows)
3. Ensure write access to the directory

#### `Chart not displaying`
**Solution**:
1. Ensure pyqtgraph is properly installed
2. Check if data exists in the database
3. Restart the application

### Installation Issues

#### `pip install fails`
**Solution**:
1. Update pip: `python -m pip install --upgrade pip`
2. Use virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

#### `PyQt6 installation fails on Windows`
**Solution**:
1. Install Visual C++ Redistributable
2. Use pre-compiled wheels:
   ```bash
   pip install PyQt6 --only-binary=PyQt6
   ```

### Performance Issues

#### `Application is slow`
**Solution**:
1. Close unnecessary applications
2. Check available RAM
3. Reduce chart complexity in settings
4. Clear old data if database is large

#### `High memory usage`
**Solution**:
1. Restart application periodically
2. Close unused modules
3. Clear cache in settings

### Data Issues

#### `Data not saving`
**Solution**:
1. Check database permissions
2. Ensure proper form validation
3. Check for required fields
4. Verify database connection

#### `Import not working`
**Solution**:
1. Check file format (CSV/Excel)
2. Verify column mapping
3. Ensure data types match
4. Check for special characters

### UI Issues

#### `Theme not applying`
**Solution**:
1. Restart application
2. Check theme file exists
3. Clear application cache
4. Reset to default theme

#### `Widgets not draggable`
**Solution**:
1. Ensure QApplication is imported
2. Check mouse events are enabled
3. Verify widget accepts drops
4. Restart customizer

### System Tray Issues

#### `System tray not working`
**Solution**:
1. Check if system supports tray icons
2. Enable notifications in system settings
3. Run as administrator (Windows)
4. Check desktop environment (Linux)

### Export Issues

#### `PDF export fails`
**Solution**:
1. Install reportlab: `pip install reportlab`
2. Check write permissions
3. Ensure sufficient disk space
4. Close PDF if open

#### `Excel export fails`
**Solution**:
1. Install openpyxl: `pip install openpyxl`
2. Check file is not open
3. Verify file path is valid
4. Ensure sufficient disk space

## Debug Mode

Enable debug mode by setting environment variable:
```bash
# Windows
set DEBUG=1
python main.py

# Linux/Mac
DEBUG=1 python main.py
```

## Log Files

Check log files in the `logs/` directory for detailed error information.

## Getting Help

1. **Check this troubleshooting guide**
2. **Review the README.md file**
3. **Check log files for errors**
4. **Verify all dependencies are installed**
5. **Try running the installation script again**

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run installation script
python install.py

# Run application
python main.py

# Check Python version
python --version

# Check installed packages
pip list

# Update packages
pip install --upgrade -r requirements.txt
```

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## Performance Tips

1. **Use SSD storage** for better database performance
2. **Close unused modules** to reduce memory usage
3. **Regular backups** to prevent data loss
4. **Update regularly** for bug fixes and improvements
5. **Monitor system resources** during heavy operations 