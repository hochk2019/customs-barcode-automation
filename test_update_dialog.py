#!/usr/bin/env python3
"""
Test script for update dialog button sizing
"""

import tkinter as tk
from gui.update_dialog import DownloadProgressDialog, UpdateDialog, InstallPromptDialog
from update.models import UpdateInfo

def test_download_dialog():
    """Test the download progress dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create and show download dialog
    dialog = DownloadProgressDialog(root, "CustomsBarcodeAutomation_V1.3.4_Full.zip")
    
    # Keep dialog open for testing
    root.after(5000, root.destroy)  # Auto close after 5 seconds
    root.mainloop()

def test_update_dialog():
    """Test the main update dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create mock update info
    update_info = UpdateInfo(
        current_version="1.3.3",
        latest_version="1.3.4", 
        release_notes="Test release notes for button sizing",
        download_url="https://example.com/test.zip",
        file_size=1024000,
        release_date="2024-12-16"
    )
    
    # Create and show update dialog
    dialog = UpdateDialog(root, update_info)
    result = dialog.show()
    print(f"User selected: {result}")

def test_install_dialog():
    """Test the install prompt dialog"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    # Create and show install dialog
    dialog = InstallPromptDialog(root, "test_installer.exe")
    result = dialog.show()
    print(f"User selected: {result}")

if __name__ == "__main__":
    print("Testing download dialog...")
    test_download_dialog()