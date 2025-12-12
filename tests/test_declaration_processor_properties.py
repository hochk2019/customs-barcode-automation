"""
Property-based tests for declaration processing

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings

from models.declaration_models import Declaration
from processors.declaration_processor import DeclarationProcessor


# Feature: customs-barcode-automation, Property 2: Channel filtering correctness
@given(
    channel=st.sampled_from(['Xanh', 'Vang', 'Do', 'Tím', 'Cam', 'Khác']),
    status=st.sampled_from(['T', 'P', 'H', 'K', 'X'])
)
@settings(max_examples=100)
def test_property_channel_filtering_correctness(channel, status):
    """
    For any CustomsDeclaration, it should be marked as eligible if and only if
    its channel is either 'Xanh' (Green) or 'Vang' (Yellow) AND its status is 'T' (Cleared).
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
    """
    # Create a declaration with the given channel and status
    # Use valid values for other fields
    declaration = Declaration(
        declaration_number='123456789012',
        tax_code='1234567890',
        declaration_date=datetime(2023, 12, 6),
        customs_office_code='18A3',
        transport_method='1',  # Valid transport method (not 9999)
        channel=channel,
        status=status,
        goods_description=None  # No internal codes
    )
    
    processor = DeclarationProcessor()
    is_eligible = processor.is_eligible(declaration)
    
    # Expected eligibility: channel must be Xanh or Vang AND status must be T
    expected_eligible = (channel in ['Xanh', 'Vang']) and (status == 'T')
    
    assert is_eligible == expected_eligible, \
        f"Declaration with channel='{channel}' and status='{status}' should be " \
        f"{'eligible' if expected_eligible else 'ineligible'}, but got {is_eligible}"



# Feature: customs-barcode-automation, Property 3: Transport method exclusion
@given(
    transport_method=st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8', '9', '9999', '10', '11'])
)
@settings(max_examples=100)
def test_property_transport_method_exclusion(transport_method):
    """
    For any CustomsDeclaration with TransportMethod code '9999', it should be excluded from processing.
    
    **Validates: Requirements 3.1**
    """
    # Create a declaration with valid channel and status, but varying transport method
    declaration = Declaration(
        declaration_number='123456789012',
        tax_code='1234567890',
        declaration_date=datetime(2023, 12, 6),
        customs_office_code='18A3',
        transport_method=transport_method,
        channel='Xanh',  # Valid channel
        status='T',  # Valid status
        goods_description=None  # No internal codes
    )
    
    processor = DeclarationProcessor()
    is_eligible = processor.is_eligible(declaration)
    
    # Expected: should be ineligible if transport_method is '9999', eligible otherwise
    expected_eligible = (transport_method != '9999')
    
    assert is_eligible == expected_eligible, \
        f"Declaration with transport_method='{transport_method}' should be " \
        f"{'eligible' if expected_eligible else 'ineligible'}, but got {is_eligible}"



# Feature: customs-barcode-automation, Property 4: Internal code exclusion
@given(
    goods_description=st.one_of(
        st.none(),
        st.just('#&NKTC'),
        st.just('#&XKTC'),
        st.text(min_size=1, max_size=50).filter(lambda x: not x.startswith('#&NKTC') and not x.startswith('#&XKTC')),
        st.text(min_size=7, max_size=50).map(lambda x: '#&NKTC' + x),
        st.text(min_size=7, max_size=50).map(lambda x: '#&XKTC' + x)
    )
)
@settings(max_examples=100)
def test_property_internal_code_exclusion(goods_description):
    """
    For any CustomsDeclaration where the goods description starts with "#&NKTC" or "#&XKTC",
    it should be excluded from processing.
    
    **Validates: Requirements 3.2, 3.3**
    """
    # Create a declaration with valid channel, status, and transport method
    declaration = Declaration(
        declaration_number='123456789012',
        tax_code='1234567890',
        declaration_date=datetime(2023, 12, 6),
        customs_office_code='18A3',
        transport_method='1',  # Valid transport method
        channel='Xanh',  # Valid channel
        status='T',  # Valid status
        goods_description=goods_description
    )
    
    processor = DeclarationProcessor()
    is_eligible = processor.is_eligible(declaration)
    
    # Expected: should be ineligible if goods_description starts with #&NKTC or #&XKTC
    if goods_description is None:
        expected_eligible = True
    elif goods_description.startswith('#&NKTC') or goods_description.startswith('#&XKTC'):
        expected_eligible = False
    else:
        expected_eligible = True
    
    assert is_eligible == expected_eligible, \
        f"Declaration with goods_description='{goods_description}' should be " \
        f"{'eligible' if expected_eligible else 'ineligible'}, but got {is_eligible}"
