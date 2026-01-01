"""
Company Tag Picker Component for v1.5.0

A compact component allowing selection of multiple companies as "tags/pills".
Features:
- Uses existing search dropdown at top
- "Add" button to add selected company to list
- Selected companies displayed as removable pills/chips
- Counter showing selected/max limit
- Persistence via UserPreferences
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable

from gui.styles import ModernStyles
from config.user_preferences import get_preferences


class CompanyTagPicker(ttk.Frame):
    """
    Compact company tag picker for multi-select.
    
    Layout:
    [Search dropdown ▼] [+ Thêm]
    
    Đã chọn (2/5):
    [2300944637 ✕] [0100034438 ✕] [2301121587 ✕]
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_selection_changed: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        """
        Initialize CompanyTagPicker.
        
        Args:
            parent: Parent widget
            on_selection_changed: Callback when selection changes
        """
        super().__init__(parent, **kwargs)
        
        self.on_selection_changed = on_selection_changed
        self._companies: List[str] = []  # Available companies
        self._selected: List[str] = []   # Selected companies
        
        # Load preferences
        self.prefs = get_preferences()
        self.max_select = self.prefs.max_companies
        
        # Load previously selected companies
        self._selected = self.prefs.selected_companies.copy()
        
        self._create_widgets()
        self._update_pills()
    
    def _create_widgets(self) -> None:
        """Create component widgets."""
        # Header with counter
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.counter_label = ttk.Label(
            header_frame,
            text=f"Đã chọn: {len(self._selected)}/{self.max_select} công ty",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL, 'bold'),
            foreground=ModernStyles.SUCCESS_COLOR if self._selected else '#666666'
        )
        self.counter_label.pack(side=tk.LEFT)
        
        # Clear all button
        self.clear_all_btn = ttk.Button(
            header_frame,
            text="Xóa tất cả",
            command=self._clear_all,
            width=10,
            style='Secondary.TButton'
        )
        self.clear_all_btn.pack(side=tk.RIGHT)
        
        from gui.components.tooltip import ToolTip
        ToolTip(self.clear_all_btn, "Xóa tất cả công ty đã chọn khỏi danh sách lọc", delay=500)
        
        # Pills container (selected companies)
        self.pills_frame = ttk.Frame(self)
        self.pills_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Placeholder text when empty
        self.empty_label = ttk.Label(
            self.pills_frame,
            text="Chưa chọn công ty nào. Tìm và thêm công ty ở trên.",
            foreground='#888888',
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
        )
    
    def _update_pills(self) -> None:
        """Update the pills display."""
        # Clear existing pills
        for widget in self.pills_frame.winfo_children():
            widget.destroy()
        
        if not self._selected:
            # Show empty message
            self.empty_label = ttk.Label(
                self.pills_frame,
                text="Chưa chọn công ty nào. Tìm và thêm công ty ở trên.",
                foreground='#888888',
                font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL)
            )
            self.empty_label.pack(anchor=tk.W)
        else:
            # Create pills for each selected company
            row_frame = ttk.Frame(self.pills_frame)
            row_frame.pack(fill=tk.X, anchor=tk.W)
            
            current_width = 0
            max_width = 400  # Approximate max width before wrapping
            
            for tax_code in self._selected:
                # Create pill
                pill = self._create_pill(row_frame, tax_code)
                pill.pack(side=tk.LEFT, padx=(0, 5), pady=2)
                # Force update immediately after pack
                pill.update_idletasks()
                
                # Simple wrap logic
                current_width += 120
                if current_width > max_width:
                    row_frame = ttk.Frame(self.pills_frame)
                    row_frame.pack(fill=tk.X, anchor=tk.W)
                    current_width = 0
        
        # Update counter
        count = len(self._selected)
        self.counter_label.config(
            text=f"Đã chọn: {count}/{self.max_select} công ty",
            foreground=ModernStyles.SUCCESS_COLOR if count > 0 else '#666666'
        )
        
        # Windows workaround: Force pill colors after update with delay
        if self._selected:
            self.after(100, self._force_pill_colors)
    
    def _create_pill(self, parent: tk.Widget, tax_code: str) -> tk.Frame:
        """Create a pill widget for a selected company."""
        pill_bg = '#3498db'  # Blue background
        pill_hover = '#2980b9'  # Darker blue on hover
        
        # Pill container with colored background
        # Use relief and highlightthickness to ensure bg shows on Windows
        pill = tk.Frame(
            parent,
            bg=pill_bg,
            padx=8,
            pady=3,
            relief=tk.FLAT,
            highlightthickness=0,
            borderwidth=0
        )
        # Force background update
        pill.configure(bg=pill_bg)
        
        # Tax code label
        label = tk.Label(
            pill,
            text=tax_code,
            bg=pill_bg,
            fg='white',
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL),
            highlightthickness=0,
            borderwidth=0
        )
        label.pack(side=tk.LEFT)
        
        # Remove button
        remove_btn = tk.Label(
            pill,
            text="✕",
            bg=pill_bg,
            fg='white',
            cursor='hand2',
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_SMALL, 'bold'),
            highlightthickness=0,
            borderwidth=0
        )
        remove_btn.pack(side=tk.LEFT, padx=(5, 0))
        remove_btn.bind('<Button-1>', lambda e, tc=tax_code: self._remove_company(tc))
        
        # Hover effects
        def on_enter(e):
            pill.config(bg=pill_hover)
            label.config(bg=pill_hover)
            remove_btn.config(bg=pill_hover)
        
        def on_leave(e):
            pill.config(bg=pill_bg)
            label.config(bg=pill_bg)
            remove_btn.config(bg=pill_bg)
        
        pill.bind('<Enter>', on_enter)
        pill.bind('<Leave>', on_leave)
        label.bind('<Enter>', on_enter)
        label.bind('<Leave>', on_leave)
        remove_btn.bind('<Enter>', on_enter)
        remove_btn.bind('<Leave>', on_leave)
        
        return pill
    
    def _force_pill_colors(self) -> None:
        """Force pill colors on Windows - workaround for theme override."""
        pill_bg = '#3498db'
        fg = 'white'
        
        # Find all pill frames and their children
        for row in self.pills_frame.winfo_children():
            if isinstance(row, ttk.Frame):
                for pill in row.winfo_children():
                    if isinstance(pill, tk.Frame):
                        pill.configure(bg=pill_bg)
                        for child in pill.winfo_children():
                            if isinstance(child, tk.Label):
                                child.configure(bg=pill_bg, fg=fg)
                        pill.update_idletasks()
    
    def add_company(self, tax_code: str) -> bool:
        """
        Add a company to selection.
        
        Args:
            tax_code: Tax code to add
            
        Returns:
            True if added, False if already selected or at limit
        """
        # Clean tax code (extract from "MST - Company Name" format)
        if ' - ' in tax_code:
            tax_code = tax_code.split(' - ')[0].strip()
        
        tax_code = tax_code.strip()
        
        if not tax_code or tax_code == 'Tất cả công ty':
            return False
        
        if tax_code in self._selected:
            messagebox.showinfo("Thông báo", f"Công ty {tax_code} đã được chọn.")
            return False
        
        if len(self._selected) >= self.max_select:
            messagebox.showwarning(
                "Giới hạn",
                f"Chỉ được chọn tối đa {self.max_select} công ty.\n"
                f"Xóa bớt công ty đã chọn hoặc thay đổi giới hạn trong Cài đặt."
            )
            return False
        
        self._selected.append(tax_code)
        self._save_selection()
        self._update_pills()
        
        if self.on_selection_changed:
            self.on_selection_changed(self._selected.copy())
        
        return True
        
    def set_selected_companies(self, companies: List[str]) -> None:
        """
        Set the list of selected companies programmatically.
        
        Args:
            companies: List of tax codes
        """
        # Filter valid and limit
        valid_companies = [c.strip() for c in companies if c.strip()][:self.max_select]
        
        self._selected = valid_companies
        self._save_selection()
        self._update_pills()
        
        if self.on_selection_changed:
            self.on_selection_changed(self._selected.copy())
    
    def _remove_company(self, tax_code: str) -> None:
        """Remove a company from selection."""
        if tax_code in self._selected:
            self._selected.remove(tax_code)
            self._save_selection()
            self._update_pills()
            
            if self.on_selection_changed:
                self.on_selection_changed(self._selected.copy())
    
    def _clear_all(self) -> None:
        """Clear all selected companies."""
        if not self._selected:
            return
        
        if messagebox.askyesno("Xác nhận", "Xóa tất cả công ty đã chọn?"):
            self._selected.clear()
            self._save_selection()
            self._update_pills()
            
            if self.on_selection_changed:
                self.on_selection_changed(self._selected.copy())
    
    def _save_selection(self) -> None:
        """Save current selection to preferences."""
        self.prefs.selected_companies = self._selected.copy()
    
    def get_selected_companies(self) -> List[str]:
        """Get list of selected company tax codes."""
        return self._selected.copy()
    
    def set_max_select(self, max_select: int) -> None:
        """Set maximum number of selectable companies."""
        self.max_select = max(1, min(max_select, 10))
        self._update_pills()
