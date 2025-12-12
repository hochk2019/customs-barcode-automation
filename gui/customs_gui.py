"""
Customs Barcode Automation GUI

This module provides the graphical user interface for the customs barcode automation system.

Copyright (c) 2024 Golden Logistics Co.,Ltd
Designer: Học HK
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, List
import threading
from datetime import datetime
import os
import subprocess
import platform
from PIL import Image, ImageTk

from models.declaration_models import Declaration, WorkflowResult, OperationMode, ProcessedDeclaration
from scheduler.scheduler import Scheduler
from database.tracking_database import TrackingDatabase
from database.ecus_connector import EcusDataConnector
from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger
from processors.company_scanner import CompanyScanner
from processors.preview_manager import PreviewManager
from gui.enhanced_manual_panel import EnhancedManualPanel
from gui.styles import ModernStyles
from gui.settings_dialog import SettingsDialog
from gui.statistics_bar import StatisticsBar
from gui.theme_manager import ThemeManager
from gui.notification_manager import NotificationManager
from gui.window_state import WindowStateManager
from database.backup_service import BackupService
from gui.branding import (
    APP_VERSION, APP_NAME, APP_FULL_NAME, WINDOW_TITLE,
    COMPANY_NAME, COMPANY_SLOGAN, COMPANY_MOTTO,
    DESIGNER_NAME, DESIGNER_EMAIL, DESIGNER_PHONE, LOGO_FILE,
    BRAND_PRIMARY_COLOR, BRAND_SECONDARY_COLOR, BRAND_ACCENT_COLOR,
    BRAND_GOLD_COLOR, BRAND_TEXT_COLOR
)


class CustomsAutomationGUI:
    """
    GUI application for customs barcode automation
    
    Responsibilities:
    - Display application status
    - Show statistics (processed, errors, etc.)
    - Provide start/stop controls
    - Support automatic/manual mode switching
    - Allow configuration changes
    - Display recent logs
    - Manage processed declarations list
    - Support re-download functionality
    """
    
    def __init__(
        self,
        root: tk.Tk,
        scheduler: Scheduler,
        tracking_db: TrackingDatabase,
        ecus_connector: EcusDataConnector,
        config_manager: ConfigurationManager,
        logger: Logger,
        barcode_retriever = None,
        file_manager = None
    ):
        """
        Initialize GUI application
        
        Args:
            root: Tkinter root window
            scheduler: Scheduler instance
            tracking_db: Tracking database instance
            ecus_connector: ECUS5 database connector instance
            config_manager: Configuration manager instance
            logger: Logger instance
            barcode_retriever: BarcodeRetriever instance (optional)
            file_manager: FileManager instance (optional)
        """
        self.root = root
        self.scheduler = scheduler
        self.tracking_db = tracking_db
        self.ecus_connector = ecus_connector
        self.config_manager = config_manager
        self.logger = logger
        self.barcode_retriever = barcode_retriever
        self.file_manager = file_manager
        
        # Statistics tracking
        self.total_processed = 0
        self.total_success = 0
        self.total_errors = 0
        self.last_run_time: Optional[datetime] = None
        
        # GUI state (is_running removed - Automatic mode no longer supported per Requirements 1.4)
        self.selected_declarations: List[ProcessedDeclaration] = []
        
        # Setup window with responsive layout (Requirements 1.4)
        self.root.title(WINDOW_TITLE)
        self.root.minsize(900, 600)  # Minimum size to prevent layout breakage
        
        # Initialize WindowStateManager and restore window state (Requirements 6.1, 6.2, 6.3, 6.4)
        self.window_state_manager = WindowStateManager(self.root, self.config_manager)
        self.window_state_manager.restore_state()
        
        # Bind window close event to save state
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Set window icon
        self._set_window_icon()
        
        # Configure modern styles at application startup (Requirement 4.1)
        self.style = ModernStyles.configure_ttk_styles(self.root)
        self.root.configure(bg=ModernStyles.BG_PRIMARY)
        
        # Initialize ThemeManager and apply saved theme (Requirements 7.5, 7.6)
        self.theme_manager = ThemeManager(self.root, self.config_manager)
        # Note: Theme is applied after GUI components are created to ensure all widgets exist
        
        # Initialize NotificationManager for desktop notifications (Requirements 2.1, 2.2)
        self.notification_manager = NotificationManager(self.config_manager)
        
        # Create GUI components (Responsive layout - Requirements 9.1)
        self._create_header_banner()
        self._create_control_panel()
        self._create_processed_declarations_panel()
        # Recent Logs panel removed per Requirements 9.1 to save vertical space
        self._create_footer()
        
        # Load initial data
        self._load_processed_declarations()
        
        # Apply saved theme after all GUI components are created (Requirements 7.5)
        saved_theme = self.config_manager.get_theme()
        if saved_theme == 'dark':
            self.theme_manager.apply_theme('dark')
        
        # Initialize BackupService and check for backup on startup (Requirements 8.1)
        self._init_backup_service()
        
        self.logger.info("GUI initialized")
    
    def _init_backup_service(self) -> None:
        """
        Initialize BackupService and check for backup on startup.
        
        Requirements: 8.1
        """
        try:
            # Get tracking database path
            db_path = self.tracking_db.db_path if hasattr(self.tracking_db, 'db_path') else 'data/tracking.db'
            
            # Initialize backup service
            self.backup_service = BackupService(db_path)
            
            # Check and create backup if needed
            backup_created = self.backup_service.check_and_backup()
            
            if backup_created:
                self.logger.info("Database backup created on startup")
            else:
                self.logger.info("Database backup not needed (recent backup exists)")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize backup service: {e}")
            self.backup_service = None
    
    def _on_window_close(self) -> None:
        """
        Handle window close event - save window state before closing.
        
        Requirements: 6.1
        """
        try:
            # Save window state
            self.window_state_manager.save_state()
            self.logger.info("Window state saved")
        except Exception as e:
            self.logger.warning(f"Failed to save window state: {e}")
        finally:
            # Destroy window
            self.root.destroy()
    
    def _set_window_icon(self) -> None:
        """Set window icon from logo file"""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), LOGO_FILE)
            if os.path.exists(logo_path):
                icon = ImageTk.PhotoImage(Image.open(logo_path))
                self.root.iconphoto(True, icon)
                self._icon_ref = icon  # Keep reference to prevent garbage collection
        except Exception as e:
            self.logger.warning(f"Could not set window icon: {e}")
    
    def _create_header_banner(self) -> None:
        """Create modern header banner with glossy black background and high contrast"""
        # Header frame with glossy black background (increased height for designer info)
        header_frame = tk.Frame(self.root, bg=BRAND_PRIMARY_COLOR, height=105)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        # Inner container for content
        header_content = tk.Frame(header_frame, bg=BRAND_PRIMARY_COLOR)
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)
        
        # LEFT SIDE: Logo + Motto (horizontal layout)
        left_frame = tk.Frame(header_content, bg=BRAND_PRIMARY_COLOR)
        left_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        # Logo on the left
        logo_container = tk.Frame(left_frame, bg=BRAND_PRIMARY_COLOR)
        logo_container.pack(side=tk.LEFT)
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), LOGO_FILE)
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((65, 65), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_container, image=self.logo_photo, bg=BRAND_PRIMARY_COLOR)
                logo_label.pack()
        except Exception as e:
            self.logger.warning(f"Could not load logo: {e}")
        
        # Motto next to logo - 3 lines, italic, gold color
        motto_frame = tk.Frame(left_frame, bg=BRAND_PRIMARY_COLOR)
        motto_frame.pack(side=tk.LEFT, padx=(15, 0), fill=tk.Y)
        
        # Line 1: "Thích thì thuê" - moved up (pady=0 at top)
        tk.Label(
            motto_frame,
            text="Thích thì thuê",
            font=("Segoe UI", 10, "italic"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.W, pady=(0, 0))
        
        # Line 2: "Không thích thì chê"
        tk.Label(
            motto_frame,
            text="Không thích thì chê",
            font=("Segoe UI", 10, "italic"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # Line 3: "Nhưng đừng bỏ!" - reduced bottom padding
        tk.Label(
            motto_frame,
            text="Nhưng đừng bỏ!",
            font=("Segoe UI", 10, "italic"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(anchor=tk.W, pady=(1, 0))
        
        # CENTER: Company name (large) + Slogan (centered below)
        center_frame = tk.Frame(header_content, bg=BRAND_PRIMARY_COLOR)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Company name - Large gold text, centered
        company_label = tk.Label(
            center_frame,
            text=COMPANY_NAME,
            font=("Segoe UI", 22, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        company_label.pack(anchor=tk.CENTER, pady=(5, 0))
        
        # Slogan - White text, centered below company name
        slogan_label = tk.Label(
            center_frame,
            text=COMPANY_SLOGAN,
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        slogan_label.pack(anchor=tk.CENTER, pady=(2, 0))
        
        # RIGHT SIDE: About button + Version
        right_frame = tk.Frame(header_content, bg=BRAND_PRIMARY_COLOR)
        right_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Button frame for About and Update buttons
        button_row = tk.Frame(right_frame, bg=BRAND_PRIMARY_COLOR)
        button_row.pack(anchor=tk.E)
        
        # About button - Gold text on dark background with gold border
        about_btn = tk.Button(
            button_row,
            text="ℹ  Giới thiệu",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_SECONDARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_ACCENT_COLOR,
            relief=tk.RIDGE,
            bd=2,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self._show_about_dialog
        )
        about_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Update check button
        update_btn = tk.Button(
            button_row,
            text="🔄  Cập nhật",
            font=("Segoe UI", 11, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_SECONDARY_COLOR,
            activebackground=BRAND_PRIMARY_COLOR,
            activeforeground=BRAND_ACCENT_COLOR,
            relief=tk.RIDGE,
            bd=2,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self._check_for_updates
        )
        update_btn.pack(side=tk.LEFT)
        
        # Version below button
        version_label = tk.Label(
            right_frame,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 9),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        version_label.pack(anchor=tk.E, pady=(5, 0))
        
        # Designer info below version
        designer_header_label = tk.Label(
            right_frame,
            text=f"Designer: {DESIGNER_NAME}",
            font=("Segoe UI", 9),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        designer_header_label.pack(anchor=tk.E, pady=(2, 0))
    
    def _create_footer(self) -> None:
        """Create footer with designer info and contact"""
        footer_frame = tk.Frame(self.root, bg=BRAND_PRIMARY_COLOR, height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Footer content
        footer_content = tk.Frame(footer_frame, bg=BRAND_PRIMARY_COLOR)
        footer_content.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # Left: Designer info
        designer_label = tk.Label(
            footer_content,
            text=f"Designer: {DESIGNER_NAME}",
            font=("Segoe UI", 9),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        designer_label.pack(side=tk.LEFT, pady=5)
        
        # Right: Contact info
        contact_label = tk.Label(
            footer_content,
            text=f"📧 {DESIGNER_EMAIL}  |  📞 {DESIGNER_PHONE}",
            font=("Segoe UI", 9),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        )
        contact_label.pack(side=tk.RIGHT, pady=5)
    
    def _check_for_updates(self) -> None:
        """Check for updates manually."""
        import threading
        from tkinter import messagebox
        
        def check_updates():
            try:
                from update.update_checker import UpdateChecker
                from gui.update_dialog import UpdateDialog, DownloadProgressDialog, InstallPromptDialog
                from update.download_manager import DownloadManager, DownloadCancelledError
                from update.models import DownloadProgress
                
                github_repo = self.config_manager.get('Update', 'github_repo', fallback='')
                if not github_repo:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Kiểm tra cập nhật",
                        "Chưa cấu hình GitHub repository cho cập nhật."
                    ))
                    return
                
                checker = UpdateChecker(APP_VERSION, github_repo, self.config_manager)
                update_info = checker.check_for_updates(force=True)
                
                if update_info:
                    def show_dialog():
                        dialog = UpdateDialog(self.root, update_info)
                        result = dialog.show()
                        
                        if result == "update_now":
                            download_manager = DownloadManager()
                            
                            # Determine file extension from download URL
                            download_url = update_info.download_url
                            if download_url.endswith('.zip'):
                                file_ext = '.zip'
                            else:
                                file_ext = '.exe'
                            
                            filename = f"CustomsBarcodeAutomation_{update_info.latest_version}{file_ext}"
                            progress_dialog = DownloadProgressDialog(self.root, filename)
                            
                            def progress_callback(downloaded, total, speed):
                                progress = DownloadProgress(downloaded, total, speed)
                                self.root.after(0, lambda: progress_dialog.update_progress(progress))
                            
                            def download_thread():
                                try:
                                    filepath = download_manager.download_file(
                                        download_url,
                                        filename,
                                        update_info.file_size,
                                        progress_callback
                                    )
                                    
                                    self.root.after(0, progress_dialog.close)
                                    
                                    # Handle ZIP extraction
                                    if download_manager.is_zip_file(filepath):
                                        try:
                                            extract_dir = download_manager.extract_zip(filepath)
                                            # Show message about extracted location
                                            self.root.after(0, lambda: messagebox.showinfo(
                                                "Tải xuống hoàn tất",
                                                f"Đã tải và giải nén phiên bản mới tại:\n{extract_dir}\n\n"
                                                "Vui lòng đóng ứng dụng và chạy file CustomsAutomation.exe trong thư mục đã giải nén."
                                            ))
                                            # Open the extracted folder
                                            import subprocess
                                            subprocess.Popen(['explorer', extract_dir])
                                        except Exception as e:
                                            self.logger.error(f"Extraction failed: {e}")
                                            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Giải nén thất bại: {e}"))
                                    else:
                                        # Handle EXE installer
                                        def show_install_prompt():
                                            install_dialog = InstallPromptDialog(self.root, filepath)
                                            install_result = install_dialog.show()
                                            
                                            if install_result == "install_now":
                                                import subprocess
                                                subprocess.Popen([filepath], shell=True)
                                                self.root.after(500, self.root.destroy)
                                            else:
                                                download_manager.save_pending_installer(filepath, self.config_manager)
                                        
                                        self.root.after(0, show_install_prompt)
                                    
                                except DownloadCancelledError:
                                    self.logger.info("Download cancelled by user")
                                except Exception as e:
                                    self.logger.error(f"Download failed: {e}")
                                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Tải xuống thất bại: {e}"))
                            
                            threading.Thread(target=download_thread, daemon=True).start()
                            
                        elif result == "skip_version":
                            checker.skip_version(update_info.latest_version)
                    
                    self.root.after(0, show_dialog)
                else:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Kiểm tra cập nhật",
                        "Bạn đang sử dụng phiên bản mới nhất."
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Update check failed: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Lỗi",
                    f"Không thể kiểm tra cập nhật: {e}"
                ))
        
        threading.Thread(target=check_updates, daemon=True).start()
    
    def _show_about_dialog(self) -> None:
        """Show About dialog with glossy black background and high contrast"""
        from gui.branding import COMPANY_NAME_FULL
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Giới thiệu")
        dialog.geometry("500x650")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=BRAND_PRIMARY_COLOR)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame with glossy black background
        main_frame = tk.Frame(dialog, bg=BRAND_PRIMARY_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Logo - Larger
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), LOGO_FILE)
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                self.about_logo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(main_frame, image=self.about_logo, bg=BRAND_PRIMARY_COLOR)
                logo_label.pack(pady=(10, 15))
        except Exception:
            pass
        
        # App name - Large gold text
        tk.Label(
            main_frame,
            text=APP_NAME,
            font=("Segoe UI", 20, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack()
        
        # Version
        tk.Label(
            main_frame,
            text=f"Version {APP_VERSION}",
            font=("Segoe UI", 12),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 12))
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, padx=40, pady=8)
        
        # Company name - Large gold
        tk.Label(
            main_frame,
            text=COMPANY_NAME_FULL,
            font=("Segoe UI", 16, "bold"),
            fg=BRAND_GOLD_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(8, 0))
        
        # Slogan - White
        tk.Label(
            main_frame,
            text=COMPANY_SLOGAN,
            font=("Segoe UI", 11),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(5, 0))
        
        # Motto - Gold accent, italic
        tk.Label(
            main_frame,
            text=COMPANY_MOTTO,
            font=("Segoe UI", 10, "italic"),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(5, 12))
        
        # Gold separator
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=2).pack(fill=tk.X, padx=40, pady=8)
        
        # Designer info - White
        tk.Label(
            main_frame,
            text=f"Designer: {DESIGNER_NAME}",
            font=("Segoe UI", 12, "bold"),
            fg=BRAND_TEXT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(8, 5))
        
        # Email - Gold accent
        tk.Label(
            main_frame,
            text=f"📧  {DESIGNER_EMAIL}",
            font=("Segoe UI", 11),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 3))
        
        # Phone - Gold accent
        tk.Label(
            main_frame,
            text=f"📞  {DESIGNER_PHONE}",
            font=("Segoe UI", 11),
            fg=BRAND_ACCENT_COLOR,
            bg=BRAND_PRIMARY_COLOR
        ).pack(pady=(0, 10))
        
        # Gold separator before disclaimer
        tk.Frame(main_frame, bg=BRAND_GOLD_COLOR, height=1).pack(fill=tk.X, padx=40, pady=5)
        
        # Disclaimer text - smaller font, gray color, at bottom
        disclaimer_text = (
            "Phần mềm phục vụ cộng đồng lấy mã vạch thuận tiện hơn thay vì lấy thủ công, "
            "không nhằm mục đích thương mại. Người dùng cần tuân thủ luật pháp nước "
            "Cộng Hòa XHCN Việt Nam, nghiêm cấm sử dụng cho mục đích vi phạm pháp luật. "
            "Tự chịu trách nhiệm dân sự/hình sự về việc sử dụng phần mềm."
        )
        tk.Label(
            main_frame,
            text=disclaimer_text,
            font=("Segoe UI", 8),
            fg="#888888",  # Gray color for disclaimer
            bg=BRAND_PRIMARY_COLOR,
            wraplength=440,
            justify=tk.CENTER
        ).pack(pady=(5, 10))
        
        # Close button - Gold with black text
        close_btn = tk.Button(
            main_frame,
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
            command=dialog.destroy
        )
        close_btn.pack(pady=(5, 10))
        
        # Bind Escape key
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def _create_control_panel(self) -> None:
        """Create control panel frame with status display and controls"""
        # Main control frame
        control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Combined Status and Statistics row (compact horizontal layout)
        status_stats_frame = ttk.Frame(control_frame)
        status_stats_frame.pack(fill=tk.X, pady=5)
        
        # Status section
        ttk.Label(
            status_stats_frame, 
            text="Status:", 
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(
            status_stats_frame, 
            text="● Ready", 
            foreground=ModernStyles.INFO_COLOR, 
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Database connection status
        ttk.Label(
            status_stats_frame, 
            text="  |  DB:", 
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, "bold")
        ).pack(side=tk.LEFT, padx=5)
        self.db_status_label = ttk.Label(
            status_stats_frame, 
            text="● Checking...", 
            foreground=ModernStyles.WARNING_COLOR, 
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        )
        self.db_status_label.pack(side=tk.LEFT, padx=5)
        
        # Database configuration button
        db_config_button = ttk.Button(
            status_stats_frame, 
            text="⚙ Cấu hình DB", 
            command=self._show_database_config_dialog,
            width=14
        )
        db_config_button.pack(side=tk.LEFT, padx=10)
        
        # Settings button (Requirements 1.1, 5.1)
        settings_button = ttk.Button(
            status_stats_frame,
            text="⚙ Cài đặt",
            command=self._show_settings_dialog,
            width=12
        )
        settings_button.pack(side=tk.LEFT, padx=5)
        
        # Check database connection in background
        self._check_database_connection()
        
        # Set scheduler to Manual mode by default (Automatic mode removed per Requirements 1.1, 1.2, 1.3)
        self.scheduler.set_operation_mode(OperationMode.MANUAL)
        
        # Statistics section using StatisticsBar component (Requirements 7.1, 7.2)
        self.statistics_bar = StatisticsBar(control_frame)
        self.statistics_bar.pack(fill=tk.X, pady=5)
        
        # Keep references for backward compatibility
        self.processed_label = self.statistics_bar.processed_label
        self.success_label = self.statistics_bar.retrieved_label
        self.errors_label = self.statistics_bar.errors_label
        self.last_run_label = self.statistics_bar.last_run_label
        self.last_run_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Start/Stop/Run Once buttons removed per Requirements 1.4
        # The EnhancedManualPanel provides all necessary controls for manual operation
        
        # Enhanced Manual Mode Panel
        # Initialize CompanyScanner and PreviewManager
        company_scanner = CompanyScanner(
            ecus_connector=self.ecus_connector,
            tracking_db=self.tracking_db,
            logger=self.logger
        )
        
        preview_manager = PreviewManager(
            ecus_connector=self.ecus_connector,
            logger=self.logger
        )
        
        # Create EnhancedManualPanel with download complete callback
        self.enhanced_manual_panel = EnhancedManualPanel(
            parent=control_frame,
            company_scanner=company_scanner,
            preview_manager=preview_manager,
            logger=self.logger,
            barcode_retriever=self.barcode_retriever,
            file_manager=self.file_manager,
            tracking_db=self.tracking_db,
            on_download_complete=self._on_download_complete
        )
        self.enhanced_manual_panel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Output directory configuration moved to EnhancedManualPanel (Requirements 3.1, 3.2, 3.3)
        # Keep output_path_var for compatibility with other methods
        self.output_path_var = tk.StringVar(value=self.config_manager.get_output_path())
    
    def _create_processed_declarations_panel(self) -> None:
        """Create processed declarations panel with search and management"""
        # Main frame with modern styling
        decl_frame = ttk.LabelFrame(
            self.root, 
            text="Processed Declarations", 
            padding=10,
            style='Card.TLabelframe'
        )
        decl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Search frame
        search_frame = ttk.Frame(decl_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            search_frame, 
            text="Search:",
            font=(ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL)
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_declarations, width=12)
        search_button.pack(side=tk.LEFT, padx=5)
        
        # Table frame with scrollbar
        table_frame = ttk.Frame(decl_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for declarations with modern styling (Requirement 4.8)
        columns = ("declaration_number", "tax_code", "date", "timestamp")
        self.declarations_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            selectmode="extended",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configure scrollbars
        v_scrollbar.config(command=self.declarations_tree.yview)
        h_scrollbar.config(command=self.declarations_tree.xview)
        
        # Column headings
        self.declarations_tree.heading("#0", text="☐")
        self.declarations_tree.heading("declaration_number", text="Declaration Number")
        self.declarations_tree.heading("tax_code", text="Tax Code")
        self.declarations_tree.heading("date", text="Date")
        self.declarations_tree.heading("timestamp", text="Processed At")
        
        # Column widths
        self.declarations_tree.column("#0", width=30, stretch=False)
        self.declarations_tree.column("declaration_number", width=200)
        self.declarations_tree.column("tax_code", width=150)
        self.declarations_tree.column("date", width=120)
        self.declarations_tree.column("timestamp", width=180)
        
        # Configure alternating row colors and hover highlighting (Requirement 4.8)
        ModernStyles.configure_treeview_tags(self.declarations_tree)
        
        # Bind hover events for highlighting
        self.declarations_tree.bind('<Motion>', self._on_tree_hover)
        self.declarations_tree.bind('<Leave>', self._on_tree_leave)
        self._hover_item = None
        
        self.declarations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(decl_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.redownload_button = ttk.Button(
            action_frame,
            text="Re-download Selected",
            command=self.redownload_selected,
            width=20
        )
        self.redownload_button.pack(side=tk.LEFT, padx=5)
        
        self.open_location_button = ttk.Button(
            action_frame,
            text="Open File Location",
            command=self.open_file_location,
            width=20
        )
        self.open_location_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(
            action_frame,
            text="Refresh",
            command=self._load_processed_declarations,
            width=12
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    # _create_log_panel removed per Requirements 9.1 to save vertical space
    # Logs are now only written to the logger file
    
    # Event Handlers (Subtask 15.4)
    # Note: start_automation, stop_automation, run_manual_cycle methods removed
    # per Requirements 1.4 - Automatic mode buttons are no longer displayed
    # The EnhancedManualPanel provides all necessary controls for manual operation
    

    
    def browse_output_directory(self) -> None:
        """Open directory selection dialog"""
        try:
            current_path = self.output_path_var.get()
            
            directory = filedialog.askdirectory(
                title="Select Output Directory",
                initialdir=current_path if os.path.exists(current_path) else None
            )
            
            if directory:
                # Update configuration
                self.config_manager.set_output_path(directory)
                self.config_manager.save()
                
                # Update UI
                self.output_path_var.set(directory)
                
                self.append_log("INFO", f"Output directory changed to: {directory}")
                self.logger.info(f"Output directory changed to: {directory}")
                
        except Exception as e:
            self.logger.error(f"Failed to change output directory: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to change output directory:\n{str(e)}")
    
    def search_declarations(self) -> None:
        """Search declarations by declaration number or tax code"""
        try:
            query = self.search_var.get().strip()
            
            if not query:
                # If empty, load all declarations
                self._load_processed_declarations()
                return
            
            # Search in tracking database
            results = self.tracking_db.search_declarations(query)
            
            # Update tree view
            self._populate_declarations_tree(results)
            
            self.append_log("INFO", f"Search completed: {len(results)} results found")
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"Search failed:\n{str(e)}")
    
    def redownload_selected(self) -> None:
        """Re-download barcodes for selected declarations"""
        def redownload_in_thread():
            try:
                # Get selected items
                selected_items = self.declarations_tree.selection()
                
                if not selected_items:
                    self.root.after(0, lambda: messagebox.showwarning("Warning", "No declarations selected"))
                    return
                
                # Get declaration details
                declarations_to_redownload = []
                
                for item_id in selected_items:
                    values = self.declarations_tree.item(item_id, "values")
                    if values:
                        # Create Declaration object from stored data
                        decl_number = values[0]
                        tax_code = values[1]
                        date_str = values[2]
                        
                        # Parse date
                        try:
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        except:
                            date_obj = datetime.now()
                        
                        # Create minimal declaration object for re-download
                        declaration = Declaration(
                            declaration_number=decl_number,
                            tax_code=tax_code,
                            declaration_date=date_obj,
                            customs_office_code="",  # Will be retrieved from tracking DB if needed
                            transport_method="",
                            channel="",
                            status="T",
                            goods_description=None
                        )
                        declarations_to_redownload.append(declaration)
                
                if not declarations_to_redownload:
                    return
                
                self.append_log("INFO", f"Re-downloading {len(declarations_to_redownload)} declarations")
                
                # Disable button during execution
                self.root.after(0, lambda: self.redownload_button.config(state=tk.DISABLED))
                
                # Execute re-download
                result = self.scheduler.redownload_declarations(declarations_to_redownload)
                
                # Update statistics
                self.root.after(0, lambda: self.update_statistics(result))
                
                # Re-enable button
                self.root.after(0, lambda: self.redownload_button.config(state=tk.NORMAL))
                
                # Refresh declarations list
                self.root.after(0, self._load_processed_declarations)
                
                self.append_log("INFO", f"Re-download completed: {result.success_count} successful, {result.error_count} errors")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Re-download Complete",
                    f"Re-download completed:\n{result.success_count} successful\n{result.error_count} errors"
                ))
                
            except Exception as e:
                self.logger.error(f"Re-download failed: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Re-download failed:\n{str(e)}"))
                self.root.after(0, lambda: self.redownload_button.config(state=tk.NORMAL))
        
        # Run in background thread
        thread = threading.Thread(target=redownload_in_thread, daemon=True)
        thread.start()
    
    def open_file_location(self) -> None:
        """Open file location in file explorer"""
        try:
            # Get first selected item
            selected_items = self.declarations_tree.selection()
            
            if not selected_items:
                messagebox.showwarning("Warning", "No declaration selected")
                return
            
            # Get file path from tracking database
            item_id = selected_items[0]
            values = self.declarations_tree.item(item_id, "values")
            
            if values:
                decl_number = values[0]
                tax_code = values[1]
                
                # Try to get file path from tracking database first
                file_path = None
                try:
                    processed_list = self.tracking_db.get_all_processed()
                    for processed in processed_list:
                        if processed.declaration_number == decl_number and processed.tax_code == tax_code:
                            file_path = processed.file_path
                            break
                except Exception as e:
                    self.logger.warning(f"Could not get file path from tracking DB: {e}")
                
                # Fallback to constructing path from config if not found in DB
                if not file_path:
                    output_dir = self.config_manager.get_output_path()
                    file_path = os.path.join(output_dir, f"{tax_code}_{decl_number}.pdf")
                
                # Normalize path
                file_path = os.path.normpath(file_path)
                
                if os.path.exists(file_path):
                    # Open file location in explorer
                    if platform.system() == "Windows":
                        # Use os.startfile to open the folder, then select the file
                        folder_path = os.path.dirname(file_path)
                        subprocess.run(["explorer", "/select,", file_path])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", "-R", file_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", os.path.dirname(file_path)])
                    
                    self.logger.info(f"Opened file location: {file_path}")
                else:
                    # File not found, try to open the output directory instead
                    output_dir = self.config_manager.get_output_path()
                    if os.path.exists(output_dir):
                        if platform.system() == "Windows":
                            os.startfile(output_dir)
                        elif platform.system() == "Darwin":
                            subprocess.run(["open", output_dir])
                        else:
                            subprocess.run(["xdg-open", output_dir])
                        messagebox.showinfo("Thông báo", f"File không tồn tại:\n{file_path}\n\nĐã mở thư mục lưu file.")
                    else:
                        messagebox.showwarning("Warning", f"File not found:\n{file_path}")
                    
        except Exception as e:
            self.logger.error(f"Failed to open file location: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open file location:\n{str(e)}")
    
    # GUI Update Methods (Subtask 15.5)
    
    def update_statistics(self, result: WorkflowResult) -> None:
        """
        Update statistics display after workflow execution
        
        Args:
            result: WorkflowResult from workflow execution
        """
        # Update cumulative statistics
        self.total_processed += result.total_eligible
        self.total_success += result.success_count
        self.total_errors += result.error_count
        self.last_run_time = result.end_time or datetime.now()
        
        # Update labels
        self.processed_label.config(text=str(self.total_processed))
        self.success_label.config(text=str(self.total_success))
        self.errors_label.config(text=str(self.total_errors))
        
        if self.last_run_time:
            self.last_run_label.config(text=self.last_run_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    def _on_download_complete(self, success_count: int, error_count: int) -> None:
        """
        Callback when download completes from EnhancedManualPanel.
        
        Updates statistics display with download results using StatisticsBar.
        Shows desktop notification if enabled.
        
        Args:
            success_count: Number of successful downloads
            error_count: Number of failed downloads
            
        Requirements: 2.1, 2.5, 10.1, 10.2, 10.3, 10.4
        """
        # Update cumulative statistics
        self.total_processed += success_count + error_count
        self.total_success += success_count
        self.total_errors += error_count
        self.last_run_time = datetime.now()
        
        # Update StatisticsBar component
        self.statistics_bar.update_stats(
            processed=self.total_processed,
            retrieved=self.total_success,
            errors=self.total_errors,
            last_run=self.last_run_time
        )
        
        # Show desktop notification (Requirements 2.1, 2.5)
        if self.notification_manager:
            self.notification_manager.notify_batch_complete(success_count, error_count)
        
        self.logger.info(f"Statistics updated: processed={self.total_processed}, success={self.total_success}, errors={self.total_errors}")
    
    def _load_processed_declarations(self) -> None:
        """Load and display all processed declarations"""
        try:
            # Get all processed declarations from tracking database
            declarations = self.tracking_db.get_all_processed_details()
            
            # Populate tree view
            self._populate_declarations_tree(declarations)
            
            self.logger.debug(f"Loaded {len(declarations)} processed declarations")
            
        except Exception as e:
            self.logger.error(f"Failed to load processed declarations: {e}", exc_info=True)
            self.append_log("ERROR", f"Failed to load declarations: {str(e)}")
    
    def _populate_declarations_tree(self, declarations: List[ProcessedDeclaration]) -> None:
        """
        Populate tree view with declarations
        
        Args:
            declarations: List of ProcessedDeclaration objects
        """
        # Clear existing items
        for item in self.declarations_tree.get_children():
            self.declarations_tree.delete(item)
        
        # Add declarations with alternating row colors (Requirement 4.8)
        for index, decl in enumerate(declarations):
            # Format date
            try:
                date_obj = datetime.strptime(decl.declaration_date, "%Y%m%d")
                date_str = date_obj.strftime("%d/%m/%Y")
            except:
                date_str = decl.declaration_date
            
            # Format timestamp
            timestamp_str = decl.processed_at.strftime("%Y-%m-%d %H:%M:%S")
            
            # Determine row tag for alternating colors
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            # Insert into tree with alternating row tag
            self.declarations_tree.insert(
                "",
                tk.END,
                text="☐",
                values=(
                    decl.declaration_number,
                    decl.tax_code,
                    date_str,
                    timestamp_str
                ),
                tags=(row_tag,)
            )
    
    def _on_tree_hover(self, event) -> None:
        """Handle hover event on treeview for highlighting (Requirement 4.8)"""
        item = self.declarations_tree.identify_row(event.y)
        if item and item != self._hover_item:
            # Restore previous item's original tag
            if self._hover_item:
                self._restore_row_tag(self._hover_item)
            
            # Apply hover tag to current item
            self._hover_item = item
            current_tags = self.declarations_tree.item(item, 'tags')
            if current_tags and 'hover' not in current_tags:
                # Store original tag and apply hover
                self.declarations_tree.item(item, tags=('hover',))
    
    def _on_tree_leave(self, event) -> None:
        """Handle leave event on treeview to remove highlighting"""
        if self._hover_item:
            self._restore_row_tag(self._hover_item)
            self._hover_item = None
    
    def _restore_row_tag(self, item: str) -> None:
        """Restore the original alternating row tag for an item"""
        try:
            # Get item index to determine original tag
            children = self.declarations_tree.get_children()
            if item in children:
                index = children.index(item)
                original_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.declarations_tree.item(item, tags=(original_tag,))
        except (ValueError, tk.TclError):
            pass
    
    def append_log(self, level: str, message: str) -> None:
        """
        Log message to logger (Recent Logs panel removed per Requirements 9.1)
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
        """
        # Log to logger instead of removed log_text widget
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def _check_database_connection(self) -> None:
        """Check database connection status in background"""
        def check_in_thread():
            try:
                is_connected = self.ecus_connector.test_connection()
                
                if is_connected:
                    self.root.after(0, lambda: self.db_status_label.config(
                        text="● Connected", 
                        foreground=ModernStyles.SUCCESS_COLOR
                    ))
                    self.append_log("INFO", "Database connection successful")
                else:
                    # Try to connect
                    if self.ecus_connector.connect():
                        self.root.after(0, lambda: self.db_status_label.config(
                            text="● Connected", 
                            foreground=ModernStyles.SUCCESS_COLOR
                        ))
                        self.append_log("INFO", "Database connection established")
                    else:
                        self.root.after(0, lambda: self.db_status_label.config(
                            text="● Disconnected", 
                            foreground=ModernStyles.ERROR_COLOR
                        ))
                        self.append_log("ERROR", "Failed to connect to database")
                        
                        # Show desktop notification for database connection failure (Requirement 2.2)
                        if self.notification_manager:
                            self.root.after(0, lambda: 
                                self.notification_manager.notify_database_error("Không thể kết nối đến cơ sở dữ liệu"))
                        
            except Exception as e:
                self.logger.error(f"Database connection check failed: {e}", exc_info=True)
                self.root.after(0, lambda: self.db_status_label.config(
                    text="● Error", 
                    foreground=ModernStyles.ERROR_COLOR
                ))
                self.append_log("ERROR", f"Database connection error: {str(e)}")
                
                # Show desktop notification for database error (Requirement 2.2)
                if self.notification_manager:
                    self.root.after(0, lambda err=str(e): 
                        self.notification_manager.notify_database_error(err))
        
        thread = threading.Thread(target=check_in_thread, daemon=True)
        thread.start()
    
    def _update_db_status(self, is_connected: bool) -> None:
        """
        Update database connection status in GUI.
        
        Args:
            is_connected: True if connected, False otherwise
        """
        if is_connected:
            self.db_status_label.config(
                text="● Connected", 
                foreground=ModernStyles.SUCCESS_COLOR
            )
            self.append_log("INFO", "Database connection established")
        else:
            self.db_status_label.config(
                text="● Disconnected", 
                foreground=ModernStyles.ERROR_COLOR
            )
            self.append_log("WARNING", "Database disconnected")
    
    def get_statistics(self) -> dict:
        """
        Get current statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_processed": self.total_processed,
            "total_success": self.total_success,
            "total_errors": self.total_errors,
            "last_run_time": self.last_run_time
        }
    
    def _show_database_config_dialog(self) -> None:
        """Show database configuration dialog with profile support"""
        from models.config_models import DatabaseProfile
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Cấu hình Cơ sở dữ liệu")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog on parent window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame with padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get current config and profiles
        try:
            db_config = self.config_manager.get_database_config()
            current_server = db_config.server
            current_database = db_config.database
            current_username = db_config.username
            current_password = db_config.password
        except Exception:
            current_server = "Server"
            current_database = "ECUS5VNACCS"
            current_username = "sa"
            current_password = ""
        
        profiles = self.config_manager.get_database_profiles()
        profile_names = [p.name for p in profiles]
        active_profile = self.config_manager.get_active_profile_name()
        
        # Variables
        server_var = tk.StringVar(value=current_server)
        database_var = tk.StringVar(value=current_database)
        username_var = tk.StringVar(value=current_username)
        password_var = tk.StringVar(value=current_password)
        profile_var = tk.StringVar(value=active_profile if active_profile else "(Không có profile)")
        
        # ===== Profile Section =====
        profile_frame = ttk.LabelFrame(main_frame, text="Profile", padding=10)
        profile_frame.pack(fill=tk.X, pady=(0, 10))
        
        profile_row = ttk.Frame(profile_frame)
        profile_row.pack(fill=tk.X)
        
        ttk.Label(profile_row, text="Profile:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Profile dropdown
        profile_combo = ttk.Combobox(
            profile_row, 
            textvariable=profile_var,
            values=profile_names if profile_names else ["(Không có profile)"],
            state="readonly",
            width=25
        )
        profile_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        def on_profile_selected(event=None):
            """Load selected profile into form"""
            selected = profile_var.get()
            if selected and selected != "(Không có profile)":
                profile = self.config_manager.get_database_profile(selected)
                if profile:
                    server_var.set(profile.server)
                    database_var.set(profile.database)
                    username_var.set(profile.username)
                    password_var.set(profile.password)
                    status_label.config(text=f"Đã tải profile: {selected}", foreground=ModernStyles.INFO_COLOR)
        
        profile_combo.bind("<<ComboboxSelected>>", on_profile_selected)
        
        def save_new_profile():
            """Save current form as new profile"""
            # Ask for profile name
            name_dialog = tk.Toplevel(dialog)
            name_dialog.title("Lưu Profile Mới")
            name_dialog.geometry("300x120")
            name_dialog.transient(dialog)
            name_dialog.grab_set()
            
            # Center
            name_dialog.update_idletasks()
            nx = dialog.winfo_x() + (dialog.winfo_width() - name_dialog.winfo_width()) // 2
            ny = dialog.winfo_y() + (dialog.winfo_height() - name_dialog.winfo_height()) // 2
            name_dialog.geometry(f"+{nx}+{ny}")
            
            name_frame = ttk.Frame(name_dialog, padding=15)
            name_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(name_frame, text="Tên profile:").pack(anchor=tk.W)
            name_var = tk.StringVar()
            name_entry = ttk.Entry(name_frame, textvariable=name_var, width=35)
            name_entry.pack(fill=tk.X, pady=5)
            name_entry.focus_set()
            
            def do_save():
                name = name_var.get().strip()
                if not name:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên profile!")
                    return
                
                # Create and save profile
                profile = DatabaseProfile(
                    name=name,
                    server=server_var.get().strip(),
                    database=database_var.get().strip(),
                    username=username_var.get().strip(),
                    password=password_var.get()
                )
                self.config_manager.save_database_profile(profile)
                
                # Update dropdown
                profiles = self.config_manager.get_database_profiles()
                profile_names = [p.name for p in profiles]
                profile_combo['values'] = profile_names
                profile_var.set(name)
                
                status_label.config(text=f"Đã lưu profile: {name}", foreground=ModernStyles.SUCCESS_COLOR)
                name_dialog.destroy()
            
            btn_frame = ttk.Frame(name_frame)
            btn_frame.pack(fill=tk.X, pady=(10, 0))
            ttk.Button(btn_frame, text="Lưu", command=do_save, width=10).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Hủy", command=name_dialog.destroy, width=10).pack(side=tk.LEFT)
            
            name_entry.bind("<Return>", lambda e: do_save())
        
        def delete_profile():
            """Delete selected profile"""
            selected = profile_var.get()
            if not selected or selected == "(Không có profile)":
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn profile để xóa!")
                return
            
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa profile '{selected}'?"):
                self.config_manager.delete_database_profile(selected)
                
                # Update dropdown
                profiles = self.config_manager.get_database_profiles()
                profile_names = [p.name for p in profiles]
                profile_combo['values'] = profile_names if profile_names else ["(Không có profile)"]
                profile_var.set(profile_names[0] if profile_names else "(Không có profile)")
                
                status_label.config(text=f"Đã xóa profile: {selected}", foreground=ModernStyles.INFO_COLOR)
        
        # Profile buttons
        ttk.Button(profile_row, text="Lưu mới", command=save_new_profile, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(profile_row, text="Xóa", command=delete_profile, width=8).pack(side=tk.LEFT, padx=2)
        
        # ===== Connection Details Section =====
        details_frame = ttk.LabelFrame(main_frame, text="Thông tin kết nối", padding=10)
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server
        row0 = ttk.Frame(details_frame)
        row0.pack(fill=tk.X, pady=3)
        ttk.Label(row0, text="Server:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row0, textvariable=server_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Database
        row1 = ttk.Frame(details_frame)
        row1.pack(fill=tk.X, pady=3)
        ttk.Label(row1, text="Cơ sở dữ liệu:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=database_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Username
        row2 = ttk.Frame(details_frame)
        row2.pack(fill=tk.X, pady=3)
        ttk.Label(row2, text="Tài khoản:", width=12).pack(side=tk.LEFT)
        ttk.Entry(row2, textvariable=username_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Password
        row3 = ttk.Frame(details_frame)
        row3.pack(fill=tk.X, pady=3)
        ttk.Label(row3, text="Mật khẩu:", width=12).pack(side=tk.LEFT)
        password_entry = ttk.Entry(row3, textvariable=password_var, width=40, show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Show/Hide password
        show_password_var = tk.BooleanVar(value=False)
        def toggle_password():
            password_entry.config(show="" if show_password_var.get() else "*")
        
        ttk.Checkbutton(
            details_frame, 
            text="Hiện mật khẩu", 
            variable=show_password_var,
            command=toggle_password
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Status label
        status_label = ttk.Label(main_frame, text="", foreground=ModernStyles.INFO_COLOR)
        status_label.pack(fill=tk.X, pady=5)
        
        # ===== Action Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def test_connection():
            """Test database connection with current settings"""
            status_label.config(text="Đang kiểm tra kết nối...", foreground=ModernStyles.INFO_COLOR)
            dialog.update()
            
            try:
                import pyodbc
                server = server_var.get().strip()
                database = database_var.get().strip()
                username = username_var.get().strip()
                password = password_var.get()
                
                connection_string = (
                    f"DRIVER={{SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"UID={username};"
                    f"PWD={password};"
                    f"Connection Timeout=10"
                )
                
                conn = pyodbc.connect(connection_string, timeout=10)
                conn.close()
                
                status_label.config(text="✓ Kết nối thành công!", foreground=ModernStyles.SUCCESS_COLOR)
                
            except Exception as e:
                status_label.config(text=f"✗ Lỗi: {str(e)[:50]}...", foreground=ModernStyles.ERROR_COLOR)
        
        def save_and_reconnect():
            """Save database configuration and reconnect immediately"""
            try:
                server = server_var.get().strip()
                database = database_var.get().strip()
                username = username_var.get().strip()
                password = password_var.get()
                
                if not all([server, database, username]):
                    messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
                    return
                
                # Save to Database section
                self.config_manager.set_database_config(server, database, username, password)
                
                # Update active profile if one is selected
                selected_profile = profile_var.get()
                if selected_profile and selected_profile != "(Không có profile)":
                    # Update the profile with new values
                    profile = DatabaseProfile(
                        name=selected_profile,
                        server=server,
                        database=database,
                        username=username,
                        password=password
                    )
                    self.config_manager.save_database_profile(profile)
                    self.config_manager.config.set('Database', 'active_profile', selected_profile)
                    self.config_manager._save_config_file()
                
                # Try to reconnect with new settings
                status_label.config(text="Đang kết nối lại...", foreground=ModernStyles.INFO_COLOR)
                dialog.update()
                
                try:
                    # Disconnect current connection if any
                    if self.ecus_connector:
                        self.ecus_connector.disconnect()
                    
                    # Update connector with new config
                    new_db_config = self.config_manager.get_database_config()
                    self.ecus_connector.config = new_db_config
                    
                    # Try to connect
                    if self.ecus_connector.connect():
                        self.logger.info("Database reconnected successfully with new configuration")
                        self._update_db_status(True)
                        messagebox.showinfo("Thành công", "Đã lưu cấu hình và kết nối lại thành công!")
                        dialog.destroy()
                    else:
                        self._update_db_status(False)
                        status_label.config(text="✗ Lưu thành công nhưng kết nối thất bại", foreground=ModernStyles.ERROR_COLOR)
                        messagebox.showwarning("Cảnh báo", "Đã lưu cấu hình nhưng không thể kết nối.\nVui lòng kiểm tra lại thông tin kết nối.")
                        
                except Exception as conn_error:
                    self._update_db_status(False)
                    self.logger.error(f"Failed to reconnect: {conn_error}")
                    status_label.config(text=f"✗ Lỗi kết nối: {str(conn_error)[:40]}...", foreground=ModernStyles.ERROR_COLOR)
                    messagebox.showwarning("Cảnh báo", f"Đã lưu cấu hình nhưng không thể kết nối:\n{str(conn_error)}")
                
            except Exception as e:
                self.logger.error(f"Failed to save database config: {e}")
                messagebox.showerror("Lỗi", f"Không thể lưu cấu hình:\n{str(e)}")
        
        # Buttons
        ttk.Button(button_frame, text="Kiểm tra kết nối", command=test_connection, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Lưu & Kết nối", command=save_and_reconnect, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Đóng", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def _show_settings_dialog(self) -> None:
        """
        Show settings dialog for configuring retrieval method, PDF naming, and theme.
        
        Implements Requirements 1.1, 5.1, 7.1, 7.5, 7.6
        """
        def on_settings_changed(retrieval_method: str, pdf_naming_format: str):
            """Callback when settings are saved - update BarcodeRetriever immediately"""
            # Update BarcodeRetriever's retrieval method
            if self.barcode_retriever:
                self.barcode_retriever.set_retrieval_method(retrieval_method)
                self.logger.info(f"BarcodeRetriever updated with new retrieval method: {retrieval_method}")
            
            # Update FileManager's PDF naming service
            if self.file_manager:
                from file_utils.pdf_naming_service import PdfNamingService
                self.file_manager.pdf_naming_service = PdfNamingService(pdf_naming_format)
                self.logger.info(f"FileManager updated with new PDF naming format: {pdf_naming_format}")
        
        SettingsDialog(
            self.root, 
            self.config_manager, 
            on_settings_changed=on_settings_changed,
            theme_manager=self.theme_manager
        )
