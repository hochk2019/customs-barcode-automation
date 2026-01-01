"""
Compact Status Bar Component

Single-row status bar with inline statistics display.
Max height: 40px

Requirements: 2.1, 2.2, 2.3, 2.4
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from datetime import datetime

from gui.styles import ModernStyles


class CompactStatusBar(ttk.Frame):
    """
    Compact single-row status bar with inline statistics.
    
    Layout: [Status: ● Ready | DB: ● Connected] [Processed: X | Retrieved: Y | Errors: Z | Last: HH:MM]
    Height: 40px max
    
    Requirements: 2.1, 2.2, 2.3, 2.4
    """
    
    # Maximum height constraint
    MAX_HEIGHT = 40
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize CompactStatusBar.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        # Configure height constraint
        self.configure(height=self.MAX_HEIGHT)
        self.pack_propagate(False)
        
        # Create main container
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create status bar widgets."""
        # Main horizontal container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left section: Status indicators
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # App status
        ttk.Label(
            status_frame,
            text="Status:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold")
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        self.status_indicator = ttk.Label(
            status_frame,
            text="● Ready",
            foreground=ModernStyles.SUCCESS_COLOR,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Separator
        ttk.Label(
            status_frame,
            text="|",
            foreground=ModernStyles.TEXT_SECONDARY
        ).pack(side=tk.LEFT, padx=5)
        
        # Database status
        ttk.Label(
            status_frame,
            text="DB:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold")
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        self.db_indicator = ttk.Label(
            status_frame,
            text="● Checking...",
            foreground=ModernStyles.WARNING_COLOR,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.db_indicator.pack(side=tk.LEFT)
        
        # Spacer to push buttons to right
        spacer = ttk.Frame(main_frame)
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Buttons section (right side)
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.db_config_btn = ttk.Button(
            buttons_frame,
            text="⚙ Cấu hình DB",
            width=14
        )
        self.db_config_btn.pack(side=tk.LEFT, padx=3)
        
        from gui.components.tooltip import ToolTip
        ToolTip(self.db_config_btn, "Cấu hình kết nối database ECUS5 để quét công ty và kiểm tra thông quan", delay=500)
        
        self.settings_btn = ttk.Button(
            buttons_frame,
            text="⚙ Cài đặt",
            width=12
        )
        self.settings_btn.pack(side=tk.LEFT, padx=3)
        ToolTip(self.settings_btn, "Mở cài đặt ứng dụng: phương thức lấy mã vạch, tự động kiểm tra, giao diện", delay=500)
    
    def update_status(self, status: str, is_ready: bool = True) -> None:
        """
        Update app status indicator.
        
        Args:
            status: Status text to display
            is_ready: True for green indicator, False for yellow
            
        Requirement: 2.4
        """
        color = ModernStyles.SUCCESS_COLOR if is_ready else ModernStyles.WARNING_COLOR
        self.status_indicator.configure(text=f"● {status}", foreground=color)
    
    def update_db_status(self, is_connected: bool, status_text: Optional[str] = None) -> None:
        """
        Update database connection status.
        
        Args:
            is_connected: True for connected (green), False for disconnected (red)
            status_text: Optional custom status text
            
        Requirement: 2.4
        """
        if status_text:
            text = f"● {status_text}"
        else:
            text = "● Connected" if is_connected else "● Disconnected"
        
        color = ModernStyles.SUCCESS_COLOR if is_connected else ModernStyles.ERROR_COLOR
        self.db_indicator.configure(text=text, foreground=color)
    
    def update_statistics(
        self,
        processed: int,
        retrieved: int,
        errors: int,
        last_run: Optional[datetime] = None
    ) -> None:
        """
        Update statistics display in inline format.
        
        Args:
            processed: Total processed count
            retrieved: Successfully retrieved count
            errors: Error count
            last_run: Last run datetime
            
        Requirement: 2.2
        """
        last_time = last_run.strftime("%H:%M") if last_run else "--:--"
        stats_text = f"Processed: {processed} | Retrieved: {retrieved} | Errors: {errors} | Last: {last_time}"
        self.stats_label.configure(text=stats_text)
    
    def format_statistics(
        self,
        processed: int,
        retrieved: int,
        errors: int,
        last_run: Optional[datetime] = None
    ) -> str:
        """
        Format statistics into inline string.
        
        Args:
            processed: Total processed count
            retrieved: Successfully retrieved count
            errors: Error count
            last_run: Last run datetime
            
        Returns:
            Formatted statistics string
            
        Requirement: 2.2 (Property 5)
        """
        last_time = last_run.strftime("%H:%M") if last_run else "--:--"
        return f"Processed: {processed} | Retrieved: {retrieved} | Errors: {errors} | Last: {last_time}"
    
    def set_db_config_command(self, command) -> None:
        """Set command for DB config button."""
        self.db_config_btn.configure(command=command)
    
    def set_settings_command(self, command) -> None:
        """Set command for Settings button."""
        self.settings_btn.configure(command=command)
