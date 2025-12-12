"""
Keyboard Shortcuts Manager

This module provides keyboard shortcut management for the application.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import tkinter as tk
from typing import Dict, Callable, Optional
from dataclasses import dataclass


@dataclass
class ShortcutInfo:
    """Information about a keyboard shortcut"""
    key: str
    description: str
    callback: Optional[Callable] = None


class KeyboardShortcutManager:
    """
    Manager for keyboard shortcuts.
    
    Provides:
    - Registration of keyboard shortcuts
    - Unregistration of shortcuts
    - Help text generation for tooltips
    
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    # Default shortcuts
    DEFAULT_SHORTCUTS = {
        'F5': 'Làm mới bảng xem trước',
        'Ctrl+A': 'Chọn tất cả tờ khai',
        'Ctrl+Shift+A': 'Bỏ chọn tất cả',
        'Escape': 'Dừng tải xuống'
    }
    
    def __init__(self, root: tk.Tk):
        """
        Initialize KeyboardShortcutManager.
        
        Args:
            root: Root Tk window
        """
        self.root = root
        self._shortcuts: Dict[str, ShortcutInfo] = {}
        self._bound_keys: Dict[str, str] = {}  # Maps tk key to shortcut name
    
    def register_shortcut(
        self, 
        key: str, 
        callback: Callable,
        description: str = ""
    ) -> None:
        """
        Register a keyboard shortcut.
        
        Args:
            key: Shortcut key (e.g., 'F5', 'Ctrl+A', 'Ctrl+Shift+A', 'Escape')
            callback: Function to call when shortcut is pressed
            description: Description for help text
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        # Convert key to tk binding format
        tk_key = self._convert_to_tk_key(key)
        
        # Store shortcut info
        self._shortcuts[key] = ShortcutInfo(
            key=key,
            description=description or self.DEFAULT_SHORTCUTS.get(key, ''),
            callback=callback
        )
        
        # Bind to root window
        self.root.bind(tk_key, lambda e: self._handle_shortcut(key, e))
        self._bound_keys[tk_key] = key
    
    def unregister_shortcut(self, key: str) -> None:
        """
        Unregister a keyboard shortcut.
        
        Args:
            key: Shortcut key to unregister
        """
        if key in self._shortcuts:
            tk_key = self._convert_to_tk_key(key)
            
            try:
                self.root.unbind(tk_key)
            except tk.TclError:
                pass
            
            if tk_key in self._bound_keys:
                del self._bound_keys[tk_key]
            
            del self._shortcuts[key]
    
    def _convert_to_tk_key(self, key: str) -> str:
        """
        Convert shortcut key to Tkinter binding format.
        
        Args:
            key: Shortcut key (e.g., 'F5', 'Ctrl+A', 'Ctrl+Shift+A')
            
        Returns:
            Tkinter binding string (e.g., '<F5>', '<Control-a>', '<Control-Shift-a>')
        """
        # Handle special keys
        if key == 'Escape':
            return '<Escape>'
        
        if key.startswith('F') and key[1:].isdigit():
            return f'<{key}>'
        
        # Handle modifier combinations
        parts = key.split('+')
        modifiers = []
        main_key = parts[-1].lower()
        
        for part in parts[:-1]:
            part_lower = part.lower()
            if part_lower == 'ctrl':
                modifiers.append('Control')
            elif part_lower == 'shift':
                modifiers.append('Shift')
            elif part_lower == 'alt':
                modifiers.append('Alt')
        
        if modifiers:
            modifier_str = '-'.join(modifiers)
            return f'<{modifier_str}-{main_key}>'
        
        return f'<{main_key}>'
    
    def _handle_shortcut(self, key: str, event) -> str:
        """
        Handle shortcut key press.
        
        Args:
            key: Shortcut key
            event: Tkinter event
            
        Returns:
            'break' to prevent further event processing
        """
        if key in self._shortcuts:
            shortcut = self._shortcuts[key]
            if shortcut.callback:
                try:
                    shortcut.callback()
                except Exception:
                    pass  # Silently ignore callback errors
        
        return 'break'
    
    def get_shortcuts_help(self) -> Dict[str, str]:
        """
        Get dictionary of shortcuts and their descriptions.
        
        Returns:
            Dictionary mapping shortcut keys to descriptions
            
        Requirements: 5.5
        """
        return {
            key: info.description 
            for key, info in self._shortcuts.items()
        }
    
    def get_shortcut_tooltip(self, action: str) -> str:
        """
        Get tooltip text for a specific action.
        
        Args:
            action: Action name (e.g., 'refresh', 'select_all', 'deselect_all', 'stop')
            
        Returns:
            Tooltip text with shortcut hint
            
        Requirements: 5.5
        """
        action_shortcuts = {
            'refresh': 'F5',
            'select_all': 'Ctrl+A',
            'deselect_all': 'Ctrl+Shift+A',
            'stop': 'Escape'
        }
        
        shortcut = action_shortcuts.get(action)
        if shortcut and shortcut in self._shortcuts:
            return f"({shortcut})"
        
        return ""
    
    def register_default_shortcuts(
        self,
        refresh_callback: Optional[Callable] = None,
        select_all_callback: Optional[Callable] = None,
        deselect_all_callback: Optional[Callable] = None,
        stop_callback: Optional[Callable] = None
    ) -> None:
        """
        Register all default shortcuts.
        
        Args:
            refresh_callback: Callback for F5 (refresh)
            select_all_callback: Callback for Ctrl+A (select all)
            deselect_all_callback: Callback for Ctrl+Shift+A (deselect all)
            stop_callback: Callback for Escape (stop download)
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        if refresh_callback:
            self.register_shortcut('F5', refresh_callback, 'Làm mới bảng xem trước')
        
        if select_all_callback:
            self.register_shortcut('Ctrl+A', select_all_callback, 'Chọn tất cả tờ khai')
        
        if deselect_all_callback:
            self.register_shortcut('Ctrl+Shift+A', deselect_all_callback, 'Bỏ chọn tất cả')
        
        if stop_callback:
            self.register_shortcut('Escape', stop_callback, 'Dừng tải xuống')
    
    def clear_all(self) -> None:
        """Unregister all shortcuts"""
        for key in list(self._shortcuts.keys()):
            self.unregister_shortcut(key)
