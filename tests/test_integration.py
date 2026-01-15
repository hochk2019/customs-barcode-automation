"""
Integration tests for the Customs Barcode Automation application.

These tests verify end-to-end functionality including:
- Configuration loading and validation
- Database connectivity
- File operations
- Error recovery
- Workflow execution
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from config.configuration_manager import ConfigurationManager, ConfigurationError
from logging_system.logger import Logger
from models.config_models import LoggingConfig, DatabaseConfig, BarcodeServiceConfig
from models.declaration_models import Declaration, OperationMode
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from file_utils.file_manager import FileManager


class TestConfigurationIntegration:
    """Integration tests for configuration loading and validation"""
    
    def test_configuration_loading_and_validation(self, tmp_path):
        """Test end-to-end configuration loading and validation"""
        # Create a valid configuration file
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[Database]
server = localhost
database = ECUS5VNACCS
username = testuser
password = testpass
timeout = 30

[BarcodeService]
api_url = http://test.api.com
primary_web_url = http://test.primary.com
backup_web_url = http://test.backup.com
timeout = 30

[Application]
output_directory = C:\\TestOutput
polling_interval = 300
max_retries = 3
retry_delay = 5
operation_mode = automatic

[Logging]
log_level = INFO
log_file = logs/test.log
max_log_size = 10485760
backup_count = 5
""")
        
        # Load and validate configuration
        config_manager = ConfigurationManager(str(config_file))
        config_manager.validate()
        
        # Verify all configurations can be retrieved
        db_config = config_manager.get_database_config()
        assert db_config.server == "localhost"
        assert db_config.database == "ECUS5VNACCS"
        
        barcode_config = config_manager.get_barcode_service_config()
        assert barcode_config.api_url == "http://test.api.com"
        
        output_path = config_manager.get_output_path()
        assert output_path == "C:\\TestOutput"
        
        polling_interval = config_manager.get_polling_interval()
        assert polling_interval == 300
        
        operation_mode = config_manager.get_operation_mode()
        assert operation_mode == "automatic"
    
    def test_configuration_validation_missing_section(self, tmp_path):
        """Test that configuration validation fails with missing sections"""
        # Create an invalid configuration file (missing Database section)
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[BarcodeService]
api_url = http://test.api.com
primary_web_url = http://test.primary.com
backup_web_url = http://test.backup.com

[Application]
output_directory = C:\\TestOutput
""")
        
        # Load configuration
        config_manager = ConfigurationManager(str(config_file))
        
        # Validation should fail
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        assert "Missing [Database] section" in str(exc_info.value)
    
    def test_configuration_validation_missing_field(self, tmp_path):
        """Test that configuration validation fails with missing required fields"""
        # Create an invalid configuration file (missing required field)
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[Database]
server = localhost
database = ECUS5VNACCS
username = testuser

[BarcodeService]
api_url = http://test.api.com
primary_web_url = http://test.primary.com
backup_web_url = http://test.backup.com

[Application]
output_directory = C:\\TestOutput
""")
        
        # Load configuration
        config_manager = ConfigurationManager(str(config_file))
        
        # Validation should fail
        with pytest.raises(ConfigurationError) as exc_info:
            config_manager.validate()
        
        assert "Missing Database.password" in str(exc_info.value)


class TestDatabaseConnectivityIntegration:
    """Integration tests for database connectivity"""
    
    def test_tracking_database_initialization(self, tmp_path):
        """Test tracking database initialization and basic operations"""
        # Create tracking database
        db_path = tmp_path / "tracking.db"
        tracking_db = TrackingDatabase(str(db_path))
        
        # Verify database file was created
        assert db_path.exists()
        
        # Test basic operations
        declaration = Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="1801",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
        
        # Add processed declaration
        file_path = "C:\\TestOutput\\MV_0123456789_123456.pdf"
        tracking_db.add_processed(declaration, file_path)
        
        # Verify it was added
        assert tracking_db.is_processed(declaration)
        
        # Get all processed IDs
        processed_ids = tracking_db.get_all_processed()
        assert len(processed_ids) == 1
        assert declaration.id in processed_ids


