"""
Database Status Controller v2.0

Extracted from customs_gui.py for GUI decomposition.
Handles database connection status checking and UI updates.
"""

import threading
from typing import Callable, Optional
import tkinter as tk

from logging_system.logger import Logger
from database.ecus_connector import EcusDataConnector


class DatabaseStatusController:
    """
    Controller for database connection status.
    """
    
    def __init__(
        self,
        ecus_connector: EcusDataConnector,
        logger: Logger,
        root: tk.Tk,
        on_status_change: Optional[Callable[[bool], None]] = None
    ):
        """
        Initialize controller.
        
        Args:
            ecus_connector: ECUS connector
            logger: Logger instance
            root: Tkinter root for after() calls
            on_status_change: Callback with (is_connected)
        """
        self.ecus_connector = ecus_connector
        self.logger = logger
        self.root = root
        self.on_status_change = on_status_change
        
        self._is_connected = False
    
    def check_connection_async(self) -> None:
        """Check database connection status in background."""
        def check_in_thread():
            try:
                # Test connection
                if self.ecus_connector.is_connected():
                    cursor = self.ecus_connector.connection.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                    is_connected = True
                else:
                    # Try to reconnect
                    result = self.ecus_connector.connect()
                    is_connected = result
                
                self._is_connected = is_connected
                
                if self.on_status_change:
                    self.root.after(0, lambda: self.on_status_change(is_connected))
                    
            except Exception as e:
                self.logger.warning(f"Database connection check failed: {e}")
                self._is_connected = False
                if self.on_status_change:
                    self.root.after(0, lambda: self.on_status_change(False))
        
        threading.Thread(target=check_in_thread, daemon=True).start()
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
