"""
RecentCompaniesPanel Component

Displays up to 5 recently used tax codes as quick-select buttons.

Requirements: 11.1, 11.2, 11.5
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable


class RecentCompaniesPanel(ttk.Frame):
    """
    Panel displaying recently used tax codes as quick-select buttons.
    
    Features:
    - Display up to 5 recent tax codes as buttons
    - Click button to select company
    - Auto-hide when no recent companies
    
    Requirements: 11.1, 11.2, 11.5
    """
    
    MAX_RECENT = 5
    
    def __init__(
        self,
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize RecentCompaniesPanel.
        
        Args:
            parent: Parent widget
            on_select: Callback when a tax code button is clicked
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.on_select = on_select
        self.buttons: List[ttk.Button] = []
        self.tax_codes: List[str] = []
        
        # Create label
        self.label = ttk.Label(self, text="Gần đây:", width=10)
        self.label.pack(side=tk.LEFT, padx=(5, 5))
        
        # Container for buttons
        self.button_container = ttk.Frame(self)
        self.button_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Initially hidden
        self.pack_forget()
    
    def update_recent(self, tax_codes: List[str]) -> None:
        """
        Update the recent companies buttons.
        
        Args:
            tax_codes: List of tax codes (max 5 will be displayed)
            
        Requirements: 11.1, 11.5
        """
        # Clear existing buttons
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # Store tax codes (limit to MAX_RECENT)
        self.tax_codes = tax_codes[:self.MAX_RECENT] if tax_codes else []
        
        # Hide if no recent companies (Requirement 11.5)
        if not self.tax_codes:
            self.pack_forget()
            return
        
        # Create new buttons for recent tax codes (Requirement 11.1)
        for tax_code in self.tax_codes:
            btn = ttk.Button(
                self.button_container,
                text=tax_code,
                command=lambda tc=tax_code: self._on_button_click(tc),
                width=12,
                style='Secondary.TButton'
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
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
        
        # Limit to MAX_RECENT
        self.tax_codes = self.tax_codes[:self.MAX_RECENT]
        
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
