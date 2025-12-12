"""
Unit tests for PreviewManager

This module contains unit tests for the PreviewManager class.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from processors.preview_manager import PreviewManager, PreviewError
from database.ecus_connector import EcusDataConnector, DatabaseConnectionError
from models.declaration_models import Declaration


@pytest.fixture
def mock_ecus_connector():
    """Create a mock ECUS connector"""
    return Mock(spec=EcusDataConnector)


@pytest.fixture
def mock_logger():
    """Create a mock logger"""
    return Mock()


@pytest.fixture
def preview_manager(mock_ecus_connector, mock_logger):
    """Create a PreviewManager instance with mocked dependencies"""
    return PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )


@pytest.fixture
def sample_declarations():
    """Create sample declarations for testing"""
    declarations = []
    for i in range(5):
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
    return declarations


def test_preview_manager_initialization(mock_ecus_connector, mock_logger):
    """Test PreviewManager initialization"""
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    assert manager.ecus_connector == mock_ecus_connector
    assert manager.logger == mock_logger
    assert not manager.is_cancelled()


def test_get_declarations_preview_success(preview_manager, mock_ecus_connector, sample_declarations):
    """Test successful preview retrieval"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    
    result = preview_manager.get_declarations_preview(from_date, to_date)
    
    assert len(result) == len(sample_declarations)
    assert result == sample_declarations
    mock_ecus_connector.get_declarations_by_date_range.assert_called_once_with(
        from_date, to_date, None, include_pending=False
    )


def test_get_declarations_preview_with_tax_codes(preview_manager, mock_ecus_connector, sample_declarations):
    """Test preview retrieval with tax code filter"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    tax_codes = ["TC0000000000", "TC0000000001"]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    
    result = preview_manager.get_declarations_preview(from_date, to_date, tax_codes)
    
    assert len(result) == len(sample_declarations)
    mock_ecus_connector.get_declarations_by_date_range.assert_called_once_with(
        from_date, to_date, tax_codes, include_pending=False
    )


def test_get_declarations_preview_invalid_date_range(preview_manager, mock_ecus_connector):
    """Test preview with invalid date range (end before start)"""
    from_date = datetime.now()
    to_date = datetime.now() - timedelta(days=10)
    
    with pytest.raises(ValueError) as exc_info:
        preview_manager.get_declarations_preview(from_date, to_date)
    
    assert "End date cannot be before start date" in str(exc_info.value)
    mock_ecus_connector.get_declarations_by_date_range.assert_not_called()


def test_get_declarations_preview_future_start_date(preview_manager, mock_ecus_connector):
    """Test preview with future start date"""
    from_date = datetime.now() + timedelta(days=10)
    to_date = from_date + timedelta(days=7)
    
    with pytest.raises(ValueError) as exc_info:
        preview_manager.get_declarations_preview(from_date, to_date)
    
    assert "Start date cannot be in the future" in str(exc_info.value)
    mock_ecus_connector.get_declarations_by_date_range.assert_not_called()


def test_get_declarations_preview_database_error(preview_manager, mock_ecus_connector):
    """Test preview with database connection error"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.side_effect = DatabaseConnectionError("Connection failed")
    
    with pytest.raises(PreviewError) as exc_info:
        preview_manager.get_declarations_preview(from_date, to_date)
    
    assert "Database connection failed" in str(exc_info.value)


def test_get_selected_declarations(preview_manager, mock_ecus_connector, sample_declarations):
    """Test getting selected declarations"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # None should be selected by default (Requirement 4.1)
    selected = preview_manager.get_selected_declarations()
    assert len(selected) == 0
    
    # Select all to test getting selected declarations
    preview_manager.select_all()
    selected = preview_manager.get_selected_declarations()
    assert len(selected) == len(sample_declarations)


def test_set_selection(preview_manager, mock_ecus_connector, sample_declarations):
    """Test setting selection"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Select only first 3 declarations
    selected_ids = {sample_declarations[i].id for i in range(3)}
    preview_manager.set_selection(selected_ids)
    
    selected = preview_manager.get_selected_declarations()
    assert len(selected) == 3
    
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == 3
    assert total_count == 5


