"""
Multi-Select Company Component for v1.5.0

A listbox with checkboxes allowing selection of multiple companies.
Features:
- Checkbox selection for each company
- "Select all" option
- Counter showing selected/total
- Max selection limit (default 5, max 10)
- Persistence via UserPreferences
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable

from gui.styles import ModernStyles
from config.user_preferences import get_preferences


class MultiSelectCompany(ttk.LabelFrame):
    """
    Multi-select company listbox with checkboxes.
    
    Features:
    - Scrollable list of companies with checkboxes
    - Select all/none button
    - Selection counter
    - Max selection enforcement
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_selection_changed: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        """
        Initialize MultiSelectCompany.
        
        Args:
            parent: Parent widget
            on_selection_changed: Callback when selection changes
            **kwargs: Additional arguments for LabelFrame
        """
        super().__init__(parent, text="Chọn công ty", **kwargs)
        
        self.on_selection_changed = on_selection_changed
        self._companies: List[str] = []
        self._check_vars: dict = {}  # tax_code -> BooleanVar
        
        # Load preferences
        self.prefs = get_preferences()
        self.max_select = self.prefs.max_companies
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create component widgets."""
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        
        # Top row: Select all checkbox + counter
        top_row = ttk.Frame(main_frame)
        top_row.pack(fill=tk.X, pady=(0, 5))
        
        self.select_all_var = tk.BooleanVar(value=False)
        self.select_all_cb = ttk.Checkbutton(
            top_row,
            text="Chọn tất cả",
            variable=self.select_all_var,
            command=self._on_select_all_changed
        )
        self.select_all_cb.pack(side=tk.LEFT)
        
        self.counter_label = ttk.Label(
            top_row,
            text=f"Đã chọn: 0/{self.max_select}",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        )
        self.counter_label.pack(side=tk.RIGHT)
        
        # Scrollable frame for company list
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas + Scrollbar for scrolling
        self.canvas = tk.Canvas(
            list_container,
            highlightthickness=0,
            height=120  # Fixed height for 5 items approx
        )
        scrollbar = ttk.Scrollbar(
            list_container,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Make scrollable frame expand to canvas width
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    def _on_canvas_configure(self, event) -> None:
        """Expand scrollable frame to canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event) -> None:
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def set_companies(self, companies: List[str]) -> None:
        """
        Set list of available companies.
        
        Args:
            companies: List of tax codes
        """
        self._companies = companies
        self._check_vars.clear()
        
        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Load previously selected companies
        saved_selected = self.prefs.selected_companies
        
        # Create checkbox for each company
        for tax_code in companies:
            var = tk.BooleanVar(value=tax_code in saved_selected)
            self._check_vars[tax_code] = var
            
            cb = ttk.Checkbutton(
                self.scrollable_frame,
                text=tax_code,
                variable=var,
                command=lambda tc=tax_code: self._on_company_toggled(tc)
            )
            cb.pack(fill=tk.X, pady=1)
        
        self._update_counter()
    
    def _on_company_toggled(self, tax_code: str) -> None:
        """Handle individual company checkbox toggle."""
        selected = self.get_selected_companies()
        
        # Enforce max limit
        if len(selected) > self.max_select:
            # Revert the selection
            self._check_vars[tax_code].set(False)
            messagebox.showwarning(
                "Giới hạn chọn",
                f"Chỉ được chọn tối đa {self.max_select} công ty.\n"
                f"Bạn có thể thay đổi giới hạn này trong Cài đặt."
            )
            return
        
        self._update_counter()
        self._save_selection()
        
        if self.on_selection_changed:
            self.on_selection_changed(selected)
    
    def _on_select_all_changed(self) -> None:
        """Handle select all checkbox toggle."""
        select_all = self.select_all_var.get()
        
        if select_all:
            # Select up to max_select companies
            count = 0
            for tax_code, var in self._check_vars.items():
                if count < self.max_select:
                    var.set(True)
                    count += 1
                else:
                    var.set(False)
        else:
            # Deselect all
            for var in self._check_vars.values():
                var.set(False)
        
        self._update_counter()
        self._save_selection()
        
        if self.on_selection_changed:
            self.on_selection_changed(self.get_selected_companies())
    
    def _update_counter(self) -> None:
        """Update selection counter label."""
        selected_count = len(self.get_selected_companies())
        self.counter_label.config(text=f"Đã chọn: {selected_count}/{self.max_select}")
        
        # Update select all state
        if selected_count == 0:
            self.select_all_var.set(False)
        elif selected_count == len(self._companies) or selected_count == self.max_select:
            self.select_all_var.set(True)
    
    def _save_selection(self) -> None:
        """Save current selection to preferences."""
        selected = self.get_selected_companies()
        self.prefs.selected_companies = selected
    
    def get_selected_companies(self) -> List[str]:
        """
        Get list of selected company tax codes.
        
        Returns:
            List of selected tax codes
        """
        return [tc for tc, var in self._check_vars.items() if var.get()]
    
    def set_max_select(self, max_select: int) -> None:
        """
        Set maximum number of selectable companies.
        
        Args:
            max_select: Max number (1-10)
        """
        self.max_select = max(1, min(max_select, 10))
        self._update_counter()
