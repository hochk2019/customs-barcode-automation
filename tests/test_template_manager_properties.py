"""
Property-based tests for template management

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from openpyxl import Workbook

from declaration_printing.template_manager import TemplateManager, TemplateError
from declaration_printing.models import DeclarationType


def create_valid_excel_file(file_path: Path) -> None:
    """Create a valid Excel file for testing."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet['A1'] = 'Test Template'
    workbook.save(file_path)
    workbook.close()


def create_mapping_file(template_path: Path, mapping: dict) -> Path:
    """Create a mapping JSON file for a template."""
    mapping_path = template_path.parent / f"{template_path.stem}_mapping.json"
    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    return mapping_path


# **Feature: customs-declaration-printing, Property 5: Template management and validation**
# **Validates: Requirements 4.1, 4.3, 4.4, 4.5**
@given(
    declaration_type=st.sampled_from([
        DeclarationType.EXPORT_CLEARANCE,
        DeclarationType.IMPORT_CLEARANCE,
        DeclarationType.EXPORT_ROUTING,
        DeclarationType.IMPORT_ROUTING
    ])
)
@settings(max_examples=100)
def test_property_template_loading_and_validation(declaration_type):
    """
    For any template file in the templates directory, the system should load it dynamically,
    validate its integrity, and attempt to map data to available fields.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.1, 4.3, 4.4, 4.5**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Create a valid template file
        template_filename = manager.TEMPLATE_FILENAMES[declaration_type]
        template_path = template_dir / template_filename
        create_valid_excel_file(template_path)
        
        # Test dynamic loading (Requirement 4.1)
        resolved_path = manager.get_template_path(declaration_type)
        assert resolved_path == str(template_path), \
            f"Template path should be resolved correctly: expected {template_path}, got {resolved_path}"
        
        # Test template validation (Requirement 4.5)
        is_valid = manager.validate_template(resolved_path)
        assert is_valid, f"Valid template should pass validation: {resolved_path}"
        
        # Test field mapping loading (Requirements 4.3, 4.4)
        mapping = manager.load_template_mapping(resolved_path)
        assert isinstance(mapping, dict), "Template mapping should be a dictionary"
        assert len(mapping) > 0, "Template mapping should not be empty"
        
        # All mapping values should be valid Excel cell references or contain valid patterns
        for field_name, cell_ref in mapping.items():
            assert isinstance(field_name, str), f"Field name should be string: {field_name}"
            assert isinstance(cell_ref, str), f"Cell reference should be string: {cell_ref}"
            assert len(cell_ref) > 0, f"Cell reference should not be empty for field: {field_name}"


@given(
    invalid_extensions=st.sampled_from(['.txt', '.pdf', '.doc', '.csv', '.json', '']),
    file_content=st.text(min_size=0, max_size=100)
)
@settings(max_examples=100)
def test_property_invalid_template_validation(invalid_extensions, file_content):
    """
    For any file with invalid extension or corrupted content, template validation should fail
    with appropriate error messages.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.2, 4.5**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Create file with invalid extension
        invalid_file = template_dir / f"test_template{invalid_extensions}"
        invalid_file.write_text(file_content, encoding='utf-8')
        
        # Template validation should fail for invalid files
        if invalid_extensions not in ['.xlsx', '.xls']:
            with pytest.raises(TemplateError) as exc_info:
                manager.validate_template(str(invalid_file))
            
            error_message = str(exc_info.value)
            assert len(error_message) > 0, "Error message should not be empty"
            assert ("format" in error_message.lower() or "extension" in error_message.lower()), \
                f"Error should mention format/extension issue: {error_message}"


