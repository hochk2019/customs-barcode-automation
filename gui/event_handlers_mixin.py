"""
GUI Event Handlers Mixin v2.0

Extracted from customs_gui.py for GUI decomposition.
Contains all UI event handler methods.
"""

import tkinter as tk
from tkinter import messagebox
import threading
import os
import subprocess
import platform
from datetime import datetime
from typing import List

from models.declaration_models import Declaration, ProcessedDeclaration, WorkflowResult


class EventHandlersMixin:
    """
    Mixin containing all event handlers for CustomsAutomationGUI.
    
    Separates event handling logic from main GUI class.
    Use with: class CustomsAutomationGUI(EventHandlersMixin):
    """
    
    # === Output and Company Section Handlers ===
    
    def _handle_output_path_changed(self, path: str) -> None:
        """Handle output path change from CompactOutputSection."""
        self.config_manager.set_output_path(path)
        if hasattr(self, 'manual_panel'):
            self.manual_panel.set_output_path(path)
    
    def _handle_company_selected(self, tax_code: str) -> None:
        """Handle company selection from CompactCompanySection."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.set_selected_company(tax_code)
    
    def _handle_scan_companies(self) -> None:
        """Handle scan companies button click."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.scan_companies()
    
    def _handle_refresh_companies(self) -> None:
        """Handle refresh companies button click."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.refresh_companies()
    
    # === Preview Panel Handlers ===
    
    def _handle_preview_click(self) -> None:
        """Handle preview button click from PreviewPanel."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.preview_declarations()
    
    def _handle_download_click(self) -> None:
        """Handle download button click from PreviewPanel."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.start_download()
    
    def _handle_cancel_click(self) -> None:
        """Handle cancel button click from PreviewPanel."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.cancel_download()
    
    def _handle_stop_click(self) -> None:
        """Handle stop button click from PreviewPanel."""
        if hasattr(self, 'scheduler'):
            self.scheduler.stop()
    
    def _handle_export_log_click(self) -> None:
        """Handle export log button click from PreviewPanel."""
        if hasattr(self, 'preview_panel'):
            self.preview_panel.export_logs()
    
    def _handle_select_all_change(self, select_all: bool) -> None:
        """Handle select all checkbox change from PreviewPanel."""
        if hasattr(self, 'preview_panel'):
            self.preview_panel.set_select_all(select_all)
    
    def _handle_retry_failed_click(self) -> None:
        """Handle retry failed button click from PreviewPanel."""
        if hasattr(self, 'manual_panel'):
            self.manual_panel.retry_failed()
    
    # === Preference Change Handlers ===
    
    def _handle_include_pending_changed(self, include_pending: bool) -> None:
        """Handle include pending checkbox change from PreviewPanel."""
        from config.user_preferences import user_preferences
        user_preferences.include_pending = include_pending
        if hasattr(self, 'logger'):
            self.logger.info(f"Include pending changed to: {include_pending}")
    
    def _handle_exclude_xnktc_changed(self, exclude_xnktc: bool) -> None:
        """Handle exclude XNK TC checkbox change from PreviewPanel."""
        from config.user_preferences import user_preferences
        user_preferences.exclude_xnktc = exclude_xnktc
        if hasattr(self, 'logger'):
            self.logger.info(f"Exclude XNKTC changed to: {exclude_xnktc}")
    
    # === Tracking Panel Handlers ===
    
    def _handle_check_clearance_click(self) -> None:
        """Handle check clearance button click from PreviewPanel (v1.5.0)."""
        if hasattr(self, 'tracking_panel'):
            self.tracking_panel.check_selected_declarations()
    
    def _handle_check_tracking_declarations(self, declarations) -> None:
        """Handle check selected tracking declarations (v1.5.0)."""
        if hasattr(self, 'clearance_checker'):
            threading.Thread(
                target=self.clearance_checker.check_declarations,
                args=(declarations,),
                daemon=True
            ).start()
    
    def _handle_add_tracking_dialog(self) -> None:
        """Open add tracking declaration dialog (v1.5.0)."""
        if hasattr(self, 'tracking_panel'):
            self.tracking_panel.show_add_dialog()
    
    # === Tree View Event Handlers ===
    
    def _handle_tree_hover(self, event) -> None:
        """Handle hover event on treeview for highlighting."""
        if not hasattr(self, 'declarations_tree'):
            return
            
        item = self.declarations_tree.identify('item', event.x, event.y)
        if item:
            if self._hover_item and self._hover_item != item:
                self._restore_row_tag(self._hover_item)
            if item != self._hover_item:
                self.declarations_tree.tag_configure('hover', background='#3d3d3d')
                self.declarations_tree.item(item, tags=('hover',))
                self._hover_item = item
    
    def _handle_tree_leave(self, event) -> None:
        """Handle leave event on treeview to remove highlighting."""
        if hasattr(self, '_hover_item') and self._hover_item:
            self._restore_row_tag(self._hover_item)
            self._hover_item = None
    
    def _restore_row_tag(self, item: str) -> None:
        """Restore the original alternating row tag for an item."""
        if not hasattr(self, 'declarations_tree'):
            return
            
        try:
            index = self.declarations_tree.index(item)
            tag = 'oddrow' if index % 2 == 0 else 'evenrow'
            self.declarations_tree.item(item, tags=(tag,))
        except Exception:
            pass
