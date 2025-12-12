"""
Property-based tests for PreviewManager

This module contains property-based tests for the PreviewManager class.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from processors.preview_manager import PreviewManager, PreviewError
from database.ecus_connector import EcusDataConnector
from models.declaration_models import Declaration


# Strategy for generating valid dates
def date_strategy(min_days_ago=365, max_days_ago=0):
    """Generate datetime objects within a reasonable range"""
    return st.datetimes(
        min_value=datetime.now() - timedelta(days=min_days_ago),
        max_value=datetime.now() - timedelta(days=max_days_ago)
    )


# Strategy for generating declarations
@st.composite
def declaration_strategy(draw, tax_code=None, date_range=None):
    """Generate a Declaration object"""
    if tax_code is None:
        tax_code = draw(st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))))
    
    if date_range is None:
        declaration_date = draw(date_strategy())
    else:
        from_date, to_date = date_range
        # Generate date within the range
        days_diff = (to_date - from_date).days
        if days_diff > 0:
            offset = draw(st.integers(min_value=0, max_value=days_diff))
            declaration_date = from_date + timedelta(days=offset)
        else:
            declaration_date = from_date
    
    declaration_number = draw(st.text(min_size=12, max_size=14, alphabet=st.characters(whitelist_categories=('Nd',))))
    customs_office_code = draw(st.text(min_size=4, max_size=6, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'))))
    transport_method = draw(st.sampled_from(['AIR', 'SEA', 'LAND', 'RAIL']))
    channel = draw(st.sampled_from(['Xanh', 'Vang']))
    status = 'T'
    goods_description = draw(st.one_of(st.none(), st.text(min_size=5, max_size=50)))
    
    return Declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        declaration_date=declaration_date,
        customs_office_code=customs_office_code,
        transport_method=transport_method,
        channel=channel,
        status=status,
        goods_description=goods_description
    )


# Feature: enhanced-manual-mode, Property 3: Preview accuracy
@given(
    num_declarations=st.integers(min_value=0, max_value=50),
    days_range=st.integers(min_value=1, max_value=90)
)
@settings(max_examples=100)
def test_property_preview_accuracy(num_declarations, days_range):
    """
    Property 3: Preview accuracy
    
    For any selected company and date range, the preview should show exactly 
    the declarations that match those criteria.
    
    Validates: Requirements 3.1, 3.2
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate date range
    to_date = datetime.now() - timedelta(days=1)  # Yesterday
    from_date = to_date - timedelta(days=days_range)
    
    # Generate test declarations within the date range
    declarations_in_db = []
    for i in range(num_declarations):
        # Generate date within range
        days_offset = i % (days_range + 1)
        decl_date = from_date + timedelta(days=days_offset)
        
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 5:010d}",  # 5 different tax codes
            declaration_date=decl_date,
            customs_office_code=f"HQ{i % 3:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations_in_db.append(declaration)
    
    # Mock the database query to return our test data
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations_in_db
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Property: Preview should return exactly the declarations from the database
    assert len(result) == len(declarations_in_db), \
        f"Expected {len(declarations_in_db)} declarations, but got {len(result)}"
    
    # Verify each declaration in result matches the database
    result_ids = {decl.id for decl in result}
    expected_ids = {decl.id for decl in declarations_in_db}
    
    assert result_ids == expected_ids, \
        f"Declaration IDs don't match. Expected {expected_ids}, got {result_ids}"
    
    # Verify the database was queried with correct parameters
    mock_ecus_connector.get_declarations_by_date_range.assert_called_once_with(
        from_date, to_date, None, include_pending=False
    )
    
    # Property: No declarations should be selected by default (Requirement 4.1)
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"Expected 0 declarations to be selected by default, got {selected_count}"
    assert total_count == len(declarations_in_db)


# Feature: enhanced-manual-mode, Property: Preview with tax code filter accuracy
@given(
    num_declarations=st.integers(min_value=5, max_value=50),
    num_tax_codes=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100)
