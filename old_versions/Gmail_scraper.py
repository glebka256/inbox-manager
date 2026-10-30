#!/usr/bin/env python3
"""
Gmail AI Manager - Intelligent Email Classification and Organization System

This is an AI-powered Gmail management system that automatically classifies and 
organizes your emails using advanced machine learning and rule-based algorithms.

Features:
- Hybrid AI classification (combines ML + rule-based intelligence)
- Automatic email labeling and organization
- Smart pattern recognition for email categorization
- Adaptive learning from your Gmail labels
- Intelligent confidence scoring and fallback systems

Usage:
    python Gmail_scraper.py

Requirements:
    - Gmail account with 2FA and App Password
    - Configured .env file with credentials
    - Python 3.8+ with required packages

This AI manager will intelligently process your emails and apply appropriate
labels automatically, helping you maintain an organized inbox effortlessly.
"""

import os
import sys

try:
    from dotenv import load_dotenv
    from rule_based_classifier import RuleBasedClassifier
    from ml_email_classifier import EmailMLClassifier
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Load environment variables
load_dotenv()


def main():
    """Main function for Gmail AI Manager"""
    print("🤖 Gmail AI Manager - Intelligent Email Organization System")
    print("=" * 60)
    print("This AI system will automatically classify and organize your emails")
    print("using advanced machine learning and rule-based algorithms.")
    print()
    print("🔧 Setup Instructions:")
    print("1. Configure your .env file with Gmail credentials")
    print("2. Run: python test_gmail_connection.py")
    print("3. Collect training data: python training_data_collector.py")
    print("4. Train AI model: python ml_email_classifier.py")
    print("5. Run this AI manager: python Gmail_scraper.py")
    print()
    print("📖 See README.md for detailed setup instructions")
    print()
    print("✅ Gmail AI Manager is ready to organize your emails!")


if __name__ == "__main__":
    main()
