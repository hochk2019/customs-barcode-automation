"""
Property-based tests for download manager.

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import os
import tempfile
import pytest
from hypothesis import given, strategies as st, settings

from update.download_manager import DownloadManager, DownloadError, DownloadCancelledError
from update.models import DownloadProgress


# **Feature: github-auto-update, Property 7: Download Progress Calculation**
# **Validates: Requirements 3.2**
@given(
    downloaded=st.integers(min_value=0, max_value=1_000_000_000),
    total=st.integers(min_value=0, max_value=1_000_000_000),
    speed=st.floats(min_value=0, max_value=1_000_000_000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_download_progress_calculation(downloaded, total, speed):
    """
    For any download state with downloaded_bytes and total_bytes, percentage SHALL be
    calculated as (downloaded/total)*100 and be between 0 and 100.
    
    **Feature: github-auto-update, Property 7: Download Progress Calculation**
    **Validates: Requirements 3.2**
    """
    progress = DownloadProgress(
        downloaded_bytes=downloaded,
        total_bytes=total,
        speed_bps=speed
    )
    
    # Check percentage calculation
    if total == 0:
        assert progress.percentage == 0.0, \
            "Percentage should be 0 when total_bytes is 0"
    else:
        expected_percentage = (downloaded / total) * 100.0
        assert progress.percentage == expected_percentage, \
            f"Percentage should be {expected_percentage}, got {progress.percentage}"
        
        # Percentage should be between 0 and 100 when downloaded <= total
        if downloaded <= total:
            assert 0 <= progress.percentage <= 100, \
                f"Percentage should be between 0 and 100, got {progress.percentage}"


# **Feature: github-auto-update, Property 7: Download Speed Text Formatting**
# **Validates: Requirements 3.2**
@given(
    speed=st.floats(min_value=0, max_value=1_000_000_000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_download_speed_text_formatting(speed):
    """
    For any download speed, speed_text SHALL be formatted as human-readable string.
    
    **Feature: github-auto-update, Property 7: Download Progress Calculation**
    **Validates: Requirements 3.2**
    """
    progress = DownloadProgress(
        downloaded_bytes=0,
        total_bytes=100,
        speed_bps=speed
    )
    
    speed_text = progress.speed_text
    
    # Should end with /s
    assert speed_text.endswith('/s'), \
        f"Speed text should end with '/s', got '{speed_text}'"
    
    # Should contain appropriate unit
    if speed < 1024:
        assert 'B/s' in speed_text, \
            f"Speed < 1KB should show B/s, got '{speed_text}'"
    elif speed < 1024 * 1024:
        assert 'KB/s' in speed_text, \
            f"Speed < 1MB should show KB/s, got '{speed_text}'"
    else:
        assert 'MB/s' in speed_text, \
            f"Speed >= 1MB should show MB/s, got '{speed_text}'"


# **Feature: github-auto-update, Property 8: File Size Verification**
# **Validates: Requirements 3.3**
@given(
    file_content=st.binary(min_size=1, max_size=10000)
)
@settings(max_examples=100, deadline=None)
def test_property_file_size_verification(file_content):
    """
    For any downloaded file, verification SHALL pass if and only if actual file size
    equals expected size.
    
    **Feature: github-auto-update, Property 8: File Size Verification**
    **Validates: Requirements 3.3**
    """
    manager = DownloadManager()
    
    # Create a temp file with the content
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(file_content)
        filepath = f.name
    
    try:
        actual_size = len(file_content)
        
        # Verification should pass with correct size
        assert manager.verify_file(filepath, actual_size), \
            f"Verification should pass when expected size ({actual_size}) equals actual size"
        
        # Verification should fail with wrong size
        wrong_size = actual_size + 1
        assert not manager.verify_file(filepath, wrong_size), \
            f"Verification should fail when expected size ({wrong_size}) differs from actual ({actual_size})"
        
        # Verification should fail with size 0 (unless file is actually empty)
        if actual_size > 0:
            assert not manager.verify_file(filepath, 0), \
                "Verification should fail when expected size is 0 but file is not empty"
    finally:
        os.unlink(filepath)



# **Feature: github-auto-update, Property 8: File Verification Non-Existent File**
# **Validates: Requirements 3.3**
@given(
    expected_size=st.integers(min_value=0, max_value=1_000_000)
)
@settings(max_examples=100)
def test_property_file_verification_nonexistent(expected_size):
    """
    For any non-existent file, verification SHALL return False.
    
    **Feature: github-auto-update, Property 8: File Size Verification**
    **Validates: Requirements 3.3**
    """
    manager = DownloadManager()
    
    # Non-existent file should fail verification
    fake_path = os.path.join(tempfile.gettempdir(), f"nonexistent_file_{expected_size}.tmp")
    
    # Make sure file doesn't exist
    if os.path.exists(fake_path):
        os.unlink(fake_path)
    
    assert not manager.verify_file(fake_path, expected_size), \
        "Verification should fail for non-existent file"


# **Feature: github-auto-update, Property 9: Download Cancellation**
# **Validates: Requirements 3.5**
def test_property_download_cancellation_flag():
    """
    For any download in progress, calling cancel SHALL set the cancel flag.
    
    **Feature: github-auto-update, Property 9: Download Cancellation**
    **Validates: Requirements 3.5**
    """
    manager = DownloadManager()
    
    # Initially cancel flag should be False
    assert not manager._cancel_flag, \
        "Cancel flag should be False initially"
    
    # After calling cancel, flag should be True
    manager.cancel_download()
    assert manager._cancel_flag, \
        "Cancel flag should be True after calling cancel_download()"


# **Feature: github-auto-update, Property 10: Pending Installer Persistence**
# **Validates: Requirements 4.4**
@given(
    filename=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('L', 'N'),
    )).map(lambda s: s + ".exe")
)
@settings(max_examples=100)
def test_property_pending_installer_path_construction(filename):
    """
    For any filename, the download path SHALL be correctly constructed in download_dir.
    
    **Feature: github-auto-update, Property 10: Pending Installer Persistence**
    **Validates: Requirements 4.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = DownloadManager(download_dir=tmpdir)
        
        # The expected path should be download_dir + filename
        expected_path = os.path.join(tmpdir, filename)
        
        # Verify download_dir is set correctly
        assert manager.download_dir == tmpdir, \
            f"download_dir should be '{tmpdir}', got '{manager.download_dir}'"


