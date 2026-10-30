#!/bin/bash
# Gmail Email Classifier Setup Script for Unix/Linux/macOS

set -e  # Exit on any error

echo "============================================================"
echo "    Gmail Email Classifier Setup for Unix/Linux/macOS"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python found:"
python3 --version
echo

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found"
    echo "Please run this script from the project directory"
    exit 1
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "Dependencies installed successfully!"
echo

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env configuration file..."
    cp ".env.example" ".env"
    echo
    echo "IMPORTANT: You need to edit the .env file with your Gmail credentials"
    echo
    echo "To get a Gmail App Password:"
    echo "1. Enable 2-Factor Authentication on your Google Account"
    echo "2. Go to Google Account Settings > Security > 2-Step Verification"
    echo "3. Click 'App passwords' and generate a password for 'Mail'"
    echo "4. Edit the .env file with your email and app password"
    echo
    
    read -p "Would you like to open .env file for editing now? (y/N): " edit_env
    if [[ $edit_env =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo ".env file already exists"
fi

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Edit .env file with your Gmail credentials (if not done already)"
echo "2. Test connection: python3 test_gmail_connection.py"
echo "3. Collect training data: python3 training_data_collector.py"
echo "4. Train model: python3 ml_email_classifier.py"
echo "5. Run classification: python3 Gmail_scraper.py"
echo
echo "See README.md for detailed instructions"
echo

read -p "Would you like to test the Gmail connection now? (y/N): " test_now
if [[ $test_now =~ ^[Yy]$ ]]; then
    echo
    echo "Testing Gmail connection..."
    python3 test_gmail_connection.py
fi

echo
echo "Setup script completed!"