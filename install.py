#!/usr/bin/env python3
"""
Dash Poultry Installation Script
This script helps set up the Dash Poultry farm management application.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = [
        "resources",
        "exports",
        "backups",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def check_dependencies():
    """Check if all dependencies are available"""
    print("Checking dependencies...")
    
    required_modules = [
        "PyQt6",
        "pyqtgraph", 
        "pandas",
        "numpy"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            print(f"❌ {module} is missing")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\nMissing modules: {', '.join(missing_modules)}")
        return False
    
    return True

def main():
    """Main installation function"""
    print("🚀 Dash Poultry Installation")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("❌ Installation failed!")
        return
    
    # Create directories
    create_directories()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Some dependencies are missing!")
        return
    
    print("\n🎉 Installation completed successfully!")
    print("\nTo run the application:")
    print("python main.py")
    
    print("\n📁 Application structure:")
    print("├── main.py              # Main application entry point")
    print("├── modules/             # Application modules")
    print("├── ui/                  # User interface components")
    print("├── utils/               # Utility functions")
    print("├── database/            # Database management")
    print("├── resources/           # Application resources")
    print("├── exports/             # Exported data")
    print("└── backups/             # Database backups")

if __name__ == "__main__":
    main() 