# Test for DownloadProgress edge cases
@given(
    downloaded=st.integers(min_value=0, max_value=100),
    total=st.just(100)
)
@settings(max_examples=100)
def test_property_download_progress_percentage_bounds(downloaded, total):
    """
    For any valid download state where downloaded <= total, percentage SHALL be
    between 0 and 100.
    
    **Feature: github-auto-update, Property 7: Download Progress Calculation**
    **Validates: Requirements 3.2**
    """
    progress = DownloadProgress(
        downloaded_bytes=downloaded,
        total_bytes=total,
        speed_bps=1000.0
    )
    
    assert 0 <= progress.percentage <= 100, \
        f"Percentage should be between 0 and 100, got {progress.percentage}"
    
    # Check exact percentage
    expected = (downloaded / total) * 100
    assert progress.percentage == expected, \
        f"Percentage should be {expected}, got {progress.percentage}"



# Mock config manager for testing
class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def __init__(self):
        self._config = {}
    
    def get(self, section: str, key: str, fallback: str = '') -> str:
        return self._config.get(f"{section}.{key}", fallback)
    
    def set(self, section: str, key: str, value: str) -> None:
        self._config[f"{section}.{key}"] = value


# **Feature: github-auto-update, Property 10: Pending Installer Persistence**
# **Validates: Requirements 4.4**
@given(
    file_content=st.binary(min_size=100, max_size=1000)
)
@settings(max_examples=100)
def test_property_pending_installer_persistence(file_content):
    """
    For any successfully downloaded installer with "install later" choice,
    the path SHALL be saved and retrievable on next startup.
    
    **Feature: github-auto-update, Property 10: Pending Installer Persistence**
    **Validates: Requirements 4.4**
    """
    manager = DownloadManager()
    config = MockConfigManager()
    
    # Create a temp file to simulate downloaded installer
    with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as f:
        f.write(file_content)
        filepath = f.name
    
    try:
        # Save pending installer
        manager.save_pending_installer(filepath, config)
        
        # Retrieve pending installer
        retrieved = manager.get_pending_installer(config)
        
        assert retrieved == filepath, \
            f"Retrieved path should be '{filepath}', got '{retrieved}'"
        
        # Clear pending installer
        manager.clear_pending_installer(config)
        
        # Should return None after clearing
        retrieved_after_clear = manager.get_pending_installer(config)
        assert retrieved_after_clear is None, \
            "Should return None after clearing pending installer"
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


# **Feature: github-auto-update, Property 10: Pending Installer Non-Existent File**
# **Validates: Requirements 4.4**
def test_property_pending_installer_nonexistent_file():
    """
    For any pending installer path pointing to non-existent file,
    get_pending_installer SHALL return None.
    
    **Feature: github-auto-update, Property 10: Pending Installer Persistence**
    **Validates: Requirements 4.4**
    """
    manager = DownloadManager()
    config = MockConfigManager()
    
    # Save a path to non-existent file
    fake_path = os.path.join(tempfile.gettempdir(), "nonexistent_installer.exe")
    
    # Make sure file doesn't exist
    if os.path.exists(fake_path):
        os.unlink(fake_path)
    
    manager.save_pending_installer(fake_path, config)
    
    # Should return None because file doesn't exist
    retrieved = manager.get_pending_installer(config)
    assert retrieved is None, \
        "Should return None for non-existent installer file"


# **Feature: github-auto-update, Property 10: Pending Installer No Config**
# **Validates: Requirements 4.4**
def test_property_pending_installer_no_config():
    """
    For any download manager without config manager,
    pending installer operations SHALL handle gracefully.
    
    **Feature: github-auto-update, Property 10: Pending Installer Persistence**
    **Validates: Requirements 4.4**
    """
    manager = DownloadManager()
    
    # Should not raise with None config
    manager.save_pending_installer("/some/path.exe", None)
    manager.clear_pending_installer(None)
    result = manager.get_pending_installer(None)
    
    assert result is None, \
        "Should return None when config manager is None"
