"""
Modern styling module for Customs Barcode Automation GUI.

This module provides centralized styling definitions for a modern UI appearance.
Implements Requirements 4.1, 4.2, 4.3, 4.4, 4.6, 4.7, 4.8.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Tuple


class ModernStyles:
    """Centralized styling for modern UI appearance."""
    
    # Color Palette - Primary colors for interactive elements
    PRIMARY_COLOR = "#0078D4"      # Microsoft Blue (Requirement 4.1)
    PRIMARY_HOVER = "#106EBE"      # Darker blue for hover
    PRIMARY_PRESSED = "#005A9E"    # Even darker for pressed state
    
    # Status Colors (Requirement 4.6)
    SUCCESS_COLOR = "#107C10"      # Green for success
    ERROR_COLOR = "#D13438"        # Red for error
    WARNING_COLOR = "#FF8C00"      # Orange for warning
    INFO_COLOR = "#0078D4"         # Blue for info
    
    # Background Colors
    BG_PRIMARY = "#FFFFFF"         # White - main background
    BG_SECONDARY = "#F5F5F5"       # Light gray - secondary background
    BG_TERTIARY = "#FAFAFA"        # Very light gray - alternate rows
    BG_HOVER = "#E8E8E8"           # Hover state background
    BG_SELECTED = "#CCE4F7"        # Selected item background
    
    # Border Colors
    BORDER_COLOR = "#D1D1D1"       # Light border
    BORDER_FOCUS = "#0078D4"       # Focus border (matches primary)
    BORDER_SUBTLE = "#E5E5E5"      # Very subtle border
    
    # Text Colors
    TEXT_PRIMARY = "#323130"       # Dark gray - main text
    TEXT_SECONDARY = "#605E5C"     # Medium gray - secondary text
    TEXT_DISABLED = "#A19F9D"      # Light gray - disabled text
    TEXT_ON_PRIMARY = "#FFFFFF"    # White text on primary color
    
    # Font Definitions
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 9
    FONT_SIZE_SMALL = 8
    FONT_SIZE_LARGE = 11
    FONT_SIZE_HEADER = 12
    
    # Padding and Spacing
    PADDING_SMALL = 4
    PADDING_NORMAL = 8
    PADDING_LARGE = 12
    
    # Border Radius (for custom drawing)
    BORDER_RADIUS = 4
    
    @classmethod
    def configure_ttk_styles(cls, root: tk.Tk) -> ttk.Style:
        """
        Configure ttk styles for modern appearance.
        
        Args:
            root: The root Tk window
            
        Returns:
            The configured ttk.Style object
        """
        style = ttk.Style(root)
        
        # Try to use a modern theme as base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        
        # Configure TButton style (Requirement 4.2)
        cls._configure_button_style(style)
        
        # Configure TEntry style (Requirement 4.3)
        cls._configure_entry_style(style)
        
        # Configure TCombobox style (Requirement 4.3)
        cls._configure_combobox_style(style)
        
        # Configure TLabelframe style (Requirement 4.4)
        cls._configure_labelframe_style(style)
        
        # Configure Treeview style (Requirement 4.8)
        cls._configure_treeview_style(style)
        
        # Configure TProgressbar style (Requirement 4.7)
        cls._configure_progressbar_style(style)
        
        # Configure TLabel style
        cls._configure_label_style(style)
        
        # Configure TFrame style
        cls._configure_frame_style(style)
        
        return style
    
    @classmethod
    def _configure_button_style(cls, style: ttk.Style) -> None:
        """Configure TButton with rounded appearance and hover effects."""
        # Primary button style
        style.configure(
            'TButton',
            background=cls.PRIMARY_COLOR,
            foreground=cls.TEXT_ON_PRIMARY,
            borderwidth=0,
            focusthickness=0,
            padding=(cls.PADDING_NORMAL, cls.PADDING_SMALL),
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
        )
        style.map(
            'TButton',
            background=[
                ('active', cls.PRIMARY_HOVER),
                ('pressed', cls.PRIMARY_PRESSED),
                ('disabled', cls.BG_SECONDARY)
            ],
            foreground=[
                ('disabled', cls.TEXT_DISABLED)
            ]
        )
        
        # Success button style
        style.configure(
            'Success.TButton',
            background=cls.SUCCESS_COLOR,
            foreground=cls.TEXT_ON_PRIMARY
        )
        style.map(
            'Success.TButton',
            background=[
                ('active', '#0E6B0E'),
                ('pressed', '#0A5A0A'),
                ('disabled', cls.BG_SECONDARY)
            ]
        )
        
        # Danger/Error button style
        style.configure(
            'Danger.TButton',
            background=cls.ERROR_COLOR,
            foreground=cls.TEXT_ON_PRIMARY
        )
        style.map(
            'Danger.TButton',
            background=[
                ('active', '#B52D30'),
                ('pressed', '#962528'),
                ('disabled', cls.BG_SECONDARY)
            ]
        )
        
        # Secondary/Outline button style
        style.configure(
            'Secondary.TButton',
            background=cls.BG_PRIMARY,
            foreground=cls.PRIMARY_COLOR,
            borderwidth=1,
            bordercolor=cls.PRIMARY_COLOR
        )
        style.map(
            'Secondary.TButton',
            background=[
                ('active', cls.BG_HOVER),
                ('pressed', cls.BG_SELECTED)
            ]
        )
    
    @classmethod
    def _configure_entry_style(cls, style: ttk.Style) -> None:
        """Configure TEntry with focus highlighting."""
        style.configure(
            'TEntry',
            fieldbackground=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            borderwidth=1,
            padding=(cls.PADDING_SMALL, cls.PADDING_SMALL),
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
        )
        style.map(
            'TEntry',
            fieldbackground=[
                ('focus', cls.BG_PRIMARY),
                ('disabled', cls.BG_SECONDARY)
            ],
            bordercolor=[
                ('focus', cls.BORDER_FOCUS),
                ('!focus', cls.BORDER_COLOR)
            ],
            lightcolor=[
                ('focus', cls.BORDER_FOCUS)
            ],
            darkcolor=[
                ('focus', cls.BORDER_FOCUS)
            ]
        )
    
    @classmethod
    def _configure_combobox_style(cls, style: ttk.Style) -> None:
        """Configure TCombobox style."""
        style.configure(
            'TCombobox',
            fieldbackground=cls.BG_PRIMARY,
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            arrowcolor=cls.PRIMARY_COLOR,
            borderwidth=1,
            padding=(cls.PADDING_SMALL, cls.PADDING_SMALL),
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
        )
        style.map(
            'TCombobox',
            fieldbackground=[
                ('readonly', cls.BG_PRIMARY),
                ('disabled', cls.BG_SECONDARY)
            ],
            background=[
                ('active', cls.BG_HOVER),
                ('pressed', cls.BG_SELECTED)
            ],
            bordercolor=[
                ('focus', cls.BORDER_FOCUS),
                ('!focus', cls.BORDER_COLOR)
            ],
            arrowcolor=[
                ('disabled', cls.TEXT_DISABLED)
            ]
        )
    
    @classmethod
    def _configure_labelframe_style(cls, style: ttk.Style) -> None:
        """Configure TLabelframe with subtle borders."""
        style.configure(
            'TLabelframe',
            background=cls.BG_PRIMARY,
            borderwidth=1,
            relief='solid',
            bordercolor=cls.BORDER_SUBTLE
        )
        style.configure(
            'TLabelframe.Label',
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, 'bold')
        )
        
        # Card-style labelframe
        style.configure(
            'Card.TLabelframe',
            background=cls.BG_PRIMARY,
            borderwidth=1,
            relief='solid',
            bordercolor=cls.BORDER_COLOR
        )
    
    @classmethod
    def _configure_treeview_style(cls, style: ttk.Style) -> None:
        """Configure Treeview with alternating row colors and hover highlighting."""
        style.configure(
            'Treeview',
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            fieldbackground=cls.BG_PRIMARY,
            borderwidth=0,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
            rowheight=25
        )
        style.configure(
            'Treeview.Heading',
            background=cls.BG_SECONDARY,
            foreground=cls.TEXT_PRIMARY,
            borderwidth=1,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, 'bold')
        )
        style.map(
            'Treeview',
            background=[
                ('selected', cls.BG_SELECTED)
            ],
            foreground=[
                ('selected', cls.TEXT_PRIMARY)
            ]
        )
        style.map(
            'Treeview.Heading',
            background=[
                ('active', cls.BG_HOVER)
            ]
        )
        
        # Configure alternating row tags (to be used with tag_configure)
        # Note: Actual tag configuration must be done on the Treeview widget itself
    
    @classmethod
    def _configure_progressbar_style(cls, style: ttk.Style) -> None:
        """Configure TProgressbar with modern appearance (Requirement 4.7)."""
        # Default progress bar with modern styling
        style.configure(
            'TProgressbar',
            background=cls.PRIMARY_COLOR,
            troughcolor=cls.BG_SECONDARY,
            borderwidth=0,
            thickness=20,
            lightcolor=cls.PRIMARY_COLOR,
            darkcolor=cls.PRIMARY_HOVER
        )
        
        # Success progress bar
        style.configure(
            'Success.TProgressbar',
            background=cls.SUCCESS_COLOR,
            troughcolor=cls.BG_SECONDARY,
            lightcolor=cls.SUCCESS_COLOR,
            darkcolor='#0E6B0E'
        )
        
        # Horizontal progress bar with gradient-like effect (Requirement 4.7)
        style.configure(
            'Horizontal.TProgressbar',
            background=cls.PRIMARY_COLOR,
            troughcolor=cls.BG_SECONDARY,
            borderwidth=0,
            thickness=20,
            lightcolor=cls.PRIMARY_HOVER,
            darkcolor=cls.PRIMARY_PRESSED,
            troughrelief='flat',
            pbarrelief='flat'
        )
        
        # Map for progress bar states
        style.map(
            'Horizontal.TProgressbar',
            background=[
                ('disabled', cls.TEXT_DISABLED)
            ]
        )
    
    @classmethod
    def _configure_label_style(cls, style: ttk.Style) -> None:
        """Configure TLabel styles."""
        style.configure(
            'TLabel',
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL)
        )
        
        # Header label
        style.configure(
            'Header.TLabel',
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_HEADER, 'bold')
        )
        
        # Secondary label
        style.configure(
            'Secondary.TLabel',
            foreground=cls.TEXT_SECONDARY
        )
        
        # Status labels (Requirement 4.6)
        style.configure(
            'Success.TLabel',
            foreground=cls.SUCCESS_COLOR
        )
        style.configure(
            'Error.TLabel',
            foreground=cls.ERROR_COLOR
        )
        style.configure(
            'Warning.TLabel',
            foreground=cls.WARNING_COLOR
        )
        style.configure(
            'Info.TLabel',
            foreground=cls.INFO_COLOR
        )
    
    @classmethod
    def _configure_frame_style(cls, style: ttk.Style) -> None:
        """Configure TFrame styles."""
        style.configure(
            'TFrame',
            background=cls.BG_PRIMARY
        )
        
        # Card frame with subtle shadow effect
        style.configure(
            'Card.TFrame',
            background=cls.BG_PRIMARY,
            borderwidth=1,
            relief='solid'
        )
    
    @classmethod
    def get_status_color(cls, status: str) -> str:
        """
        Get the appropriate color for a status type.
        
        Args:
            status: One of 'success', 'error', 'warning', 'info'
            
        Returns:
            The hex color code for the status
        """
        status_colors = {
            'success': cls.SUCCESS_COLOR,
            'error': cls.ERROR_COLOR,
            'warning': cls.WARNING_COLOR,
            'info': cls.INFO_COLOR
        }
        return status_colors.get(status.lower(), cls.TEXT_PRIMARY)
    
    @classmethod
    def configure_treeview_tags(cls, treeview: ttk.Treeview) -> None:
        """
        Configure alternating row tags for a Treeview widget.
        
        Args:
            treeview: The Treeview widget to configure
        """
        treeview.tag_configure('oddrow', background=cls.BG_PRIMARY)
        treeview.tag_configure('evenrow', background=cls.BG_TERTIARY)
        treeview.tag_configure('hover', background=cls.BG_HOVER)
        
        # Status row tags
        treeview.tag_configure('success', background='#E6F4E6')
        treeview.tag_configure('error', background='#FDE7E7')
        treeview.tag_configure('warning', background='#FFF4E5')
        treeview.tag_configure('info', background='#E6F2FA')
    
    @classmethod
    def get_button_config(cls, button_type: str = 'primary') -> Dict[str, Any]:
        """
        Get configuration dict for tk.Button (non-ttk).
        
        Args:
            button_type: One of 'primary', 'success', 'danger', 'secondary'
            
        Returns:
            Dictionary of button configuration options
        """
        configs = {
            'primary': {
                'bg': cls.PRIMARY_COLOR,
                'fg': cls.TEXT_ON_PRIMARY,
                'activebackground': cls.PRIMARY_HOVER,
                'activeforeground': cls.TEXT_ON_PRIMARY,
                'relief': 'flat',
                'borderwidth': 0,
                'padx': cls.PADDING_NORMAL,
                'pady': cls.PADDING_SMALL,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'cursor': 'hand2'
            },
            'success': {
                'bg': cls.SUCCESS_COLOR,
                'fg': cls.TEXT_ON_PRIMARY,
                'activebackground': '#0E6B0E',
                'activeforeground': cls.TEXT_ON_PRIMARY,
                'relief': 'flat',
                'borderwidth': 0,
                'padx': cls.PADDING_NORMAL,
                'pady': cls.PADDING_SMALL,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'cursor': 'hand2'
            },
            'danger': {
                'bg': cls.ERROR_COLOR,
                'fg': cls.TEXT_ON_PRIMARY,
                'activebackground': '#B52D30',
                'activeforeground': cls.TEXT_ON_PRIMARY,
                'relief': 'flat',
                'borderwidth': 0,
                'padx': cls.PADDING_NORMAL,
                'pady': cls.PADDING_SMALL,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'cursor': 'hand2'
            },
            'secondary': {
                'bg': cls.BG_PRIMARY,
                'fg': cls.PRIMARY_COLOR,
                'activebackground': cls.BG_HOVER,
                'activeforeground': cls.PRIMARY_COLOR,
                'relief': 'solid',
                'borderwidth': 1,
                'padx': cls.PADDING_NORMAL,
                'pady': cls.PADDING_SMALL,
                'font': (cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
                'cursor': 'hand2'
            }
        }
        return configs.get(button_type, configs['primary'])
    
    @classmethod
    def is_valid_hex_color(cls, color: str) -> bool:
        """
        Check if a string is a valid hex color code.
        
        Args:
            color: The color string to validate
            
        Returns:
            True if valid hex color, False otherwise
        """
        if not isinstance(color, str):
            return False
        if not color.startswith('#'):
            return False
        if len(color) not in (4, 7):  # #RGB or #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
