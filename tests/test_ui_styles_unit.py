"""
Unit tests for ModernStyles module.

These tests verify the styling functionality for the modern UI.
Requirements: 4.1
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import tkinter as tk
from tkinter import ttk


class TestModernStylesColorConstants:
    """Test that color constants are valid hex codes."""
    
    def test_primary_color_is_valid_hex(self):
        """Test PRIMARY_COLOR is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.PRIMARY_COLOR)
        assert ModernStyles.PRIMARY_COLOR == "#0078D4"
    
    def test_primary_hover_is_valid_hex(self):
        """Test PRIMARY_HOVER is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.PRIMARY_HOVER)
    
    def test_primary_pressed_is_valid_hex(self):
        """Test PRIMARY_PRESSED is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.PRIMARY_PRESSED)
    
    def test_success_color_is_valid_hex(self):
        """Test SUCCESS_COLOR is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.SUCCESS_COLOR)
        assert ModernStyles.SUCCESS_COLOR == "#107C10"
    
    def test_error_color_is_valid_hex(self):
        """Test ERROR_COLOR is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.ERROR_COLOR)
        assert ModernStyles.ERROR_COLOR == "#D13438"
    
    def test_warning_color_is_valid_hex(self):
        """Test WARNING_COLOR is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.WARNING_COLOR)
        assert ModernStyles.WARNING_COLOR == "#FF8C00"
    
    def test_info_color_is_valid_hex(self):
        """Test INFO_COLOR is a valid hex color."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color(ModernStyles.INFO_COLOR)
        assert ModernStyles.INFO_COLOR == "#0078D4"
    
    def test_all_background_colors_are_valid_hex(self):
        """Test all background colors are valid hex codes."""
        from gui.styles import ModernStyles
        bg_colors = [
            ModernStyles.BG_PRIMARY,
            ModernStyles.BG_SECONDARY,
            ModernStyles.BG_TERTIARY,
            ModernStyles.BG_HOVER,
            ModernStyles.BG_SELECTED
        ]
        for color in bg_colors:
            assert ModernStyles.is_valid_hex_color(color), f"{color} is not a valid hex color"
    
    def test_all_border_colors_are_valid_hex(self):
        """Test all border colors are valid hex codes."""
        from gui.styles import ModernStyles
        border_colors = [
            ModernStyles.BORDER_COLOR,
            ModernStyles.BORDER_FOCUS,
            ModernStyles.BORDER_SUBTLE
        ]
        for color in border_colors:
            assert ModernStyles.is_valid_hex_color(color), f"{color} is not a valid hex color"
    
    def test_all_text_colors_are_valid_hex(self):
        """Test all text colors are valid hex codes."""
        from gui.styles import ModernStyles
        text_colors = [
            ModernStyles.TEXT_PRIMARY,
            ModernStyles.TEXT_SECONDARY,
            ModernStyles.TEXT_DISABLED,
            ModernStyles.TEXT_ON_PRIMARY
        ]
        for color in text_colors:
            assert ModernStyles.is_valid_hex_color(color), f"{color} is not a valid hex color"


