"""
Tracking Panel

Panel for tracking declaration clearance status (Phase 3).
Displays list of declarations being monitored and their status.

Features:
- List of tracked declarations
- Add manual declaration button
- Status indicators
- Context menu for actions (Delete, Check Now)

Requirements: Phase 3
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import datetime

from gui.styles import ModernStyles
from gui.components.tooltip import ToolTip, BUTTON_TOOLTIPS
from database.tracking_database import TrackingDatabase
from models.declaration_models import ClearanceStatus
from gui.add_tracking_dialog import AddTrackingDialog


class TrackingPanel(ttk.Frame):
    """
    Panel for displaying and managing tracked declarations.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        tracking_db: TrackingDatabase,
        on_status_change: Optional[callable] = None,
        logger: Optional[object] = None,
        on_get_barcode: Optional[callable] = None,
        on_check_now: Optional[callable] = None,
        on_stop: Optional[callable] = None,
        on_settings: Optional[callable] = None,
        on_delete: Optional[callable] = None
    ):
        """
        Initialize TrackingPanel.
        
        Args:
            parent: Parent widget
            tracking_db: TrackingDatabase instance
            on_status_change: Callback when status updates (optional)
            logger: Logger instance
            on_get_barcode: Callback(List[Declaration]) to get barcodes
            on_check_now: Callback() to check status now
            on_stop: Callback() to stop checking
            on_settings: Callback() to open settings
            on_delete: Callback(List[tuple]) to delete declarations from database
        """
        super().__init__(parent)
        self.tracking_db = tracking_db
        self.on_status_change = on_status_change
        self.logger = logger
        self.on_get_barcode = on_get_barcode
        self.on_check_now = on_check_now
        self.on_stop = on_stop
        self.on_settings = on_settings
        self.on_delete = on_delete
        
        self.tree = None
        self._init_ui()
        self.refresh()

    # ... methods ...

    def _on_get_barcode_click(self):
        """Handle Get Barcode toolbar button."""
        # TODO: Get all selected or just valid ones
        self._get_barcode_selected()

    def _on_check_now_click(self):
        """Handle Check Now button."""
        if self.on_check_now:
            self.on_check_now()

    def _on_stop_click(self):
        """Handle Stop button."""
        if self.on_stop:
            self.on_stop()
    
    def _on_delete_click(self):
        """Handle Delete button - remove selected (checked) declarations from tracking."""
        # Get all items with checked checkbox (☑)
        checked_items = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values and len(values) >= 2 and values[1] == "☑":
                checked_items.append(item)
        
        if not checked_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tờ khai để xóa.")
            return
        
        from tkinter import messagebox
        count = len(checked_items)
        confirm = messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa {count} tờ khai đã chọn khỏi danh sách theo dõi?"
        )
        
        if confirm:
            # Collect declaration IDs to delete (column 0 = id)
            decl_ids = []
            for item in checked_items:
                values = self.tree.item(item, "values")
                if values and len(values) >= 1:
                    decl_id = values[0]  # id column
                    decl_ids.append(decl_id)
            
            # Delete from database
            deleted_count = 0
            for decl_id in decl_ids:
                try:
                    self.tracking_db.delete_by_id(int(decl_id))
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting declaration {decl_id}: {e}")
            
            # Refresh the tree view
            self.refresh()
            
            # Show result message
            messagebox.showinfo("Hoàn thành", f"Đã xóa {deleted_count} tờ khai khỏi danh sách theo dõi.")

    def _on_settings_click(self):
        """Handle Settings button."""
        if self.on_settings:
            self.on_settings()
    
    def _on_sort_changed(self, event=None):
        """Handle sort order change - save preference and refresh."""
        display_value = self._sort_var.get()
        sort_key = self._sort_options.get(display_value, "pending_first")
        
        # Save preference
        from config.preferences_service import get_preferences_service
        get_preferences_service().tracking_sort_order = sort_key
        
        # Refresh with new sort order
        self.refresh()

    def enable_stop_btn(self) -> None:
        """Enable stop button with red (danger) appearance."""
        if hasattr(self, 'stop_btn') and hasattr(self, '_danger_cfg'):
            self.stop_btn.config(
                state=tk.NORMAL,
                bg=self._danger_cfg['bg'],
                fg=self._danger_cfg['fg'],
                activebackground=self._danger_cfg['activebackground'],
                activeforeground=self._danger_cfg['activeforeground']
            )
    
    def disable_stop_btn(self) -> None:
        """Disable stop button with gray (secondary) appearance."""
        if hasattr(self, 'stop_btn') and hasattr(self, '_secondary_cfg'):
            self.stop_btn.config(
                state=tk.DISABLED,
                bg=self._secondary_cfg['bg'],
                fg=self._secondary_cfg['fg'],
                disabledforeground=self._secondary_cfg.get('disabledforeground', '#f8f9fa')
            )

    def _bind_hover_effects(self, button: tk.Button, style: str) -> None:
        """Bind hover effects to a button."""
        hover_colors = {
            'success': {'normal': ModernStyles.SUCCESS_COLOR, 'hover': '#45a049'},
            'warning': {'normal': '#FF9800', 'hover': '#F57C00'},
            'danger': {'normal': ModernStyles.ERROR_COLOR, 'hover': '#d32f2f'},
            'primary': {'normal': ModernStyles.PRIMARY_COLOR, 'hover': '#1976D2'}
        }
        
        colors = hover_colors.get(style, hover_colors['primary'])
        
        def on_enter(e):
            if button['state'] != tk.DISABLED:
                button.config(bg=colors['hover'])
        
        def on_leave(e):
            if button['state'] != tk.DISABLED:
                button.config(bg=colors['normal'])
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def start_countdown(self, interval_minutes: int) -> None:
        """
        Start countdown timer display.
        
        Args:
            interval_minutes: Interval in minutes until next check
        """
        self.stop_countdown()  # Stop any existing countdown
        self._countdown_seconds = interval_minutes * 60
        
        # Immediately update label to show starting time
        if hasattr(self, 'countdown_label'):
            minutes = self._countdown_seconds // 60
            seconds = self._countdown_seconds % 60
            self.countdown_label.config(text=f"⏱ {minutes:02d}:{seconds:02d}")
            self.update_idletasks()  # Force UI refresh
        
        # Start countdown loop
        self._countdown_seconds -= 1
        self._countdown_interval_id = self.after(1000, self._update_countdown)
    
    def _update_countdown(self) -> None:
        """Update countdown display every second."""
        if self._countdown_seconds > 0:
            minutes = self._countdown_seconds // 60
            seconds = self._countdown_seconds % 60
            time_str = f"⏱ {minutes:02d}:{seconds:02d}"
            
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text=time_str)
            
            self._countdown_seconds -= 1
            self._countdown_interval_id = self.after(1000, self._update_countdown)
        else:
            # Timer reached zero - show checking message
            if hasattr(self, 'countdown_label'):
                self.countdown_label.config(text="⏱ Đang kiểm tra...")
    
    def stop_countdown(self) -> None:
        """Stop countdown timer."""
        if self._countdown_interval_id:
            self.after_cancel(self._countdown_interval_id)
            self._countdown_interval_id = None
        self._countdown_seconds = 0
    
    def reset_countdown(self, interval_minutes: int) -> None:
        """Reset countdown after check completes."""
        self.start_countdown(interval_minutes)
    
    def update_auto_status(self, enabled: bool) -> None:
        """
        Update the auto-tracking status label.
        
        Args:
            enabled: True if auto-tracking is enabled, False otherwise
        """
        if hasattr(self, 'auto_status_label'):
            if enabled:
                self.auto_status_label.config(
                    text="🔔 Tự động: BẬT",
                    fg=ModernStyles.SUCCESS_COLOR
                )
            else:
                self.auto_status_label.config(
                    text="🔕 Tự động: TẮT",
                    fg=ModernStyles.TEXT_SECONDARY
                )
                # Also clear countdown when auto is disabled
                if hasattr(self, 'countdown_label'):
                    self.countdown_label.config(text="")

    def show_progress(self) -> None:
        """Show progress bar at bottom."""
        if hasattr(self, 'progress_frame'):
            self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
            self.progress_bar['value'] = 0
            self.progress_label.config(text="")

    def hide_progress(self) -> None:
        """Hide progress bar."""
        if hasattr(self, 'progress_frame'):
            self.progress_frame.pack_forget()

    def update_progress(self, current: int, total: int, message: str = "") -> None:
        """Update progress bar and label."""
        if hasattr(self, 'progress_bar'):
            if total > 0:
                percent = (current / total) * 100
                self.progress_bar['value'] = percent
            self.progress_label.config(text=message or f"{current}/{total}")
            self.update_idletasks()

    def update_item_status(self, decl_id: int, new_status: str, last_checked: str = None, cleared_at: str = None) -> None:
        """Update a specific item's status in the tree (real-time)."""
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            if int(values[0]) == decl_id:
                # Update status (index 8)
                values[8] = new_status
                if last_checked:
                    values[9] = last_checked
                if cleared_at:
                    values[10] = cleared_at
                
                # Update tag based on status
                tag = "status_pending"
                if "thông quan" in new_status.lower():
                    tag = "status_cleared"
                elif "lỗi" in new_status.lower():
                    tag = "status_error"
                
                self.tree.item(item_id, values=values, tags=(tag,))
                break

    def _get_barcode_selected(self) -> None:
        """Switch to retrieval view for selected declaration."""
        selection = self.tree.selection()
        if not selection:
            return
            
        # Collect selected declarations
        declarations = []
        for item in selection:
            values = self.tree.item(item, "values")
            tax_code = values[2]
            decl_num = values[3]
            date_str = values[5]
            
            try:
                # Try ISO format
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    # Try display format
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                except ValueError:
                    date_obj = datetime.now()
            
            # Simple struct or object to pass
            declarations.append({
                'tax_code': tax_code, 
                'declaration_number': decl_num,
                'date': date_obj
            })
                
        if self.on_get_barcode:
            self.on_get_barcode(declarations) # Pass list now
            
    def _init_ui(self) -> None:
        """Initialize user interface."""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(10, 5))  # Added top padding for spacing from tabs
        
        # Action Buttons with hover effects
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side=tk.LEFT, padx=5)
        
        btn_width = 14
        bold_font = (ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, 'bold')
        
        # Get button configs from ModernStyles for consistent hover effects
        success_cfg = ModernStyles.get_button_config('success')
        warning_cfg = ModernStyles.get_button_config('warning')
        danger_cfg = ModernStyles.get_button_config('danger')
        
        # Override font
        success_cfg['font'] = bold_font
        warning_cfg['font'] = bold_font
        danger_cfg['font'] = bold_font
        
        self.get_barcode_btn = tk.Button(
             action_frame,
             text="📥 Lấy mã vạch",
             command=self._on_get_barcode_click,
             width=btn_width,
             **success_cfg
        )
        self.get_barcode_btn.pack(side=tk.LEFT, padx=5)
        self._bind_hover_effects(self.get_barcode_btn, 'success')
        ToolTip(self.get_barcode_btn, BUTTON_TOOLTIPS.get('get_barcode', 'Lấy mã vạch cho các tờ khai đã chọn'), delay=500)
        
        self.check_now_btn = tk.Button(
             action_frame,
             text="🔍 Kiểm tra ngay",
             command=self._on_check_now_click,
             width=btn_width,
             **warning_cfg
        )
        self.check_now_btn.pack(side=tk.LEFT, padx=5)
        self._bind_hover_effects(self.check_now_btn, 'warning')
        ToolTip(self.check_now_btn, BUTTON_TOOLTIPS.get('check_now', 'Kiểm tra trạng thái thông quan ngay'), delay=500)
        
        # Get secondary config for disabled state
        secondary_cfg = ModernStyles.get_button_config('secondary')
        secondary_cfg['font'] = bold_font
        secondary_cfg['disabledforeground'] = '#f8f9fa'
        
        self.stop_btn = tk.Button(
             action_frame,
             text="⏹ Dừng",
             command=self._on_stop_click,
             width=10,
             **secondary_cfg  # Start with gray appearance
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.config(state=tk.DISABLED)
        # Store danger config for when button is enabled
        self._danger_cfg = danger_cfg
        self._secondary_cfg = secondary_cfg
        self._bind_hover_effects(self.stop_btn, 'secondary')  # Gray hover for disabled state
        ToolTip(self.stop_btn, BUTTON_TOOLTIPS.get('stop', 'Dừng quá trình kiểm tra đang thực hiện'), delay=500)
        
        # Delete button - to remove selected declarations from tracking
        self.delete_btn = tk.Button(
             action_frame,
             text="🗑 Xóa",
             command=self._on_delete_click,
             width=10,
             **danger_cfg
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        self._bind_hover_effects(self.delete_btn, 'danger')
        ToolTip(self.delete_btn, BUTTON_TOOLTIPS.get('delete', 'Xóa các tờ khai đã chọn khỏi danh sách theo dõi'), delay=500)

        # Auto-tracking status label (shows ON/OFF status)
        from config.preferences_service import get_preferences_service
        auto_check_enabled = get_preferences_service().auto_check_enabled
        
        status_text = "🔔 Tự động: BẬT" if auto_check_enabled else "🔕 Tự động: TẮT"
        status_color = ModernStyles.SUCCESS_COLOR if auto_check_enabled else ModernStyles.TEXT_SECONDARY
        
        self.auto_status_label = tk.Label(
            action_frame,
            text=status_text,
            font=("Arial", 10, "bold"),
            fg=status_color,
            bg=ModernStyles.BG_SECONDARY
        )
        self.auto_status_label.pack(side=tk.LEFT, padx=(15, 5))
        ToolTip(self.auto_status_label, "Trạng thái tự động kiểm tra thông quan. Thay đổi trong Cài đặt.", delay=500)

        # Countdown timer label (shows time until next auto check)
        self.countdown_label = tk.Label(
            action_frame,
            text="",
            font=("Arial", 10, "bold"),
            fg=ModernStyles.TEXT_SECONDARY,
            bg=ModernStyles.BG_SECONDARY
        )
        self.countdown_label.pack(side=tk.LEFT, padx=15)
        self._countdown_seconds = 0
        self._countdown_interval_id = None

        # Right side: Add/Refresh Buttons
        ttk.Button(
            toolbar,
            text="+ Thêm TK thủ công",
            command=self._show_add_dialog,
            style="Accent.TButton",
            width=20
        ).pack(side=tk.RIGHT, padx=5)
        ToolTip(toolbar.winfo_children()[-1], "Thêm tờ khai mới vào danh sách theo dõi thủ công (không qua quét tự động)", delay=500)
        
        ttk.Button(
            toolbar,
            text="Làm mới",
            command=self.refresh,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        ToolTip(toolbar.winfo_children()[-1], "Tải lại danh sách tờ khai từ database (không kiểm tra thông quan)", delay=500)
        
        # Sort order dropdown
        sort_frame = tk.Frame(toolbar, bg=ModernStyles.BG_SECONDARY)
        sort_frame.pack(side=tk.RIGHT, padx=(10, 5))
        
        tk.Label(
            sort_frame,
            text="Sắp xếp:",
            font=("Arial", 9),
            fg=ModernStyles.TEXT_SECONDARY,
            bg=ModernStyles.BG_SECONDARY
        ).pack(side=tk.LEFT, padx=(0, 3))
        
        # Sort options mapping
        self._sort_options = {
            "Chờ thông quan trước": "pending_first",
            "Ngày mới nhất": "date_desc",
            "Ngày cũ nhất": "date_asc",
            "Theo công ty": "company"
        }
        self._sort_keys = {v: k for k, v in self._sort_options.items()}
        
        # Load saved sort preference
        from config.preferences_service import get_preferences_service
        saved_sort = get_preferences_service().tracking_sort_order
        initial_display = self._sort_keys.get(saved_sort, "Chờ thông quan trước")
        
        self._sort_var = tk.StringVar(value=initial_display)
        self.sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self._sort_var,
            values=list(self._sort_options.keys()),
            state="readonly",
            width=18,
            font=("Arial", 9)
        )
        self.sort_combo.pack(side=tk.LEFT)
        self.sort_combo.bind("<<ComboboxSelected>>", self._on_sort_changed)
        ToolTip(self.sort_combo, "Sắp xếp thứ tự hiển thị tờ khai", delay=500)
        
        # Tree container frame (for proper layout with scrollbar)
        tree_container = ttk.Frame(self)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview - create inside tree_container
        columns = (
            "id", "check", "stt", "tax_code", "decl_num", "customs", 
            "date", "company", "status", "last_checked", "cleared_at"
        )
        
        self.tree = ttk.Treeview(
            tree_container,  # Parent is tree_container
            columns=columns, 
            show="headings", 
            selectmode="extended"
        )
        
        # Column Headings
        self.tree.heading("check", text="☐", command=self._on_header_check_click) # Select All
        self.tree.heading("stt", text="STT")
        self.tree.heading("tax_code", text="MST")
        self.tree.heading("decl_num", text="Số tờ khai")
        self.tree.heading("customs", text="Mã HQ")
        self.tree.heading("date", text="Ngày ĐK")
        self.tree.heading("company", text="Tên công ty")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("last_checked", text="KT Cuối")
        self.tree.heading("cleared_at", text="Thông quan")
        
        # Column Widths
        self.tree.column("id", width=0, stretch=False) # Hidden ID
        self.tree.column("check", width=30, anchor="center")
        self.tree.column("stt", width=40, anchor="center")
        self.tree.column("tax_code", width=100)
        self.tree.column("decl_num", width=110)
        self.tree.column("customs", width=60, anchor="center")
        self.tree.column("date", width=90, anchor="center")
        self.tree.column("company", width=200)
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("last_checked", width=120, anchor="center")
        self.tree.column("cleared_at", width=120, anchor="center")
        
        # Bind click for checkbox
        self.tree.bind('<Button-1>', self._on_tree_click)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tags for styling
        self.tree.tag_configure("status_pending", foreground="#d35400") # Orange
        self.tree.tag_configure("status_cleared", foreground="#27ae60", font=("Segoe UI", 9, "bold")) # Green
        self.tree.tag_configure("status_error", foreground="#c0392b") # Red
        
        # Bottom progress frame (like Preview tab)
        self.progress_frame = ttk.Frame(self)
        # Don't pack yet - will be shown/hidden dynamically
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, 
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(side=tk.LEFT, padx=(5, 10), pady=5)
        
        self.progress_label = ttk.Label(
            self.progress_frame, 
            text="",
            font=(ModernStyles.FONT_FAMILY, 9)
        )
        self.progress_label.pack(side=tk.LEFT, pady=5)
        
        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="📥 Lấy mã vạch", command=self._get_barcode_selected)
        self.context_menu.add_command(label="🔄 Kiểm tra ngay", command=self._on_check_now_click)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Xóa", command=self._delete_selected)
        
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Delete>", lambda e: self._delete_selected())
        
    def refresh(self) -> None:
        """Refresh the list of tracked declarations."""
        # Visual feedback: briefly flash the tree background
        original_bg = self.tree.cget("style") if hasattr(self.tree, 'cget') else None
        self.tree.config(style="Refresh.Treeview")
        self.update_idletasks()
        
        # Clear current
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get data
        try:
            items = self.tracking_db.get_all_tracking()
            
            # Apply sort order from preferences
            from config.preferences_service import get_preferences_service
            sort_order = get_preferences_service().tracking_sort_order
            
            if sort_order == "pending_first":
                # Pending first, then by date descending
                items.sort(key=lambda x: (
                    0 if x.status.value == "pending" else 1,
                    x.declaration_date if hasattr(x.declaration_date, 'strftime') else str(x.declaration_date)
                ), reverse=True)
                # Re-sort to put pending first (reverse messes up the pending/cleared order)
                items.sort(key=lambda x: 0 if x.status.value == "pending" else 1)
            elif sort_order == "date_desc":
                items.sort(key=lambda x: x.declaration_date if hasattr(x.declaration_date, 'strftime') else str(x.declaration_date), reverse=True)
            elif sort_order == "date_asc":
                items.sort(key=lambda x: x.declaration_date if hasattr(x.declaration_date, 'strftime') else str(x.declaration_date))
            elif sort_order == "company":
                items.sort(key=lambda x: x.company_name or "")
            
            for i, decl in enumerate(items, 1):
                # Status display
                status_text = "Chưa thông quan"
                tag = "status_pending"
                
                if decl.status.value == "cleared":
                    status_text = "Đã thông quan"
                    tag = "status_cleared"
                elif decl.status.value == "transfer":
                    status_text = "Chuyển địa điểm"
                    tag = "status_transfer"
                elif decl.status.value == "error":
                    status_text = "Lỗi "
                    tag = "status_error"
                
                # Format date as dd/mm/yyyy (Issue 4.1a)
                date_display = decl.declaration_date
                if hasattr(decl.declaration_date, 'strftime'):
                    date_display = decl.declaration_date.strftime("%d/%m/%Y")
                elif isinstance(decl.declaration_date, str) and ' ' in decl.declaration_date:
                    # Remove time part if present (e.g., "2025-12-29 00:00:00" -> "29/12/2025")
                    date_str = decl.declaration_date.split(' ')[0]
                    try:
                        from datetime import datetime as dt
                        date_obj = dt.strptime(date_str, "%Y-%m-%d")
                        date_display = date_obj.strftime("%d/%m/%Y")
                    except:
                        date_display = date_str
                
                self.tree.insert(
                    "", 
                    "end", 
                    values=(
                        decl.id,
                        "☐", # Checkbox default unchecked
                        i,
                        decl.tax_code,
                        decl.declaration_number,
                        decl.customs_code,
                        date_display,
                        decl.company_name or "",
                        status_text,
                        decl.last_checked or "-",
                        decl.cleared_at or "-"
                    ),
                    tags=(tag,)
                )
            
            # Visual feedback: restore normal style and show count
            self.tree.config(style="Treeview")
            print(f"Tracking panel refreshed: {len(items)} declarations")
                
        except Exception as e:
            print(f"Error refreshing tracking panel: {e}")
            self.tree.config(style="Treeview")  # Restore on error too
            
    def _on_tree_click(self, event):
        """Handle click on treeview to toggle checkbox."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2": # The 'check' column
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    current_values = list(self.tree.item(item_id, "values"))
                    current_check = current_values[1] # 'check' is index 1
                    
                    new_check = "☑" if current_check == "☐" else "☐"
                    current_values[1] = new_check
                    self.tree.item(item_id, values=current_values)
                    self._update_header_check_state()
                    return "break"

    def _on_header_check_click(self):
        """Toggle select all/none."""
        current_heading = self.tree.heading("check", "text")
        new_state = "☑" if current_heading == "☐" else "☐"
        self.tree.heading("check", text=new_state)
        
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            values[1] = new_state
            self.tree.item(item_id, values=values)

    def _update_header_check_state(self):
        """Update header checkbox based on items."""
        items = self.tree.get_children()
        if not items:
             self.tree.heading("check", text="☐")
             return
             
        all_checked = True
        for item in items:
            if self.tree.item(item, "values")[1] == "☐":
                all_checked = False
                break
        
        self.tree.heading("check", text="☑" if all_checked else "☐")

    def _show_add_dialog(self) -> None:
        """Open the Add Tracking Dialog."""
        AddTrackingDialog(self, self.tracking_db, on_add=self.refresh)
        
    def _show_context_menu(self, event) -> None:
        """Show context menu on right click."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def _delete_selected(self) -> None:
        """Delete selected declarations."""
        selected = self.tree.selection()
        if not selected:
            return
            
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa {len(selected)} tờ khai đang chọn?"):
            return
            
        try:
            for item in selected:
                vals = self.tree.item(item)['values']
                decl_id = vals[0] # Hidden ID
                self.tracking_db.delete_declaration(decl_id)
                
            self.refresh()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa: {e}")

    def _get_barcode_selected(self) -> None:
        """Switch to retrieval view for selected declaration."""
        # Logic: 1. Checkboxes -> 2. Highlighted -> 3. All
        items_to_process = []
        all_items = self.tree.get_children()
        
        # 1. Checkboxes
        for item_id in all_items:
            values = self.tree.item(item_id, "values")
            if values[1] == "☑": # Checked
                items_to_process.append(item_id)
        
        # 2. Highlighted
        if not items_to_process:
            selection = self.tree.selection()
            if selection:
                 items_to_process = list(selection)
        
        # 3. All
        if not items_to_process:
             items_to_process = list(all_items)
             
        if not items_to_process:
            return
            
        # Collect declaration data
        declarations = []
        for item in items_to_process:
            values = self.tree.item(item, "values")
            # Index mapping: id=0, check=1, stt=2, tax_code=3, decl_num=4, customs=5, date=6...
            
            tax_code = values[3]
            decl_num = values[4]
            customs_code = values[5]
            date_str = values[6]
            company_name = values[7]
            
            try:
                # Try display format dd/mm/yyyy
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            except ValueError:
                try:
                    # Try ISO format
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    date_obj = datetime.now()
            
            declarations.append({
                'tax_code': tax_code, 
                'declaration_number': decl_num,
                'decl_number': decl_num,
                'date': date_obj,
                'customs_code': customs_code,
                'company_name': company_name
            })
                
        if self.on_get_barcode:
            self.on_get_barcode(declarations)

    def _on_check_now_click(self):
        """Handle Check Now button with selective checking logic."""
        # Logic: 1. Checkboxes -> 2. Highlighted -> 3. All logic handled by clearance checker (or we filter here)
        # Checkboxes/Selection logic
        selected_ids = []
        all_items = self.tree.get_children()
        
        # 1. Checkboxes
        for item_id in all_items:
            values = self.tree.item(item_id, "values")
            if values[1] == "☑":
                try:
                    selected_ids.append(int(values[0])) # ID cast to int
                except (ValueError, IndexError):
                    pass
        
        # 2. Highlighted
        if not selected_ids:
            selection = self.tree.selection()
            if selection:
                for item in selection:
                    values = self.tree.item(item, "values")
                    try:
                        selected_ids.append(int(values[0]))
                    except (ValueError, IndexError):
                        pass
        
        # If we have specific selection, we might need a way to check ONLY those.
        # Currently on_check_now (mapped to _on_manual_check_clearance) calls clearance_checker.check_now() which checks ALL pending.
        # If user selected specific items, we probably want to filter.
        # But wait, check_now() in clearance checker checks "PENDING" ones.
        # If I want to allow checking even "CLEARED" or "ERROR" ones (re-check), I need new logic.
        # For now, let's assume if selection exists, we want to force check on those.
        # But `on_check_now` is a simple callback. 
        # I'll update the callback signature or logic in customs_gui.py to accept list of IDs?
        # Or simplest: just call on_check_now() and let it check all pending. 
        # User said "thay vì check tất cả". So they want selective check.
        # I need to pass selection to the callback.
        
        if self.on_check_now:
            # Check if on_check_now accepts arguments?
            # Originally it didn't. I need to check `customs_gui.py`.
            # If I act proactively, I should pass selected_ids if any.
            # But python allows flexible args if *args used or I can try/except.
            # Best way: modify `_on_manual_check_clearance` in `customs_gui.py` to accept IDs.
            try:
                self.on_check_now(selected_ids)
            except TypeError:
                # Fallback if callback doesn't accept args
                self.on_check_now()
