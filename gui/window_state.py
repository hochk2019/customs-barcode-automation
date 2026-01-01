"""
Window State Manager

This module provides window position and size persistence.

Requirements: 6.1, 6.2, 6.3, 6.4
"""

import tkinter as tk
from dataclasses import dataclass
from typing import Tuple, Optional

from config.configuration_manager import ConfigurationManager


@dataclass
class WindowState:
    """Window position and size state"""
    x: int
    y: int
    width: int
    height: int


class WindowStateManager:
    """
    Manager for window position and size persistence.
    
    Provides:
    - Save window state on close
    - Restore window state on startup
    - Validate position is on visible screen
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    DEFAULT_WIDTH = 1100
    DEFAULT_HEIGHT = 680
    
    def __init__(self, root: tk.Tk, config_manager: ConfigurationManager):
        """
        Initialize WindowStateManager.
        
        Args:
            root: Root Tk window
            config_manager: Configuration manager for persistence
        """
        self.root = root
        self.config_manager = config_manager
    
    def save_state(self) -> None:
        """
        Save current window position and size to config.
        
        Requirements: 6.1
        """
        try:
            # Reload config from disk to prevent overwriting changes from other components 
            # (e.g., UserPreferences which saves in real-time)
            if hasattr(self.config_manager, '_load_config'):
                try:
                    self.config_manager._load_config()
                except Exception:
                    pass

            # Get current geometry
            geometry = self.root.geometry()
            
            # Parse geometry string (WxH+X+Y or WxH-X-Y)
            # Handle both positive and negative positions
            import re
            match = re.match(r'(\d+)x(\d+)([+-]\d+)([+-]\d+)', geometry)
            
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                x = int(match.group(3))
                y = int(match.group(4))
                
                # Save to config
                self.config_manager.set_window_state(x, y, width, height)
                self.config_manager.save()
                
        except Exception:
            pass  # Silently ignore save errors
    
    def restore_state(self) -> None:
        """
        Restore window position and size from config.
        
        Requirements: 6.2, 6.3, 6.4
        """
        try:
            # Get saved state
            x = self.config_manager.get_window_x()
            y = self.config_manager.get_window_y()
            width = self.config_manager.get_window_width()
            height = self.config_manager.get_window_height()
            
            # Use defaults if not set (Requirement 6.4)
            if width <= 0:
                width = self.DEFAULT_WIDTH
            if height <= 0:
                height = self.DEFAULT_HEIGHT
            
            # Check if position is valid (Requirement 6.3)
            if x == -1 or y == -1 or not self.is_position_valid(x, y, width, height):
                # Center on screen
                x, y = self.get_centered_position(width, height)
            
            # Apply geometry
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception:
            # Fall back to defaults
            self._apply_default_geometry()
    
    def is_position_valid(self, x: int, y: int, width: int = 100, height: int = 100) -> bool:
        """
        Check if position is on a visible screen.
        
        Args:
            x: X position
            y: Y position
            width: Window width (for checking if at least part is visible)
            height: Window height
            
        Returns:
            True if position is valid (at least partially visible)
            
        Requirements: 6.3
        """
        try:
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Check if at least part of window is visible
            # Allow some margin for taskbar etc.
            min_visible = 100
            
            # Window should have at least min_visible pixels on screen
            if x + width < min_visible:
                return False
            if y + height < min_visible:
                return False
            if x > screen_width - min_visible:
                return False
            if y > screen_height - min_visible:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_centered_position(self, width: int = None, height: int = None) -> Tuple[int, int]:
        """
        Get centered position for window.
        
        Args:
            width: Window width (uses default if not specified)
            height: Window height (uses default if not specified)
            
        Returns:
            Tuple of (x, y) for centered position
            
        Requirements: 6.4
        """
        if width is None:
            width = self.DEFAULT_WIDTH
        if height is None:
            height = self.DEFAULT_HEIGHT
        
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            # Ensure non-negative
            x = max(0, x)
            y = max(0, y)
            
            return x, y
            
        except Exception:
            return 0, 0
    
    def _apply_default_geometry(self) -> None:
        """Apply default window geometry (centered, default size)"""
        x, y = self.get_centered_position()
        self.root.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}+{x}+{y}")
    
    def get_current_state(self) -> WindowState:
        """
        Get current window state.
        
        Returns:
            WindowState with current position and size
        """
        try:
            geometry = self.root.geometry()
            import re
            match = re.match(r'(\d+)x(\d+)([+-]\d+)([+-]\d+)', geometry)
            
            if match:
                return WindowState(
                    x=int(match.group(3)),
                    y=int(match.group(4)),
                    width=int(match.group(1)),
                    height=int(match.group(2))
                )
        except Exception:
            pass
        
        return WindowState(
            x=0, y=0,
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT
        )
