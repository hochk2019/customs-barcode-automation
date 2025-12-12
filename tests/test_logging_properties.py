"""
Property-based tests for logging system

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import os
import tempfile
import re
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

from logging_system.logger import Logger
from models.config_models import LoggingConfig


# Feature: customs-barcode-automation, Property 12: Log entry completeness
@given(
    message=st.text(min_size=1, max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
    log_level=st.sampled_from(['debug', 'info', 'warning', 'error', 'critical'])
)
@settings(max_examples=100)
def test_property_log_entry_completeness(message, log_level):
    """
    For any logged operation, the log entry should include a timestamp and module name.
    
    **Validates: Requirements 7.1**
    """
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        # Create logging configuration
        config = LoggingConfig(
            log_level='DEBUG',  # Capture all levels
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        # Create logger
        logger = Logger(config, name="TestLogger")
        
        # Log the message at the specified level
        log_method = getattr(logger, log_level)
        log_method(message)
        
        # Read the log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify log entry contains timestamp
        # Format: YYYY-MM-DD HH:MM:SS
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, log_content), \
            f"Log entry should contain timestamp in format YYYY-MM-DD HH:MM:SS"
        
        # Verify log entry contains module name
        assert "TestLogger" in log_content, \
            f"Log entry should contain module name 'TestLogger'"
        
        # Verify log entry contains the log level
        assert log_level.upper() in log_content, \
            f"Log entry should contain log level '{log_level.upper()}'"
        
        # Verify log entry contains the message (if it's not empty or whitespace)
        if message.strip():
            assert message in log_content, \
                f"Log entry should contain the logged message"
        
    finally:
        # Close all handlers to release file locks
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
        # Cleanup
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


# Feature: customs-barcode-automation, Property 13: Error log detail
@given(
    error_message=st.text(min_size=1, max_size=200, alphabet=st.characters(min_codepoint=32, max_codepoint=126))
)
@settings(max_examples=100)
def test_property_error_log_detail(error_message):
    """
    For any logged error, the log entry should include the full stack trace.
    
    **Validates: Requirements 7.2**
    """
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        # Create logging configuration
        config = LoggingConfig(
            log_level='DEBUG',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        # Create logger
        logger = Logger(config, name="TestLogger")
        
        # Create an exception and log it
        try:
            # Generate a traceable exception
            raise ValueError(error_message)
        except ValueError:
            # Log the error with exception info
            logger.error("An error occurred", exc_info=True)
        
        # Read the log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify log entry contains the error message
        assert "An error occurred" in log_content, \
            "Log entry should contain the error message"
        
        # Verify log entry contains stack trace indicators
        assert "Traceback" in log_content, \
            "Log entry should contain 'Traceback' from stack trace"
        
        # Verify log entry contains the exception type
        assert "ValueError" in log_content, \
            "Log entry should contain the exception type 'ValueError'"
        
        # Verify log entry contains the exception message
        if error_message.strip():
            assert error_message in log_content, \
                "Log entry should contain the exception message"
        
        # Verify log entry contains file information (line numbers, etc.)
        # Stack traces typically contain "File" and "line"
        assert "File" in log_content, \
            "Log entry should contain file information from stack trace"
        
    finally:
        # Close all handlers to release file locks
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
        # Cleanup
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


# Feature: customs-barcode-automation, Property 14: Log rotation trigger
@given(
    num_messages=st.integers(min_value=10, max_value=50)
)
@settings(max_examples=100)
def test_property_log_rotation(num_messages):
    """
    For any log file that exceeds the configured size limit,
    the system should rotate to a new log file.
    
    **Validates: Requirements 7.6**
    """
    # Create a temporary log file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        # Create logging configuration with very small max size to trigger rotation
        # Set to 1KB to ensure rotation happens
        config = LoggingConfig(
            log_level='DEBUG',
            log_file=log_file_path,
            max_log_size=1024,  # 1KB
            backup_count=5
        )
        
        # Create logger
        logger = Logger(config, name="TestLogger")
        
        # Generate enough log messages to exceed the size limit
        # Each message is about 100 bytes, so we need at least 11 messages to exceed 1KB
        large_message = "X" * 100  # 100 character message
        
        for i in range(num_messages):
            logger.info(f"Message {i}: {large_message}")
        
        # Check if rotation occurred
        # When rotation happens, backup files are created with .1, .2, etc. suffixes
        log_dir = Path(log_file_path).parent
        log_name = Path(log_file_path).name
        
        # Look for rotated log files
        rotated_files = list(log_dir.glob(f"{log_name}.*"))
        
        # Calculate total size of all messages
        total_size = num_messages * (len(large_message) + 50)  # Approximate size with overhead
        
        # If total size exceeds max_log_size, rotation should have occurred
        if total_size > config.max_log_size:
            assert len(rotated_files) > 0 or os.path.getsize(log_file_path) <= config.max_log_size * 1.1, \
                f"Log rotation should occur when size exceeds {config.max_log_size} bytes. " \
                f"Total size: {total_size}, Rotated files: {len(rotated_files)}"
        
        # Verify the main log file exists
        assert os.path.exists(log_file_path), \
            "Main log file should still exist after rotation"
        
        # Verify backup count is respected
        assert len(rotated_files) <= config.backup_count, \
            f"Number of backup files ({len(rotated_files)}) should not exceed backup_count ({config.backup_count})"
        
    finally:
        # Close all handlers to release file locks
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
        # Cleanup
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)
        
        # Clean up rotated files
        log_dir = Path(log_file_path).parent
        log_name = Path(log_file_path).name
        for rotated_file in log_dir.glob(f"{log_name}.*"):
            try:
                rotated_file.unlink()
            except:
                pass
