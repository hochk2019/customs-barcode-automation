"""
Unit tests for ConfigurationManager

These tests verify specific examples and edge cases for configuration management.
"""

import os
import tempfile
import pytest

from config.configuration_manager import ConfigurationManager, ConfigurationError
from models.config_models import DatabaseConfig, BarcodeServiceConfig


def create_valid_config_file():
    """Helper function to create a valid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write("""[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = test_password_123
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


def test_loading_valid_configuration():
    """Test loading a valid configuration file"""
    config_path = create_valid_config_file()
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        # Verify database config
        db_config = config_manager.get_database_config()
        assert db_config.server == "localhost"
        assert db_config.database == "ECUS5VNACCS"
        assert db_config.username == "sa"
        assert db_config.password == "test_password_123"
        assert db_config.timeout == 30
        
        # Verify barcode service config
        barcode_config = config_manager.get_barcode_service_config()
        assert barcode_config.api_url == "http://test.com/api"
        assert barcode_config.primary_web_url == "https://test.com/primary"
        assert barcode_config.backup_web_url == "https://test.com/backup"
        assert barcode_config.timeout == 30
        
        # Verify application settings
        assert config_manager.get_output_path() == "C:\\Test"
        assert config_manager.get_polling_interval() == 300
        assert config_manager.get_operation_mode() == "automatic"
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_handling_missing_configuration():
    """Test handling of missing configuration file"""
    non_existent_path = "non_existent_config.ini"
    
    with pytest.raises(ConfigurationError) as exc_info:
        ConfigurationManager(non_existent_path)
    
    assert "not found" in str(exc_info.value).lower()


def test_password_encryption_decryption():
    """Test password encryption and decryption"""
    config_path = create_valid_config_file()
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Get original password
        db_config = config_manager.get_database_config()
        original_password = db_config.password
        assert original_password == "test_password_123"
        
        # Save configuration (should encrypt password)
        config_manager.save()
        
        # Read raw file to verify encryption
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Password should be encrypted in file
        assert "gAAAAA" in content
        assert "test_password_123" not in content
        
        # Load again and verify decryption
        config_manager2 = ConfigurationManager(config_path)
        db_config2 = config_manager2.get_database_config()
        assert db_config2.password == original_password
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_configuration_validation():
    """Test configuration validation"""
    # Test missing Database section
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write("""[BarcodeService]
api_url = http://test.com/api
primary_web_url = https://test.com/primary
backup_web_url = https://test.com/backup

[Application]
output_directory = C:\\Test
""")
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        assert "Database" in str(exc_info.value)
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_set_output_path():
    """Test setting output path"""
    config_path = create_valid_config_file()
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        # Set new output path
        new_path = "D:\\NewPath"
        config_manager.set_output_path(new_path)
        
        # Verify it was set
        assert config_manager.get_output_path() == new_path
        
        # Save and reload to verify persistence
        config_manager.save()
        config_manager2 = ConfigurationManager(config_path)
        assert config_manager2.get_output_path() == new_path
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_set_operation_mode():
    """Test setting operation mode"""
    config_path = create_valid_config_file()
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        # Set to manual mode
        config_manager.set_operation_mode('manual')
        assert config_manager.get_operation_mode() == 'manual'
        
        # Save and reload
        config_manager.save()
        config_manager2 = ConfigurationManager(config_path)
        assert config_manager2.get_operation_mode() == 'manual'
        
        # Test invalid mode
        with pytest.raises(ValueError):
            config_manager.set_operation_mode('invalid_mode')
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_missing_database_fields():
    """Test validation with missing database fields"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write("""[Database]
server = localhost
database = ECUS5VNACCS
# Missing username and password

[BarcodeService]
api_url = http://test.com/api
primary_web_url = https://test.com/primary
backup_web_url = https://test.com/backup

[Application]
output_directory = C:\\Test
""")
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        error_msg = str(exc_info.value)
        assert "username" in error_msg or "password" in error_msg
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_connection_string_generation():
    """Test database connection string generation"""
    config_path = create_valid_config_file()
    
    try:
        config_manager = ConfigurationManager(config_path)
        db_config = config_manager.get_database_config()
        
        conn_str = db_config.connection_string
        
        # Verify connection string contains required components
        assert "DRIVER={SQL Server}" in conn_str
        assert "SERVER=localhost" in conn_str
        assert "DATABASE=ECUS5VNACCS" in conn_str
        assert "UID=sa" in conn_str
        assert "PWD=test_password_123" in conn_str
        assert "Connection Timeout=30" in conn_str
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


def test_default_values():
    """Test that default values are used when optional fields are missing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write("""[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = test123
# timeout not specified

[BarcodeService]
api_url = http://test.com/api
primary_web_url = https://test.com/primary
backup_web_url = https://test.com/backup
# timeout not specified

[Application]
output_directory = C:\\Test
# polling_interval not specified
""")
    
    try:
        config_manager = ConfigurationManager(config_path)
        
        # Verify defaults are used
        db_config = config_manager.get_database_config()
        assert db_config.timeout == 30  # Default value
        
        barcode_config = config_manager.get_barcode_service_config()
        assert barcode_config.timeout == 30  # Default value
        
        assert config_manager.get_polling_interval() == 300  # Default value
        
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)