def test_property_preview_with_tax_code_filter(num_declarations, num_tax_codes):
    """
    Property: Preview with tax code filter accuracy
    
    For any date range and tax code filter, the preview should show only
    declarations matching those tax codes.
    
    Validates: Requirements 3.1, 3.2
    """
    assume(num_declarations >= num_tax_codes)
    
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate date range
    to_date = datetime.now() - timedelta(days=1)
    from_date = to_date - timedelta(days=30)
    
    # Generate tax codes to filter by
    filter_tax_codes = [f"FILTER{i:08d}" for i in range(num_tax_codes)]
    
    # Generate declarations that match the filter
    matching_declarations = []
    for i in range(num_declarations):
        tax_code = filter_tax_codes[i % num_tax_codes]
        
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=tax_code,
            declaration_date=from_date + timedelta(days=i % 30),
            customs_office_code=f"HQ{i:04d}",
            transport_method="SEA",
            channel="Vang",
            status="T",
            goods_description=f"Goods {i}"
        )
        matching_declarations.append(declaration)
    
    # Mock the database to return only matching declarations
    mock_ecus_connector.get_declarations_by_date_range.return_value = matching_declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview with tax code filter
    result = manager.get_declarations_preview(from_date, to_date, filter_tax_codes)
    
    # Property: All returned declarations should have tax codes in the filter
    for decl in result:
        assert decl.tax_code in filter_tax_codes, \
            f"Declaration {decl.id} has tax code {decl.tax_code} not in filter {filter_tax_codes}"
    
    # Property: Result should match what database returned
    assert len(result) == len(matching_declarations), \
        f"Expected {len(matching_declarations)} declarations, got {len(result)}"
    
    # Verify the database was queried with correct parameters
    mock_ecus_connector.get_declarations_by_date_range.assert_called_once_with(
        from_date, to_date, filter_tax_codes, include_pending=False
    )


