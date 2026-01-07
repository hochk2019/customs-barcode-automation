"""
Tests for security validation and protection features.
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from declaration_printing.security_validator import (
    DataSanitizer, FilePermissionValidator, SecureQueryBuilder,
    SecurityAuditLogger, XMLSecurityError, FileSecurityError, SecurityError
)
from logging_system.logger import Logger, SensitiveDataFilter
from models.config_models import LoggingConfig


class TestDataSanitizer:
    """Test data sanitization features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.sanitizer = DataSanitizer(self.logger)
    
    def test_sanitize_xml_content_removes_xxe_patterns(self):
        """Test that XXE attack patterns are detected and removed."""
        malicious_xml = '''<?xml version="1.0"?>
        <!DOCTYPE test [
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <root>&xxe;</root>'''
        
        with pytest.raises(XMLSecurityError):
            self.sanitizer.sanitize_xml_content(malicious_xml)
    
    def test_sanitize_xml_content_removes_doctype(self):
        """Test that DOCTYPE declarations are removed."""
        xml_with_doctype = '''<?xml version="1.0"?>
        <!DOCTYPE root>
        <root><data>test</data></root>'''
        
        sanitized = self.sanitizer.sanitize_xml_content(xml_with_doctype)
        assert '<!DOCTYPE' not in sanitized
        assert '<root><data>test</data></root>' in sanitized
    
    def test_validate_xml_structure_accepts_valid_xml(self):
        """Test that valid ECUS XML structure is accepted."""
        valid_xml = '''<?xml version="1.0"?>
        <ECUS5VNACCS2018>
            <DToKhaiMD>
                <Data>
                    <SOTK>123456789012</SOTK>
                </Data>
            </DToKhaiMD>
        </ECUS5VNACCS2018>'''
        
        result = self.sanitizer.validate_xml_structure(valid_xml)
        assert result is True
    
    def test_validate_xml_structure_rejects_invalid_root(self):
        """Test that invalid XML root elements are rejected."""
        invalid_xml = '''<?xml version="1.0"?>
        <malicious>
            <script>alert('xss')</script>
        </malicious>'''
        
        with pytest.raises(XMLSecurityError):
            self.sanitizer.validate_xml_structure(invalid_xml)
    
    def test_sanitize_sql_parameter_detects_injection(self):
        """Test that SQL injection attempts are detected."""
        malicious_params = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "EXEC xp_cmdshell('dir')",
            "/* comment */ SELECT * FROM"
        ]
        
        for param in malicious_params:
            with pytest.raises(SecurityError):
                self.sanitizer.sanitize_sql_parameter(param)
    
    def test_sanitize_sql_parameter_allows_valid_data(self):
        """Test that valid parameters are allowed."""
        valid_params = [
            "123456789012",  # Declaration number
            "0123456789",    # Tax code
            "Company Name Ltd",
            None,
            123
        ]
        
        for param in valid_params:
            result = self.sanitizer.sanitize_sql_parameter(param)
            assert result == param or (param is None and result is None)
    
    def test_sanitize_for_logging_redacts_sensitive_data(self):
        """Test that sensitive data is redacted in log messages."""
        sensitive_message = "Processing declaration 123456789012 for tax code 0123456789"
        
        sanitized = self.sanitizer.sanitize_for_logging(sensitive_message)
        
        assert "123456789012" not in sanitized
        assert "0123456789" not in sanitized
        assert "[DECLARATION_NUMBER]" in sanitized
        assert "[TAX_CODE]" in sanitized
    
    def test_validate_file_path_prevents_traversal(self):
        """Test that directory traversal attempts are prevented."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32"
        ]
        
        for path in malicious_paths:
            with pytest.raises(FileSecurityError, match="directory traversal attempt"):
                self.sanitizer.validate_file_path(path)
    
    def test_validate_file_path_allows_safe_paths(self):
        """Test that safe file paths are allowed."""
        safe_paths = [
            "output/file.xlsx",
            "templates/template.xlsx",
            "data/sample.xml"
        ]
        
        for path in safe_paths:
            result = self.sanitizer.validate_file_path(path)
            assert isinstance(result, Path)
    
    def test_generate_secure_filename(self):
        """Test secure filename generation."""
        base_name = "test<>file|name"
        result = self.sanitizer.generate_secure_filename(base_name)
        
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert result.endswith(".xlsx")
        assert len(result) > len(base_name)  # Should include timestamp


class TestFilePermissionValidator:
    """Test file permission validation features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.validator = FilePermissionValidator(self.logger)
    
    def test_validate_file_permissions_existing_file(self):
        """Test validation of existing file permissions."""
        # Create a test file in current directory to avoid path validation issues
        test_file = Path("test_security_file.txt")
        test_file.write_text("test content")
        
        try:
            permissions = self.validator.validate_file_permissions(test_file)
            
            assert permissions['exists'] is True
            assert permissions['readable'] is True
            assert permissions['is_file'] is True
            assert permissions['is_directory'] is False
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_validate_directory_permissions_creates_directory(self):
        """Test that directory validation creates missing directories."""
        test_dir = Path("test_security_dir")
        
        try:
            result = self.validator.validate_directory_permissions(test_dir)
            
            assert result is True
            assert test_dir.exists()
            assert test_dir.is_dir()
        finally:
            if test_dir.exists():
                import shutil
                shutil.rmtree(test_dir)
    
    def test_secure_file_write_creates_backup(self):
        """Test that secure file write creates backups."""
        file_path = Path("test_security.xlsx")
        
        try:
            # Create initial file
            file_path.write_bytes(b"original content")
            
            # Write new content
            new_content = b"new content"
            result = self.validator.secure_file_write(file_path, new_content, backup_existing=True)
            
            assert result is True
            assert file_path.read_bytes() == new_content
            
            # Check backup was created
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            assert backup_path.exists()
            assert backup_path.read_bytes() == b"original content"
        finally:
            # Clean up test files
            for test_file in [file_path, file_path.with_suffix(f"{file_path.suffix}.backup")]:
                if test_file.exists():
                    test_file.unlink()
    
    def test_validate_template_file_checks_extension(self):
        """Test that template validation checks file extensions."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            with pytest.raises(FileSecurityError):
                self.validator.validate_template_file(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_template_file_checks_size(self):
        """Test that template validation checks file size."""
        test_file = Path("test_large_template.xlsx")
        test_file.write_bytes(b"test content")
        
        try:
            # Mock the stat method to return a large file size
            import stat
            from unittest.mock import Mock
            mock_stat = Mock()
            mock_stat.st_size = 100 * 1024 * 1024  # 100MB
            mock_stat.st_mode = stat.S_IFREG | 0o644  # Regular file mode
            
            with patch.object(Path, 'stat', return_value=mock_stat):
                with pytest.raises(FileSecurityError, match="Template file too large"):
                    self.validator.validate_template_file(test_file)
        finally:
            if test_file.exists():
                test_file.unlink()


class TestSecureQueryBuilder:
    """Test secure query building features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock()
        self.builder = SecureQueryBuilder(self.logger)
    
    def test_build_declaration_query_sanitizes_parameters(self):
        """Test that declaration queries sanitize parameters."""
        declaration_number = "123456789012"
        
        query, params = self.builder.build_declaration_query(declaration_number)
        
        assert "?" in query
        assert "SOTK = ?" in query
        assert params[0] == declaration_number
        assert "SELECT" in query.upper()
        assert "FROM DTOKHAIMD" in query
    
    def test_build_declaration_query_with_filters(self):
        """Test declaration query with additional filters."""
        declaration_number = "123456789012"
        filters = {
            'tax_code': '0123456789',
            'status': 'T'
        }
        
        query, params = self.builder.build_declaration_query(declaration_number, filters)
        
        assert len(params) == 3  # declaration_number + 2 filters
        assert "MA_DV = ?" in query
        assert "TTTK = ?" in query
        assert params[0] == declaration_number
        assert params[1] == filters['tax_code']
        assert params[2] == filters['status']
    
    def test_build_goods_query_structure(self):
        """Test goods query structure."""
        declaration_number = "123456789012"
        
        query, params = self.builder.build_goods_query(declaration_number)
        
        assert "DHANGMDDK" in query
        assert "INNER JOIN DTOKHAIMD" in query
        assert "SOTK = ?" in query
        assert len(params) == 1
        assert params[0] == declaration_number
    
    def test_validate_query_parameters_sanitizes_all(self):
        """Test that all query parameters are sanitized."""
        params = ["123456789012", "Company Name", "'; DROP TABLE"]
        
        # Should raise error for malicious parameter
        with pytest.raises(SecurityError):
            self.builder.validate_query_parameters(params)


