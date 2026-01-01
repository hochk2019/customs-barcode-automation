"""
Compact Company & Time Management Section Component

Compact section with company selection and date range.
Max height: 150px

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List
from datetime import datetime, timedelta
from tkcalendar import DateEntry

from gui.styles import ModernStyles
from gui.recent_companies_panel import RecentCompaniesPanel
from gui.autocomplete_combobox import AutocompleteCombobox
from gui.multi_select_company import MultiSelectCompany


class CompactCompanySection(ttk.LabelFrame):
    """
    Compact company and time management section.
    
    Layout:
    Row 1: [Quét công ty] [Làm mới] [Company Combo (expanded)] [Xóa]
    Row 2: [Recent: pill1 pill2 pill3 pill4 pill5]
    Row 3: [Từ ngày] [DatePicker] [đến ngày] [DatePicker]
    
    Height: 150px max
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    # Maximum height constraint (increased in v1.5.0 for multi-select)
    MAX_HEIGHT = 280
    
    # Compact dropdown height
    DROPDOWN_HEIGHT = 28
    
    def __init__(
        self,
        parent: tk.Widget,
        company_scanner=None,
        config_manager=None,
        on_company_selected: Optional[Callable[[str], None]] = None,
        on_companies_selected: Optional[Callable[[List[str]], None]] = None,  # v1.5.0: Multi-select
        on_scan_companies: Optional[Callable[[], None]] = None,
        on_refresh: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize CompactCompanySection.
        
        Args:
            parent: Parent widget
            company_scanner: CompanyScanner instance
            config_manager: ConfigurationManager instance
            on_company_selected: Callback when company is selected
            on_scan_companies: Callback for scan companies button
            on_refresh: Callback for refresh button
            **kwargs: Additional arguments for ttk.LabelFrame
        """
        super().__init__(parent, text="Quản lý công ty & thời gian", **kwargs)
        
        self.company_scanner = company_scanner
        self.config_manager = config_manager
        self.on_company_selected = on_company_selected
        self.on_companies_selected = on_companies_selected  # v1.5.0: Multi-select callback
        self.on_scan_companies = on_scan_companies
        self.on_refresh = on_refresh
        
        # Company list
        self._companies: List[str] = []
        
        # Configure height constraint
        self.configure(height=self.MAX_HEIGHT)
        self.pack_propagate(False)
        
        # Create widgets
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create company section widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Row 1: Buttons and Company Combo
        row1 = ttk.Frame(main_frame)
        row1.pack(fill=tk.X, pady=(0, 5))
        
        # Scan companies button
        self.scan_btn = ttk.Button(
            row1,
            text="🔍 Quét công ty",
            command=self._on_scan_click,
            width=14
        )
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 3))
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            row1,
            text="🔄 Làm mới",
            command=self._on_refresh_click,
            width=10
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Company combo (expandable) - Requirement 4.5
        self.company_var = tk.StringVar()
        self.company_combo = AutocompleteCombobox(
            row1,
            textvariable=self.company_var,
            height=self.DROPDOWN_HEIGHT,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.company_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_change)
        self.company_combo.bind("<Return>", self._on_company_change)
        
        # Clear button
        self.clear_btn = ttk.Button(
            row1,
            text="✕",
            command=self._clear_company,
            width=3
        )
        self.clear_btn.pack(side=tk.LEFT)
        
        # Row 2: Multi-select company list (v1.5.0)
        self.multi_select = MultiSelectCompany(
            main_frame,
            on_selection_changed=self._on_multi_select_changed
        )
        self.multi_select.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Row 3: Date range
        row3 = ttk.Frame(main_frame)
        row3.pack(fill=tk.X, pady=(5, 0))
        
        # From date
        ttk.Label(
            row3,
            text="Từ ngày:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        # Default: 1 day ago (changed from 7 days in v1.5.0)
        default_from = datetime.now() - timedelta(days=1)
        self.from_date = DateEntry(
            row3,
            width=12,
            date_pattern="dd/mm/yyyy",
            year=default_from.year,
            month=default_from.month,
            day=default_from.day,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.from_date.pack(side=tk.LEFT, padx=(0, 10))
        
        # To date
        ttk.Label(
            row3,
            text="đến ngày:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        # Default: today
        self.to_date = DateEntry(
            row3,
            width=12,
            date_pattern="dd/mm/yyyy",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.to_date.pack(side=tk.LEFT)
    
    def _on_scan_click(self) -> None:
        """Handle scan companies button click."""
        if self.on_scan_companies:
            self.on_scan_companies()
    
    def _on_refresh_click(self) -> None:
        """Handle refresh button click."""
        if self.on_refresh:
            self.on_refresh()
    
    def _on_company_change(self, event=None) -> None:
        """Handle company selection change (single-select combo, for quick search)."""
        tax_code = self.company_var.get().strip()
        if tax_code and self.on_company_selected:
            self.on_company_selected(tax_code)
    
    def _on_multi_select_changed(self, selected_companies: List[str]) -> None:
        """Handle multi-select company list change (v1.5.0)."""
        if self.on_companies_selected:
            self.on_companies_selected(selected_companies)
    
    def _clear_company(self) -> None:
        """Clear company selection."""
        self.company_var.set("")
    
    def set_companies(self, companies: List[str]) -> None:
        """
        Set available companies list.
        
        Args:
            companies: List of tax codes
        """
        self._companies = companies
        self.company_combo.set_completion_list(companies)
        # v1.5.0: Also update multi-select list
        self.multi_select.set_companies(companies)
    
    def get_selected_company(self) -> str:
        """
        Get currently selected company.
        
        Returns:
            Selected tax code or empty string
        """
        return self.company_var.get().strip()
    
    def set_selected_company(self, tax_code: str) -> None:
        """
        Set selected company.
        
        Args:
            tax_code: Tax code to select
        """
        self.company_var.set(tax_code)
    
    def get_date_range(self) -> tuple:
        """
        Get selected date range.
        
        Returns:
            Tuple of (from_date, to_date) as datetime objects
        """
        return (self.from_date.get_date(), self.to_date.get_date())
    
    def set_date_range(self, from_date: datetime, to_date: datetime) -> None:
        """
        Set date range.
        
        Args:
            from_date: Start date
            to_date: End date
        """
        self.from_date.set_date(from_date)
        self.to_date.set_date(to_date)
    
    def get_selected_companies(self) -> List[str]:
        """
        Get list of selected companies (v1.5.0 multi-select).
        
        Returns:
            List of selected tax codes
        """
        return self.multi_select.get_selected_companies()
    
    def set_scan_button_state(self, state: str) -> None:
        """
        Set scan button state.
        
        Args:
            state: 'normal' or 'disabled'
        """
        self.scan_btn.configure(state=state)
    
    def set_refresh_button_state(self, state: str) -> None:
        """
        Set refresh button state.
        
        Args:
            state: 'normal' or 'disabled'
        """
        self.refresh_btn.configure(state=state)
