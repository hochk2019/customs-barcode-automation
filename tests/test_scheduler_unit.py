"""
Unit tests for Scheduler

These tests verify specific functionality of the workflow scheduler.
"""

import pytest
import tempfile
import os
import configparser
import time
from datetime import datetime
from unittest.mock import Mock, MagicMock, call

from scheduler.scheduler import Scheduler
from models.declaration_models import Declaration, OperationMode, WorkflowResult
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from logging_system.logger import Logger


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
        'polling_interval': '2',  # Short interval for testing
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


def create_mock_components(config_manager):
    """Create mock components for scheduler"""
    ecus_connector = Mock(spec=EcusDataConnector)
    tracking_db = Mock(spec=TrackingDatabase)
    processor = Mock(spec=DeclarationProcessor)
    barcode_retriever = Mock(spec=BarcodeRetriever)
    file_manager = Mock(spec=FileManager)
    logger = Mock(spec=Logger)
    
    return ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger


def test_scheduler_initialization():
    """Test that scheduler initializes correctly"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "automatic")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        
        scheduler = Scheduler(config_manager, *components)
        
        assert scheduler.get_operation_mode() == OperationMode.AUTOMATIC
        assert not scheduler.is_running()


def test_scheduler_start_stop_automatic_mode():
    """Test starting and stopping scheduler in automatic mode"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "automatic")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        
        scheduler = Scheduler(config_manager, *components)
        
        # Start scheduler
        scheduler.start()
        assert scheduler.is_running()
        
        # Stop scheduler
        scheduler.stop()
        assert not scheduler.is_running()


def test_scheduler_start_stop_manual_mode():
    """Test starting and stopping scheduler in manual mode"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "manual")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        
        scheduler = Scheduler(config_manager, *components)
        
        # Start scheduler
        scheduler.start()
        assert scheduler.is_running()
        
        # Stop scheduler
        scheduler.stop()
        assert not scheduler.is_running()


def test_mode_switching():
    """Test switching between automatic and manual modes"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "automatic")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        
        scheduler = Scheduler(config_manager, *components)
        
        # Initial mode
        assert scheduler.get_operation_mode() == OperationMode.AUTOMATIC
        
        # Switch to manual
        scheduler.set_operation_mode(OperationMode.MANUAL)
        assert scheduler.get_operation_mode() == OperationMode.MANUAL
        
        # Verify persistence
        config_manager2 = ConfigurationManager(config_path)
        assert config_manager2.get_operation_mode() == "manual"


def test_workflow_execution():
    """Test workflow execution with mock components"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "manual")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Create test declarations
        declaration1 = Declaration(
            declaration_number="123456789012",
            tax_code="1234567890",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description=None
        )
        
        declaration2 = Declaration(
            declaration_number="987654321098",
            tax_code="0987654321",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="18A3",
            transport_method="1",
            channel="Vang",
            status="T",
            goods_description=None
        )
        
        # Set up mocks
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = [declaration1, declaration2]
        processor.filter_declarations.return_value = [declaration1, declaration2]
        barcode_retriever.retrieve_barcode.return_value = b"PDF content"
        file_manager.save_barcode.return_value = "/path/to/file.pdf"
        
        scheduler = Scheduler(config_manager, *components)
        
        # Execute workflow
        result = scheduler.run_once()
        
        # Verify workflow execution
        assert result.total_fetched == 2
        assert result.total_eligible == 2
        assert result.success_count == 2
        assert result.error_count == 0
        
        # Verify component calls
        tracking_db.get_all_processed.assert_called_once()
        ecus_connector.get_new_declarations.assert_called_once()
        processor.filter_declarations.assert_called_once()
        assert barcode_retriever.retrieve_barcode.call_count == 2
        assert file_manager.save_barcode.call_count == 2
        assert tracking_db.add_processed.call_count == 2


def test_workflow_execution_with_errors():
    """Test workflow execution handles errors gracefully"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "manual")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Create test declaration
        declaration = Declaration(
            declaration_number="123456789012",
            tax_code="1234567890",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description=None
        )
        
        # Set up mocks - barcode retrieval fails
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = [declaration]
        processor.filter_declarations.return_value = [declaration]
        barcode_retriever.retrieve_barcode.return_value = None  # Failure
        
        scheduler = Scheduler(config_manager, *components)
        
        # Execute workflow
        result = scheduler.run_once()
        
        # Verify error handling
        assert result.total_fetched == 1
        assert result.total_eligible == 1
        assert result.success_count == 0
        assert result.error_count == 1
        
        # File should not be saved
        file_manager.save_barcode.assert_not_called()
        tracking_db.add_processed.assert_not_called()


def test_redownload_logic():
    """Test re-download functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "manual")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Create test declaration
        declaration = Declaration(
            declaration_number="123456789012",
            tax_code="1234567890",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="18A3",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description=None
        )
        
        # Set up mocks
        barcode_retriever.retrieve_barcode.return_value = b"PDF content"
        file_manager.save_barcode.return_value = "/path/to/file.pdf"
        
        scheduler = Scheduler(config_manager, *components)
        
        # Re-download declarations
        result = scheduler.redownload_declarations([declaration])
        
        # Verify re-download
        assert result.success_count == 1
        assert result.error_count == 0
        
        # Verify overwrite flag was set
        call_args = file_manager.save_barcode.call_args
        assert call_args[1]['overwrite'] == True
        
        # Verify timestamp was updated
        tracking_db.update_processed_timestamp.assert_called_once_with(declaration)


def test_automatic_mode_executes_periodically():
    """Test that automatic mode executes workflow periodically"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "automatic")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Set up mocks
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = []
        processor.filter_declarations.return_value = []
        
        scheduler = Scheduler(config_manager, *components)
        
        # Start scheduler
        scheduler.start()
        
        # Wait for at least 2 polling intervals
        time.sleep(5)
        
        # Stop scheduler
        scheduler.stop()
        
        # Verify workflow was executed at least once
        assert ecus_connector.get_new_declarations.call_count >= 1


def test_manual_mode_does_not_execute_automatically():
    """Test that manual mode does not execute workflow automatically"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = create_test_config_file(temp_dir, "manual")
        config_manager = ConfigurationManager(config_path)
        components = create_mock_components(config_manager)
        ecus_connector, tracking_db, processor, barcode_retriever, file_manager, logger = components
        
        # Set up mocks
        tracking_db.get_all_processed.return_value = set()
        ecus_connector.get_new_declarations.return_value = []
        processor.filter_declarations.return_value = []
        
        scheduler = Scheduler(config_manager, *components)
        
        # Start scheduler
        scheduler.start()
        
        # Wait for some time
        time.sleep(3)
        
        # Stop scheduler
        scheduler.stop()
        
        # Verify workflow was NOT executed automatically
        assert ecus_connector.get_new_declarations.call_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
