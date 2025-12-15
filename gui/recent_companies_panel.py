"""
RecentCompaniesPanel Component

Displays recently used tax codes as quick-select pill buttons.
Supports configurable max count (3-10, default 5).

Requirements: 6.4, 6.5, 11.1, 11.2, 11.5
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from config.configuration_manager import ConfigurationManager


class RecentCompaniesPanel(ttk.Frame):
    """
    Panel displaying recently used tax codes as quick-select pill buttons.
    
    Features:
    - Display configurable number of recent tax codes (3-10, default 5)
    - Pill-shaped button styling
    - Click button to select company
    - Auto-hide when no recent companies
    
    Requirements: 6.4, 6.5, 11.1, 11.2, 11.5
    """
    
    # Default max recent count
    DEFAULT_MAX_RECENT = 5
    MIN_RECENT = 3
    MAX_RECENT_LIMIT = 10
    
    def __init__(
        self,
        parent: tk.Widget,
        config_manager: Optional['ConfigurationManager'] = None,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize RecentCompaniesPanel.
        
        Args:
            parent: Parent widget
            config_manager: ConfigurationManager for loading max count setting
            on_select: Callback when a tax code button is clicked
            **kwargs: Additional arguments for ttk.Frame
            
        Requirements: 6.4
        """
        super().__init__(parent, **kwargs)
        
        self.config_manager = config_manager
        self.on_select = on_select
        self.buttons: List[ttk.Button] = []
        self.tax_codes: List[str] = []
        
        # Load max recent count from config (Requirement 6.4)
        self._max_recent = self._load_max_recent()
        
        # Create header row with label
        header_row = ttk.Frame(self)
        header_row.pack(fill=tk.X, pady=(0, 2))
        
        self.label = ttk.Label(header_row, text="Gần đây:")
        self.label.pack(side=tk.LEFT, padx=(5, 5))
        
        # Container for buttons - uses grid for wrapping
        self.button_container = ttk.Frame(self)
        self.button_container.pack(fill=tk.X, expand=True, padx=5)
        
        # Initially hidden
        self.pack_forget()
    
    def _load_max_recent(self) -> int:
        """
        Load max recent count from config.
        
        Returns:
            Max recent count (3-10, default 5)
            
        Requirement: 6.4
        """
        if self.config_manager:
            try:
                return self.config_manager.get_recent_companies_count()
            except Exception:
                pass
        return self.DEFAULT_MAX_RECENT
    
    @property
    def max_recent(self) -> int:
        """Get current max recent count."""
        return self._max_recent
    
    def set_max_recent(self, count: int) -> None:
        """
        Update max recent count and refresh display.
        
        Args:
            count: New max count (will be clamped to 3-10)
            
        Requirement: 6.5
        """
        # Clamp to valid range
        count = max(self.MIN_RECENT, min(self.MAX_RECENT_LIMIT, count))
        self._max_recent = count
        
        # Trim tax codes if needed and refresh display
        if len(self.tax_codes) > count:
            self.tax_codes = self.tax_codes[:count]
        
        self.update_recent(self.tax_codes)
    
    def update_recent(self, tax_codes: List[str]) -> None:
        """
        Update the recent companies buttons.
        
        Args:
            tax_codes: List of tax codes (limited to max_recent)
            
        Requirements: 6.5, 11.1, 11.5
        """
        # Clear existing buttons
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # Store tax codes (limit to max_recent)
        self.tax_codes = tax_codes[:self._max_recent] if tax_codes else []
        
        # Hide if no recent companies (Requirement 11.5)
        if not self.tax_codes:
            self.pack_forget()
            return
        
        # Create new pill-shaped buttons for recent tax codes (Requirements 4.3, 11.1)
        # Use grid layout for automatic wrapping when many buttons
        # Layout: 5 buttons per row to prevent overflow
        buttons_per_row = 5
        for idx, tax_code in enumerate(self.tax_codes):
            row = idx // buttons_per_row
            col = idx % buttons_per_row
            
            btn = ttk.Button(
                self.button_container,
                text=tax_code,
                command=lambda tc=tax_code: self._on_button_click(tc),
                width=12,
                style='Pill.TButton'  # Pill-shaped style
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='w')
            self.buttons.append(btn)
        
        # Show panel
        self.pack(fill=tk.X, pady=(2, 5))
    
    def _on_button_click(self, tax_code: str) -> None:
        """
        Handle button click.
        
        Args:
            tax_code: The tax code of the clicked button
            
        Requirements: 11.2
        """
        if self.on_select:
            self.on_select(tax_code)
    
    def add_recent(self, tax_code: str) -> None:
        """
        Add a tax code to the recent list.
        
        If already exists, moves it to the front.
        
        Args:
            tax_code: Tax code to add
        """
        if not tax_code:
            return
        
        # Remove if already exists
        if tax_code in self.tax_codes:
            self.tax_codes.remove(tax_code)
        
        # Add to front
        self.tax_codes.insert(0, tax_code)
        
        # Limit to max_recent
        self.tax_codes = self.tax_codes[:self._max_recent]
        
        # Update display
        self.update_recent(self.tax_codes)
    
    def get_recent(self) -> List[str]:
        """
        Get list of recent tax codes.
        
        Returns:
            List of recent tax codes
        """
        return self.tax_codes.copy()
    
    def clear(self) -> None:
        """Clear all recent companies."""
        self.update_recent([])
