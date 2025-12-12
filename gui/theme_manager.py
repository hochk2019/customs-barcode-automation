"""
Theme Manager for Customs Barcode Automation

This module provides theme management functionality for switching between
light and dark modes with proper color contrast.

Implements Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Tuple, Callable, List
import math

from config.configuration_manager import ConfigurationManager


class ThemeManager:
    """
    Manages light and dark themes for the application.
    
    Implements Requirements:
    - 7.1: Apply dark color scheme to all UI components
    - 7.2: Use high-contrast color palette for dark mode
    - 7.3: Ensure minimum contrast ratio of 4.5:1
    - 7.4: Restore default light color scheme
    - 7.5: Apply saved theme preference on startup
    - 7.6: Update all visible components immediately without restart
    """
    
    # Light theme colors (default)
    # All text/background pairs meet WCAG 4.5:1 contrast ratio
    LIGHT_THEME: Dict[str, str] = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_card': '#ffffff',
        'text_primary': '#212121',
        'text_secondary': '#5f5f5f',  # Darkened from #757575 to meet 4.5:1 contrast
        'accent': '#1565c0',  # Darkened from #1976d2 to meet 4.5:1 contrast
        'success': '#2e7d32',  # Darkened from #4caf50 to meet 4.5:1 contrast
        'error': '#c62828',  # Darkened from #f44336 to meet 4.5:1 contrast
        'warning': '#b45309',  # Darkened from #ff9800 to meet 4.5:1 contrast (amber-700)
        'border': '#e0e0e0'
    }
    
    # Dark theme colors (Requirements 7.2)
    DARK_THEME: Dict[str, str] = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#2d2d2d',
        'bg_card': '#383838',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'accent': '#4fc3f7',
        'success': '#66bb6a',
        'error': '#ef5350',
        'warning': '#ffca28',
        'border': '#555555'
    }
    
    def __init__(self, root: tk.Tk, config_manager: ConfigurationManager):
        """
        Initialize ThemeManager.
        
        Args:
            root: The root Tk window
            config_manager: Configuration manager for persisting theme preference
        """
        self.root = root
        self.config_manager = config_manager
        self._current_theme: str = 'light'
        self._theme_change_callbacks: List[Callable[[str], None]] = []
        self._style: Optional[ttk.Style] = None
        
        # Load saved theme preference (Requirement 7.5)
        saved_theme = self.config_manager.get_theme()
        if saved_theme in ('light', 'dark'):
            self._current_theme = saved_theme
    
    def get_current_theme(self) -> str:
        """
        Get the current theme name.
        
        Returns:
            Current theme name ('light' or 'dark')
        """
        return self._current_theme
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color value from the current theme.
        
        Args:
            color_name: Name of the color (e.g., 'bg_primary', 'text_primary')
            
        Returns:
            Hex color code for the requested color
        """
        theme_colors = self.DARK_THEME if self._current_theme == 'dark' else self.LIGHT_THEME
        return theme_colors.get(color_name, '#000000')
    
    def get_theme_colors(self, theme: Optional[str] = None) -> Dict[str, str]:
        """
        Get all colors for a theme.
        
        Args:
            theme: Theme name ('light' or 'dark'), or None for current theme
            
        Returns:
            Dictionary of color names to hex values
        """
        if theme is None:
            theme = self._current_theme
        return self.DARK_THEME.copy() if theme == 'dark' else self.LIGHT_THEME.copy()

    def apply_theme(self, theme: str) -> None:
        """
        Apply a theme to the application.
        
        Args:
            theme: Theme name ('light' or 'dark')
            
        Implements Requirements 7.1, 7.4, 7.6
        """
        if theme not in ('light', 'dark'):
            theme = 'light'
        
        self._current_theme = theme
        colors = self.get_theme_colors(theme)
        
        # Configure ttk styles
        self._configure_ttk_styles(colors)
        
        # Update root window background
        self.root.configure(bg=colors['bg_primary'])
        
        # Recursively update all widgets
        self._update_widget_colors(self.root, colors)
        
        # Save preference to config (Requirement 7.5)
        self.config_manager.set_theme(theme)
        
        # Notify callbacks (Requirement 7.6)
        for callback in self._theme_change_callbacks:
            try:
                callback(theme)
            except Exception:
                pass  # Don't let callback errors break theme switching
    
    def toggle_theme(self) -> None:
        """
        Toggle between light and dark themes.
        
        Implements Requirement 7.6 - immediate update without restart
        """
        new_theme = 'dark' if self._current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
    
    def register_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback to be called when theme changes.
        
        Args:
            callback: Function that takes theme name as argument
        """
        if callback not in self._theme_change_callbacks:
            self._theme_change_callbacks.append(callback)
    
    def unregister_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Unregister a theme change callback.
        
        Args:
            callback: Previously registered callback function
        """
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)
    
    def _configure_ttk_styles(self, colors: Dict[str, str]) -> None:
        """
        Configure ttk styles for the current theme.
        
        Args:
            colors: Theme color dictionary
        """
        if self._style is None:
            self._style = ttk.Style(self.root)
        
        style = self._style
        
        # Try to use clam theme as base for better customization
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure TFrame
        style.configure('TFrame', background=colors['bg_primary'])
        style.configure('Card.TFrame', background=colors['bg_card'])
        
        # Configure TLabel
        style.configure(
            'TLabel',
            background=colors['bg_primary'],
            foreground=colors['text_primary']
        )
        style.configure(
            'Secondary.TLabel',
            foreground=colors['text_secondary']
        )
        style.configure('Success.TLabel', foreground=colors['success'])
        style.configure('Error.TLabel', foreground=colors['error'])
        style.configure('Warning.TLabel', foreground=colors['warning'])
        style.configure('Info.TLabel', foreground=colors['accent'])
        
        # Configure TButton
        style.configure(
            'TButton',
            background=colors['accent'],
            foreground='#ffffff' if self._current_theme == 'light' else colors['text_primary']
        )
        style.map(
            'TButton',
            background=[('active', colors['accent']), ('disabled', colors['bg_secondary'])],
            foreground=[('disabled', colors['text_secondary'])]
        )
        
        # Configure TEntry
        style.configure(
            'TEntry',
            fieldbackground=colors['bg_card'],
            foreground=colors['text_primary'],
            insertcolor=colors['text_primary']
        )
        style.map(
            'TEntry',
            fieldbackground=[('disabled', colors['bg_secondary'])]
        )
        
        # Configure TCombobox
        style.configure(
            'TCombobox',
            fieldbackground=colors['bg_card'],
            background=colors['bg_card'],
            foreground=colors['text_primary'],
            arrowcolor=colors['accent']
        )
        style.map(
            'TCombobox',
            fieldbackground=[('readonly', colors['bg_card']), ('disabled', colors['bg_secondary'])],
            background=[('active', colors['bg_secondary'])]
        )
        
        # Configure TLabelframe
        style.configure(
            'TLabelframe',
            background=colors['bg_primary'],
            bordercolor=colors['border']
        )
        style.configure(
            'TLabelframe.Label',
            background=colors['bg_primary'],
            foreground=colors['text_primary']
        )
        style.configure(
            'Card.TLabelframe',
            background=colors['bg_card'],
            bordercolor=colors['border']
        )
        
        # Configure Treeview
        style.configure(
            'Treeview',
            background=colors['bg_card'],
            foreground=colors['text_primary'],
            fieldbackground=colors['bg_card']
        )
        style.configure(
            'Treeview.Heading',
            background=colors['bg_secondary'],
            foreground=colors['text_primary']
        )
        style.map(
            'Treeview',
            background=[('selected', colors['accent'])],
            foreground=[('selected', '#ffffff')]
        )
        
        # Configure TProgressbar
        style.configure(
            'TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_secondary']
        )
        style.configure(
            'Horizontal.TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_secondary']
        )
        
        # Configure TCheckbutton
        style.configure(
            'TCheckbutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary']
        )
        
        # Configure TRadiobutton
        style.configure(
            'TRadiobutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary']
        )
        
        # Configure TScrollbar
        style.configure(
            'TScrollbar',
            background=colors['bg_secondary'],
            troughcolor=colors['bg_primary']
        )

    def _update_widget_colors(self, widget: tk.Widget, colors: Dict[str, str]) -> None:
        """
        Recursively update colors for tk widgets (non-ttk).
        
        Args:
            widget: Widget to update
            colors: Theme color dictionary
        """
        try:
            widget_class = widget.winfo_class()
            
            # Update tk.Frame
            if widget_class == 'Frame':
                try:
                    widget.configure(bg=colors['bg_primary'])
                except tk.TclError:
                    pass
            
            # Update tk.Label
            elif widget_class == 'Label':
                try:
                    # Check if it's a special label (gold, accent, etc.)
                    current_fg = str(widget.cget('fg')).lower()
                    # Don't change branded colors (gold, accent colors)
                    if current_fg not in ('#d4af37', '#c9a227', '#ffd700', '#4fc3f7'):
                        widget.configure(
                            bg=colors['bg_primary'],
                            fg=colors['text_primary']
                        )
                    else:
                        widget.configure(bg=colors['bg_primary'])
                except tk.TclError:
                    pass
            
            # Update tk.Button
            elif widget_class == 'Button':
                try:
                    # Check if it's a branded button (gold background)
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in ('#d4af37', '#c9a227', '#ffd700'):
                        widget.configure(
                            bg=colors['bg_secondary'],
                            fg=colors['text_primary'],
                            activebackground=colors['bg_card'],
                            activeforeground=colors['text_primary']
                        )
                except tk.TclError:
                    pass
            
            # Update tk.Entry
            elif widget_class == 'Entry':
                try:
                    widget.configure(
                        bg=colors['bg_card'],
                        fg=colors['text_primary'],
                        insertbackground=colors['text_primary']
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Text
            elif widget_class == 'Text':
                try:
                    widget.configure(
                        bg=colors['bg_card'],
                        fg=colors['text_primary'],
                        insertbackground=colors['text_primary']
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Listbox
            elif widget_class == 'Listbox':
                try:
                    widget.configure(
                        bg=colors['bg_card'],
                        fg=colors['text_primary'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff'
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Canvas
            elif widget_class == 'Canvas':
                try:
                    widget.configure(bg=colors['bg_primary'])
                except tk.TclError:
                    pass
            
        except Exception:
            pass  # Ignore errors for widgets that can't be configured
        
        # Recursively update children
        try:
            for child in widget.winfo_children():
                self._update_widget_colors(child, colors)
        except Exception:
            pass
    
    @staticmethod
    def calculate_contrast_ratio(color1: str, color2: str) -> float:
        """
        Calculate the contrast ratio between two colors.
        
        Uses WCAG 2.0 formula for contrast ratio calculation.
        Implements Requirement 7.3 - ensure minimum 4.5:1 ratio.
        
        Args:
            color1: First hex color (e.g., '#ffffff')
            color2: Second hex color (e.g., '#000000')
            
        Returns:
            Contrast ratio (1.0 to 21.0)
        """
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            """Convert hex color to RGB tuple."""
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
            """Calculate relative luminance of a color."""
            def channel_luminance(channel: int) -> float:
                srgb = channel / 255.0
                if srgb <= 0.03928:
                    return srgb / 12.92
                return math.pow((srgb + 0.055) / 1.055, 2.4)
            
            r, g, b = rgb
            return (
                0.2126 * channel_luminance(r) +
                0.7152 * channel_luminance(g) +
                0.0722 * channel_luminance(b)
            )
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = get_relative_luminance(rgb1)
        lum2 = get_relative_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def validate_dark_theme_contrast(self) -> Dict[str, Tuple[float, bool]]:
        """
        Validate that all dark theme text/background pairs meet 4.5:1 contrast.
        
        Implements Requirement 7.3.
        
        Returns:
            Dictionary mapping color pair names to (ratio, passes) tuples
        """
        results = {}
        dark = self.DARK_THEME
        min_ratio = 4.5
        
        # Text on primary background
        pairs = [
            ('text_primary on bg_primary', dark['text_primary'], dark['bg_primary']),
            ('text_primary on bg_secondary', dark['text_primary'], dark['bg_secondary']),
            ('text_primary on bg_card', dark['text_primary'], dark['bg_card']),
            ('text_secondary on bg_primary', dark['text_secondary'], dark['bg_primary']),
            ('text_secondary on bg_secondary', dark['text_secondary'], dark['bg_secondary']),
            ('text_secondary on bg_card', dark['text_secondary'], dark['bg_card']),
            ('accent on bg_primary', dark['accent'], dark['bg_primary']),
            ('success on bg_primary', dark['success'], dark['bg_primary']),
            ('error on bg_primary', dark['error'], dark['bg_primary']),
            ('warning on bg_primary', dark['warning'], dark['bg_primary']),
        ]
        
        for name, fg, bg in pairs:
            ratio = self.calculate_contrast_ratio(fg, bg)
            results[name] = (ratio, ratio >= min_ratio)
        
        return results
    
    def get_text_color_pairs(self, theme: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """
        Get all text/background color pairs for a theme.
        
        Args:
            theme: Theme name or None for current theme
            
        Returns:
            List of (pair_name, text_color, bg_color) tuples
        """
        colors = self.get_theme_colors(theme)
        
        return [
            ('text_primary on bg_primary', colors['text_primary'], colors['bg_primary']),
            ('text_primary on bg_secondary', colors['text_primary'], colors['bg_secondary']),
            ('text_primary on bg_card', colors['text_primary'], colors['bg_card']),
            ('text_secondary on bg_primary', colors['text_secondary'], colors['bg_primary']),
            ('text_secondary on bg_secondary', colors['text_secondary'], colors['bg_secondary']),
            ('text_secondary on bg_card', colors['text_secondary'], colors['bg_card']),
            ('accent on bg_primary', colors['accent'], colors['bg_primary']),
            ('success on bg_primary', colors['success'], colors['bg_primary']),
            ('error on bg_primary', colors['error'], colors['bg_primary']),
            ('warning on bg_primary', colors['warning'], colors['bg_primary']),
        ]
