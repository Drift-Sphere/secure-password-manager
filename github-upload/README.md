# 🔐 Secure Offline Password Manager

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?style=for-the-badge&logo=github)](https://github.com/sponsors/YOUR_USERNAME)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-ff5e5b?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/YOUR_USERNAME)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-00457C?style=for-the-badge&logo=paypal)](https://paypal.me/YOUR_USERNAME)

A zero-knowledge, offline-first password manager that generates cryptographically secure passwords and stores credentials using AES-256 encryption. **Your data stays local—no internet, no cloud, no third parties.**

---

> 💖 **This software is 100% free and open source.** If you find it useful, consider [buying me a coffee](https://ko-fi.com/YOUR_USERNAME)!

## ✨ Features

- **🎲 Cryptographic Password Generator**: Uses Python's `secrets` module for true randomness
- **🔒 Military-Grade Encryption**: AES-256 via Fernet with PBKDF2 key derivation (480k iterations)
- **🌐 100% Offline**: No network calls, no API dependencies, no cloud storage
- **🛡️ Zero-Knowledge Architecture**: Your Master Password is never stored; data is unreadable without it
- **⏰ Auto-Lock**: Vault locks after 5 minutes of inactivity
- **📋 Clipboard Security**: Auto-clears clipboard 30 seconds after copying passwords
- **🎨 Modern Dark-Mode GUI**: Clean, intuitive interface built with CustomTkinter

## 🚀 Installation

### 1. Install Python
Download and install Python 3.8 or later from [python.org](https://www.python.org/downloads/)

### 2. Install Dependencies
Open a terminal/command prompt in this directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `cryptography` - AES encryption and Fernet
- `pyperclip` - Clipboard operations
- `customtkinter` - Modern GUI framework
- `bcrypt` - Master Password hashing

## 📖 Usage

### First Launch
Run the application:

```bash
python main.py
```

On first launch, you'll be prompted to create a **Master Password**. This password:
- Must be at least 8 characters
- Must contain 3 of: uppercase, lowercase, digits, special characters
- **Cannot be recovered if forgotten** (zero-knowledge design)

> [!WARNING]
> **Write down your Master Password** in a secure physical location. If you forget it, your data is permanently unrecoverable.

### Daily Use

1. **Unlock**: Enter your Master Password
2. **Vault Tab**: 
   - View all saved credentials
   - Search by website or username
   - Copy username/password to clipboard
   - Add, edit, or delete entries
3. **Generator Tab**:
   - Adjust password length (12-64 characters)
   - Select character types
   - Generate and copy passwords

### Security Features

- **Auto-Lock**: After 5 minutes of inactivity, the vault automatically locks
- **Clipboard Auto-Clear**: Copied passwords are cleared from clipboard after 30 seconds
- **Manual Lock**: Click "🔒 Lock Vault" anytime to lock immediately

## 🔒 Security Model

### Encryption Details

- **Algorithm**: AES-256 (via Fernet symmetric encryption)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 480,000 iterations
- **Master Password Verification**: bcrypt with 12 rounds
- **Salt**: Unique 16-byte cryptographic salt (stored in `salt.key`)

### What Gets Stored

**Files Created**:
- `vault.db` - SQLite database with encrypted passwords
- `salt.key` - 16-byte salt for key derivation

**What's Encrypted**:
- All passwords are encrypted before storage
- Even with access to `vault.db`, passwords are unreadable without your Master Password

**What's NOT Stored**:
- Your Master Password (only a bcrypt hash is stored)
- Decrypted passwords (only encrypted ciphertext)

## 💾 Backup & Recovery

### Regular Backups

It's **critical** to back up these files regularly:
- `vault.db` (your encrypted credential database)
- `salt.key` (required for decryption)

Recommended backup locations:
- USB flash drive
- External hard drive
- Encrypted personal cloud storage (if you accept the internet risk)

### Recovery Process

If you lose your data:
1. Copy `vault.db` and `salt.key` back to the application directory
2. Run `python main.py`
3. Enter your Master Password
4. All credentials will be restored

> [!CAUTION]
> If you lose **either** `salt.key` OR your Master Password, your data is **permanently unrecoverable**.

## 🌐 Offline Verification

To verify the application works 100% offline:

**Windows**:
```powershell
# Disable network
Get-NetAdapter | Disable-NetAdapter

# Run app
python main.py

# Re-enable network
Get-NetAdapter | Enable-NetAdapter
```

**macOS/Linux**:
```bash
# Disable Wi-Fi
sudo ifconfig en0 down  # or your network interface

# Run app
python main.py

# Re-enable Wi-Fi
sudo ifconfig en0 up
```

The application should work perfectly with no internet connection.

## 🔧 Troubleshooting

### "Module not found" errors
Run: `pip install -r requirements.txt`

### Can't see passwords after restart
- Ensure `salt.key` exists in the same directory
- Verify you're using the correct Master Password

### Clipboard not working
- On Linux, you may need: `sudo apt-get install xclip xsel`
- On macOS, clipboard access requires system permissions

### Application won't start
- Check Python version: `python --version` (must be 3.8+)
- Verify dependencies: `pip list | findstr "cryptography customtkinter"`

## 📊 Technical Architecture

```
password-manager/
├── main.py                 # Application entry point
├── crypto_manager.py       # Encryption/decryption (AES-256, PBKDF2)
├── database.py            # SQLite operations (CRUD)
├── password_generator.py  # Cryptographically secure generation
├── gui.py                 # CustomTkinter interface
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── vault.db              # Encrypted database (created on first run)
└── salt.key              # Encryption salt (created on first run)
```

## 🛡️ Security Best Practices

1. **Strong Master Password**: Use a long, unique password you'll remember
2. **Regular Backups**: Back up `vault.db` and `salt.key` weekly
3. **Physical Security**: Keep backup files in a secure physical location
4. **Offline Storage**: Consider storing backups on air-gapped USB drives
5. **Firewall**: Optionally block this application from network access via OS firewall

## 🚨 Limitations & Warnings

> [!IMPORTANT]
> **This is NOT a cloud password manager.** There is no sync, no recovery service, no support team. You are 100% responsible for:
> - Remembering your Master Password
> - Backing up your vault and salt files
> - Securing your computer from malware

> [!WARNING]
> **No Password Recovery**: Zero-knowledge encryption means if you forget your Master Password, **there is no way to recover your data**. Not even the developer can help.

> [!CAUTION]
> **Malware Risk**: If your computer is infected with keyloggers or screen capture malware, your passwords can be stolen when you decrypt them. This tool does not protect against compromised systems.

## 📄 License

This software is provided as-is for personal use. Use at your own risk.

## 🙏 Credits

Built using:
- [cryptography](https://cryptography.io/) - Encryption library
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [bcrypt](https://github.com/pyca/bcrypt/) - Password hashing
- [pyperclip](https://github.com/asweigart/pyperclip) - Clipboard operations

---

**Stay secure. Stay offline. Stay in control.** 🔐
