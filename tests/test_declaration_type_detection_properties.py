"""
Property-based tests for declaration type detection

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings

from declaration_printing.type_detector import DeclarationTypeDetector
from declaration_printing.models import DeclarationType


# **Feature: customs-declaration-printing, Property 1: Declaration type classification and template selection**
# **Validates: Requirements 1.2, 1.3, 2.1, 2.2**
@given(
    export_suffix=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))),
    import_suffix=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',)))
)
@settings(max_examples=100)
def test_property_declaration_type_classification_and_template_selection(export_suffix, import_suffix):
    """
    For any valid declaration number, the system should correctly classify it as export (30...) 
    or import (10...) and select the corresponding template (ToKhaiHQ7X_QDTQ or ToKhaiHQ7N_QDTQ).
    
    **Feature: customs-declaration-printing, Property 1: Declaration type classification and template selection**
    **Validates: Requirements 1.2, 1.3, 2.1, 2.2**
    """
    detector = DeclarationTypeDetector()
    
    # Create valid export and import numbers
    export_number = "30" + export_suffix
    import_number = "10" + import_suffix
    
    # Test export declaration classification
    export_type = detector.detect_type(export_number)
    assert export_type == DeclarationType.EXPORT_CLEARANCE, \
        f"Export declaration {export_number} should be classified as EXPORT_CLEARANCE, got {export_type}"
    
    # Test export declaration boolean check
    assert detector.is_export_declaration(export_number), \
        f"Declaration {export_number} should be identified as export declaration"
    assert not detector.is_import_declaration(export_number), \
        f"Declaration {export_number} should not be identified as import declaration"
    
    # Test export template selection
    export_template = detector.get_template_name(export_type)
    assert export_template == "ToKhaiHQ7X_QDTQ.xlsx", \
        f"Export declaration should use ToKhaiHQ7X_QDTQ.xlsx template, got {export_template}"
    
    # Test import declaration classification
    import_type = detector.detect_type(import_number)
    assert import_type == DeclarationType.IMPORT_CLEARANCE, \
        f"Import declaration {import_number} should be classified as IMPORT_CLEARANCE, got {import_type}"
    
    # Test import declaration boolean check
    assert detector.is_import_declaration(import_number), \
        f"Declaration {import_number} should be identified as import declaration"
    assert not detector.is_export_declaration(import_number), \
        f"Declaration {import_number} should not be identified as export declaration"
    
    # Test import template selection
    import_template = detector.get_template_name(import_type)
    assert import_template == "ToKhaiHQ7N_QDTQ.xlsx", \
        f"Import declaration should use ToKhaiHQ7N_QDTQ.xlsx template, got {import_template}"


@given(
    invalid_number=st.one_of(
        # Too short
        st.text(min_size=1, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        # Too long
        st.text(min_size=13, max_size=20, alphabet=st.characters(whitelist_categories=('Nd',))),
        # Contains non-digits
        st.text(min_size=12, max_size=12).filter(lambda x: not x.isdigit()),
        # Empty string
        st.just(""),
        # Starts with unsupported prefix (not 10 or 30)
        st.text(min_size=12, max_size=12).filter(
            lambda x: x.isdigit() and len(x) == 12 and not x.startswith('10') and not x.startswith('30')
        )
    )
)
@settings(max_examples=100)
def test_property_invalid_declaration_numbers_raise_errors(invalid_number):
    """
    For any invalid declaration number format or unsupported type, the system should raise ValueError.
    
    **Feature: customs-declaration-printing, Property 1: Declaration type classification and template selection**
    **Validates: Requirements 2.3**
    """
    detector = DeclarationTypeDetector()
    
    # Invalid declaration numbers should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        detector.detect_type(invalid_number)
    
    # Error message should be informative
    error_message = str(exc_info.value)
    assert len(error_message) > 0, "Error message should not be empty"
    assert invalid_number in error_message or "Invalid" in error_message or "Cannot determine" in error_message, \
        f"Error message should mention the invalid number or indicate validation failure: {error_message}"


@given(
    valid_12_digit=st.text(min_size=12, max_size=12, alphabet=st.characters(whitelist_categories=('Nd',)))
)
@settings(max_examples=100)
def test_property_valid_format_validation(valid_12_digit):
    """
    For any 12-digit string, the validation should pass format checks, but may fail type detection
    if it doesn't start with supported prefixes.
    
    **Feature: customs-declaration-printing, Property 1: Declaration type classification and template selection**
    **Validates: Requirements 2.1, 2.2**
    """
    detector = DeclarationTypeDetector()
    
    # All 12-digit strings should pass format validation
    is_valid_format = detector._is_valid_declaration_number(valid_12_digit)
    assert is_valid_format, f"12-digit number {valid_12_digit} should pass format validation"
    
    # But only those starting with 10 or 30 should successfully detect type
    if valid_12_digit.startswith('10'):
        declaration_type = detector.detect_type(valid_12_digit)
        assert declaration_type == DeclarationType.IMPORT_CLEARANCE
        assert detector.is_import_declaration(valid_12_digit)
        assert not detector.is_export_declaration(valid_12_digit)
    elif valid_12_digit.startswith('30'):
        declaration_type = detector.detect_type(valid_12_digit)
        assert declaration_type == DeclarationType.EXPORT_CLEARANCE
        assert detector.is_export_declaration(valid_12_digit)
        assert not detector.is_import_declaration(valid_12_digit)
    else:
        # Should raise ValueError for unsupported prefixes
        with pytest.raises(ValueError) as exc_info:
            detector.detect_type(valid_12_digit)
        
        error_message = str(exc_info.value)
        assert "Cannot determine" in error_message or "type" in error_message, \
            f"Error should indicate type detection failure: {error_message}"


# **Feature: customs-declaration-printing, Property 4: Error handling and continuation**
# **Validates: Requirements 2.3, 2.5, 7.2**
@given(
    mixed_declarations=st.lists(
        st.one_of(
            # Valid export declarations
            st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))).map(lambda x: "30" + x),
            # Valid import declarations  
            st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))).map(lambda x: "10" + x),
            # Invalid format declarations
            st.one_of(
                st.text(min_size=1, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),  # Too short
                st.text(min_size=13, max_size=20, alphabet=st.characters(whitelist_categories=('Nd',))),  # Too long
                st.text(min_size=12, max_size=12).filter(lambda x: not x.isdigit()),  # Non-digits
                st.just(""),  # Empty
                # Unsupported prefixes (not 10 or 30)
                st.text(min_size=12, max_size=12).filter(
                    lambda x: x.isdigit() and len(x) == 12 and not x.startswith('10') and not x.startswith('30')
                )
            )
        ),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=100)
def test_property_error_handling_and_continuation(mixed_declarations):
    """
    For any batch of declarations containing invalid items, the system should log errors for 
    invalid items and continue processing valid ones.
    
    **Feature: customs-declaration-printing, Property 4: Error handling and continuation**
    **Validates: Requirements 2.3, 2.5, 7.2**
    """
    detector = DeclarationTypeDetector()
    
    valid_results = []
    error_results = []
    
    # Process each declaration and track results
    for declaration_number in mixed_declarations:
        try:
            declaration_type = detector.detect_type(declaration_number)
            valid_results.append((declaration_number, declaration_type))
        except ValueError as e:
            error_results.append((declaration_number, str(e)))
    
    # Verify that valid declarations were processed successfully
    for declaration_number, declaration_type in valid_results:
        # Valid declarations should have correct type
        if declaration_number.startswith('30'):
            assert declaration_type == DeclarationType.EXPORT_CLEARANCE, \
                f"Export declaration {declaration_number} should be EXPORT_CLEARANCE"
        elif declaration_number.startswith('10'):
            assert declaration_type == DeclarationType.IMPORT_CLEARANCE, \
                f"Import declaration {declaration_number} should be IMPORT_CLEARANCE"
    
    # Verify that invalid declarations produced meaningful errors
    for declaration_number, error_message in error_results:
        # Error message should be informative
        assert len(error_message) > 0, "Error message should not be empty"
        assert ("Invalid" in error_message or "Cannot determine" in error_message), \
            f"Error message should indicate the problem: {error_message}"
        
        # Verify the declaration was actually invalid
        is_valid_format = detector._is_valid_declaration_number(declaration_number)
        if is_valid_format:
            # If format is valid, it should be unsupported type
            assert not (declaration_number.startswith('10') or declaration_number.startswith('30')), \
                f"Valid format declaration {declaration_number} should have unsupported prefix"
        else:
            # If format is invalid, it should fail format validation
            assert not is_valid_format, f"Declaration {declaration_number} should fail format validation"
    
    # The system should continue processing despite errors (no exceptions should propagate)
    # This is demonstrated by the fact that we can process the entire list
    total_processed = len(valid_results) + len(error_results)
    assert total_processed == len(mixed_declarations), \
        "All declarations should be processed (either successfully or with error)"


@given(
    declaration_type=st.sampled_from([
        DeclarationType.EXPORT_CLEARANCE,
        DeclarationType.IMPORT_CLEARANCE,
        DeclarationType.EXPORT_ROUTING,
        DeclarationType.IMPORT_ROUTING
    ])
)
@settings(max_examples=100)
def test_property_template_name_mapping_completeness(declaration_type):
    """
    For any supported declaration type, the system should return a valid template filename.
    
    **Feature: customs-declaration-printing, Property 1: Declaration type classification and template selection**
    **Validates: Requirements 1.2, 1.3**
    """
    detector = DeclarationTypeDetector()
    
    template_name = detector.get_template_name(declaration_type)
    
    # Template name should not be empty
    assert template_name, f"Template name should not be empty for {declaration_type}"
    
    # Template name should end with .xlsx
    assert template_name.endswith('.xlsx'), f"Template name should end with .xlsx: {template_name}"
    
    # Template name should follow expected patterns
    if declaration_type in [DeclarationType.EXPORT_CLEARANCE, DeclarationType.EXPORT_ROUTING]:
        assert template_name.startswith('ToKhaiHQ7X'), \
            f"Export template should start with ToKhaiHQ7X: {template_name}"
    else:
        assert template_name.startswith('ToKhaiHQ7N'), \
            f"Import template should start with ToKhaiHQ7N: {template_name}"
    
    # Template name should contain appropriate suffix
    if declaration_type in [DeclarationType.EXPORT_CLEARANCE, DeclarationType.IMPORT_CLEARANCE]:
        assert 'QDTQ' in template_name, f"Clearance template should contain QDTQ: {template_name}"
    else:
        assert 'PL' in template_name, f"Routing template should contain PL: {template_name}"