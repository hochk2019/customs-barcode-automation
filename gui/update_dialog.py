"""
Update dialog for displaying update information and download progress.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import threading

from update.models import UpdateInfo, DownloadProgress

logger = logging.getLogger(__name__)


class UpdateDialog:
    """Dialog for displaying update information."""
    
    def __init__(self, parent: tk.Tk, update_info: UpdateInfo):
        """
        Initialize update dialog.
        
        Args:
            parent: Parent window
            update_info: Information about the available update
        """
        self.parent = parent
        self.update_info = update_info
        self.result: Optional[str] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cập nhật phần mềm")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("500x400")
        self._center_dialog()
        
        self._create_widgets()
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Có phiên bản mới!",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))

        # Version info
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(version_frame, text="Phiên bản hiện tại:").pack(side=tk.LEFT)
        ttk.Label(version_frame, text=self.update_info.current_version, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(version_frame, text="→").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(version_frame, text="Phiên bản mới:").pack(side=tk.LEFT)
        ttk.Label(version_frame, text=self.update_info.latest_version, font=('Segoe UI', 10, 'bold'), style='Success.TLabel').pack(side=tk.LEFT, padx=5)
        
        # Release notes
        notes_label = ttk.Label(main_frame, text="Nội dung cập nhật:")
        notes_label.pack(anchor=tk.W, pady=(15, 5))
        
        notes_frame = ttk.Frame(main_frame)
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        self.notes_text = tk.Text(notes_frame, wrap=tk.WORD, height=10, width=50)
        scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=scrollbar.set)
        
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notes_text.insert(tk.END, self.update_info.release_notes or "Không có thông tin chi tiết.")
        self.notes_text.configure(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="Cập nhật ngay",
            command=self._on_update_now
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Nhắc lại sau",
            command=self._on_remind_later
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Bỏ qua phiên bản này",
            command=self._on_skip_version
        ).pack(side=tk.LEFT, padx=5)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_remind_later)
    
    def _on_update_now(self):
        """Handle 'Update Now' button click."""
        self.result = "update_now"
        self.dialog.destroy()
    
    def _on_remind_later(self):
        """Handle 'Remind Later' button click."""
        self.result = "remind_later"
        self.dialog.destroy()
    
    def _on_skip_version(self):
        """Handle 'Skip Version' button click."""
        self.result = "skip_version"
        self.dialog.destroy()
    
    def show(self) -> str:
        """
        Show dialog and wait for user response.
        
        Returns:
            "update_now" | "remind_later" | "skip_version"
        """
        self.dialog.wait_window()
        return self.result or "remind_later"


class DownloadProgressDialog:
    """Dialog for showing download progress."""
    
    def __init__(self, parent: tk.Tk, filename: str):
        """
        Initialize download progress dialog.
        
        Args:
            parent: Parent window
            filename: Name of file being downloaded
        """
        self.parent = parent
        self.filename = filename
        self.cancelled = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Đang tải xuống...")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("400x150")
        self._center_dialog()
        
        self._create_widgets()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filename label
        self.filename_label = ttk.Label(main_frame, text=f"Đang tải: {self.filename}")
        self.filename_label.pack(anchor=tk.W)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, length=350, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Đang chuẩn bị...")
        self.status_label.pack(anchor=tk.W)
        
        # Cancel button
        self.cancel_button = ttk.Button(main_frame, text="Hủy", command=self._on_cancel)
        self.cancel_button.pack(pady=(10, 0))
    
    def update_progress(self, progress: DownloadProgress):
        """
        Update progress display.
        
        Args:
            progress: Current download progress
        """
        if self.cancelled:
            return
        
        self.progress_bar['value'] = progress.percentage
        
        # Format downloaded size
        downloaded_mb = progress.downloaded_bytes / (1024 * 1024)
        total_mb = progress.total_bytes / (1024 * 1024)
        
        status_text = f"{downloaded_mb:.1f} MB / {total_mb:.1f} MB ({progress.percentage:.1f}%) - {progress.speed_text}"
        self.status_label.configure(text=status_text)
        
        self.dialog.update()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.dialog.destroy()
    
    def close(self):
        """Close the dialog."""
        if self.dialog.winfo_exists():
            self.dialog.destroy()


class InstallPromptDialog:
    """Dialog for prompting user to install now or later."""
    
    def __init__(self, parent: tk.Tk, installer_path: str):
        """
        Initialize install prompt dialog.
        
        Args:
            parent: Parent window
            installer_path: Path to downloaded installer
        """
        self.parent = parent
        self.installer_path = installer_path
        self.result: Optional[str] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cài đặt cập nhật")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.dialog.geometry("350x150")
        self._center_dialog()
        
        self._create_widgets()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_install_later)
    
    def _center_dialog(self):
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        message_label = ttk.Label(
            main_frame,
            text="Tải xuống hoàn tất!\nBạn muốn cài đặt ngay bây giờ?",
            justify=tk.CENTER
        )
        message_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        ttk.Button(
            button_frame,
            text="Cài đặt ngay",
            command=self._on_install_now
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame,
            text="Cài đặt sau",
            command=self._on_install_later
        ).pack(side=tk.LEFT, padx=10)
    
    def _on_install_now(self):
        """Handle 'Install Now' button click."""
        self.result = "install_now"
        self.dialog.destroy()
    
    def _on_install_later(self):
        """Handle 'Install Later' button click."""
        self.result = "install_later"
        self.dialog.destroy()
    
    def show(self) -> str:
        """
        Show dialog and wait for user response.
        
        Returns:
            "install_now" | "install_later"
        """
        self.dialog.wait_window()
        return self.result or "install_later"
