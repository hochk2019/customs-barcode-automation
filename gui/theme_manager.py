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
        'bg_input': '#ffffff',         # Input fields background
        'text_primary': '#212121',
        'text_secondary': '#5f5f5f',   # Darkened from #757575 to meet 4.5:1 contrast
        'accent': '#1565c0',           # Darkened from #1976d2 to meet 4.5:1 contrast
        'success': '#2e7d32',          # Darkened from #4caf50 to meet 4.5:1 contrast
        'error': '#c62828',            # Darkened from #f44336 to meet 4.5:1 contrast
        'warning': '#b45309',          # Darkened from #ff9800 to meet 4.5:1 contrast (amber-700)
        'border': '#e0e0e0',
        'border_light': '#d0d0d0',     # Slightly darker border for emphasis
        'highlight': '#e8e8e8'         # Highlight/hover state
    }
    
    # Dark theme colors (Requirements 7.2)
    # Unified dark background for consistent appearance
    DARK_THEME: Dict[str, str] = {
        'bg_primary': '#1e1e1e',       # Main background - unified dark gray
        'bg_secondary': '#252525',     # Secondary areas - very slightly lighter
        'bg_card': '#1e1e1e',          # Cards - same as primary for consistency
        'bg_input': '#2d2d2d',         # Input fields - slightly lighter for visibility
        'text_primary': '#ffffff',     # Main text - pure white
        'text_secondary': '#b0b0b0',   # Secondary text - light gray
        'accent': '#4da6ff',           # Accent - bright blue
        'success': '#4caf50',          # Success - bright green
        'error': '#f44336',            # Error - bright red
        'warning': '#ffb74d',          # Warning - bright orange
        'border': '#3a3a3a',           # Borders - subtle gray
        'border_light': '#4a4a4a',     # Lighter borders for emphasis
        'highlight': '#333333'         # Highlight/hover state
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

    def apply_theme_to_dialog(self, dialog: tk.Toplevel) -> None:
        """
        Apply current theme to a newly created dialog.
        
        This should be called after creating a new Toplevel dialog to ensure
        it uses the current theme colors.
        
        Args:
            dialog: The Toplevel dialog to apply theme to
        """
        colors = self.get_theme_colors()
        
        try:
            # Check if this is a branding dialog
            dialog_bg = str(dialog.cget('bg')).lower()
            if dialog_bg not in self.BRANDING_BG_COLORS:
                dialog.configure(bg=colors['bg_primary'])
                self._update_widget_colors(dialog, colors)
                self._refresh_ttk_widgets(dialog)
        except:
            pass

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
        
        # Recursively update all widgets including ttk widgets
        self._update_widget_colors(self.root, colors)
        
        # Force refresh ttk widgets to apply new styles
        self._refresh_ttk_widgets(self.root)
        
        # Also update any open Toplevel windows (dialogs)
        for child in self.root.winfo_children():
            if child.winfo_class() == 'Toplevel':
                # Check if this is a branding dialog (has branding bg)
                try:
                    dialog_bg = str(child.cget('bg')).lower()
                    if dialog_bg not in self.BRANDING_BG_COLORS:
                        child.configure(bg=colors['bg_primary'])
                        self._update_widget_colors(child, colors)
                        self._refresh_ttk_widgets(child)
                except:
                    pass
        
        # Save preference to config (Requirement 7.5)
        self.config_manager.set_theme(theme)
        
        # Force full update of all widgets (Requirement 7.6 - immediate update)
        self.root.update_idletasks()
        
        # Force redraw of all tk.Button widgets by simulating Enter/Leave events
        self._force_refresh_buttons(self.root)
        
        # Notify callbacks (Requirement 7.6)
        for callback in self._theme_change_callbacks:
            try:
                callback(theme)
            except Exception:
                pass  # Don't let callback errors break theme switching
    
    def _force_refresh_buttons(self, widget: tk.Widget) -> None:
        """Force all tk.Button widgets to refresh their appearance."""
        try:
            if widget.winfo_class() == 'Button':
                # Force redraw by updating the relief
                current_relief = widget.cget('relief')
                widget.config(relief=current_relief)
        except Exception:
            pass
        
        # Recursively refresh children
        try:
            for child in widget.winfo_children():
                self._force_refresh_buttons(child)
        except Exception:
            pass
    
    def toggle_theme(self) -> None:
        """
        Toggle between light and dark themes.
        
        Implements Requirement 7.6 - immediate update without restart
        """
        new_theme = 'dark' if self._current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
    
    def _refresh_ttk_widgets(self, widget: tk.Widget) -> None:
        """
        Force refresh ttk widgets to apply new styles.
        
        This is necessary because ttk widgets cache their styles and don't
        automatically update when style configuration changes.
        
        Args:
            widget: Root widget to start refreshing from
        """
        try:
            widget_class = widget.winfo_class()
            
            # List of ttk widget classes that need refreshing
            ttk_classes = {
                'TButton', 'TLabel', 'TFrame', 'TEntry', 'TCombobox',
                'TLabelframe', 'TCheckbutton', 'TRadiobutton', 'TScrollbar',
                'TNotebook', 'TProgressbar', 'TSeparator', 'Treeview'
            }
            
            if widget_class in ttk_classes:
                try:
                    # Get current style
                    current_style = ''
                    try:
                        current_style = str(widget.cget('style')) if hasattr(widget, 'cget') else ''
                    except:
                        pass
                    
                    # Force widget to re-read its style by temporarily changing and restoring
                    # This triggers the widget to update its appearance
                    if current_style:
                        widget.configure(style=current_style)
                    else:
                        # For widgets without explicit style, use default
                        default_style = widget_class if widget_class.startswith('T') else f'T{widget_class}'
                        try:
                            widget.configure(style=default_style)
                        except:
                            pass
                    
                    # Force update
                    widget.update_idletasks()
                except tk.TclError:
                    pass
            
            # Special handling for Treeview - update tags
            if widget_class == 'Treeview':
                try:
                    colors = self.get_theme_colors()
                    self._update_treeview_tags(widget, colors)
                except:
                    pass
            
        except Exception:
            pass
        
        # Recursively refresh children
        try:
            for child in widget.winfo_children():
                self._refresh_ttk_widgets(child)
        except Exception:
            pass
    
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
        
        # Get input background color (use bg_input if available, fallback to bg_card)
        bg_input = colors.get('bg_input', colors['bg_card'])
        border_light = colors.get('border_light', colors['border'])
        highlight = colors.get('highlight', colors['bg_secondary'])
        
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
        
        # Configure TButton - white text on colored background for both themes
        # Primary buttons have accent color background, so text should always be white
        style.configure(
            'TButton',
            background=colors['accent'],
            foreground='#ffffff',  # Always white text on accent background
            borderwidth=1,
            focusthickness=2,
            focuscolor=colors['accent'],
            padding=(8, 4)
        )
        style.map(
            'TButton',
            background=[('active', colors['accent']), ('pressed', colors['accent']), ('disabled', colors['bg_secondary'])],
            foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', colors['text_secondary'])]
        )
        
        # Configure TEntry - lighter background for better visibility
        style.configure(
            'TEntry',
            fieldbackground=bg_input,
            foreground=colors['text_primary'],
            insertcolor=colors['text_primary'],
            bordercolor=border_light,
            lightcolor=border_light,
            darkcolor=border_light
        )
        style.map(
            'TEntry',
            fieldbackground=[('disabled', colors['bg_secondary']), ('focus', bg_input)],
            bordercolor=[('focus', colors['accent'])]
        )
        
        # Configure TCombobox - improved visibility
        style.configure(
            'TCombobox',
            fieldbackground=bg_input,
            background=bg_input,
            foreground=colors['text_primary'],
            arrowcolor=colors['accent'],
            bordercolor=border_light,
            lightcolor=border_light,
            darkcolor=border_light
        )
        style.map(
            'TCombobox',
            fieldbackground=[('readonly', bg_input), ('disabled', colors['bg_secondary'])],
            background=[('active', highlight)],
            bordercolor=[('focus', colors['accent'])]
        )
        
        # Configure TLabelframe - visible borders in dark mode
        style.configure(
            'TLabelframe',
            background=colors['bg_primary'],
            bordercolor=border_light,
            borderwidth=2,
            relief='groove'
        )
        style.configure(
            'TLabelframe.Label',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            font=('Segoe UI', 9, 'bold')
        )
        style.configure(
            'Card.TLabelframe',
            background=colors['bg_card'],
            bordercolor=border_light
        )
        
        # Configure Treeview - improved contrast
        style.configure(
            'Treeview',
            background=colors['bg_card'],
            foreground=colors['text_primary'],
            fieldbackground=colors['bg_card'],
            bordercolor=border_light,
            lightcolor=border_light,
            darkcolor=border_light
        )
        style.configure(
            'Treeview.Heading',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=border_light,
            relief='raised'
        )
        style.map(
            'Treeview',
            background=[('selected', colors['accent'])],
            foreground=[('selected', '#ffffff')]
        )
        style.map(
            'Treeview.Heading',
            background=[('active', highlight)]
        )
        
        # Configure TProgressbar
        style.configure(
            'TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_secondary'],
            bordercolor=border_light
        )
        style.configure(
            'Horizontal.TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_secondary'],
            bordercolor=border_light
        )
        
        # Configure TCheckbutton
        style.configure(
            'TCheckbutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            indicatorcolor=bg_input,
            indicatorrelief='sunken'
        )
        style.map(
            'TCheckbutton',
            indicatorcolor=[('selected', colors['accent']), ('!selected', bg_input)],
            background=[('active', highlight)]
        )
        
        # Configure TRadiobutton
        style.configure(
            'TRadiobutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            indicatorcolor=bg_input
        )
        style.map(
            'TRadiobutton',
            indicatorcolor=[('selected', colors['accent']), ('!selected', bg_input)],
            background=[('active', highlight)]
        )
        
        # Configure TScrollbar - more visible
        style.configure(
            'TScrollbar',
            background=highlight,
            troughcolor=colors['bg_secondary'],
            bordercolor=border_light,
            arrowcolor=colors['text_primary']
        )
        style.map(
            'TScrollbar',
            background=[('active', colors['accent'])]
        )
        
        # Configure TNotebook (tabs)
        style.configure(
            'TNotebook',
            background=colors['bg_primary'],
            bordercolor=border_light
        )
        style.configure(
            'TNotebook.Tab',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            padding=[10, 5]
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', colors['bg_card']), ('active', highlight)],
            foreground=[('selected', colors['text_primary'])]
        )
        
        # Configure TSeparator
        style.configure(
            'TSeparator',
            background=border_light
        )
        
        # Configure Success.TButton - green button for actions like "Download"
        style.configure(
            'Success.TButton',
            background=colors['success'],
            foreground='#ffffff',
            borderwidth=0,
            focusthickness=2,
            focuscolor=colors['success'],
            padding=(8, 4)
        )
        style.map(
            'Success.TButton',
            background=[('active', colors['success']), ('pressed', colors['success']), ('disabled', colors['bg_secondary'])],
            foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', colors['text_secondary'])]
        )
        
        # Configure Danger.TButton - red button for actions like "Stop"
        style.configure(
            'Danger.TButton',
            background=colors['error'],
            foreground='#ffffff',
            borderwidth=0,
            focusthickness=2,
            focuscolor=colors['error'],
            padding=(8, 4)
        )
        style.map(
            'Danger.TButton',
            background=[('active', colors['error']), ('pressed', colors['error']), ('disabled', colors['bg_secondary'])],
            foreground=[('active', '#ffffff'), ('pressed', '#ffffff'), ('disabled', colors['text_secondary'])]
        )
        
        # Configure Warning.TButton - orange/yellow button for warnings
        style.configure(
            'Warning.TButton',
            background=colors['warning'],
            foreground='#000000' if self._current_theme == 'dark' else '#ffffff',
            borderwidth=0,
            focusthickness=2,
            focuscolor=colors['warning'],
            padding=(8, 4)
        )
        style.map(
            'Warning.TButton',
            background=[('active', colors['warning']), ('pressed', colors['warning']), ('disabled', colors['bg_secondary'])],
            foreground=[('active', '#000000' if self._current_theme == 'dark' else '#ffffff'), 
                       ('pressed', '#000000' if self._current_theme == 'dark' else '#ffffff'), 
                       ('disabled', colors['text_secondary'])]
        )
        
        # Configure Secondary.TButton - outline style button
        style.configure(
            'Secondary.TButton',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            borderwidth=1,
            focusthickness=2,
            focuscolor=colors['accent'],
            padding=(8, 4)
        )
        style.map(
            'Secondary.TButton',
            background=[('active', highlight), ('pressed', highlight), ('disabled', colors['bg_secondary'])],
            foreground=[('active', colors['text_primary']), ('pressed', colors['text_primary']), ('disabled', colors['text_secondary'])]
        )

    # Branding colors that should NOT be changed by theme switching
    # These are the header/footer colors that must remain constant
    PROTECTED_COLORS = {
        '#0d0d0d',  # Header/footer dark background (primary branding)
        '#ffd700', '#d4a853', '#d4af37', '#c9a227',  # Gold colors for branding
    }
    
    # Colors that indicate a widget is part of the branding header/footer
    # Note: #1a1a1a is used both for branding AND dark theme bg_primary
    # We only protect #0d0d0d which is exclusively for branding
    BRANDING_BG_COLORS = {'#0d0d0d'}
    
    def _is_protected_color(self, color: str) -> bool:
        """Check if a color is a protected branding color."""
        if not color:
            return False
        color_lower = str(color).lower()
        return color_lower in self.PROTECTED_COLORS
    
    def _is_branding_widget(self, widget: tk.Widget) -> bool:
        """Check if widget is part of branding (header/footer)."""
        try:
            bg = str(widget.cget('bg')).lower()
            if bg in self.BRANDING_BG_COLORS:
                return True
            # Also check if any parent has branding background
            parent = widget.master
            while parent:
                try:
                    parent_bg = str(parent.cget('bg')).lower()
                    if parent_bg in self.BRANDING_BG_COLORS:
                        return True
                except:
                    pass
                parent = getattr(parent, 'master', None)
            return False
        except:
            return False
    
    def _update_widget_colors(self, widget: tk.Widget, colors: Dict[str, str]) -> None:
        """
        Recursively update colors for tk widgets (non-ttk).
        Preserves branding colors (header, footer, etc.)
        
        Args:
            widget: Widget to update
            colors: Theme color dictionary
        """
        # Check if this widget or its parent is a branding widget
        is_branding = self._is_branding_widget(widget)
        
        # Get input background color (use bg_input if available, fallback to bg_card)
        bg_input = colors.get('bg_input', colors['bg_card'])
        border_light = colors.get('border_light', colors['border'])
        highlight = colors.get('highlight', colors['bg_secondary'])
        
        try:
            widget_class = widget.winfo_class()
            
            # Skip branding widgets entirely
            if is_branding:
                # Still recurse to children but they will also be skipped if branding
                pass
            
            # Update tk.Frame
            elif widget_class == 'Frame':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    # Don't change frames with branding background colors
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(bg=colors['bg_primary'])
                except tk.TclError:
                    pass
            
            # Update tk.Label
            elif widget_class == 'Label':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    current_fg = str(widget.cget('fg')).lower()
                    
                    # Don't change labels on branding backgrounds
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(bg=colors['bg_primary'])
                        
                        # Map semantic colors to theme colors
                        # This preserves the semantic meaning while using theme-appropriate colors
                        semantic_color_map = {
                            'green': colors['success'],
                            'red': colors['error'],
                            'blue': colors['accent'],
                            'orange': colors['warning'],
                            'gray': colors['text_secondary'],
                            'grey': colors['text_secondary'],
                            # Also handle hex versions of common colors
                            '#228b22': colors['success'],  # Forest green
                            '#dc143c': colors['error'],    # Crimson red
                            '#107c10': colors['success'],  # MS green
                            '#d13438': colors['error'],    # MS red
                            '#0078d4': colors['accent'],   # MS blue
                            '#ff8c00': colors['warning'],  # Dark orange
                        }
                        
                        # Check if current foreground is a semantic color
                        if current_fg in semantic_color_map:
                            widget.configure(fg=semantic_color_map[current_fg])
                        elif current_fg not in self.PROTECTED_COLORS:
                            # Only update non-semantic, non-protected colors
                            widget.configure(fg=colors['text_primary'])
                except tk.TclError:
                    pass
            
            # Update tk.Button - improved visibility with border
            elif widget_class == 'Button':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    current_fg = str(widget.cget('fg')).lower()
                    
                    # Don't change buttons on branding backgrounds
                    if current_bg not in self.BRANDING_BG_COLORS and not self._is_protected_color(current_bg):
                        # Check if this is a colored action button (success, danger, etc.)
                        # These buttons have specific colors that should be mapped to theme colors
                        is_success_btn = current_bg in ['#107c10', '#0e6b0e', '#2e7d32', '#58d68d', '#4caf50']
                        is_danger_btn = current_bg in ['#d13438', '#b52d30', '#c62828', '#ec7063', '#f44336']
                        is_primary_btn = current_bg in ['#0078d4', '#106ebe', '#1565c0', '#5dade2', '#4da6ff']
                        is_warning_btn = current_bg in ['#ff8c00', '#b45309', '#f7dc6f', '#ffb74d']
                        is_secondary_btn = current_bg in ['#f5f5f5', '#ffffff', '#e8e8e8', '#2a2a2a', '#333333', '#404040', '#1e1e1e', '#252525']
                        
                        if is_success_btn:
                            widget.configure(
                                bg=colors['success'],
                                fg='#ffffff',
                                activebackground=colors['success'],
                                activeforeground='#ffffff'
                            )
                        elif is_danger_btn:
                            widget.configure(
                                bg=colors['error'],
                                fg='#ffffff',
                                activebackground=colors['error'],
                                activeforeground='#ffffff'
                            )
                        elif is_primary_btn:
                            widget.configure(
                                bg=colors['accent'],
                                fg='#ffffff',
                                activebackground=colors['accent'],
                                activeforeground='#ffffff'
                            )
                        elif is_warning_btn:
                            widget.configure(
                                bg=colors['warning'],
                                fg='#000000' if self._current_theme == 'dark' else '#ffffff',
                                activebackground=colors['warning'],
                                activeforeground='#000000' if self._current_theme == 'dark' else '#ffffff'
                            )
                        elif is_secondary_btn:
                            # Secondary/neutral button
                            widget.configure(
                                bg=colors['bg_secondary'],
                                fg=colors['text_primary'],
                                activebackground=highlight,
                                activeforeground=colors['text_primary'],
                                highlightbackground=border_light,
                                highlightcolor=colors['accent']
                            )
                        else:
                            # Unknown button type - apply secondary style as default
                            widget.configure(
                                bg=colors['bg_secondary'],
                                fg=colors['text_primary'],
                                activebackground=highlight,
                                activeforeground=colors['text_primary'],
                                highlightbackground=border_light,
                                highlightcolor=colors['accent']
                            )
                except tk.TclError:
                    pass
            
            # Update tk.Entry - lighter background for visibility
            elif widget_class == 'Entry':
                try:
                    widget.configure(
                        bg=bg_input,
                        fg=colors['text_primary'],
                        insertbackground=colors['text_primary'],
                        highlightbackground=border_light,
                        highlightcolor=colors['accent'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff'
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Text - lighter background for visibility
            elif widget_class == 'Text':
                try:
                    widget.configure(
                        bg=bg_input,
                        fg=colors['text_primary'],
                        insertbackground=colors['text_primary'],
                        highlightbackground=border_light,
                        highlightcolor=colors['accent'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff'
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Listbox - improved contrast
            elif widget_class == 'Listbox':
                try:
                    widget.configure(
                        bg=bg_input,
                        fg=colors['text_primary'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff',
                        highlightbackground=border_light,
                        highlightcolor=colors['accent']
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Canvas
            elif widget_class == 'Canvas':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(
                            bg=colors['bg_primary'],
                            highlightbackground=border_light
                        )
                except tk.TclError:
                    pass
            
            # Update tk.Checkbutton
            elif widget_class == 'Checkbutton':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(
                            bg=colors['bg_primary'],
                            fg=colors['text_primary'],
                            selectcolor=bg_input,
                            activebackground=highlight,
                            activeforeground=colors['text_primary'],
                            highlightbackground=colors['bg_primary']
                        )
                except tk.TclError:
                    pass
            
            # Update tk.Radiobutton
            elif widget_class == 'Radiobutton':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(
                            bg=colors['bg_primary'],
                            fg=colors['text_primary'],
                            selectcolor=bg_input,
                            activebackground=highlight,
                            activeforeground=colors['text_primary'],
                            highlightbackground=colors['bg_primary']
                        )
                except tk.TclError:
                    pass
            
            # Update tk.Spinbox
            elif widget_class == 'Spinbox':
                try:
                    widget.configure(
                        bg=bg_input,
                        fg=colors['text_primary'],
                        buttonbackground=colors['bg_secondary'],
                        insertbackground=colors['text_primary'],
                        highlightbackground=border_light,
                        highlightcolor=colors['accent'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff'
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Scale
            elif widget_class == 'Scale':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(
                            bg=colors['bg_primary'],
                            fg=colors['text_primary'],
                            troughcolor=colors['bg_secondary'],
                            activebackground=colors['accent'],
                            highlightbackground=colors['bg_primary']
                        )
                except tk.TclError:
                    pass
            
            # Update tk.LabelFrame
            elif widget_class == 'Labelframe':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    if current_bg not in self.BRANDING_BG_COLORS:
                        widget.configure(
                            bg=colors['bg_primary'],
                            fg=colors['text_primary'],
                            highlightbackground=border_light,
                            highlightcolor=border_light
                        )
                except tk.TclError:
                    pass
            
            # Update tk.Scrollbar
            elif widget_class == 'Scrollbar':
                try:
                    widget.configure(
                        bg=highlight,
                        troughcolor=colors['bg_secondary'],
                        activebackground=colors['accent'],
                        highlightbackground=colors['bg_primary']
                    )
                except tk.TclError:
                    pass
            
            # Update tk.Menu
            elif widget_class == 'Menu':
                try:
                    widget.configure(
                        bg=colors['bg_card'],
                        fg=colors['text_primary'],
                        activebackground=colors['accent'],
                        activeforeground='#ffffff'
                    )
                except tk.TclError:
                    pass
            
            # Update DateEntry (from tkcalendar)
            elif widget_class == 'DateEntry':
                try:
                    widget.configure(
                        background=colors['accent'],
                        foreground='#ffffff',
                        headersbackground=colors['bg_secondary'],
                        headersforeground=colors['text_primary'],
                        normalbackground=colors['bg_card'],
                        normalforeground=colors['text_primary'],
                        weekendbackground=colors['bg_card'],
                        weekendforeground=colors['text_primary'],
                        selectbackground=colors['accent'],
                        selectforeground='#ffffff'
                    )
                except (tk.TclError, AttributeError):
                    pass
            
            # Update ttk.Label - map light theme colors to dark theme colors
            elif widget_class == 'TLabel':
                try:
                    # Get current foreground color
                    current_style = str(widget.cget('style')) if widget.cget('style') else ''
                    
                    # Only update labels without a specific style (those with hardcoded colors)
                    if not current_style or current_style == 'TLabel':
                        # Map light theme status colors to dark theme equivalents
                        self._update_ttk_label_foreground(widget, colors)
                except tk.TclError:
                    pass
            
            # Update Treeview tags for proper theme colors
            elif widget_class == 'Treeview':
                try:
                    self._update_treeview_tags(widget, colors)
                except tk.TclError:
                    pass
            
            # Update ttk.Frame background
            elif widget_class == 'TFrame':
                try:
                    current_style = str(widget.cget('style')) if widget.cget('style') else ''
                    if current_style == 'Card.TFrame':
                        # Card frames use bg_card
                        pass  # Style already configured
                    # ttk.Frame doesn't have direct bg config, relies on style
                except tk.TclError:
                    pass
            
            # Update ttk.LabelFrame
            elif widget_class == 'TLabelframe':
                try:
                    # ttk.LabelFrame relies on style configuration
                    # Force style refresh
                    current_style = str(widget.cget('style')) if widget.cget('style') else ''
                    if current_style:
                        widget.configure(style=current_style)
                except tk.TclError:
                    pass
            
            # Update ttk.Button - ensure proper style is applied
            elif widget_class == 'TButton':
                try:
                    current_style = str(widget.cget('style')) if widget.cget('style') else ''
                    # Force style refresh by re-applying the style
                    if current_style:
                        widget.configure(style=current_style)
                    else:
                        widget.configure(style='TButton')
                except tk.TclError:
                    pass
            
            # Update ttk.Combobox
            elif widget_class == 'TCombobox':
                try:
                    # Force style refresh
                    widget.configure(style='TCombobox')
                except tk.TclError:
                    pass
            
            # Update ttk.Entry
            elif widget_class == 'TEntry':
                try:
                    # Force style refresh
                    widget.configure(style='TEntry')
                except tk.TclError:
                    pass
            
            # Update ttk.Checkbutton
            elif widget_class == 'TCheckbutton':
                try:
                    widget.configure(style='TCheckbutton')
                except tk.TclError:
                    pass
            
            # Update ttk.Radiobutton
            elif widget_class == 'TRadiobutton':
                try:
                    widget.configure(style='TRadiobutton')
                except tk.TclError:
                    pass
            
            # Update ttk.Progressbar
            elif widget_class == 'TProgressbar' or widget_class == 'Horizontal.TProgressbar':
                try:
                    current_style = str(widget.cget('style')) if widget.cget('style') else ''
                    if current_style:
                        widget.configure(style=current_style)
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
    
    def _update_treeview_tags(self, treeview: tk.Widget, colors: Dict[str, str]) -> None:
        """
        Update Treeview tags for proper theme colors.
        
        Args:
            treeview: Treeview widget to update
            colors: Current theme colors
        """
        try:
            # Update alternating row colors - use same background for consistency
            if self._current_theme == 'dark':
                # Dark theme - unified background with subtle alternation
                treeview.tag_configure('oddrow', background=colors['bg_primary'])
                treeview.tag_configure('evenrow', background=colors['bg_secondary'])
                treeview.tag_configure('hover', background=colors.get('highlight', colors['bg_secondary']))
                
                # Status row tags - subtle colored backgrounds
                treeview.tag_configure('success', background='#1a2e1a', foreground=colors['success'])
                treeview.tag_configure('error', background='#2e1a1a', foreground=colors['error'])
                treeview.tag_configure('warning', background='#2e2a1a', foreground=colors['warning'])
                treeview.tag_configure('info', background='#1a2a2e', foreground=colors['accent'])
            else:
                # Light theme - white background with subtle alternation
                treeview.tag_configure('oddrow', background=colors['bg_primary'])
                treeview.tag_configure('evenrow', background='#fafafa')
                treeview.tag_configure('hover', background=colors.get('highlight', colors['bg_secondary']))
                
                # Status row tags - light colored backgrounds
                treeview.tag_configure('success', background='#E6F4E6', foreground='#107C10')
                treeview.tag_configure('error', background='#FDE7E7', foreground='#D13438')
                treeview.tag_configure('warning', background='#FFF4E5', foreground='#FF8C00')
                treeview.tag_configure('info', background='#E6F2FA', foreground='#0078D4')
            
            # Update result column tags
            treeview.tag_configure('success_result', foreground=colors['success'], font=('Segoe UI', 12, 'bold'))
            treeview.tag_configure('error_result', foreground=colors['error'], font=('Segoe UI', 12, 'bold'))
            
        except Exception:
            pass  # Ignore errors for treeviews that can't be configured
    
    # Light theme colors that need to be mapped to dark theme equivalents
    LIGHT_TO_DARK_COLOR_MAP = {
        '#0078d4': 'accent',      # INFO_COLOR -> accent
        '#107c10': 'success',     # SUCCESS_COLOR -> success
        '#d13438': 'error',       # ERROR_COLOR -> error
        '#ff8c00': 'warning',     # WARNING_COLOR -> warning
        '#605e5c': 'text_secondary',  # TEXT_SECONDARY -> text_secondary
        '#323130': 'text_primary',    # TEXT_PRIMARY -> text_primary
        # Also handle lowercase versions
        '#1565c0': 'accent',      # Light theme accent
        '#2e7d32': 'success',     # Light theme success
        '#c62828': 'error',       # Light theme error
        '#b45309': 'warning',     # Light theme warning
    }
    
    def _update_ttk_label_foreground(self, widget: tk.Widget, colors: Dict[str, str]) -> None:
        """
        Update ttk.Label foreground color based on current theme.
        Maps semantic colors to theme equivalents.
        
        Args:
            widget: ttk.Label widget
            colors: Current theme colors
        """
        try:
            # Try to get the current foreground color from the widget
            # ttk widgets store foreground in their configuration
            current_fg = ''
            try:
                current_fg = str(widget.cget('foreground')).lower()
            except:
                pass
            
            if not current_fg:
                return
            
            # Map semantic colors to theme colors
            semantic_color_map = {
                'green': colors['success'],
                'red': colors['error'],
                'blue': colors['accent'],
                'orange': colors['warning'],
                'gray': colors['text_secondary'],
                'grey': colors['text_secondary'],
                # Hex versions
                '#228b22': colors['success'],
                '#dc143c': colors['error'],
                '#107c10': colors['success'],
                '#d13438': colors['error'],
                '#0078d4': colors['accent'],
                '#ff8c00': colors['warning'],
                '#666666': colors['text_secondary'],
                '#888888': colors['text_secondary'],
            }
            
            # Check if current foreground is a semantic color
            if current_fg in semantic_color_map:
                widget.configure(foreground=semantic_color_map[current_fg])
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
        
        # Get bg_input with fallback
        bg_input = dark.get('bg_input', dark['bg_card'])
        
        # Text on primary background
        pairs = [
            ('text_primary on bg_primary', dark['text_primary'], dark['bg_primary']),
            ('text_primary on bg_secondary', dark['text_primary'], dark['bg_secondary']),
            ('text_primary on bg_card', dark['text_primary'], dark['bg_card']),
            ('text_primary on bg_input', dark['text_primary'], bg_input),
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
        bg_input = colors.get('bg_input', colors['bg_card'])
        
        return [
            ('text_primary on bg_primary', colors['text_primary'], colors['bg_primary']),
            ('text_primary on bg_secondary', colors['text_primary'], colors['bg_secondary']),
            ('text_primary on bg_card', colors['text_primary'], colors['bg_card']),
            ('text_primary on bg_input', colors['text_primary'], bg_input),
            ('text_secondary on bg_primary', colors['text_secondary'], colors['bg_primary']),
            ('text_secondary on bg_secondary', colors['text_secondary'], colors['bg_secondary']),
            ('text_secondary on bg_card', colors['text_secondary'], colors['bg_card']),
            ('accent on bg_primary', colors['accent'], colors['bg_primary']),
            ('success on bg_primary', colors['success'], colors['bg_primary']),
            ('error on bg_primary', colors['error'], colors['bg_primary']),
            ('warning on bg_primary', colors['warning'], colors['bg_primary']),
        ]