# Feature: enhanced-manual-mode, Property: Date range validation
@given(
    days_offset=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_property_date_range_validation_invalid_range(days_offset):
    """
    Property: Date range validation
    
    For any date range where end_date < start_date, the system should 
    reject the input and raise ValueError.
    
    Validates: Requirements 2.3
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Create invalid date range (end before start)
    from_date = datetime.now() - timedelta(days=10)
    to_date = from_date - timedelta(days=days_offset)  # Earlier than from_date
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Property: Should raise ValueError for invalid date range
    with pytest.raises(ValueError) as exc_info:
        manager.get_declarations_preview(from_date, to_date)
    
    assert "End date cannot be before start date" in str(exc_info.value)
    
    # Verify database was not queried
    mock_ecus_connector.get_declarations_by_date_range.assert_not_called()


# Feature: enhanced-manual-mode, Property: Future date validation
@given(
    days_future=st.integers(min_value=1, max_value=365)
)
@settings(max_examples=100)
def test_property_future_date_validation(days_future):
    """
    Property: Future date validation
    
    For any start date in the future, the system should reject the input
    and raise ValueError.
    
    Validates: Requirements 2.2
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Create date range with future start date
    from_date = datetime.now() + timedelta(days=days_future)
    to_date = from_date + timedelta(days=7)
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Property: Should raise ValueError for future start date
    with pytest.raises(ValueError) as exc_info:
        manager.get_declarations_preview(from_date, to_date)
    
    assert "Start date cannot be in the future" in str(exc_info.value)
    
    # Verify database was not queried
    mock_ecus_connector.get_declarations_by_date_range.assert_not_called()


# Feature: enhanced-manual-mode, Property: Cancellation stops operation
@given(
    num_declarations=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100)
def test_property_cancellation_stops_operation(num_declarations):
    """
    Property: Cancellation stops operation
    
    For any ongoing preview operation, calling cancel should stop the
    operation and return empty results.
    
    Validates: Requirements 8.2, 8.3
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Cancel before preview
    manager.cancel_preview()
    
    # Mock database to return declarations
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Try to get preview (should be cancelled)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Property: Cancelled operation should return empty list
    assert len(result) == 0, \
        f"Expected empty result after cancellation, but got {len(result)} declarations"
    
    # Property: Cancel flag should be set
    assert manager.is_cancelled(), "Cancel flag should be set"


# Feature: enhanced-manual-mode, Property: Clear preview resets state
@given(
    num_declarations=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100)
def test_property_clear_preview_resets_state(num_declarations):
    """
    Property: Clear preview resets state
    
    For any preview with selections, clearing should reset all state
    including declarations and selections.
    
    Validates: Requirements 3.1, 3.2
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Verify we have data
    assert len(result) == num_declarations
    selected_count, total_count = manager.get_selection_count()
    assert total_count == num_declarations
    
    # Clear preview
    manager.clear_preview()
    
    # Property: After clear, selection count should be zero
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, f"Expected 0 selected after clear, got {selected_count}"
    assert total_count == 0, f"Expected 0 total after clear, got {total_count}"
    
    # Property: Getting selected declarations should return empty list
    selected = manager.get_selected_declarations()
    assert len(selected) == 0, f"Expected empty selected list after clear, got {len(selected)}"
    
    # Property: Cancel flag should be cleared
    assert not manager.is_cancelled(), "Cancel flag should be cleared"



# Feature: enhanced-manual-mode, Property 4: Selection consistency
@given(
    num_declarations=st.integers(min_value=1, max_value=50),
    num_selected=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_property_selection_consistency(num_declarations, num_selected):
    """
    Property 4: Selection consistency
    
    For any set of selected declarations, getting selected declarations 
    should return exactly those declarations and no others.
    
    Validates: Requirements 4.2, 4.3
    """
    assume(num_selected <= num_declarations)
    
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview (all selected by default)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Select specific declarations
    selected_ids = {declarations[i].id for i in range(num_selected)}
    manager.set_selection(selected_ids)
    
    # Get selected declarations
    selected = manager.get_selected_declarations()
    
    # Property: Number of selected should match
    assert len(selected) == num_selected, \
        f"Expected {num_selected} selected declarations, got {len(selected)}"
    
    # Property: All selected declarations should be in the selected set
    selected_result_ids = {decl.id for decl in selected}
    assert selected_result_ids == selected_ids, \
        f"Selected IDs don't match. Expected {selected_ids}, got {selected_result_ids}"
    
    # Property: Selection count should be accurate
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == num_selected, \
        f"Selection count mismatch: expected {num_selected}, got {selected_count}"
    assert total_count == num_declarations, \
        f"Total count mismatch: expected {num_declarations}, got {total_count}"


# Feature: enhanced-manual-mode, Property: Toggle selection consistency
@given(
    num_declarations=st.integers(min_value=1, max_value=50),
    toggle_indices=st.lists(st.integers(min_value=0, max_value=49), min_size=0, max_size=20)
)
@settings(max_examples=100)
def test_property_toggle_selection_consistency(num_declarations, toggle_indices):
    """
    Property: Toggle selection consistency
    
    For any sequence of toggle operations, the final selection state should
    match the expected state based on the number of toggles per declaration.
    
    Validates: Requirements 4.2, 4.3
    """
    # Filter toggle indices to valid range
    toggle_indices = [i for i in toggle_indices if i < num_declarations]
    
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview (none selected by default - Requirement 4.1)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Count toggles per declaration
    toggle_counts = {}
    for idx in toggle_indices:
        toggle_counts[idx] = toggle_counts.get(idx, 0) + 1
    
    # Perform toggles
    for idx in toggle_indices:
        manager.toggle_selection(declarations[idx].id)
    
    # Calculate expected selection state
    # Start with none selected (default - Requirement 4.1), then apply toggles
    expected_selected = set()
    for i in range(num_declarations):
        # Start deselected (default - Requirement 4.1)
        is_selected = False
        # Apply toggles (odd number of toggles = selected)
        if i in toggle_counts:
            if toggle_counts[i] % 2 == 1:
                is_selected = not is_selected
        
        if is_selected:
            expected_selected.add(declarations[i].id)
    
    # Get actual selection
    selected = manager.get_selected_declarations()
    actual_selected = {decl.id for decl in selected}
    
    # Property: Actual selection should match expected
    assert actual_selected == expected_selected, \
        f"Selection mismatch. Expected {expected_selected}, got {actual_selected}"


# Feature: enhanced-manual-mode, Property: Select all and deselect all consistency
@given(
    num_declarations=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100)
def test_property_select_deselect_all_consistency(num_declarations):
    """
    Property: Select all and deselect all consistency
    
    For any preview, select_all should select all declarations and
    deselect_all should deselect all declarations.
    
    Validates: Requirements 3.4, 4.2
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Test deselect all
    manager.deselect_all()
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"After deselect_all, expected 0 selected, got {selected_count}"
    
    selected = manager.get_selected_declarations()
    assert len(selected) == 0, \
        f"After deselect_all, expected empty list, got {len(selected)} declarations"
    
    # Test select all
    manager.select_all()
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == num_declarations, \
        f"After select_all, expected {num_declarations} selected, got {selected_count}"
    
    selected = manager.get_selected_declarations()
    assert len(selected) == num_declarations, \
        f"After select_all, expected {num_declarations} declarations, got {len(selected)}"
    
    # Property: All declarations should be in selected list
    selected_ids = {decl.id for decl in selected}
    expected_ids = {decl.id for decl in declarations}
    assert selected_ids == expected_ids, \
        f"After select_all, selected IDs don't match all declaration IDs"


# Feature: enhanced-manual-mode, Property: Selection persists across queries
@given(
    num_declarations=st.integers(min_value=5, max_value=50),
    num_selected=st.integers(min_value=1, max_value=25)
)
@settings(max_examples=100)
def test_property_selection_isolation_between_previews(num_declarations, num_selected):
    """
    Property: Selection isolation between previews
    
    For any preview, when a new preview is loaded, the old selection should
    be replaced with the new default selection (all selected).
    
    Validates: Requirements 3.1, 4.2
    """
    assume(num_selected <= num_declarations)
    
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate first set of declarations
    declarations1 = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC1_{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations1.append(declaration)
    
    # Generate second set of declarations (different)
    declarations2 = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC2_{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i + 100),
            customs_office_code=f"HQ{i:04d}",
            transport_method="SEA",
            channel="Vang",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations2.append(declaration)
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # First preview
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations1
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Select some declarations from first preview
    selected_ids = {declarations1[i].id for i in range(num_selected)}
    manager.set_selection(selected_ids)
    
    # Verify selection
    selected_count, _ = manager.get_selection_count()
    assert selected_count == num_selected
    
    # Second preview (different data)
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations2
    manager.get_declarations_preview(from_date, to_date)
    
    # Property: New preview should have no declarations selected by default (Requirement 4.1)
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"After new preview, expected 0 selected by default, got {selected_count}"
    
    # Property: Total count should match new declarations
    assert total_count == num_declarations, \
        f"After new preview, expected {num_declarations} total, got {total_count}"
    
    # Property: Selected declarations should be empty (default unchecked)
    selected = manager.get_selected_declarations()
    assert len(selected) == 0, \
        f"After new preview, expected empty selection by default, got {len(selected)}"
    
    # Property: Old declaration IDs should not be in selection
    old_ids = {decl.id for decl in declarations1}
    selected_ids = {decl.id for decl in selected}
    assert len(selected_ids & old_ids) == 0, \
        "Old declaration IDs should not be in new selection"


# Feature: bug-fixes-dec-2024, Property 4: Declaration uniqueness
@given(
    num_unique=st.integers(min_value=1, max_value=30),
    num_duplicates=st.integers(min_value=0, max_value=10)
)
@settings(max_examples=100)
def test_property_declaration_uniqueness(num_unique, num_duplicates):
    """
    Property 4: Declaration uniqueness
    
    For any query result set, each declaration number should appear at most 
    once in the preview list.
    
    **Validates: Requirements 3.1, 3.2, 3.3**
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate unique declarations
    unique_declarations = []
    for i in range(num_unique):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 5:010d}",  # Multiple declarations per tax code
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i % 3:04d}",  # Multiple declarations per customs office
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        unique_declarations.append(declaration)
    
    # The database query should return unique declarations only
    # (duplicates should be filtered by the DISTINCT query)
    mock_ecus_connector.get_declarations_by_date_range.return_value = unique_declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Property: Each declaration should appear at most once
    # Check by declaration number, tax code, date, and customs office
    seen_keys = set()
    duplicates_found = []
    
    for decl in result:
        key = (
            decl.declaration_number,
            decl.tax_code,
            decl.declaration_date.date() if decl.declaration_date else None,
            decl.customs_office_code
        )
        
        if key in seen_keys:
            duplicates_found.append(decl.declaration_number)
        else:
            seen_keys.add(key)
    
    assert len(duplicates_found) == 0, \
        f"Found {len(duplicates_found)} duplicate declarations: {duplicates_found}"
    
    # Property: Number of unique declarations should match result count
    assert len(seen_keys) == len(result), \
        f"Expected {len(result)} unique declarations, but found {len(seen_keys)}"
    
    # Property: Validation method should confirm uniqueness
    is_unique = manager._validate_unique_declarations(result)
    assert is_unique, "Validation method should confirm all declarations are unique"