def test_select_all(preview_manager, mock_ecus_connector, sample_declarations):
    """Test select all functionality"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Deselect all first
    preview_manager.deselect_all()
    assert preview_manager.get_selection_count()[0] == 0
    
    # Select all
    preview_manager.select_all()
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == len(sample_declarations)
    assert total_count == len(sample_declarations)


def test_deselect_all(preview_manager, mock_ecus_connector, sample_declarations):
    """Test deselect all functionality"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Deselect all
    preview_manager.deselect_all()
    
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == len(sample_declarations)
    
    selected = preview_manager.get_selected_declarations()
    assert len(selected) == 0


def test_toggle_selection(preview_manager, mock_ecus_connector, sample_declarations):
    """Test toggle selection functionality"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # None selected by default (Requirement 4.1)
    selected_count, _ = preview_manager.get_selection_count()
    assert selected_count == 0
    
    # Toggle first declaration (should select it)
    result = preview_manager.toggle_selection(sample_declarations[0].id)
    assert result == True  # Now selected
    
    selected_count, _ = preview_manager.get_selection_count()
    assert selected_count == 1
    
    # Toggle again (should deselect it)
    result = preview_manager.toggle_selection(sample_declarations[0].id)
    assert result == False  # Now deselected
    
    selected_count, _ = preview_manager.get_selection_count()
    assert selected_count == 0


def test_cancel_preview(preview_manager, mock_ecus_connector, sample_declarations):
    """Test cancelling preview operation"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    # Cancel before preview
    preview_manager.cancel_preview()
    assert preview_manager.is_cancelled()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    
    # Try to get preview (should return empty due to cancellation)
    result = preview_manager.get_declarations_preview(from_date, to_date)
    assert len(result) == 0


def test_clear_preview(preview_manager, mock_ecus_connector, sample_declarations):
    """Test clearing preview data"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Verify we have data
    selected_count, total_count = preview_manager.get_selection_count()
    assert total_count == len(sample_declarations)
    
    # Clear preview
    preview_manager.clear_preview()
    
    # Verify data is cleared
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == 0
    assert not preview_manager.is_cancelled()


def test_get_selection_count_empty(preview_manager):
    """Test getting selection count when no preview loaded"""
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == 0


def test_progress_callback(preview_manager, mock_ecus_connector, sample_declarations):
    """Test progress callback functionality"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    
    # Track progress updates
    progress_updates = []
    
    def progress_callback(current, total, message):
        progress_updates.append((current, total, message))
    
    preview_manager.get_declarations_preview(from_date, to_date, progress_callback=progress_callback)
    
    # Verify progress callback was called
    assert len(progress_updates) > 0
    assert any("Đang truy vấn database" in msg for _, _, msg in progress_updates)
    assert any("Tìm thấy" in msg for _, _, msg in progress_updates)