class TestIsValidHexColor:
    """Test the is_valid_hex_color utility method."""
    
    def test_valid_6_digit_hex(self):
        """Test valid 6-digit hex colors."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color("#FFFFFF")
        assert ModernStyles.is_valid_hex_color("#000000")
        assert ModernStyles.is_valid_hex_color("#0078D4")
        assert ModernStyles.is_valid_hex_color("#abcdef")
    
    def test_valid_3_digit_hex(self):
        """Test valid 3-digit hex colors."""
        from gui.styles import ModernStyles
        assert ModernStyles.is_valid_hex_color("#FFF")
        assert ModernStyles.is_valid_hex_color("#000")
        assert ModernStyles.is_valid_hex_color("#abc")
    
    def test_invalid_hex_no_hash(self):
        """Test invalid hex without hash prefix."""
        from gui.styles import ModernStyles
        assert not ModernStyles.is_valid_hex_color("FFFFFF")
        assert not ModernStyles.is_valid_hex_color("0078D4")
    
    def test_invalid_hex_wrong_length(self):
        """Test invalid hex with wrong length."""
        from gui.styles import ModernStyles
        assert not ModernStyles.is_valid_hex_color("#FF")
        assert not ModernStyles.is_valid_hex_color("#FFFF")
        assert not ModernStyles.is_valid_hex_color("#FFFFFFFF")
    
    def test_invalid_hex_non_hex_chars(self):
        """Test invalid hex with non-hex characters."""
        from gui.styles import ModernStyles
        assert not ModernStyles.is_valid_hex_color("#GGGGGG")
        assert not ModernStyles.is_valid_hex_color("#ZZZZZZ")
    
    def test_invalid_hex_non_string(self):
        """Test invalid hex with non-string input."""
        from gui.styles import ModernStyles
        assert not ModernStyles.is_valid_hex_color(None)
        assert not ModernStyles.is_valid_hex_color(123456)
        assert not ModernStyles.is_valid_hex_color(['#FFFFFF'])


class TestGetStatusColor:
    """Test the get_status_color method."""
    
    def test_success_status_returns_green(self):
        """Test success status returns SUCCESS_COLOR."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('success') == ModernStyles.SUCCESS_COLOR
    
    def test_error_status_returns_red(self):
        """Test error status returns ERROR_COLOR."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('error') == ModernStyles.ERROR_COLOR
    
    def test_warning_status_returns_orange(self):
        """Test warning status returns WARNING_COLOR."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('warning') == ModernStyles.WARNING_COLOR
    
    def test_info_status_returns_blue(self):
        """Test info status returns INFO_COLOR."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('info') == ModernStyles.INFO_COLOR
    
    def test_case_insensitive_status(self):
        """Test status lookup is case-insensitive."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('SUCCESS') == ModernStyles.SUCCESS_COLOR
        assert ModernStyles.get_status_color('Error') == ModernStyles.ERROR_COLOR
        assert ModernStyles.get_status_color('WARNING') == ModernStyles.WARNING_COLOR
        assert ModernStyles.get_status_color('INFO') == ModernStyles.INFO_COLOR
    
    def test_unknown_status_returns_default(self):
        """Test unknown status returns TEXT_PRIMARY as default."""
        from gui.styles import ModernStyles
        assert ModernStyles.get_status_color('unknown') == ModernStyles.TEXT_PRIMARY
        assert ModernStyles.get_status_color('') == ModernStyles.TEXT_PRIMARY