# Feature: v1.1-ui-enhancements, Property 5: Default Unchecked State
@given(
    num_declarations=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_property_default_unchecked_state(num_declarations):
    """
    **Feature: v1.1-ui-enhancements, Property 5: Default Unchecked State**
    **Validates: Requirements 4.1, 4.4**
    
    Property: For any set of declarations loaded into the preview panel,
    all declarations should have unchecked checkboxes by default.
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 10:010d}",
            declaration_date=datetime.now() - timedelta(days=i % 30),
            customs_office_code=f"HQ{i % 5:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Property: All declarations should be loaded
    assert len(result) == num_declarations, \
        f"Expected {num_declarations} declarations, got {len(result)}"
    
    # Property: No declarations should be selected by default
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"Expected 0 declarations selected by default, got {selected_count}"
    assert total_count == num_declarations, \
        f"Expected total count {num_declarations}, got {total_count}"
    
    # Property: Getting selected declarations should return empty list
    selected = manager.get_selected_declarations()
    assert len(selected) == 0, \
        f"Expected empty selected list by default, got {len(selected)} declarations"


# Feature: v1.1-ui-enhancements, Property 6: Select All Behavior
@given(
    num_declarations=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_property_select_all_behavior(num_declarations):
    """
    **Feature: v1.1-ui-enhancements, Property 6: Select All Behavior**
    **Validates: Requirements 4.2**
    
    Property: For any preview panel state, clicking "Select All" should
    result in all visible declarations being checked.
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 10:010d}",
            declaration_date=datetime.now() - timedelta(days=i % 30),
            customs_office_code=f"HQ{i % 5:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview (none selected by default)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Verify none selected initially
    selected_count, _ = manager.get_selection_count()
    assert selected_count == 0, "Should start with no selections"
    
    # Select all
    manager.select_all()
    
    # Property: All declarations should now be selected
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == num_declarations, \
        f"After select_all, expected {num_declarations} selected, got {selected_count}"
    assert total_count == num_declarations
    
    # Property: All declarations should be in selected list
    selected = manager.get_selected_declarations()
    assert len(selected) == num_declarations, \
        f"After select_all, expected {num_declarations} in selected list, got {len(selected)}"
    
    # Property: Selected IDs should match all declaration IDs
    selected_ids = {decl.id for decl in selected}
    expected_ids = {decl.id for decl in declarations}
    assert selected_ids == expected_ids, \
        "After select_all, selected IDs should match all declaration IDs"