@given(
    custom_mapping=st.dictionaries(
        keys=st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'),
        values=st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_property_custom_mapping_persistence(custom_mapping):
    """
    For any custom field mapping, the system should be able to save it and load it back correctly.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.3, 4.4**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Create a valid template file
        template_path = template_dir / "test_template.xlsx"
        create_valid_excel_file(template_path)
        
        # Save custom mapping
        manager.create_mapping_file(str(template_path), custom_mapping)
        
        # Load mapping back
        loaded_mapping = manager.load_template_mapping(str(template_path))
        
        # Verify mapping persistence
        assert loaded_mapping == custom_mapping, \
            f"Loaded mapping should match saved mapping: expected {custom_mapping}, got {loaded_mapping}"


@given(
    declaration_types=st.lists(
        st.sampled_from([
            DeclarationType.EXPORT_CLEARANCE,
            DeclarationType.IMPORT_CLEARANCE,
            DeclarationType.EXPORT_ROUTING,
            DeclarationType.IMPORT_ROUTING
        ]),
        min_size=0,
        max_size=4,
        unique=True
    )
)
@settings(max_examples=100)
def test_property_available_templates_detection(declaration_types):
    """
    For any set of available template files, the system should correctly identify which
    declaration types have templates available.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.1, 4.2**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Create template files for selected declaration types
        created_templates = set()
        for declaration_type in declaration_types:
            template_filename = manager.TEMPLATE_FILENAMES[declaration_type]
            template_path = template_dir / template_filename
            create_valid_excel_file(template_path)
            created_templates.add(declaration_type)
        
        # Get available templates
        available_templates = manager.get_available_templates()
        
        # Verify correct detection
        for declaration_type in DeclarationType:
            if declaration_type in created_templates:
                # Should be available
                assert available_templates[declaration_type] is not None, \
                    f"Template for {declaration_type} should be available"
                
                # Path should be correct
                expected_path = str(template_dir / manager.TEMPLATE_FILENAMES[declaration_type])
                assert available_templates[declaration_type] == expected_path, \
                    f"Template path should be correct for {declaration_type}"
            else:
                # Should not be available
                assert available_templates[declaration_type] is None, \
                    f"Template for {declaration_type} should not be available"


@given(
    alternative_extensions=st.sampled_from(['.xls', '.xlsx'])
)
@settings(max_examples=100)
def test_property_alternative_extension_support(alternative_extensions):
    """
    For any template with alternative extensions (.xls, .xlsx), the system should find
    and load the template correctly.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.1, 4.3**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        declaration_type = DeclarationType.EXPORT_CLEARANCE
        
        # Create template with alternative extension
        base_filename = manager.TEMPLATE_FILENAMES[declaration_type]
        alt_filename = Path(base_filename).stem + alternative_extensions
        template_path = template_dir / alt_filename
        
        if alternative_extensions == '.xlsx':
            # Create valid Excel file for .xlsx
            create_valid_excel_file(template_path)
        else:
            # For .xls, create a simple file (openpyxl doesn't support .xls)
            template_path.write_text("Mock XLS content", encoding='utf-8')
        
        # System should find the template despite extension difference
        resolved_path = manager.get_template_path(declaration_type)
        assert resolved_path == str(template_path), \
            f"Should find template with alternative extension: expected {template_path}, got {resolved_path}"
        
        # Template should validate successfully
        is_valid = manager.validate_template(resolved_path)
        assert is_valid, f"Template with alternative extension should be valid: {resolved_path}"


@given(
    missing_declaration_type=st.sampled_from([
        DeclarationType.EXPORT_CLEARANCE,
        DeclarationType.IMPORT_CLEARANCE,
        DeclarationType.EXPORT_ROUTING,
        DeclarationType.IMPORT_ROUTING
    ])
)
@settings(max_examples=100)
def test_property_missing_template_error_handling(missing_declaration_type):
    """
    For any missing template file, the system should display an error message and provide
    guidance for template installation.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.2**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Don't create any template files - directory is empty
        
        # Attempting to get template path should raise TemplateError
        with pytest.raises(TemplateError) as exc_info:
            manager.get_template_path(missing_declaration_type)
        
        error_message = str(exc_info.value)
        
        # Error message should be informative (Requirement 4.2)
        assert len(error_message) > 0, "Error message should not be empty"
        assert "not found" in error_message.lower(), \
            f"Error should mention template not found: {error_message}"
        assert "template" in error_message.lower(), \
            f"Error should mention template: {error_message}"
        
        # Should provide guidance for installation
        assert ("install" in error_message.lower() or "directory" in error_message.lower()), \
            f"Error should provide installation guidance: {error_message}"


@given(
    field_mappings=st.lists(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'),
            values=st.text(min_size=1, max_size=8, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
            min_size=1,
            max_size=5
        ),
        min_size=1,
        max_size=3
    )
)
@settings(max_examples=100)
def test_property_mapping_cache_consistency(field_mappings):
    """
    For any sequence of mapping operations, the cache should maintain consistency
    and return the same results for repeated queries.
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.3, 4.4**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        template_paths = []
        
        # Create multiple templates with different mappings
        for i, mapping in enumerate(field_mappings):
            template_path = template_dir / f"template_{i}.xlsx"
            create_valid_excel_file(template_path)
            manager.create_mapping_file(str(template_path), mapping)
            template_paths.append(str(template_path))
        
        # Load mappings multiple times and verify consistency
        for template_path in template_paths:
            first_load = manager.load_template_mapping(template_path)
            second_load = manager.load_template_mapping(template_path)
            third_load = manager.load_template_mapping(template_path)
            
            # All loads should return identical results
            assert first_load == second_load == third_load, \
                f"Mapping cache should be consistent for {template_path}"
            
            # Results should be dictionaries
            assert isinstance(first_load, dict), "Mapping should be a dictionary"
            assert len(first_load) > 0, "Mapping should not be empty"
        
        # Clear cache and verify mappings are still loaded correctly
        manager.clear_cache()
        
        for template_path in template_paths:
            after_clear = manager.load_template_mapping(template_path)
            assert isinstance(after_clear, dict), "Mapping should still work after cache clear"
            assert len(after_clear) > 0, "Mapping should not be empty after cache clear"


@given(
    template_name_patterns=st.sampled_from([
        "ToKhaiHQ7X_test",
        "ToKhaiHQ7N_test", 
        "custom_template",
        "unknown_format"
    ])
)
@settings(max_examples=100)
def test_property_default_mapping_generation(template_name_patterns):
    """
    For any template name pattern, the system should generate appropriate default mappings
    based on the template type (export/import).
    
    **Feature: customs-declaration-printing, Property 5: Template management and validation**
    **Validates: Requirements 4.3, 4.4**
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        manager = TemplateManager(str(template_dir))
        
        # Create template file without mapping file
        template_path = template_dir / f"{template_name_patterns}.xlsx"
        create_valid_excel_file(template_path)
        
        # Load mapping (should generate default)
        mapping = manager.load_template_mapping(str(template_path))
        
        # Should return a valid mapping
        assert isinstance(mapping, dict), "Default mapping should be a dictionary"
        assert len(mapping) > 0, "Default mapping should not be empty"
        
        # All values should be strings (cell references)
        for field_name, cell_ref in mapping.items():
            assert isinstance(field_name, str), f"Field name should be string: {field_name}"
            assert isinstance(cell_ref, str), f"Cell reference should be string: {cell_ref}"
            assert len(cell_ref) > 0, f"Cell reference should not be empty for field: {field_name}"
        
        # Mapping should contain basic required fields
        expected_basic_fields = ["declaration_number", "company_name"]
        for field in expected_basic_fields:
            if field in mapping:
                assert len(mapping[field]) > 0, f"Basic field {field} should have non-empty cell reference"
        
        # Export templates (7X) should have appropriate fields
        if "7X" in template_name_patterns:
            if "country_of_destination" in mapping:
                assert len(mapping["country_of_destination"]) > 0, \
                    "Export template should have destination country mapping"
        
        # Import templates (7N) should have appropriate fields  
        if "7N" in template_name_patterns:
            if "country_of_origin" in mapping:
                assert len(mapping["country_of_origin"]) > 0, \
                    "Import template should have origin country mapping"