class TestGetButtonConfig:
    """Test the get_button_config method."""
    
    def test_primary_button_config(self):
        """Test primary button configuration for light theme."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('primary', 'light')
        
        assert config['bg'] == ModernStyles.PRIMARY_COLOR
        assert config['fg'] == '#ffffff'
        assert config['activebackground'] == ModernStyles.PRIMARY_COLOR
        assert config['relief'] == 'flat'
        assert config['cursor'] == 'hand2'
    
    def test_success_button_config(self):
        """Test success button configuration for light theme."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('success', 'light')
        
        assert config['bg'] == ModernStyles.SUCCESS_COLOR
        assert config['fg'] == '#ffffff'
    
    def test_danger_button_config(self):
        """Test danger button configuration for light theme."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('danger', 'light')
        
        assert config['bg'] == ModernStyles.ERROR_COLOR
        assert config['fg'] == '#ffffff'
    
    def test_secondary_button_config(self):
        """Test secondary button configuration for light theme."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('secondary', 'light')
        
        assert config['bg'] == ModernStyles.BG_SECONDARY
        assert config['fg'] == ModernStyles.TEXT_PRIMARY
        assert config['relief'] == 'solid'
    
    def test_dark_theme_button_config(self):
        """Test button configuration for dark theme."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('primary', 'dark')
        
        # Dark theme uses different accent color
        assert config['bg'] == '#4da6ff'  # Dark theme accent
        assert config['fg'] == '#ffffff'
    
    def test_warning_button_config(self):
        """Test warning button configuration."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('warning', 'light')
        
        assert config['bg'] == ModernStyles.WARNING_COLOR
        assert config['fg'] == '#ffffff'  # Light theme uses white text on warning
    
    def test_unknown_button_type_returns_primary(self):
        """Test unknown button type returns primary config."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config('unknown')
        primary_config = ModernStyles.get_button_config('primary')
        
        assert config == primary_config
    
    def test_default_button_type_is_primary(self):
        """Test default button type is primary."""
        from gui.styles import ModernStyles
        config = ModernStyles.get_button_config()
        primary_config = ModernStyles.get_button_config('primary')
        
        assert config == primary_config


class TestConfigureTtkStyles:
    """Test the configure_ttk_styles method."""
    
    @pytest.fixture
    def mock_tk_root(self):
        """Create a mock Tk root window."""
        with patch('tkinter.Tk') as mock_tk:
            root = MagicMock()
            mock_tk.return_value = root
            yield root
    
    def test_configure_ttk_styles_returns_style_object(self, mock_tk_root):
        """Test that configure_ttk_styles returns a ttk.Style object."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['clam', 'default']
            mock_style_class.return_value = mock_style
            
            result = ModernStyles.configure_ttk_styles(mock_tk_root)
            
            assert result == mock_style
            mock_style_class.assert_called_once_with(mock_tk_root)
    
    def test_configure_ttk_styles_uses_clam_theme_if_available(self, mock_tk_root):
        """Test that clam theme is used if available."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['clam', 'default', 'vista']
            mock_style_class.return_value = mock_style
            
            ModernStyles.configure_ttk_styles(mock_tk_root)
            
            mock_style.theme_use.assert_called_with('clam')
    
    def test_configure_ttk_styles_uses_vista_theme_as_fallback(self, mock_tk_root):
        """Test that vista theme is used as fallback."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['default', 'vista']
            mock_style_class.return_value = mock_style
            
            ModernStyles.configure_ttk_styles(mock_tk_root)
            
            mock_style.theme_use.assert_called_with('vista')
    
    def test_configure_ttk_styles_configures_button_style(self, mock_tk_root):
        """Test that TButton style is configured."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['clam']
            mock_style_class.return_value = mock_style
            
            ModernStyles.configure_ttk_styles(mock_tk_root)
            
            # Check that configure was called for TButton
            configure_calls = [call for call in mock_style.configure.call_args_list 
                             if call[0][0] == 'TButton']
            assert len(configure_calls) > 0
    
    def test_configure_ttk_styles_configures_entry_style(self, mock_tk_root):
        """Test that TEntry style is configured."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['clam']
            mock_style_class.return_value = mock_style
            
            ModernStyles.configure_ttk_styles(mock_tk_root)
            
            # Check that configure was called for TEntry
            configure_calls = [call for call in mock_style.configure.call_args_list 
                             if call[0][0] == 'TEntry']
            assert len(configure_calls) > 0
    
    def test_configure_ttk_styles_configures_treeview_style(self, mock_tk_root):
        """Test that Treeview style is configured."""
        from gui.styles import ModernStyles
        
        with patch('tkinter.ttk.Style') as mock_style_class:
            mock_style = MagicMock()
            mock_style.theme_names.return_value = ['clam']
            mock_style_class.return_value = mock_style
            
            ModernStyles.configure_ttk_styles(mock_tk_root)
            
            # Check that configure was called for Treeview
            configure_calls = [call for call in mock_style.configure.call_args_list 
                             if call[0][0] == 'Treeview']
            assert len(configure_calls) > 0


