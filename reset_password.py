"""
Reset Database Password Script

This script encrypts the database password and updates config.ini
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
import configparser

KEY_FILE = ".encryption_key"
CONFIG_FILE = "config.ini"

def load_or_generate_key():
    """Load existing encryption key or generate a new one"""
    key_path = Path(KEY_FILE)
    
    if key_path.exists():
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
        print(f"✓ Loaded existing encryption key from {KEY_FILE}")
    else:
        # Generate new key
        key = Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        print(f"✓ Generated new encryption key and saved to {KEY_FILE}")
    
    return Fernet(key)

def encrypt_password(cipher, password):
    """Encrypt a password"""
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode()

def main():
    print("=" * 60)
    print("RESET DATABASE PASSWORD")
    print("=" * 60)
    print()
    
    # Load encryption key
    cipher = load_or_generate_key()
    
    # Password to encrypt
    password = "1"
    print(f"Password to encrypt: {password}")
    
    # Encrypt password
    encrypted_password = encrypt_password(cipher, password)
    print(f"Encrypted password: {encrypted_password[:50]}...")
    print()
    
    # Update config.ini
    config = configparser.ConfigParser(interpolation=None)
    config.read(CONFIG_FILE)
    
    # Update password
    config['Database']['password'] = encrypted_password
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    
    print(f"✓ Updated {CONFIG_FILE} with new encrypted password")
    print()
    
    # Verify by decrypting
    decrypted = cipher.decrypt(encrypted_password.encode()).decode()
    print(f"Verification - Decrypted password: {decrypted}")
    
    if decrypted == password:
        print("✓ Password encryption/decryption verified!")
    else:
        print("✗ Password verification failed!")
    
    print()
    print("=" * 60)
    print("Now run: python test_db_connection.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
