"""
Cryptographic Security Module
Handles encryption, decryption, key derivation, and Master Password management.
Uses AES-256 encryption via Fernet with PBKDF2 key derivation.
"""

import os
import base64
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Manages all cryptographic operations for the password vault."""
    
    SALT_FILE = "salt.key"
    ITERATIONS = 480000  # High iteration count for security
    
    def __init__(self, master_password: str):
        """
        Initialize the crypto manager.
        
        Args:
            master_password: The user's Master Password
        """
        self.master_password = master_password
        self.salt = self._load_or_create_salt()
        self.key = self._derive_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_create_salt(self) -> bytes:
        """
        Load existing salt from file or create a new one.
        
        Returns:
            16-byte salt
        """
        if os.path.exists(self.SALT_FILE):
            with open(self.SALT_FILE, 'rb') as f:
                return f.read()
        else:
            # Generate cryptographically random 16-byte salt
            salt = os.urandom(16)
            with open(self.SALT_FILE, 'wb') as f:
                f.write(salt)
            return salt
    
    def _derive_key(self) -> bytes:
        """
        Derive encryption key from Master Password using PBKDF2.
        
        Returns:
            Base64-encoded 32-byte key suitable for Fernet
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )
        key = kdf.derive(self.master_password.encode())
        # Fernet requires base64-encoded key
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The text to encrypt
            
        Returns:
            Encrypted text as string
        """
        if not plaintext:
            return ""
        encrypted_bytes = self.fernet.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a ciphertext string.
        
        Args:
            ciphertext: The encrypted text
            
        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return ""
        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def hash_master_password(password: str) -> str:
        """
        Create bcrypt hash of Master Password for verification.
        
        Args:
            password: The Master Password
            
        Returns:
            Bcrypt hash as string
        """
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
        return hashed.decode()
    
    @staticmethod
    def verify_master_password(password: str, hashed: str) -> bool:
        """
        Verify a Master Password against its hash.
        
        Args:
            password: The password to check
            hashed: The stored bcrypt hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate Master Password strength.
        
        Args:
            password: The password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        strength_checks = [has_upper, has_lower, has_digit, has_special]
        
        if sum(strength_checks) < 3:
            return False, "Password must contain at least 3 of: uppercase, lowercase, digit, special character"
        
        return True, ""
