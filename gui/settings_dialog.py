"""
Settings Dialog for Customs Barcode Automation

This module provides a settings dialog for configuring:
- Barcode retrieval method (Auto/API/Web)
- PDF file naming format
- Theme (Light/Dark mode)
- Desktop notifications and sound settings

Implements Requirements 1.1, 2.3, 2.4, 2.6, 5.1, 7.1, 7.5, 7.6
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, TYPE_CHECKING

from config.configuration_manager import ConfigurationManager
from gui.styles import ModernStyles
from gui.branding import (
    BRAND_PRIMARY_COLOR, BRAND_SECONDARY_COLOR, BRAND_ACCENT_COLOR,
    BRAND_GOLD_COLOR, BRAND_TEXT_COLOR
)

if TYPE_CHECKING:
    from gui.theme_manager import ThemeManager


class SettingsDialog:
    """
    Settings dialog with retrieval method, PDF naming, and theme options.
    
    Implements Requirements 1.1, 5.1, 7.1, 7.5, 7.6:
    - Display dropdown to select Retrieval_Method with options: Auto, API, Web
    - Display PDF_Naming options: Tax_Code + Declaration_Number, 
      Invoice_Number + Declaration_Number, Bill_of_Lading + Declaration_Number
    - Display theme toggle for Light/Dark mode
    """
    
    # Retrieval method options with display labels
    RETRIEVAL_METHOD_OPTIONS = {
        "auto": "Tự động (API ưu tiên, Web dự phòng)",
        "api": "Chỉ dùng API",
        "web": "Chỉ dùng Web"
    }
    
    # PDF naming format options with display labels and examples
    PDF_NAMING_OPTIONS = {
        "tax_code": "Mã số thuế + Số tờ khai (VD: 2300944637_107784915560.pdf)",
        "invoice": "Số hóa đơn + Số tờ khai (VD: JYE-VN-P-25-259_107784915560.pdf)",
        "bill_of_lading": "Số vận đơn + Số tờ khai (VD: FCHAN2512025_107784915560.pdf)"
    }
    
    # Theme options with display labels
    THEME_OPTIONS = {
        "light": "Sáng (Light)",
        "dark": "Tối (Dark)"
    }
    
    def __init__(self, parent: tk.Tk, config_manager: ConfigurationManager, 
                 on_settings_changed: Optional[callable] = None,
                 theme_manager: Optional['ThemeManager'] = None):
        """
        Initialize Settings dialog.
        
        Args:
            parent: Parent window
            config_manager: Configuration manager instance
            on_settings_changed: Optional callback function called when settings are saved.
                                 Receives (retrieval_method: str, pdf_naming_format: str) as arguments.
            theme_manager: Optional ThemeManager instance for theme switching
        """
        self.parent = parent
        self.config_manager = config_manager
        self.on_settings_changed = on_settings_changed
        self.theme_manager = theme_manager
        self.dialog: Optional[tk.Toplevel] = None
        
        # Variables for settings
        self.retrieval_method_var: Optional[tk.StringVar] = None
        self.pdf_naming_var: Optional[tk.StringVar] = None
        self.theme_var: Optional[tk.StringVar] = None
        self.notifications_var: Optional[tk.BooleanVar] = None
        self.sound_var: Optional[tk.BooleanVar] = None
        self.batch_limit_var: Optional[tk.IntVar] = None
        
        # Create and show dialog
        self._create_dialog()
    
    def _create_dialog(self) -> None:
        """Create the settings dialog window with glossy black theme."""
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Cài đặt")
        self.dialog.geometry("520x580")  # Increased height for notification and batch limit sections
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=BRAND_PRIMARY_COLOR)
        
        # Center dialog on parent window
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Main frame with glossy black background
        main_frame = tk.Frame(self.dialog, bg=BRAND_PRIMARY_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="⚙ Cài đặt",
            font=("Segoe UI", 16, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, pady=(0, 15))
        
        # Create retrieval method section
        self._create_retrieval_method_section(main_frame)
        
        # Create PDF naming section
        self._create_pdf_naming_section(main_frame)
        
        # Create theme section (Requirements 7.1, 7.5, 7.6)
        self._create_theme_section(main_frame)
        
        # Create notification settings section (Requirements 2.3, 2.4, 2.6)
        self._create_notification_section(main_frame)
        
        # Create batch limit section (Requirements 10.3)
        self._create_batch_limit_section(main_frame)
        
        # Gold separator before buttons
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, pady=(15, 15))
        
        # Create button section
        self._create_buttons(main_frame)
        
        # Bind Escape key to close
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def _create_retrieval_method_section(self, parent: tk.Frame) -> None:
        """
        Create dropdown for barcode retrieval method selection.
        
        Args:
            parent: Parent frame
        """
        # Section label
        label = tk.Label(
            parent,
            text="Phương thức lấy mã vạch:",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Get current value
        current_method = self.config_manager.get_retrieval_method()
        
        # Create StringVar with display value
        self.retrieval_method_var = tk.StringVar(
            value=self.RETRIEVAL_METHOD_OPTIONS.get(current_method, self.RETRIEVAL_METHOD_OPTIONS["auto"])
        )
        
        # Create combobox with display values
        retrieval_combo = ttk.Combobox(
            parent,
            textvariable=self.retrieval_method_var,
            values=list(self.RETRIEVAL_METHOD_OPTIONS.values()),
            state="readonly",
            width=50,
            font=("Segoe UI", 10)
        )
        retrieval_combo.pack(anchor=tk.W, pady=(0, 15))
    
    def _create_pdf_naming_section(self, parent: tk.Frame) -> None:
        """
        Create dropdown for PDF file naming format.
        
        Args:
            parent: Parent frame
        """
        # Section label
        label = tk.Label(
            parent,
            text="Định dạng tên file PDF:",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Get current value
        current_format = self.config_manager.get_pdf_naming_format()
        
        # Create StringVar with display value
        self.pdf_naming_var = tk.StringVar(
            value=self.PDF_NAMING_OPTIONS.get(current_format, self.PDF_NAMING_OPTIONS["tax_code"])
        )
        
        # Create combobox with display values
        naming_combo = ttk.Combobox(
            parent,
            textvariable=self.pdf_naming_var,
            values=list(self.PDF_NAMING_OPTIONS.values()),
            state="readonly",
            width=50,
            font=("Segoe UI", 10)
        )
        naming_combo.pack(anchor=tk.W, pady=(0, 10))
    
    def _create_theme_section(self, parent: tk.Frame) -> None:
        """
        Create dropdown for theme selection.
        
        Implements Requirements 7.1, 7.5, 7.6
        
        Args:
            parent: Parent frame
        """
        # Section label
        label = tk.Label(
            parent,
            text="Giao diện (Theme):",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        # Get current value
        current_theme = self.config_manager.get_theme()
        
        # Create StringVar with display value
        self.theme_var = tk.StringVar(
            value=self.THEME_OPTIONS.get(current_theme, self.THEME_OPTIONS["light"])
        )
        
        # Create combobox with display values
        theme_combo = ttk.Combobox(
            parent,
            textvariable=self.theme_var,
            values=list(self.THEME_OPTIONS.values()),
            state="readonly",
            width=50,
            font=("Segoe UI", 10)
        )
        theme_combo.pack(anchor=tk.W, pady=(0, 10))
    
    def _get_theme_key(self) -> str:
        """
        Get the config key for the selected theme.
        
        Returns:
            Config key ('light' or 'dark')
        """
        display_value = self.theme_var.get()
        for key, value in self.THEME_OPTIONS.items():
            if value == display_value:
                return key
        return "light"  # Default fallback
    
    def _create_notification_section(self, parent: tk.Frame) -> None:
        """
        Create notification and sound settings section.
        
        Implements Requirements 2.3, 2.4, 2.6
        
        Args:
            parent: Parent frame
        """
        # Section label
        label = tk.Label(
            parent,
            text="Thông báo:",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        label.pack(anchor=tk.W, pady=(10, 5))
        
        # Checkbox frame
        checkbox_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        checkbox_frame.pack(anchor=tk.W, pady=(0, 10))
        
        # Get current values from config
        notifications_enabled = self.config_manager.get_notifications_enabled()
        sound_enabled = self.config_manager.get_sound_enabled()
        
        # Notifications checkbox (Requirement 2.3, 2.4)
        self.notifications_var = tk.BooleanVar(value=notifications_enabled)
        notifications_cb = tk.Checkbutton(
            checkbox_frame,
            text="Hiển thị thông báo desktop khi hoàn thành",
            variable=self.notifications_var,
            font=("Segoe UI", 10),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_TEXT_COLOR,
            selectcolor=BRAND_SECONDARY_COLOR
        )
        notifications_cb.pack(anchor=tk.W, pady=2)
        
        # Sound checkbox (Requirement 2.6)
        self.sound_var = tk.BooleanVar(value=sound_enabled)
        sound_cb = tk.Checkbutton(
            checkbox_frame,
            text="Phát âm thanh khi hoàn thành",
            variable=self.sound_var,
            font=("Segoe UI", 10),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_TEXT_COLOR,
            selectcolor=BRAND_SECONDARY_COLOR
        )
        sound_cb.pack(anchor=tk.W, pady=2)
    
    def _create_batch_limit_section(self, parent: tk.Frame) -> None:
        """
        Create batch limit setting section.
        
        Implements Requirements 10.3
        
        Args:
            parent: Parent frame
        """
        # Section label
        label = tk.Label(
            parent,
            text="Giới hạn tải xuống:",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        label.pack(anchor=tk.W, pady=(10, 5))
        
        # Batch limit frame
        batch_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        batch_frame.pack(anchor=tk.W, pady=(0, 10))
        
        # Get current value from config
        current_limit = self.config_manager.get_batch_limit()
        
        # Batch limit spinbox (Requirement 10.3)
        self.batch_limit_var = tk.IntVar(value=current_limit)
        
        tk.Label(
            batch_frame,
            text="Số tờ khai tối đa mỗi lần tải (1-50):",
            font=("Segoe UI", 10),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        batch_spinbox = ttk.Spinbox(
            batch_frame,
            from_=1,
            to=50,
            textvariable=self.batch_limit_var,
            width=5,
            font=("Segoe UI", 10)
        )
        batch_spinbox.pack(side=tk.LEFT)
    
    def _create_buttons(self, parent: tk.Frame) -> None:
        """
        Create save and cancel buttons.
        
        Args:
            parent: Parent frame
        """
        # Button frame
        button_frame = tk.Frame(parent, bg=BRAND_PRIMARY_COLOR)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Cancel button - on the right
        cancel_btn = tk.Button(
            button_frame,
            text="Hủy",
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_SECONDARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_ACCENT_COLOR,
            width=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Save button - Gold with black text
        save_btn = tk.Button(
            button_frame,
            text="Lưu",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_PRIMARY_COLOR,
            bg=BRAND_GOLD_COLOR,
            activebackground=BRAND_ACCENT_COLOR,
            activeforeground=BRAND_PRIMARY_COLOR,
            width=12,
            pady=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.save_settings
        )
        save_btn.pack(side=tk.RIGHT)
    
    def _get_retrieval_method_key(self) -> str:
        """
        Get the config key for the selected retrieval method.
        
        Returns:
            Config key ('auto', 'api', or 'web')
        """
        display_value = self.retrieval_method_var.get()
        for key, value in self.RETRIEVAL_METHOD_OPTIONS.items():
            if value == display_value:
                return key
        return "auto"  # Default fallback
    
    def _get_pdf_naming_key(self) -> str:
        """
        Get the config key for the selected PDF naming format.
        
        Returns:
            Config key ('tax_code', 'invoice', or 'bill_of_lading')
        """
        display_value = self.pdf_naming_var.get()
        for key, value in self.PDF_NAMING_OPTIONS.items():
            if value == display_value:
                return key
        return "tax_code"  # Default fallback
    
    def save_settings(self) -> None:
        """Save all settings to config.ini and notify listeners."""
        try:
            # Get selected values as config keys
            retrieval_method = self._get_retrieval_method_key()
            pdf_naming_format = self._get_pdf_naming_key()
            theme = self._get_theme_key()
            
            # Get notification settings (Requirements 2.3, 2.6)
            notifications_enabled = self.notifications_var.get() if self.notifications_var else True
            sound_enabled = self.sound_var.get() if self.sound_var else True
            
            # Get batch limit setting (Requirements 10.3, 10.5)
            batch_limit = self.batch_limit_var.get() if self.batch_limit_var else 20
            # Clamp to valid range
            batch_limit = max(1, min(50, batch_limit))
            
            # Save to config manager
            self.config_manager.set_retrieval_method(retrieval_method)
            self.config_manager.set_pdf_naming_format(pdf_naming_format)
            self.config_manager.set_theme(theme)
            self.config_manager.set_notifications_enabled(notifications_enabled)
            self.config_manager.set_sound_enabled(sound_enabled)
            self.config_manager.set_batch_limit(batch_limit)
            
            # Persist to file
            self.config_manager.save()
            
            # Apply theme immediately if theme_manager is available (Requirement 7.6)
            if self.theme_manager:
                self.theme_manager.apply_theme(theme)
            
            # Notify callback if provided (to update BarcodeRetriever immediately)
            if self.on_settings_changed:
                try:
                    self.on_settings_changed(retrieval_method, pdf_naming_format)
                except Exception as callback_error:
                    # Log but don't fail if callback has issues
                    print(f"Warning: Settings callback failed: {callback_error}")
            
            # Show success message
            messagebox.showinfo(
                "Thành công",
                "Đã lưu cài đặt thành công!\nCài đặt mới sẽ được áp dụng ngay lập tức."
            )
            
            # Close dialog
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Lỗi",
                f"Không thể lưu cài đặt:\n{str(e)}"
            )
    
    def get_retrieval_method(self) -> str:
        """
        Get the currently selected retrieval method.
        
        Returns:
            Retrieval method key ('auto', 'api', or 'web')
        """
        return self._get_retrieval_method_key()
    
    def get_pdf_naming_format(self) -> str:
        """
        Get the currently selected PDF naming format.
        
        Returns:
            PDF naming format key ('tax_code', 'invoice', or 'bill_of_lading')
        """
        return self._get_pdf_naming_key()
