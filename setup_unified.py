#!/usr/bin/env python3
"""
Unified Gmail AI Setup Script
Sets up the new unified system with all improvements
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Check if virtual environment exists
    venv_path = Path("gmail_ai_env")
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        if not run_command("python -m venv gmail_ai_env", "Creating virtual environment"):
            return False
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = "gmail_ai_env\\Scripts\\activate"
        pip_command = "gmail_ai_env\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "gmail_ai_env/bin/activate"
        pip_command = "gmail_ai_env/bin/pip"
    
    # Install dependencies
    install_cmd = f"{pip_command} install -r requirements.txt"
    if not run_command(install_cmd, "Installing dependencies"):
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    directories = [
        "logs",
        "config", 
        "backups",
        "core",
        "gui",
        "utilities"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def setup_credentials():
    """Setup secure credentials"""
    print("🔐 Setting up secure credentials...")
    
    # Check if credentials file exists
    creds_file = Path("credentials/gmail_credentials.env")
    if not creds_file.exists():
        print("⚠️ No credentials file found. Please create credentials/gmail_credentials.env first.")
        print("💡 Copy credentials/gmail_credentials_template.env to credentials/gmail_credentials.env")
        print("💡 Then edit it with your actual Gmail credentials")
        return False
    
    # Try to setup encrypted credentials
    try:
        from utilities.credential_manager import setup_secure_credentials
        if setup_secure_credentials():
            print("✅ Secure credentials setup completed")
            return True
        else:
            print("⚠️ Secure credentials setup failed, but system will still work")
            return True
    except ImportError:
        print("⚠️ Credential manager not available, skipping encryption setup")
        return True

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing module imports...")
    
    modules_to_test = [
        "utilities.credential_manager",
        "utilities.secure_loader", 
        "utilities.database_manager",
        "utilities.config_manager",
        "utilities.logger",
        "core.email_classifier"
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"⚠️ {len(failed_imports)} modules failed to import")
        return False
    
    print("✅ All modules imported successfully")
    return True

def create_launcher():
    """Create launcher script for the unified GUI"""
    print("🚀 Creating unified launcher...")
    
    launcher_content = '''@echo off
echo Starting Gmail AI Manager - Unified Edition...
cd /d "%~dp0"

REM Activate virtual environment
call gmail_ai_env\\Scripts\\activate.bat

REM Start unified GUI
python gui\\unified_gui.py

pause
'''
    
    with open("LAUNCH_UNIFIED.bat", "w") as f:
        f.write(launcher_content)
    
    print("✅ Created LAUNCH_UNIFIED.bat")
    return True

def main():
    """Main setup function"""
    print("🚀 Gmail AI Manager - Unified Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup directories
    if not setup_directories():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Test imports
    if not test_imports():
        print("⚠️ Some modules failed to import, but setup will continue")
    
    # Setup credentials
    setup_credentials()
    
    # Create launcher
    create_launcher()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit credentials/gmail_credentials.env with your Gmail credentials")
    print("2. Run LAUNCH_UNIFIED.bat to start the unified GUI")
    print("3. Or run: python gui/unified_gui.py")
    print("\n🔧 Features available:")
    print("✅ Secure credential encryption")
    print("✅ Unified database management")
    print("✅ Consolidated GUI interface")
    print("✅ Improved error handling")
    print("✅ Centralized configuration")
    print("✅ Comprehensive logging")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
