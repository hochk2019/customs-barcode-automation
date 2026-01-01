"""
Download Controller v2.0

Handles declaration download operations.
Extracted from customs_gui.py for GUI decomposition.
"""

import threading
from typing import Optional, Callable, List
from tkinter import messagebox

from models.declaration_models import Declaration, WorkflowResult
from services.workflow_service import WorkflowService
from database.tracking_database import TrackingDatabase
from logging_system.logger import Logger


class DownloadController:
    """
    Controller for download operations.
    
    Handles:
    - Redownload selected declarations
    - Download progress callbacks
    - Error handling
    """
    
    def __init__(
        self,
        workflow_service: WorkflowService,
        tracking_db: TrackingDatabase,
        logger: Logger,
        on_complete: Optional[Callable[[int, int], None]] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Initialize download controller.
        
        Args:
            workflow_service: WorkflowService instance
            tracking_db: Tracking database
            logger: Logger instance
            on_complete: Callback(success_count, error_count)
            on_progress: Callback(current, total, status)
        """
        self.workflow_service = workflow_service
        self.tracking_db = tracking_db
        self.logger = logger
        self.on_complete = on_complete
        self.on_progress = on_progress
        
        self._is_downloading = False
    
    def redownload_declarations(
        self,
        declarations: List[Declaration],
        force: bool = True
    ) -> None:
        """
        Redownload declarations in background thread.
        
        Args:
            declarations: List of declarations to download
            force: Force redownload even if exists
        """
        if self._is_downloading:
            messagebox.showwarning("Đang xử lý", "Đang có tác vụ tải xuống đang chạy.")
            return
        
        if not declarations:
            messagebox.showinfo("Thông báo", "Vui lòng chọn ít nhất một tờ khai để tải lại.")
            return
        
        self._is_downloading = True
        
        def download_thread():
            try:
                # Track progress via events
                if self.on_progress:
                    def event_handler(event):
                        if event.data:
                            current = event.data.get("current", 0)
                            total = event.data.get("total", 0)
                            self.on_progress(current, total, event.message)
                    self.workflow_service.add_event_listener(event_handler)
                
                result = self.workflow_service.execute(
                    declarations=declarations,
                    force_redownload=force
                )
                
                self.logger.info(f"Redownload complete: {result.success_count} success, {result.error_count} errors")
                
                if self.on_complete:
                    self.on_complete(result.success_count, result.error_count)
                    
            except Exception as e:
                self.logger.error(f"Redownload failed: {e}")
                if self.on_complete:
                    self.on_complete(0, len(declarations))
            finally:
                self._is_downloading = False
                if self.on_progress:
                    self.workflow_service.remove_event_listener(event_handler)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def cancel_download(self) -> None:
        """Cancel ongoing download."""
        if self._is_downloading:
            self.workflow_service.cancel()
            self.logger.info("Download cancelled by user")
    
    @property
    def is_downloading(self) -> bool:
        return self._is_downloading
