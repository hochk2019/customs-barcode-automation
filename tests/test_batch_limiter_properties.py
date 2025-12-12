"""
Property-based tests for Batch Limiter

**Feature: v1.3-enhancements**
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings
import pytest

from processors.batch_limiter import BatchLimiter
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
batch_limit = 20
""")
    return config_path


# **Feature: v1.3-enhancements, Property 12: Batch Limit Validation**
# **Validates: Requirements 10.3, 10.4**
@given(limit=st.integers(min_value=-100, max_value=200))
@settings(max_examples=100)
def test_property_batch_limit_validation(limit):
    """
    Batch limit should be clamped between MIN_LIMIT (1) and MAX_LIMIT (50),
    with DEFAULT_LIMIT (20) for invalid values.
    
    **Feature: v1.3-enhancements, Property 12: Batch Limit Validation**
    **Validates: Requirements 10.3, 10.4**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        limiter = BatchLimiter(config_manager)
        
        # Try to set the limit
        result = limiter.set_limit(limit)
        
        if BatchLimiter.MIN_LIMIT <= limit <= BatchLimiter.MAX_LIMIT:
            assert result == True, f"Valid limit {limit} should be accepted"
            assert limiter.get_limit() == limit
        else:
            assert result == False, f"Invalid limit {limit} should be rejected"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 13: Batch Selection Validation**
# **Validates: Requirements 10.1, 10.2**
@given(
    count=st.integers(min_value=0, max_value=100),
    limit=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100)
def test_property_batch_selection_validation(count, limit):
    """
    Selection validation should correctly identify when count exceeds limit.
    
    **Feature: v1.3-enhancements, Property 13: Batch Selection Validation**
    **Validates: Requirements 10.1, 10.2**
    """
    config_path = create_test_config()
    
    try:
        config_manager = ConfigurationManager(config_path)
        limiter = BatchLimiter(config_manager)
        limiter.set_limit(limit)
        
        is_valid, message = limiter.validate_selection(count)
        
        if count <= 0:
            assert is_valid == False, "Zero or negative count should be invalid"
        elif count > limit:
            assert is_valid == False, f"Count {count} exceeding limit {limit} should be invalid"
            assert str(count) in message, "Message should contain count"
            assert str(limit) in message, "Message should contain limit"
        else:
            assert is_valid == True, f"Count {count} within limit {limit} should be valid"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_property_default_limit():
    """
    Default limit should be 20.
    
    **Feature: v1.3-enhancements, Property 12: Batch Limit Validation**
    **Validates: Requirements 10.4**
    """
    assert BatchLimiter.DEFAULT_LIMIT == 20
    assert BatchLimiter.MIN_LIMIT == 1
    assert BatchLimiter.MAX_LIMIT == 50