class TestConfigureTreeviewTags:
    """Test the configure_treeview_tags method."""
    
    def test_configure_treeview_tags_sets_oddrow(self):
        """Test that oddrow tag is configured."""
        from gui.styles import ModernStyles
        
        mock_treeview = MagicMock()
        ModernStyles.configure_treeview_tags(mock_treeview)
        
        # Check oddrow tag was configured
        oddrow_calls = [call for call in mock_treeview.tag_configure.call_args_list 
                       if call[0][0] == 'oddrow']
        assert len(oddrow_calls) == 1
    
    def test_configure_treeview_tags_sets_evenrow(self):
        """Test that evenrow tag is configured."""
        from gui.styles import ModernStyles
        
        mock_treeview = MagicMock()
        ModernStyles.configure_treeview_tags(mock_treeview)
        
        # Check evenrow tag was configured
        evenrow_calls = [call for call in mock_treeview.tag_configure.call_args_list 
                        if call[0][0] == 'evenrow']
        assert len(evenrow_calls) == 1
    
    def test_configure_treeview_tags_sets_status_tags(self):
        """Test that status tags are configured."""
        from gui.styles import ModernStyles
        
        mock_treeview = MagicMock()
        ModernStyles.configure_treeview_tags(mock_treeview)
        
        # Check status tags were configured
        tag_names = [call[0][0] for call in mock_treeview.tag_configure.call_args_list]
        assert 'success' in tag_names
        assert 'error' in tag_names
        assert 'warning' in tag_names
        assert 'info' in tag_names


class TestFontConstants:
    """Test font-related constants."""
    
    def test_font_family_is_string(self):
        """Test FONT_FAMILY is a string."""
        from gui.styles import ModernStyles
        assert isinstance(ModernStyles.FONT_FAMILY, str)
        assert len(ModernStyles.FONT_FAMILY) > 0
    
    def test_font_sizes_are_positive_integers(self):
        """Test font sizes are positive integers."""
        from gui.styles import ModernStyles
        assert isinstance(ModernStyles.FONT_SIZE_NORMAL, int)
        assert isinstance(ModernStyles.FONT_SIZE_SMALL, int)
        assert isinstance(ModernStyles.FONT_SIZE_LARGE, int)
        assert isinstance(ModernStyles.FONT_SIZE_HEADER, int)
        
        assert ModernStyles.FONT_SIZE_NORMAL > 0
        assert ModernStyles.FONT_SIZE_SMALL > 0
        assert ModernStyles.FONT_SIZE_LARGE > 0
        assert ModernStyles.FONT_SIZE_HEADER > 0
    
    def test_font_size_ordering(self):
        """Test font sizes are in correct order."""
        from gui.styles import ModernStyles
        assert ModernStyles.FONT_SIZE_SMALL < ModernStyles.FONT_SIZE_NORMAL
        assert ModernStyles.FONT_SIZE_NORMAL < ModernStyles.FONT_SIZE_LARGE
        assert ModernStyles.FONT_SIZE_LARGE <= ModernStyles.FONT_SIZE_HEADER


class TestPaddingConstants:
    """Test padding-related constants."""
    
    def test_padding_values_are_positive_integers(self):
        """Test padding values are positive integers."""
        from gui.styles import ModernStyles
        assert isinstance(ModernStyles.PADDING_SMALL, int)
        assert isinstance(ModernStyles.PADDING_NORMAL, int)
        assert isinstance(ModernStyles.PADDING_LARGE, int)
        
        assert ModernStyles.PADDING_SMALL > 0
        assert ModernStyles.PADDING_NORMAL > 0
        assert ModernStyles.PADDING_LARGE > 0
    
    def test_padding_ordering(self):
        """Test padding values are in correct order."""
        from gui.styles import ModernStyles
        assert ModernStyles.PADDING_SMALL < ModernStyles.PADDING_NORMAL
        assert ModernStyles.PADDING_NORMAL < ModernStyles.PADDING_LARGE
