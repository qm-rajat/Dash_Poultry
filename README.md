# Dash Poultry

A professional farm management desktop application for poultry farms, built with PyQt6 and encrypted SQLite.

## Features
- Secure admin login
- Batch, feed, water, vaccination, mortality, worker, and expense management
- Dashboard with charts
- Export to PDF, CSV, PPT
- Light/Dark themes

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python main.py
   ```

## Packaging (Windows)
To generate an .exe:
```bash
pyinstaller --onefile --windowed main.py
```

---
Default login: `admin1` / `admin1`

