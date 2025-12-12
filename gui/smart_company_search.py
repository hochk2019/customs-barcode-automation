"""
Smart Company Search Component

This module provides a smart search component that filters and auto-selects
companies based on user input. It supports searching by company name or tax code.

Requirements: 3.1, 3.2, 3.3
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass


@dataclass
class Company:
    """Company data model for smart search"""
    tax_code: str
    name: str
    
    @property
    def display_text(self) -> str:
        """Get display text for dropdown: 'TaxCode - CompanyName'"""
        return f"{self.tax_code} - {self.name}"
    
    def matches(self, search_text: str) -> bool:
        """
        Check if company matches search text (case-insensitive)
        
        Args:
            search_text: Text to search for
            
        Returns:
            True if tax_code or name contains search_text
        """
        search_lower = search_text.lower()
        return (search_lower in self.tax_code.lower() or 
                search_lower in self.name.lower())
    
    def exact_match(self, search_text: str) -> bool:
        """
        Check if company exactly matches search text (case-insensitive)
        
        Args:
            search_text: Text to match
            
        Returns:
            True if tax_code or name exactly equals search_text
        """
        search_lower = search_text.lower().strip()
        return (search_lower == self.tax_code.lower() or 
                search_lower == self.name.lower())


class SmartCompanySearchLogic:
    """
    Core logic for smart company search (UI-independent)
    
    This class contains the filtering and auto-select logic that can be
    tested without requiring a tkinter root window.
    
    Requirements: 3.1, 3.2, 3.3
    """
    
    ALL_COMPANIES_OPTION = "Tất cả công ty"
    
    def __init__(self):
        """Initialize SmartCompanySearchLogic"""
        self.all_companies: List[Company] = []
        self._filtered_companies: List[Company] = []
        self._selected_company: Optional[Company] = None
    
    def set_companies(self, companies: List[Tuple[str, str]]) -> None:
        """
        Set the list of companies for searching
        
        Args:
            companies: List of (tax_code, company_name) tuples
        """
        self.all_companies = [
            Company(tax_code=tc, name=name) 
            for tc, name in companies
        ]
        self._filtered_companies = self.all_companies.copy()
        self._selected_company = None
    
    def filter_companies(self, search_text: str) -> List[Company]:
        """
        Filter companies by name or tax code (case-insensitive)
        
        Args:
            search_text: Text to filter by
            
        Returns:
            List of matching companies
            
        Requirements: 3.1 - WHEN a user types in the Smart_Search field 
        THEN the System SHALL filter the company dropdown to show matching companies
        """
        if not search_text or not search_text.strip():
            # Return all companies if search is empty
            return self.all_companies.copy()
        
        search_text = search_text.strip()
        
        # Filter companies where tax_code or name contains search text
        return [
            company for company in self.all_companies
            if company.matches(search_text)
        ]
    
    def auto_select_if_exact_match(self, search_text: str) -> bool:
        """
        Auto-select company if exact match found
        
        Args:
            search_text: Text to match
            
        Returns:
            True if a company was auto-selected, False otherwise
            
        Requirements: 3.2 - WHEN the typed text exactly matches a single company 
        name or Tax_Code THEN the System SHALL auto-select that company
        """
        if not search_text or not search_text.strip():
            return False
        
        search_text = search_text.strip()
        
        # Find companies with exact match
        exact_matches = [
            company for company in self.all_companies
            if company.exact_match(search_text)
        ]
        
        # Auto-select only if exactly one match
        if len(exact_matches) == 1:
            self._selected_company = exact_matches[0]
            return True
        
        return False
    
    def get_selected_company(self) -> Optional[Company]:
        """
        Get currently selected company
        
        Returns:
            Selected Company or None if "all companies" is selected
        """
        return self._selected_company
    
    def get_selected_tax_code(self) -> Optional[str]:
        """
        Get tax code of selected company
        
        Returns:
            Tax code string or None if "all companies" is selected
        """
        return self._selected_company.tax_code if self._selected_company else None
    
    def get_filtered_companies(self) -> List[Company]:
        """
        Get current filtered company list
        
        Returns:
            List of filtered companies
        """
        return self._filtered_companies.copy()
    
    def clear_selection(self) -> None:
        """Clear the current selection"""
        self._selected_company = None
    
    @property
    def company_count(self) -> int:
        """Get total number of companies"""
        return len(self.all_companies)
    
    @property
    def filtered_count(self) -> int:
        """Get number of filtered companies"""
        return len(self._filtered_companies)


class SmartCompanySearch:
    """
    Smart search component that filters and auto-selects companies
    
    Features:
    - Real-time filtering as user types
    - Auto-select on exact match (tax code or company name)
    - Case-insensitive search
    - Maintains "Tất cả công ty" option
    
    Requirements: 3.1, 3.2, 3.3
    """
    
    ALL_COMPANIES_OPTION = "Tất cả công ty"
    
    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        on_company_selected: Optional[Callable[[Optional[Company]], None]] = None,
        on_filter_changed: Optional[Callable[[List[Company]], None]] = None
    ):
        """
        Initialize SmartCompanySearch
        
        Args:
            parent: Parent widget (can be None for testing)
            on_company_selected: Callback when a company is selected (None for "all")
            on_filter_changed: Callback when filter results change
        """
        self.parent = parent
        self.on_company_selected = on_company_selected
        self.on_filter_changed = on_filter_changed
        
        # Core logic (UI-independent)
        self._logic = SmartCompanySearchLogic()
        
        # UI variables (only created if parent is provided)
        self.search_var: Optional[tk.StringVar] = None
        self.company_var: Optional[tk.StringVar] = None
        
        # Track if we're programmatically updating to avoid recursive events
        self._updating = False
        
        # Initialize UI if parent is provided
        if parent is not None:
            self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize UI components (requires tkinter root)"""
        self.search_var = tk.StringVar()
        self.company_var = tk.StringVar()
    
    # Delegate to logic class for core functionality
    
    def set_companies(self, companies: List[Tuple[str, str]]) -> None:
        """
        Set the list of companies for searching
        
        Args:
            companies: List of (tax_code, company_name) tuples
        """
        self._logic.set_companies(companies)
        
        # Clear search and reset dropdown
        if self.search_var:
            self.search_var.set('')
        self._update_dropdown_values()
    
    def filter_companies(self, search_text: str) -> List[Company]:
        """
        Filter companies by name or tax code (case-insensitive)
        
        Args:
            search_text: Text to filter by
            
        Returns:
            List of matching companies
        """
        return self._logic.filter_companies(search_text)
    
    def auto_select_if_exact_match(self, search_text: str) -> bool:
        """
        Auto-select company if exact match found
        
        Args:
            search_text: Text to match
            
        Returns:
            True if a company was auto-selected, False otherwise
        """
        result = self._logic.auto_select_if_exact_match(search_text)
        
        if result and self.company_var:
            company = self._logic.get_selected_company()
            if company:
                self._updating = True
                try:
                    self.company_var.set(company.display_text)
                    if self.on_company_selected:
                        self.on_company_selected(company)
                finally:
                    self._updating = False
        
        return result
    
    def _select_company(self, company: Optional[Company]) -> None:
        """
        Select a company in the dropdown
        
        Args:
            company: Company to select, or None for "all companies"
        """
        self._updating = True
        try:
            self._logic._selected_company = company
            
            if self.company_var:
                if company is None:
                    self.company_var.set(self.ALL_COMPANIES_OPTION)
                else:
                    self.company_var.set(company.display_text)
            
            # Notify callback
            if self.on_company_selected:
                self.on_company_selected(company)
        finally:
            self._updating = False
    
    def _update_dropdown_values(self) -> None:
        """Update dropdown values based on filtered companies"""
        values = [self.ALL_COMPANIES_OPTION]
        values.extend([c.display_text for c in self._logic._filtered_companies])
        
        if hasattr(self, 'company_combo') and self.company_combo:
            self.company_combo['values'] = values
            
            # Reset to "all" if current selection not in filtered list
            if self.company_var:
                current = self.company_var.get()
                if current not in values:
                    self.company_combo.current(0)
    
    def on_search_changed(self, event=None) -> None:
        """
        Handle search text change - filter and auto-select
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        if self._updating:
            return
        
        search_text = self.search_var.get() if self.search_var else ""
        
        # Filter companies
        self._logic._filtered_companies = self._logic.filter_companies(search_text)
        
        # Update dropdown
        self._update_dropdown_values()
        
        # Notify filter changed
        if self.on_filter_changed:
            self.on_filter_changed(self._logic._filtered_companies)
        
        # Try auto-select on exact match
        if search_text and search_text.strip():
            self.auto_select_if_exact_match(search_text)
    
    def clear_search(self) -> None:
        """
        Clear search input and restore full company list
        
        Requirements: 3.5 - WHEN the Smart_Search field is cleared 
        THEN the System SHALL reset the dropdown to show all companies
        """
        self._updating = True
        try:
            if self.search_var:
                self.search_var.set('')
            self._logic._filtered_companies = self._logic.all_companies.copy()
            self._update_dropdown_values()
            
            # Reset to "all companies"
            if hasattr(self, 'company_combo') and self.company_combo:
                self.company_combo.current(0)
            
            # Notify filter changed
            if self.on_filter_changed:
                self.on_filter_changed(self._logic._filtered_companies)
        finally:
            self._updating = False
    
    def get_selected_company(self) -> Optional[Company]:
        """
        Get currently selected company
        
        Returns:
            Selected Company or None if "all companies" is selected
        """
        if self.company_var:
            selection = self.company_var.get()
            
            if not selection or selection == self.ALL_COMPANIES_OPTION:
                return None
            
            # Find company by display text
            for company in self._logic.all_companies:
                if company.display_text == selection:
                    return company
        
        return self._logic.get_selected_company()
    
    def get_selected_tax_code(self) -> Optional[str]:
        """
        Get tax code of selected company
        
        Returns:
            Tax code string or None if "all companies" is selected
        """
        company = self.get_selected_company()
        return company.tax_code if company else None
    
    def get_filtered_companies(self) -> List[Company]:
        """
        Get current filtered company list
        
        Returns:
            List of filtered companies
        """
        return self._logic.get_filtered_companies()
    
    @property
    def all_companies(self) -> List[Company]:
        """Get all companies"""
        return self._logic.all_companies
    
    @property
    def company_count(self) -> int:
        """Get total number of companies"""
        return self._logic.company_count
    
    @property
    def filtered_count(self) -> int:
        """Get number of filtered companies"""
        return self._logic.filtered_count
