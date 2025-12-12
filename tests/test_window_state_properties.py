"""
Property-based tests for Window State Manager

**Feature: v1.3-enhancements**
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings
import pytest

from gui.window_state import WindowStateManager, WindowState
from config.configuration_manager import ConfigurationManager


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

[UI]
theme = light
notifications_enabled = true
sound_enabled = true
batch_limit = 20
window_x = -1
window_y = -1
window_width = 1200
window_height = 850
""")
    return config_path


class MockTk:
    """Mock Tk root for testing"""
    
    def __init__(self, width=1920, height=1080):
        self._width = 1200
        self._height = 850
        self._x = 100
        self._y = 100
        self._screen_width = width
        self._screen_height = height
    
    def geometry(self, geo=None):
        if geo is None:
            return f"{self._width}x{self._height}+{self._x}+{self._y}"
        # Parse geometry string
        import re
        match = re.match(r'(\d+)x(\d+)([+-]\d+)([+-]\d+)', geo)
        if match:
            self._width = int(match.group(1))
            self._height = int(match.group(2))
            self._x = int(match.group(3))
            self._y = int(match.group(4))
    
    def winfo_screenwidth(self):
        return self._screen_width
    
    def winfo_screenheight(self):
        return self._screen_height


# Strategy for valid window positions
position_strategy = st.integers(min_value=0, max_value=2000)
# ConfigurationManager enforces minimum 800x600
size_strategy = st.integers(min_value=800, max_value=2000)
height_strategy = st.integers(min_value=600, max_value=2000)


# **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
# **Validates: Requirements 6.1, 6.2**
@given(
    x=position_strategy,
    y=position_strategy,
    width=size_strategy,
    height=height_strategy
)
@settings(max_examples=100)
def test_property_window_state_round_trip(x, y, width, height):
    """
    For any valid window position and size, saving state and restoring
    should result in the same position and size.
    
    **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
    **Validates: Requirements 6.1, 6.2**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        mock_root = MockTk()
        manager = WindowStateManager(mock_root, config_manager)
        
        # Set initial geometry
        mock_root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Save state
        manager.save_state()
        
        # Verify saved values
        saved_x = config_manager.get_window_x()
        saved_y = config_manager.get_window_y()
        saved_width = config_manager.get_window_width()
        saved_height = config_manager.get_window_height()
        
        assert saved_x == x, f"X should be {x}, got {saved_x}"
        assert saved_y == y, f"Y should be {y}, got {saved_y}"
        assert saved_width == width, f"Width should be {width}, got {saved_width}"
        assert saved_height == height, f"Height should be {height}, got {saved_height}"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 7: Position Validation**
# **Validates: Requirements 6.3**
@given(
    x=st.integers(min_value=-5000, max_value=5000),
    y=st.integers(min_value=-5000, max_value=5000)
)
@settings(max_examples=100, deadline=None)
def test_property_position_validation(x, y):
    """
    Position validation should correctly identify off-screen positions.
    
    **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
    **Validates: Requirements 6.3**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        mock_root = MockTk(width=1920, height=1080)
        manager = WindowStateManager(mock_root, config_manager)
        
        is_valid = manager.is_position_valid(x, y, 800, 600)
        
        # Position should be valid if at least 100px of window is on screen
        min_visible = 100
        expected_valid = (
            x + 800 >= min_visible and
            y + 600 >= min_visible and
            x <= 1920 - min_visible and
            y <= 1080 - min_visible
        )
        
        assert is_valid == expected_valid, \
            f"Position ({x}, {y}) validation mismatch: got {is_valid}, expected {expected_valid}"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 7: Centered Position**
# **Validates: Requirements 6.4**
def test_property_centered_position():
    """
    Centered position should be in the middle of the screen.
    
    **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
    **Validates: Requirements 6.4**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        mock_root = MockTk(width=1920, height=1080)
        manager = WindowStateManager(mock_root, config_manager)
        
        x, y = manager.get_centered_position(800, 600)
        
        # Should be centered
        expected_x = (1920 - 800) // 2
        expected_y = (1080 - 600) // 2
        
        assert x == expected_x, f"X should be {expected_x}, got {x}"
        assert y == expected_y, f"Y should be {expected_y}, got {y}"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 7: Default Size**
# **Validates: Requirements 6.4**
def test_property_default_size():
    """
    Default size should be 1200x850.
    
    **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
    **Validates: Requirements 6.4**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        mock_root = MockTk()
        manager = WindowStateManager(mock_root, config_manager)
        
        assert manager.DEFAULT_WIDTH == 1200
        assert manager.DEFAULT_HEIGHT == 850
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_property_restore_invalid_position_centers():
    """
    Restoring invalid position should center the window.
    
    **Feature: v1.3-enhancements, Property 7: Window State Round-Trip**
    **Validates: Requirements 6.3**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        # Set invalid position (off screen)
        config_manager.set_window_state(5000, 5000, 800, 600)
        config_manager.save()
        
        mock_root = MockTk(width=1920, height=1080)
        manager = WindowStateManager(mock_root, config_manager)
        
        # Restore should center
        manager.restore_state()
        
        # Check that window was centered
        state = manager.get_current_state()
        expected_x = (1920 - 800) // 2
        expected_y = (1080 - 600) // 2
        
        assert state.x == expected_x, f"X should be centered at {expected_x}, got {state.x}"
        assert state.y == expected_y, f"Y should be centered at {expected_y}, got {state.y}"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)
