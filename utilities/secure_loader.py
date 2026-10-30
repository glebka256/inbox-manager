#!/usr/bin/env python3
"""
Secure Credential Loader
Provides secure access to encrypted credentials across all modules
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path

# Add utilities to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from credential_manager import CredentialManager
except ImportError:
    print("⚠️ CredentialManager not available - using fallback method")
    CredentialManager = None

class SecureCredentialLoader:
    """Secure credential loader with fallback to environment variables"""
    
    def __init__(self):
        self.credentials = None
        self.encrypted_file = "credentials/gmail_credentials.encrypted"
        self.env_file = "credentials/gmail_credentials.env"
        self.template_file = "credentials/gmail_credentials_template.env"
    
    def load_credentials(self) -> Dict[str, str]:
        """Load credentials with priority: encrypted > env > template"""
        
        # Try encrypted credentials first
        if self._load_encrypted_credentials():
            return self.credentials
        
        # Fallback to environment file
        if self._load_env_credentials():
            return self.credentials
        
        # Last resort - template file
        if self._load_template_credentials():
            return self.credentials
        
        raise FileNotFoundError("No valid credentials found. Please set up credentials first.")
    
    def _load_encrypted_credentials(self) -> bool:
        """Try to load encrypted credentials"""
        if not os.path.exists(self.encrypted_file):
            return False
        
        if not CredentialManager:
            print("⚠️ CredentialManager not available - cannot decrypt credentials")
            return False
        
        try:
            manager = CredentialManager()
            self.credentials = manager.load_encrypted_credentials(self.encrypted_file)
            print("🔐 Loaded encrypted credentials")
            return True
        except Exception as e:
            print(f"⚠️ Failed to load encrypted credentials: {e}")
            return False
    
    def _load_env_credentials(self) -> bool:
        """Load credentials from .env file"""
        if not os.path.exists(self.env_file):
            return False
        
        try:
            self.credentials = {}
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.credentials[key.strip()] = value.strip()
            
            if self.credentials:
                print("📁 Loaded credentials from .env file")
                return True
        except Exception as e:
            print(f"⚠️ Failed to load .env credentials: {e}")
        
        return False
    
    def _load_template_credentials(self) -> bool:
        """Load template credentials (for setup)"""
        if not os.path.exists(self.template_file):
            return False
        
        try:
            self.credentials = {}
            with open(self.template_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.credentials[key.strip()] = value.strip()
            
            print("📋 Loaded template credentials (please update with real values)")
            return True
        except Exception as e:
            print(f"⚠️ Failed to load template credentials: {e}")
        
        return False
    
    def get_gmail_credentials(self) -> tuple[str, str]:
        """Get Gmail email and password"""
        if not self.credentials:
            self.load_credentials()
        
        # Try different naming conventions
        email = (self.credentials.get('GMAIL_USER') or 
                self.credentials.get('GMAIL_EMAIL') or 
                self.credentials.get('EMAIL'))
        
        password = (self.credentials.get('GMAIL_PASS') or 
                   self.credentials.get('GMAIL_PASSWORD') or 
                   self.credentials.get('PASSWORD'))
        
        if not email or not password:
            raise ValueError("Gmail credentials not found. Please check your credentials file.")
        
        return email, password
    
    def get_all_credentials(self) -> Dict[str, str]:
        """Get all credentials"""
        if not self.credentials:
            self.load_credentials()
        return self.credentials.copy()

# Global instance for easy access
credential_loader = SecureCredentialLoader()

def get_gmail_credentials() -> tuple[str, str]:
    """Convenience function to get Gmail credentials"""
    return credential_loader.get_gmail_credentials()

def get_all_credentials() -> Dict[str, str]:
    """Convenience function to get all credentials"""
    return credential_loader.get_all_credentials()

if __name__ == "__main__":
    # Test credential loading
    try:
        email, password = get_gmail_credentials()
        print(f"✅ Successfully loaded credentials for: {email}")
        print(f"🔑 Password: {'*' * len(password)}")
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
