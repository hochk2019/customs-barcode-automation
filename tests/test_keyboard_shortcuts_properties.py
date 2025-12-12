"""
Property-based tests for Keyboard Shortcuts Manager

**Feature: v1.3-enhancements**
"""

from hypothesis import given, strategies as st, settings
import pytest

from gui.keyboard_shortcuts import KeyboardShortcutManager, ShortcutInfo


class MockTk:
    """Mock Tk root for testing"""
    
    def __init__(self):
        self._bindings = {}
    
    def bind(self, key, callback):
        self._bindings[key] = callback
    
    def unbind(self, key):
        if key in self._bindings:
            del self._bindings[key]


# Strategy for shortcut keys
shortcut_key_strategy = st.sampled_from([
    'F5', 'F1', 'F2', 'F12',
    'Ctrl+A', 'Ctrl+S', 'Ctrl+Z',
    'Ctrl+Shift+A', 'Ctrl+Shift+S',
    'Escape'
])


# **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
# **Validates: Requirements 5.2, 5.3**
@given(shortcut_key=shortcut_key_strategy)
@settings(max_examples=100)
def test_property_shortcut_registration(shortcut_key):
    """
    For any shortcut key, registering it should make it available in shortcuts.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.2, 5.3**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    callback_called = [False]
    
    def test_callback():
        callback_called[0] = True
    
    # Register shortcut
    manager.register_shortcut(shortcut_key, test_callback, "Test description")
    
    # Verify shortcut is registered
    shortcuts = manager.get_shortcuts_help()
    assert shortcut_key in shortcuts, f"Shortcut {shortcut_key} should be registered"
    assert shortcuts[shortcut_key] == "Test description"


# **Feature: v1.3-enhancements, Property 6: Selection Shortcuts - Unregister**
# **Validates: Requirements 5.2, 5.3**
@given(shortcut_key=shortcut_key_strategy)
@settings(max_examples=100)
def test_property_shortcut_unregistration(shortcut_key):
    """
    For any registered shortcut, unregistering it should remove it from shortcuts.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.2, 5.3**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Register shortcut
    manager.register_shortcut(shortcut_key, lambda: None, "Test")
    
    # Verify registered
    assert shortcut_key in manager.get_shortcuts_help()
    
    # Unregister
    manager.unregister_shortcut(shortcut_key)
    
    # Verify unregistered
    assert shortcut_key not in manager.get_shortcuts_help()


# **Feature: v1.3-enhancements, Property 6: Key Conversion**
# **Validates: Requirements 5.2, 5.3**
def test_property_key_conversion_f_keys():
    """
    F-keys should be converted to correct Tk format.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.1**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Test F-key conversions
    assert manager._convert_to_tk_key('F5') == '<F5>'
    assert manager._convert_to_tk_key('F1') == '<F1>'
    assert manager._convert_to_tk_key('F12') == '<F12>'


def test_property_key_conversion_ctrl():
    """
    Ctrl combinations should be converted to correct Tk format.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.2**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Test Ctrl combinations
    assert manager._convert_to_tk_key('Ctrl+A') == '<Control-a>'
    assert manager._convert_to_tk_key('Ctrl+S') == '<Control-s>'


def test_property_key_conversion_ctrl_shift():
    """
    Ctrl+Shift combinations should be converted to correct Tk format.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.3**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Test Ctrl+Shift combinations
    assert manager._convert_to_tk_key('Ctrl+Shift+A') == '<Control-Shift-a>'


def test_property_key_conversion_escape():
    """
    Escape key should be converted to correct Tk format.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.4**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    assert manager._convert_to_tk_key('Escape') == '<Escape>'


# **Feature: v1.3-enhancements, Property 6: Default Shortcuts**
# **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
def test_property_default_shortcuts_registration():
    """
    Registering default shortcuts should register all four shortcuts.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Register all default shortcuts
    manager.register_default_shortcuts(
        refresh_callback=lambda: None,
        select_all_callback=lambda: None,
        deselect_all_callback=lambda: None,
        stop_callback=lambda: None
    )
    
    shortcuts = manager.get_shortcuts_help()
    
    # Verify all default shortcuts are registered
    assert 'F5' in shortcuts
    assert 'Ctrl+A' in shortcuts
    assert 'Ctrl+Shift+A' in shortcuts
    assert 'Escape' in shortcuts


def test_property_clear_all_shortcuts():
    """
    Clearing all shortcuts should remove all registered shortcuts.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.2, 5.3**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Register some shortcuts
    manager.register_shortcut('F5', lambda: None)
    manager.register_shortcut('Ctrl+A', lambda: None)
    
    # Verify registered
    assert len(manager.get_shortcuts_help()) == 2
    
    # Clear all
    manager.clear_all()
    
    # Verify all cleared
    assert len(manager.get_shortcuts_help()) == 0


def test_property_shortcut_tooltip():
    """
    Tooltip should return correct shortcut hint.
    
    **Feature: v1.3-enhancements, Property 6: Selection Shortcuts**
    **Validates: Requirements 5.5**
    """
    mock_root = MockTk()
    manager = KeyboardShortcutManager(mock_root)
    
    # Register shortcuts
    manager.register_shortcut('F5', lambda: None)
    manager.register_shortcut('Ctrl+A', lambda: None)
    
    # Test tooltips
    assert manager.get_shortcut_tooltip('refresh') == '(F5)'
    assert manager.get_shortcut_tooltip('select_all') == '(Ctrl+A)'
    
    # Unknown action should return empty
    assert manager.get_shortcut_tooltip('unknown') == ''