def test_set_selection_with_invalid_ids(preview_manager, mock_ecus_connector, sample_declarations):
    """Test setting selection with IDs that don't exist in current preview"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = sample_declarations
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Try to select IDs that don't exist
    invalid_ids = {"INVALID_ID_1", "INVALID_ID_2"}
    preview_manager.set_selection(invalid_ids)
    
    # Should have no selections (invalid IDs filtered out)
    selected_count, _ = preview_manager.get_selection_count()
    assert selected_count == 0


def test_multiple_previews_reset_selection(preview_manager, mock_ecus_connector):
    """Test that loading a new preview resets selection"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    # First preview
    declarations1 = [
        Declaration(
            declaration_number=f"DEC1_{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(3)
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations1
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # Select some declarations
    preview_manager.set_selection({declarations1[0].id})
    assert preview_manager.get_selection_count()[0] == 1
    
    # Second preview with different declarations
    declarations2 = [
        Declaration(
            declaration_number=f"DEC2_{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i + 100),
            customs_office_code=f"HQ{i:04d}",
            transport_method="SEA",
            channel="Vang",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(5)
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations2
    preview_manager.get_declarations_preview(from_date, to_date)
    
    # New preview should have no declarations selected by default (Requirement 4.1)
    selected_count, total_count = preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == 5


def test_validate_unique_declarations_no_duplicates(preview_manager):
    """Test validation with unique declarations only"""
    declarations = [
        Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(5)
    ]
    
    # Should return True for unique declarations
    is_unique = preview_manager._validate_unique_declarations(declarations)
    assert is_unique == True


def test_validate_unique_declarations_with_duplicates(preview_manager):
    """Test validation detects duplicate declarations"""
    base_date = datetime.now() - timedelta(days=1)
    
    declarations = [
        Declaration(
            declaration_number="DEC000000000001",
            tax_code="TC0000000001",
            declaration_date=base_date,
            customs_office_code="HQ0001",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description="Goods 1"
        ),
        Declaration(
            declaration_number="DEC000000000002",
            tax_code="TC0000000002",
            declaration_date=base_date,
            customs_office_code="HQ0002",
            transport_method="SEA",
            channel="Vang",
            status="T",
            goods_description="Goods 2"
        ),
        # Duplicate of first declaration
        Declaration(
            declaration_number="DEC000000000001",
            tax_code="TC0000000001",
            declaration_date=base_date,
            customs_office_code="HQ0001",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description="Goods 1 duplicate"
        )
    ]
    
    # Should return False and log warning
    is_unique = preview_manager._validate_unique_declarations(declarations)
    assert is_unique == False


def test_validate_unique_declarations_empty_list(preview_manager):
    """Test validation with empty list"""
    declarations = []
    
    # Should return True for empty list
    is_unique = preview_manager._validate_unique_declarations(declarations)
    assert is_unique == True


def test_preview_calls_validation(preview_manager, mock_ecus_connector):
    """Test that preview calls duplicate validation"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    declarations = [
        Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(3)
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Get preview - should call validation internally
    result = preview_manager.get_declarations_preview(from_date, to_date)
    
    # Verify result is returned correctly
    assert len(result) == 3
    
    # Validation is called internally, we can verify by checking logs if logger is mocked
    # For now, just verify the preview works correctly


def test_database_query_returns_unique_declarations(mock_ecus_connector, mock_logger):
    """Test that database query is expected to return unique declarations"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    # Create declarations with potential duplicates
    # The database query should handle deduplication
    declarations = [
        Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i % 3:010d}",  # Some tax codes repeat
            declaration_date=datetime.now() - timedelta(days=i % 5),  # Some dates repeat
            customs_office_code=f"HQ{i % 2:04d}",  # Some customs offices repeat
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(10)
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    manager = PreviewManager(
        ecus_connector=mock_ecus_connector,
        logger=mock_logger
    )
    
    result = manager.get_declarations_preview(from_date, to_date)
    
    # Verify each declaration appears only once
    seen_keys = set()
    for decl in result:
        key = (
            decl.declaration_number,
            decl.tax_code,
            decl.declaration_date.date() if decl.declaration_date else None,
            decl.customs_office_code
        )
        assert key not in seen_keys, f"Duplicate declaration found: {decl.declaration_number}"
        seen_keys.add(key)


def test_counting_returns_correct_unique_count(preview_manager, mock_ecus_connector):
    """Test that counting returns correct count of unique declarations"""
    from_date = datetime.now() - timedelta(days=30)
    to_date = datetime.now()
    
    # Create unique declarations
    declarations = [
        Declaration(
            declaration_number=f"DEC{i:012d}",
            tax_code=f"TC{i:010d}",
            declaration_date=datetime.now() - timedelta(days=i),
            customs_office_code=f"HQ{i:04d}",
            transport_method="AIR",
            channel="Xanh",
            status="T",
            goods_description=f"Goods {i}"
        )
        for i in range(7)
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    result = preview_manager.get_declarations_preview(from_date, to_date)
    
    # Get counts
    selected_count, total_count = preview_manager.get_selection_count()
    
    # Verify counts match unique declarations
    assert total_count == 7, f"Expected 7 unique declarations, got {total_count}"
    assert selected_count == 0, f"Expected 0 selected by default (Requirement 4.1), got {selected_count}"
    assert len(result) == 7, f"Expected 7 declarations in result, got {len(result)}"