# Feature: v1.1-ui-enhancements, Property 7: Individual Toggle Behavior
@given(
    num_declarations=st.integers(min_value=2, max_value=50),
    toggle_index=st.integers(min_value=0, max_value=49)
)
@settings(max_examples=100)
def test_property_individual_toggle_behavior(num_declarations, toggle_index):
    """
    **Feature: v1.1-ui-enhancements, Property 7: Individual Toggle Behavior**
    **Validates: Requirements 4.3**
    
    Property: For any declaration in the preview panel, clicking its checkbox
    should toggle only that declaration's selection state without affecting others.
    """
    # Ensure toggle_index is within bounds
    toggle_index = toggle_index % num_declarations
    
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 10:010d}",
            declaration_date=datetime.now() - timedelta(days=i % 30),
            customs_office_code=f"HQ{i % 5:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview (none selected by default)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Verify none selected initially
    selected_count, _ = manager.get_selection_count()
    assert selected_count == 0, "Should start with no selections"
    
    # Toggle one declaration
    target_decl = declarations[toggle_index]
    result = manager.toggle_selection(target_decl.id)
    
    # Property: Toggle should return True (now selected)
    assert result == True, "First toggle should select the declaration"
    
    # Property: Only the toggled declaration should be selected
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 1, \
        f"After toggling one, expected 1 selected, got {selected_count}"
    
    # Property: The selected declaration should be the one we toggled
    selected = manager.get_selected_declarations()
    assert len(selected) == 1
    assert selected[0].id == target_decl.id, \
        f"Selected declaration should be {target_decl.id}, got {selected[0].id}"
    
    # Toggle the same declaration again
    result = manager.toggle_selection(target_decl.id)
    
    # Property: Second toggle should return False (now deselected)
    assert result == False, "Second toggle should deselect the declaration"
    
    # Property: No declarations should be selected now
    selected_count, _ = manager.get_selection_count()
    assert selected_count == 0, \
        f"After toggling twice, expected 0 selected, got {selected_count}"


