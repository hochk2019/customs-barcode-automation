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
from gui.components.tooltip import ToolTip, BUTTON_TOOLTIPS
from models.declaration_models import Declaration
from config.user_preferences import get_preferences
from config.preferences_service import get_preferences_service


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
        on_check_clearance: Optional[Callable[[], None]] = None,  # v1.5.0
        on_add_to_tracking: Optional[Callable[[], None]] = None,  # v1.5.0
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
            on_check_clearance: Callback for check clearance button
            on_add_to_tracking: Callback for add to tracking button
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
        self.on_check_clearance = on_check_clearance
        self.on_add_to_tracking = on_add_to_tracking
        self.on_include_pending_changed = on_include_pending_changed
        self.on_exclude_xnktc_changed = on_exclude_xnktc_changed
        
        # Selection state
        self._select_all_var = tk.BooleanVar(value=False)
        self._selected_items: List[str] = []
        self._item_data_by_id: Dict[str, Dict[str, Any]] = {}
        self._all_declarations: List[Dict[str, Any]] = []
        self._filtered_declarations: List[Dict[str, Any]] = []
        self._declarations: List[Dict[str, Any]] = []
        
        # Filter options
        self._filter_options = ["Tất cả", "Chưa lấy", "Đã lấy", "Lỗi"]
        self._current_filter = "Tất cả"
        self._sort_column: Optional[str] = None
        self._sort_descending = False
        self._retry_enabled = False
        self._retry_restore = False
        self._preferences_service = get_preferences_service()
        self._overlay_message = ""
        self._overlay_spinner_frames = ["|", "/", "-", "\\"]
        self._overlay_spinner_index = 0
        self._overlay_spinner_after_id = None
        
        # Create widgets
        self._create_widgets()

        # Restore saved filter/sort/column settings
        self._load_preview_settings()
        
        # Windows workaround: Force button colors after widget creation
        self.after_idle(self._force_button_colors)
    
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
        ToolTip(self.preview_btn, BUTTON_TOOLTIPS.get('preview', 'Xem trước danh sách tờ khai từ database (F5)'), delay=500)
        
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
        ToolTip(self.download_btn, BUTTON_TOOLTIPS.get('download', 'Lấy mã vạch cho các tờ khai đã chọn'), delay=500)

        # v1.5.0: Add to Tracking button (secondary/info style)
        self.add_tracking_btn = tk.Button(
            action_frame,
            text="+ Theo dõi",
            command=self._on_add_to_tracking_click,
            width=btn_width,
            **secondary_cfg
        )
        self.add_tracking_btn.pack(side=tk.LEFT, padx=(0, btn_padx))
        self._bind_hover_effects(self.add_tracking_btn, 'secondary')
        ToolTip(self.add_tracking_btn, BUTTON_TOOLTIPS.get('add_tracking', 'Thêm tờ khai vào danh sách theo dõi thông quan'), delay=500)
        
        # v1.5.0: Check Clearance button REMOVED (Issue 3)
        # Functionality moved to 'Theo dõi thông quan' tab

        
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
        ToolTip(self.cancel_btn, BUTTON_TOOLTIPS.get('cancel', 'Hủy thao tác xem trước đang thực hiện'), delay=500)
        
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
        ToolTip(self.stop_btn, BUTTON_TOOLTIPS.get('stop', 'Dừng quá trình tải mã vạch (chờ tờ khai hiện tại hoàn tất)'), delay=500)
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
        ToolTip(self.export_btn, BUTTON_TOOLTIPS.get('export_log', 'Xuất nhật ký lỗi ra file'), delay=500)
        
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
        ToolTip(self.retry_btn, BUTTON_TOOLTIPS.get('retry_failed', 'Thử lại các tờ khai tải thất bại'), delay=500)
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
        # v1.5.0: Load from preferences, default=True
        prefs = get_preferences()
        self.include_pending_var = tk.BooleanVar(value=prefs.include_pending)
        self.include_pending_checkbox = ttk.Checkbutton(
            filter_frame,
            text="Xem cả tờ khai chưa thông quan",
            variable=self.include_pending_var,
            command=self._on_include_pending_changed
        )
        self.include_pending_checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkbox to exclude XNK TC declarations (Requirements 1.1, 1.2, 1.5)
        # v1.5.0: Load from preferences, default=False
        self.exclude_xnktc_var = tk.BooleanVar(value=prefs.exclude_xnktc)
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

        self._base_heading_text = {
            "stt": "STT",
            "declaration_number": "Số tờ khai",
            "tax_code": "Mã số thuế",
            "date": "Ngày",
            "status": "Trạng thái",
            "declaration_type": "Loại hình",
            "bill_of_lading": "Vận đơn",
            "invoice_number": "Số hóa đơn",
            "result": "Kết quả",
        }
        self._column_keys = ("#0",) + tuple(self._base_heading_text.keys())
        self._sortable_columns = list(self._base_heading_text.keys())

        for col in self._sortable_columns:
            self.preview_tree.heading(col, command=lambda c=col: self._toggle_sort(c))
        
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
        self.preview_tree.column("result", width=80, anchor=tk.CENTER)
        
        # Configure tags for styling
        ModernStyles.configure_treeview_tags(self.preview_tree)
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True)

        # Busy overlay (shown during long-running tasks)
        self._overlay_frame = tk.Frame(tree_frame, bg=ModernStyles.BG_SECONDARY)
        self._overlay_label = tk.Label(
            self._overlay_frame,
            text="",
            bg=ModernStyles.BG_SECONDARY,
            fg=ModernStyles.TEXT_PRIMARY,
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, 'bold')
        )
        self._overlay_label.pack(expand=True)
        self._overlay_frame.place_forget()
        
        # Bind selection events
        self.preview_tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.preview_tree.bind("<ButtonRelease-1>", self._on_tree_mouse_up, add=True)
        
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
    
    def _force_button_colors(self) -> None:
        """Force button colors on Windows - workaround for theme override."""
        button_colors = {
            self.preview_btn: ModernStyles.PRIMARY_COLOR,
            self.download_btn: ModernStyles.SUCCESS_COLOR,
            self.cancel_btn: '#6c757d',  # secondary 
            self.stop_btn: ModernStyles.ERROR_COLOR,
            self.export_btn: ModernStyles.PRIMARY_COLOR,
            self.retry_btn: '#FF9800',  # warning
        }

        for btn, color in button_colors.items():
            if hasattr(btn, '_is_sunken') and not btn._is_sunken:
                btn.configure(bg=color)
            btn.update_idletasks()
    
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
    
    def _on_check_clearance_click(self) -> None:
        """Handle check clearance button click (v1.5.0)."""
        if self.on_check_clearance:
            self.on_check_clearance()

    def _on_add_to_tracking_click(self) -> None:
        """Handle add to tracking button click (v1.5.0)."""
        if self.on_add_to_tracking:
            self.on_add_to_tracking()
    
    def _on_include_pending_changed(self) -> None:
        """Handle include pending checkbox change - triggers preview refresh and saves preference."""
        # v1.5.0: Save preference immediately
        prefs = get_preferences()
        prefs.include_pending = self.include_pending_var.get()
        
        if self.on_include_pending_changed:
            self.on_include_pending_changed(self.include_pending_var.get())
    
    def _on_exclude_xnktc_changed(self) -> None:
        """Handle exclude XNK TC checkbox change - triggers preview refresh and saves preference."""
        # v1.5.0: Save preference immediately
        prefs = get_preferences()
        prefs.exclude_xnktc = self.exclude_xnktc_var.get()
        
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
        self._save_preview_settings()
        self._apply_filter()

    def _apply_filter(self) -> None:
        """Filter preview items based on current filter selection."""
        if not self._all_declarations:
            self._render_preview_items([])
            return

        filter_value = self._current_filter
        filtered = []
        for decl in self._all_declarations:
            result = str(decl.get('result', '')).strip()

            if filter_value == self._filter_options[0]:
                filtered.append(decl)
            elif filter_value == self._filter_options[1]:
                if result not in ("✔", "✘"):
                    filtered.append(decl)
            elif filter_value == self._filter_options[2]:
                if result == "✔":
                    filtered.append(decl)
            elif filter_value == self._filter_options[3]:
                if result == "✘":
                    filtered.append(decl)
            else:
                filtered.append(decl)

        filtered = self._sort_declarations(filtered)
        self._filtered_declarations = filtered
        self._render_preview_items(filtered)

    def _render_preview_items(self, declarations: List[Dict[str, Any]]) -> None:
        """Render preview items to treeview while preserving selection."""
        selected_numbers = set()
        for item_id in self._selected_items:
            values = self.preview_tree.item(item_id, "values")
            if values:
                selected_numbers.add(str(values[1]).strip())

        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        self._selected_items = []
        self._item_data_by_id = {}

        for index, decl in enumerate(declarations):
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'

            tags = [row_tag]
            result_value = str(decl.get('result', '')).strip()
            if result_value == "✔":
                tags.extend(['success_result', 'success'])
            elif result_value == "✘":
                tags.extend(['error_result', 'error'])

            date_str = decl.get('date', '')
            if isinstance(date_str, datetime):
                date_str = date_str.strftime("%d/%m/%Y")

            item_id = self.preview_tree.insert(
                "",
                tk.END,
                text="☐",
                values=(
                    index + 1,
                    decl.get('declaration_number', ''),
                    decl.get('tax_code', ''),
                    date_str,
                    decl.get('status', 'Chua ki?m tra'),
                    decl.get('declaration_type', ''),
                    decl.get('bill_of_lading', ''),
                    decl.get('invoice_number', ''),
                    decl.get('result', '')
                ),
                tags=tuple(tags)
            )
            self._item_data_by_id[item_id] = decl

            decl_num = str(decl.get('declaration_number', '')).strip()
            if decl_num and decl_num in selected_numbers:
                self.preview_tree.item(item_id, text="☑")
                self._selected_items.append(item_id)

        self._update_selection_count()
    
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
        self._selected_items = []
        self._select_all_var.set(False)

        self._all_declarations = [dict(decl) for decl in declarations]
        self._declarations = self._all_declarations
        self._filtered_declarations = []
        self._apply_filter()

    def get_selected_declarations_data(self) -> List[Dict[str, Any]]:
        """
        Get data of selected declarations.
        Returns list of dicts.
        """
        selected_data: List[Dict[str, Any]] = []

        for item_id in self._selected_items:
            if item_id in self._item_data_by_id:
                selected_data.append(self._item_data_by_id[item_id])
                continue

            values = self.preview_tree.item(item_id, "values")
            if not values:
                continue

            data = {
                'declaration_number': values[1],
                'tax_code': values[2],
                'date': values[3],
                'status': values[4],
                'declaration_type': values[5],
                'bill_of_lading': values[6] if len(values) > 6 else '',
                'invoice_number': values[7] if len(values) > 7 else '',
                'result': values[8] if len(values) > 8 else ''
            }
            selected_data.append(data)

        return selected_data

    def update_item_status(self, declaration_number: str, new_status: str) -> None:
        """
        Update status column for a specific declaration.
        """
        target = str(declaration_number).strip()
        for item_id in self.preview_tree.get_children():
            values = self.preview_tree.item(item_id, "values")
            if not values:
                continue

            current = str(values[1]).strip()
            if current != target:
                continue

            new_values = list(values)
            new_values[4] = new_status

            tags = list(self.preview_tree.item(item_id, "tags"))
            tags = [t for t in tags if t not in ("success", "error")]
            if "Th“ng quan" in new_status:
                tags.append("success")
            elif "L?i" in new_status:
                tags.append("error")

            self.preview_tree.item(item_id, values=new_values, tags=tuple(tags))

            if item_id in self._item_data_by_id:
                self._item_data_by_id[item_id]['status'] = new_status

        for decl in self._all_declarations:
            if str(decl.get('declaration_number', '')).strip() == target:
                decl['status'] = new_status

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
                selected.append(values[1])
        return selected

    def update_item_result(self, declaration_number: str, result: str, is_success: bool) -> None:
        """
        Update result column for a specific declaration.

        Args:
            declaration_number: Declaration number to update
            result: Result text
            is_success: True for success styling, False for error
        """
        target = str(declaration_number).strip()
        for item_id in self.preview_tree.get_children():
            values = self.preview_tree.item(item_id, "values")
            if not values:
                continue

            current = str(values[1]).strip()
            if current != target:
                continue

            new_values = list(values)
            new_values[8] = result
            self.preview_tree.item(item_id, values=tuple(new_values))

            tags = list(self.preview_tree.item(item_id, "tags"))
            tags = [t for t in tags if t not in ("success_result", "error_result", "success", "error")]
            if is_success:
                tags.extend(["success_result", "success"])
            else:
                tags.extend(["error_result", "error"])
            self.preview_tree.item(item_id, tags=tuple(tags))

            if item_id in self._item_data_by_id:
                self._item_data_by_id[item_id]['result'] = result

        for decl in self._all_declarations:
            if str(decl.get('declaration_number', '')).strip() == target:
                decl['result'] = result

        if self._current_filter != self._filter_options[0]:
            self._apply_filter()

    def update_status(self, text: str, is_error: bool = False) -> None:
        """
        Update status label.
        
        Args:
            text: Status text
            is_error: True for error styling
        """
        color = ModernStyles.ERROR_COLOR if is_error else ModernStyles.TEXT_SECONDARY
        self.status_label.configure(text=text, foreground=color)

    def _load_preview_settings(self) -> None:
        """Load filter/sort/column width settings from preferences."""
        prefs = self._preferences_service
        try:
            filter_index = int(prefs.get("preview_filter_index", 0))
        except (TypeError, ValueError):
            filter_index = 0

        if filter_index < 0 or filter_index >= len(self._filter_options):
            filter_index = 0

        self._current_filter = self._filter_options[filter_index]
        self.filter_var.set(self._current_filter)

        sort_column = prefs.get("preview_sort_column", "")
        sort_desc = bool(prefs.get("preview_sort_descending", False))
        if sort_column in self._sortable_columns:
            self._sort_column = sort_column
            self._sort_descending = sort_desc
        else:
            self._sort_column = None
            self._sort_descending = False

        widths = prefs.get("preview_column_widths", {})
        if isinstance(widths, dict):
            for col, width in widths.items():
                if col in self._column_keys and isinstance(width, int) and width > 0:
                    try:
                        self.preview_tree.column(col, width=width)
                    except tk.TclError:
                        pass

        self._update_sort_indicator()
        self._apply_filter()

    def _save_preview_settings(self) -> None:
        """Persist filter/sort/column width settings to preferences."""
        prefs = self._preferences_service
        try:
            filter_index = self._filter_options.index(self._current_filter)
        except ValueError:
            filter_index = 0

        prefs.set("preview_filter_index", filter_index)
        prefs.set("preview_sort_column", self._sort_column or "")
        prefs.set("preview_sort_descending", bool(self._sort_descending))
        prefs.set("preview_column_widths", self._get_column_widths())

    def _get_column_widths(self) -> Dict[str, int]:
        """Collect current treeview column widths."""
        widths: Dict[str, int] = {}
        for col in self._column_keys:
            try:
                widths[col] = int(self.preview_tree.column(col, "width"))
            except (tk.TclError, ValueError, TypeError):
                continue
        return widths

    def _persist_column_settings(self) -> None:
        """Persist column widths without changing filter/sort state."""
        prefs = self._preferences_service
        prefs.set("preview_column_widths", self._get_column_widths())

    def _on_tree_mouse_up(self, event) -> None:
        """Persist column widths after resize actions."""
        try:
            region = self.preview_tree.identify_region(event.x, event.y)
        except tk.TclError:
            region = ""
        if region in ("separator", "heading"):
            self._persist_column_settings()

    def _sort_declarations(self, declarations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort declarations based on current sort state."""
        if not self._sort_column:
            return list(declarations)

        def sort_key(item: Dict[str, Any]):
            value = item.get(self._sort_column, "")
            if self._sort_column == "stt":
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0
            if self._sort_column == "date":
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str) and value.strip():
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
                        try:
                            return datetime.strptime(value.strip(), fmt)
                        except ValueError:
                            continue
                return datetime.min
            return str(value).lower()

        return sorted(declarations, key=sort_key, reverse=self._sort_descending)

    def _toggle_sort(self, column: str) -> None:
        """Toggle sort state for a column."""
        if column not in self._sortable_columns:
            return

        if self._sort_column == column:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_column = column
            self._sort_descending = False

        self._update_sort_indicator()
        self._save_preview_settings()
        self._apply_filter()

    def _update_sort_indicator(self) -> None:
        """Update column header text with sort indicator."""
        for col, label in self._base_heading_text.items():
            text = label
            if self._sort_column == col:
                text = f"{label} {'v' if self._sort_descending else '^'}"
            self.preview_tree.heading(col, text=text)

    def _show_overlay(self, message: str) -> None:
        """Show overlay message during background tasks."""
        if not message:
            message = "⏳ Đang xử lý, vui lòng chờ..."
        self._overlay_message = message
        self._start_overlay_spinner()
        self._overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._overlay_frame.lift()

    def _hide_overlay(self) -> None:
        """Hide overlay message."""
        self._stop_overlay_spinner()
        self._overlay_frame.place_forget()

    def _start_overlay_spinner(self) -> None:
        """Start spinner animation for overlay."""
        if self._overlay_spinner_after_id:
            try:
                self.after_cancel(self._overlay_spinner_after_id)
            except tk.TclError:
                pass
        self._overlay_spinner_index = 0
        self._animate_overlay_spinner()

    def _stop_overlay_spinner(self) -> None:
        """Stop spinner animation for overlay."""
        if self._overlay_spinner_after_id:
            try:
                self.after_cancel(self._overlay_spinner_after_id)
            except tk.TclError:
                pass
            self._overlay_spinner_after_id = None

    def _animate_overlay_spinner(self) -> None:
        """Animate spinner frames inside overlay."""
        if not self._overlay_spinner_frames:
            self._overlay_label.configure(text=self._overlay_message)
            return
        frame = self._overlay_spinner_frames[self._overlay_spinner_index % len(self._overlay_spinner_frames)]
        self._overlay_label.configure(text=f"{self._overlay_message} {frame}")
        self._overlay_spinner_index += 1
        self._overlay_spinner_after_id = self.after(120, self._animate_overlay_spinner)

    def _set_filter_controls_state(self, enabled: bool) -> None:
        """Enable or disable filter/selection controls."""
        combo_state = "readonly" if enabled else "disabled"
        self.filter_combo.configure(state=combo_state)

        cb_state = tk.NORMAL if enabled else tk.DISABLED
        self.select_all_cb.configure(state=cb_state)
        self.include_pending_checkbox.configure(state=cb_state)
        self.exclude_xnktc_checkbox.configure(state=cb_state)

        if enabled:
            self.preview_tree.state(["!disabled"])
        else:
            self.preview_tree.state(["disabled"])
    
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
            # Disable actions while running
            self._set_button_disabled(self.preview_btn)
            self._set_button_disabled(self.download_btn)
            self._set_button_disabled(self.cancel_btn)
            self._set_button_disabled(self.add_tracking_btn)
            self._set_button_disabled(self.export_btn)

            # Enable stop button (raised/prominent)
            self._set_button_raised(self.stop_btn)
            # Keep retry sunken
            self._retry_restore = self._retry_enabled
            self._set_button_sunken(self.retry_btn)
            self._set_filter_controls_state(False)
            self._show_overlay("⏳ Đang lấy mã vạch, vui lòng chờ...")
            self.show_progress(True)
        else:
            # Enable preview and download buttons
            self._set_button_enabled(self.preview_btn)
            self._set_button_enabled(self.download_btn)
            self._set_button_enabled(self.cancel_btn)
            self._set_button_enabled(self.add_tracking_btn)
            self._set_button_enabled(self.export_btn)
            # Disable stop button (sunken/muted)
            self._set_button_sunken(self.stop_btn)
            self.enable_retry_button(self._retry_restore)
            self._set_filter_controls_state(True)
            self._hide_overlay()
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
        self._retry_enabled = enable
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
            values = self.preview_tree.item(item, "values")
            if not values:
                continue
            result_value = values[8] if len(values) > 8 else ""
            tags = self.preview_tree.item(item, "tags")
            if result_value == "✘" or 'error_result' in tags or 'error' in tags:
                failed.append(values[1])
        return failed

    def clear(self) -> None:
        """Clear all items from preview."""
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self._selected_items = []
        self._select_all_var.set(False)
        self._update_selection_count()
        self.update_status("Sẵn sàng")
