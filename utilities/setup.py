#!/usr/bin/env python3
"""
Gmail Email Classifier Setup Script
Automated setup and configuration for the email classification system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀 Gmail Email Classifier Setup")
    print("=" * 50)
    print("This script will help you set up the email classification system.")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n🔐 Setting up environment configuration...")
    
    if os.path.exists(".env"):
        response = input("⚠️ .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return True
    
    # Copy from template
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
    else:
        # Create basic .env file
        with open(".env", "w") as f:
            f.write("# Gmail Credentials\n")
            f.write("GMAIL_EMAIL=your.email@gmail.com\n")
            f.write("GMAIL_PASSWORD=your_app_password_here\n")
        print("✅ Created basic .env file")
    
    print("\n🔑 Gmail App Password Setup:")
    print("1. Enable 2-Factor Authentication on your Google Account")
    print("2. Go to Google Account Settings > Security > 2-Step Verification")
    print("3. Click 'App passwords' and generate a password for 'Mail'")
    print("4. Edit the .env file with your email and app password")
    print()
    
    return True

def test_connection():
    """Test Gmail connection"""
    print("\n🔍 Testing Gmail connection...")
    try:
        # Import here to avoid dependency issues during setup
        from test_gmail_connection import test_gmail_connection
        test_gmail_connection()
        return True
    except Exception as e:
        print(f"⚠️ Connection test failed: {e}")
        print("Please check your .env configuration")
        return False

def collect_training_data():
    """Collect initial training data"""
    print("\n📚 Collecting training data...")
    response = input("Do you want to collect training data from existing Gmail labels? (y/N): ")
    
    if response.lower() == 'y':
        try:
            subprocess.check_call([sys.executable, "training_data_collector.py"])
            print("✅ Training data collected")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Failed to collect training data")
            return False
    else:
        print("Skipping training data collection")
        return True

def train_model():
    """Train the ML model"""
    print("\n🤖 Training machine learning model...")
    
    if not os.path.exists("email_training_data.csv"):
        print("⚠️ No training data found. Skipping model training.")
        return True
    
    try:
        subprocess.check_call([sys.executable, "ml_email_classifier.py"])
        print("✅ Model trained successfully")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Model training failed")
        return False

def run_demo():
    """Run a demo classification"""
    print("\n🎯 Running demo classification...")
    response = input("Do you want to run a demo classification? (y/N): ")
    
    if response.lower() == 'y':
        try:
            subprocess.check_call([sys.executable, "rule_based_classifier.py"])
            print("✅ Demo completed")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Demo failed")
            return False
    else:
        print("Skipping demo")
        return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Edit .env file with your Gmail credentials")
    print("2. Test connection: python test_gmail_connection.py")
    print("3. Collect training data: python training_data_collector.py")
    print("4. Train model: python ml_email_classifier.py")
    print("5. Run classification: python Gmail_scraper.py")
    print()
    print("📖 See README.md for detailed usage instructions")
    print("🐛 Report issues: https://github.com/your-username/gmail-email-classifier/issues")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Install dependencies", install_dependencies),
        ("Create environment file", create_env_file),
        ("Test Gmail connection", test_connection),
        ("Collect training data", collect_training_data),
        ("Train ML model", train_model),
        ("Run demo", run_demo),
    ]
    
    failed_steps = []
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    # Summary
    if failed_steps:
        print(f"\n⚠️ Setup completed with {len(failed_steps)} issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease review the errors above and run the setup again if needed.")
    else:
        print_next_steps()

if __name__ == "__main__":
    main()