class TestSecurityAuditLogger:
    """Test security audit logging features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.base_logger = Mock()
        self.audit_logger = SecurityAuditLogger(self.base_logger)
    
    def test_log_security_event_sanitizes_details(self):
        """Test that security events sanitize sensitive details."""
        details = {
            'declaration_number': '123456789012',
            'file_path': '/path/to/file.xlsx',
            'operation': 'write'
        }
        
        self.audit_logger.log_security_event('FILE_ACCESS', 'test_user', details)
        
        # Check that logger was called
        self.base_logger.warning.assert_called_once()
        call_args = self.base_logger.warning.call_args[0][0]
        
        assert 'SECURITY_AUDIT: FILE_ACCESS' in call_args
        assert 'User: test_user' in call_args
        assert '[DECLARATION_NUMBER]' in call_args
        assert '123456789012' not in call_args
    
    def test_log_file_access(self):
        """Test file access logging."""
        self.audit_logger.log_file_access('/path/to/file.xlsx', 'read', True)
        
        self.base_logger.warning.assert_called_once()
        call_args = self.base_logger.warning.call_args[0][0]
        
        assert 'FILE_ACCESS' in call_args
        assert 'read' in call_args
        assert 'True' in call_args
    
    def test_log_database_access(self):
        """Test database access logging."""
        self.audit_logger.log_database_access('SELECT', 'DTOKHAIMD', 2, True)
        
        self.base_logger.warning.assert_called_once()
        call_args = self.base_logger.warning.call_args[0][0]
        
        assert 'DATABASE_ACCESS' in call_args
        assert 'SELECT' in call_args
        assert 'DTOKHAIMD' in call_args
    
    def test_log_xml_processing(self):
        """Test XML processing logging."""
        self.audit_logger.log_xml_processing('/path/to/file.xml', True, True)
        
        self.base_logger.warning.assert_called_once()
        call_args = self.base_logger.warning.call_args[0][0]
        
        assert 'XML_PROCESSING' in call_args
        assert 'True' in call_args


class TestSensitiveDataFilter:
    """Test sensitive data filtering in logging."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.filter = SensitiveDataFilter()
    
    def test_filter_redacts_declaration_numbers(self):
        """Test that declaration numbers are redacted."""
        import logging
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='Processing declaration 123456789012', args=(), exc_info=None
        )
        
        self.filter.filter(record)
        
        assert '123456789012' not in record.msg
        assert '[DECLARATION_NUMBER]' in record.msg
    
    def test_filter_redacts_passwords(self):
        """Test that passwords are redacted."""
        import logging
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='Login with password=secret123', args=(), exc_info=None
        )
        
        self.filter.filter(record)
        
        assert 'secret123' not in record.msg
        assert 'password=[REDACTED]' in record.msg
    
    def test_filter_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        import logging
        
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='Processing completed successfully', args=(), exc_info=None
        )
        
        original_msg = record.msg
        self.filter.filter(record)
        
        assert record.msg == original_msg


class TestIntegratedSecurity:
    """Test integrated security features."""
    
    def test_end_to_end_security_workflow(self):
        """Test complete security workflow from XML to database."""
        # This would be an integration test that combines all security features
        # Testing the complete flow: XML sanitization -> SQL parameterization -> File security
        pass
    
    def test_security_audit_trail(self):
        """Test that security events create proper audit trail."""
        # Test that all security operations are properly logged and auditable
        pass


if __name__ == '__main__':
    pytest.main([__file__])