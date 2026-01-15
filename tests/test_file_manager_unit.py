"""
Unit tests for FileManager

These tests verify specific functionality of the FileManager class.
"""

import os
import tempfile
import shutil
import pytest
from datetime import datetime

from models.declaration_models import Declaration
from file_utils.file_manager import FileManager


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_declaration():
    """Create a sample declaration for testing"""
    return Declaration(
        declaration_number='308010891440',
        tax_code='2300782217',
        declaration_date=datetime(2023, 1, 5),
        customs_office_code='18A3',
        transport_method='1',
        channel='Xanh',
        status='T',
        goods_description=None
    )


def test_filename_generation(sample_declaration):
    """
    Test that filenames are generated in the correct format.
    
    Requirements: 5.1
    """
    file_manager = FileManager('/tmp/output')
    filename = file_manager.generate_filename(sample_declaration)
    
    expected = 'MV_2300782217_308010891440.pdf'
    assert filename == expected
    assert filename.endswith('.pdf')
    assert '_' in filename


def test_filename_generation_with_special_characters():
    """
    Test filename generation with various tax codes and declaration numbers.
    
    Requirements: 5.1
    """
    declaration = Declaration(
        declaration_number='ABC123XYZ789',
        tax_code='0700798384',
        declaration_date=datetime(2022, 12, 30),
        customs_office_code='18A3',
        transport_method='1',
        channel='Vang',
        status='T',
        goods_description=None
    )
    
    file_manager = FileManager('/tmp/output')
    filename = file_manager.generate_filename(declaration)
    
    expected = 'MV_0700798384_ABC123XYZ789.pdf'
    assert filename == expected


def test_get_file_path(sample_declaration, temp_directory):
    """
    Test that full file paths are constructed correctly.
    
    Requirements: 5.1
    """
    file_manager = FileManager(temp_directory)
    file_path = file_manager.get_file_path(sample_declaration)
    
    expected_filename = 'MV_2300782217_308010891440.pdf'
    expected_path = os.path.join(temp_directory, expected_filename)
    
    assert file_path == expected_path
    assert temp_directory in file_path
    assert expected_filename in file_path


def test_file_exists_when_file_does_not_exist(sample_declaration, temp_directory):
    """
    Test file_exists returns False when file doesn't exist.
    
    Requirements: 5.3
    """
    file_manager = FileManager(temp_directory)
    exists = file_manager.file_exists(sample_declaration)
    
    assert exists is False


def test_file_exists_when_file_exists(sample_declaration, temp_directory):
    """
    Test file_exists returns True when file exists.
    
    Requirements: 5.3
    """
    file_manager = FileManager(temp_directory)
    
    # Create the file
    file_path = file_manager.get_file_path(sample_declaration)
    with open(file_path, 'wb') as f:
        f.write(b'test content')
    
    exists = file_manager.file_exists(sample_declaration)
    assert exists is True


def test_directory_creation(temp_directory):
    """
    Test that directories are created when they don't exist.
    
    Requirements: 5.2
    """
    # Create a nested directory path that doesn't exist
    nested_dir = os.path.join(temp_directory, 'level1', 'level2', 'level3')
    
    assert not os.path.exists(nested_dir)
    
    file_manager = FileManager(nested_dir)
    file_manager.ensure_directory_exists()
    
    assert os.path.exists(nested_dir)
    assert os.path.isdir(nested_dir)


def test_directory_creation_when_already_exists(temp_directory):
    """
    Test that ensure_directory_exists works when directory already exists.
    
    Requirements: 5.2
    """
    file_manager = FileManager(temp_directory)
    
    # Should not raise an error
    file_manager.ensure_directory_exists()
    
    assert os.path.exists(temp_directory)


def test_save_barcode_success(sample_declaration, temp_directory):
    """
    Test successful PDF saving.
    
    Requirements: 5.1, 5.2, 5.4
    """
    file_manager = FileManager(temp_directory)
    pdf_content = b'%PDF-1.4\ntest pdf content'
    
    result = file_manager.save_barcode(sample_declaration, pdf_content, overwrite=False)
    
    assert result is not None
    assert os.path.exists(result)
    
    # Verify content
    with open(result, 'rb') as f:
        saved_content = f.read()
    assert saved_content == pdf_content


