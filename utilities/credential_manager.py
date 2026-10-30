#!/usr/bin/env python3
"""
Secure Credential Manager
Handles encryption/decryption of sensitive credentials
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
from typing import Optional, Dict, Any

class CredentialManager:
    """Secure credential management with encryption"""
    
    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password or self._get_master_password()
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _get_master_password(self) -> str:
        """Get master password from environment or prompt user"""
        master_pwd = os.getenv('GMAIL_AI_MASTER_PASSWORD')
        if not master_pwd:
            print("🔐 No master password found in environment variables.")
            print("💡 Set GMAIL_AI_MASTER_PASSWORD environment variable for automatic decryption")
            print("   Or enter master password when prompted")
            master_pwd = input("Enter master password for credential encryption: ")
        return master_pwd
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from master password"""
        # Use a fixed salt for consistency (in production, store salt separately)
        salt = b'gmail_ai_salt_2024'  # In production, generate random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        return key
    
    def encrypt_credentials(self, credentials: Dict[str, str]) -> str:
        """Encrypt credentials dictionary"""
        credentials_json = json.dumps(credentials)
        encrypted_data = self.cipher.encrypt(credentials_json.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_credentials(self, encrypted_credentials: str) -> Dict[str, str]:
        """Decrypt credentials string"""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_credentials.encode())
            decrypted_json = self.cipher.decrypt(encrypted_data).decode()
            return json.loads(decrypted_json)
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {e}")
    
    def save_encrypted_credentials(self, credentials: Dict[str, str], file_path: str):
        """Save encrypted credentials to file"""
        encrypted = self.encrypt_credentials(credentials)
        with open(file_path, 'w') as f:
            f.write(encrypted)
        print(f"✅ Encrypted credentials saved to {file_path}")
    
    def load_encrypted_credentials(self, file_path: str) -> Dict[str, str]:
        """Load and decrypt credentials from file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Encrypted credentials file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            encrypted = f.read().strip()
        
        return self.decrypt_credentials(encrypted)
    
    def migrate_from_env(self, env_file_path: str, encrypted_file_path: str):
        """Migrate credentials from .env file to encrypted format"""
        if not os.path.exists(env_file_path):
            print(f"⚠️ Environment file not found: {env_file_path}")
            return False
        
        # Load from .env file
        credentials = {}
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        
        if not credentials:
            print("⚠️ No credentials found in environment file")
            return False
        
        # Save encrypted version
        self.save_encrypted_credentials(credentials, encrypted_file_path)
        print(f"✅ Migrated {len(credentials)} credentials to encrypted format")
        return True

def setup_secure_credentials():
    """Setup secure credentials - migrate from existing .env file"""
    print("🔐 Setting up secure credential management...")
    
    # Paths
    env_file = "credentials/gmail_credentials.env"
    encrypted_file = "credentials/gmail_credentials.encrypted"
    
    # Check if encrypted file already exists
    if os.path.exists(encrypted_file):
        print("✅ Encrypted credentials already exist")
        return True
    
    # Check if .env file exists
    if not os.path.exists(env_file):
        print("⚠️ No credentials file found to migrate")
        print("💡 Please create credentials/gmail_credentials.env first")
        return False
    
    try:
        # Create credential manager
        manager = CredentialManager()
        
        # Migrate credentials
        success = manager.migrate_from_env(env_file, encrypted_file)
        
        if success:
            print("🔒 Credentials are now encrypted and secure!")
            print("💡 You can safely delete the original .env file if you want")
            print("💡 Remember to set GMAIL_AI_MASTER_PASSWORD environment variable")
            return True
        else:
            print("❌ Failed to migrate credentials")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up secure credentials: {e}")
        return False

if __name__ == "__main__":
    setup_secure_credentials()
