"""
Check Results Dialog

Shows results after checking declaration clearance status.
Modern, compact design with clean layout.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result of a single declaration check."""
    decl_id: int
    declaration_number: str
    tax_code: str
    company_name: str
    status: str  # 'cleared', 'transfer', 'pending', 'error'
    status_text: str  # Display text


class CheckResultsDialog:
    """
    Dialog showing clearance check results with modern design.
    """
    
    # Maximum number of rows before scrollbar appears
    MAX_VISIBLE_ROWS = 5
    
    def __init__(
        self,
        parent: tk.Tk,
        total_checked: int,
        results: List[CheckResult],
        on_get_barcodes: Optional[Callable[[List[CheckResult]], None]] = None
    ):
        self.parent = parent
        self.total_checked = total_checked
        self.results = results
        self.on_get_barcodes = on_get_barcodes
        
        # Categorize results
        self.cleared = [r for r in results if r.status in ('cleared', 'transfer')]
        self.pending = [r for r in results if r.status == 'pending']
        self.errors = [r for r in results if r.status == 'error']
        
        self.dialog = None
        self.selected_items = set()
        self.row_widgets = {}
        
    def show(self) -> None:
        """Display the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Kết quả kiểm tra")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Set background color
        self.bg_color = "#f5f5f5"
        self.dialog.configure(bg=self.bg_color)
        
        # Create custom style for checkbuttons to match background
        self.style = ttk.Style()
        self.style.configure("Dialog.TCheckbutton", background=self.bg_color)
        self.style.configure("Table.TCheckbutton", background="white")
        
        self._create_widgets()
        
        # Center on parent
        self.dialog.update_idletasks()
        width = self.dialog.winfo_reqwidth()
        height = self.dialog.winfo_reqheight()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - height) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
    def _create_widgets(self) -> None:
        """Create dialog widgets with modern layout."""
        # Main container
        main_frame = tk.Frame(self.dialog, bg=self.bg_color, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== HEADER: Summary Stats (Centered) ==========
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Stats container - centered
        stats_container = tk.Frame(header_frame, bg=self.bg_color)
        stats_container.pack(anchor=tk.CENTER)
        
        # Create 3 stat boxes side by side
        self._create_stat_box(stats_container, "Đã kiểm tra", str(self.total_checked), "#2196F3")
        self._create_stat_box(stats_container, "Thông quan", str(len(self.cleared)), "#4CAF50")
        self._create_stat_box(stats_container, "Chờ xử lý", str(len(self.pending)), "#FF9800")
        
        # ========== CONTENT ==========
        if self.cleared:
            self._create_cleared_section(main_frame)
        else:
            self._create_no_cleared_section(main_frame)
        
        # ========== FOOTER: Buttons ==========
        self._create_footer(main_frame)
    
    def _create_stat_box(self, parent, label: str, value: str, color: str) -> None:
        """Create a stat display box - centered vertically."""
        frame = tk.Frame(parent, bg=self.bg_color, padx=25)
        frame.pack(side=tk.LEFT)
        
        # Label on top - centered, larger and darker
        tk.Label(
            frame,
            text=label,
            font=("Segoe UI", 11),
            fg="#444",
            bg=self.bg_color
        ).pack(anchor=tk.CENTER)
        
        # Value below - centered, colored
        tk.Label(
            frame,
            text=value,
            font=("Segoe UI", 20, "bold"),
            fg=color,
            bg=self.bg_color
        ).pack(anchor=tk.CENTER)
    
    def _create_cleared_section(self, parent) -> None:
        """Create section for cleared declarations."""
        # Section header
        title_frame = tk.Frame(parent, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(
            title_frame,
            text="Tờ khai đã thông quan",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg="#333"
        ).pack(side=tk.LEFT)
        
        # Select all checkbox - styled to match background
        self.select_all_var = tk.BooleanVar(value=True)
        select_all_cb = ttk.Checkbutton(
            title_frame,
            text="Chọn tất cả",
            variable=self.select_all_var,
            command=self._toggle_select_all,
            style="Dialog.TCheckbutton"
        )
        select_all_cb.pack(side=tk.RIGHT)
        
        # Table frame with white background
        table_frame = tk.Frame(parent, bg="white", relief="solid", bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        # Create custom table with text wrapping
        self._create_custom_table(table_frame)
    
    def _create_custom_table(self, parent) -> None:
        """Create custom table with text wrapping support."""
        # Header row
        header_frame = tk.Frame(parent, bg="#e0e0e0")
        header_frame.pack(fill=tk.X)
        
        # Header columns
        tk.Label(header_frame, text="", width=3, bg="#e0e0e0", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
        tk.Label(header_frame, text="Số tờ khai", width=14, bg="#e0e0e0", font=("Segoe UI", 9, "bold"), anchor=tk.W).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Công ty", width=28, bg="#e0e0e0", font=("Segoe UI", 9, "bold"), anchor=tk.W).pack(side=tk.LEFT, padx=5)
        tk.Label(header_frame, text="Trạng thái", width=12, bg="#e0e0e0", font=("Segoe UI", 9, "bold"), anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        
        # Calculate visible height (max 5 rows, each ~40px)
        visible_rows = min(len(self.cleared), self.MAX_VISIBLE_ROWS)
        row_height = 40
        canvas_height = visible_rows * row_height
        
        # Container for canvas and scrollbar
        content_container = tk.Frame(parent, bg="white")
        content_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable content
        self.canvas = tk.Canvas(content_container, bg="white", highlightthickness=0, height=canvas_height)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Only show scrollbar if more than MAX_VISIBLE_ROWS
        if len(self.cleared) > self.MAX_VISIBLE_ROWS:
            scrollbar = ttk.Scrollbar(content_container, orient=tk.VERTICAL, command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bind mousewheel for scrolling
            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
            self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Data rows
        for i, result in enumerate(self.cleared):
            row_bg = "white" if i % 2 == 0 else "#fafafa"
            self._create_table_row(self.scrollable_frame, result, row_bg)
            self.selected_items.add(result.decl_id)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_table_row(self, parent, result, bg_color) -> None:
        """Create a single table row with wrapping text."""
        row_frame = tk.Frame(parent, bg=bg_color)
        row_frame.pack(fill=tk.X, pady=2, padx=2)
        
        # Style for white background checkbox
        self.style.configure("Row.TCheckbutton", background=bg_color)
        
        # Checkbox - use tk.Checkbutton for better control
        check_var = tk.BooleanVar(value=True)
        check_btn = tk.Checkbutton(
            row_frame,
            variable=check_var,
            command=lambda r=result, v=check_var: self._on_row_check(r, v),
            bg=bg_color,
            activebackground=bg_color,
            highlightthickness=0,
            bd=0
        )
        check_btn.pack(side=tk.LEFT, padx=5)
        
        # Store reference
        self.row_widgets[result.decl_id] = {'check_var': check_var, 'check_btn': check_btn}
        
        # Declaration number
        tk.Label(
            row_frame,
            text=result.declaration_number,
            width=14,
            font=("Segoe UI", 9),
            bg=bg_color,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=5)
        
        # Company name - with wrapping
        company_label = tk.Label(
            row_frame,
            text=result.company_name,
            width=28,
            font=("Segoe UI", 9),
            bg=bg_color,
            anchor=tk.W,
            wraplength=200,
            justify=tk.LEFT
        )
        company_label.pack(side=tk.LEFT, padx=5)
        
        # Status with color
        status_color = "#4CAF50" if result.status == "cleared" else "#FF9800"
        tk.Label(
            row_frame,
            text=result.status_text,
            width=12,
            font=("Segoe UI", 9),
            bg=bg_color,
            fg=status_color,
            anchor=tk.CENTER
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_row_check(self, result, check_var) -> None:
        """Handle row checkbox toggle."""
        if check_var.get():
            self.selected_items.add(result.decl_id)
        else:
            self.selected_items.discard(result.decl_id)
        
        self._update_selected_count()
        
        # Update select all checkbox
        if hasattr(self, 'select_all_var'):
            self.select_all_var.set(len(self.selected_items) == len(self.cleared))
    
    def _create_no_cleared_section(self, parent) -> None:
        """Create section when no declarations are cleared."""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            frame,
            text="⏳ Không có tờ khai nào được thông quan lần này.",
            font=("Segoe UI", 10),
            fg="#666",
            bg=self.bg_color
        ).pack()
    
    def _create_footer(self, parent) -> None:
        """Create footer with action buttons."""
        footer_frame = tk.Frame(parent, bg=self.bg_color)
        footer_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Right side: Close button
        close_btn = ttk.Button(
            footer_frame,
            text="Đóng",
            command=self.dialog.destroy,
            width=10
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Left side: Get barcodes button (if cleared items exist)
        if self.cleared and self.on_get_barcodes:
            self.barcode_btn = ttk.Button(
                footer_frame,
                text="📥 Lấy mã vạch",
                command=self._on_get_barcodes_click,
                width=14
            )
            self.barcode_btn.pack(side=tk.LEFT)
            
            self.selected_label = tk.Label(
                footer_frame,
                text=f"({len(self.selected_items)} tờ khai)",
                font=("Segoe UI", 9),
                fg="#666",
                bg=self.bg_color
            )
            self.selected_label.pack(side=tk.LEFT, padx=(8, 0))
    
    def _toggle_select_all(self) -> None:
        """Toggle select all checkboxes."""
        select_all = self.select_all_var.get()
        
        for decl_id, widgets in self.row_widgets.items():
            widgets['check_var'].set(select_all)
            if select_all:
                self.selected_items.add(decl_id)
            else:
                self.selected_items.discard(decl_id)
        
        self._update_selected_count()
    
    def _update_selected_count(self) -> None:
        """Update the selected count label."""
        if hasattr(self, 'selected_label'):
            self.selected_label.config(text=f"({len(self.selected_items)} tờ khai)")
    
    def _on_get_barcodes_click(self) -> None:
        """Handle get barcodes button click."""
        if not self.selected_items:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 tờ khai.")
            return
        
        selected_results = [r for r in self.cleared if r.decl_id in self.selected_items]
        
        if self.on_get_barcodes:
            self.dialog.destroy()
            self.on_get_barcodes(selected_results)
