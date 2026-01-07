"""
Unit tests for template installation functionality.

Tests template file validation, loading, field mapping configuration parsing,
and template integrity checking.

Requirements: 4.1, 4.2, 4.5
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from declaration_printing.template_installer import TemplateInstaller, TemplateInstallationError
from declaration_printing.template_manager import TemplateManager, TemplateError
from declaration_printing.models import DeclarationType


class TestTemplateInstallation(unittest.TestCase):
    """Unit tests for template installation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.installer = TemplateInstaller(str(self.template_dir))
        self.template_manager = TemplateManager(str(self.template_dir))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_template_file_validation_success(self):
        """Test successful template file validation."""
        # Create a mock Excel file and mapping file
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        mapping_file = self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json"
        template_file.write_bytes(b"mock excel content")
        mapping_file.write_text('{"declaration_number": "B5"}')
        
        # Mock the template manager validation and permission checker
        with patch.object(self.installer.template_manager, 'validate_template', return_value=True):
            with patch.object(self.installer.permission_checker, 'check_file_access', return_value=(True, None)):
                is_valid, issues = self.installer.validate_template_file(str(template_file))
        
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)  # No issues when mapping file exists
    
    def test_template_file_validation_missing_file(self):
        """Test template file validation with missing file."""
        non_existent_file = self.template_dir / "missing.xlsx"
        
        is_valid, issues = self.installer.validate_template_file(str(non_existent_file))
        
        self.assertFalse(is_valid)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0], "Template file does not exist")
    
    def test_template_file_validation_invalid_extension(self):
        """Test template file validation with invalid extension."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        invalid_file = self.template_dir / "template.txt"
        invalid_file.write_text("not an excel file")
        
        is_valid, issues = self.installer.validate_template_file(str(invalid_file))
        
        self.assertFalse(is_valid)
        self.assertIn("Invalid file extension", issues[0])
    
    def test_template_loading_success(self):
        """Test successful template loading."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        template_file.write_bytes(b"mock excel content")
        
        with patch('declaration_printing.template_manager.load_workbook') as mock_load:
            mock_workbook = Mock()
            mock_workbook.worksheets = [Mock()]  # At least one worksheet
            mock_load.return_value = mock_workbook
            
            is_valid = self.template_manager.validate_template(str(template_file))
            
            self.assertTrue(is_valid)
            mock_load.assert_called_once_with(str(template_file), read_only=True)
            mock_workbook.close.assert_called_once()
    
    def test_template_loading_no_worksheets(self):
        """Test template loading with no worksheets."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        template_file.write_bytes(b"mock excel content")
        
        with patch('declaration_printing.template_manager.load_workbook') as mock_load:
            mock_workbook = Mock()
            mock_workbook.worksheets = []  # No worksheets
            mock_load.return_value = mock_workbook
            
            with self.assertRaises(TemplateError) as context:
                self.template_manager.validate_template(str(template_file))
            
            self.assertIn("Template has no worksheets", str(context.exception))
    
    def test_field_mapping_configuration_parsing_success(self):
        """Test successful field mapping configuration parsing."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        mapping_file = self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json"
        
        # Create mock mapping file
        mapping_data = {
            "declaration_number": "B5",
            "company_name": "B10",
            "total_value": "F20"
        }
        mapping_file.write_text(json.dumps(mapping_data, ensure_ascii=False))
        
        mapping = self.template_manager.load_template_mapping(str(template_file))
        
        self.assertEqual(mapping, mapping_data)
    
    def test_field_mapping_configuration_parsing_invalid_json(self):
        """Test field mapping configuration parsing with invalid JSON."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        mapping_file = self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json"
        
        # Create invalid JSON file
        mapping_file.write_text("{ invalid json }")
        
        # Should fall back to default mapping
        mapping = self.template_manager.load_template_mapping(str(template_file))
        
        # Should return default mapping for 7N template
        self.assertIn("declaration_number", mapping)
        self.assertIn("company_name", mapping)
        self.assertEqual(mapping["declaration_number"], "B5")
    
    def test_field_mapping_configuration_parsing_missing_file(self):
        """Test field mapping configuration parsing with missing mapping file."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        
        # No mapping file exists
        mapping = self.template_manager.load_template_mapping(str(template_file))
        
        # Should return default mapping for 7N template
        self.assertIn("declaration_number", mapping)
        self.assertIn("company_name", mapping)
        self.assertEqual(mapping["declaration_number"], "B5")
    
    def test_template_integrity_checking_corrupted_file(self):
        """Test template integrity checking with corrupted file."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        template_file.write_bytes(b"corrupted content")
        
        with patch('declaration_printing.template_manager.load_workbook', side_effect=Exception("Corrupted file")):
            with self.assertRaises(TemplateError) as context:
                self.template_manager.validate_template(str(template_file))
            
            self.assertIn("Failed to load template", str(context.exception))
            self.assertIn("Corrupted file", str(context.exception))
    
    def test_template_integrity_checking_xls_format(self):
        """Test template integrity checking with .xls format."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xls"
        template_file.write_bytes(b"mock xls content")
        
        # .xls files should pass basic validation with warning
        is_valid = self.template_manager.validate_template(str(template_file))
        
        self.assertTrue(is_valid)
    
    def test_check_template_installation_complete(self):
        """Test checking template installation when complete."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock template files
        export_template = self.template_dir / "ToKhaiHQ7X_QDTQ.xlsx"
        import_template = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        export_template.write_bytes(b"mock excel")
        import_template.write_bytes(b"mock excel")
        
        # Create mapping files
        export_mapping = self.template_dir / "ToKhaiHQ7X_QDTQ_mapping.json"
        import_mapping = self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json"
        export_mapping.write_text('{"declaration_number": "B5"}')
        import_mapping.write_text('{"declaration_number": "B5"}')
        
        with patch.object(self.installer.template_manager, 'validate_template', return_value=True):
            with patch.object(self.installer.permission_checker, 'check_directory_access', return_value=(True, None)):
                is_complete, status = self.installer.check_template_installation()
        
        self.assertTrue(is_complete)
        self.assertTrue(status['directory_exists'])
        self.assertTrue(status['directory_accessible'])
        self.assertEqual(len(status['missing_templates']), 0)
        self.assertEqual(len(status['invalid_templates']), 0)
    
    def test_check_template_installation_missing_directory(self):
        """Test checking template installation with missing directory."""
        # Don't create the directory
        is_complete, status = self.installer.check_template_installation()
        
        self.assertFalse(is_complete)
        self.assertFalse(status['directory_exists'])
        self.assertIn("Template directory does not exist", status['errors'][0])
        self.assertIn("Create the templates directory", status['suggestions'][0])
    
    def test_check_template_installation_missing_templates(self):
        """Test checking template installation with missing templates."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        with patch.object(self.installer.permission_checker, 'check_directory_access', return_value=(True, None)):
            is_complete, status = self.installer.check_template_installation()
        
        self.assertFalse(is_complete)
        self.assertTrue(status['directory_exists'])
        self.assertTrue(status['directory_accessible'])
        self.assertEqual(len(status['missing_templates']), 2)  # Both export and import templates
        self.assertIn("ToKhaiHQ7X_QDTQ.xlsx", status['missing_templates'])
        self.assertIn("ToKhaiHQ7N_QDTQ.xlsx", status['missing_templates'])
    
    def test_install_sample_templates_success(self):
        """Test successful installation of sample templates."""
        # Create source directory with sample templates
        source_dir = Path(self.temp_dir) / "sample"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        sample_export = source_dir / "ToKhaiHQ7X_QDTQ.xlsx"
        sample_import = source_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        sample_export.write_bytes(b"mock export template")
        sample_import.write_bytes(b"mock import template")
        
        success, messages = self.installer.install_sample_templates(str(source_dir))
        
        self.assertTrue(success)
        self.assertIn("Successfully installed 2 template(s)", messages[-1])
        
        # Check that templates were copied
        self.assertTrue((self.template_dir / "ToKhaiHQ7X_QDTQ.xlsx").exists())
        self.assertTrue((self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx").exists())
        
        # Check that mapping files were created
        self.assertTrue((self.template_dir / "ToKhaiHQ7X_QDTQ_mapping.json").exists())
        self.assertTrue((self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json").exists())
    
    def test_install_sample_templates_missing_source(self):
        """Test installation with missing source directory."""
        non_existent_source = Path(self.temp_dir) / "missing_source"
        
        success, messages = self.installer.install_sample_templates(str(non_existent_source))
        
        self.assertFalse(success)
        self.assertIn("Source directory does not exist", messages[0])
    
    def test_install_sample_templates_partial_success(self):
        """Test installation with only some templates available."""
        # Create source directory with only one template
        source_dir = Path(self.temp_dir) / "sample"
        source_dir.mkdir(parents=True, exist_ok=True)
        
        sample_import = source_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        sample_import.write_bytes(b"mock import template")
        
        success, messages = self.installer.install_sample_templates(str(source_dir))
        
        self.assertTrue(success)  # Should succeed if at least one template is installed
        self.assertIn("Successfully installed 1 template(s)", messages[-1])
        self.assertIn("Template not found in source: ToKhaiHQ7X_QDTQ.xlsx", messages)
    
    def test_create_mapping_file(self):
        """Test creating mapping configuration file."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        
        mapping_data = {
            "declaration_number": "B5",
            "company_name": "B10"
        }
        
        self.template_manager.create_mapping_file(str(template_file), mapping_data)
        
        # Check that mapping file was created
        mapping_file = self.template_dir / "ToKhaiHQ7N_QDTQ_mapping.json"
        self.assertTrue(mapping_file.exists())
        
        # Check content
        with open(mapping_file, 'r', encoding='utf-8') as f:
            saved_mapping = json.load(f)
        
        self.assertEqual(saved_mapping, mapping_data)
    
    def test_get_available_templates(self):
        """Test getting list of available templates."""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create only import template
        import_template = self.template_dir / "ToKhaiHQ7N_QDTQ.xlsx"
        import_template.write_bytes(b"mock template")
        
        available = self.template_manager.get_available_templates()
        
        # Should find import template but not export template
        self.assertIsNotNone(available[DeclarationType.IMPORT_CLEARANCE])
        self.assertIsNone(available[DeclarationType.EXPORT_CLEARANCE])
        self.assertIn("ToKhaiHQ7N_QDTQ.xlsx", available[DeclarationType.IMPORT_CLEARANCE])


if __name__ == '__main__':
    unittest.main()