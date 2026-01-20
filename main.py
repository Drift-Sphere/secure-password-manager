"""
Secure Offline Password Manager
Main entry point for the application.

A zero-knowledge password manager that:
- Generates cryptographically secure random passwords
- Encrypts data using AES-256 with PBKDF2 key derivation
- Stores everything locally (no internet connection required)
- Auto-locks after inactivity and clears clipboard for security
"""

import sys
import os


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    
    try:
        import cryptography
    except ImportError:
        missing.append("cryptography")
    
    try:
        import pyperclip
    except ImportError:
        missing.append("pyperclip")
    
    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")
    
    try:
        import bcrypt
    except ImportError:
        missing.append("bcrypt")
    
    if missing:
        print("ERROR: Missing required dependencies!")
        print("\nPlease install them using:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main application entry point."""
    print("=" * 60)
    print("🔐 SECURE OFFLINE PASSWORD MANAGER")
    print("=" * 60)
    print("Zero-Knowledge Architecture | AES-256 Encryption")
    print("100% Offline | Your data never leaves your computer")
    print("=" * 60)
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Import and run GUI
    try:
        from gui import PasswordManagerGUI
        
        app = PasswordManagerGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nApplication closed by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
