"""
Integration tests for file management and error handling in declaration printing.
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from declaration_printing.file_manager import DeclarationFileManager, FileConflictAction
from declaration_printing.error_handler import DeclarationErrorHandler, DeclarationErrorType
from declaration_printing.models import DeclarationType
from logging_system.logger import Logger
from models.config_models import LoggingConfig


class TestFileManagementIntegration:
    """Test integration between file management and error handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = LoggingConfig(
            log_level='INFO',
            log_file='logs/test.log',
            max_log_size=1024*1024,
            backup_count=3
        )
        self.logger = Logger(self.config)
        self.file_manager = DeclarationFileManager(self.temp_dir, self.logger)
        self.error_handler = DeclarationErrorHandler(self.logger)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_successful_file_save(self):
        """Test successful file save operation."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        file_content = b"test excel content"
        
        # Act
        result = self.file_manager.save_excel_file(
            file_content, declaration_number, declaration_type
        )
        
        # Assert
        assert result.success
        assert result.file_path is not None
        assert Path(result.file_path).exists()
        assert result.action_taken == "created"
        
        # Verify file content
        with open(result.file_path, 'rb') as f:
            assert f.read() == file_content
    
    def test_file_conflict_overwrite(self):
        """Test file conflict resolution with overwrite."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        original_content = b"original content"
        new_content = b"new content"
        
        # Create original file
        result1 = self.file_manager.save_excel_file(
            original_content, declaration_number, declaration_type
        )
        assert result1.success
        
        # Set up conflict resolver to overwrite
        def conflict_resolver(file_path, decl_num):
            return FileConflictAction.OVERWRITE
        
        self.file_manager.conflict_resolver = conflict_resolver
        
        # Act - save new content
        result2 = self.file_manager.save_excel_file(
            new_content, declaration_number, declaration_type
        )
        
        # Assert
        assert result2.success
        assert result2.action_taken == "overwritten"
        
        # Verify new content
        with open(result2.file_path, 'rb') as f:
            assert f.read() == new_content
    
    def test_file_conflict_rename(self):
        """Test file conflict resolution with rename."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        original_content = b"original content"
        new_content = b"new content"
        
        # Create original file
        result1 = self.file_manager.save_excel_file(
            original_content, declaration_number, declaration_type
        )
        assert result1.success
        
        # Set up conflict resolver to rename
        def conflict_resolver(file_path, decl_num):
            return FileConflictAction.RENAME
        
        self.file_manager.conflict_resolver = conflict_resolver
        
        # Act - save new content
        result2 = self.file_manager.save_excel_file(
            new_content, declaration_number, declaration_type
        )
        
        # Assert
        assert result2.success
        assert result2.action_taken == "renamed"
        assert result2.file_path != result1.file_path
        
        # Verify both files exist with correct content
        with open(result1.file_path, 'rb') as f:
            assert f.read() == original_content
        with open(result2.file_path, 'rb') as f:
            assert f.read() == new_content
    
    def test_file_conflict_skip(self):
        """Test file conflict resolution with skip."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        original_content = b"original content"
        new_content = b"new content"
        
        # Create original file
        result1 = self.file_manager.save_excel_file(
            original_content, declaration_number, declaration_type
        )
        assert result1.success
        
        # Set up conflict resolver to skip
        def conflict_resolver(file_path, decl_num):
            return FileConflictAction.SKIP
        
        self.file_manager.conflict_resolver = conflict_resolver
        
        # Act - try to save new content
        result2 = self.file_manager.save_excel_file(
            new_content, declaration_number, declaration_type
        )
        
        # Assert
        assert result2.success
        assert result2.action_taken == "skipped"
        
        # Verify original content unchanged
        with open(result1.file_path, 'rb') as f:
            assert f.read() == original_content
    
    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        file_content = b"test content"
        
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            # Act
            result = self.file_manager.save_excel_file(
                file_content, declaration_number, declaration_type
            )
            
            # Assert
            assert not result.success
            assert "file_system" in result.error_message.lower()
    
    def test_disk_space_check(self):
        """Test disk space checking functionality."""
        # Act
        space_info = self.file_manager.get_disk_space_info()
        sufficient = self.file_manager.check_disk_space_sufficient(1024)  # 1KB
        
        # Assert
        assert 'total' in space_info
        assert 'used' in space_info
        assert 'free' in space_info
        assert space_info['total'] > 0
        assert sufficient  # Should have at least 1KB free
    
    def test_alternative_directory_selection(self):
        """Test alternative directory selection when primary fails."""
        # Arrange - create a file manager with invalid primary directory
        invalid_dir = "/invalid/path/that/does/not/exist"
        
        # Create file manager that will fail to initialize primary directory
        with patch.object(DeclarationFileManager, 'validate_and_create_directory') as mock_validate:
            # First call (primary directory) fails, second call (alternative) succeeds
            mock_validate.side_effect = [OSError("Cannot create directory"), None]
            
            with patch.object(DeclarationFileManager, 'get_alternative_output_directory') as mock_alt:
                mock_alt.return_value = Path(self.temp_dir)
                
                file_manager = DeclarationFileManager(invalid_dir, self.logger)
                
                # Act
                declaration_number = "305254403660"
                declaration_type = DeclarationType.EXPORT_CLEARANCE
                file_content = b"test content"
                
                result = file_manager.save_excel_file(
                    file_content, declaration_number, declaration_type
                )
                
                # Assert
                assert result.success
                # The file should be saved in the alternative directory
                assert result.file_path is not None
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        # Arrange
        declaration_number = "305254403660"
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        file_content = b"test content"
        
        # Act
        result = self.file_manager.save_excel_file(
            file_content, declaration_number, declaration_type
        )
        
        # Assert
        assert result.success
        
        # Check audit log
        audit_summary = self.file_manager.get_audit_summary()
        assert audit_summary['total_operations'] > 0
        assert audit_summary['successful_saves'] == 1
        assert audit_summary['failed_saves'] == 0
    
    def test_error_categorization(self):
        """Test error categorization and handling."""
        # Test different error types with appropriate contexts
        test_cases = [
            (FileNotFoundError("Template not found"), "template loading", DeclarationErrorType.TEMPLATE_NOT_FOUND),
            (PermissionError("Access denied"), "file saving", DeclarationErrorType.FILE_PERMISSION_DENIED),
            (OSError("No space left on device"), "file saving", DeclarationErrorType.INSUFFICIENT_DISK_SPACE),
            (ValueError("Invalid data"), "data validation", DeclarationErrorType.DATA_VALIDATION_FAILED),
        ]
        
        for exception, context, expected_type in test_cases:
            # Act
            error = self.error_handler.categorize_and_handle_error(
                exception, "305254403660", context
            )
            
            # Assert
            assert error.error_type == expected_type
            assert error.declaration_number == "305254403660"
            assert len(error.recovery_suggestions) > 0
    
    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        # Arrange - create some temporary files
        temp_file1 = Path(self.temp_dir) / "temp1.tmp"
        temp_file2 = Path(self.temp_dir) / "temp2.tmp"
        
        temp_file1.write_text("temp content 1")
        temp_file2.write_text("temp content 2")
        
        # Act
        cleaned_count = self.file_manager.cleanup_temp_files(max_age_hours=0)  # Clean all
        
        # Assert
        assert cleaned_count == 2
        assert not temp_file1.exists()
        assert not temp_file2.exists()
    
    def test_filename_generation(self):
        """Test filename generation for different declaration types."""
        test_cases = [
            ("305254403660", DeclarationType.EXPORT_CLEARANCE, "ToKhaiHQ7X_QDTQ_305254403660.xlsx"),
            ("107772836360", DeclarationType.IMPORT_CLEARANCE, "ToKhaiHQ7N_QDTQ_107772836360.xlsx"),
            ("305254403660", DeclarationType.EXPORT_ROUTING, "ToKhaiHQ7X_PL_305254403660.xlsx"),
            ("107772836360", DeclarationType.IMPORT_ROUTING, "ToKhaiHQ7N_PL_107772836360.xlsx"),
        ]
        
        for decl_num, decl_type, expected_filename in test_cases:
            # Act
            filename = self.file_manager.generate_filename(decl_num, decl_type)
            
            # Assert
            assert filename == expected_filename
    
    def test_error_statistics_tracking(self):
        """Test error statistics tracking."""
        # Arrange
        declaration_number = "305254403660"
        
        # Generate some errors with appropriate contexts
        error_cases = [
            (FileNotFoundError("Template not found"), "template loading"),
            (PermissionError("Access denied"), "file saving"),
            (FileNotFoundError("Another template not found"), "template loading"),
        ]
        
        for error, context in error_cases:
            self.error_handler.categorize_and_handle_error(
                error, declaration_number, context
            )
        
        # Act
        stats = self.error_handler.get_error_statistics()
        
        # Assert
        assert stats['total_errors'] == 3
        assert stats['error_counts']['template_not_found'] == 2
        assert stats['error_counts']['file_permission_denied'] == 1
        assert len(stats['recent_errors']) == 3
        assert stats['most_common_error'] == 'template_not_found'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])