"""
StatisticsBar Component

Bottom status bar showing download statistics.

Requirements: 7.1, 7.2, 10.1, 10.2, 10.3, 10.4
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from datetime import datetime

from gui.styles import ModernStyles


class StatisticsBar(ttk.Frame):
    """
    Bottom status bar showing download statistics.
    
    Displays:
    - Declarations Processed count
    - Barcodes Retrieved count
    - Errors count
    - Last Run timestamp
    
    Requirements: 7.1, 7.2, 10.1, 10.2, 10.3, 10.4
    """
    
    FIXED_HEIGHT = 35
    
    def __init__(self, parent: tk.Widget, **kwargs):
        """
        Initialize StatisticsBar.
        
        Args:
            parent: Parent widget
            **kwargs: Additional arguments for ttk.Frame
        """
        # Set fixed height
        super().__init__(parent, height=self.FIXED_HEIGHT, **kwargs)
        self.pack_propagate(False)  # Prevent children from changing frame size
        
        # Statistics variables
        self.processed_var = tk.StringVar(value="0")
        self.retrieved_var = tk.StringVar(value="0")
        self.errors_var = tk.StringVar(value="0")
        self.last_run_var = tk.StringVar(value="Never")
        
        # Internal counters
        self._processed = 0
        self._retrieved = 0
        self._errors = 0
        self._last_run: Optional[datetime] = None
        
        # Create UI
        self._create_labels()
    
    def _create_labels(self) -> None:
        """Create statistics labels."""
        # Container frame for centering
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Processed count
        ttk.Label(
            container,
            text="Declarations Processed:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT, padx=(5, 2))
        
        self.processed_label = ttk.Label(
            container,
            textvariable=self.processed_var,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold"),
            style='Info.TLabel'  # Use style for theme support
        )
        self.processed_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Retrieved count
        ttk.Label(
            container,
            text="Barcodes Retrieved:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT, padx=(5, 2))
        
        self.retrieved_label = ttk.Label(
            container,
            textvariable=self.retrieved_var,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold"),
            style='Success.TLabel'  # Use style for theme support
        )
        self.retrieved_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Errors count
        ttk.Label(
            container,
            text="Errors:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT, padx=(5, 2))
        
        self.errors_label = ttk.Label(
            container,
            textvariable=self.errors_var,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold"),
            style='Error.TLabel'  # Use style for theme support
        )
        self.errors_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Last run
        ttk.Label(
            container,
            text="Last Run:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        ).pack(side=tk.LEFT, padx=(5, 2))
        
        self.last_run_label = ttk.Label(
            container,
            textvariable=self.last_run_var,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL),
            style='Secondary.TLabel'  # Use style for theme support
        )
        self.last_run_label.pack(side=tk.LEFT, padx=(0, 5))
    
    def update_stats(
        self,
        processed: Optional[int] = None,
        retrieved: Optional[int] = None,
        errors: Optional[int] = None,
        last_run: Optional[datetime] = None
    ) -> None:
        """
        Update statistics display.
        
        Args:
            processed: Number of declarations processed
            retrieved: Number of barcodes retrieved
            errors: Number of errors
            last_run: Last run timestamp
            
        Requirements: 10.4
        """
        if processed is not None:
            self._processed = processed
            self.processed_var.set(str(processed))
        
        if retrieved is not None:
            self._retrieved = retrieved
            self.retrieved_var.set(str(retrieved))
        
        if errors is not None:
            self._errors = errors
            self.errors_var.set(str(errors))
        
        if last_run is not None:
            self._last_run = last_run
            self.last_run_var.set(last_run.strftime("%H:%M:%S %d/%m/%Y"))
    
    def increment_processed(self, count: int = 1) -> None:
        """
        Increment processed count.
        
        Args:
            count: Amount to increment (default 1)
        """
        self._processed += count
        self.processed_var.set(str(self._processed))
    
    def increment_retrieved(self, count: int = 1) -> None:
        """
        Increment retrieved count.
        
        Args:
            count: Amount to increment (default 1)
            
        Requirements: 10.1
        """
        self._retrieved += count
        self.retrieved_var.set(str(self._retrieved))
    
    def increment_errors(self, count: int = 1) -> None:
        """
        Increment errors count.
        
        Args:
            count: Amount to increment (default 1)
            
        Requirements: 10.2
        """
        self._errors += count
        self.errors_var.set(str(self._errors))
    
    def set_last_run(self, timestamp: Optional[datetime] = None) -> None:
        """
        Set last run timestamp.
        
        Args:
            timestamp: Timestamp to set (default: now)
            
        Requirements: 10.3
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self._last_run = timestamp
        self.last_run_var.set(timestamp.strftime("%H:%M:%S %d/%m/%Y"))
    
    def reset_stats(self) -> None:
        """Reset all statistics to zero."""
        self._processed = 0
        self._retrieved = 0
        self._errors = 0
        self._last_run = None
        
        self.processed_var.set("0")
        self.retrieved_var.set("0")
        self.errors_var.set("0")
        self.last_run_var.set("Never")
    
    def get_stats(self) -> dict:
        """
        Get current statistics.
        
        Returns:
            Dictionary with processed, retrieved, errors, last_run
        """
        return {
            'processed': self._processed,
            'retrieved': self._retrieved,
            'errors': self._errors,
            'last_run': self._last_run
        }