class TestFileOperationsIntegration:
    """Integration tests for file operations"""
    
    def test_file_manager_directory_creation_and_save(self, tmp_path):
        """Test file manager creates directories and saves files"""
        # Create file manager with non-existent directory
        output_dir = tmp_path / "output" / "barcodes"
        file_manager = FileManager(str(output_dir))
        
        # Ensure directory exists
        file_manager.ensure_directory_exists()
        
        # Verify directory was created
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Create a test declaration
        declaration = Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="1801",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
        
        # Save a test PDF
        pdf_content = b"%PDF-1.4 test content"
        file_path = file_manager.save_barcode(declaration, pdf_content)
        
        # Verify file was saved
        assert file_path is not None
        assert os.path.exists(file_path)
        
        # Verify filename format
        expected_filename = "MV_0123456789_123456.pdf"
        assert file_path.endswith(expected_filename)
        
        # Verify content
        with open(file_path, 'rb') as f:
            saved_content = f.read()
        assert saved_content == pdf_content
    
    def test_file_manager_duplicate_handling(self, tmp_path):
        """Test file manager handles duplicate files correctly"""
        output_dir = tmp_path / "output"
        file_manager = FileManager(str(output_dir))
        file_manager.ensure_directory_exists()
        
        declaration = Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=datetime(2023, 12, 6),
            customs_office_code="1801",
            transport_method="1",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
        
        # Save first time
        pdf_content = b"%PDF-1.4 first version"
        file_path1 = file_manager.save_barcode(declaration, pdf_content, overwrite=False)
        assert file_path1 is not None
        
        # Try to save again without overwrite - should return None
        pdf_content2 = b"%PDF-1.4 second version"
        file_path2 = file_manager.save_barcode(declaration, pdf_content2, overwrite=False)
        assert file_path2 is None
        
        # Verify original content is unchanged
        with open(file_path1, 'rb') as f:
            saved_content = f.read()
        assert saved_content == pdf_content
        
        # Save again with overwrite - should succeed
        file_path3 = file_manager.save_barcode(declaration, pdf_content2, overwrite=True)
        assert file_path3 is not None
        
        # Verify content was updated
        with open(file_path3, 'rb') as f:
            saved_content = f.read()
        assert saved_content == pdf_content2


class TestErrorRecoveryIntegration:
    """Integration tests for error recovery"""
    
    def test_declaration_processor_filters_correctly(self):
        """Test declaration processor applies all business rules correctly"""
        processor = DeclarationProcessor()
        
        # Create test declarations with various characteristics
        declarations = [
            # Valid green channel declaration
            Declaration(
                declaration_number="123456",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description="Normal goods"
            ),
            # Valid yellow channel declaration
            Declaration(
                declaration_number="123457",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="2",
                channel="Vang",
                status="T",
                goods_description="Normal goods"
            ),
            # Invalid - red channel
            Declaration(
                declaration_number="123458",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Do",
                status="T",
                goods_description="Normal goods"
            ),
            # Invalid - not cleared
            Declaration(
                declaration_number="123459",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Xanh",
                status="P",
                goods_description="Normal goods"
            ),
            # Invalid - transport method 9999
            Declaration(
                declaration_number="123460",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="9999",
                channel="Xanh",
                status="T",
                goods_description="Normal goods"
            ),
            # Invalid - internal code NKTC
            Declaration(
                declaration_number="123461",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description="#&NKTC special goods"
            ),
            # Invalid - internal code XKTC
            Declaration(
                declaration_number="123462",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description="#&XKTC special goods"
            ),
        ]
        
        # Filter declarations
        eligible = processor.filter_declarations(declarations)
        
        # Should only have 2 valid declarations
        assert len(eligible) == 2
        assert eligible[0].declaration_number == "123456"
        assert eligible[1].declaration_number == "123457"


class TestWorkflowIntegration:
    """Integration tests for end-to-end workflow"""
    
    def test_workflow_components_integration(self, tmp_path):
        """Test that all workflow components work together"""
        # Set up test environment
        output_dir = tmp_path / "output"
        db_path = tmp_path / "tracking.db"
        
        # Initialize components
        file_manager = FileManager(str(output_dir))
        file_manager.ensure_directory_exists()
        
        tracking_db = TrackingDatabase(str(db_path))
        processor = DeclarationProcessor()
        
        # Create test declarations
        declarations = [
            Declaration(
                declaration_number="123456",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description="Test goods"
            ),
            Declaration(
                declaration_number="123457",
                tax_code="0123456789",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="1801",
                transport_method="9999",  # Should be filtered out
                channel="Xanh",
                status="T",
                goods_description="Test goods"
            ),
        ]
        
        # Filter declarations
        eligible = processor.filter_declarations(declarations)
        assert len(eligible) == 1
        
        # Simulate processing
        for declaration in eligible:
            # Simulate barcode retrieval
            pdf_content = b"%PDF-1.4 test barcode"
            
            # Save file
            file_path = file_manager.save_barcode(declaration, pdf_content)
            assert file_path is not None
            
            # Track as processed
            tracking_db.add_processed(declaration, file_path)
        
        # Verify tracking
        assert tracking_db.is_processed(eligible[0])
        
        # Verify file exists
        expected_file = output_dir / "MV_0123456789_123456.pdf"
        assert expected_file.exists()
        
        # Get processed IDs for next cycle
        processed_ids = tracking_db.get_all_processed()
        assert len(processed_ids) == 1
        
        # Simulate next cycle - should filter out already processed
        new_declarations = declarations.copy()
        filtered_by_tracking = [d for d in new_declarations if d.id not in processed_ids]
        assert len(filtered_by_tracking) == 1  # Only the one with transport 9999
        
        # Apply business rules
        eligible_new = processor.filter_declarations(filtered_by_tracking)
        assert len(eligible_new) == 0  # Should be filtered out by transport method


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
