"""
Add Tracking Dialog

Popup dialog for manually adding a declaration to the tracking list.
Features:
- Company autocomplete from database
- Declaration number validation (12 digits)
- Date picker
- Customs code entry

Requirements: Phase 3
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Callable, List, Tuple
from tkcalendar import DateEntry

from gui.styles import ModernStyles
from gui.autocomplete_combobox import AutocompleteCombobox
from database.tracking_database import TrackingDatabase


class AddTrackingDialog(tk.Toplevel):
    """Dialog for adding a manual tracking entry."""
    
    def __init__(
        self,
        parent: tk.Widget,
        tracking_db: TrackingDatabase,
        on_add: Callable[[], None]
    ):
        """
        Initialize dialog.
        
        Args:
            parent: Parent widget
            tracking_db: TrackingDatabase instance
            on_add: Callback when declaration is successfully added
        """
        super().__init__(parent)
        self.tracking_db = tracking_db
        self.on_add = on_add
        
        self.title("Thêm tờ khai theo dõi thủ công")
        self.geometry("500x350")
        self.resizable(False, False)
        
        # Modal setup
        self.transient(parent)
        self.grab_set()
        
        # Style
        self.configure(bg=ModernStyles.BG_PRIMARY)
        
        # Data
        self.companies = self._load_companies()
        self.company_values = [f"{t} - {n}" for t, n, _ in self.companies]
        self.recent_customs_codes = self._load_recent_customs_codes()
        
        self._init_ui()
        
        # Center dialog
        self._center_window()
        
    def _load_companies(self) -> List[Tuple[str, str, str]]:
        """Load companies from database."""
        try:
            return self.tracking_db.get_all_companies()
        except Exception:
            return []
    
    def _load_recent_customs_codes(self) -> List[str]:
        """Load recent customs codes from preferences."""
        try:
            from config.preferences_service import get_preferences_service
            codes = get_preferences_service().get("recent_customs_codes", [])
            return codes if isinstance(codes, list) else []
        except Exception:
            return []
    
    def _save_recent_customs_code(self, code: str) -> None:
        """Save customs code to recent list (max 10)."""
        if not code:
            return
        try:
            from config.preferences_service import get_preferences_service
            prefs = get_preferences_service()
            codes = prefs.get("recent_customs_codes", [])
            if not isinstance(codes, list):
                codes = []
            # Remove if exists, add to front
            if code in codes:
                codes.remove(code)
            codes.insert(0, code)
            # Keep max 10
            codes = codes[:10]
            prefs.set("recent_customs_codes", codes)
        except Exception:
            pass
            
    def _init_ui(self) -> None:
        """Initialize user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text="THÊM TỜ KHAI MỚI",
            font=("Segoe UI", 12, "bold"),
            foreground=ModernStyles.PRIMARY_COLOR
        ).pack(fill=tk.X, pady=(0, 20))
        
        # Form Grid
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)
        
        form_frame.columnconfigure(1, weight=1)
        
        # 1. Company
        ttk.Label(form_frame, text="Công ty:").grid(row=0, column=0, sticky='w', pady=10)
        
        self.company_combo = AutocompleteCombobox(
            form_frame,
            values=self.company_values,
            placeholder="Nhập Mã số thuế hoặc Tên công ty...",
            width=40
        )
        self.company_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0))
        
        # 2. Declaration Number
        ttk.Label(form_frame, text="Số tờ khai:").grid(row=1, column=0, sticky='w', pady=10)
        
        self.decl_entry = ttk.Entry(form_frame)
        self.decl_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0))
        
        # 3. Customs Code (with recent dropdown)
        ttk.Label(form_frame, text="Mã Hải quan:").grid(row=2, column=0, sticky='w', pady=10)
        
        self.customs_entry = ttk.Combobox(form_frame, values=self.recent_customs_codes)
        self.customs_entry.grid(row=2, column=1, sticky='ew', padx=(10, 0))
        if self.recent_customs_codes:
            self.customs_entry.set(self.recent_customs_codes[0])  # Default to most recent
        
        # 4. Date
        ttk.Label(form_frame, text="Ngày tờ khai:").grid(row=3, column=0, sticky='w', pady=10)
        
        self.date_entry = DateEntry(
            form_frame,
            width=12,
            background=ModernStyles.PRIMARY_COLOR,
            foreground='white',
            borderwidth=0,
            date_pattern='dd/mm/yyyy'
        )
        self.date_entry.grid(row=3, column=1, sticky='w', padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(30, 0))
        
        ttk.Button(
            btn_frame,
            text="Hủy bỏ",
            command=self.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="Thêm vào danh sách",
            command=self._save,
            width=20,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)
        
    def _center_window(self) -> None:
        """Center the window on screen/parent."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
        
    def _save(self) -> None:
        """Validate and save declaration."""
        # 1. Validate Company
        company_raw = self.company_combo.get()
        if not company_raw:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng chọn công ty!")
            self.company_combo.focus_set()
            return
            
        # Parse Tax Code & Name
        if " - " in company_raw:
            tax_code, company_name = company_raw.split(" - ", 1)
        else:
            # Maybe user typed manually? Assume input IS tax code if digits, else name?
            # Better to enforce structure, but let's be flexible
            # If user typed "1234567890", use it as tax code
            if company_raw.isdigit() and len(company_raw) >= 10:
                tax_code = company_raw
                company_name = "Công ty (Manual)"
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn công ty từ danh sách!")
                return
        
        # 2. Validate Declaration Number
        decl_num = self.decl_entry.get().strip()
        if not decl_num:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập Số tờ khai!")
            self.decl_entry.focus_set()
            return
            
        if not decl_num.isdigit() or len(decl_num) != 12:
            messagebox.showwarning("Dữ liệu không hợp lệ", "Số tờ khai phải là 12 chữ số!")
            self.decl_entry.focus_set()
            return
            
        # 3. Get other fields
        customs_code = self.customs_entry.get().strip().upper()
        
        try:
            decl_date = self.date_entry.get_date().strftime('%d/%m/%Y')
        except Exception:
            decl_date = datetime.now().strftime('%d/%m/%Y')
            
        # 4. Save to DB
        try:
            result = self.tracking_db.add_declaration(
                tax_code=tax_code.strip(),
                declaration_number=decl_num,
                customs_code=customs_code,
                declaration_date=decl_date,
                company_name=company_name.strip()
            )
            
            if result:
                # Save customs code to recent list
                if customs_code:
                    self._save_recent_customs_code(customs_code)
                    
                messagebox.showinfo("Thành công", f"Đã thêm tờ khai {decl_num} vào danh sách theo dõi.")
                if self.on_add:
                    self.on_add()
                self.destroy()
            else:
                messagebox.showwarning("Trùng lặp", f"Tờ khai {decl_num} đã tồn tại trong danh sách!")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu tờ khai:\n{e}")
