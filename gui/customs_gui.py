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
from gui.two_column_layout import TwoColumnLayout
from gui.compact_status_bar import CompactStatusBar
from gui.compact_output_section import CompactOutputSection
from gui.compact_company_section import CompactCompanySection
from gui.preview_panel import PreviewPanel
from gui.tracking_panel import TrackingPanel
# v2.0: Extracted GUI components
from gui.dialogs.about_dialog import show_about_dialog
from gui.components.header_banner import HeaderBanner
from gui.components.footer import Footer
from gui.controllers.updater_controller import UpdaterController
from gui.controllers.file_operations_controller import FileOperationsController
from gui.layout_builders import create_left_pane_content, create_right_pane_content
from gui.branding import (
    APP_VERSION, APP_NAME, APP_FULL_NAME, WINDOW_TITLE,
    COMPANY_NAME, COMPANY_SLOGAN, COMPANY_MOTTO,
    DESIGNER_NAME_HEADER, DESIGNER_NAME, DESIGNER_EMAIL, DESIGNER_PHONE, LOGO_FILE,
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
        
        # Setup window with responsive layout (Requirements 1.4, 9.3)
        self.root.title(WINDOW_TITLE)
        self.root.minsize(1000, 700)  # Minimum size for two-column layout
        
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
        
        # Create GUI components (Two-column layout - Requirements 1.1)
        self._create_header_banner()
        self._create_two_column_layout()  # New two-column layout
        self._create_footer()
        
        # Load initial data
        self._load_processed_declarations()
        
        # Initialize ClearanceChecker (Phase 4)
        from gui.clearance_checker import ClearanceChecker
        from config.user_preferences import get_preferences
        prefs = get_preferences()
        
        self.clearance_checker = ClearanceChecker(
            tracking_db=self.tracking_db,
            ecus_connector=self.ecus_connector,
            notification_manager=self.notification_manager,
            logger=self.logger
        )
        
        # Configure and start if enabled
        self.clearance_checker.set_config(prefs.auto_check_enabled, prefs.auto_check_interval)
        if prefs.auto_check_enabled:
            self.clearance_checker.start()
            
        # Register callback to refresh TrackingPanel (will work since method uses self.tracking_panel)
        self.clearance_checker.on_status_changed = self._on_clearance_status_changed
        
        # Apply saved theme after all GUI components are created (Requirements 7.5)
        # Always apply the saved theme to ensure consistent styling
        saved_theme = self.config_manager.get_theme()
        self.theme_manager.apply_theme(saved_theme)
        
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
            # Stop ClearanceChecker
            if hasattr(self, 'clearance_checker'):
                self.clearance_checker.stop()
                
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
        """Create header banner - v2.0: Uses extracted HeaderBanner component."""
        self._header = HeaderBanner(
            parent=self.root,
            logger=self.logger,
            on_about_click=self._show_about_dialog,
            on_update_click=self._check_for_updates
        )
    
    def _create_footer(self) -> None:
        """Create footer - v2.0: Uses extracted Footer component."""
        self._footer = Footer(self.root)
    
    def _check_for_updates(self) -> None:
        """Check for updates - v2.0: Uses extracted UpdaterController."""
        if not hasattr(self, '_updater_controller'):
            self._updater_controller = UpdaterController(
                root=self.root,
                config_manager=self.config_manager,
                logger=self.logger
            )
        self._updater_controller.check_for_updates()
    
    def _show_about_dialog(self) -> None:
        """Show About dialog - v2.0: Uses extracted component."""
        show_about_dialog(self.root)
    
    def _create_two_column_layout(self) -> None:
        """
        Create two-column layout with Control Panel on left and Preview Panel on right.
        
        Requirements: 1.1, 1.2, 1.4, 8.1, 8.2
        """
        # Create TwoColumnLayout container
        self.two_column_layout = TwoColumnLayout(
            self.root,
            config_manager=self.config_manager
        )
        self.two_column_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Get pane references
        left_pane = self.two_column_layout.get_left_pane()
        right_pane = self.two_column_layout.get_right_pane()
        
        # === LEFT PANE: Control Panel ===
        self._create_left_pane_content(left_pane)
        
        # === RIGHT PANE: Preview Panel ===
        self._create_right_pane_content(right_pane)
        
        # Check database connection in background
        self._check_database_connection()
        
        # Set scheduler to Manual mode by default
        self.scheduler.set_operation_mode(OperationMode.MANUAL)
        
        # Keep output_path_var for compatibility
        self.output_path_var = tk.StringVar(value=self.config_manager.get_output_path())
    
    def _create_left_pane_content(self, parent: ttk.Frame) -> None:
        """
        Create left pane content - Control Panel with compact layout.
        
        Layout:
        - Compact Status Bar (status + DB status + buttons)
        - Statistics Bar
        - EnhancedManualPanel (without preview table - moved to right pane)
        
        Requirements: 2.1, 3.1, 4.1
        """
        # Compact Status Bar (40px) - Requirements 2.1, 2.2, 2.3, 2.4
        self.compact_status_bar = CompactStatusBar(parent)
        self.compact_status_bar.pack(fill=tk.X, pady=(0, 5))
        self.compact_status_bar.set_db_config_command(self._show_database_config_dialog)
        self.compact_status_bar.set_settings_command(self._show_settings_dialog)
        
        # Keep references for backward compatibility
        self.status_label = self.compact_status_bar.status_indicator
        self.db_status_label = self.compact_status_bar.db_indicator
        
        # Statistics bar
        self.statistics_bar = StatisticsBar(parent)
        self.statistics_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Keep references for backward compatibility
        self.processed_label = self.statistics_bar.processed_label
        self.success_label = self.statistics_bar.retrieved_label
        self.errors_label = self.statistics_bar.errors_label
        self.last_run_label = self.statistics_bar.last_run_label
        
        # Initialize CompanyScanner and PreviewManager
        self.company_scanner = CompanyScanner(
            ecus_connector=self.ecus_connector,
            tracking_db=self.tracking_db,
            logger=self.logger
        )
        
        self.preview_manager = PreviewManager(
            ecus_connector=self.ecus_connector,
            logger=self.logger
        )
        
        # Enhanced Manual Panel - contains output dir, company selection, date range
        # Preview table will be hidden and moved to right pane
        self.enhanced_manual_panel = EnhancedManualPanel(
            parent=parent,
            company_scanner=self.company_scanner,
            preview_manager=self.preview_manager,
            logger=self.logger,
            barcode_retriever=self.barcode_retriever,
            file_manager=self.file_manager,
            tracking_db=self.tracking_db,
            on_download_complete=self._on_download_complete,
            hide_preview_section=True  # Hide preview table - moved to right pane
        )
        self.enhanced_manual_panel.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def _create_right_pane_content(self, parent: ttk.Frame) -> None:
        """
        Create right pane content with tabbed interface (v1.5.0).
        
        Tabs:
        - Preview Panel (Xem trước tờ khai)
        - Tracking Panel (Theo dõi thông quan)
        
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        # v1.5.0: Create notebook for tabs
        self.right_notebook = ttk.Notebook(parent)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Preview Panel
        preview_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(preview_tab, text="📋 Xem trước tờ khai")
        
        self.preview_panel = PreviewPanel(
            preview_tab,
            on_preview=self._on_preview_click,
            on_download=self._on_download_click,
            on_cancel=self._on_cancel_click,
            on_stop=self._on_stop_click,
            on_export_log=self._on_export_log_click,
            on_select_all=self._on_select_all_change,
            on_retry_failed=self._on_retry_failed_click,
            on_check_clearance=self._on_check_clearance_click,
            on_include_pending_changed=self._on_include_pending_changed,
            on_exclude_xnktc_changed=self._on_exclude_xnktc_changed
        )
        self.preview_panel.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Tracking Panel (v1.5.0)
        tracking_tab = ttk.Frame(self.right_notebook)
        self.right_notebook.add(tracking_tab, text="🔍 Theo dõi thông quan")
        
        # Initialize TrackingPanel
        self.tracking_panel = TrackingPanel(
            tracking_tab,
            tracking_db=self.tracking_db,
            on_get_barcode=self._on_download_tracking_declarations,
            on_check_now=self._on_manual_check_clearance,
            on_stop=self._on_stop_tracking_check,
            on_settings=self._show_settings_dialog
        )
        self.tracking_panel.pack(fill=tk.BOTH, expand=True)
        
        # Start countdown timer if auto check is enabled
        from config.user_preferences import get_preferences
        prefs = get_preferences()
        if prefs.auto_check_enabled:
            self.tracking_panel.start_countdown(prefs.auto_check_interval)
        

        
        # Connect EnhancedManualPanel to PreviewPanel for two-column layout
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.set_external_preview_panel(self.preview_panel)
            
            # v1.5.0: Connect callbacks (Added in Phase 6)
            self.preview_panel.on_check_clearance = self._on_check_clearance_click
            self.preview_panel.on_add_to_tracking = self._on_add_to_tracking_click
    
    def _on_output_path_changed(self, path: str) -> None:
        """Handle output path change from CompactOutputSection."""
        self.config_manager.set_output_path(path)
        self.config_manager.save()
        self.output_path_var.set(path)
        self.logger.info(f"Output directory changed to: {path}")
    
    def _on_company_selected(self, tax_code: str) -> None:
        """Handle company selection from CompactCompanySection."""
        self.logger.info(f"Company selected: {tax_code}")
        # Sync with EnhancedManualPanel if needed
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.company_combo.set(tax_code)
    
    def _on_scan_companies(self) -> None:
        """Handle scan companies button click."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel._scan_companies()
    
    def _on_refresh_companies(self) -> None:
        """Handle refresh companies button click."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel._refresh_companies()
    
    def _on_preview_click(self) -> None:
        """Handle preview button click from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.preview_declarations()
    
    def _on_download_click(self) -> None:
        """Handle download button click from PreviewPanel - uses same mechanism as tracking panel."""
        if not hasattr(self, 'preview_panel'):
            return
        
        from tkinter import messagebox
        
        # Get selected declarations from preview panel
        selected = self.preview_panel.get_selected_declarations_data()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tờ khai để lấy mã vạch.")
            return
        
        # Use the same mechanism as tracking panel - call enhanced_manual_panel.download_specific_declarations
        if hasattr(self, 'enhanced_manual_panel'):
            # Convert to format expected by panel - include all required fields
            declarations = []
            for decl in selected:
                declarations.append({
                    'tax_code': decl.get('tax_code', ''),
                    'declaration_number': decl.get('declaration_number', ''),
                    'date': decl.get('declaration_date') or decl.get('date', None),
                    'customs_code': decl.get('customs_code') or decl.get('customs_office_code', ''),
                    'company_name': decl.get('company_name', '')
                })
            self.enhanced_manual_panel.download_specific_declarations(declarations)
        else:
            messagebox.showerror("Lỗi", "Enhanced manual panel chưa được khởi tạo.")
    
    def _on_cancel_click(self) -> None:
        """Handle cancel button click from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.cancel_operation()
    
    def _on_stop_click(self) -> None:
        """Handle stop button click from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.stop_download()
    
    def _on_export_log_click(self) -> None:
        """Handle export log button click from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.export_error_log()
    
    def _on_select_all_change(self, select_all: bool) -> None:
        """Handle select all checkbox change from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.toggle_select_all()
    
    def _on_retry_failed_click(self) -> None:
        """Handle retry failed button click from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            self.enhanced_manual_panel.retry_failed_downloads()
    
    def _on_include_pending_changed(self, include_pending: bool) -> None:
        """Handle include pending checkbox change from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            # Sync the checkbox value to EnhancedManualPanel
            self.enhanced_manual_panel.include_pending_var.set(include_pending)
            # Trigger preview refresh if data exists
            if self.enhanced_manual_panel.preview_manager._all_declarations:
                self.enhanced_manual_panel.preview_declarations()
    
    def _on_exclude_xnktc_changed(self, exclude_xnktc: bool) -> None:
        """Handle exclude XNK TC checkbox change from PreviewPanel."""
        if hasattr(self, 'enhanced_manual_panel'):
            # Sync the checkbox value to EnhancedManualPanel
            self.enhanced_manual_panel.exclude_xnktc_var.set(exclude_xnktc)
            # Trigger preview refresh if data exists
            if self.enhanced_manual_panel.preview_manager._all_declarations:
                self.enhanced_manual_panel.preview_declarations()
    
    def _on_check_clearance_click(self) -> None:
        """Check clearance - v2.0: Uses simplified inline check."""
        if not hasattr(self, 'preview_panel'):
            return
        selected = self.preview_panel.get_selected_declarations_data()
        if not selected:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tờ khai.")
            return
        def check():
            for d in selected:
                try:
                    status = self.ecus_connector.check_declarations_status(d['tax_code'], d['declaration_number'])
                    if status:
                        self.root.after(0, lambda dn=d['declaration_number'], s=status: self.preview_panel.update_item_status(dn, s))
                except Exception as e:
                    self.logger.error(f"Check failed: {e}")
            self.root.after(0, lambda: __import__('tkinter').messagebox.showinfo("Hoàn tất", "Đã kiểm tra xong."))
        import threading
        threading.Thread(target=check, daemon=True).start()
    
    def _on_add_to_tracking_click(self) -> None:
        """Add to tracking - v2.0: Uses TrackingController."""
        from gui.controllers.tracking_controller import TrackingController
        if not hasattr(self, '_tracking_controller'):
            self._tracking_controller = TrackingController(
                tracking_db=self.tracking_db,
                logger=self.logger,
                root=self.root
            )
        if hasattr(self, 'preview_panel'):
            selected = self.preview_panel.get_selected_declarations_data()
            tracking_panel = getattr(self, 'tracking_panel', None)
            self._tracking_controller.add_to_tracking(selected, tracking_panel)
    
    def _on_download_tracking_declarations(self, declarations: List[dict]) -> None:
        """Download tracking declarations - v2.0: Uses TrackingController."""
        from gui.controllers.tracking_controller import TrackingController
        if not hasattr(self, '_tracking_controller'):
            self._tracking_controller = TrackingController(
                tracking_db=self.tracking_db,
                logger=self.logger,
                root=self.root
            )
        panel = getattr(self, 'enhanced_manual_panel', None)
        self._tracking_controller.download_tracking_declarations(declarations, panel)
    
    def _on_manual_check_clearance(self):
        """Manual trigger for clearance check service."""
        if not hasattr(self, 'clearance_checker'):
             messagebox.showinfo("Thông báo", "Dịch vụ tự động kiểm tra chưa được khởi tạo.")
             return
             
        # Disable button? (Ideally we have a handle to the button or manage state)
        if hasattr(self, 'tracking_panel'):
            # self.tracking_panel.check_now_btn.config(state=tk.DISABLED)
            # self.tracking_panel.stop_btn.config(state=tk.NORMAL)
            pass
            
        def run_check():
            try:
                if hasattr(self, 'tracking_panel'):
                   self.root.after(0, self.tracking_panel.enable_stop_btn)
                   
                count = self.clearance_checker.check_now()
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Hoàn tất kiểm tra", 
                    f"Đã kiểm tra xong.\nSố tờ khai thông quan mới: {count}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi kiểm tra: {e}"))
            finally:
                if hasattr(self, 'tracking_panel'):
                   self.root.after(0, self.tracking_panel.disable_stop_btn)
        
        threading.Thread(target=run_check, daemon=True).start()
            
    def _on_stop_tracking_check(self):
        """Stop current check."""
        if hasattr(self, 'clearance_checker'):
            self.clearance_checker.stop_current_check()

    def _on_get_barcode(self, tax_code: str, date: datetime) -> None:
        """Legacy handler, kept for compatibility if needed."""
        pass
        
    def _on_clearance_status_changed(self):
        """Callback when clearance status updates."""
        if hasattr(self, 'tracking_panel'):
            # Schedule update on main thread
            self.root.after(0, self.tracking_panel.refresh)
    
    def _show_database_config_dialog(self) -> None:
        """Show database config - v2.0: Uses extracted DatabaseConfigDialog."""
        from gui.dialogs.database_config_dialog import show_database_config_dialog
        show_database_config_dialog(
            parent=self.root,
            config_manager=self.config_manager,
            ecus_connector=self.ecus_connector,
            logger=self.logger,
            on_reconnect=self._check_database_connection
        )
    
    def _show_settings_dialog(self) -> None:
        """Show settings dialog - v2.0: Uses extracted SettingsDialog."""
        from gui.settings_dialog import SettingsDialog
        
        def on_settings_changed(retrieval_method: str, pdf_naming_format: str):
            """Callback when settings are saved."""
            if hasattr(self, 'barcode_retriever') and self.barcode_retriever:
                self.barcode_retriever.set_retrieval_method(retrieval_method)
            if hasattr(self, 'file_manager') and self.file_manager:
                self.file_manager.set_naming_format(pdf_naming_format)
            self.logger.info(f"Settings updated: method={retrieval_method}, format={pdf_naming_format}")
        
        def on_auto_check_changed(enabled: bool, interval: int):
            """Callback when auto-check settings change."""
            print(f"DEBUG [customs_gui] on_auto_check_changed called: enabled={enabled}, interval={interval}")
            
            # Update tracking panel status label
            print(f"DEBUG [customs_gui] hasattr tracking_panel: {hasattr(self, 'tracking_panel')}")
            print(f"DEBUG [customs_gui] tracking_panel: {self.tracking_panel if hasattr(self, 'tracking_panel') else 'N/A'}")
            
            if hasattr(self, 'tracking_panel') and self.tracking_panel:
                print(f"DEBUG [customs_gui] Calling tracking_panel.update_auto_status({enabled})...")
                self.tracking_panel.update_auto_status(enabled)
                print(f"DEBUG [customs_gui] update_auto_status completed")
                
                if enabled:
                    # Start/restart countdown and clearance checker
                    self.tracking_panel.start_countdown(interval)
                    if hasattr(self, 'clearance_checker') and self.clearance_checker:
                        self.clearance_checker.set_config(enabled, interval)
                        self.clearance_checker.start()
                else:
                    # Stop countdown and clearance checker
                    self.tracking_panel.stop_countdown()
                    if hasattr(self, 'clearance_checker') and self.clearance_checker:
                        self.clearance_checker.stop()
            else:
                print("DEBUG [customs_gui] WARNING: tracking_panel not found!")
                        
            self.logger.info(f"Auto-check settings updated: enabled={enabled}, interval={interval}min")
        
        dialog = SettingsDialog(
            self.root,
            self.config_manager,
            on_settings_changed=on_settings_changed,
            theme_manager=self.theme_manager,
            on_auto_check_changed=on_auto_check_changed
        )
    
    def _on_download_complete(self, success_count: int, error_count: int) -> None:
        """
        Callback when download completes from EnhancedManualPanel.
        
        Args:
            success_count: Number of successful downloads
            error_count: Number of failed downloads
        """
        # Update statistics bar
        if hasattr(self, 'statistics_bar'):
            self.statistics_bar.update_counts(
                processed=success_count + error_count,
                retrieved=success_count,
                errors=error_count
            )
        
        # Update compact status bar  
        if hasattr(self, 'compact_status_bar'):
            status = "Ready" if error_count == 0 else f"{error_count} errors"
            self.compact_status_bar.set_status(status)
        
        # Show desktop notification
        if hasattr(self, 'notification_manager') and self.notification_manager:
            self.notification_manager.notify_download_complete(success_count, error_count)
        
        self.logger.info(f"Download completed: {success_count} success, {error_count} errors")
    
    def _check_database_connection(self) -> None:
        """Check database connection status in background."""
        def check_in_thread():
            try:
                is_connected = self.ecus_connector.test_connection()
                if not is_connected:
                    is_connected = self.ecus_connector.connect()
                self.root.after(0, lambda: self._update_db_status(is_connected))
            except Exception as e:
                self.logger.error(f"Database connection check failed: {e}")
                self.root.after(0, lambda: self._update_db_status(False))
        import threading
        threading.Thread(target=check_in_thread, daemon=True).start()
    
    def _update_db_status(self, is_connected: bool) -> None:
        """Update database connection status in GUI."""
        if is_connected:
            if hasattr(self, 'db_status_label'):
                self.db_status_label.config(text="● Connected", foreground=ModernStyles.SUCCESS_COLOR)
            self.append_log("INFO", "Database connection successful")
        else:
            if hasattr(self, 'db_status_label'):
                self.db_status_label.config(text="● Disconnected", foreground=ModernStyles.ERROR_COLOR)
            self.append_log("ERROR", "Database connection failed")
            if hasattr(self, 'notification_manager') and self.notification_manager:
                self.notification_manager.notify_database_error("Không thể kết nối đến CSDL")
    
    def _on_clearance_status_changed(self) -> None:
        """
        Callback called by ClearanceChecker when status changes.
        Schedules tracking panel refresh on main thread.
        """
        try:
            # Schedule refresh on main thread since this is called from background thread
            self.root.after(0, self._refresh_tracking_panel)
        except Exception as e:
            self.logger.error(f"Error scheduling tracking panel refresh: {e}")
    
    def _refresh_tracking_panel(self) -> None:
        """Refresh tracking panel from main thread and reset countdown timer."""
        try:
            self.logger.info("_refresh_tracking_panel called - refreshing UI and resetting countdown")
            
            if hasattr(self, 'tracking_panel') and self.tracking_panel:
                self.tracking_panel.refresh()
                self.logger.info("Tracking panel refreshed after clearance check")
                
                # Reset countdown timer if auto check is enabled
                from config.user_preferences import get_preferences
                prefs = get_preferences()
                if prefs.auto_check_enabled:
                    self.tracking_panel.reset_countdown(prefs.auto_check_interval)
                    self.logger.info(f"Countdown timer reset to {prefs.auto_check_interval} minutes")
        except Exception as e:
            self.logger.error(f"Error refreshing tracking panel: {e}")
    
    def update_statistics(self, result) -> None:
        """Update statistics display after workflow execution."""
        if hasattr(self, 'statistics_bar'):
            self.statistics_bar.update_counts(
                processed=result.total_processed if hasattr(result, 'total_processed') else result.success_count + result.error_count,
                retrieved=result.success_count,
                errors=result.error_count
            )
        self.total_processed += result.success_count + result.error_count
        self.total_success += result.success_count
        self.total_errors += result.error_count
        self.last_run_time = datetime.now()
    
    def append_log(self, level: str, message: str) -> None:
        """Log message to logger."""
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
    
    def _load_processed_declarations(self) -> None:
        """Load and display all processed declarations."""
        try:
            declarations = self.tracking_db.get_all_processed_declarations()
            self._populate_declarations_tree(declarations)
        except Exception as e:
            self.logger.error(f"Failed to load processed declarations: {e}")
    
    def _populate_declarations_tree(self, declarations) -> None:
        """Populate tree view with declarations."""
        if not hasattr(self, 'declarations_tree'):
            return
        # Clear existing items
        for item in self.declarations_tree.get_children():
            self.declarations_tree.delete(item)
        # Add declarations
        for i, decl in enumerate(declarations):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.declarations_tree.insert('', 'end', values=(
                decl.declaration_number if hasattr(decl, 'declaration_number') else decl.get('declaration_number', ''),
                decl.tax_code if hasattr(decl, 'tax_code') else decl.get('tax_code', ''),
                decl.declaration_date.strftime('%d/%m/%Y') if hasattr(decl, 'declaration_date') and decl.declaration_date else '',
                decl.processed_at.strftime('%d/%m/%Y %H:%M') if hasattr(decl, 'processed_at') and decl.processed_at else ''
            ), tags=(tag,))
    
    def search_declarations(self) -> None:
        """Search declarations based on search_var."""
        if not hasattr(self, 'search_var'):
            return
        query = self.search_var.get().strip()
        if not query:
            self._load_processed_declarations()
            return
        try:
            results = self.tracking_db.search_declarations(query)
            self._populate_declarations_tree(results)
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
    
    def get_statistics(self) -> dict:
        """Get current statistics."""
        return {
            "total_processed": self.total_processed,
            "total_success": self.total_success,
            "total_errors": self.total_errors,
            "last_run_time": self.last_run_time
        }
    
    def _on_download_tracking_declarations(self, declarations: list) -> None:
        """Handle 'Get Barcode' from Tracking Panel - trigger download for passed declarations."""
        if not declarations:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Không có tờ khai để tải mã vạch.")
            return
        
        self.logger.info(f"Downloading barcodes for {len(declarations)} tracking declarations...")
        
        # Use EnhancedManualPanel to download
        if hasattr(self, 'enhanced_manual_panel') and self.enhanced_manual_panel:
            # Convert tracking format to download format
            for decl in declarations:
                if 'decl_number' in decl and 'declaration_number' not in decl:
                    decl['declaration_number'] = decl['decl_number']
            self.enhanced_manual_panel.download_specific_declarations(declarations)
        else:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", "Không thể tải mã vạch - panel không sẵn sàng.")
    
    def _on_add_to_tracking_click(self) -> None:
        """Handle 'Add to Tracking' from Preview Panel - add selected declarations."""
        if not hasattr(self, 'preview_panel'):
            return
        
        selected = self.preview_panel.get_selected_declarations_data()
        if not selected:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tờ khai để thêm vào theo dõi.")
            return
        
        added_count = 0
        for decl in selected:
            try:
                decl_number = decl.get('declaration_number') or decl.get('decl_number')
                tax_code = decl.get('tax_code')
                decl_date = decl.get('date') or decl.get('declaration_date')
                company_name = decl.get('company_name', '')  # Issue 4.1b: Include company name
                customs_code = decl.get('customs_office_code') or decl.get('customs_code', '')
                
                if isinstance(decl_date, str):
                    try:
                        decl_date = datetime.strptime(decl_date, "%d/%m/%Y")
                    except:
                        try:
                            decl_date = datetime.strptime(decl_date, "%Y-%m-%d")
                        except:
                            decl_date = datetime.now()
                
                # Add to tracking with company name
                self.tracking_db.add_to_tracking(
                    declaration_number=decl_number,
                    tax_code=tax_code,
                    declaration_date=decl_date,
                    company_name=company_name,
                    customs_code=customs_code
                )
                added_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to add {decl.get('declaration_number')}: {e}")
        
        # Refresh tracking panel
        if hasattr(self, 'tracking_panel'):
            self.tracking_panel.refresh()
        
        from tkinter import messagebox
        messagebox.showinfo("Hoàn tất", f"Đã thêm {added_count}/{len(selected)} tờ khai vào danh sách theo dõi.")
    
    def _on_check_clearance_click(self) -> None:
        """Handle 'Check Clearance' from Preview Panel - removed, redirect to tracking tab."""
        # Issue 3: This button is being removed, but keep method for safety
        from tkinter import messagebox
        messagebox.showinfo("Thông báo", "Vui lòng dùng tab 'Theo dõi thông quan' để kiểm tra trạng thái.")
    
    def _on_manual_check_clearance(self, ids: list = None) -> None:
        """Handle 'Check Now' from Tracking Panel - trigger immediate clearance check."""
        if hasattr(self, 'clearance_checker') and self.clearance_checker:
            def run_check():
                try:
                    # Show progress bar
                    if hasattr(self, 'tracking_panel'):
                        self.root.after(0, self.tracking_panel.show_progress)
                        self.root.after(0, self.tracking_panel.enable_stop_btn)
                    
                    # Get pending count for progress
                    pending_ids = ids if ids else []
                    if not pending_ids and hasattr(self, 'tracking_db'):
                        try:
                            pending_items = self.tracking_db.get_all_tracking()
                            pending_ids = [d.id for d in pending_items if d.status.value == 'pending']
                        except:
                            pass
                    
                    total = len(pending_ids) if pending_ids else 1
                    
                    # Progress callback for real-time updates
                    def on_progress(current, checked_count, decl_id=None, new_status=None, last_checked=None, cleared_at=None):
                        if hasattr(self, 'tracking_panel'):
                            self.root.after(0, lambda: self.tracking_panel.update_progress(
                                current, total, f"Đang kiểm tra {current}/{total}..."
                            ))
                            if decl_id and new_status:
                                self.root.after(0, lambda: self.tracking_panel.update_item_status(
                                    decl_id, new_status, last_checked, cleared_at
                                ))
                    
                    # Pass IDs and progress callback if supported
                    count = self.clearance_checker.check_now(ids_to_check=ids, progress_callback=on_progress)
                    
                    # Hide progress and refresh
                    if hasattr(self, 'tracking_panel'):
                        self.root.after(0, self.tracking_panel.hide_progress)
                        self.root.after(0, self.tracking_panel.refresh)
                    
                    # Get updated data for results dialog
                    check_results = []
                    try:
                        from gui.dialogs.check_results_dialog import CheckResultsDialog, CheckResult
                        all_tracking = self.tracking_db.get_all_tracking()
                        
                        self.logger.info(f"=== DEBUG: After check_now, count={count} ===")
                        self.logger.info(f"=== DEBUG: ids to check = {ids} ===")
                        
                        # Filter to get checked items (if specific IDs, use them; else use all just checked)
                        checked_items = all_tracking if not ids else [d for d in all_tracking if d.id in ids]
                        
                        self.logger.info(f"=== DEBUG: checked_items count = {len(checked_items)} ===")
                        for decl in checked_items:
                            self.logger.info(f"  - {decl.declaration_number}: DB status = '{decl.status.value}'")
                        
                        for decl in checked_items:
                            status_map = {
                                'cleared': ('cleared', 'Đã thông quan'),
                                'transfer': ('transfer', 'Chuyển địa điểm'),
                                'pending': ('pending', 'Chưa thông quan'),
                                'error': ('error', 'Lỗi')
                            }
                            status_info = status_map.get(decl.status.value, ('pending', 'Chưa thông quan'))
                            
                            check_results.append(CheckResult(
                                decl_id=decl.id,
                                declaration_number=decl.declaration_number,
                                tax_code=decl.tax_code,
                                company_name=decl.company_name or "",
                                status=status_info[0],
                                status_text=status_info[1]
                            ))
                        
                        # Show results dialog
                        def show_dialog():
                            dialog = CheckResultsDialog(
                                self.root,
                                total_checked=len(checked_items),
                                results=check_results,
                                on_get_barcodes=lambda selected: self._get_barcodes_for_declarations(selected)
                            )
                            dialog.show()
                        
                        self.root.after(0, show_dialog)
                        
                    except Exception as dialog_err:
                        self.logger.warning(f"Failed to show results dialog: {dialog_err}")
                        # Fallback to simple message
                        msg = f"Đã kiểm tra xong.\nSố tờ khai thông quan mới: {count}"
                        self.root.after(0, lambda: messagebox.showinfo("Hoàn tất kiểm tra", msg))
                except Exception as e:
                    if hasattr(self, 'tracking_panel'):
                        self.root.after(0, self.tracking_panel.hide_progress)
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi kiểm tra: {e}"))
                finally:
                    if hasattr(self, 'tracking_panel'):
                        self.root.after(0, self.tracking_panel.disable_stop_btn)
            
            import threading
            threading.Thread(target=run_check, daemon=True).start()
        else:
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", "Clearance checker chưa khởi tạo.")
    
    def _on_stop_tracking_check(self) -> None:
        """Handle 'Stop' from Tracking Panel - stop current check."""
        if hasattr(self, 'clearance_checker') and self.clearance_checker:
            self.clearance_checker.stop_current_check()
    
    def _on_include_pending_changed(self, include: bool) -> None:
        """Handle include pending checkbox change."""
        self.logger.debug(f"Include pending: {include}")
    
    def _on_exclude_xnktc_changed(self, exclude: bool) -> None:
        """Handle exclude XNKTC checkbox change."""
        self.logger.debug(f"Exclude XNKTC: {exclude}")

    def _show_settings_dialog(self) -> None:
        """Open settings dialog."""
        try:
            def on_settings_saved(retrieval_method, pdf_naming_format):
                """Callback when settings are saved - update clearance checker."""
                from config.user_preferences import get_preferences
                prefs = get_preferences()
                
                # Update clearance checker with new auto-check settings
                if hasattr(self, 'clearance_checker'):
                    self.clearance_checker.set_config(
                        prefs.auto_check_enabled,
                        prefs.auto_check_interval
                    )
                    self.logger.info(f"Clearance checker updated: enabled={prefs.auto_check_enabled}, interval={prefs.auto_check_interval}m")
                
                # Update barcode retriever method
                if hasattr(self, 'barcode_retriever'):
                    self.barcode_retriever.retrieval_method = retrieval_method
                    self.logger.info(f"Barcode retriever method updated: {retrieval_method}")
            
            def on_auto_check_changed(enabled: bool, interval: int):
                """Callback when auto-check settings change - update UI immediately."""
                # Update tracking panel status label
                if hasattr(self, 'tracking_panel') and self.tracking_panel:
                    self.tracking_panel.update_auto_status(enabled)
                    
                    if enabled:
                        # Start/restart countdown and clearance checker
                        self.tracking_panel.start_countdown(interval)
                        if hasattr(self, 'clearance_checker') and self.clearance_checker:
                            self.clearance_checker.set_config(enabled, interval)
                            self.clearance_checker.start()
                    else:
                        # Stop countdown and clearance checker
                        self.tracking_panel.stop_countdown()
                        if hasattr(self, 'clearance_checker') and self.clearance_checker:
                            self.clearance_checker.stop()
                            
                self.logger.info(f"Auto-check settings updated: enabled={enabled}, interval={interval}min")
            
            def on_max_companies_changed(max_companies: int):
                """Callback when max companies setting changes - update CompanyTagPicker immediately."""
                # Update CompanyTagPicker in enhanced_manual_panel
                if hasattr(self, 'enhanced_manual_panel') and self.enhanced_manual_panel:
                    if hasattr(self.enhanced_manual_panel, 'company_tag_picker'):
                        self.enhanced_manual_panel.company_tag_picker.set_max_select(max_companies)
                self.logger.info(f"Max companies setting updated: {max_companies}")
            
            # SettingsDialog requires config_manager and auto-shows on init
            dialog = SettingsDialog(
                self.root,
                config_manager=self.config_manager,
                on_settings_changed=on_settings_saved,
                theme_manager=self.theme_manager if hasattr(self, 'theme_manager') else None,
                on_auto_check_changed=on_auto_check_changed,
                on_max_companies_changed=on_max_companies_changed
            )
        except Exception as e:
            self.logger.error(f"Failed to open settings dialog: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở cài đặt: {e}")

    def _show_database_config_dialog(self) -> None:
        """Open database configuration dialog."""
        try:
            from gui.dialogs.database_config_dialog import DatabaseConfigDialog
            dialog = DatabaseConfigDialog(
                self.root,
                config_manager=self.config_manager,
                ecus_connector=self.ecus_connector,
                logger=self.logger
            )
        except Exception as e:
            self.logger.error(f"Failed to open database config dialog: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở cấu hình database: {e}")

    def _get_barcodes_for_declarations(self, selected_results) -> None:
        """
        Get barcodes for selected cleared declarations from results dialog.
        
        Args:
            selected_results: List of CheckResult objects for which to retrieve barcodes
        """
        if not selected_results:
            return
        
        try:
            # Convert CheckResult to declaration data format for barcode retrieval
            declarations = []
            for result in selected_results:
                # Get full tracking data
                all_tracking = self.tracking_db.get_all_tracking()
                tracking_decl = next((d for d in all_tracking if d.id == result.decl_id), None)
                
                if tracking_decl:
                    declarations.append({
                        'tax_code': tracking_decl.tax_code,
                        'declaration_number': tracking_decl.declaration_number,
                        'customs_office_code': tracking_decl.customs_code,
                        'declaration_date': tracking_decl.declaration_date,
                        'company_name': tracking_decl.company_name
                    })
            
            if declarations:
                self.logger.info(f"Getting barcodes for {len(declarations)} declarations from results dialog")
                
                # Switch to manual panel tab if using tabs
                if hasattr(self, 'tabs') and hasattr(self.tabs, 'select'):
                    # Find and select the barcode retrieval tab
                    pass  # Tab selection depends on implementation
                
                # Trigger barcode download via enhanced manual panel
                if hasattr(self, 'enhanced_manual_panel') and hasattr(self.enhanced_manual_panel, 'download_specific_declarations'):
                    self.enhanced_manual_panel.download_specific_declarations(declarations)
                else:
                    messagebox.showinfo(
                        "Lấy mã vạch",
                        f"Đã chọn {len(declarations)} tờ khai để lấy mã vạch.\n\n"
                        "Vui lòng sử dụng Tab 'Lấy mã vạch' để tải mã vạch."
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to get barcodes for declarations: {e}")
            messagebox.showerror("Lỗi", f"Không thể lấy mã vạch: {e}")
