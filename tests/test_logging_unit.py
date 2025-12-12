"""
Unit tests for Logger

These tests verify specific examples and edge cases for the logging system.
"""

import os
import tempfile
import logging
from pathlib import Path
import pytest

from logging_system.logger import Logger
from models.config_models import LoggingConfig


def test_logger_initialization():
    """Test that logger initializes correctly"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        config = LoggingConfig(
            log_level='INFO',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Verify logger was created
        assert logger is not None
        assert logger.name == "TestLogger"
        
        # Verify log file was created
        assert os.path.exists(log_file_path)
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_log_levels():
    """Test that all log levels work correctly"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        config = LoggingConfig(
            log_level='DEBUG',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Log messages at all levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Read log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify all messages are present
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        assert "Critical message" in log_content
        
        # Verify log levels are present
        assert "DEBUG" in log_content
        assert "INFO" in log_content
        assert "WARNING" in log_content
        assert "ERROR" in log_content
        assert "CRITICAL" in log_content
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_log_directory_creation():
    """Test that log directory is created if it doesn't exist"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a log file path in a subdirectory that doesn't exist
        log_file_path = os.path.join(temp_dir, "subdir", "test.log")
        
        config = LoggingConfig(
            log_level='INFO',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Verify directory was created
        assert os.path.exists(os.path.dirname(log_file_path))
        
        # Verify log file was created
        logger.info("Test message")
        assert os.path.exists(log_file_path)
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_log_formatting():
    """Test that log messages are formatted correctly"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        config = LoggingConfig(
            log_level='INFO',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="CustomsAutomation")
        
        # Log a message
        logger.info("Test message")
        
        # Read log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify format: timestamp - name - level - message
        import re
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - CustomsAutomation - INFO - Test message'
        assert re.search(pattern, log_content), \
            f"Log format should match expected pattern. Got: {log_content}"
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_error_with_exception_info():
    """Test that errors can be logged with exception information"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        config = LoggingConfig(
            log_level='ERROR',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Create and log an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("An error occurred", exc_info=True)
        
        # Read log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify exception information is present
        assert "An error occurred" in log_content
        assert "ValueError" in log_content
        assert "Test exception" in log_content
        assert "Traceback" in log_content
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_log_level_filtering():
    """Test that log level filtering works correctly"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        # Set log level to WARNING
        config = LoggingConfig(
            log_level='WARNING',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Log messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Close handlers before reading to flush
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
        # Read log file
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # Verify only WARNING and above are logged (logger level filters all handlers)
        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_get_logger():
    """Test that get_logger returns the underlying logger"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        log_file_path = f.name
    
    try:
        config = LoggingConfig(
            log_level='INFO',
            log_file=log_file_path,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger = Logger(config, name="TestLogger")
        
        # Get underlying logger
        underlying_logger = logger.get_logger()
        
        # Verify it's a Python logger
        assert isinstance(underlying_logger, logging.Logger)
        assert underlying_logger.name == "TestLogger"
        
        # Close handlers
        for handler in logger.get_logger().handlers[:]:
            handler.close()
            logger.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path):
            os.unlink(log_file_path)


def test_multiple_loggers():
    """Test that multiple loggers can coexist"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f1:
        log_file_path1 = f1.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f2:
        log_file_path2 = f2.name
    
    try:
        config1 = LoggingConfig(
            log_level='INFO',
            log_file=log_file_path1,
            max_log_size=10485760,
            backup_count=5
        )
        
        config2 = LoggingConfig(
            log_level='DEBUG',
            log_file=log_file_path2,
            max_log_size=10485760,
            backup_count=5
        )
        
        logger1 = Logger(config1, name="Logger1")
        logger2 = Logger(config2, name="Logger2")
        
        # Log to both loggers
        logger1.info("Message from logger1")
        logger2.debug("Message from logger2")
        
        # Read log files
        with open(log_file_path1, 'r', encoding='utf-8') as f:
            log_content1 = f.read()
        
        with open(log_file_path2, 'r', encoding='utf-8') as f:
            log_content2 = f.read()
        
        # Verify messages are in correct files
        assert "Message from logger1" in log_content1
        assert "Logger1" in log_content1
        
        assert "Message from logger2" in log_content2
        assert "Logger2" in log_content2
        
        # Verify messages are NOT in wrong files
        assert "Message from logger2" not in log_content1
        assert "Message from logger1" not in log_content2
        
        # Close handlers
        for handler in logger1.get_logger().handlers[:]:
            handler.close()
            logger1.get_logger().removeHandler(handler)
        
        for handler in logger2.get_logger().handlers[:]:
            handler.close()
            logger2.get_logger().removeHandler(handler)
        
    finally:
        if os.path.exists(log_file_path1):
            os.unlink(log_file_path1)
        if os.path.exists(log_file_path2):
            os.unlink(log_file_path2)
