#!/usr/bin/env python3
"""
Gmail Connection Test - Diagnose connection issues
"""

import imaplib
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gmail_connection():
    """Test Gmail connection with detailed error reporting"""
    print("🔍 Gmail Connection Diagnostic Test")
    print("=" * 50)
    
    # Check credentials with better error handling
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    
    print(f"Debug - Raw email from env: '{gmail_email}'")
    print(f"Debug - Raw password from env: '{gmail_password}'")
    
    if not gmail_email:
        print("❌ GMAIL_EMAIL not found in .env file")
        # Try reading file directly
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Debug - .env file content:\n{repr(content)}")
        except Exception as e:
            print(f"Debug - Error reading .env: {e}")
        return False
    
    if not gmail_password:
        print("❌ GMAIL_PASSWORD not found in .env file")
        return False
    
    print(f"✅ Found Gmail Email: {gmail_email}")
    print(f"✅ Found Gmail Password: {'*' * len(gmail_password)}")
    print()
    
    # Test connection steps
    try:
        print("🔗 Step 1: Testing IMAP SSL connection to Gmail...")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=context)
        print("✅ Successfully connected to imap.gmail.com:993")
        
        print("🔑 Step 2: Testing authentication...")
        
        # Attempt login
        mail.login(gmail_email, gmail_password)
        print("✅ Authentication successful!")
        
        print("📂 Step 3: Testing inbox access...")
        
        # Select inbox
        status, messages = mail.select("inbox")
        if status == 'OK':
            print(f"✅ Inbox access successful! Found {messages[0].decode()} messages")
        else:
            print(f"⚠️ Inbox access issue: {status}")
        
        print("📊 Step 4: Getting inbox statistics...")
        
        # Get total emails
        _, data = mail.search(None, "ALL")
        total_emails = len(data[0].split()) if data[0] else 0
        
        # Get unread emails  
        _, unread_data = mail.search(None, "UNSEEN")
        unread_emails = len(unread_data[0].split()) if unread_data[0] else 0
        
        print(f"📧 Total emails in inbox: {total_emails}")
        print(f"📩 Unread emails: {unread_emails}")
        
        # Test email fetching
        if total_emails > 0:
            print("📬 Step 5: Testing email fetch...")
            email_ids = data[0].split()
            latest_id = email_ids[-1]
            
            _, msg_data = mail.fetch(latest_id, "(RFC822)")
            if msg_data[0]:
                print("✅ Email fetch successful!")
            else:
                print("⚠️ Email fetch returned no data")
        
        # Logout
        mail.logout()
        print("🚪 Logged out successfully")
        print()
        print("🎉 ALL TESTS PASSED! Gmail connection is working perfectly.")
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        print()
        print("🔧 Possible solutions:")
        print("   1. Check if Gmail App Password is correct")
        print("   2. Verify IMAP is enabled in Gmail settings")
        print("   3. Try generating a new App Password")
        return False
        
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print()
        print("🔧 Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Verify firewall/antivirus isn't blocking connection")
        print("   3. Try connecting from a different network")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print(f"❌ Error Type: {type(e).__name__}")
        print()
        print("🔧 General troubleshooting:")
        print("   1. Check .env file exists and has correct format")
        print("   2. Verify Gmail credentials are correct")
        print("   3. Check internet connection")
        print("   4. Try restarting the application")
        return False

def check_env_file():
    """Check if .env file exists and is properly formatted"""
    print("📁 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print()
        print("🔧 Create .env file with this format:")
        print("GMAIL_EMAIL=your.email@gmail.com")
        print("GMAIL_PASSWORD=your_app_password")
        return False
    
    print("✅ .env file exists")
    
    # Check content
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'GMAIL_EMAIL=' not in content:
        print("❌ GMAIL_EMAIL not found in .env")
        return False
    
    if 'GMAIL_PASSWORD=' not in content:
        print("❌ GMAIL_PASSWORD not found in .env")
        return False
    
    print("✅ .env file appears to be properly formatted")
    return True

def main():
    """Main diagnostic function"""
    print("🚀 Gmail AI Manager - Connection Diagnostic")
    print("=" * 60)
    print()
    
    # Check environment file first
    if not check_env_file():
        return
    
    print()
    
    # Test connection
    success = test_gmail_connection()
    
    print()
    print("=" * 60)
    
    if success:
        print("🎯 DIAGNOSIS: Connection is working!")
        print("   Your Gmail AI Manager should work normally.")
    else:
        print("🚨 DIAGNOSIS: Connection failed!")
        print("   Please fix the issues above before using the GUI.")
    
    print()
    print("💡 Need help setting up Gmail App Password?")
    print("   Visit: https://support.google.com/accounts/answer/185833")

if __name__ == "__main__":
    main()