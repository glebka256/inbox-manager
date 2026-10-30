#!/usr/bin/env python3
"""
Quick test script to verify credentials are loading properly
"""

import os
import sys

def test_credentials():
    """Test credential loading from the credentials folder"""
    print("🔍 Testing Gmail Credentials Loading...")
    print("=" * 50)
    
    # Test 1: Check if credentials folder exists
    # Go up one level from utilities folder to find credentials
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    credentials_dir = os.path.join(parent_dir, 'credentials')
    if os.path.exists(credentials_dir):
        print("✅ Credentials folder found")
    else:
        print("❌ Credentials folder not found")
        return False
    
    # Test 2: Check if credentials file exists
    credentials_file = os.path.join(credentials_dir, 'gmail_credentials.env')
    if os.path.exists(credentials_file):
        print("✅ gmail_credentials.env file found")
    else:
        print("❌ gmail_credentials.env file not found")
        print(f"💡 Expected location: {credentials_file}")
        return False
    
    # Test 3: Try loading credentials
    try:
        from dotenv import load_dotenv
        load_dotenv(credentials_file)
        
        email = os.getenv('GMAIL_USER', '') or os.getenv('GMAIL_EMAIL', '')
        password = os.getenv('GMAIL_PASS', '') or os.getenv('GMAIL_PASSWORD', '')
        
        if email:
            print(f"✅ Gmail email loaded: {email}")
        else:
            print("❌ Gmail email not found in credentials file")
            return False
            
        if password:
            print(f"✅ Gmail password loaded: {'*' * 4} {password[-4:] if len(password) >= 4 else '****'}")
        else:
            print("❌ Gmail password not found in credentials file")
            return False
            
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All credential tests passed!")
    print("🚀 Your Gmail AI Manager is ready to use!")
    return True

if __name__ == "__main__":
    success = test_credentials()
    if not success:
        print("\n💡 To fix this:")
        print("1. Go to the credentials folder")
        print("2. Copy gmail_credentials_template.env to gmail_credentials.env")
        print("3. Edit gmail_credentials.env with your Gmail App Password")
        print("4. See credentials/README.md for detailed instructions")
        sys.exit(1)