"""
Property-based tests for configuration management

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import os
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

from config.configuration_manager import ConfigurationManager, ConfigurationError


# Feature: customs-barcode-automation, Property 10: Configuration encryption
@given(password=st.text(min_size=8, max_size=100, alphabet=st.characters(min_codepoint=33, max_codepoint=126)))
@settings(max_examples=100, deadline=None)
def test_property_configuration_encryption(password):
    """
    For any password stored in configuration, it should be encrypted when saved to disk.
    
    **Validates: Requirements 6.6**
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write(f"""[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = {password}
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
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Get the database config (this should decrypt the password)
        db_config = config_manager.get_database_config()
        
        # Verify the password is correctly decrypted
        assert db_config.password == password, "Password should be decrypted correctly"
        
        # Save the configuration (this should encrypt the password)
        config_manager.save()
        
        # Read the raw file content
        with open(config_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # The password in the file should be encrypted (not plain text)
        # Fernet encrypted strings start with 'gAAAAA' when base64 encoded
        # Check that the password line contains an encrypted value
        import re
        password_line_match = re.search(r'password\s*=\s*(.+)', file_content)
        assert password_line_match, "Password line should exist in config"
        
        saved_password = password_line_match.group(1).strip()
        
        # The saved password should be encrypted (starts with gAAAAA)
        assert saved_password.startswith('gAAAAA'), \
            f"Saved password should be encrypted (start with 'gAAAAA'), but got: {saved_password[:20]}"
        
        # The saved password should NOT be the plain text password
        assert saved_password != password, \
            "Saved password should not be plain text"
        
        # Load the configuration again to verify round-trip
        config_manager2 = ConfigurationManager(config_path)
        db_config2 = config_manager2.get_database_config()
        
        # The password should still decrypt correctly
        assert db_config2.password == password, \
            "Password should decrypt correctly after save/load cycle"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        # Clean up encryption key file
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# Feature: customs-barcode-automation, Property 11: Configuration validation
@given(
    missing_section=st.sampled_from(['Database', 'BarcodeService', 'Application']),
)
@settings(max_examples=100)
def test_property_configuration_validation(missing_section):
    """
    For any application startup, if required configuration fields are missing or invalid,
    the system should display an error and prevent startup.
    
    **Validates: Requirements 6.7**
    """
    # Create a temporary config file with a missing section
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        config_path = f.name
        
        # Write all sections except the missing one
        sections = {
            'Database': """[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = test123
timeout = 30
""",
            'BarcodeService': """[BarcodeService]
api_url = http://test.com/api
primary_web_url = https://test.com/primary
backup_web_url = https://test.com/backup
timeout = 30
""",
            'Application': """[Application]
output_directory = C:\\Test
polling_interval = 300
max_retries = 3
retry_delay = 5
operation_mode = automatic
""",
            'Logging': """[Logging]
log_level = INFO
log_file = logs/app.log
max_log_size = 10485760
backup_count = 5
"""
        }
        
        # Write all sections except the missing one
        for section_name, section_content in sections.items():
            if section_name != missing_section:
                f.write(section_content + "\n")
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Validation should fail for missing required section
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        # The error message should mention the missing section
        error_message = str(exc_info.value)
        assert missing_section in error_message or missing_section.lower() in error_message.lower(), \
            f"Error message should mention the missing section: {missing_section}"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        # Clean up encryption key file
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


@given(
    missing_field=st.sampled_from([
        ('Database', 'server'),
        ('Database', 'database'),
        ('Database', 'username'),
        ('Database', 'password'),
        ('BarcodeService', 'api_url'),
        ('BarcodeService', 'primary_web_url'),
        ('BarcodeService', 'backup_web_url'),
        ('Application', 'output_directory'),
    ])
)
@settings(max_examples=100)
def test_property_configuration_validation_missing_fields(missing_field):
    """
    For any application startup, if required configuration fields are missing,
    the system should display an error and prevent startup.
    
    **Validates: Requirements 6.7**
    """
    section, field = missing_field
    
    # Create a complete config
    config_content = """[Database]
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
"""
    
    # Remove the specific field
    lines = config_content.split('\n')
    filtered_lines = [line for line in lines if not line.startswith(f'{field} =')]
    modified_content = '\n'.join(filtered_lines)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        config_path = f.name
        f.write(modified_content)
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Validation should fail for missing required field
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        # The error message should mention the missing field
        error_message = str(exc_info.value)
        assert field in error_message or field.lower() in error_message.lower(), \
            f"Error message should mention the missing field: {field}"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        # Clean up encryption key file
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.1-ui-enhancements, Property 1: Config Persistence Round-Trip (Retrieval Method)**
# **Validates: Requirements 1.2**
@given(retrieval_method=st.sampled_from(['auto', 'api', 'web']))
@settings(max_examples=100)
def test_property_retrieval_method_round_trip(retrieval_method):
    """
    For any valid retrieval method value ("auto", "api", "web"), saving to config.ini
    and reloading should return the same value.
    
    **Feature: v1.1-ui-enhancements, Property 1: Config Persistence Round-Trip (Retrieval Method)**
    **Validates: Requirements 1.2**
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write(f"""[Database]
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
retrieval_method = auto

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
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Set the retrieval method
        config_manager.set_retrieval_method(retrieval_method)
        
        # Save the configuration
        config_manager.save()
        
        # Load the configuration again
        config_manager2 = ConfigurationManager(config_path)
        
        # Verify the retrieval method is correctly persisted
        loaded_method = config_manager2.get_retrieval_method()
        assert loaded_method == retrieval_method, \
            f"Retrieval method should be '{retrieval_method}' after save/load, but got '{loaded_method}'"
        
        # Also verify via BarcodeServiceConfig
        barcode_config = config_manager2.get_barcode_service_config()
        assert barcode_config.retrieval_method == retrieval_method, \
            f"BarcodeServiceConfig.retrieval_method should be '{retrieval_method}', but got '{barcode_config.retrieval_method}'"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.1-ui-enhancements, Property 2: Config Persistence Round-Trip (PDF Naming)**
# **Validates: Requirements 5.2**
@given(pdf_naming_format=st.sampled_from(['tax_code', 'invoice', 'bill_of_lading']))
@settings(max_examples=100)
def test_property_pdf_naming_format_round_trip(pdf_naming_format):
    """
    For any valid PDF naming format ("tax_code", "invoice", "bill_of_lading"), saving to config.ini
    and reloading should return the same value.
    
    **Feature: v1.1-ui-enhancements, Property 2: Config Persistence Round-Trip (PDF Naming)**
    **Validates: Requirements 5.2**
    """
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
        config_path = f.name
        f.write(f"""[Database]
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
retrieval_method = auto
pdf_naming_format = tax_code

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
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Set the PDF naming format
        config_manager.set_pdf_naming_format(pdf_naming_format)
        
        # Save the configuration
        config_manager.save()
        
        # Load the configuration again
        config_manager2 = ConfigurationManager(config_path)
        
        # Verify the PDF naming format is correctly persisted
        loaded_format = config_manager2.get_pdf_naming_format()
        assert loaded_format == pdf_naming_format, \
            f"PDF naming format should be '{pdf_naming_format}' after save/load, but got '{loaded_format}'"
        
        # Also verify via BarcodeServiceConfig
        barcode_config = config_manager2.get_barcode_service_config()
        assert barcode_config.pdf_naming_format == pdf_naming_format, \
            f"BarcodeServiceConfig.pdf_naming_format should be '{pdf_naming_format}', but got '{barcode_config.pdf_naming_format}'"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 2: Settings Persistence Round-Trip**
# **Validates: Requirements 2.3, 2.6, 7.5, 10.5**
@given(
    theme=st.sampled_from(['light', 'dark']),
    notifications_enabled=st.booleans(),
    sound_enabled=st.booleans(),
    batch_limit=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100)
def test_property_ui_settings_round_trip(theme, notifications_enabled, sound_enabled, batch_limit):
    """
    For any valid settings value (notifications_enabled, sound_enabled, theme, batch_limit),
    saving to config and loading back should return the same value.
    
    **Feature: v1.3-enhancements, Property 2: Settings Persistence Round-Trip**
    **Validates: Requirements 2.3, 2.6, 7.5, 10.5**
    """
    # Create a temporary config file
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
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Set all UI settings
        config_manager.set_theme(theme)
        config_manager.set_notifications_enabled(notifications_enabled)
        config_manager.set_sound_enabled(sound_enabled)
        config_manager.set_batch_limit(batch_limit)
        
        # Save the configuration
        config_manager.save()
        
        # Load the configuration again
        config_manager2 = ConfigurationManager(config_path)
        
        # Verify theme is correctly persisted
        loaded_theme = config_manager2.get_theme()
        assert loaded_theme == theme, \
            f"Theme should be '{theme}' after save/load, but got '{loaded_theme}'"
        
        # Verify notifications_enabled is correctly persisted
        loaded_notifications = config_manager2.get_notifications_enabled()
        assert loaded_notifications == notifications_enabled, \
            f"notifications_enabled should be {notifications_enabled} after save/load, but got {loaded_notifications}"
        
        # Verify sound_enabled is correctly persisted
        loaded_sound = config_manager2.get_sound_enabled()
        assert loaded_sound == sound_enabled, \
            f"sound_enabled should be {sound_enabled} after save/load, but got {loaded_sound}"
        
        # Verify batch_limit is correctly persisted
        loaded_batch_limit = config_manager2.get_batch_limit()
        assert loaded_batch_limit == batch_limit, \
            f"batch_limit should be {batch_limit} after save/load, but got {loaded_batch_limit}"
        
        # Also verify via UIConfig
        ui_config = config_manager2.get_ui_config()
        assert ui_config.theme == theme, \
            f"UIConfig.theme should be '{theme}', but got '{ui_config.theme}'"
        assert ui_config.notifications_enabled == notifications_enabled, \
            f"UIConfig.notifications_enabled should be {notifications_enabled}, but got {ui_config.notifications_enabled}"
        assert ui_config.sound_enabled == sound_enabled, \
            f"UIConfig.sound_enabled should be {sound_enabled}, but got {ui_config.sound_enabled}"
        assert ui_config.batch_limit == batch_limit, \
            f"UIConfig.batch_limit should be {batch_limit}, but got {ui_config.batch_limit}"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)


# **Feature: v1.3-enhancements, Property 2: Settings Persistence Round-Trip (Window State)**
# **Validates: Requirements 6.1, 6.2**
@given(
    window_x=st.integers(min_value=-1, max_value=3000),
    window_y=st.integers(min_value=-1, max_value=2000),
    window_width=st.integers(min_value=800, max_value=3840),
    window_height=st.integers(min_value=600, max_value=2160)
)
@settings(max_examples=100)
def test_property_window_state_round_trip(window_x, window_y, window_width, window_height):
    """
    For any valid window position and size, saving state and restoring should result
    in the same position and size.
    
    **Feature: v1.3-enhancements, Property 2: Settings Persistence Round-Trip (Window State)**
    **Validates: Requirements 6.1, 6.2**
    """
    # Create a temporary config file
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
    
    try:
        # Load configuration
        config_manager = ConfigurationManager(config_path)
        
        # Set window state
        config_manager.set_window_state(window_x, window_y, window_width, window_height)
        
        # Save the configuration
        config_manager.save()
        
        # Load the configuration again
        config_manager2 = ConfigurationManager(config_path)
        
        # Get window state
        loaded_state = config_manager2.get_window_state()
        
        # Verify window state is correctly persisted
        assert loaded_state[0] == window_x, \
            f"window_x should be {window_x} after save/load, but got {loaded_state[0]}"
        assert loaded_state[1] == window_y, \
            f"window_y should be {window_y} after save/load, but got {loaded_state[1]}"
        assert loaded_state[2] == window_width, \
            f"window_width should be {window_width} after save/load, but got {loaded_state[2]}"
        assert loaded_state[3] == window_height, \
            f"window_height should be {window_height} after save/load, but got {loaded_state[3]}"
        
        # Also verify via UIConfig
        ui_config = config_manager2.get_ui_config()
        assert ui_config.window_x == window_x, \
            f"UIConfig.window_x should be {window_x}, but got {ui_config.window_x}"
        assert ui_config.window_y == window_y, \
            f"UIConfig.window_y should be {window_y}, but got {ui_config.window_y}"
        assert ui_config.window_width == window_width, \
            f"UIConfig.window_width should be {window_width}, but got {ui_config.window_width}"
        assert ui_config.window_height == window_height, \
            f"UIConfig.window_height should be {window_height}, but got {ui_config.window_height}"
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)
        if os.path.exists(ConfigurationManager.KEY_FILE):
            os.unlink(ConfigurationManager.KEY_FILE)
