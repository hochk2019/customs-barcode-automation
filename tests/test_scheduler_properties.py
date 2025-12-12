"""
Property-based tests for Scheduler

These tests verify correctness properties of the workflow scheduler
using property-based testing with Hypothesis.
"""

import pytest
import tempfile
import os
import configparser
from datetime import datetime
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock

from scheduler.scheduler import Scheduler
from models.declaration_models import Declaration, OperationMode
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from logging_system.logger import Logger
from models.config_models import LoggingConfig


def create_test_config_file(temp_dir: str, operation_mode: str = "automatic") -> str:
    """Create a test configuration file"""
    config_path = os.path.join(temp_dir, "test_config.ini")
    
    config = configparser.ConfigParser(interpolation=None)
    config['Database'] = {
        'server': 'test_server',
        'database': 'test_db',
        'username': 'test_user',
        'password': 'test_pass',
        'timeout': '30'
    }
    config['BarcodeService'] = {
        'api_url': 'http://test.api',
        'primary_web_url': 'http://test.web',
        'backup_web_url': 'http://test.backup',
        'timeout': '30'
    }
    config['Application'] = {
        'output_directory': temp_dir,
        'polling_interval': '300',
        'max_retries': '3',
        'retry_delay': '5',
        'operation_mode': operation_mode
    }
    config['Logging'] = {
        'log_level': 'INFO',
        'log_file': os.path.join(temp_dir, 'test.log'),
        'max_log_size': '10485760',
        'backup_count': '5'
    }
    
    with open(config_path, 'w') as f:
        config.write(f)
    
    return config_path


def create_mock_scheduler_components(config_manager):
    """Create mock components for scheduler"""
    ecus_connector = Mock(spec=EcusDataConnector)
    tracking_db = Mock(spec=TrackingDatabase)
    processor = Mock(spec=DeclarationProcessor)
    barcode_retriever = Mock(spec=BarcodeRetriever)
    file_manager = Mock(spec=FileManager)
    
    # Create mock logger to avoid file locking issues
    logger = Mock(spec=Logger)
    
    return ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger


# Feature: customs-barcode-automation, Property 21: Operation mode persistence
@given(
    initial_mode=st.sampled_from(['automatic', 'manual']),
    new_mode=st.sampled_from(['automatic', 'manual'])
)
@settings(max_examples=100, deadline=None)
def test_property_operation_mode_persistence(initial_mode, new_mode):
    """
    For any operation mode change, the new mode should be saved to configuration
    and loaded on the next application start.
    
    **Validates: Requirements 11.1, 11.6**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create initial configuration with initial_mode
        config_path = create_test_config_file(temp_dir, initial_mode)
        
        # Create first scheduler instance
        config_manager1 = ConfigurationManager(config_path)
        components = create_mock_scheduler_components(config_manager1)
        scheduler1 = Scheduler(config_manager1, *components)
        
        # Verify initial mode is loaded correctly
        assert scheduler1.get_operation_mode() == OperationMode(initial_mode)
        
        # Change operation mode
        scheduler1.set_operation_mode(OperationMode(new_mode))
        
        # Verify mode changed in current instance
        assert scheduler1.get_operation_mode() == OperationMode(new_mode)
        
        # Create second scheduler instance (simulating application restart)
        config_manager2 = ConfigurationManager(config_path)
        components2 = create_mock_scheduler_components(config_manager2)
        scheduler2 = Scheduler(config_manager2, *components2)
        
        # Verify new mode persisted and loaded correctly
        assert scheduler2.get_operation_mode() == OperationMode(new_mode)
        
        # Verify configuration file contains the new mode
        loaded_mode = config_manager2.get_operation_mode()
        assert loaded_mode == new_mode


# Feature: customs-barcode-automation, Property 22: Automatic mode scheduling
@given(
    polling_interval=st.integers(min_value=1, max_value=10)  # Short intervals for testing
)
@settings(max_examples=100, deadline=None)
def test_property_automatic_mode_scheduling(polling_interval):
    """
    For any time period when automatic mode is enabled, the system should execute
    polling cycles at the configured interval.
    
    **Validates: Requirements 11.3**
    """
    import time
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration with automatic mode
        config_path = create_test_config_file(temp_dir, "automatic")
        
        # Update polling interval in config
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path)
        config['Application']['polling_interval'] = str(polling_interval)
        with open(config_path, 'w') as f:
            config.write(f)
        
        # Create scheduler
        config_manager = ConfigurationManager(config_path)
        components = create_mock_scheduler_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Set up mocks to track workflow execution
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = []
        processor.filter_declarations.return_value = []
        
        scheduler = Scheduler(config_manager, *components)
        
        # Verify mode is automatic
        assert scheduler.get_operation_mode() == OperationMode.AUTOMATIC
        
        # Start scheduler
        scheduler.start()
        assert scheduler.is_running()
        
        # Wait for at least 2 polling intervals plus some buffer
        wait_time = (polling_interval * 2) + 1
        time.sleep(wait_time)
        
        # Stop scheduler
        scheduler.stop()
        assert not scheduler.is_running()
        
        # Verify workflow was executed at least once (automatic scheduling)
        # In automatic mode, the workflow should be called periodically
        assert ecus_connector.get_new_declarations.call_count >= 1


# Feature: customs-barcode-automation, Property 23: Manual mode execution control
@given(
    wait_time=st.integers(min_value=1, max_value=3)  # Short wait times for testing
)
@settings(max_examples=100, deadline=None)
def test_property_manual_mode_execution_control(wait_time):
    """
    For any time period when manual mode is enabled, the system should only execute
    workflow when manually triggered by the user.
    
    **Validates: Requirements 11.4**
    """
    import time
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration with manual mode
        config_path = create_test_config_file(temp_dir, "manual")
        
        # Create scheduler
        config_manager = ConfigurationManager(config_path)
        components = create_mock_scheduler_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Set up mocks to track workflow execution
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = []
        processor.filter_declarations.return_value = []
        
        scheduler = Scheduler(config_manager, *components)
        
        # Verify mode is manual
        assert scheduler.get_operation_mode() == OperationMode.MANUAL
        
        # Start scheduler in manual mode
        scheduler.start()
        assert scheduler.is_running()
        
        # Wait for some time
        time.sleep(wait_time)
        
        # In manual mode, workflow should NOT be executed automatically
        # So get_new_declarations should not have been called
        assert ecus_connector.get_new_declarations.call_count == 0
        
        # Now manually trigger workflow
        scheduler.run_once()
        
        # After manual trigger, workflow should have been executed
        assert ecus_connector.get_new_declarations.call_count == 1
        
        # Wait again
        time.sleep(wait_time)
        
        # Should still be only 1 call (no automatic execution)
        assert ecus_connector.get_new_declarations.call_count == 1
        
        # Stop scheduler
        scheduler.stop()
        assert not scheduler.is_running()


# Feature: customs-barcode-automation, Property 24: Re-download overwrite behavior
@given(
    tax_code=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))),
    declaration_number=st.text(min_size=12, max_size=12, alphabet=st.characters(whitelist_categories=('Nd',)))
)
@settings(max_examples=100, deadline=None)
def test_property_redownload_overwrite_behavior(tax_code, declaration_number):
    """
    For any re-download operation on a processed declaration, the system should
    overwrite the existing PDF file and update the processed timestamp.
    
    **Validates: Requirements 12.4, 12.5**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration
        config_path = create_test_config_file(temp_dir, "manual")
        
        # Create scheduler
        config_manager = ConfigurationManager(config_path)
        components = create_mock_scheduler_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        scheduler = Scheduler(config_manager, *components)
        
        # Create a test declaration
        declaration = Declaration(
            declaration_number=declaration_number,
            tax_code=tax_code,
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description=None
        )
        
        # Set up mocks
        pdf_content = b"PDF content"
        barcode_retriever.retrieve_barcode.return_value = pdf_content
        file_manager.save_barcode.return_value = f"/path/to/{tax_code}_{declaration_number}.pdf"
        tracking_db.is_processed.return_value = True  # Declaration is already processed
        
        # Call redownload_declarations
        result = scheduler.redownload_declarations([declaration])
        
        # Verify barcode was retrieved
        assert barcode_retriever.retrieve_barcode.call_count == 1
        barcode_retriever.retrieve_barcode.assert_called_with(declaration)
        
        # Verify file was saved with overwrite=True
        assert file_manager.save_barcode.call_count == 1
        call_args = file_manager.save_barcode.call_args
        assert call_args[0][0] == declaration  # First positional arg
        assert call_args[0][1] == pdf_content  # Second positional arg
        assert call_args[1]['overwrite'] == True  # Keyword arg
        
        # Verify timestamp was updated
        assert tracking_db.update_processed_timestamp.call_count == 1
        tracking_db.update_processed_timestamp.assert_called_with(declaration)
        
        # Verify result statistics
        assert result.success_count == 1
        assert result.error_count == 0
        assert result.total_fetched == 1
        assert result.total_eligible == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
