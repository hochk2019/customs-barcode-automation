"""
Tracking Controller v2.0

Extracted from customs_gui.py for GUI decomposition.
Handles adding declarations to tracking and related operations.
"""

import threading
from datetime import datetime
from tkinter import messagebox
import tkinter as tk
from typing import Callable, Optional, List, Dict

from logging_system.logger import Logger


class TrackingController:
    """
    Controller for tracking-related operations.
    """
    
    def __init__(
        self,
        tracking_db,
        logger: Logger,
        root: tk.Tk,
        on_complete: Optional[Callable[[int], None]] = None
    ):
        """
        Initialize controller.
        
        Args:
            tracking_db: Tracking database
            logger: Logger instance
            root: Tkinter root for after() calls
            on_complete: Callback with added count
        """
        self.tracking_db = tracking_db
        self.logger = logger
        self.root = root
        self.on_complete = on_complete
    
    def add_to_tracking(
        self,
        selected_declarations: List[Dict],
        tracking_panel=None
    ) -> None:
        """
        Add selected declarations to tracking database.
        
        Args:
            selected_declarations: List of declaration dicts
            tracking_panel: Optional tracking panel to refresh
        """
        if not selected_declarations:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tờ khai để thêm vào theo dõi.")
            return
        
        def add_thread():
            added_count = 0
            for decl in selected_declarations:
                try:
                    decl_number = decl.get('declaration_number') or decl.get('decl_number')
                    tax_code = decl.get('tax_code')
                    decl_date = decl.get('date') or decl.get('declaration_date')
                    
                    if isinstance(decl_date, str):
                        try:
                            decl_date = datetime.strptime(decl_date, "%d/%m/%Y")
                        except:
                            decl_date = datetime.now()
                    
                    # Add to tracking
                    self.tracking_db.add_to_tracking(
                        declaration_number=decl_number,
                        tax_code=tax_code,
                        declaration_date=decl_date
                    )
                    added_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to add {decl.get('declaration_number')}: {e}")
            
            # Refresh tracking panel
            if tracking_panel:
                self.root.after(0, tracking_panel.refresh)
            
            if self.on_complete:
                self.root.after(0, lambda: self.on_complete(added_count))
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Hoàn tất",
                f"Đã thêm {added_count}/{len(selected_declarations)} tờ khai vào danh sách theo dõi."
            ))
        
        threading.Thread(target=add_thread, daemon=True).start()
    
    def download_tracking_declarations(
        self,
        declarations: List[Dict],
        enhanced_manual_panel=None
    ) -> None:
        """
        Trigger download for tracking declarations.
        
        Args:
            declarations: List of declaration dicts
            enhanced_manual_panel: Panel to trigger download
        """
        if not declarations:
            messagebox.showwarning("Cảnh báo", "Không có tờ khai để tải.")
            return
        
        if enhanced_manual_panel:
            # Convert to format expected by panel
            for decl in declarations:
                if 'decl_number' in decl and 'declaration_number' not in decl:
                    decl['declaration_number'] = decl['decl_number']
            
            enhanced_manual_panel.download_specific_declarations(declarations)