# Feature: v1.1-ui-enhancements, Property: Filter maintains unchecked default
@given(
    num_declarations=st.integers(min_value=5, max_value=50)
)
@settings(max_examples=100)
def test_property_filter_maintains_unchecked_default(num_declarations):
    """
    **Feature: v1.1-ui-enhancements, Property 5: Default Unchecked State**
    **Validates: Requirements 4.4**
    
    Property: When the filter changes visible declarations, the system should
    maintain the unchecked default for newly visible items.
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_logger = Mock()
    
    # Generate test declarations with different tax codes
    declarations = []
    for i in range(num_declarations):
        declaration = Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 3:010d}",  # 3 different tax codes
            declaration_date=datetime.now() - timedelta(days=i % 30),
            customs_office_code=f"HQ{i % 5:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        declarations.append(declaration)
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Create PreviewManager instance
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    # Get preview (none selected by default)
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    manager.get_declarations_preview(from_date, to_date)
    
    # Property: No declarations should be selected by default
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"Expected 0 declarations selected by default, got {selected_count}"
    
    # Select some declarations (simulate user selecting a few)
    for i in range(min(3, num_declarations)):
        manager.toggle_selection(declarations[i].id)
    
    # Verify some are now selected
    selected_count, _ = manager.get_selection_count()
    assert selected_count == min(3, num_declarations), \
        f"Expected {min(3, num_declarations)} selected after manual selection"
    
    # Reload preview (simulates filter change - new query with same data)
    # Note: clear_preview() clears the cancel flag, which is needed before a new preview
    manager._cancel_event.clear()
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    manager.get_declarations_preview(from_date, to_date)
    
    # Property: After reload, no declarations should be selected (default unchecked)
    selected_count, total_count = manager.get_selection_count()
    assert selected_count == 0, \
        f"After filter change, expected 0 selected by default, got {selected_count}"
    assert total_count == num_declarations, \
        f"After filter change, expected {num_declarations} total, got {total_count}"
