"""
Layout Builders v2.0

Extracted from customs_gui.py for GUI decomposition.
Contains layout creation functions for left and right panes.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any

from gui.compact_status_bar import CompactStatusBar
from gui.compact_output_section import CompactOutputSection
from gui.compact_company_section import CompactCompanySection
from gui.enhanced_manual_panel import EnhancedManualPanel
from gui.statistics_bar import StatisticsBar
from gui.preview_panel import PreviewPanel
from gui.tracking_panel import TrackingPanel
from gui.settings_dialog import SettingsDialog


def create_left_pane_content(
    parent: ttk.Frame,
    dependencies: Dict[str, Any],
    callbacks: Dict[str, Callable]
) -> Dict[str, Any]:
    """
    Create left pane content - Control Panel.
    
    Args:
        parent: Parent frame
        dependencies: Dict containing scheduler, tracking_db, ecus_connector, etc.
        callbacks: Dict of callback functions
        
    Returns:
        Dict of created widgets
    """
    widgets = {}
    
    # Compact Status Bar
    widgets['status_bar'] = CompactStatusBar(
        parent,
        on_settings_click=callbacks.get('on_settings_click'),
        logger=dependencies.get('logger')
    )
    widgets['status_bar'].pack(fill=tk.X, pady=(0, 5))
    
    # Statistics Bar
    widgets['statistics_bar'] = StatisticsBar(parent)
    widgets['statistics_bar'].pack(fill=tk.X, pady=(0, 5))
    
    # Output Section
    widgets['output_section'] = CompactOutputSection(
        parent,
        config_manager=dependencies.get('config_manager'),
        on_path_change=callbacks.get('on_output_path_changed')
    )
    widgets['output_section'].pack(fill=tk.X, pady=(0, 5))
    
    # Company Section
    widgets['company_section'] = CompactCompanySection(
        parent,
        tracking_db=dependencies.get('tracking_db'),
        config_manager=dependencies.get('config_manager'),
        on_company_select=callbacks.get('on_company_selected'),
        on_scan_companies=callbacks.get('on_scan_companies'),
        on_refresh_companies=callbacks.get('on_refresh_companies')
    )
    widgets['company_section'].pack(fill=tk.X, pady=(0, 5))
    
    # Enhanced Manual Panel
    widgets['manual_panel'] = EnhancedManualPanel(
        parent,
        scheduler=dependencies.get('scheduler'),
        tracking_db=dependencies.get('tracking_db'),
        ecus_connector=dependencies.get('ecus_connector'),
        config_manager=dependencies.get('config_manager'),
        logger=dependencies.get('logger'),
        barcode_retriever=dependencies.get('barcode_retriever'),
        file_manager=dependencies.get('file_manager'),
        on_download_complete=callbacks.get('on_download_complete')
    )
    widgets['manual_panel'].pack(fill=tk.BOTH, expand=True)
    
    return widgets


def create_right_pane_content(
    parent: ttk.Frame,
    dependencies: Dict[str, Any],
    callbacks: Dict[str, Callable]
) -> Dict[str, Any]:
    """
    Create right pane content with tabbed interface.
    
    Args:
        parent: Parent frame
        dependencies: Dict containing scheduler, tracking_db, ecus_connector, etc.
        callbacks: Dict of callback functions
        
    Returns:
        Dict of created widgets
    """
    widgets = {}
    
    # Create notebook for tabs
    widgets['notebook'] = ttk.Notebook(parent)
    widgets['notebook'].pack(fill=tk.BOTH, expand=True)
    
    # Preview Panel tab
    preview_frame = ttk.Frame(widgets['notebook'])
    widgets['notebook'].add(preview_frame, text="🔍 Xem trước tờ khai")
    
    widgets['preview_panel'] = PreviewPanel(
        preview_frame,
        tracking_db=dependencies.get('tracking_db'),
        config_manager=dependencies.get('config_manager'),
        on_preview_click=callbacks.get('on_preview_click'),
        on_download_click=callbacks.get('on_download_click'),
        on_cancel_click=callbacks.get('on_cancel_click'),
        on_stop_click=callbacks.get('on_stop_click'),
        on_export_log_click=callbacks.get('on_export_log_click'),
        on_select_all_change=callbacks.get('on_select_all_change'),
        on_retry_failed_click=callbacks.get('on_retry_failed_click'),
        on_include_pending_changed=callbacks.get('on_include_pending_changed'),
        on_exclude_xnktc_changed=callbacks.get('on_exclude_xnktc_changed'),
        on_check_clearance_click=callbacks.get('on_check_clearance_click')
    )
    widgets['preview_panel'].pack(fill=tk.BOTH, expand=True)
    
    # Tracking Panel tab
    tracking_frame = ttk.Frame(widgets['notebook'])
    widgets['notebook'].add(tracking_frame, text="📋 Theo dõi thông quan")
    
    widgets['tracking_panel'] = TrackingPanel(
        tracking_frame,
        tracking_db=dependencies.get('tracking_db'),
        ecus_connector=dependencies.get('ecus_connector'),
        clearance_checker=dependencies.get('clearance_checker'),
        on_check_declarations=callbacks.get('on_check_tracking_declarations'),
        on_add_dialog=callbacks.get('on_add_tracking_dialog')
    )
    widgets['tracking_panel'].pack(fill=tk.BOTH, expand=True)
    
    return widgets
