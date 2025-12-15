"""
Compact Output Directory Section Component

Single-row output directory section with path truncation.
Max height: 50px

Requirements: 3.1, 3.2, 3.3
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, Callable
import os
import subprocess
import platform

from gui.styles import ModernStyles


class CompactOutputSection(ttk.LabelFrame):
    """
    Compact output directory section.
    
    Layout: [Thư mục lưu:] [Path Entry (truncated)] [Chọn...] [Mở]
    Height: 50px max
    
    Requirements: 3.1, 3.2, 3.3
    """
    
    # Maximum height constraint
    MAX_HEIGHT = 50
    
    # Maximum display length for path before truncation
    MAX_PATH_DISPLAY_LENGTH = 50
    
    def __init__(
        self,
        parent: tk.Widget,
        initial_path: str = "",
        on_path_changed: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize CompactOutputSection.
        
        Args:
            parent: Parent widget
            initial_path: Initial output path
            on_path_changed: Callback when path changes
            **kwargs: Additional arguments for ttk.LabelFrame
        """
        super().__init__(parent, text="Thư mục lưu file", **kwargs)
        
        self._full_path = initial_path
        self.on_path_changed = on_path_changed
        
        # Configure height constraint
        self.configure(height=self.MAX_HEIGHT)
        self.pack_propagate(False)
        
        # Create widgets
        self._create_widgets()
        
        # Set initial path
        if initial_path:
            self.set_output_path(initial_path)
    
    def _create_widgets(self) -> None:
        """Create output section widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Path entry (expandable)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(
            main_frame,
            textvariable=self.path_var,
            state="readonly",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bind tooltip for full path
        self.path_entry.bind("<Enter>", self._show_tooltip)
        self.path_entry.bind("<Leave>", self._hide_tooltip)
        self._tooltip = None
        
        # Browse button
        self.browse_btn = ttk.Button(
            main_frame,
            text="Chọn...",
            command=self._browse_directory,
            width=8
        )
        self.browse_btn.pack(side=tk.LEFT, padx=2)
        
        # Open folder button
        self.open_btn = ttk.Button(
            main_frame,
            text="Mở",
            command=self._open_directory,
            width=6
        )
        self.open_btn.pack(side=tk.LEFT, padx=2)
    
    def _browse_directory(self) -> None:
        """Open directory selection dialog."""
        initial_dir = self._full_path if os.path.exists(self._full_path) else None
        
        directory = filedialog.askdirectory(
            title="Chọn thư mục lưu file",
            initialdir=initial_dir
        )
        
        if directory:
            self.set_output_path(directory)
            if self.on_path_changed:
                self.on_path_changed(directory)
    
    def _open_directory(self) -> None:
        """Open output directory in file explorer."""
        if not self._full_path or not os.path.exists(self._full_path):
            return
        
        try:
            if platform.system() == "Windows":
                os.startfile(self._full_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self._full_path])
            else:  # Linux
                subprocess.run(["xdg-open", self._full_path])
        except Exception:
            pass
    
    def get_output_path(self) -> str:
        """
        Get current output path (full path).
        
        Returns:
            Full output path
        """
        return self._full_path
    
    def set_output_path(self, path: str) -> None:
        """
        Set output path with truncation for display.
        
        Args:
            path: Full path to set
            
        Requirement: 3.3
        """
        self._full_path = path
        truncated = self.truncate_path(path, self.MAX_PATH_DISPLAY_LENGTH)
        self.path_var.set(truncated)
    
    @staticmethod
    def truncate_path(path: str, max_length: int = 50) -> str:
        """
        Truncate path with ellipsis, preserving the end (folder/filename).
        
        Args:
            path: Full path to truncate
            max_length: Maximum display length
            
        Returns:
            Truncated path with "..." prefix if needed
            
        Requirement: 3.3 (Property 6)
        """
        if not path or len(path) <= max_length:
            return path
        
        # Preserve the last part of the path
        # Find a good break point (path separator)
        path_parts = path.replace("\\", "/").split("/")
        
        # Start from the end and build up
        result = path_parts[-1] if path_parts else ""
        
        for i in range(len(path_parts) - 2, -1, -1):
            candidate = path_parts[i] + "/" + result
            if len(candidate) + 3 > max_length:  # +3 for "..."
                break
            result = candidate
        
        # Add ellipsis if truncated
        if len(result) < len(path):
            result = "..." + result
        
        return result
    
    def _show_tooltip(self, event) -> None:
        """Show tooltip with full path."""
        if not self._full_path:
            return
        
        # Create tooltip window
        self._tooltip = tk.Toplevel(self)
        self._tooltip.wm_overrideredirect(True)
        
        # Position tooltip below the entry
        x = self.path_entry.winfo_rootx()
        y = self.path_entry.winfo_rooty() + self.path_entry.winfo_height() + 2
        self._tooltip.wm_geometry(f"+{x}+{y}")
        
        # Tooltip label
        label = tk.Label(
            self._tooltip,
            text=self._full_path,
            background="#FFFFE0",
            relief="solid",
            borderwidth=1,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL),
            padx=5,
            pady=2
        )
        label.pack()
    
    def _hide_tooltip(self, event) -> None:
        """Hide tooltip."""
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None
