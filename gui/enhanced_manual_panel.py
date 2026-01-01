"""
Enhanced Manual Panel

This module provides the GUI component for Enhanced Manual Mode,
allowing users to scan companies, select date ranges, preview declarations,
and selectively download barcodes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Callable, Dict, Any
from datetime import datetime, timedelta
import threading
from tkcalendar import DateEntry

from processors.company_scanner import CompanyScanner, CompanyScanError
from processors.preview_manager import PreviewManager, PreviewError
from models.declaration_models import Declaration
from logging_system.logger import Logger
from gui.styles import ModernStyles
from gui.smart_company_search import SmartCompanySearchLogic, Company
from gui.recent_companies_panel import RecentCompaniesPanel
from gui.autocomplete_combobox import AutocompleteCombobox
from file_utils.error_log_exporter import ErrorLogExporter, ErrorEntry
from error_handling.error_tracker import ErrorTracker
from gui.preview_table_controller import PreviewTableController, FilterStatus
from gui.keyboard_shortcuts import KeyboardShortcutManager
from processors.batch_limiter import BatchLimiter
from config.configuration_manager import ConfigurationManager
from web_utils.parallel_downloader import ParallelDownloader, DownloadResult
from gui.company_tag_picker import CompanyTagPicker
from config.user_preferences import get_preferences
from gui.components.tooltip import ToolTip


class EnhancedManualPanel(ttk.Frame):
    """
    GUI component for Enhanced Manual Mode
    
    Provides:
    - Company scanning and selection
    - Date range picker with validation
    - Declaration preview with checkboxes
    - Selective barcode download
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        company_scanner: CompanyScanner,
        preview_manager: PreviewManager,
        logger: Optional[Logger] = None,
        download_callback: Optional[Callable[[List[Declaration]], None]] = None,
        barcode_retriever = None,
        file_manager = None,
        tracking_db = None,
        on_download_complete: Optional[Callable[[int, int], None]] = None,
        error_tracker: Optional[ErrorTracker] = None,
        hide_preview_section: bool = False
    ):
        """
        Initialize EnhancedManualPanel
        
        Args:
            parent: Parent widget
            company_scanner: CompanyScanner instance
            preview_manager: PreviewManager instance
            logger: Optional logger instance
            download_callback: Optional callback for download operation
            barcode_retriever: BarcodeRetriever instance for downloading barcodes
            file_manager: FileManager instance for saving files
            tracking_db: TrackingDatabase instance for tracking processed declarations
            on_download_complete: Callback with (success_count, error_count) after download
            error_tracker: Optional ErrorTracker instance for persistent error storage (Requirements 4.4)
        """
        super().__init__(parent, padding=10)
        
        self.company_scanner = company_scanner
        self.preview_manager = preview_manager
        self.logger = logger
        self.download_callback = download_callback
        self.barcode_retriever = barcode_retriever
        self.file_manager = file_manager
        self.tracking_db = tracking_db
        self.on_download_complete = on_download_complete
        self._error_tracker = error_tracker
        self._hide_preview_section = hide_preview_section  # Hide preview table when used in two-column layout
        
        # External preview panel reference (set when hide_preview_section=True)
        self._external_preview_panel = None
        
        # State tracking
        self.current_state = "initial"  # initial, companies_loaded, preview_displayed, downloading, complete
        self.is_operation_running = False
        self.stop_download_flag = False
        self.download_thread = None
        
        # Error tracking for current session (Requirements 1.1, 1.2)
        self._error_log_exporter = ErrorLogExporter()
        
        # Initialize ErrorTracker if tracking_db is available but error_tracker not provided (Requirements 4.4)
        if self._error_tracker is None and self.tracking_db is not None:
            try:
                self._error_tracker = ErrorTracker(self.tracking_db)
                self._log('info', "ErrorTracker initialized for persistent error storage")
            except Exception as e:
                self._log('warning', f"Failed to initialize ErrorTracker: {e}")
        
        # Company filtering
        self.all_companies = []  # Store all companies for filtering
        self._smart_search = SmartCompanySearchLogic()  # Smart search logic for filtering and auto-select
        
        # Initialize BatchLimiter for download limit validation (Requirements 10.1, 10.2)
        try:
            config_manager = ConfigurationManager('config.ini')
            self._batch_limiter = BatchLimiter(config_manager)
            self._log('info', f"BatchLimiter initialized with limit: {self._batch_limiter.get_limit()}")
        except Exception as e:
            self._log('warning', f"Failed to initialize BatchLimiter: {e}")
            self._batch_limiter = None
        
        # Initialize checkbox variables (needed for both internal and external preview panel)
        # These are used by preview_declarations() regardless of hide_preview_section
        prefs = get_preferences()
        self.include_pending_var = tk.BooleanVar(value=prefs.include_pending)
        self.exclude_xnktc_var = tk.BooleanVar(value=prefs.exclude_xnktc)
        
        # Apply modern styles (Requirements 4.1, 4.2, 4.3, 4.4)
        self._apply_modern_styles()
        
        # Create UI components
        self._create_output_directory_section()
        self._create_company_section()
        self._create_date_range_section()
        
        # Only create action buttons and preview section if not hidden
        # When hide_preview_section=True, these are in the right pane (PreviewPanel)
        if not self._hide_preview_section:
            self._create_action_buttons()
            self._create_preview_section()
        
        # Initialize keyboard shortcuts (Requirements 5.1, 5.2, 5.3, 5.4, 5.5)
        self._setup_keyboard_shortcuts()
        
        # Load companies on startup (this will set the appropriate state)
        self.load_companies_on_startup()
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Helper method to log messages if logger is available"""
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message, **kwargs)
    
    def set_external_preview_panel(self, preview_panel) -> None:
        """
        Set external preview panel reference for two-column layout.
        
        When hide_preview_section=True, this panel is used to display
        preview data instead of the internal preview table.
        
        Args:
            preview_panel: PreviewPanel instance from right pane
        """
        self._external_preview_panel = preview_panel
    
    def _update_pdf_naming_service(self) -> None:
        """
        Update the PDF naming service from current config settings.
        
        This ensures the file manager uses the latest PDF naming format
        configured in settings before downloading barcodes.
        
        Requirements: 5.3
        """
        try:
            from config.configuration_manager import ConfigurationManager
            from file_utils.pdf_naming_service import PdfNamingService
            
            config_manager = ConfigurationManager('config.ini')
            pdf_naming_format = config_manager.get_pdf_naming_format()
            
            # Update file manager's PDF naming service
            if self.file_manager:
                self.file_manager.pdf_naming_service = PdfNamingService(pdf_naming_format)
                self._log('info', f"PDF naming format updated to: {pdf_naming_format}")
        except Exception as e:
            self._log('warning', f"Failed to update PDF naming service: {e}")
            # Continue with existing naming service
    
    def _apply_modern_styles(self) -> None:
        """
        Apply modern styling to the panel.
        
        Configures ttk styles for buttons, entries, frames, and other widgets.
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        try:
            # Get the root window
            root = self.winfo_toplevel()
            
            # Configure ttk styles using ModernStyles
            ModernStyles.configure_ttk_styles(root)
            
            self._log('info', "Modern styles applied to EnhancedManualPanel")
        except Exception as e:
            self._log('warning', f"Failed to apply modern styles: {e}")
    
    def _setup_keyboard_shortcuts(self) -> None:
        """
        Setup keyboard shortcuts for the panel.
        
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        try:
            root = self.winfo_toplevel()
            self._keyboard_manager = KeyboardShortcutManager(root)
            
            # Register default shortcuts
            self._keyboard_manager.register_default_shortcuts(
                refresh_callback=self._shortcut_refresh,
                select_all_callback=self._shortcut_select_all,
                deselect_all_callback=self._shortcut_deselect_all,
                stop_callback=self._shortcut_stop
            )
            
            # Update button tooltips with shortcut hints (Requirement 5.5)
            self._update_button_tooltips()
            
            self._log('info', "Keyboard shortcuts initialized")
        except Exception as e:
            self._log('warning', f"Failed to setup keyboard shortcuts: {e}")
    
    def _shortcut_refresh(self) -> None:
        """Handle F5 shortcut - refresh preview (Requirement 5.1)"""
        if self.current_state in ("companies_loaded", "preview_displayed", "complete"):
            self.preview_declarations()
    
    def _shortcut_select_all(self) -> None:
        """Handle Ctrl+A shortcut - select all (Requirement 5.2)"""
        if self.current_state in ("preview_displayed", "complete"):
            if hasattr(self, 'select_all_var') and self.select_all_var:
                self.select_all_var.set(True)
            self.toggle_select_all()
    
    def _shortcut_deselect_all(self) -> None:
        """Handle Ctrl+Shift+A shortcut - deselect all (Requirement 5.3)"""
        if self.current_state in ("preview_displayed", "complete"):
            if hasattr(self, 'select_all_var') and self.select_all_var:
                self.select_all_var.set(False)
            self.toggle_select_all()
    
    def _shortcut_stop(self) -> None:
        """Handle Escape shortcut - stop download (Requirement 5.4)"""
        if self.current_state == "downloading":
            self.stop_download()
    
    def _update_button_tooltips(self) -> None:
        """
        Update button tooltips with keyboard shortcut hints.
        
        Requirement 5.5
        """
        # Create tooltip bindings for buttons (only if they exist)
        if hasattr(self, 'preview_button') and self.preview_button:
            self._create_tooltip(self.preview_button, "Xem trước tờ khai (F5)")
        if hasattr(self, 'stop_button') and self.stop_button:
            self._create_tooltip(self.stop_button, "Dừng tải xuống (Escape)")
    
    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """
        Create a tooltip for a widget.
        
        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
        """
        def show_tooltip(event):
            if not hasattr(self, '_button_tooltip') or self._button_tooltip is None:
                self._button_tooltip = tk.Toplevel(self)
                self._button_tooltip.wm_overrideredirect(True)
                self._button_tooltip.wm_attributes("-topmost", True)
                
                label = ttk.Label(
                    self._button_tooltip,
                    text=text,
                    background="#ffffe0",
                    foreground="#333333",
                    padding=(5, 2)
                )
                label.pack()
            else:
                for child in self._button_tooltip.winfo_children():
                    child.config(text=text)
            
            x = event.x_root + 10
            y = event.y_root + 10
            self._button_tooltip.wm_geometry(f"+{x}+{y}")
            self._button_tooltip.deiconify()
        
        def hide_tooltip(event):
            if hasattr(self, '_button_tooltip') and self._button_tooltip is not None:
                self._button_tooltip.withdraw()
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def _create_output_directory_section(self) -> None:
        """Create output directory selection UI section with modern styling"""
        # Output directory frame with modern styling (Requirement 4.4)
        output_frame = ttk.LabelFrame(self, text="Thư mục lưu file", padding=10, style='Card.TLabelframe')
        output_frame.pack(fill=tk.X, pady=5)
        
        # Directory row
        dir_row = ttk.Frame(output_frame)
        dir_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_row, text="Thư mục lưu:").pack(side=tk.LEFT, padx=5)
        
        # Get output path from config (will be loaded from config manager)
        from config.configuration_manager import ConfigurationManager
        try:
            config_manager = ConfigurationManager('config.ini')
            initial_path = config_manager.get_output_path()
        except:
            initial_path = 'C:\\CustomsBarcodes'
        
        # Entry with modern styling (Requirement 4.3)
        self.output_var = tk.StringVar(value=initial_path)
        entry = ttk.Entry(dir_row, textvariable=self.output_var, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button with modern styling (Requirement 4.2)
        browse_btn = ttk.Button(
            dir_row,
            text="Chọn...",
            command=self._browse_output_directory,
            width=10,
            style='Secondary.TButton'
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Open folder button
        open_btn = ttk.Button(
            dir_row,
            text="Mở",
            command=self._open_output_directory,
            width=8,
            style='Secondary.TButton'
        )
        open_btn.pack(side=tk.LEFT, padx=5)
    
    def load_companies_on_startup(self) -> None:
        """
        Load saved companies from tracking database on startup
        
        This method is called during initialization to populate the company
        dropdown with previously scanned companies.
        """
        try:
            self._log('info', "Loading companies on startup")
            
            # Load companies from tracking database
            companies = self.company_scanner.load_companies()
            
            if companies:
                # Populate dropdown
                self._populate_company_dropdown(companies)
                
                # Update status
                self.company_status_label.config(
                    text=f"Đã tải {len(companies)} công ty từ database",
                    foreground="green"
                )
                
                # Set state to companies_loaded
                self._set_state("companies_loaded")
                
                self._log('info', f"Loaded {len(companies)} companies on startup")
            else:
                # No companies in database
                self.company_status_label.config(
                    text="Không có công ty nào. Vui lòng quét công ty trước.",
                    foreground="gray"
                )
                
                # Keep initial state
                self._set_state("initial")
                
                self._log('info', "No companies found in database on startup")
                
        except Exception as e:
            # Handle errors gracefully - don't block startup
            self._log('warning', f"Failed to load companies on startup: {e}", exc_info=True)
            
            # Show empty state
            self.company_status_label.config(
                text="Vui lòng quét công ty trước",
                foreground="gray"
            )
            
            # Keep initial state
            self._set_state("initial")
    
    def _create_company_section(self) -> None:
        """
        Create unified company management and date selection section with modern styling.
        
        This section combines company scanning/selection with date range selection
        in a single unified panel for better UX.
        
        Layout order (Requirement 2.2):
        1. Buttons row (Quét công ty, Làm mới)
        2. Search row (Tìm kiếm input + Xóa button)
        3. Company dropdown row
        4. Date range row (Từ ngày ... đến ngày ...)
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 4.4
        """
        # Unified company and time frame with modern styling (Requirement 2.1, 4.4)
        company_frame = ttk.LabelFrame(self, text="Quản lý công ty & Thời gian", padding=10, style='Card.TLabelframe')
        company_frame.pack(fill=tk.X, pady=5)
        
        # Row 1: Button row (Requirement 2.2 - buttons row first)
        button_row = ttk.Frame(company_frame)
        button_row.pack(fill=tk.X, pady=(0, 8))
        
        # Scan button with primary style (Requirement 4.2)
        self.scan_button = ttk.Button(
            button_row,
            text="Quét công ty",
            command=self.scan_companies,
            width=15
        )
        self.scan_button.pack(side=tk.LEFT, padx=(5, 10))
        ToolTip(self.scan_button, "Quét danh sách công ty từ database ECUS5 để lấy thông tin mã số thuế và tên công ty", delay=500)
        
        # Refresh button with secondary style (Requirement 4.2)
        self.refresh_button = ttk.Button(
            button_row,
            text="Làm mới",
            command=self.refresh_companies,
            width=15,
            style='Secondary.TButton'
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.refresh_button, "Tải lại danh sách công ty từ cache đã lưu", delay=500)
        
        # Row 2: Company selection with AutocompleteCombobox (Requirements 4.1, 4.2, 8.1-8.5)
        # Combines search and dropdown into single control
        selection_row = ttk.Frame(company_frame)
        selection_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(selection_row, text="Công ty:", width=10).pack(side=tk.LEFT, padx=5)
        
        # AutocompleteCombobox with filtering (Requirements 4.1, 4.2, 8.1-8.5)
        # Updated with on_filter callback for result count display (Search UX Improvement)
        self.company_var = tk.StringVar()
        self.company_combo = AutocompleteCombobox(
            selection_row,
            values=['Tất cả công ty'],
            on_select=self._on_company_selected,
            on_filter=self._on_company_filter,  # New callback for result count
            placeholder="Nhập mã số thuế hoặc tên công ty...",
            no_match_text="Không tìm thấy",
            textvariable=self.company_var,
            width=50
        )
        self.company_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # v1.5.0: Add button - adds selected company to tag picker
        self.add_company_button = ttk.Button(
            selection_row,
            text="+ Thêm",
            command=self._add_company_to_selection,
            width=8,
            style='Success.TButton'
        )
        self.add_company_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_search_button = ttk.Button(
            selection_row,
            text="Xóa",
            command=self._clear_company_search,
            width=6,
            style='Secondary.TButton'
        )
        self.clear_search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Keep company_search_var for backward compatibility
        self.company_search_var = self.company_var
        
        # Result count label (Search UX Improvement - Requirements 3.1, 3.2)
        self.company_result_count_label = ttk.Label(
            company_frame,
            text="",
            style='Secondary.TLabel',
            foreground='#666666'
        )
        self.company_result_count_label.pack(fill=tk.X, pady=(0, 2))
        
        # Status label with secondary style
        self.company_status_label = ttk.Label(
            company_frame,
            text="Vui lòng quét công ty trước",
            style='Secondary.TLabel'
        )
        self.company_status_label.pack(fill=tk.X, pady=(2, 5))
        
        # Recent companies panel (Requirements 11.1, 11.2, 11.5)
        self.recent_companies_panel = RecentCompaniesPanel(
            company_frame,
            on_select=self._on_recent_company_selected
        )
        # Panel will show itself when there are recent companies
        
        # Load recent companies from database
        self._load_recent_companies()
        
        # v1.5.0: Company Tag Picker - shows selected companies as pills
        self.company_tag_picker = CompanyTagPicker(
            company_frame,
            on_selection_changed=self._on_multi_select_changed
        )
        self.company_tag_picker.pack(fill=tk.X, pady=(5, 0))
        
        # Row 4: Date range row (Requirement 2.1, 2.2 - date row fourth)
        date_row = ttk.Frame(company_frame)
        date_row.pack(fill=tk.X, pady=5)
        
        # Set default dates (v1.5.0: changed from 2 days to 1 day)
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # "Từ ngày" label and picker with consistent alignment
        ttk.Label(date_row, text="Từ ngày", width=10).pack(side=tk.LEFT, padx=5)
        
        self.from_date_var = tk.StringVar()
        self.from_date_entry = self._create_date_picker(date_row, self.from_date_var, yesterday)
        self.from_date_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # "đến ngày" label and picker
        ttk.Label(date_row, text="đến ngày").pack(side=tk.LEFT, padx=(10, 5))
        
        self.to_date_var = tk.StringVar()
        self.to_date_entry = self._create_date_picker(date_row, self.to_date_var, today)
        self.to_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Validation message with warning style
        self.date_validation_label = ttk.Label(
            company_frame,
            text="",
            style='Warning.TLabel'
        )
        self.date_validation_label.pack(fill=tk.X, pady=(2, 0))
    
    def _create_date_range_section(self) -> None:
        """
        DEPRECATED: Date range section is now integrated into _create_company_section.
        
        This method is kept for backward compatibility but does nothing.
        The date pickers are now part of the unified "Quản lý công ty & Thời gian" section.
        
        Requirements: 2.1 - Unified Company_Panel
        """
        # Date range is now integrated into _create_company_section
        # This method is kept empty for backward compatibility
        pass
    
    def _create_preview_section(self) -> None:
        """Create declaration preview section with modern styling (Requirement 4.4, 4.8)"""
        # Preview frame with modern styling
        preview_frame = ttk.LabelFrame(self, text="Xem trước tờ khai", padding=10, style='Card.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Selection controls
        control_row = ttk.Frame(preview_frame)
        control_row.pack(fill=tk.X, pady=5)
        
        # Default to unchecked (Requirement 4.1)
        self.select_all_var = tk.BooleanVar(value=False)
        self.select_all_checkbox = ttk.Checkbutton(
            control_row,
            text="Chọn tất cả",
            variable=self.select_all_var,
            command=self.toggle_select_all
        )
        self.select_all_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Selection count with header style
        self.selection_count_label = ttk.Label(
            control_row,
            text="Đã chọn: 0/0 tờ khai",
            style='Header.TLabel'
        )
        self.selection_count_label.pack(side=tk.LEFT, padx=20)
        
        # Checkbox to include non-cleared declarations (phân luồng nhưng chưa thông quan)
        # Note: include_pending_var is already created in __init__
        self.include_pending_checkbox = ttk.Checkbutton(
            control_row,
            text="Xem cả tờ khai chưa thông quan",
            variable=self.include_pending_var,
            command=self._on_include_pending_changed
        )
        self.include_pending_checkbox.pack(side=tk.LEFT, padx=20)
        
        # Checkbox to exclude XNK TC declarations (Requirements 1.1, 1.2, 1.5)
        # Note: exclude_xnktc_var is already created in __init__
        self.exclude_xnktc_checkbox = ttk.Checkbutton(
            control_row,
            text="Không lấy mã vạch tờ khai XNK TC",
            variable=self.exclude_xnktc_var,
            command=self._on_exclude_xnktc_changed
        )
        self.exclude_xnktc_checkbox.pack(side=tk.LEFT, padx=20)
        
        # Filter dropdown (Requirements 3.1, 3.2)
        filter_frame = ttk.Frame(control_row)
        filter_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(filter_frame, text="Lọc:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Tất cả")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["Tất cả", "Thành công", "Thất bại", "Chưa xử lý"],
            state="readonly",
            width=12
        )
        self.filter_combo.pack(side=tk.LEFT)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)
        
        # Preview table
        table_frame = ttk.Frame(preview_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview with modern styling (Requirement 4.8)
        columns = ("stt", "checkbox", "declaration_number", "tax_code", "date", "status", "declaration_type", "bill_of_lading", "invoice_number", "result")
        self.preview_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.preview_tree.yview)
        h_scrollbar.config(command=self.preview_tree.xview)
        
        # Column headings with sort handlers (Requirements 3.3, 3.4)
        # Store original heading texts for sort indicator
        self._column_headings = {
            "stt": "STT",
            "checkbox": "☐",
            "declaration_number": "Số tờ khai",
            "tax_code": "Mã số thuế",
            "date": "Ngày",
            "status": "Trạng thái",
            "declaration_type": "Loại hình",
            "bill_of_lading": "Vận đơn",
            "invoice_number": "Số hóa đơn",
            "result": "Kết quả"
        }
        
        # Sortable columns (excluding checkbox and result)
        sortable_columns = ["declaration_number", "tax_code", "date", "status", "declaration_type", "bill_of_lading", "invoice_number"]
        
        for col, text in self._column_headings.items():
            if col in sortable_columns:
                # Add click handler for sorting
                self.preview_tree.heading(
                    col, 
                    text=text,
                    command=lambda c=col: self._on_column_header_click(c)
                )
            else:
                self.preview_tree.heading(col, text=text)
        
        # Column widths
        self.preview_tree.column("stt", width=40, stretch=False, anchor="center")
        self.preview_tree.column("checkbox", width=40, stretch=False)
        self.preview_tree.column("declaration_number", width=150)
        self.preview_tree.column("tax_code", width=120)
        self.preview_tree.column("date", width=100)
        self.preview_tree.column("status", width=100)
        self.preview_tree.column("declaration_type", width=80)
        self.preview_tree.column("bill_of_lading", width=150)
        self.preview_tree.column("invoice_number", width=120)
        self.preview_tree.column("result", width=60, stretch=False, anchor="center")
        
        self.preview_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure alternating row colors for Treeview (Requirement 4.8)
        # Note: Theme-aware colors will be applied by ThemeManager when theme changes
        ModernStyles.configure_treeview_tags(self.preview_tree)
        
        # Configure result column tags for success/error colors
        # Use bold font for better visibility of checkmarks
        # Note: These colors will be updated by ThemeManager._update_treeview_tags when theme changes
        self.preview_tree.tag_configure('success_result', foreground=ModernStyles.SUCCESS_COLOR, font=('Segoe UI', 12, 'bold'))
        self.preview_tree.tag_configure('error_result', foreground=ModernStyles.ERROR_COLOR, font=('Segoe UI', 12, 'bold'))
        
        # Bind click event for checkbox toggle
        self.preview_tree.bind("<Button-1>", self._on_tree_click)
        
        # Bind double-click to open PDF (Requirements 3.5, 3.6)
        self.preview_tree.bind("<Double-1>", self._on_tree_double_click)
        
        # Bind hover highlighting (Requirement 4.8)
        self.preview_tree.bind("<Motion>", self._on_tree_hover)
        self.preview_tree.bind("<Leave>", self._on_tree_leave)
        self._last_hover_item = None
        
        # Initialize PreviewTableController (Requirements 3.1-3.6)
        self._preview_table_controller = PreviewTableController(
            self.preview_tree,
            on_filter_change=self._on_controller_filter_change,
            on_sort_change=self._on_controller_sort_change
        )
        
        # Preview status with secondary style
        self.preview_status_label = ttk.Label(
            preview_frame,
            text="Chưa có dữ liệu xem trước",
            style='Secondary.TLabel'
        )
        self.preview_status_label.pack(fill=tk.X, pady=5)
    
    def _create_action_buttons(self) -> None:
        """Create action buttons section with modern styling (Requirement 4.2)"""
        # Action frame
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=10)
        
        # Preview button with primary style
        self.preview_button = ttk.Button(
            action_frame,
            text="Xem trước",
            command=self.preview_declarations,
            width=15
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        # Download button with success style (Requirement 4.2)
        self.download_button = ttk.Button(
            action_frame,
            text="Lấy mã vạch",
            command=self.download_selected,
            width=15,
            style='Success.TButton'
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # Cancel button with secondary style
        self.cancel_button = ttk.Button(
            action_frame,
            text="Hủy",
            command=self.cancel_operation,
            width=15,
            style='Secondary.TButton'
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button with danger style (Requirement 4.2)
        self.stop_button = ttk.Button(
            action_frame,
            text="Dừng",
            command=self.stop_download,
            width=15,
            style='Danger.TButton'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Export error log button (Requirements 1.1, 1.3, 1.4)
        self.export_error_log_button = ttk.Button(
            action_frame,
            text="Xuất log lỗi",
            command=self.export_error_log,
            width=15,
            style='Secondary.TButton'
        )
        self.export_error_log_button.pack(side=tk.LEFT, padx=5)
        
        # Retry failed button (Requirements 4.2, 4.3)
        self.retry_failed_button = ttk.Button(
            action_frame,
            text="Tải lại thất bại",
            command=self.retry_failed_downloads,
            width=15,
            style='Warning.TButton'
        )
        self.retry_failed_button.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar with modern styling (Requirement 4.7)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400,
            style='Horizontal.TProgressbar'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Progress label with info style
        self.progress_label = ttk.Label(
            progress_frame,
            text="",
            style='Info.TLabel'
        )
        self.progress_label.pack(side=tk.LEFT, padx=5)
    
    def _create_date_picker(self, parent: tk.Widget, variable: tk.StringVar, initial_date: datetime) -> DateEntry:
        """
        Create date picker with calendar
        
        Args:
            parent: Parent widget
            variable: StringVar to bind to
            initial_date: Initial date to display
            
        Returns:
            DateEntry widget
        """
        date_entry = DateEntry(
            parent,
            textvariable=variable,
            date_pattern='dd/mm/yyyy',
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            locale='en_US',  # Using en_US as vi_VN may not be available
            year=initial_date.year,
            month=initial_date.month,
            day=initial_date.day
        )
        return date_entry
    
    # Event Handlers
    
    def _browse_output_directory(self) -> None:
        """
        Browse and select output directory
        
        Opens a directory selection dialog and validates the selected directory.
        Updates the output_var with the selected path if valid.
        """
        from tkinter import filedialog
        import os
        
        # Open directory selection dialog
        selected_dir = filedialog.askdirectory(
            title="Chọn thư mục lưu file PDF",
            initialdir=self.output_var.get()
        )
        
        if selected_dir:
            # Validate directory exists and is writable
            if os.path.exists(selected_dir):
                # Test if directory is writable
                test_file = os.path.join(selected_dir, '.test_write')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    
                    # Directory is valid and writable
                    self.output_var.set(selected_dir)
                    self._log('info', f"Output directory changed to: {selected_dir}")
                    
                    # Save to config
                    self._save_output_directory(selected_dir)
                    
                    messagebox.showinfo(
                        "Thành công",
                        f"Đã chọn thư mục:\n{selected_dir}"
                    )
                except (IOError, OSError) as e:
                    self._log('error', f"Directory not writable: {selected_dir}, error: {e}")
                    messagebox.showerror(
                        "Lỗi",
                        f"Không thể ghi vào thư mục:\n{selected_dir}\n\nVui lòng chọn thư mục khác."
                    )
            else:
                self._log('error', f"Directory does not exist: {selected_dir}")
                messagebox.showerror(
                    "Lỗi",
                    f"Thư mục không tồn tại:\n{selected_dir}"
                )
    
    def _save_output_directory(self, path: str) -> None:
        """
        Save selected output directory to config.ini
        
        Args:
            path: Directory path to save
        """
        try:
            from config.configuration_manager import ConfigurationManager
            
            config_manager = ConfigurationManager('config.ini')
            config_manager.set_output_path(path)
            config_manager.save()
            
            self._log('info', f"Saved output directory to config: {path}")
        except Exception as e:
            self._log('error', f"Failed to save output directory to config: {e}", exc_info=True)
            messagebox.showwarning(
                "Cảnh báo",
                f"Không thể lưu cấu hình:\n{str(e)}\n\nThư mục đã được chọn nhưng sẽ không được lưu lại."
            )
    
    def _open_output_directory(self) -> None:
        """
        Open the output directory in file explorer
        """
        import subprocess
        import platform
        import os
        
        output_path = self.output_var.get()
        
        if not output_path:
            messagebox.showwarning("Cảnh báo", "Chưa chọn thư mục lưu file.")
            return
        
        # Normalize path (convert forward slashes to backslashes on Windows)
        output_path = os.path.normpath(output_path)
        
        if not os.path.exists(output_path):
            # Try to create the directory
            try:
                os.makedirs(output_path, exist_ok=True)
                self._log('info', f"Created output directory: {output_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Thư mục không tồn tại và không thể tạo:\n{output_path}")
                return
        
        try:
            # Open directory in file explorer
            system = platform.system()
            if system == "Windows":
                # Use os.startfile for better Windows compatibility with paths containing spaces
                os.startfile(output_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", output_path])
            else:  # Linux
                subprocess.run(["xdg-open", output_path])
            
            self._log('info', f"Opened output directory: {output_path}")
        except Exception as e:
            self._log('error', f"Error opening output directory: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở thư mục:\n{str(e)}")
    
    def scan_companies(self) -> None:
        """Scan companies from database"""
        def scan_in_thread():
            try:
                self._log('info', "Starting company scan")
                self.is_operation_running = True
                
                # Update UI
                self.after(0, lambda: self.scan_button.config(state=tk.DISABLED))
                self.after(0, lambda: self.company_status_label.config(
                    text="Đang quét công ty...",
                    foreground="blue"
                ))
                
                # Scan and save companies
                saved_count, companies = self.company_scanner.scan_and_save_companies(
                    days_back=90
                )
                
                # Update company dropdown
                self.after(0, lambda: self._populate_company_dropdown(companies))
                
                # Update status
                self.after(0, lambda: self.company_status_label.config(
                    text=f"Đã tìm thấy {len(companies)} công ty",
                    foreground="green"
                ))
                
                # Change state
                self.after(0, lambda: self._set_state("companies_loaded"))
                
                self._log('info', f"Company scan completed: {saved_count} companies saved")
                
            except CompanyScanError as e:
                self._log('error', f"Company scan failed: {e}", exc_info=True)
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi quét công ty",
                    f"Không thể quét công ty:\n{str(e)}"
                ))
                self.after(0, lambda: self.company_status_label.config(
                    text="Lỗi quét công ty",
                    foreground="red"
                ))
            finally:
                self.is_operation_running = False
                self.after(0, lambda: self.scan_button.config(state=tk.NORMAL))
        
        # Run in background thread
        thread = threading.Thread(target=scan_in_thread, daemon=True)
        thread.start()
    
    def refresh_companies(self) -> None:
        """
        Refresh company list and reset all UI elements to initial state.
        
        Resets:
        - Company dropdown and search box
        - Preview table (clears all declarations)
        - Progress bar (resets to 0)
        - Selection count
        """
        try:
            self._log('info', "Refreshing company list and resetting UI")
            
            # 1. Reset company search box
            self.company_combo.clear()  # Clear and show placeholder
            
            # 2. Reset preview table - clear all items (only if not hidden)
            if not self._hide_preview_section and hasattr(self, 'preview_tree'):
                for item in self.preview_tree.get_children():
                    self.preview_tree.delete(item)
            elif self._external_preview_panel:
                self._external_preview_panel.clear()
            
            # 3. Reset progress bar to 0 (only if not hidden)
            if not self._hide_preview_section and hasattr(self, 'progress_bar'):
                self.progress_bar['value'] = 0
                self.progress_label.config(text="")
            
            # 4. Reset selection count (only if not hidden)
            if not self._hide_preview_section and hasattr(self, 'selection_count_label'):
                self.selection_count_label.config(text="Đã chọn: 0/0 tờ khai")
                self.select_all_var.set(False)
            
            # 5. Reset preview status (only if not hidden)
            if not self._hide_preview_section and hasattr(self, 'preview_status_label'):
                self.preview_status_label.config(
                    text="Chưa có dữ liệu xem trước",
                    foreground="gray"
                )
            
            # 6. Clear preview manager data
            if hasattr(self.preview_manager, 'clear_preview'):
                self.preview_manager.clear_preview()
            
            # 7. Reset filter dropdown (only if not hidden)
            if not self._hide_preview_section and hasattr(self, 'filter_var'):
                self.filter_var.set("Tất cả")
            
            # 8. Load companies from database
            companies = self.company_scanner.load_companies()
            self._populate_company_dropdown(companies)
            
            if companies:
                self.company_status_label.config(
                    text=f"Đã tải {len(companies)} công ty",
                    foreground="green"
                )
                self._set_state("companies_loaded")
            else:
                self.company_status_label.config(
                    text="Không có công ty nào. Vui lòng quét công ty trước.",
                    foreground="gray"
                )
                self._set_state("initial")
            
            self._log('info', "UI reset complete")
            
        except Exception as e:
            self._log('error', f"Failed to refresh companies: {e}", exc_info=True)
            messagebox.showerror(
                "Lỗi",
                f"Không thể tải danh sách công ty:\n{str(e)}"
            )
    
    def preview_declarations(self) -> None:
        """Preview declarations based on selected filters"""
        # Sync checkbox values from external preview panel if using two-column layout
        if self._hide_preview_section and self._external_preview_panel:
            self.include_pending_var.set(self._external_preview_panel.include_pending_var.get())
            self.exclude_xnktc_var.set(self._external_preview_panel.exclude_xnktc_var.get())
        
        def preview_in_thread():
            try:
                self._log('info', "Starting declaration preview")
                self.is_operation_running = True
                
                # Clear any previous cancel state
                self.preview_manager.clear_preview()
                
                # Update UI - only if widgets exist (not hidden)
                if not self._hide_preview_section:
                    self.after(0, lambda: self.preview_button.config(state=tk.DISABLED))
                    self.after(0, lambda: self.cancel_button.config(state=tk.NORMAL))
                    self.after(0, lambda: self.preview_status_label.config(
                        text="Đang truy vấn database...",
                        foreground="blue"
                    ))
                elif self._external_preview_panel:
                    self.after(0, lambda: self._external_preview_panel.update_status("Đang truy vấn database..."))
                
                # Validate date formats first
                from_date_str = self.from_date_var.get()
                to_date_str = self.to_date_var.get()
                
                if not self._validate_date_format(from_date_str):
                    return
                if not self._validate_date_format(to_date_str):
                    return
                
                # Parse dates
                from_date = self._parse_date(from_date_str)
                to_date = self._parse_date(to_date_str)
                
                # Validate dates
                validation_error = self._validate_date_range(from_date, to_date)
                if validation_error:
                    self.after(0, lambda: messagebox.showwarning(
                        "Lỗi ngày tháng",
                        validation_error
                    ))
                    return
                
                # v1.5.0: Get selected companies from tag picker (multi-select)
                tax_codes = None
                if hasattr(self, 'company_tag_picker'):
                    selected_companies = self.company_tag_picker.get_selected_companies()
                    if selected_companies:
                        tax_codes = selected_companies
                        self._log('info', f"Previewing {len(tax_codes)} selected companies: {tax_codes}")
                
                # Fallback to dropdown if no companies selected in tag picker
                if not tax_codes:
                    company_selection = self.company_var.get()
                    if company_selection and company_selection != 'Tất cả công ty':
                        # Extract tax code from selection (format: "TaxCode - Company Name")
                        if ' - ' in company_selection:
                            tax_code = company_selection.split(' - ')[0].strip()
                            tax_codes = [tax_code]
                
                # Get include_pending option
                include_pending = self.include_pending_var.get()
                
                # Get preview
                declarations = self.preview_manager.get_declarations_preview(
                    from_date,
                    to_date,
                    tax_codes,
                    include_pending=include_pending
                )
                
                # Store original count before filtering (Requirements 3.1, 3.2, 3.3)
                total_count = len(declarations)
                
                # Apply XNK TC filter if enabled (Requirements 1.3, 1.4, 4.1, 4.2)
                exclude_xnktc = self.exclude_xnktc_var.get()
                declarations = self.preview_manager.filter_xnktc_declarations(
                    declarations, 
                    exclude_xnktc=exclude_xnktc
                )
                filtered_count = len(declarations)
                excluded_count = total_count - filtered_count
                
                # Update preview table
                self.after(0, lambda: self._populate_preview_table(declarations))
                
                # Update status with filtered count (Requirements 3.1, 3.3)
                if declarations:
                    if exclude_xnktc and excluded_count > 0:
                        status_text = f"Tìm thấy {filtered_count} tờ khai (đã lọc bỏ {excluded_count} tờ khai XNK TC)"
                    else:
                        status_text = f"Tìm thấy {filtered_count} tờ khai"
                    
                    if not self._hide_preview_section:
                        self.after(0, lambda: self.preview_status_label.config(
                            text=status_text,
                            foreground="green"
                        ))
                    elif self._external_preview_panel:
                        self.after(0, lambda: self._external_preview_panel.update_status(status_text))
                    
                    self.after(0, lambda: self._set_state("preview_displayed"))
                else:
                    if exclude_xnktc and excluded_count > 0:
                        status_text = f"Không tìm thấy tờ khai nào (đã lọc bỏ {excluded_count} tờ khai XNK TC)"
                    else:
                        status_text = "Không tìm thấy tờ khai nào"
                    
                    if not self._hide_preview_section:
                        self.after(0, lambda: self.preview_status_label.config(
                            text=status_text,
                            foreground="orange"
                        ))
                    elif self._external_preview_panel:
                        self.after(0, lambda: self._external_preview_panel.update_status(status_text))
                
                self._log('info', f"Preview completed: {filtered_count} declarations found (filtered from {total_count}, excluded {excluded_count} XNK TC)")
                
            except ValueError as e:
                self._log('error', f"Date validation error: {e}")
                self.after(0, lambda: messagebox.showwarning(
                    "Lỗi ngày tháng",
                    str(e)
                ))
            except PreviewError as e:
                self._log('error', f"Preview failed: {e}", exc_info=True)
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi xem trước",
                    f"Không thể xem trước tờ khai:\n{str(e)}"
                ))
                if not self._hide_preview_section:
                    self.after(0, lambda: self.preview_status_label.config(
                        text="Lỗi xem trước",
                        foreground="red"
                    ))
                elif self._external_preview_panel:
                    self.after(0, lambda: self._external_preview_panel.update_status("Lỗi xem trước", is_error=True))
            finally:
                self.is_operation_running = False
                if not self._hide_preview_section:
                    self.after(0, lambda: self.preview_button.config(state=tk.NORMAL))
                    self.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
        
        # Run in background thread
        thread = threading.Thread(target=preview_in_thread, daemon=True)
        thread.start()
    
    def download_specific_declarations(self, declarations: List[Dict[str, Any]]) -> None:
        """
        Download specific declarations passed from external source (e.g. Tracking Tab).
        
        Args:
            declarations: List of declaration dictionaries
        """
        if not declarations:
            return
            
        # Convert dictionaries to objects compatible with download logic
        # We need Declaration-like objects
        from models.declaration_models import Declaration
        
        target_declarations = []
        for d in declarations:
            # Handle key variations
            decl_num = d.get('declaration_number') or d.get('decl_number')
            tax_code = d.get('tax_code')
            
            # Skip invalid
            if not decl_num or not tax_code:
                continue
                
            # Create Declaration object (or similar)
            # We need minimal fields for barcode retrieval: tax_code, declaration_number, customs_code, declaration_date
            
            # Parse date
            decl_date = d.get('date') or d.get('declaration_date')
            if isinstance(decl_date, str):
                try:
                    decl_date = datetime.strptime(decl_date, "%d/%m/%Y")
                except:
                    try:
                        decl_date = datetime.strptime(decl_date, "%Y-%m-%d") 
                    except:
                        decl_date = datetime.now()
            
            decl_obj = Declaration(
                declaration_number=decl_num,
                tax_code=tax_code,
                declaration_date=decl_date,
                customs_office_code=d.get('customs_code', '') or d.get('customs_office_code', ''),
                transport_method="",
                channel="",
                status="",
                goods_description=None,
                company_name=d.get('company_name', '')
            )
            target_declarations.append(decl_obj)
            
        if not target_declarations:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu hợp lệ để tải.")
            return

        # Reuse download logic
        # We need to bypass 'selected_declarations' logic of download_selected
        # Can we refactor download_selected/download_in_thread to accept list?
        # download_in_thread is nested inside download_selected.
        # We should extract the inner logic or copy it.
        # Given constraints, I'll copy/adapt the logic to run immediately.
        
        # Check dependencies
        if not self.barcode_retriever or not self.file_manager or not self.tracking_db:
            messagebox.showerror("Lỗi", "Thiếu dependency.")
            return

        self._update_pdf_naming_service()
        self.stop_download_flag = False
        self.clear_session_errors()
        self._set_state("downloading")
        
        if self._external_preview_panel:
            self._external_preview_panel.set_downloading_state(True)
            
        # Run in thread
        def download_thread():
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from threading import Lock
            
            success = 0
            error = 0
            skipped = 0
            total = len(target_declarations)
            completed = 0
            lock = Lock()
            output_dir = self.output_var.get()
            
            self.file_manager.output_directory = output_dir

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for decl in target_declarations:
                     # We reuse the process logic. 
                     # But since process_single_declaration is nested in download_selected,
                     # we must duplicate it or make it a method.
                     # For safety and speed now, I'll call barcode_retriever directly here.
                     futures.append(executor.submit(self._process_single_download, decl, output_dir, lock))
                     
                for future in as_completed(futures):
                    result_type, decl_res = future.result()
                    completed += 1
                    
                    if result_type == 'success':
                        success += 1
                    elif result_type == 'skipped':
                        skipped += 1
                    else:
                        error += 1
                        
                    # Update progress
                    progress = (completed / total) * 100
                    if self._external_preview_panel:
                        self.after(0, lambda p=progress, c=completed, t=total: 
                            self._external_preview_panel.update_progress(p, c, t))
                            
            # Finish
            self.after(0, lambda: self._show_download_result_popup(success, error, skipped, total))
            self.after(0, lambda: self._set_state("ready"))
            if self._external_preview_panel:
                self.after(0, lambda: self._external_preview_panel.set_downloading_state(False))
                
        import threading
        t = threading.Thread(target=download_thread, daemon=True)
        t.start()

    def _process_single_download(self, declaration, output_dir, lock):
        """Helper for list download"""
        try:
            if self.stop_download_flag:
                return 'skipped', declaration
                
            pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
            if pdf_content:
                file_path = self.file_manager.save_barcode(declaration, pdf_content, overwrite=True)
                if file_path:
                    self.tracking_db.add_processed(declaration, file_path)
                    try:
                        self.tracking_db.save_recent_company(declaration.tax_code)
                    except: pass
                    return 'success', declaration
                else:
                    return 'skipped', declaration
            else:
                 return 'error', declaration
        except Exception:
            return 'error', declaration

            if self._hide_preview_section and self._external_preview_panel:
                # Get selected declaration numbers from PreviewPanel
                selected_numbers = self._external_preview_panel.get_selected_declarations()
                
                # Find matching Declaration objects
                selected_declarations = [
                    decl for decl in self.preview_manager._all_declarations
                    if decl.declaration_number in selected_numbers
                ]
                
                # Sync selection to preview_manager for consistency
                self.preview_manager._selected_declarations = {decl.id for decl in selected_declarations}
            else:
                selected_declarations = self.preview_manager.get_selected_declarations()
            
            if not selected_declarations:
                messagebox.showwarning(
                    "Không có tờ khai",
                    "Vui lòng chọn ít nhất một tờ khai để tải mã vạch"
                )
                return
            
            # Validate selection count against batch limit (Requirements 10.1, 10.2)
            if self._batch_limiter:
                is_valid, message = self._batch_limiter.validate_selection(len(selected_declarations))
                if not is_valid:
                    messagebox.showwarning("Vượt quá giới hạn", message)
                    return
            
            # Check if required dependencies are available
            if not self.barcode_retriever or not self.file_manager or not self.tracking_db:
                self._log('error', "Missing required dependencies for download")
                messagebox.showerror(
                    "Lỗi cấu hình",
                    "Thiếu các thành phần cần thiết để tải mã vạch"
                )
                return
            
            # Update PDF naming service from current config (Requirements 5.3)
            self._update_pdf_naming_service()
            
            self._log('info', f"Starting download for {len(selected_declarations)} declarations")
            
            # Reset stop flag
            self.stop_download_flag = False
            
            # Clear previous session errors before starting new download (Requirements 1.1)
            self.clear_session_errors()
            
            # Set state to downloading
            self._set_state("downloading")
            
            # Update external preview panel state
            if self._external_preview_panel:
                self._external_preview_panel.set_downloading_state(True)
            
            # Run download in background thread with parallel processing (Requirements 9.1)
            def download_in_thread():
                from concurrent.futures import ThreadPoolExecutor, as_completed
                from threading import Lock
                
                success_count = 0
                error_count = 0
                skipped_count = 0
                total = len(selected_declarations)
                completed_count = 0
                count_lock = Lock()
                
                # Set output directory once
                output_dir = self.output_var.get()
                
                def process_single_declaration(declaration):
                    """Process a single declaration - runs in thread pool"""
                    nonlocal success_count, error_count, skipped_count, completed_count
                    
                    # Check stop flag
                    if self.stop_download_flag:
                        return None
                    
                    try:
                        self._log('info', f"Processing declaration: {declaration.id}")
                        
                        # Update file_manager output directory
                        self.file_manager.output_directory = output_dir
                        
                        # Retrieve barcode
                        pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
                        
                        if pdf_content:
                            # Save to file
                            file_path = self.file_manager.save_barcode(
                                declaration,
                                pdf_content,
                                overwrite=True
                            )
                            
                            if file_path:
                                # Track in database
                                self.tracking_db.add_processed(declaration, file_path)
                                
                                # Update recent companies (Requirements 11.3)
                                try:
                                    self.tracking_db.save_recent_company(declaration.tax_code)
                                except Exception as rc_error:
                                    self._log('warning', f"Failed to save recent company: {rc_error}")
                                
                                with count_lock:
                                    success_count += 1
                                self._log('info', f"Successfully saved barcode for {declaration.id}")
                                
                                # Update result column with green checkmark (Requirements 3.5, 3.6)
                                self.after(0, lambda dn=declaration.declaration_number, fp=file_path: 
                                    self._update_download_result(dn, True, file_path=fp))
                                return ('success', declaration)
                            else:
                                with count_lock:
                                    skipped_count += 1
                                self._log('warning', f"Skipped saving barcode for {declaration.id}")
                                
                                # Record error for skipped file (Requirements 1.1, 1.2)
                                skip_error = 'File could not be saved (skipped)'
                                self._record_error(
                                    declaration_number=declaration.declaration_number,
                                    error_type='file_error',
                                    error_message=skip_error
                                )
                                
                                # Update result column with red X for skipped (Requirements 4.1)
                                self.after(0, lambda dn=declaration.declaration_number, em=skip_error: 
                                    self._update_download_result(dn, False, error_message=em))
                                return ('skipped', declaration)
                        else:
                            with count_lock:
                                error_count += 1
                            self._log('error', f"Failed to retrieve barcode for {declaration.id}")
                            
                            # Record error for failed retrieval (Requirements 1.1, 1.2)
                            api_error = 'Failed to retrieve barcode from API'
                            self._record_error(
                                declaration_number=declaration.declaration_number,
                                error_type='api_error',
                                error_message=api_error
                            )
                            
                            # Update result column with red X for error (Requirements 4.1)
                            self.after(0, lambda dn=declaration.declaration_number, em=api_error: 
                                self._update_download_result(dn, False, error_message=em))
                            return ('error', declaration)
                    
                    except Exception as e:
                        with count_lock:
                            error_count += 1
                        self._log('error', f"Error processing {declaration.id}: {e}", exc_info=True)
                        
                        # Record exception error (Requirements 1.1, 1.2)
                        exc_error = str(e)
                        self._record_error(
                            declaration_number=declaration.declaration_number,
                            error_type='exception',
                            error_message=exc_error
                        )
                        
                        # Update result column with red X for exception (Requirements 4.1)
                        self.after(0, lambda dn=declaration.declaration_number, em=exc_error: 
                            self._update_download_result(dn, False, error_message=em))
                        return ('error', declaration)
                
                try:
                    # Use ThreadPoolExecutor for parallel downloads (Requirements 9.1)
                    # Limit to 3 concurrent downloads to avoid overwhelming the server
                    MAX_CONCURRENT = 3
                    
                    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
                        # Submit all tasks
                        futures = {executor.submit(process_single_declaration, decl): decl 
                                   for decl in selected_declarations}
                        
                        # Process completed tasks
                        for future in as_completed(futures):
                            if self.stop_download_flag:
                                # Cancel remaining futures
                                for f in futures:
                                    f.cancel()
                                break
                            
                            with count_lock:
                                completed_count += 1
                            
                            # Update progress
                            progress = int((completed_count / total) * 100)
                            self.after(0, lambda p=progress, idx=completed_count, t=total: 
                                self._update_progress(p, idx, t))
                    
                    # Update final progress
                    final_progress = 100 if not self.stop_download_flag else int((completed_count / total) * 100)
                    self.after(0, lambda: self._update_progress(final_progress, completed_count, total))
                    
                    # Show summary
                    if self.stop_download_flag:
                        summary_msg = f"Đã dừng tải xuống\n\n"
                        summary_msg += f"Hoàn thành: {success_count}/{total}\n"
                        summary_msg += f"Đã xử lý: {completed_count}/{total}\n"
                        summary_msg += f"Còn lại: {total - completed_count}\n"
                        if error_count > 0:
                            summary_msg += f"Lỗi: {error_count}\n"
                        
                        self.after(0, lambda: messagebox.showinfo("Đã dừng", summary_msg))
                        if not self._hide_preview_section and hasattr(self, 'preview_status_label'):
                            self.after(0, lambda: self.preview_status_label.config(
                                text=f"Đã dừng: {success_count}/{total} thành công (đa luồng)",
                                foreground="orange"
                            ))
                        elif self._external_preview_panel:
                            self.after(0, lambda: self._external_preview_panel.update_status(
                                f"Đã dừng: {success_count}/{total} thành công (đa luồng)"))
                    else:
                        # Show custom result popup with "Open folder" button
                        self.after(0, lambda sc=success_count, ec=error_count, sk=skipped_count, t=total: 
                            self._show_download_result_popup(sc, ec, sk, t))
                        if not self._hide_preview_section and hasattr(self, 'preview_status_label'):
                            self.after(0, lambda: self.preview_status_label.config(
                                text=f"Hoàn thành: {success_count}/{total} thành công (đa luồng)",
                                foreground="green"
                            ))
                        elif self._external_preview_panel:
                            self.after(0, lambda: self._external_preview_panel.update_status(
                                f"Hoàn thành: {success_count}/{total} thành công (đa luồng)"))
                    
                    self._log('info', f"Download completed: {success_count} success, {error_count} errors, {skipped_count} skipped")
                    
                    # Call download complete callback (Requirements 10.1, 10.2, 10.3)
                    if self.on_download_complete:
                        self.after(0, lambda sc=success_count, ec=error_count: 
                            self.on_download_complete(sc, ec))
                    
                    # Refresh recent companies panel (Requirements 11.3)
                    self.after(0, self._load_recent_companies)
                    
                    # Update external preview panel - enable retry if errors
                    if self._external_preview_panel:
                        self.after(0, lambda: self._external_preview_panel.set_downloading_state(False))
                        if error_count > 0:
                            self.after(0, lambda: self._external_preview_panel.enable_retry_button(True))
                
                except Exception as e:
                    self._log('error', f"Download thread failed: {e}", exc_info=True)
                    self.after(0, lambda: messagebox.showerror(
                        "Lỗi",
                        f"Lỗi trong quá trình tải:\n{str(e)}"
                    ))
                finally:
                    # Reset state
                    self.after(0, lambda: self._set_state("complete"))
                    self.is_operation_running = False
            
            # Start download thread
            self.is_operation_running = True
            self.download_thread = threading.Thread(target=download_in_thread, daemon=True)
            self.download_thread.start()
        
        except Exception as e:
            self._log('error', f"Download failed: {e}", exc_info=True)
            messagebox.showerror(
                "Lỗi",
                f"Không thể tải mã vạch:\n{str(e)}"
            )
            self._set_state("preview_displayed")
    
    def _show_download_result_popup(self, success_count: int, error_count: int, skipped_count: int, total: int) -> None:
        """
        Show download result popup with option to open output folder
        
        Args:
            success_count: Number of successful downloads
            error_count: Number of failed downloads
            skipped_count: Number of skipped downloads
            total: Total number of declarations
        """
        import subprocess
        import platform
        
        try:
            # Create custom dialog
            dialog = tk.Toplevel(self)
            dialog.title("Kết quả lấy mã vạch")
            dialog.geometry("420x280")
            dialog.resizable(False, False)
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Determine icon and title based on results
            if success_count > 0 and error_count == 0:
                icon = "✅"
                title = "Hoàn thành thành công!"
                title_color = "green"
            elif success_count > 0 and error_count > 0:
                icon = "⚠️"
                title = "Hoàn thành một phần"
                title_color = "orange"
            else:
                icon = "❌"
                title = "Không thành công"
                title_color = "red"
            
            # Title frame
            title_frame = ttk.Frame(main_frame)
            title_frame.pack(fill=tk.X, pady=(0, 15))
            
            title_label = tk.Label(
                title_frame,
                text=f"{icon} {title}",
                font=("Arial", 14, "bold"),
                fg=title_color,
                bg="white"
            )
            title_label.pack()
            
            # Results frame
            results_frame = ttk.Frame(main_frame)
            results_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Results text
            results_text = f"Tổng số tờ khai: {total}\n"
            if success_count > 0:
                results_text += f"✅ Thành công: {success_count}\n"
            if error_count > 0:
                results_text += f"❌ Lỗi: {error_count}\n"
            if skipped_count > 0:
                results_text += f"⏭️ Bỏ qua: {skipped_count}\n"
            
            results_label = tk.Label(
                results_frame,
                text=results_text,
                font=("Arial", 11),
                justify=tk.LEFT,
                bg="white"
            )
            results_label.pack()
            
            # Output directory info
            output_path = self.output_var.get()
            if output_path and success_count > 0:
                path_label = tk.Label(
                    results_frame,
                    text=f"\n📁 Thư mục: {output_path}",
                    font=("Arial", 9),
                    fg="gray",
                    bg="white",
                    justify=tk.LEFT,
                    wraplength=380
                )
                path_label.pack()
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Open folder button (only if there are successful downloads)
            if success_count > 0:
                def open_and_close():
                    self._open_output_directory()
                    dialog.destroy()
                
                open_folder_btn = ttk.Button(
                    buttons_frame,
                    text="📂 Mở thư mục",
                    command=open_and_close,
                    width=15,
                    style='Primary.TButton'
                )
                open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            # Close button
            close_btn = ttk.Button(
                buttons_frame,
                text="Đóng",
                command=dialog.destroy,
                width=12,
                style='Secondary.TButton'
            )
            close_btn.pack(side=tk.RIGHT)
            
            # Focus on close button
            close_btn.focus_set()
            
            # Handle Enter key and Escape key
            dialog.bind('<Return>', lambda e: dialog.destroy())
            dialog.bind('<Escape>', lambda e: dialog.destroy())
            
        except Exception as e:
            self._log('error', f"Error showing download result popup: {e}")
            # Fallback to simple messagebox
            if success_count > 0 and error_count == 0:
                messagebox.showinfo("Thành công", f"Đã lấy thành công {success_count} mã vạch!")
            elif success_count > 0 and error_count > 0:
                messagebox.showwarning("Hoàn thành một phần", f"Thành công: {success_count}, Lỗi: {error_count}")
            else:
                messagebox.showerror("Thất bại", f"Không thể lấy mã vạch. Lỗi: {error_count}")
    
    def cancel_operation(self) -> None:
        """Cancel ongoing preview operation"""
        try:
            self._log('info', "Cancelling operation")
            
            # Signal cancellation to preview manager
            self.preview_manager.cancel_preview()
            
            # Update UI to show cancellation
            if not self._hide_preview_section and hasattr(self, 'preview_status_label'):
                self.preview_status_label.config(
                    text="Đã hủy xem trước",
                    foreground="orange"
                )
            elif self._external_preview_panel:
                self._external_preview_panel.update_status("Đã hủy xem trước")
                self._external_preview_panel.clear()
            
            # Disable cancel button immediately (if exists)
            if hasattr(self, 'cancel_button') and self.cancel_button:
                self.cancel_button.config(state=tk.DISABLED)
            
            # Return to appropriate state based on whether we have companies
            if self.company_combo['values'] and len(self.company_combo['values']) > 1:
                self._set_state("companies_loaded")
            else:
                self._set_state("initial")
            
        except Exception as e:
            self._log('error', f"Cancel failed: {e}", exc_info=True)
    
    def stop_download(self) -> None:
        """Stop ongoing download operation"""
        try:
            self._log('info', "Stopping download")
            
            # Set stop flag
            self.stop_download_flag = True
            
            # Update UI
            self.stop_button.config(state=tk.DISABLED)
            self.progress_label.config(
                text="Đang dừng...",
                foreground="orange"
            )
            
            self._log('info', "Stop flag set, waiting for current declaration to complete")
            
        except Exception as e:
            self._log('error', f"Stop failed: {e}", exc_info=True)
    
    def export_error_log(self) -> None:
        """
        Export error log from current session to a text file.
        
        Opens a file save dialog and exports all error entries from the current
        session to the selected file.
        
        Requirements: 1.1, 1.3, 1.4
        """
        from tkinter import filedialog
        
        try:
            # Check if there are any errors to export (Requirement 1.4)
            if not self._error_log_exporter.has_errors():
                messagebox.showinfo(
                    "Thông báo",
                    "Không có lỗi để xuất"
                )
                return
            
            # Get default filename
            default_filename = self._error_log_exporter.get_default_filename()
            
            # Open file save dialog (Requirement 1.3)
            filepath = filedialog.asksaveasfilename(
                title="Xuất log lỗi",
                defaultextension=".txt",
                initialfile=default_filename,
                filetypes=[
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if not filepath:
                # User cancelled
                return
            
            # Export to file (Requirements 1.1, 1.2)
            success = self._error_log_exporter.export_to_file(filepath)
            
            if success:
                self._log('info', f"Exported error log to {filepath}")
                messagebox.showinfo(
                    "Thành công",
                    f"Đã xuất {self._error_log_exporter.get_error_count()} lỗi ra file:\n{filepath}"
                )
            else:
                self._log('error', f"Failed to export error log to {filepath}")
                messagebox.showerror(
                    "Lỗi",
                    f"Không thể xuất log lỗi ra file:\n{filepath}"
                )
                
        except Exception as e:
            self._log('error', f"Export error log failed: {e}", exc_info=True)
            messagebox.showerror(
                "Lỗi",
                f"Lỗi khi xuất log:\n{str(e)}"
            )
    
    def retry_failed_downloads(self) -> None:
        """
        Retry download for all failed declarations in the current batch.
        
        Requirements: 4.2, 4.3
        """
        try:
            # Get failed declarations from controller or external preview panel
            failed_declaration_numbers = []
            if self._hide_preview_section and self._external_preview_panel:
                # Get from external preview panel (two-column layout)
                failed_declaration_numbers = self._external_preview_panel.get_failed_declarations()
            elif hasattr(self, '_preview_table_controller'):
                # Get from internal controller (single-column layout)
                failed_declaration_numbers = self._preview_table_controller.get_failed_declarations()
            
            if not failed_declaration_numbers:
                messagebox.showinfo(
                    "Thông báo",
                    "Không có tờ khai thất bại để tải lại"
                )
                return
            
            # Find the Declaration objects for failed declarations
            failed_declarations = []
            for decl in self.preview_manager._all_declarations:
                if decl.declaration_number in failed_declaration_numbers:
                    failed_declarations.append(decl)
            
            if not failed_declarations:
                messagebox.showinfo(
                    "Thông báo",
                    "Không tìm thấy tờ khai thất bại để tải lại"
                )
                return
            
            # Check if required dependencies are available
            if not self.barcode_retriever or not self.file_manager or not self.tracking_db:
                self._log('error', "Missing required dependencies for retry download")
                messagebox.showerror(
                    "Lỗi cấu hình",
                    "Thiếu các thành phần cần thiết để tải mã vạch"
                )
                return
            
            # Confirm retry
            confirm = messagebox.askyesno(
                "Xác nhận",
                f"Bạn có muốn tải lại {len(failed_declarations)} tờ khai thất bại?"
            )
            
            if not confirm:
                return
            
            self._log('info', f"Retrying download for {len(failed_declarations)} failed declarations")
            
            # Reset stop flag
            self.stop_download_flag = False
            
            # Set state to downloading
            self._set_state("downloading")
            
            # Run retry in background thread
            def retry_in_thread():
                success_count = 0
                error_count = 0
                total = len(failed_declarations)
                
                try:
                    for i, declaration in enumerate(failed_declarations):
                        # Check stop flag
                        if self.stop_download_flag:
                            self._log('info', f"Retry stopped by user at {i}/{total}")
                            break
                        
                        # Update progress
                        progress = int((i / total) * 100)
                        self.after(0, lambda p=progress, idx=i, t=total: self._update_progress(p, idx, t))
                        
                        try:
                            self._log('info', f"Retrying declaration {i+1}/{total}: {declaration.id}")
                            
                            # Update file_manager output directory
                            self.file_manager.output_directory = self.output_var.get()
                            
                            # Retrieve barcode
                            pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
                            
                            if pdf_content:
                                # Save to file
                                file_path = self.file_manager.save_barcode(
                                    declaration,
                                    pdf_content,
                                    overwrite=True
                                )
                                
                                if file_path:
                                    # Track in database
                                    self.tracking_db.add_processed(declaration, file_path)
                                    
                                    success_count += 1
                                    self._log('info', f"Retry successful for {declaration.id}")
                                    
                                    # Update result column (Requirements 4.3)
                                    self.after(0, lambda dn=declaration.declaration_number, fp=file_path: 
                                        self._update_download_result(dn, True, file_path=fp))
                                else:
                                    error_count += 1
                                    retry_error = 'File could not be saved on retry'
                                    self.after(0, lambda dn=declaration.declaration_number, em=retry_error: 
                                        self._update_download_result(dn, False, error_message=em))
                            else:
                                error_count += 1
                                retry_error = 'Failed to retrieve barcode on retry'
                                self.after(0, lambda dn=declaration.declaration_number, em=retry_error: 
                                    self._update_download_result(dn, False, error_message=em))
                        
                        except Exception as e:
                            error_count += 1
                            self._log('error', f"Retry error for {declaration.id}: {e}", exc_info=True)
                            self.after(0, lambda dn=declaration.declaration_number, em=str(e): 
                                self._update_download_result(dn, False, error_message=em))
                    
                    # Update final progress
                    self.after(0, lambda: self._update_progress(100, total, total))
                    
                    # Show summary
                    summary_msg = f"Kết quả tải lại:\n\n"
                    summary_msg += f"Thành công: {success_count}/{total}\n"
                    if error_count > 0:
                        summary_msg += f"Vẫn thất bại: {error_count}\n"
                    
                    self.after(0, lambda: messagebox.showinfo("Hoàn thành", summary_msg))
                    if not self._hide_preview_section and hasattr(self, 'preview_status_label'):
                        self.after(0, lambda: self.preview_status_label.config(
                            text=f"Tải lại hoàn thành: {success_count}/{total} thành công",
                            foreground="green" if error_count == 0 else "orange"
                        ))
                    elif self._external_preview_panel:
                        self.after(0, lambda: self._external_preview_panel.update_status(
                            f"Tải lại hoàn thành: {success_count}/{total} thành công"))
                    
                    self._log('info', f"Retry completed: {success_count} success, {error_count} still failed")
                    
                    # Call download complete callback
                    if self.on_download_complete:
                        self.after(0, lambda sc=success_count, ec=error_count: 
                            self.on_download_complete(sc, ec))
                
                except Exception as e:
                    self._log('error', f"Retry thread failed: {e}", exc_info=True)
                    self.after(0, lambda: messagebox.showerror(
                        "Lỗi",
                        f"Lỗi trong quá trình tải lại:\n{str(e)}"
                    ))
                finally:
                    # Reset state
                    self.after(0, lambda: self._set_state("complete"))
                    self.is_operation_running = False
            
            # Start retry thread
            self.is_operation_running = True
            retry_thread = threading.Thread(target=retry_in_thread, daemon=True)
            retry_thread.start()
        
        except Exception as e:
            self._log('error', f"Retry failed downloads failed: {e}", exc_info=True)
            messagebox.showerror(
                "Lỗi",
                f"Không thể tải lại:\n{str(e)}"
            )
            self._set_state("preview_displayed")
    
    def _record_error(self, declaration_number: str, error_type: str, error_message: str) -> None:
        """
        Record an error entry for the current session and persist to database.
        
        Args:
            declaration_number: The declaration number associated with the error
            error_type: Category of error (e.g., 'api_error', 'network_error')
            error_message: Detailed error message
            
        Requirements: 1.1, 1.2, 4.4
        """
        # Record in session error log (for export functionality)
        self._error_log_exporter.add_error_from_values(
            declaration_number=declaration_number,
            error_type=error_type,
            error_message=error_message
        )
        
        # Persist to database via ErrorTracker (Requirements 4.4)
        if self._error_tracker is not None:
            try:
                self._error_tracker.record_error(
                    declaration_number=declaration_number,
                    error_type=error_type,
                    message=error_message
                )
                self._log('debug', f"Persisted error to database for {declaration_number}: {error_type}")
            except Exception as e:
                self._log('warning', f"Failed to persist error to database: {e}")
        
        self._log('debug', f"Recorded error for {declaration_number}: {error_type}")
    
    def clear_session_errors(self) -> None:
        """
        Clear all error entries from the current session.
        
        Called when starting a new download batch.
        """
        self._error_log_exporter.clear()
        self._log('debug', "Cleared session errors")
    
    def toggle_select_all(self) -> None:
        """Toggle select all checkboxes - only affects visible (filtered) declarations"""
        # Skip if preview section is hidden (using external preview panel)
        if self._hide_preview_section:
            # Delegate to external preview panel if available
            # Use _update_select_all_ui to avoid recursion (don't call _on_select_all_change)
            if self._external_preview_panel:
                select_all = self._external_preview_panel._select_all_var.get()
                self._external_preview_panel._update_select_all_ui(select_all)
            return
            
        select_all = self.select_all_var.get()
        
        if select_all:
            # Only select declarations that are currently visible in the tree view
            self._select_visible_declarations()
            self._update_all_checkboxes(True)
        else:
            # Deselect only visible declarations
            self._deselect_visible_declarations()
            self._update_all_checkboxes(False)
        
        self._update_selection_count()
    
    def _select_visible_declarations(self) -> None:
        """Select only declarations that are currently visible in the tree view"""
        # Skip if preview section is hidden
        if self._hide_preview_section:
            return
            
        # Get all declaration numbers from the tree view (visible items)
        visible_declaration_numbers = set()
        for item in self.preview_tree.get_children():
            values = self.preview_tree.item(item, "values")
            if len(values) > 2:
                declaration_number = values[2]  # Column 2 is declaration_number (after STT and checkbox)
                visible_declaration_numbers.add(declaration_number)
        
        # Select only declarations that are visible
        for decl in self.preview_manager._all_declarations:
            if decl.declaration_number in visible_declaration_numbers:
                self.preview_manager._selected_declarations.add(decl.id)
        
        self._log('debug', f"Selected {len(visible_declaration_numbers)} visible declarations")
    
    def _deselect_visible_declarations(self) -> None:
        """Deselect only declarations that are currently visible in the tree view"""
        # Skip if preview section is hidden
        if self._hide_preview_section:
            return
            
        # Get all declaration numbers from the tree view (visible items)
        visible_declaration_numbers = set()
        for item in self.preview_tree.get_children():
            values = self.preview_tree.item(item, "values")
            if len(values) > 2:
                declaration_number = values[2]  # Column 2 is declaration_number (after STT and checkbox)
                visible_declaration_numbers.add(declaration_number)
        
        # Deselect only declarations that are visible
        for decl in self.preview_manager._all_declarations:
            if decl.declaration_number in visible_declaration_numbers:
                self.preview_manager._selected_declarations.discard(decl.id)
        
        self._log('debug', f"Deselected {len(visible_declaration_numbers)} visible declarations")
    
    def _on_include_pending_changed(self) -> None:
        """Handle include pending checkbox change - refresh preview if data exists"""
        # If there's already preview data, refresh it with new filter
        if self.preview_manager._all_declarations:
            self.preview_declarations()
    
    def _on_exclude_xnktc_changed(self) -> None:
        """
        Handle exclude XNK TC checkbox change - refresh preview if data exists
        
        Requirements: 1.5 - WHEN the user toggles the filter checkbox THEN the System 
        SHALL refresh the preview table to reflect the new filter state
        """
        # If there's already preview data, refresh it with new filter
        if self.preview_manager._all_declarations:
            self.preview_declarations()
    
    def _on_filter_changed(self, event=None) -> None:
        """
        Handle filter dropdown change.
        
        Requirements: 3.1, 3.2
        """
        filter_text = self.filter_var.get()
        
        # Map Vietnamese filter names to FilterStatus values
        filter_map = {
            "Tất cả": "all",
            "Thành công": "success",
            "Thất bại": "failed",
            "Chưa xử lý": "pending"
        }
        
        filter_value = filter_map.get(filter_text, "all")
        
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.set_filter(filter_value)
            self._update_selection_count()
            self._log('info', f"Filter changed to: {filter_text}")
    
    def _on_controller_filter_change(self, filter_status: FilterStatus) -> None:
        """
        Callback when PreviewTableController filter changes.
        
        Args:
            filter_status: New filter status
        """
        self._log('debug', f"Controller filter changed to: {filter_status.value}")
    
    def _on_controller_sort_change(self, column: str, is_descending: bool) -> None:
        """
        Callback when PreviewTableController sort changes.
        
        Args:
            column: Column being sorted
            is_descending: True if descending order
        """
        self._log('debug', f"Controller sort changed: {column} {'DESC' if is_descending else 'ASC'}")
        # Update column header visual indicator
        self._update_sort_indicator(column, is_descending)
    
    def _on_column_header_click(self, column: str) -> None:
        """
        Handle column header click for sorting.
        
        Args:
            column: Column name that was clicked
            
        Requirements: 3.3, 3.4
        """
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.toggle_sort(column)
            self._update_selection_count()
            self._log('info', f"Sort toggled on column: {column}")
    
    def _update_sort_indicator(self, sorted_column: str, is_descending: bool) -> None:
        """
        Update column header text to show sort direction indicator.
        
        Args:
            sorted_column: Column currently being sorted
            is_descending: True if descending order
            
        Requirements: 3.3, 3.4
        """
        if not hasattr(self, '_column_headings'):
            return
        
        # Skip if preview section is hidden
        if self._hide_preview_section:
            return
        
        # Sort indicators
        asc_indicator = " ▲"
        desc_indicator = " ▼"
        
        # Update all column headings
        for col, original_text in self._column_headings.items():
            if col == sorted_column:
                # Add sort indicator
                indicator = desc_indicator if is_descending else asc_indicator
                self.preview_tree.heading(col, text=original_text + indicator)
            else:
                # Reset to original text (no indicator)
                self.preview_tree.heading(col, text=original_text)
    
    def _on_tree_double_click(self, event) -> None:
        """
        Handle double-click on tree row to open PDF file.
        
        Requirements: 3.5, 3.6
        """
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.on_double_click(event)
    
    def _on_tree_click(self, event) -> None:
        """Handle tree click for checkbox toggle"""
        region = self.preview_tree.identify_region(event.x, event.y)
        
        if region == "cell":
            column = self.preview_tree.identify_column(event.x)
            
            # Check if clicked on checkbox column
            if column == "#2":  # Second column (checkbox) - STT is #1
                item = self.preview_tree.identify_row(event.y)
                if item:
                    # Toggle checkbox
                    current_value = self.preview_tree.item(item, "values")[1]  # Index 1 for checkbox
                    new_value = "☐" if current_value == "☑" else "☑"
                    
                    # Update tree
                    values = list(self.preview_tree.item(item, "values"))
                    values[1] = new_value  # Index 1 for checkbox
                    self.preview_tree.item(item, values=values)
                    
                    # Find the declaration by number and get its ID
                    declaration_number = values[2]  # Index 2 for declaration_number
                    declaration_id = self._get_declaration_id_by_number(declaration_number)
                    
                    if declaration_id:
                        # Update selection in preview manager
                        self.preview_manager.toggle_selection(declaration_id)
                        
                        # Update selection count
                        self._update_selection_count()
    
    def _on_tree_hover(self, event) -> None:
        """Handle tree hover for row highlighting and tooltip (Requirements 4.1, 4.8)"""
        item = self.preview_tree.identify_row(event.y)
        
        if item and item != self._last_hover_item:
            # Remove hover from previous item
            if self._last_hover_item:
                self._restore_row_tag(self._last_hover_item)
            
            # Apply hover to current item
            self.preview_tree.item(item, tags=('hover',))
            self._last_hover_item = item
            
            # Show tooltip for failed rows (Requirement 4.1)
            self._show_error_tooltip(item, event)
        elif item:
            # Update tooltip position if still on same item
            self._update_tooltip_position(event)
    
    def _on_tree_leave(self, event) -> None:
        """Handle tree leave to remove hover highlighting and tooltip"""
        if self._last_hover_item:
            self._restore_row_tag(self._last_hover_item)
            self._last_hover_item = None
        
        # Hide tooltip
        self._hide_error_tooltip()
    
    def _show_error_tooltip(self, item: str, event) -> None:
        """
        Show tooltip with error message for failed rows.
        
        Args:
            item: Tree item ID
            event: Mouse event
            
        Requirements: 4.1
        """
        # Get values for this row
        values = self.preview_tree.item(item, "values")
        if not values or len(values) <= 9:
            self._hide_error_tooltip()
            return
        
        result = values[9]  # Result column
        declaration_number = values[2]  # Declaration number
        
        # Only show tooltip for failed rows
        if result != "✘":
            self._hide_error_tooltip()
            return
        
        # Get error message from controller
        error_message = None
        if hasattr(self, '_preview_table_controller'):
            error_message = self._preview_table_controller.get_error_message(declaration_number)
        
        if not error_message:
            error_message = "Lỗi không xác định"
        
        # Create or update tooltip
        if not hasattr(self, '_tooltip_window') or self._tooltip_window is None:
            self._tooltip_window = tk.Toplevel(self)
            self._tooltip_window.wm_overrideredirect(True)
            self._tooltip_window.wm_attributes("-topmost", True)
            
            # Tooltip frame with border
            tooltip_frame = ttk.Frame(self._tooltip_window, relief="solid", borderwidth=1)
            tooltip_frame.pack(fill=tk.BOTH, expand=True)
            
            # Tooltip label
            self._tooltip_label = ttk.Label(
                tooltip_frame,
                text="",
                background="#ffffe0",  # Light yellow
                foreground="#333333",
                padding=(8, 4),
                wraplength=300
            )
            self._tooltip_label.pack()
        
        # Update tooltip text
        self._tooltip_label.config(text=f"Lỗi: {error_message}")
        
        # Position tooltip near cursor
        x = event.x_root + 15
        y = event.y_root + 10
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        self._tooltip_window.deiconify()
    
    def _update_tooltip_position(self, event) -> None:
        """Update tooltip position as mouse moves"""
        if hasattr(self, '_tooltip_window') and self._tooltip_window is not None:
            try:
                if self._tooltip_window.winfo_viewable():
                    x = event.x_root + 15
                    y = event.y_root + 10
                    self._tooltip_window.wm_geometry(f"+{x}+{y}")
            except tk.TclError:
                pass
    
    def _hide_error_tooltip(self) -> None:
        """Hide the error tooltip"""
        if hasattr(self, '_tooltip_window') and self._tooltip_window is not None:
            try:
                self._tooltip_window.withdraw()
            except tk.TclError:
                pass
    
    def _restore_row_tag(self, item: str) -> None:
        """Restore the original row tag (oddrow/evenrow) after hover"""
        try:
            # Get the index of the item
            children = self.preview_tree.get_children()
            if item in children:
                index = children.index(item)
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.preview_tree.item(item, tags=(tag,))
        except (ValueError, tk.TclError):
            pass
    
    def _add_company_to_selection(self) -> None:
        """
        Add currently selected company from dropdown to tag picker (v1.5.0).
        
        Called when user clicks the "+ Thêm" button.
        """
        selected = self.company_var.get().strip()
        
        if not selected or selected == 'Tất cả công ty':
            messagebox.showinfo("Thông báo", "Vui lòng chọn một công ty cụ thể để thêm.")
            return
        
        # Add to tag picker
        if hasattr(self, 'company_tag_picker'):
            if self.company_tag_picker.add_company(selected):
                # Successfully added - clear search box
                self.company_combo.set('')
                self._log('info', f"Added company to selection: {selected}")
    
    def _on_multi_select_changed(self, selected_companies: List[str]) -> None:
        """
        Handle multi-select company list change (v1.5.0).
        
        Args:
            selected_companies: List of selected tax codes
        """
        self._log('info', f"Multi-select changed: {len(selected_companies)} companies selected")
        # The selected companies will be used when preview_declarations is called
        # For now, just log the change
    
    # Helper Methods
    
    def _populate_company_dropdown(self, companies: List[tuple]) -> None:
        """Populate company dropdown with companies using AutocompleteCombobox"""
        company_list = ['Tất cả công ty']
        
        # v1.5.0: Extract tax codes for multi-select
        tax_codes = []
        
        for tax_code, company_name in companies:
            # Format: "Mã số thuế - Tên Công Ty"
            company_list.append(f"{tax_code} - {company_name}")
            tax_codes.append(tax_code)
        
        # Store all companies for filtering
        self.all_companies = company_list
        
        # Update SmartCompanySearchLogic with companies (Requirements 3.1, 3.2, 3.3)
        self._smart_search.set_companies(companies)
        
        # Update AutocompleteCombobox values
        self.company_combo.set_values(company_list)
        
        # v1.5.0: CompanyTagPicker manages its own state via preferences
        # No need to populate - it loads saved selection from preferences
        
        # Keep current selection if still valid
        current = self.company_var.get()
        if current not in company_list:
            self.company_combo.set('Tất cả công ty')
    
    def _on_company_selected(self, selected: str) -> None:
        """
        Callback when company is selected from AutocompleteCombobox.
        
        Args:
            selected: Selected company string
        """
        self._log('info', f"Company selected: {selected}")
        # Clear result count when selection is made
        if hasattr(self, 'company_result_count_label'):
            self.company_result_count_label.config(text="")
    
    def _on_company_filter(self, count: int, has_matches: bool) -> None:
        """
        Callback when company filter completes.
        
        Updates the result count label with filter results.
        
        Args:
            count: Number of matching companies
            has_matches: True if there are matches
            
        Search UX Improvement - Requirements 3.1, 3.2
        """
        if hasattr(self, 'company_result_count_label'):
            if has_matches:
                if count == 0:
                    text = ""
                elif count == 1:
                    text = "Tìm thấy 1 công ty"
                else:
                    text = f"Tìm thấy {count} công ty"
            else:
                text = "Không tìm thấy kết quả"
            
            self.company_result_count_label.config(text=text)
    
    # _filter_companies removed - AutocompleteCombobox handles filtering internally
    
    def _clear_company_search(self) -> None:
        """
        Clear search input and restore full company list using AutocompleteCombobox
        
        Validates: Requirements 3.5
        Search UX Improvement - Requirements 6.2
        """
        # Clear SmartCompanySearchLogic selection
        self._smart_search.clear_selection()
        
        # Clear AutocompleteCombobox and restore all values using new method
        self.company_combo.clear_and_reset()
        self.company_combo.set('Tất cả công ty')
        
        # Clear result count label
        if hasattr(self, 'company_result_count_label'):
            self.company_result_count_label.config(text="")
    
    def _load_recent_companies(self) -> None:
        """
        Load recent companies from tracking database.
        
        Requirements: 11.3, 11.4
        """
        try:
            if self.tracking_db:
                recent = self.tracking_db.get_recent_companies(limit=5)
                if recent:
                    self.recent_companies_panel.update_recent(recent)
                    self._log('info', f"Loaded {len(recent)} recent companies")
        except Exception as e:
            self._log('warning', f"Failed to load recent companies: {e}")
    
    def _on_recent_company_selected(self, tax_code: str) -> None:
        """
        Handle selection from recent companies panel.
        
        Args:
            tax_code: Selected tax code
            
        Requirements: 11.2
        """
        # Find company in dropdown by tax code
        for value in self.all_companies:
            if tax_code in value:
                self.company_combo.set(value)
                self._log('info', f"Selected recent company: {tax_code}")
                return
        
        # If not found, set search text and filter
        self.company_combo.set(tax_code)
        self.company_combo._filter_values(tax_code)
    
    def _save_recent_company(self, tax_code: str) -> None:
        """
        Save company to recent list after successful download.
        
        Args:
            tax_code: Tax code to save
            
        Requirements: 11.3
        """
        try:
            if self.tracking_db and tax_code:
                self.tracking_db.save_recent_company(tax_code)
                # Refresh recent companies panel
                self._load_recent_companies()
                self._log('info', f"Saved recent company: {tax_code}")
        except Exception as e:
            self._log('warning', f"Failed to save recent company: {e}")
    
    def _populate_preview_table(self, declarations: List[Declaration]) -> None:
        """Populate preview table with declarations and alternating row colors (Requirement 4.8)"""
        # Build items list for both internal and external preview
        preview_items = []
        
        for index, decl in enumerate(declarations):
            # Format date
            try:
                if isinstance(decl.declaration_date, datetime):
                    date_str = decl.declaration_date.strftime("%d/%m/%Y")
                else:
                    date_obj = datetime.strptime(str(decl.declaration_date), "%Y%m%d")
                    date_str = date_obj.strftime("%d/%m/%Y")
            except:
                date_str = str(decl.declaration_date)
            
            # Get status display
            status_display = decl.status_display if hasattr(decl, 'status_display') else ""
            
            # Get other fields with fallback to empty string
            declaration_type = decl.declaration_type if decl.declaration_type else ""
            bill_of_lading = decl.bill_of_lading if decl.bill_of_lading else ""
            invoice_number = decl.invoice_number if decl.invoice_number else ""
            
            preview_items.append({
                'stt': index + 1,
                'checkbox': '☐',
                'declaration_number': decl.declaration_number,
                'tax_code': decl.tax_code,
                'date': date_str,
                'status': status_display,
                'declaration_type': declaration_type,
                'bill_of_lading': bill_of_lading,
                'invoice_number': invoice_number,
                'result': '',
                # Include for Add to Tracking feature
                'customs_office_code': decl.customs_office_code if hasattr(decl, 'customs_office_code') else '',
                'company_name': decl.company_name if hasattr(decl, 'company_name') else ''
            })
        
        # If using external preview panel (two-column layout)
        if self._hide_preview_section and self._external_preview_panel:
            self._external_preview_panel.populate_preview(preview_items)
            return
        
        # Internal preview table (original behavior)
        if not hasattr(self, 'preview_tree') or self.preview_tree is None:
            return
            
        # Clear existing items
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Clear controller data
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.clear()
        
        # Add declarations with alternating row colors
        for index, item_data in enumerate(preview_items):
            # Determine row tag for alternating colors (Requirement 4.8)
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            # Insert into tree with alternating row tag
            self.preview_tree.insert(
                "",
                tk.END,
                values=(
                    item_data['stt'],
                    item_data['checkbox'],
                    item_data['declaration_number'],
                    item_data['tax_code'],
                    item_data['date'],
                    item_data['status'],
                    item_data['declaration_type'],
                    item_data['bill_of_lading'],
                    item_data['invoice_number'],
                    item_data['result']
                ),
                tags=(row_tag,)
            )
        
        # Store items in controller for filtering/sorting
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.store_items(preview_items)
            # Reset filter to "All" (only if filter_var exists)
            if hasattr(self, 'filter_var'):
                self.filter_var.set("Tất cả")
        
        # Update selection count
        self._update_selection_count()
    
    def _update_all_checkboxes(self, selected: bool) -> None:
        """Update all checkboxes in preview table"""
        # Skip if preview section is hidden
        if self._hide_preview_section:
            return
            
        checkbox_value = "☑" if selected else "☐"
        
        for item in self.preview_tree.get_children():
            values = list(self.preview_tree.item(item, "values"))
            values[1] = checkbox_value  # Index 1 because STT is at index 0
            self.preview_tree.item(item, values=values)
    
    def _get_declaration_id_by_number(self, declaration_number: str) -> Optional[str]:
        """
        Get declaration ID by declaration number
        
        Args:
            declaration_number: Declaration number to search for
            
        Returns:
            Declaration ID if found, None otherwise
        """
        for decl in self.preview_manager._all_declarations:
            if decl.declaration_number == declaration_number:
                return decl.id
        return None
    
    def _update_download_result(self, declaration_number: str, success: bool, file_path: str = None, error_message: str = None) -> None:
        """
        Update the result column for a declaration after download.
        
        Args:
            declaration_number: Declaration number to update
            success: True for success (green checkmark), False for failure (red X)
            file_path: Path to downloaded PDF file (for double-click to open)
            error_message: Error message if failed (for tooltip display)
        """
        # Update external preview panel if using two-column layout
        if self._hide_preview_section and self._external_preview_panel:
            result_text = "✔" if success else "✘"
            self._external_preview_panel.update_item_result(declaration_number, result_text, success)
        elif hasattr(self, 'preview_tree') and self.preview_tree:
            # Update internal preview tree
            for item in self.preview_tree.get_children():
                values = list(self.preview_tree.item(item, "values"))
                if len(values) > 2 and values[2] == declaration_number:
                    # Update result column (last column, index 9)
                    # Use larger/bolder Unicode symbols for better visibility
                    values[9] = "✔" if success else "✘"  # Heavy check mark and heavy ballot X
                    self.preview_tree.item(item, values=values)
                    
                    # Apply color tag for result
                    current_tags = list(self.preview_tree.item(item, "tags"))
                    # Remove any existing result tags
                    current_tags = [t for t in current_tags if t not in ('success_result', 'error_result')]
                    # Add new result tag
                    current_tags.append('success_result' if success else 'error_result')
                    self.preview_tree.item(item, tags=current_tags)
                    break
        
        # Update controller data (Requirements 3.5, 3.6, 4.1, 4.2, 4.3)
        if hasattr(self, '_preview_table_controller'):
            self._preview_table_controller.update_result(declaration_number, success)
            if file_path:
                self._preview_table_controller.set_file_path(declaration_number, file_path)
            if error_message:
                self._preview_table_controller.set_error_message(declaration_number, error_message)
    
    def _update_selection_count(self) -> None:
        """Update selection count label - counts only visible declarations"""
        # Skip if preview section is hidden (using external preview panel)
        if self._hide_preview_section:
            return
            
        # Count visible declarations in tree view
        visible_total = len(self.preview_tree.get_children())
        
        # Count selected declarations that are visible
        visible_declaration_numbers = set()
        for item in self.preview_tree.get_children():
            values = self.preview_tree.item(item, "values")
            if len(values) > 2:
                declaration_number = values[2]  # Index 2 for declaration_number (after STT and checkbox)
                visible_declaration_numbers.add(declaration_number)
        
        # Count how many visible declarations are selected
        visible_selected = 0
        for decl in self.preview_manager._all_declarations:
            if decl.declaration_number in visible_declaration_numbers:
                if decl.id in self.preview_manager._selected_declarations:
                    visible_selected += 1
        
        # Check batch limit and show warning if exceeded (Requirements 10.1, 10.2)
        batch_limit_exceeded = False
        if self._batch_limiter and visible_selected > 0:
            is_valid, message = self._batch_limiter.validate_selection(visible_selected)
            if not is_valid:
                batch_limit_exceeded = True
                self.selection_count_label.config(
                    text=f"Đã chọn: {visible_selected}/{visible_total} tờ khai ⚠️ (Giới hạn: {self._batch_limiter.get_limit()})",
                    foreground="red"
                )
            else:
                self.selection_count_label.config(
                    text=f"Đã chọn: {visible_selected}/{visible_total} tờ khai",
                    foreground=""  # Reset to default color
                )
        else:
            self.selection_count_label.config(
                text=f"Đã chọn: {visible_selected}/{visible_total} tờ khai",
                foreground=""  # Reset to default color
            )
        
        # Update "Chọn tất cả" checkbox state based on visible declarations
        if visible_total > 0:
            if visible_selected == visible_total:
                self.select_all_var.set(True)
            elif visible_selected == 0:
                self.select_all_var.set(False)
            # If some but not all are selected, leave the checkbox as-is
        
        # Update download button state based on current workflow state
        if self.current_state == "preview_displayed":
            # Disable download button if batch limit exceeded (Requirements 10.1, 10.2)
            if visible_selected > 0 and not batch_limit_exceeded:
                self.download_button.config(state=tk.NORMAL)
            else:
                self.download_button.config(state=tk.DISABLED)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string in DD/MM/YYYY format"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Định dạng ngày không hợp lệ: {date_str}. Vui lòng sử dụng DD/MM/YYYY")
    
    def _validate_date_format(self, date_string: str) -> bool:
        """
        Validate date format DD/MM/YYYY
        
        Args:
            date_string: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_string, '%d/%m/%Y')
            return True
        except ValueError:
            self._log('error', f"Invalid date format: {date_string}")
            messagebox.showerror(
                "Lỗi",
                f"Ngày không hợp lệ: {date_string}\n"
                "Định dạng đúng: DD/MM/YYYY"
            )
            return False
    
    def _validate_date_range(self, from_date: datetime, to_date: datetime) -> Optional[str]:
        """
        Validate date range
        
        Returns:
            Error message if invalid, None if valid
        """
        # Check if start date is in future
        if from_date > datetime.now():
            return "Ngày bắt đầu không thể ở tương lai"
        
        # Check if end date is before start date
        if to_date < from_date:
            return "Ngày kết thúc không thể trước ngày bắt đầu"
        
        # Check if range exceeds 90 days
        date_diff = (to_date - from_date).days
        if date_diff > 90:
            self.date_validation_label.config(
                text=f"⚠ Cảnh báo: Khoảng thời gian {date_diff} ngày (> 90 ngày)",
                foreground="orange"
            )
        else:
            self.date_validation_label.config(text="")
        
        return None
    
    def _set_state(self, state: str) -> None:
        """
        Set workflow state and update UI accordingly
        
        States:
        - initial: Only scan button enabled
        - companies_loaded: Enable dropdown and dates
        - preview_displayed: Enable download button
        - downloading: Disable inputs, show stop button
        - complete: Re-enable all
        """
        self.current_state = state
        
        # Helper to safely configure button state (handles hide_preview_section mode)
        def safe_config(widget_name: str, **kwargs) -> None:
            widget = getattr(self, widget_name, None)
            if widget is not None:
                widget.config(**kwargs)
        
        if state == "initial":
            # State 1: Initial (only scan button enabled)
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.DISABLED)
            self.company_combo.config(state=tk.DISABLED)
            self.from_date_entry.config(state=tk.DISABLED)
            self.to_date_entry.config(state=tk.DISABLED)
            safe_config('preview_button', state=tk.DISABLED)
            safe_config('download_button', state=tk.DISABLED)
            safe_config('cancel_button', state=tk.DISABLED)
            safe_config('stop_button', state=tk.DISABLED)
            
        elif state == "companies_loaded":
            # State 2: Companies loaded (enable dropdown and dates)
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            # Use NORMAL state to allow typing for autocomplete filtering
            self.company_combo.config(state=tk.NORMAL)
            self.from_date_entry.config(state=tk.NORMAL)
            self.to_date_entry.config(state=tk.NORMAL)
            safe_config('preview_button', state=tk.NORMAL)
            safe_config('download_button', state=tk.DISABLED)
            safe_config('cancel_button', state=tk.DISABLED)
            safe_config('stop_button', state=tk.DISABLED)
            
        elif state == "preview_displayed":
            # State 3: Preview displayed (enable download button)
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            # Use NORMAL state to allow typing for autocomplete filtering
            self.company_combo.config(state=tk.NORMAL)
            self.from_date_entry.config(state=tk.NORMAL)
            self.to_date_entry.config(state=tk.NORMAL)
            safe_config('preview_button', state=tk.NORMAL)
            safe_config('download_button', state=tk.NORMAL)
            safe_config('cancel_button', state=tk.DISABLED)
            safe_config('stop_button', state=tk.DISABLED)
            
        elif state == "downloading":
            # State 4: Downloading (disable inputs, show stop button)
            self.scan_button.config(state=tk.DISABLED)
            self.refresh_button.config(state=tk.DISABLED)
            self.company_combo.config(state=tk.DISABLED)
            self.from_date_entry.config(state=tk.DISABLED)
            self.to_date_entry.config(state=tk.DISABLED)
            safe_config('preview_button', state=tk.DISABLED)
            safe_config('download_button', state=tk.DISABLED)
            safe_config('cancel_button', state=tk.DISABLED)
            safe_config('stop_button', state=tk.NORMAL)
            
        elif state == "complete":
            # State 5: Complete (re-enable all)
            self.scan_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
            # Use NORMAL state to allow typing for autocomplete filtering
            self.company_combo.config(state=tk.NORMAL)
            self.from_date_entry.config(state=tk.NORMAL)
            self.to_date_entry.config(state=tk.NORMAL)
            safe_config('preview_button', state=tk.NORMAL)
            safe_config('download_button', state=tk.NORMAL)
            safe_config('cancel_button', state=tk.DISABLED)
            safe_config('stop_button', state=tk.DISABLED)
    
    def set_download_complete(self) -> None:
        """Called when download operation completes"""
        self._set_state("complete")
        if hasattr(self, 'preview_status_label') and self.preview_status_label:
            self.preview_status_label.config(
                text="Hoàn thành tải mã vạch",
                foreground="green"
            )
        elif self._external_preview_panel:
            self._external_preview_panel.update_status("Hoàn thành tải mã vạch")
    
    def _update_progress(self, progress: int, current: int, total: int) -> None:
        """
        Update progress bar and label
        
        Args:
            progress: Progress percentage (0-100)
            current: Current item number
            total: Total items
        """
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar['value'] = progress
        if hasattr(self, 'progress_label') and self.progress_label:
            self.progress_label.config(
                text=f"Đang xử lý {current}/{total}...",
                foreground="blue"
            )
        
        # Also update external preview panel if available
        if self._external_preview_panel:
            self._external_preview_panel.update_progress(progress, current, total)
            self._external_preview_panel.update_status(f"Đang xử lý {current}/{total}...")
        
    def select_for_retrieval(self, tax_code: str, date: datetime) -> None:
        """
        Programmatically set selection for retrieval.
        
        Args:
            tax_code: Tax code to select
            date: Declaration date
        """
        # 1. Update Company Selection
        if hasattr(self, 'company_tag_picker'):
            self.company_tag_picker.set_selected_companies([tax_code])
            
        # 2. Update Date Range (Date - 1 to Date + 1 to be safe)
        if date:
            start_date = date - timedelta(days=1)
            end_date = date + timedelta(days=1)
            
            if hasattr(self, 'from_date_entry'):
                try:
                    self.from_date_entry.set_date(start_date)
                except:
                    pass
                    
            if hasattr(self, 'to_date_entry'):
                try:
                    self.to_date_entry.set_date(end_date)
                except:
                    pass
                    
        # 3. Log
        self._log('info', f"Prepared retrieval for {tax_code} on {date.strftime('%d/%m/%Y')}")
    def execute_direct_download(self, declarations_data: List[dict]) -> None:
        """
        Execute download directly without manual selection interface (Phase 6).
        
        Args:
            declarations_data: List of dicts with tax_code, declaration_number, date
        """
        if not declarations_data:
            return
            
        self._log('info', f"Executing direct download for {len(declarations_data)} items")
        
        # 1. Update Preview Manager with these items (mocking a "preview" result)
        from models.declaration_models import Declaration
        
        declarations = []
        for data in declarations_data:
            # Create Declaration object
            decl = Declaration(
                 declaration_number=data['declaration_number'],
                 tax_code=data['tax_code'],
                 declaration_date=data['date'],
                 status='P' # Pending
            )
            declarations.append(decl)
            
        self.preview_manager._all_declarations = declarations
        # Select all by default for this flow
        self.preview_manager._selected_declarations = {d.id for d in declarations}
        
        # 2. Update UI to show these "selected" items in Preview Panel
        if self._external_preview_panel:
             # Convert to dict format for populate_preview
             preview_data = []
             for d in declarations:
                 preview_data.append({
                     'declaration_number': d.declaration_number,
                     'tax_code': d.tax_code,
                     'date': d.declaration_date,
                     'status': 'Ready'
                 })
             self._external_preview_panel.populate_preview(preview_data)
             # Auto-select all visual checkboxes
             self._external_preview_panel._on_select_all_change() 
             
        # 3. Trigger download logic
        self.download_selected()
