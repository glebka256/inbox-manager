import imaplib
import email
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get email credentials from environment variables
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', '').strip()
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '').strip().replace(' ', '').replace('\xa0', '')

# Validate that credentials are loaded
if not GMAIL_EMAIL or not GMAIL_PASSWORD:
    raise ValueError("Please set GMAIL_EMAIL and GMAIL_PASSWORD in your .env file")

print(f"📧 Email: {GMAIL_EMAIL}")
print(f"🔑 Password length: {len(GMAIL_PASSWORD)} characters")
print(f"🔑 Password (first 4 chars): {GMAIL_PASSWORD[:4]}...")

def test_gmail_connection():
    """Test Gmail connection and fetch a few emails"""
    try:
        print(f"🔗 Connecting to Gmail for: {GMAIL_EMAIL}")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        print("🔐 Logging in...")
        mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        print("✅ Successfully logged in!")
        
        print("📁 Selecting inbox...")
        mail.select("inbox")
        
        print("📧 Searching for emails...")
        # Get the last 5 emails instead of just unread ones
        _, data = mail.search(None, "ALL")
        
        if not data[0]:
            print("❌ No emails found in inbox")
            return
        
        # Get last 5 emails
        email_ids = data[0].split()[-5:]  # Last 5 emails
        
        print(f"📨 Found {len(email_ids)} recent emails:")
        print("-" * 60)
        
        for i, num in enumerate(email_ids, 1):
            try:
                # Fetch email message
                _, msg_data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                subject = msg["subject"] or 'No Subject'
                sender = msg["from"] or 'Unknown Sender'
                date = msg["date"] or 'Unknown Date'
                
                print(f"{i}. Subject: {subject}")
                print(f"   From: {sender}")
                print(f"   Date: {date}")
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Error processing email {num}: {e}")
        
        mail.logout()
        print("✅ Successfully disconnected from Gmail")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP Error: {e}")
        print("💡 Check your email and app password")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def list_gmail_folders():
    """List all available Gmail folders/labels"""
    try:
        print(f"📁 Listing Gmail folders for: {GMAIL_EMAIL}")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        
        # List all folders
        _, folders = mail.list()
        print("Available folders:")
        for folder in folders:
            folder_name = folder.decode('utf-8')
            print(f"  {folder_name}")
        
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error listing folders: {e}")

if __name__ == "__main__":
    print("🚀 Testing Gmail Email Scraper")
    print("=" * 60)
    
    # Test basic connection and email fetching
    test_gmail_connection()
    
    print("\n" + "=" * 60)
    
    # List available folders
    list_gmail_folders()