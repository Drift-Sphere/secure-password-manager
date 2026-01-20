"""
Graphical User Interface Module
Modern dark-mode desktop application using CustomTkinter.
"""

import customtkinter as ctk
from tkinter import messagebox
import pyperclip
import threading
from typing import Optional, Callable
from datetime import datetime

from crypto_manager import CryptoManager
from database import Database
from password_generator import generate_password, estimate_password_strength


class PasswordManagerGUI:
    """Main GUI application for the password manager."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = ctk.CTk()
        self.root.title("Secure Password Manager")
        self.root.geometry("900x650")
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Application state
        self.db = Database()
        self.crypto_manager: Optional[CryptoManager] = None
        self.is_locked = True
        self.auto_lock_timer: Optional[threading.Timer] = None
        self.clipboard_timer: Optional[threading.Timer] = None
        
        # Start the appropriate screen
        if self.db.is_first_run():
            self.show_setup_screen()
        else:
            self.show_login_screen()
    
    def reset_auto_lock(self):
        """Reset the auto-lock timer (5 minutes of inactivity)."""
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
        
        if not self.is_locked:
            self.auto_lock_timer = threading.Timer(300, self.lock_vault)  # 5 minutes
            self.auto_lock_timer.daemon = True
            self.auto_lock_timer.start()
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ==================== SETUP SCREEN ====================
    
    def show_setup_screen(self):
        """Display first-time setup screen for creating Master Password."""
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="🔐 Welcome to Secure Password Manager",
                            font=("Helvetica", 24, "bold"))
        title.pack(pady=20)
        
        subtitle = ctk.CTkLabel(frame, 
                               text="Create your Master Password\n" +
                                    "⚠️ This password cannot be recovered if forgotten!",
                               font=("Helvetica", 12))
        subtitle.pack(pady=10)
        
        # Password requirements
        requirements = ctk.CTkLabel(frame,
                                   text="Requirements:\n" +
                                        "• At least 8 characters\n" +
                                        "• 3 of: uppercase, lowercase, digit, special character",
                                   font=("Helvetica", 10),
                                   justify="left")
        requirements.pack(pady=10)
        
        # Master Password input
        ctk.CTkLabel(frame, text="Master Password:").pack(pady=(20, 5))
        password_entry = ctk.CTkEntry(frame, width=300, show="*")
        password_entry.pack(pady=5)
        
        ctk.CTkLabel(frame, text="Confirm Master Password:").pack(pady=(10, 5))
        confirm_entry = ctk.CTkEntry(frame, width=300, show="*")
        confirm_entry.pack(pady=5)
        
        # Show password toggle
        show_var = ctk.BooleanVar(value=False)
        
        def toggle_password():
            show_char = "" if show_var.get() else "*"
            password_entry.configure(show=show_char)
            confirm_entry.configure(show=show_char)
        
        show_checkbox = ctk.CTkCheckBox(frame, text="Show passwords",
                                       variable=show_var, command=toggle_password)
        show_checkbox.pack(pady=10)
        
        # Error label
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=5)
        
        def create_master_password():
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            # Validate inputs
            if not password:
                error_label.configure(text="Please enter a password")
                return
            
            if password != confirm:
                error_label.configure(text="Passwords do not match")
                return
            
            # Check password strength
            is_valid, error_msg = CryptoManager.validate_password_strength(password)
            if not is_valid:
                error_label.configure(text=error_msg)
                return
            
            # Create hash and store
            password_hash = CryptoManager.hash_master_password(password)
            self.db.set_master_password_hash(password_hash)
            
            # Initialize crypto manager
            self.crypto_manager = CryptoManager(password)
            self.is_locked = False
            
            messagebox.showinfo("Success", 
                              "Master Password created successfully!\n\n" +
                              "IMPORTANT: Back up these files:\n" +
                              "• vault.db\n• salt.key")
            
            self.show_main_dashboard()
        
        create_btn = ctk.CTkButton(frame, text="Create Master Password",
                                  command=create_master_password,
                                  font=("Helvetica", 14, "bold"),
                                  height=40)
        create_btn.pack(pady=20)
        
        # Bind Enter key
        confirm_entry.bind("<Return>", lambda e: create_master_password())
    
    # ==================== LOGIN SCREEN ====================
    
    def show_login_screen(self):
        """Display login screen for entering Master Password."""
        self.clear_window()
        
        frame = ctk.CTkFrame(self.root)
        frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(frame, text="🔐 Secure Password Manager",
                            font=("Helvetica", 24, "bold"))
        title.pack(pady=30)
        
        subtitle = ctk.CTkLabel(frame, text="Enter your Master Password to unlock",
                               font=("Helvetica", 12))
        subtitle.pack(pady=10)
        
        # Password input
        password_entry = ctk.CTkEntry(frame, width=300, show="*",
                                     font=("Helvetica", 14))
        password_entry.pack(pady=20)
        password_entry.focus()
        
        # Show password toggle
        show_var = ctk.BooleanVar(value=False)
        
        def toggle_password():
            password_entry.configure(show="" if show_var.get() else "*")
        
        show_checkbox = ctk.CTkCheckBox(frame, text="Show password",
                                       variable=show_var, command=toggle_password)
        show_checkbox.pack(pady=5)
        
        # Error label
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=5)
        
        def unlock_vault():
            password = password_entry.get()
            
            if not password:
                error_label.configure(text="Please enter your Master Password")
                return
            
            # Verify password
            stored_hash = self.db.get_master_password_hash()
            if not CryptoManager.verify_master_password(password, stored_hash):
                error_label.configure(text="Incorrect Master Password")
                password_entry.delete(0, 'end')
                return
            
            # Initialize crypto manager and unlock
            self.crypto_manager = CryptoManager(password)
            self.is_locked = False
            
            self.show_main_dashboard()
        
        unlock_btn = ctk.CTkButton(frame, text="Unlock Vault",
                                  command=unlock_vault,
                                  font=("Helvetica", 14, "bold"),
                                  height=40)
        unlock_btn.pack(pady=20)
        
        # Bind Enter key
        password_entry.bind("<Return>", lambda e: unlock_vault())
    
    # ==================== MAIN DASHBOARD ====================
    
    def show_main_dashboard(self):
        """Display the main dashboard with credentials and generator."""
        self.clear_window()
        self.reset_auto_lock()
        
        # Header frame
        header = ctk.CTkFrame(self.root, height=60)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="🔐 Password Vault (Unlocked)",
                            font=("Helvetica", 20, "bold"))
        title.pack(side="left", padx=20)
        
        lock_btn = ctk.CTkButton(header, text="🔒 Lock Vault",
                                command=self.lock_vault,
                                width=120)
        lock_btn.pack(side="right", padx=20)
        
        # Tab view
        tabview = ctk.CTkTabview(self.root)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        vault_tab = tabview.add("Vault")
        generator_tab = tabview.add("Generator")
        
        # Build tab contents
        self.build_vault_tab(vault_tab)
        self.build_generator_tab(generator_tab)
        
        # Track mouse movement for auto-lock
        self.root.bind("<Motion>", lambda e: self.reset_auto_lock())
        self.root.bind("<Key>", lambda e: self.reset_auto_lock())
    
    def build_vault_tab(self, parent):
        """Build the vault credentials list tab."""
        # Search frame
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by website or username...",
                                   width=400)
        search_entry.pack(side="left", padx=5)
        
        def search_credentials():
            query = search_entry.get().strip()
            if query:
                credentials = self.db.search_credentials(query)
            else:
                credentials = self.db.get_all_credentials()
            refresh_list(credentials)
        
        search_btn = ctk.CTkButton(search_frame, text="Search", command=search_credentials,
                                  width=100)
        search_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(search_frame, text="Clear", 
                                 command=lambda: [search_entry.delete(0, 'end'), search_credentials()],
                                 width=100)
        clear_btn.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(search_frame, text="+ Add New", 
                               command=lambda: self.show_add_edit_dialog(),
                               width=120, fg_color="green", hover_color="darkgreen")
        add_btn.pack(side="right", padx=5)
        
        # Scrollable credentials list
        list_frame = ctk.CTkScrollableFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        def refresh_list(credentials=None):
            """Refresh the credentials list."""
            # Clear existing
            for widget in list_frame.winfo_children():
                widget.destroy()
            
            if credentials is None:
                credentials = self.db.get_all_credentials()
            
            if not credentials:
                no_data = ctk.CTkLabel(list_frame, text="No credentials saved yet.\nClick '+ Add New' to get started!",
                                      font=("Helvetica", 14))
                no_data.pack(pady=50)
                return
            
            # Create credential cards
            for cred in credentials:
                self.create_credential_card(list_frame, cred, refresh_list)
        
        # Initial load
        refresh_list()
        
        # Bind Enter key to search
        search_entry.bind("<Return>", lambda e: search_credentials())
    
    def create_credential_card(self, parent, cred: dict, refresh_callback: Callable):
        """Create a credential card widget."""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(fill="x", padx=5, pady=5)
        
        # Left side: Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        website_label = ctk.CTkLabel(info_frame, text=cred['website'],
                                     font=("Helvetica", 16, "bold"))
        website_label.pack(anchor="w")
        
        username_label = ctk.CTkLabel(info_frame, text=f"👤 {cred['username']}",
                                      font=("Helvetica", 12))
        username_label.pack(anchor="w", pady=(3, 0))
        
        if cred.get('url'):
            url_label = ctk.CTkLabel(info_frame, text=f"🔗 {cred['url']}",
                                    font=("Helvetica", 10), text_color="gray")
            url_label.pack(anchor="w", pady=(3, 0))
        
        # Right side: Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        def copy_username():
            pyperclip.copy(cred['username'])
            messagebox.showinfo("Copied", f"Username copied to clipboard")
        
        def copy_password():
            decrypted = self.crypto_manager.decrypt(cred['encrypted_password'])
            pyperclip.copy(decrypted)
            
            # Auto-clear clipboard after 30 seconds
            if self.clipboard_timer:
                self.clipboard_timer.cancel()
            
            self.clipboard_timer = threading.Timer(30, lambda: pyperclip.copy(""))
            self.clipboard_timer.daemon = True
            self.clipboard_timer.start()
            
            messagebox.showinfo("Copied", "Password copied!\nClipboard will clear in 30 seconds.")
        
        def edit_credential():
            self.show_add_edit_dialog(cred, refresh_callback)
        
        def delete_credential():
            if messagebox.askyesno("Confirm Delete",
                                  f"Delete credential for {cred['website']}?"):
                self.db.delete_credential(cred['id'])
                refresh_callback()
        
        copy_user_btn = ctk.CTkButton(actions_frame, text="📋 Copy User",
                                     command=copy_username, width=110)
        copy_user_btn.grid(row=0, column=0, padx=3, pady=2)
        
        copy_pass_btn = ctk.CTkButton(actions_frame, text="🔑 Copy Password",
                                     command=copy_password, width=130,
                                     fg_color="purple", hover_color="darkviolet")
        copy_pass_btn.grid(row=0, column=1, padx=3, pady=2)
        
        edit_btn = ctk.CTkButton(actions_frame, text="✏️ Edit",
                                command=edit_credential, width=80)
        edit_btn.grid(row=1, column=0, padx=3, pady=2)
        
        delete_btn = ctk.CTkButton(actions_frame, text="🗑️ Delete",
                                  command=delete_credential, width=80,
                                  fg_color="darkred", hover_color="red")
        delete_btn.grid(row=1, column=1, padx=3, pady=2)
    
    def show_add_edit_dialog(self, credential: dict = None, refresh_callback: Callable = None):
        """Show dialog for adding or editing a credential."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Credential" if credential else "Add New Credential")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form fields
        ctk.CTkLabel(frame, text="Website/Service:").pack(anchor="w", pady=(0, 5))
        website_entry = ctk.CTkEntry(frame, width=450)
        website_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Username/Email:").pack(anchor="w", pady=(0, 5))
        username_entry = ctk.CTkEntry(frame, width=450)
        username_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Password:").pack(anchor="w", pady=(0, 5))
        
        password_frame = ctk.CTkFrame(frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 10))
        
        password_entry = ctk.CTkEntry(password_frame, width=350, show="*")
        password_entry.pack(side="left", padx=(0, 5))
        
        def generate_new_password():
            new_pass = generate_password(16)
            password_entry.delete(0, 'end')
            password_entry.insert(0, new_pass)
        
        gen_btn = ctk.CTkButton(password_frame, text="Generate",
                               command=generate_new_password, width=90)
        gen_btn.pack(side="left")
        
        ctk.CTkLabel(frame, text="URL (optional):").pack(anchor="w", pady=(0, 5))
        url_entry = ctk.CTkEntry(frame, width=450)
        url_entry.pack(pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Notes (optional):").pack(anchor="w", pady=(0, 5))
        notes_entry = ctk.CTkTextbox(frame, width=450, height=100)
        notes_entry.pack(pady=(0, 10))
        
        # Pre-fill if editing
        if credential:
            website_entry.insert(0, credential['website'])
            username_entry.insert(0, credential['username'])
            decrypted_pass = self.crypto_manager.decrypt(credential['encrypted_password'])
            password_entry.insert(0, decrypted_pass)
            url_entry.insert(0, credential.get('url', ''))
            notes_entry.insert("1.0", credential.get('notes', ''))
        
        # Error label
        error_label = ctk.CTkLabel(frame, text="", text_color="red")
        error_label.pack(pady=5)
        
        def save_credential():
            website = website_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get()
            url = url_entry.get().strip()
            notes = notes_entry.get("1.0", "end").strip()
            
            if not website or not username or not password:
                error_label.configure(text="Website, username, and password are required")
                return
            
            encrypted_pass = self.crypto_manager.encrypt(password)
            
            if credential:
                # Update existing
                self.db.update_credential(
                    credential['id'],
                    website=website,
                    username=username,
                    encrypted_password=encrypted_pass,
                    url=url,
                    notes=notes
                )
            else:
                # Add new
                self.db.add_credential(website, username, encrypted_pass, url, notes)
            
            dialog.destroy()
            if refresh_callback:
                refresh_callback()
        
        save_btn = ctk.CTkButton(frame, text="Save", command=save_credential,
                                font=("Helvetica", 14, "bold"),
                                height=40, fg_color="green", hover_color="darkgreen")
        save_btn.pack(pady=10)
        
        cancel_btn = ctk.CTkButton(frame, text="Cancel", command=dialog.destroy,
                                  height=35)
        cancel_btn.pack()
    
    def build_generator_tab(self, parent):
        """Build the password generator tab."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(frame, text="🎲 Password Generator",
                            font=("Helvetica", 20, "bold"))
        title.pack(pady=20)
        
        # Length slider
        length_label = ctk.CTkLabel(frame, text="Password Length: 16",
                                   font=("Helvetica", 14))
        length_label.pack(pady=(10, 5))
        
        length_slider = ctk.CTkSlider(frame, from_=12, to=64, number_of_steps=52,
                                     width=400)
        length_slider.set(16)
        length_slider.pack(pady=5)
        
        def update_length_label(value):
            length_label.configure(text=f"Password Length: {int(value)}")
        
        length_slider.configure(command=update_length_label)
        
        # Character type checkboxes
        options_frame = ctk.CTkFrame(frame, fg_color="transparent")
        options_frame.pack(pady=20)
        
        uppercase_var = ctk.BooleanVar(value=True)
        lowercase_var = ctk.BooleanVar(value=True)
        digits_var = ctk.BooleanVar(value=True)
        symbols_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(options_frame, text="Uppercase (A-Z)", variable=uppercase_var).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(options_frame, text="Lowercase (a-z)", variable=lowercase_var).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(options_frame, text="Digits (0-9)", variable=digits_var).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkCheckBox(options_frame, text="Symbols (!@#$...)", variable=symbols_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Generated password display
        password_display = ctk.CTkTextbox(frame, width=500, height=80,
                                         font=("Courier", 16, "bold"))
        password_display.pack(pady=20)
        password_display.insert("1.0", "Click 'Generate' to create a password")
        password_display.configure(state="disabled")
        
        # Strength indicator
        strength_label = ctk.CTkLabel(frame, text="", font=("Helvetica", 12))
        strength_label.pack(pady=5)
        
        def generate_new():
            try:
                length = int(length_slider.get())
                password = generate_password(
                    length=length,
                    use_uppercase=uppercase_var.get(),
                    use_lowercase=lowercase_var.get(),
                    use_digits=digits_var.get(),
                    use_symbols=symbols_var.get()
                )
                
                password_display.configure(state="normal")
                password_display.delete("1.0", "end")
                password_display.insert("1.0", password)
                password_display.configure(state="disabled")
                
                strength, entropy = estimate_password_strength(password)
                strength_label.configure(text=f"Strength: {strength} ({entropy:.1f} bits of entropy)")
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        def copy_generated():
            password = password_display.get("1.0", "end").strip()
            if password and password != "Click 'Generate' to create a password":
                pyperclip.copy(password)
                
                # Auto-clear clipboard
                if self.clipboard_timer:
                    self.clipboard_timer.cancel()
                
                self.clipboard_timer = threading.Timer(30, lambda: pyperclip.copy(""))
                self.clipboard_timer.daemon = True
                self.clipboard_timer.start()
                
                messagebox.showinfo("Copied", "Password copied!\nClipboard will clear in 30 seconds.")
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        generate_btn = ctk.CTkButton(btn_frame, text="🎲 Generate Password",
                                    command=generate_new,
                                    font=("Helvetica", 14, "bold"),
                                    width=200, height=45,
                                    fg_color="green", hover_color="darkgreen")
        generate_btn.grid(row=0, column=0, padx=10)
        
        copy_btn = ctk.CTkButton(btn_frame, text="📋 Copy to Clipboard",
                                command=copy_generated,
                                width=200, height=45,
                                fg_color="purple", hover_color="darkviolet")
        copy_btn.grid(row=0, column=1, padx=10)
    
    def lock_vault(self):
        """Lock the vault and return to login screen."""
        self.is_locked = True
        self.crypto_manager = None
        
        # Cancel timers
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
        if self.clipboard_timer:
            self.clipboard_timer.cancel()
        
        # Clear clipboard for security
        pyperclip.copy("")
        
        self.show_login_screen()
    
    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup on exit."""
        if hasattr(self, 'db'):
            self.db.close()


if __name__ == "__main__":
    app = PasswordManagerGUI()
    app.run()
