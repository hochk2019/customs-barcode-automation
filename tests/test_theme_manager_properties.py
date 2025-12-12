"""
Property-based tests for Theme Manager

These tests use Hypothesis to verify correctness properties for theme management,
particularly the color contrast requirements for accessibility.

**Feature: v1.3-enhancements**
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings, assume
import pytest

from gui.theme_manager import ThemeManager
from config.configuration_manager import ConfigurationManager


# Strategy for generating valid hex colors
hex_color_strategy = st.from_regex(r'^#[0-9a-fA-F]{6}$', fullmatch=True)


def create_test_config():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write("""[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = test123
timeout = 30

[BarcodeService]
api_url = http://test.com/api
primary_web_url = https://test.com/primary
backup_web_url = https://test.com/backup
timeout = 30

[Application]
output_directory = C:\\Test
polling_interval = 300
max_retries = 3
retry_delay = 5
operation_mode = automatic

[Logging]
log_level = INFO
log_file = logs/app.log
max_log_size = 10485760
backup_count = 5
""")
    return config_path


# Strategy for text/background color pairs in dark theme
dark_theme_pairs_strategy = st.sampled_from([
    ('text_primary', 'bg_primary'),
    ('text_primary', 'bg_secondary'),
    ('text_primary', 'bg_card'),
    ('text_secondary', 'bg_primary'),
    ('text_secondary', 'bg_secondary'),
    ('text_secondary', 'bg_card'),
    ('accent', 'bg_primary'),
    ('success', 'bg_primary'),
    ('error', 'bg_primary'),
    ('warning', 'bg_primary'),
])


# **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
# **Validates: Requirements 7.3**
@given(color_pair=dark_theme_pairs_strategy)
@settings(max_examples=100)
def test_property_dark_theme_color_contrast(color_pair):
    """
    For any text color and background color pair in dark theme,
    the contrast ratio should be at least 4.5:1.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    text_key, bg_key = color_pair
    dark_theme = ThemeManager.DARK_THEME
    
    text_color = dark_theme[text_key]
    bg_color = dark_theme[bg_key]
    
    min_contrast_ratio = 4.5
    ratio = ThemeManager.calculate_contrast_ratio(text_color, bg_color)
    
    assert ratio >= min_contrast_ratio, \
        f"Dark theme contrast ratio for {text_key} on {bg_key} is {ratio:.2f}:1, " \
        f"but minimum required is {min_contrast_ratio}:1"


# Strategy for text/background color pairs in light theme
light_theme_pairs_strategy = st.sampled_from([
    ('text_primary', 'bg_primary'),
    ('text_primary', 'bg_secondary'),
    ('text_primary', 'bg_card'),
    ('text_secondary', 'bg_primary'),
    ('text_secondary', 'bg_secondary'),
    ('text_secondary', 'bg_card'),
    ('accent', 'bg_primary'),
    ('success', 'bg_primary'),
    ('error', 'bg_primary'),
    ('warning', 'bg_primary'),
])


# **Feature: v1.3-enhancements, Property 8: Theme Color Contrast (Light Theme)**
# **Validates: Requirements 7.3**
@given(color_pair=light_theme_pairs_strategy)
@settings(max_examples=100)
def test_property_light_theme_color_contrast(color_pair):
    """
    For any text color and background color pair in light theme,
    the contrast ratio should be at least 4.5:1.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    text_key, bg_key = color_pair
    light_theme = ThemeManager.LIGHT_THEME
    
    text_color = light_theme[text_key]
    bg_color = light_theme[bg_key]
    
    min_contrast_ratio = 4.5
    ratio = ThemeManager.calculate_contrast_ratio(text_color, bg_color)
    
    assert ratio >= min_contrast_ratio, \
        f"Light theme contrast ratio for {text_key} on {bg_key} is {ratio:.2f}:1, " \
        f"but minimum required is {min_contrast_ratio}:1"


# Property test for contrast ratio calculation correctness
@given(
    color1=hex_color_strategy,
    color2=hex_color_strategy
)
@settings(max_examples=100)
def test_property_contrast_ratio_bounds(color1, color2):
    """
    For any two colors, the contrast ratio should be between 1.0 and 21.0.
    
    The WCAG contrast ratio formula always produces values in this range:
    - Minimum: 1.0 (identical colors)
    - Maximum: 21.0 (black on white or white on black)
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    ratio = ThemeManager.calculate_contrast_ratio(color1, color2)
    
    assert 1.0 <= ratio <= 21.0, \
        f"Contrast ratio {ratio} for {color1} and {color2} is outside valid range [1.0, 21.0]"


# Property test for contrast ratio symmetry
@given(
    color1=hex_color_strategy,
    color2=hex_color_strategy
)
@settings(max_examples=100)
def test_property_contrast_ratio_symmetry(color1, color2):
    """
    For any two colors, the contrast ratio should be the same regardless of order.
    
    contrast_ratio(A, B) == contrast_ratio(B, A)
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    ratio_ab = ThemeManager.calculate_contrast_ratio(color1, color2)
    ratio_ba = ThemeManager.calculate_contrast_ratio(color2, color1)
    
    assert abs(ratio_ab - ratio_ba) < 0.001, \
        f"Contrast ratio should be symmetric: {ratio_ab} != {ratio_ba}"


# Property test for identical colors
@given(color=hex_color_strategy)
@settings(max_examples=100)
def test_property_contrast_ratio_identical_colors(color):
    """
    For any color compared with itself, the contrast ratio should be exactly 1.0.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    ratio = ThemeManager.calculate_contrast_ratio(color, color)
    
    assert abs(ratio - 1.0) < 0.001, \
        f"Contrast ratio for identical colors should be 1.0, but got {ratio}"


# Property test for black and white contrast
def test_property_contrast_ratio_black_white():
    """
    The contrast ratio between pure black and pure white should be 21.0.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.3**
    """
    ratio = ThemeManager.calculate_contrast_ratio('#000000', '#ffffff')
    
    assert abs(ratio - 21.0) < 0.1, \
        f"Contrast ratio for black/white should be ~21.0, but got {ratio}"


# Property test for theme color retrieval
@given(theme=st.sampled_from(['light', 'dark']))
@settings(max_examples=100)
def test_property_theme_colors_complete(theme):
    """
    For any theme, all required color keys should be present.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.1, 7.2**
    """
    required_keys = [
        'bg_primary', 'bg_secondary', 'bg_card',
        'text_primary', 'text_secondary',
        'accent', 'success', 'error', 'warning', 'border'
    ]
    
    theme_colors = ThemeManager.DARK_THEME if theme == 'dark' else ThemeManager.LIGHT_THEME
    
    for key in required_keys:
        assert key in theme_colors, \
            f"Theme '{theme}' is missing required color key: {key}"
        
        # Verify it's a valid hex color
        color = theme_colors[key]
        assert color.startswith('#'), \
            f"Color {key} in theme '{theme}' should start with #"
        assert len(color) == 7, \
            f"Color {key} in theme '{theme}' should be 7 characters (#RRGGBB)"


# Property test for theme toggle
def test_property_theme_toggle_round_trip():
    """
    Toggling theme twice should return to the original theme.
    
    **Feature: v1.3-enhancements, Property 8: Theme Color Contrast**
    **Validates: Requirements 7.4, 7.6**
    """
    config_path = create_test_config()
    
    try:
        # We can't create a real Tk window in tests, so we test the logic directly
        config_manager = ConfigurationManager(config_path)
        
        # Test starting from light theme
        config_manager.set_theme('light')
        assert config_manager.get_theme() == 'light'
        
        # Toggle to dark
        current = config_manager.get_theme()
        new_theme = 'dark' if current == 'light' else 'light'
        config_manager.set_theme(new_theme)
        assert config_manager.get_theme() == 'dark'
        
        # Toggle back to light
        current = config_manager.get_theme()
        new_theme = 'dark' if current == 'light' else 'light'
        config_manager.set_theme(new_theme)
        assert config_manager.get_theme() == 'light'
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)
