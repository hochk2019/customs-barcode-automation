"""
Database Configuration Dialog v2.0

Extracted from customs_gui.py for GUI decomposition.
Handles database connection configuration with profile support.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional, Dict, Any

from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from logging_system.logger import Logger
from models.config_models import DatabaseProfile


class DatabaseConfigDialog:
    """
    Database configuration dialog with profile support.
    
    Features:
    - Server/database/credentials configuration
    - Profile saving and loading
    - Connection testing
    - Save and reconnect
    """
    
    def __init__(
        self,
        parent: tk.Tk,
        config_manager: ConfigurationManager,
        ecus_connector: EcusDataConnector,
        logger: Logger,
        on_reconnect: Optional[Callable[[], None]] = None
    ):
        """
        Initialize dialog.
        
        Args:
            parent: Parent window
            config_manager: Configuration manager
            ecus_connector: ECUS connector for testing
            logger: Logger instance
            on_reconnect: Callback after reconnection
        """
        self.parent = parent
        self.config_manager = config_manager
        self.ecus_connector = ecus_connector
        self.logger = logger
        self.on_reconnect = on_reconnect
        
        self._create_dialog()
    
    def _create_dialog(self) -> None:
        """Create the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Cấu hình kết nối CSDL")
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (250)
        y = (self.dialog.winfo_screenheight() // 2) - (275)
        self.dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Profile section
        self._create_profile_section(main_frame)
        
        # Connection settings
        self._create_connection_section(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
        
        # Load current values
        self._load_current_config()
        
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def _create_profile_section(self, parent: ttk.Frame) -> None:
        """Create profile selection section."""
        profile_frame = ttk.LabelFrame(parent, text="Hồ sơ kết nối", padding=10)
        profile_frame.pack(fill=tk.X, pady=(0, 10))
        
        profile_row = ttk.Frame(profile_frame)
        profile_row.pack(fill=tk.X)
        
        ttk.Label(profile_row, text="Chọn hồ sơ:").pack(side=tk.LEFT)
        
        self.profile_var = tk.StringVar()
        profiles = self._get_profiles()
        self.profile_combo = ttk.Combobox(
            profile_row, 
            textvariable=self.profile_var,
            values=profiles,
            width=25
        )
        self.profile_combo.pack(side=tk.LEFT, padx=5)
        self.profile_combo.bind('<<ComboboxSelected>>', self._on_profile_selected)
        
        ttk.Button(profile_row, text="Lưu mới", width=8, command=self._save_new_profile).pack(side=tk.LEFT, padx=2)
        ttk.Button(profile_row, text="Xóa", width=5, command=self._delete_profile).pack(side=tk.LEFT, padx=2)
    
    def _create_connection_section(self, parent: ttk.Frame) -> None:
        """Create connection settings section."""
        conn_frame = ttk.LabelFrame(parent, text="Thông tin kết nối", padding=10)
        conn_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Server
        self._create_labeled_entry(conn_frame, "Server:", "server_var", 0)
        
        # Database
        self._create_labeled_entry(conn_frame, "Database:", "database_var", 1)
        
        # Windows Authentication checkbox
        auth_row = ttk.Frame(conn_frame)
        auth_row.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.windows_auth_var = tk.BooleanVar(value=False)  # Default to SQL Auth (sa/password)
        ttk.Checkbutton(
            auth_row, 
            text="Sử dụng Windows Authentication (không cần username/password)",
            variable=self.windows_auth_var,
            command=self._toggle_auth_mode
        ).pack(side=tk.LEFT)
        
        # Username (row 3)
        self._create_labeled_entry(conn_frame, "Username:", "username_var", 3)
        
        # Password with toggle (row 4)
        row_frame = ttk.Frame(conn_frame)
        row_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(row_frame, text="Password:", width=12).pack(side=tk.LEFT)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(row_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            row_frame, 
            text="Hiện", 
            variable=self.show_password_var,
            command=self._toggle_password
        ).pack(side=tk.LEFT)
        
        # Driver - dropdown with available drivers (row 5)
        driver_row = ttk.Frame(conn_frame)
        driver_row.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(driver_row, text="Driver:", width=12).pack(side=tk.LEFT)
        self.driver_var = tk.StringVar()
        
        # Get available ODBC drivers
        try:
            import pyodbc
            available_drivers = pyodbc.drivers()
            # Filter to SQL Server drivers only
            sql_drivers = [d for d in available_drivers if 'SQL' in d.upper()]
            if not sql_drivers:
                sql_drivers = available_drivers[:5]  # Fallback to first 5 drivers
        except:
            sql_drivers = ['SQL Server', 'SQL Server Native Client 10.0', 'ODBC Driver 17 for SQL Server']
        
        self.driver_combo = ttk.Combobox(
            driver_row,
            textvariable=self.driver_var,
            values=sql_drivers,
            width=33
        )
        self.driver_combo.pack(side=tk.LEFT, padx=5)
    
    def _create_labeled_entry(self, parent: ttk.Frame, label: str, var_name: str, row: int) -> None:
        """Create a labeled entry field."""
        row_frame = ttk.Frame(parent)
        row_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(row_frame, text=label, width=12).pack(side=tk.LEFT)
        var = tk.StringVar()
        setattr(self, var_name, var)
        ttk.Entry(row_frame, textvariable=var, width=35).pack(side=tk.LEFT, padx=5)
    
    def _create_buttons(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Kiểm tra kết nối", command=self._test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Lưu & Kết nối lại", command=self._save_and_reconnect).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Đóng", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _get_profiles(self) -> list:
        """Get list of saved profile names."""
        try:
            profiles = self.config_manager.get_database_profiles()
            # get_database_profiles returns list of DatabaseProfile objects
            return [p.name for p in profiles] if profiles else []
        except:
            return []
    
    def _load_current_config(self) -> None:
        """Load current configuration into form."""
        self.server_var.set(self.config_manager.get('ECUS5', 'server', fallback=''))
        self.database_var.set(self.config_manager.get('ECUS5', 'database', fallback=''))
        self.username_var.set(self.config_manager.get('ECUS5', 'username', fallback=''))
        self.password_var.set(self.config_manager.get('ECUS5', 'password', fallback=''))
        
        # Get driver from config, fallback to first available driver
        saved_driver = self.config_manager.get('ECUS5', 'driver', fallback='')
        if saved_driver:
            self.driver_var.set(saved_driver)
        else:
            # Use first available driver from combobox
            if hasattr(self, 'driver_combo') and self.driver_combo['values']:
                self.driver_var.set(self.driver_combo['values'][0])
    
    def _on_profile_selected(self, event=None) -> None:
        """Load selected profile."""
        profile_name = self.profile_var.get()
        if profile_name:
            profile = self.config_manager.get_database_profile(profile_name)
            if profile:
                # profile is a DatabaseProfile object
                self.server_var.set(profile.server or '')
                self.database_var.set(profile.database or '')
                self.username_var.set(profile.username or '')
                self.password_var.set(profile.password or '')
    
    def _save_new_profile(self) -> None:
        """Save current settings as new profile."""
        name = simpledialog.askstring("Tên hồ sơ", "Nhập tên hồ sơ mới:", parent=self.dialog)
        if name:
            # Create DatabaseProfile object (required by ConfigurationManager)
            profile = DatabaseProfile(
                name=name,
                server=self.server_var.get(),
                database=self.database_var.get(),
                username=self.username_var.get(),
                password=self.password_var.get(),
                timeout=30
            )
            self.config_manager.save_database_profile(profile)
            self.profile_combo['values'] = self._get_profiles()
            self.profile_var.set(name)
            messagebox.showinfo("Thành công", f"Đã lưu hồ sơ '{name}'")
    
    def _delete_profile(self) -> None:
        """Delete selected profile."""
        name = self.profile_var.get()
        if name and messagebox.askyesno("Xác nhận", f"Xóa hồ sơ '{name}'?"):
            self.config_manager.delete_database_profile(name)
            self.profile_combo['values'] = self._get_profiles()
            self.profile_var.set('')
    
    def _toggle_password(self) -> None:
        """Toggle password visibility."""
        self.password_entry.config(show="" if self.show_password_var.get() else "*")
    
    def _toggle_auth_mode(self) -> None:
        """Toggle between Windows and SQL Authentication."""
        # Enable/disable username and password fields based on auth mode
        pass  # Fields will still work, just different connection string
    
    def _test_connection(self) -> None:
        """Test database connection."""
        try:
            driver = self.driver_var.get()
            server = self.server_var.get()
            database = self.database_var.get()
            
            if self.windows_auth_var.get():
                # Windows Authentication
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"Trusted_Connection=yes"
                )
            else:
                # SQL Server Authentication
                conn_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={self.username_var.get()};"
                    f"PWD={self.password_var.get()}"
                )
            
            import pyodbc
            conn = pyodbc.connect(conn_str, timeout=10)
            conn.close()
            messagebox.showinfo("Thành công", "Kết nối thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối:\n{e}")
    
    def _save_and_reconnect(self) -> None:
        """Save settings and reconnect."""
        # Save to config
        self.config_manager.set('ECUS5', 'server', self.server_var.get())
        self.config_manager.set('ECUS5', 'database', self.database_var.get())
        self.config_manager.set('ECUS5', 'username', self.username_var.get())
        self.config_manager.set('ECUS5', 'password', self.password_var.get())
        self.config_manager.set('ECUS5', 'driver', self.driver_var.get())
        self.config_manager.save()
        
        # Reconnect
        try:
            self.ecus_connector.disconnect()
            self.ecus_connector.connect()
            messagebox.showinfo("Thành công", "Đã lưu và kết nối lại thành công!")
            
            if self.on_reconnect:
                self.on_reconnect()
            
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lưu thành công nhưng kết nối thất bại:\n{e}")


def show_database_config_dialog(
    parent: tk.Tk,
    config_manager: ConfigurationManager,
    ecus_connector: EcusDataConnector,
    logger: Logger,
    on_reconnect: Optional[Callable[[], None]] = None
) -> None:
    """Show database configuration dialog."""
    DatabaseConfigDialog(parent, config_manager, ecus_connector, logger, on_reconnect)
