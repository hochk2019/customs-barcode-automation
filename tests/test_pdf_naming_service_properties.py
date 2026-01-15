"""
Property-based tests for PDF Naming Service

These tests use Hypothesis to verify correctness properties for PDF filename
generation across many random inputs.

**Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
**Validates: Requirements 5.3, 5.4, 5.5, 5.6**
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
import pytest

from models.declaration_models import Declaration
from file_utils.pdf_naming_service import PdfNamingService, PdfNamingFormat


# Strategy for generating valid alphanumeric strings (safe for filenames)
safe_text = st.text(
    min_size=1, 
    max_size=30, 
    alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )
)

# Strategy for generating optional text (can be None or empty)
optional_text = st.one_of(
    st.none(),
    st.just(""),
    st.just("   "),  # whitespace only
    safe_text
)

# Strategy for valid naming formats
naming_format_strategy = st.sampled_from(["tax_code", "invoice", "bill_of_lading"])


def create_declaration(
    declaration_number: str,
    tax_code: str = "1234567890",
    invoice_number: str = None,
    bill_of_lading: str = None
) -> Declaration:
    """Helper to create a Declaration with specified fields"""
    return Declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        declaration_date=datetime(2024, 12, 10),
        customs_office_code='18A3',
        transport_method='1',
        channel='Xanh',
        status='T',
        goods_description=None,
        invoice_number=invoice_number,
        bill_of_lading=bill_of_lading
    )


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.3, 5.4, 5.5, 5.6**
@given(
    declaration_number=safe_text,
    tax_code=safe_text,
    naming_format=naming_format_strategy
)
@settings(max_examples=100)
def test_property_filename_ends_with_pdf(declaration_number, tax_code, naming_format):
    """
    *For any* declaration and naming format, the generated filename should 
    always end with '.pdf'.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.3**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code
    )
    
    service = PdfNamingService(naming_format)
    filename = service.generate_filename(declaration)
    
    assert filename.endswith('.pdf'), \
        f"Filename should end with '.pdf', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.3, 5.4, 5.5, 5.6**
@given(
    declaration_number=safe_text,
    tax_code=safe_text,
    naming_format=naming_format_strategy
)
@settings(max_examples=100)
def test_property_filename_contains_declaration_number(declaration_number, tax_code, naming_format):
    """
    *For any* declaration and naming format, the generated filename should 
    always contain the declaration number.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.3, 5.5, 5.6**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code
    )
    
    service = PdfNamingService(naming_format)
    filename = service.generate_filename(declaration)
    
    assert declaration_number in filename, \
        f"Filename should contain declaration number '{declaration_number}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.3**
@given(
    declaration_number=safe_text,
    tax_code=safe_text
)
@settings(max_examples=100)
def test_property_tax_code_format(declaration_number, tax_code):
    """
    *For any* declaration with tax_code format, the filename should be 
    MV_{tax_code}_{declaration_number}.pdf
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.3**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code
    )
    
    service = PdfNamingService("tax_code")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{tax_code}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.5**
@given(
    declaration_number=safe_text,
    tax_code=safe_text,
    invoice_number=safe_text
)
@settings(max_examples=100)
def test_property_invoice_format(declaration_number, tax_code, invoice_number):
    """
    *For any* declaration with invoice format and non-empty invoice_number,
    the filename should be MV_{invoice_number}_{declaration_number}.pdf
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.5**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        invoice_number=invoice_number
    )
    
    service = PdfNamingService("invoice")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{invoice_number}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.6**
@given(
    declaration_number=safe_text,
    tax_code=safe_text,
    bill_of_lading=safe_text
)
@settings(max_examples=100)
def test_property_bill_of_lading_format(declaration_number, tax_code, bill_of_lading):
    """
    *For any* declaration with bill_of_lading format and non-empty bill_of_lading,
    the filename should be MV_{bill_of_lading}_{declaration_number}.pdf
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.6**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        bill_of_lading=bill_of_lading
    )
    
    service = PdfNamingService("bill_of_lading")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{bill_of_lading}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.4**
@given(
    declaration_number=safe_text,
    tax_code=safe_text
)
@settings(max_examples=100)
def test_property_fallback_invoice_to_tax_code(declaration_number, tax_code):
    """
    *For any* declaration with invoice format but empty invoice_number,
    the filename should fallback to tax_code format.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.4**
    """
    # Test with None invoice_number
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        invoice_number=None
    )
    
    service = PdfNamingService("invoice")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{tax_code}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected fallback to tax_code format '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.4**
@given(
    declaration_number=safe_text,
    tax_code=safe_text
)
@settings(max_examples=100)
def test_property_fallback_bill_of_lading_to_tax_code(declaration_number, tax_code):
    """
    *For any* declaration with bill_of_lading format but empty bill_of_lading,
    the filename should fallback to tax_code format.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.4**
    """
    # Test with empty string bill_of_lading
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        bill_of_lading=""
    )
    
    service = PdfNamingService("bill_of_lading")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{tax_code}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected fallback to tax_code format '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.4**
@given(
    declaration_number=safe_text,
    tax_code=safe_text
)
@settings(max_examples=100)
def test_property_fallback_whitespace_only_to_tax_code(declaration_number, tax_code):
    """
    *For any* declaration with invoice format but whitespace-only invoice_number,
    the filename should fallback to tax_code format.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.4**
    """
    # Test with whitespace-only invoice_number
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        invoice_number="   "
    )
    
    service = PdfNamingService("invoice")
    filename = service.generate_filename(declaration)
    
    expected = f"MV_{tax_code}_{declaration_number}.pdf"
    assert filename == expected, \
        f"Expected fallback to tax_code format '{expected}', got: {filename}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.3**
@given(naming_format=naming_format_strategy)
@settings(max_examples=100)
def test_property_invalid_format_defaults_to_tax_code(naming_format):
    """
    *For any* invalid naming format, the service should default to tax_code.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.3**
    """
    # Test with invalid format
    service = PdfNamingService("invalid_format")
    
    assert service.naming_format == "tax_code", \
        f"Invalid format should default to 'tax_code', got: {service.naming_format}"


# **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
# **Validates: Requirements 5.3, 5.4, 5.5, 5.6**
@given(
    declaration_number=safe_text,
    tax_code=safe_text,
    invoice_number=optional_text,
    bill_of_lading=optional_text,
    naming_format=naming_format_strategy
)
@settings(max_examples=100)
def test_property_filename_no_invalid_chars(
    declaration_number, tax_code, invoice_number, bill_of_lading, naming_format
):
    """
    *For any* declaration and naming format, the generated filename should 
    not contain invalid filename characters.
    
    **Feature: v1.1-ui-enhancements, Property 8: PDF Filename Generation**
    **Validates: Requirements 5.3, 5.4, 5.5, 5.6**
    """
    declaration = create_declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        invoice_number=invoice_number,
        bill_of_lading=bill_of_lading
    )
    
    service = PdfNamingService(naming_format)
    filename = service.generate_filename(declaration)
    
    # Check for invalid Windows filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        assert char not in filename, \
            f"Filename should not contain '{char}', got: {filename}"
