"""
Preview Panel Component

Right-side panel containing action buttons, filter row, and preview treeview.
Minimum height: 400px

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime

from gui.styles import ModernStyles
from models.declaration_models import Declaration


class PreviewPanel(ttk.Frame):
    """
    Right-side preview panel containing action buttons and preview table.
    
    Layout:
    - Action buttons row (top)
    - Filter/selection row
    - Preview Treeview (expandable)
    - Status label (bottom)
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    # Minimum height constraint
    MIN_HEIGHT = 400
    
    def __init__(
        self,
        parent: tk.Widget,
        on_preview: Optional[Callable[[], None]] = None,
        on_download: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        on_export_log: Optional[Callable[[], None]] = None,
        on_select_all: Optional[Callable[[bool], None]] = None,
        on_retry_failed: Optional[Callable[[], None]] = None,
        on_include_pending_changed: Optional[Callable[[bool], None]] = None,
        on_exclude_xnktc_changed: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        """
        Initialize PreviewPanel.
        
        Args:
            parent: Parent widget
            on_preview: Callback for preview button
            on_download: Callback for download button
            on_cancel: Callback for cancel button
            on_stop: Callback for stop button
            on_export_log: Callback for export log button
            on_select_all: Callback for select all checkbox
            on_retry_failed: Callback for retry failed button
            on_include_pending_changed: Callback for include pending checkbox
            on_exclude_xnktc_changed: Callback for exclude XNK TC checkbox
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.on_preview = on_preview
        self.on_download = on_download
        self.on_cancel = on_cancel
        self.on_stop = on_stop
        self.on_export_log = on_export_log
        self.on_select_all = on_select_all
        self.on_retry_failed = on_retry_failed
        self.on_include_pending_changed = on_include_pending_changed
        self.on_exclude_xnktc_changed = on_exclude_xnktc_changed
        
        # Selection state
        self._select_all_var = tk.BooleanVar(value=False)
        self._selected_items: List[str] = []
        
        # Filter options
        self._filter_options = ["Tất cả", "Chưa lấy", "Đã lấy", "Lỗi"]
        self._current_filter = "Tất cả"
        
        # Create widgets
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create preview panel widgets."""
        # Row 1: Action buttons with better spacing and uniform width
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Button width for uniform appearance
        btn_width = 14
        btn_padx = 5  # Increased spacing between buttons
        
        # Bold font for buttons
        bold_font = (ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, 'bold')
        
        # Get button configs from ModernStyles for clear hover effects
        primary_cfg = ModernStyles.get_button_config('primary')
        success_cfg = ModernStyles.get_button_config('success')
        secondary_cfg = ModernStyles.get_button_config('secondary')
        danger_cfg = ModernStyles.get_button_config('danger')
        warning_cfg = ModernStyles.get_button_config('warning')
        
        # Override font to bold for all configs
        primary_cfg['font'] = bold_font
        success_cfg['font'] = bold_font
        secondary_cfg['font'] = bold_font
        danger_cfg['font'] = bold_font
        warning_cfg['font'] = bold_font
        
        # Preview button (primary style)
        self.preview_btn = tk.Button(
            action_frame,
            text="👁 Xem trước",
            command=self._on_preview_click,
            width=btn_width,
            **primary_cfg
        )
        self.preview_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.preview_btn, 'primary')
        
        # Download button (success style)
        self.download_btn = tk.Button(
            action_frame,
            text="📥 Lấy mã vạch",
            command=self._on_download_click,
            width=btn_width,
            **success_cfg
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.download_btn, 'success')
        
        # Cancel button (secondary style)
        self.cancel_btn = tk.Button(
            action_frame,
            text="✕ Hủy",
            command=self._on_cancel_click,
            width=btn_width,
            **secondary_cfg
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.cancel_btn, 'secondary')
        
        # Stop button (danger style) - starts disabled/sunken
        self.stop_btn = tk.Button(
            action_frame,
            text="⏹ Dừng",
            command=self._on_stop_click,
            width=btn_width,
            **danger_cfg
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.stop_btn, 'danger')
        # Set initial sunken state
        self._set_button_sunken(self.stop_btn)
        
        # Export log button (primary style)
        self.export_btn = tk.Button(
            action_frame,
            text="📋 Xuất log",
            command=self._on_export_click,
            width=btn_width,
            **primary_cfg
        )
        self.export_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.export_btn, 'primary')
        
        # Retry failed button (warning style) - starts disabled/sunken
        self.retry_btn = tk.Button(
            action_frame,
            text="🔄 Tải lại lỗi",
            command=self._on_retry_click,
            width=btn_width,
            **warning_cfg
        )
        self.retry_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.retry_btn, 'warning')
        # Set initial sunken state
        self._set_button_sunken(self.retry_btn)
        
        # Row 2: Filter and selection
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Select all checkbox
        self.select_all_cb = ttk.Checkbutton(
            filter_frame,
            text="Chọn tất cả",
            variable=self._select_all_var,
            command=self._on_select_all_change
        )
        self.select_all_cb.pack(side=tk.LEFT, padx=(0, 10))
        
        # Selection count label
        self.selection_label = ttk.Label(
            filter_frame,
            text="Đã chọn: 0",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.selection_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # Checkbox to include non-cleared declarations (phân luồng nhưng chưa thông quan)
        self.include_pending_var = tk.BooleanVar(value=False)
        self.include_pending_checkbox = ttk.Checkbutton(
            filter_frame,
            text="Xem cả tờ khai chưa thông quan",
            variable=self.include_pending_var,
            command=self._on_include_pending_changed
        )
        self.include_pending_checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkbox to exclude XNK TC declarations (Requirements 1.1, 1.2, 1.5)
        self.exclude_xnktc_var = tk.BooleanVar(value=True)  # Default: enabled
        self.exclude_xnktc_checkbox = ttk.Checkbutton(
            filter_frame,
            text="Không lấy mã vạch tờ khai XNK TC",
            variable=self.exclude_xnktc_var,
            command=self._on_exclude_xnktc_changed
        )
        self.exclude_xnktc_checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Filter dropdown (right side)
        filter_right = ttk.Frame(filter_frame)
        filter_right.pack(side=tk.RIGHT)
        
        ttk.Label(
            filter_right,
            text="Lọc:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        self.filter_var = tk.StringVar(value=self._filter_options[0])
        self.filter_combo = ttk.Combobox(
            filter_right,
            textvariable=self.filter_var,
            values=self._filter_options,
            state="readonly",
            width=12
        )
        self.filter_combo.pack(side=tk.LEFT)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        # Row 3: Preview Treeview (expandable) - Requirement 5.2
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview with STT column and additional columns
        columns = ("stt", "declaration_number", "tax_code", "date", "status", "declaration_type", "bill_of_lading", "invoice_number", "result")
        self.preview_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            selectmode="extended",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        
        v_scroll.config(command=self.preview_tree.yview)
        h_scroll.config(command=self.preview_tree.xview)
        
        # Column headings
        self.preview_tree.heading("#0", text="☐", anchor=tk.W)
        self.preview_tree.heading("stt", text="STT")
        self.preview_tree.heading("declaration_number", text="Số tờ khai")
        self.preview_tree.heading("tax_code", text="Mã số thuế")
        self.preview_tree.heading("date", text="Ngày")
        self.preview_tree.heading("status", text="Trạng thái")
        self.preview_tree.heading("declaration_type", text="Loại hình")
        self.preview_tree.heading("bill_of_lading", text="Vận đơn")
        self.preview_tree.heading("invoice_number", text="Số hóa đơn")
        self.preview_tree.heading("result", text="Kết quả")
        
        # Column widths
        self.preview_tree.column("#0", width=30, stretch=False)
        self.preview_tree.column("stt", width=40, anchor=tk.CENTER)
        self.preview_tree.column("declaration_number", width=130)
        self.preview_tree.column("tax_code", width=100)
        self.preview_tree.column("date", width=90)
        self.preview_tree.column("status", width=110)
        self.preview_tree.column("declaration_type", width=80)
        self.preview_tree.column("bill_of_lading", width=120)
        self.preview_tree.column("invoice_number", width=100)
        self.preview_tree.column("result", width=80)
        
        # Configure tags for styling
        ModernStyles.configure_treeview_tags(self.preview_tree)
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection events
        self.preview_tree.bind("<ButtonRelease-1>", self._on_tree_click)
        
        # Row 4: Progress and Status
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Progress bar (left side, hidden by default)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            mode='determinate'
        )
        # Will be shown during download
        
        # Progress label (shows "Đang xử lý X/Y...")
        self.progress_label = ttk.Label(
            status_frame,
            text="",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL),
            foreground=ModernStyles.INFO_COLOR if hasattr(ModernStyles, 'INFO_COLOR') else "#2196F3"
        )
        # Will be shown during download
        
        # Status label (right side)
        self.status_label = ttk.Label(
            status_frame,
            text="Sẵn sàng",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL),
            foreground=ModernStyles.TEXT_SECONDARY
        )
        self.status_label.pack(side=tk.LEFT)
    
    def _bind_hover_effects(self, button: tk.Button, button_type: str) -> None:
        """
        Bind hover effects to a tk.Button for visual feedback.
        
        Args:
            button: The button widget
            button_type: One of 'primary', 'success', 'danger', 'secondary', 'warning'
        """
        # Define hover colors for each button type
        hover_colors = {
            'primary': {'normal': ModernStyles.PRIMARY_COLOR, 'hover': ModernStyles.PRIMARY_HOVER, 'fg': '#ffffff'},
            'success': {'normal': ModernStyles.SUCCESS_COLOR, 'hover': '#0E6B0E', 'fg': '#ffffff'},
            'danger': {'normal': ModernStyles.ERROR_COLOR, 'hover': '#B52D30', 'fg': '#ffffff'},
            'secondary': {'normal': ModernStyles.BG_SECONDARY, 'hover': ModernStyles.BG_HOVER, 'fg': ModernStyles.TEXT_PRIMARY},
            'warning': {'normal': '#FF9800', 'hover': '#F57C00', 'fg': '#ffffff'}
        }
        
        colors = hover_colors.get(button_type, hover_colors['primary'])
        
        def on_enter(e):
            if not button._is_sunken:
                button.configure(bg=colors['hover'])
        
        def on_leave(e):
            if not button._is_sunken:
                button.configure(bg=colors['normal'])
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        # Store colors and state for later use
        button._hover_colors = colors
        button._is_sunken = False
    
    def _set_button_sunken(self, button: tk.Button) -> None:
        """
        Set button to sunken/disabled appearance (chìm).
        Button appears muted/faded when not active.
        
        Args:
            button: The button widget
        """
        button._is_sunken = True
        button.configure(
            state=tk.DISABLED,
            bg='#E0E0E0',  # Light gray background
            fg='#9E9E9E',  # Gray text
            relief='sunken'
        )
    
    def _set_button_raised(self, button: tk.Button) -> None:
        """
        Set button to raised/enabled appearance (nổi).
        Button appears prominent with full color when active.
        
        Args:
            button: The button widget
        """
        button._is_sunken = False
        if hasattr(button, '_hover_colors'):
            button.configure(
                state=tk.NORMAL,
                bg=button._hover_colors['normal'],
                fg=button._hover_colors['fg'],
                relief='flat'
            )
    
    def _on_preview_click(self) -> None:
        """Handle preview button click."""
        if self.on_preview:
            self.on_preview()
    
    def _on_download_click(self) -> None:
        """Handle download button click."""
        if self.on_download:
            self.on_download()
    
    def _on_cancel_click(self) -> None:
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()
    
    def _on_stop_click(self) -> None:
        """Handle stop button click."""
        if self.on_stop:
            self.on_stop()
    
    def _on_export_click(self) -> None:
        """Handle export log button click."""
        if self.on_export_log:
            self.on_export_log()
    
    def _on_retry_click(self) -> None:
        """Handle retry failed button click."""
        if self.on_retry_failed:
            self.on_retry_failed()
    
    def _on_include_pending_changed(self) -> None:
        """Handle include pending checkbox change - triggers preview refresh."""
        if self.on_include_pending_changed:
            self.on_include_pending_changed(self.include_pending_var.get())
    
    def _on_exclude_xnktc_changed(self) -> None:
        """Handle exclude XNK TC checkbox change - triggers preview refresh."""
        if self.on_exclude_xnktc_changed:
            self.on_exclude_xnktc_changed(self.exclude_xnktc_var.get())
    
    def _on_select_all_change(self) -> None:
        """Handle select all checkbox change."""
        select_all = self._select_all_var.get()
        
        # Update UI without triggering callback (to avoid recursion)
        self._update_select_all_ui(select_all)
        
        if self.on_select_all:
            self.on_select_all(select_all)
    
    def _update_select_all_ui(self, select_all: bool) -> None:
        """
        Update select all UI without triggering callback.
        
        This method is used internally and by external callers to avoid recursion.
        
        Args:
            select_all: True to select all, False to deselect all
        """
        # Update all items
        for item in self.preview_tree.get_children():
            self.preview_tree.item(item, text="☑" if select_all else "☐")
        
        # Update selection list
        if select_all:
            self._selected_items = list(self.preview_tree.get_children())
        else:
            self._selected_items = []
        
        self._update_selection_count()
    
    def _on_tree_click(self, event) -> None:
        """Handle tree item click for checkbox toggle."""
        region = self.preview_tree.identify_region(event.x, event.y)
        # Handle click on tree column (checkbox) or cell
        if region in ("tree", "cell"):
            item = self.preview_tree.identify_row(event.y)
            if item:
                # Only toggle checkbox when clicking on tree column (checkbox area)
                if region == "tree":
                    # Toggle checkbox
                    current = self.preview_tree.item(item, "text")
                    new_state = "☐" if current == "☑" else "☑"
                    self.preview_tree.item(item, text=new_state)
                    
                    # Update selection list
                    if new_state == "☑":
                        if item not in self._selected_items:
                            self._selected_items.append(item)
                    else:
                        if item in self._selected_items:
                            self._selected_items.remove(item)
                    
                    self._update_selection_count()
    
    def _on_filter_change(self, event=None) -> None:
        """Handle filter dropdown change."""
        self._current_filter = self.filter_var.get()
        # Filter logic would be implemented here
    
    def _update_selection_count(self) -> None:
        """Update selection count label."""
        count = len(self._selected_items)
        self.selection_label.configure(text=f"Đã chọn: {count}")
    
    def populate_preview(self, declarations: List[Dict[str, Any]]) -> None:
        """
        Populate preview tree with declarations.
        
        Args:
            declarations: List of declaration dictionaries with keys:
                - declaration_number, tax_code, date, status, result
                - Optional: stt, checkbox, declaration_type, bill_of_lading, invoice_number
        """
        # Clear existing items
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        self._selected_items = []
        self._select_all_var.set(False)
        
        # Store declarations for later reference
        self._declarations = declarations
        
        # Add declarations
        for index, decl in enumerate(declarations):
            # Determine row tag
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            # Format date
            date_str = decl.get('date', '')
            if isinstance(date_str, datetime):
                date_str = date_str.strftime("%d/%m/%Y")
            
            self.preview_tree.insert(
                "",
                tk.END,
                text="☐",
                values=(
                    index + 1,  # STT (số thứ tự bắt đầu từ 1)
                    decl.get('declaration_number', ''),
                    decl.get('tax_code', ''),
                    date_str,
                    decl.get('status', ''),
                    decl.get('declaration_type', ''),
                    decl.get('bill_of_lading', ''),
                    decl.get('invoice_number', ''),
                    decl.get('result', '')
                ),
                tags=(row_tag,)
            )
        
        self._update_selection_count()
        self.update_status(f"Đã tải {len(declarations)} tờ khai")
    
    def get_selected_declarations(self) -> List[str]:
        """
        Get list of selected declaration numbers.
        
        Returns:
            List of selected declaration numbers
        """
        selected = []
        for item in self._selected_items:
            values = self.preview_tree.item(item, "values")
            if values:
                selected.append(values[1])  # declaration_number (index 1 after STT)
        return selected
    
    def update_item_result(self, declaration_number: str, result: str, is_success: bool) -> None:
        """
        Update result column for a specific declaration.
        
        Args:
            declaration_number: Declaration number to update
            result: Result text
            is_success: True for success styling, False for error
        """
        for item in self.preview_tree.get_children():
            values = self.preview_tree.item(item, "values")
            if values and values[1] == declaration_number:  # index 1 after STT
                # Update result column (index 8 - last column after adding STT)
                new_values = list(values)
                new_values[8] = result
                self.preview_tree.item(item, values=tuple(new_values))
                
                # Update tag for styling
                tag = 'success' if is_success else 'error'
                self.preview_tree.item(item, tags=(tag,))
                break
    
    def update_status(self, text: str, is_error: bool = False) -> None:
        """
        Update status label.
        
        Args:
            text: Status text
            is_error: True for error styling
        """
        color = ModernStyles.ERROR_COLOR if is_error else ModernStyles.TEXT_SECONDARY
        self.status_label.configure(text=text, foreground=color)
    
    def show_progress(self, show: bool = True) -> None:
        """
        Show or hide progress bar and label.
        
        Args:
            show: True to show, False to hide
        """
        if show:
            self.progress_bar.pack(side=tk.LEFT, padx=(0, 5))
            self.progress_label.pack(side=tk.LEFT, padx=(0, 10))
        else:
            self.progress_bar.pack_forget()
            self.progress_label.pack_forget()
            self.progress_label.configure(text="")
    
    def update_progress(self, value: float, current: int = 0, total: int = 0) -> None:
        """
        Update progress bar value and label.
        
        Args:
            value: Progress value (0-100)
            current: Current item number
            total: Total items
        """
        self.progress_var.set(value)
        if current > 0 and total > 0:
            self.progress_label.configure(text=f"Đang xử lý {current}/{total}...")
    
    def set_downloading_state(self, is_downloading: bool) -> None:
        """
        Set UI state for downloading.
        
        Args:
            is_downloading: True when downloading
        """
        if is_downloading:
            # Disable preview and download buttons (normal disabled)
            self._set_button_disabled(self.preview_btn)
            self._set_button_disabled(self.download_btn)
            # Enable stop button (raised/prominent)
            self._set_button_raised(self.stop_btn)
            # Keep retry sunken
            self._set_button_sunken(self.retry_btn)
            self.show_progress(True)
        else:
            # Enable preview and download buttons
            self._set_button_enabled(self.preview_btn)
            self._set_button_enabled(self.download_btn)
            # Disable stop button (sunken/muted)
            self._set_button_sunken(self.stop_btn)
            self.show_progress(False)
    
    def _set_button_disabled(self, button: tk.Button) -> None:
        """
        Set button to disabled state (for normal buttons like preview/download).
        
        Args:
            button: The button widget
        """
        button.configure(
            state=tk.DISABLED,
            bg=ModernStyles.BG_SECONDARY,
            fg=ModernStyles.TEXT_DISABLED
        )
    
    def _set_button_enabled(self, button: tk.Button) -> None:
        """
        Set button to enabled state (for normal buttons like preview/download).
        
        Args:
            button: The button widget
        """
        if hasattr(button, '_hover_colors'):
            button.configure(
                state=tk.NORMAL,
                bg=button._hover_colors['normal'],
                fg=button._hover_colors['fg']
            )
    
    def enable_retry_button(self, enable: bool = True) -> None:
        """
        Enable or disable retry failed button.
        Uses sunken/raised appearance for clear visual feedback.
        
        Args:
            enable: True to enable (raised/prominent), False to disable (sunken/muted)
        """
        if enable:
            self._set_button_raised(self.retry_btn)
        else:
            self._set_button_sunken(self.retry_btn)
    
    def get_failed_declarations(self) -> List[str]:
        """
        Get list of declaration numbers that have failed (error tag).
        
        Returns:
            List of declaration numbers with error status
        """
        failed = []
        for item in self.preview_tree.get_children():
            tags = self.preview_tree.item(item, "tags")
            if 'error' in tags:
                values = self.preview_tree.item(item, "values")
                if values:
                    failed.append(values[1])  # declaration_number (index 1 after STT)
        return failed
    
    def clear(self) -> None:
        """Clear all items from preview."""
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self._selected_items = []
        self._select_all_var.set(False)
        self._update_selection_count()
        self.update_status("Sẵn sàng")
