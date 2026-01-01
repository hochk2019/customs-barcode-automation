"""
About Dialog v2.0

Extracted from customs_gui.py for GUI decomposition.
Shows application information, version, and designer credits.
"""

import os
import tkinter as tk
from PIL import Image, ImageTk

from gui.branding import (
    APP_NAME, APP_VERSION, COMPANY_SLOGAN, COMPANY_MOTTO,
    DESIGNER_NAME, DESIGNER_EMAIL, DESIGNER_PHONE, LOGO_FILE,
    BRAND_PRIMARY_COLOR, BRAND_ACCENT_COLOR, BRAND_GOLD_COLOR, BRAND_TEXT_COLOR,
    COMPANY_NAME_FULL
)


class AboutDialog:
    """
    About dialog showing application information.
    
    Displays:
    - Logo
    - App name and version
    - Company info
    - Designer credits
    - Disclaimer
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Create and show about dialog.
        
        Args:
            parent: Parent window
        """
        self.parent = parent
        self._logo_image = None  # Keep reference to prevent GC
        self._create_dialog()
    
    def _create_dialog(self) -> None:
        """Create the about dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Giới thiệu")
        self.dialog.geometry("500x650")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=BRAND_PRIMARY_COLOR)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(self.dialog, bg=BRAND_PRIMARY_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Logo
        self._add_logo(main_frame)
        
        # App info
        self._add_app_info(main_frame)
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, padx=40, pady=8)
        
        # Company info
        self._add_company_info(main_frame)
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, padx=40, pady=8)
        
        # Designer info
        self._add_designer_info(main_frame)
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=1).pack(fill=tk.X, padx=40, pady=5)
        
        # Disclaimer
        self._add_disclaimer(main_frame)
        
        # Close button
        self._add_close_button(main_frame)
        
        # Bind Escape
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def _add_logo(self, parent: tk.Frame) -> None:
        """Add logo image."""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), LOGO_FILE)
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                self._logo_image = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(parent, image=self._logo_image, bg=BRAND_PRIMARY_COLOR)
                logo_label.pack(pady=(10, 15))
        except Exception:
            pass
    
    def _add_app_info(self, parent: tk.Frame) -> None:
        """Add app name and version."""
        tk.Label(
            parent,
            text=APP_NAME,
            font=("Segoe UI", 20, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack()
        
        tk.Label(
            parent,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 12),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 12))
    
    def _add_company_info(self, parent: tk.Frame) -> None:
        """Add company information."""
        tk.Label(
            parent,
            text=COMPANY_NAME_FULL,
            font=("Segoe UI", 16, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(8, 0))
        
        tk.Label(
            parent,
            text=COMPANY_SLOGAN,
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(5, 0))
        
        tk.Label(
            parent,
            text=COMPANY_MOTTO,
            font=("Segoe UI", 10, "italic"),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(5, 12))
    
    def _add_designer_info(self, parent: tk.Frame) -> None:
        """Add designer credits."""
        tk.Label(
            parent,
            text=DESIGNER_NAME,
            font=("Segoe UI", 10, "bold"),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR,
            wraplength=400
        ).pack(pady=(8, 5))
        
        tk.Label(
            parent,
            text=f"📧  {DESIGNER_EMAIL}",
            font=("Segoe UI", 11),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 3))
        
        tk.Label(
            parent,
            text=f"📞  {DESIGNER_PHONE}",
            font=("Segoe UI", 11),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 10))
    
    def _add_disclaimer(self, parent: tk.Frame) -> None:
        """Add disclaimer text."""
        disclaimer_text = (
            "Phần mềm phục vụ cộng đồng lấy mã vạch thuận tiện hơn thay vì lấy thủ công, "
            "không nhằm mục đích thương mại. Người dùng cần tuân thủ luật pháp nước "
            "Cộng Hòa XHCN Việt Nam, nghiêm cấm sử dụng cho mục đích vi phạm pháp luật. "
            "Tự chịu trách nhiệm dân sự/hình sự về việc sử dụng phần mềm."
        )
        tk.Label(
            parent,
            text=disclaimer_text,
            font=("Segoe UI", 8),
            fg="#888888",
            bg=BRAND_PRIMARY_COLOR,
            wraplength=440,
            justify=tk.CENTER
        ).pack(pady=(5, 10))
    
    def _add_close_button(self, parent: tk.Frame) -> None:
        """Add close button."""
        close_btn = tk.Button(
            parent,
            text="Đóng",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_PRIMARY_COLOR,
            bg=BRAND_GOLD_COLOR,
            activebackground=BRAND_ACCENT_COLOR,
            activeforeground=BRAND_PRIMARY_COLOR,
            width=15,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.dialog.destroy
        )
        close_btn.pack(pady=(5, 10))


def show_about_dialog(parent: tk.Tk) -> None:
    """
    Show about dialog.
    
    Args:
        parent: Parent window
    """
    AboutDialog(parent)
