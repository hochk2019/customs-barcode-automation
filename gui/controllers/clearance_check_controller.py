"""
Clearance Check Controller v2.0

Extracted from customs_gui.py for GUI decomposition.
Handles checking clearance status for declarations.
"""

import threading
from datetime import datetime
from tkinter import messagebox
import tkinter as tk
from typing import Callable, Optional, List, Dict

from logging_system.logger import Logger


class ClearanceCheckController:
    """
    Controller for clearance status checking.
    """
    
    def __init__(
        self,
        ecus_connector,
        tracking_db,
        logger: Logger,
        root: tk.Tk,
        on_status_update: Optional[Callable[[str, str], None]] = None
    ):
        """
        Initialize controller.
        
        Args:
            ecus_connector: ECUS connector
            tracking_db: Tracking database
            logger: Logger instance
            root: Tkinter root for after() calls
            on_status_update: Callback with (decl_number, status)
        """
        self.ecus_connector = ecus_connector
        self.tracking_db = tracking_db
        self.logger = logger
        self.root = root
        self.on_status_update = on_status_update
        
        self._is_checking = False
    
    def check_selected_declarations(
        self,
        selected_declarations: List[Dict],
        preview_panel=None
    ) -> None:
        """
        Check clearance status for selected declarations.
        
        Args:
            selected_declarations: List of declaration dicts with decl_number, tax_code, date
            preview_panel: Optional preview panel to update status
        """
        if not selected_declarations:
            messagebox.showinfo("Thông báo", "Vui lòng chọn tờ khai để kiểm tra.")
            return
        
        if self._is_checking:
            messagebox.showwarning("Cảnh báo", "Đang kiểm tra, vui lòng đợi...")
            return
        
        def check_thread():
            self._is_checking = True
            try:
                for decl in selected_declarations:
                    decl_number = decl.get('declaration_number') or decl.get('decl_number')
                    tax_code = decl.get('tax_code')
                    
                    try:
                        # Query ECUS for status
                        status = self.ecus_connector.get_clearance_status(decl_number, tax_code)
                        
                        if status and preview_panel:
                            self.root.after(0, lambda d=decl_number, s=status: 
                                preview_panel.update_clearance_status(d, s))
                        
                        if self.on_status_update:
                            self.root.after(0, lambda d=decl_number, s=status: 
                                self.on_status_update(d, s))
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to check clearance for {decl_number}: {e}")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Hoàn tất", 
                    f"Đã kiểm tra {len(selected_declarations)} tờ khai."
                ))
                
            finally:
                self._is_checking = False
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    @property
    def is_checking(self) -> bool:
        return self._is_checking