def test_save_barcode_creates_directory(sample_declaration):
    """
    Test that save_barcode creates directory if it doesn't exist.
    
    Requirements: 5.2
    """
    temp_base = tempfile.mkdtemp()
    try:
        nested_dir = os.path.join(temp_base, 'new', 'directory')
        assert not os.path.exists(nested_dir)
        
        file_manager = FileManager(nested_dir)
        pdf_content = b'test content'
        
        result = file_manager.save_barcode(sample_declaration, pdf_content, overwrite=False)
        
        assert result is not None
        assert os.path.exists(nested_dir)
        assert os.path.exists(result)
    finally:
        if os.path.exists(temp_base):
            shutil.rmtree(temp_base)


def test_save_barcode_skip_when_exists(sample_declaration, temp_directory):
    """
    Test that save_barcode skips when file exists and overwrite=False.
    
    Requirements: 5.3
    """
    file_manager = FileManager(temp_directory)
    
    # First save
    original_content = b'original content'
    result1 = file_manager.save_barcode(sample_declaration, original_content, overwrite=False)
    assert result1 is not None
    
    # Second save with different content and overwrite=False
    new_content = b'new content'
    result2 = file_manager.save_barcode(sample_declaration, new_content, overwrite=False)
    
    # Should return None (skipped)
    assert result2 is None
    
    # Verify original content is preserved
    with open(result1, 'rb') as f:
        saved_content = f.read()
    assert saved_content == original_content


def test_overwrite_behavior(sample_declaration, temp_directory):
    """
    Test that save_barcode overwrites when overwrite=True.
    
    Requirements: 5.3, 5.4
    """
    file_manager = FileManager(temp_directory)
    
    # First save
    original_content = b'original content'
    result1 = file_manager.save_barcode(sample_declaration, original_content, overwrite=False)
    assert result1 is not None
    
    # Second save with overwrite=True
    new_content = b'new content that is different'
    result2 = file_manager.save_barcode(sample_declaration, new_content, overwrite=True)
    
    # Should succeed
    assert result2 is not None
    assert result2 == result1  # Same path
    
    # Verify new content is saved
    with open(result2, 'rb') as f:
        saved_content = f.read()
    assert saved_content == new_content


def test_error_handling_invalid_directory():
    """
    Test error handling when directory creation fails.
    
    Requirements: 5.5
    """
    # Try to create a directory in an invalid location (Windows)
    # Using a path with invalid characters
    invalid_dir = 'C:\\invalid<>path\\test'
    
    file_manager = FileManager(invalid_dir)
    
    declaration = Declaration(
        declaration_number='123456789012',
        tax_code='1234567890',
        declaration_date=datetime(2023, 12, 6),
        customs_office_code='18A3',
        transport_method='1',
        channel='Xanh',
        status='T',
        goods_description=None
    )
    
    pdf_content = b'test content'
    
    # Should raise OSError
    with pytest.raises(OSError):
        file_manager.save_barcode(declaration, pdf_content, overwrite=False)


def test_save_empty_pdf_content(sample_declaration, temp_directory):
    """
    Test saving empty PDF content (edge case).
    
    Requirements: 5.4
    """
    file_manager = FileManager(temp_directory)
    empty_content = b''
    
    result = file_manager.save_barcode(sample_declaration, empty_content, overwrite=False)
    
    assert result is not None
    assert os.path.exists(result)
    
    # Verify empty content is saved
    with open(result, 'rb') as f:
        saved_content = f.read()
    assert saved_content == empty_content
    assert len(saved_content) == 0


def test_save_large_pdf_content(sample_declaration, temp_directory):
    """
    Test saving large PDF content.
    
    Requirements: 5.4
    """
    file_manager = FileManager(temp_directory)
    
    # Create a large content (1 MB)
    large_content = b'x' * (1024 * 1024)
    
    result = file_manager.save_barcode(sample_declaration, large_content, overwrite=False)
    
    assert result is not None
    assert os.path.exists(result)
    
    # Verify content size
    file_size = os.path.getsize(result)
    assert file_size == len(large_content)
