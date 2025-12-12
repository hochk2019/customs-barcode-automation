"""
Property-based tests for file management

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings
import os
import tempfile
import shutil

from models.declaration_models import Declaration
from file_utils.file_manager import FileManager


# Feature: customs-barcode-automation, Property 7: Filename format consistency
@given(
    tax_code=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'), 
        min_codepoint=48, 
        max_codepoint=122
    )),
    declaration_number=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    ))
)
@settings(max_examples=100)
def test_property_filename_format_consistency(tax_code, declaration_number):
    """
    For any CustomsDeclaration, the generated PDF filename should follow 
    the format "{TaxCode}_{DeclarationNumber}.pdf".
    
    **Validates: Requirements 5.1**
    """
    # Create a declaration with the given tax_code and declaration_number
    declaration = Declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        declaration_date=datetime(2023, 12, 6),
        customs_office_code='18A3',
        transport_method='1',
        channel='Xanh',
        status='T',
        goods_description=None
    )
    
    file_manager = FileManager('/tmp/test_output')
    filename = file_manager.generate_filename(declaration)
    
    # Expected format: TaxCode_DeclarationNumber.pdf
    expected = f"{tax_code}_{declaration_number}.pdf"
    
    assert filename == expected, \
        f"Filename should be '{expected}', but got '{filename}'"
    
    # Additional checks
    assert filename.endswith('.pdf'), \
        f"Filename should end with '.pdf', but got '{filename}'"
    
    assert '_' in filename, \
        f"Filename should contain underscore separator, but got '{filename}'"
    
    # Verify the filename starts with tax_code
    assert filename.startswith(tax_code), \
        f"Filename should start with tax_code '{tax_code}', but got '{filename}'"
    
    # Verify the filename contains declaration_number
    assert declaration_number in filename, \
        f"Filename should contain declaration_number '{declaration_number}', but got '{filename}'"



# Feature: customs-barcode-automation, Property 8: Directory creation before save
@given(
    tax_code=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )),
    declaration_number=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )),
    pdf_content=st.binary(min_size=100, max_size=1000)
)
@settings(max_examples=100)
def test_property_directory_creation_before_save(tax_code, declaration_number, pdf_content):
    """
    For any file save operation, if the output directory does not exist, 
    it should be created before attempting to save the file.
    
    **Validates: Requirements 5.2**
    """
    # Create a temporary directory path that doesn't exist yet
    temp_base = tempfile.mkdtemp()
    try:
        # Create a nested directory path that doesn't exist
        non_existent_dir = os.path.join(temp_base, 'nested', 'output', 'directory')
        
        # Verify the directory doesn't exist initially
        assert not os.path.exists(non_existent_dir), \
            "Test setup error: directory should not exist initially"
        
        # Create a declaration
        declaration = Declaration(
            declaration_number=declaration_number,
            tax_code=tax_code,
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        # Create FileManager with non-existent directory
        file_manager = FileManager(non_existent_dir)
        
        # Save the barcode - this should create the directory
        result = file_manager.save_barcode(declaration, pdf_content, overwrite=False)
        
        # Verify the directory was created
        assert os.path.exists(non_existent_dir), \
            f"Directory '{non_existent_dir}' should have been created before saving"
        
        # Verify the file was saved successfully
        assert result is not None, \
            "File should have been saved successfully"
        
        # Verify the file exists
        assert os.path.exists(result), \
            f"Saved file '{result}' should exist"
        
        # Verify the file content matches
        with open(result, 'rb') as f:
            saved_content = f.read()
        assert saved_content == pdf_content, \
            "Saved file content should match the original PDF content"
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_base):
            shutil.rmtree(temp_base)



# Feature: customs-barcode-automation, Property 9: Duplicate file handling
@given(
    tax_code=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )),
    declaration_number=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )),
    pdf_content_1=st.binary(min_size=100, max_size=500),
    pdf_content_2=st.binary(min_size=100, max_size=500)
)
@settings(max_examples=100, deadline=None)
def test_property_duplicate_file_handling(tax_code, declaration_number, pdf_content_1, pdf_content_2):
    """
    For any file save operation where a file with the same name already exists 
    and overwrite is False, the system should skip saving and log a warning.
    
    **Validates: Requirements 5.3**
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a declaration
        declaration = Declaration(
            declaration_number=declaration_number,
            tax_code=tax_code,
            declaration_date=datetime(2023, 12, 6),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        file_manager = FileManager(temp_dir)
        
        # First save - should succeed
        result1 = file_manager.save_barcode(declaration, pdf_content_1, overwrite=False)
        assert result1 is not None, \
            "First save should succeed"
        
        # Verify the file exists and has the correct content
        assert os.path.exists(result1), \
            "First saved file should exist"
        with open(result1, 'rb') as f:
            saved_content_1 = f.read()
        assert saved_content_1 == pdf_content_1, \
            "First saved file should have correct content"
        
        # Second save with overwrite=False - should skip (return None)
        result2 = file_manager.save_barcode(declaration, pdf_content_2, overwrite=False)
        assert result2 is None, \
            "Second save with overwrite=False should return None (skipped)"
        
        # Verify the file still has the original content (not overwritten)
        with open(result1, 'rb') as f:
            current_content = f.read()
        assert current_content == pdf_content_1, \
            "File content should remain unchanged when overwrite=False"
        
        # Third save with overwrite=True - should succeed and overwrite
        result3 = file_manager.save_barcode(declaration, pdf_content_2, overwrite=True)
        assert result3 is not None, \
            "Third save with overwrite=True should succeed"
        
        # Verify the file now has the new content
        with open(result3, 'rb') as f:
            final_content = f.read()
        assert final_content == pdf_content_2, \
            "File content should be updated when overwrite=True"
        
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
