"""
Database Management Module
Handles all SQLite database operations for the password vault.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class Database:
    """Manages SQLite database for credential storage."""
    
    DB_FILE = "vault.db"
    
    def __init__(self):
        """Initialize database connection and create tables if needed."""
        self.conn = sqlite3.connect(self.DB_FILE)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        # Credentials table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                url TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Settings table for storing Master Password hash
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def set_master_password_hash(self, password_hash: str):
        """
        Store the Master Password hash.
        
        Args:
            password_hash: Bcrypt hash of the Master Password
        """
        self.cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES ('master_password_hash', ?)
        """, (password_hash,))
        self.conn.commit()
    
    def get_master_password_hash(self) -> Optional[str]:
        """
        Retrieve the stored Master Password hash.
        
        Returns:
            The password hash, or None if not set
        """
        self.cursor.execute("""
            SELECT value FROM settings WHERE key = 'master_password_hash'
        """)
        result = self.cursor.fetchone()
        return result['value'] if result else None
    
    def is_first_run(self) -> bool:
        """
        Check if this is the first run (no Master Password set).
        
        Returns:
            True if first run, False otherwise
        """
        return self.get_master_password_hash() is None
    
    def add_credential(self, website: str, username: str, encrypted_password: str,
                      url: str = "", notes: str = "") -> int:
        """
        Add a new credential to the vault.
        
        Args:
            website: Website/service name
            username: Username or email
            encrypted_password: Encrypted password
            url: Optional URL
            notes: Optional notes
            
        Returns:
            ID of the newly created credential
        """
        self.cursor.execute("""
            INSERT INTO credentials (website, username, encrypted_password, url, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (website, username, encrypted_password, url, notes))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_credential(self, credential_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single credential by ID.
        
        Args:
            credential_id: The credential ID
            
        Returns:
            Dictionary with credential data, or None if not found
        """
        self.cursor.execute("""
            SELECT * FROM credentials WHERE id = ?
        """, (credential_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_credentials(self) -> List[Dict[str, Any]]:
        """
        Retrieve all credentials.
        
        Returns:
            List of credential dictionaries
        """
        self.cursor.execute("""
            SELECT * FROM credentials ORDER BY website, username
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_credentials(self, query: str) -> List[Dict[str, Any]]:
        """
        Search credentials by website or username.
        
        Args:
            query: Search term
            
        Returns:
            List of matching credential dictionaries
        """
        search_pattern = f"%{query}%"
        self.cursor.execute("""
            SELECT * FROM credentials 
            WHERE website LIKE ? OR username LIKE ?
            ORDER BY website, username
        """, (search_pattern, search_pattern))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_credential(self, credential_id: int, website: str = None,
                         username: str = None, encrypted_password: str = None,
                         url: str = None, notes: str = None):
        """
        Update an existing credential.
        
        Args:
            credential_id: The credential ID to update
            website: New website name (optional)
            username: New username (optional)
            encrypted_password: New encrypted password (optional)
            url: New URL (optional)
            notes: New notes (optional)
        """
        # Build update query dynamically based on provided fields
        updates = []
        values = []
        
        if website is not None:
            updates.append("website = ?")
            values.append(website)
        if username is not None:
            updates.append("username = ?")
            values.append(username)
        if encrypted_password is not None:
            updates.append("encrypted_password = ?")
            values.append(encrypted_password)
        if url is not None:
            updates.append("url = ?")
            values.append(url)
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
        
        if not updates:
            return  # Nothing to update
        
        updates.append("modified_at = ?")
        values.append(datetime.now().isoformat())
        values.append(credential_id)
        
        query = f"UPDATE credentials SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
    
    def delete_credential(self, credential_id: int):
        """
        Delete a credential from the vault.
        
        Args:
            credential_id: The credential ID to delete
        """
        self.cursor.execute("""
            DELETE FROM credentials WHERE id = ?
        """, (credential_id,))
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
