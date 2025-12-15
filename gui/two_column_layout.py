"""
Two Column Layout Component

This module provides a resizable two-column layout using ttk.PanedWindow.
The left pane contains the Control Panel and the right pane contains the Preview Panel.

Requirements: 1.1, 1.4, 8.1, 8.2, 8.3, 8.4
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from config.configuration_manager import ConfigurationManager


class TwoColumnLayout(ttk.Frame):
    """
    Two-column layout with resizable splitter.
    
    Uses ttk.PanedWindow to create a horizontal split layout with:
    - Left pane (Control Panel): 35-40% width, min 400px
    - Right pane (Preview Panel): 60-65% width, min 500px
    
    The splitter position is saved to config and restored on startup.
    
    Requirements: 1.1, 8.1, 8.2, 8.3, 8.4
    """
    
    # Minimum widths for each pane
    MIN_LEFT_WIDTH = 400
    MIN_RIGHT_WIDTH = 500
    
    # Default split ratio (left pane width / total width)
    DEFAULT_SPLIT_RATIO = 0.38
    
    def __init__(
        self,
        parent: tk.Widget,
        config_manager: Optional[ConfigurationManager] = None,
        **kwargs
    ):
        """
        Initialize TwoColumnLayout.
        
        Args:
            parent: Parent widget
            config_manager: ConfigurationManager for saving/loading split position
            **kwargs: Additional arguments for ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        self.config_manager = config_manager
        self._split_ratio = self.DEFAULT_SPLIT_RATIO
        
        # Create PanedWindow with horizontal orientation
        self.paned_window = ttk.PanedWindow(
            self,
            orient=tk.HORIZONTAL
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create left pane (Control Panel)
        self.left_pane = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_pane, weight=1)
        
        # Create right pane (Preview Panel)
        self.right_pane = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_pane, weight=2)
        
        # Configure minimum sizes (Requirements 1.4, 8.2)
        self._configure_min_sizes()
        
        # Bind sash release to save position (Requirement 8.3)
        self.paned_window.bind('<ButtonRelease-1>', self._on_sash_release)
        
        # Bind configure event to restore position after layout
        self.bind('<Configure>', self._on_configure)
        self._initial_configure_done = False
        
        # Load saved split position (Requirement 8.4)
        self._load_split_position()
    
    def _configure_min_sizes(self) -> None:
        """
        Configure minimum sizes for panes.
        
        Requirements: 1.4, 8.2
        """
        # Note: ttk.PanedWindow doesn't have direct minsize support like tk.PanedWindow
        # We'll enforce minimum sizes in the sash release handler
        pass
    
    def _load_split_position(self) -> None:
        """
        Load saved split position from config.
        
        Requirement: 8.4
        """
        if self.config_manager:
            try:
                self._split_ratio = self.config_manager.get_panel_split_position()
            except Exception:
                self._split_ratio = self.DEFAULT_SPLIT_RATIO
    
    def _on_configure(self, event) -> None:
        """
        Handle configure event to apply split position after initial layout.
        """
        if not self._initial_configure_done and self.winfo_width() > 1:
            self._initial_configure_done = True
            self.after(100, self._apply_split_position)
    
    def _apply_split_position(self) -> None:
        """
        Apply the saved split position to the PanedWindow.
        
        Requirement: 8.4
        """
        total_width = self.winfo_width()
        if total_width <= 1:
            return
        
        # Calculate left pane width from ratio
        left_width = int(total_width * self._split_ratio)
        
        # Enforce minimum widths
        left_width = max(self.MIN_LEFT_WIDTH, left_width)
        left_width = min(total_width - self.MIN_RIGHT_WIDTH, left_width)
        
        # Apply sash position
        try:
            self.paned_window.sashpos(0, left_width)
        except tk.TclError:
            pass  # Sash may not exist yet
    
    def _on_sash_release(self, event) -> None:
        """
        Handle sash release to save position and enforce minimum widths.
        
        Requirement: 8.3
        """
        self.after(10, self._save_and_enforce_position)
    
    def _save_and_enforce_position(self) -> None:
        """
        Save current sash position and enforce minimum widths.
        
        Requirements: 8.2, 8.3
        """
        total_width = self.winfo_width()
        if total_width <= 1:
            return
        
        try:
            sash_pos = self.paned_window.sashpos(0)
        except tk.TclError:
            return
        
        # Enforce minimum widths (Requirement 8.2)
        if sash_pos < self.MIN_LEFT_WIDTH:
            sash_pos = self.MIN_LEFT_WIDTH
            self.paned_window.sashpos(0, sash_pos)
        elif sash_pos > total_width - self.MIN_RIGHT_WIDTH:
            sash_pos = total_width - self.MIN_RIGHT_WIDTH
            self.paned_window.sashpos(0, sash_pos)
        
        # Calculate and save ratio (Requirement 8.3)
        self._split_ratio = sash_pos / total_width
        
        if self.config_manager:
            try:
                self.config_manager.set_panel_split_position(self._split_ratio)
                self.config_manager._save_config_file()
            except Exception:
                pass  # Silently fail if config save fails
    
    def get_left_pane(self) -> ttk.Frame:
        """
        Get the left pane (Control Panel) frame.
        
        Returns:
            ttk.Frame for the left pane
            
        Requirement: 1.1
        """
        return self.left_pane
    
    def get_right_pane(self) -> ttk.Frame:
        """
        Get the right pane (Preview Panel) frame.
        
        Returns:
            ttk.Frame for the right pane
            
        Requirement: 1.1
        """
        return self.right_pane
    
    def save_split_position(self) -> None:
        """
        Manually save current split position to config.
        
        Requirement: 8.3
        """
        self._save_and_enforce_position()
    
    def restore_split_position(self) -> None:
        """
        Restore split position from config.
        
        Requirement: 8.4
        """
        self._load_split_position()
        self._apply_split_position()
    
    def set_split_ratio(self, ratio: float) -> None:
        """
        Set split ratio programmatically.
        
        Args:
            ratio: Split ratio (0.25 to 0.50 for left pane width)
        """
        # Clamp to valid range
        ratio = max(0.25, min(0.50, ratio))
        self._split_ratio = ratio
        self._apply_split_position()
    
    def get_split_ratio(self) -> float:
        """
        Get current split ratio.
        
        Returns:
            Current split ratio
        """
        total_width = self.winfo_width()
        if total_width <= 1:
            return self._split_ratio
        
        try:
            sash_pos = self.paned_window.sashpos(0)
            return sash_pos / total_width
        except tk.TclError:
            return self._split_ratio
    
    def is_narrow_mode(self) -> bool:
        """
        Check if window is in narrow mode (< 1000px).
        
        Returns:
            True if window width is less than minimum for two-column layout
            
        Requirement: 9.4
        """
        total_width = self.winfo_width()
        return total_width < (self.MIN_LEFT_WIDTH + self.MIN_RIGHT_WIDTH)
    
    def get_minimum_window_size(self) -> tuple:
        """
        Get minimum window size for two-column layout.
        
        Returns:
            Tuple of (min_width, min_height)
            
        Requirement: 9.3
        """
        return (1000, 700)
