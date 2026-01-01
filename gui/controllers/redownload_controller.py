"""
Redownload Controller v2.0

Handles re-downloading barcodes for selected declarations.
Extracted from customs_gui.py for GUI decomposition.
"""

import threading
from datetime import datetime
from tkinter import messagebox, ttk
import tkinter as tk
from typing import Callable, Optional, List

from models.declaration_models import Declaration, WorkflowResult
from logging_system.logger import Logger


class RedownloadController:
    """
    Controller for re-downloading declarations.
    
    Handles:
    - Building declarations from tree selection
    - Executing re-download in background
    - Updating UI on completion
    """
    
    def __init__(
        self,
        scheduler,
        tracking_db,
        logger: Logger,
        root: tk.Tk,
        on_complete: Optional[Callable[[WorkflowResult], None]] = None,
        on_refresh: Optional[Callable[[], None]] = None
    ):
        """
        Initialize controller.
        
        Args:
            scheduler: Scheduler instance
            tracking_db: Tracking database
            logger: Logger instance
            root: Tkinter root for after() calls
            on_complete: Callback with WorkflowResult
            on_refresh: Callback to refresh declarations list
        """
        self.scheduler = scheduler
        self.tracking_db = tracking_db
        self.logger = logger
        self.root = root
        self.on_complete = on_complete
        self.on_refresh = on_refresh
        
        self._is_running = False
    
    def redownload_selected(
        self,
        tree: ttk.Treeview,
        redownload_button: Optional[ttk.Button] = None,
        append_log: Optional[Callable[[str, str], None]] = None
    ) -> None:
        """
        Re-download barcodes for selected declarations.
        
        Args:
            tree: Treeview with selected declarations
            redownload_button: Button to disable during operation
            append_log: Optional log function
        """
        if self._is_running:
            messagebox.showwarning("Warning", "Re-download already in progress")
            return
        
        def redownload_in_thread():
            try:
                self._is_running = True
                
                # Get selected items
                selected_items = tree.selection()
                
                if not selected_items:
                    self.root.after(0, lambda: messagebox.showwarning("Warning", "No declarations selected"))
                    return
                
                # Build declarations
                declarations = self._build_declarations(tree, selected_items)
                
                if not declarations:
                    return
                
                if append_log:
                    self.root.after(0, lambda: append_log("INFO", f"Re-downloading {len(declarations)} declarations"))
                
                # Disable button
                if redownload_button:
                    self.root.after(0, lambda: redownload_button.config(state=tk.DISABLED))
                
                # Execute re-download
                result = self.scheduler.redownload_declarations(declarations)
                
                # Callbacks
                if self.on_complete:
                    self.root.after(0, lambda: self.on_complete(result))
                
                if redownload_button:
                    self.root.after(0, lambda: redownload_button.config(state=tk.NORMAL))
                
                if self.on_refresh:
                    self.root.after(0, self.on_refresh)
                
                if append_log:
                    self.root.after(0, lambda: append_log("INFO", f"Re-download completed: {result.success_count} successful, {result.error_count} errors"))
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Re-download Complete",
                    f"Re-download completed:\n{result.success_count} successful\n{result.error_count} errors"
                ))
                
            except Exception as e:
                self.logger.error(f"Re-download failed: {e}", exc_info=True)
                self.root.after(0, lambda: messagebox.showerror("Error", f"Re-download failed:\n{str(e)}"))
                if redownload_button:
                    self.root.after(0, lambda: redownload_button.config(state=tk.NORMAL))
            finally:
                self._is_running = False
        
        threading.Thread(target=redownload_in_thread, daemon=True).start()
    
    def _build_declarations(self, tree: ttk.Treeview, selected_items) -> List[Declaration]:
        """Build Declaration objects from tree selection."""
        declarations = []
        
        for item_id in selected_items:
            values = tree.item(item_id, "values")
            if values:
                decl_number = values[0]
                tax_code = values[1]
                date_str = values[2]
                
                # Parse date
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    date_obj = datetime.now()
                
                declaration = Declaration(
                    declaration_number=decl_number,
                    tax_code=tax_code,
                    declaration_date=date_obj,
                    customs_office_code="",
                    transport_method="",
                    channel="",
                    status="T",
                    goods_description=None
                )
                declarations.append(declaration)
        
        return declarations
    
    @property
    def is_running(self) -> bool:
        return self._is_running
