"""
Integration tests for preview workflow

Tests the complete preview workflow including:
- Preview declarations handler
- Cancel preview handler  
- Checkbox selection logic
"""

import pytest
import tkinter as tk
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from gui.enhanced_manual_panel import EnhancedManualPanel
from processors.company_scanner import CompanyScanner
from processors.preview_manager import PreviewManager
from models.declaration_models import Declaration


@pytest.fixture
def mock_ecus_connector():
    """Create mock ECUS connector"""
    connector = Mock()
    return connector


@pytest.fixture
def mock_tracking_db():
    """Create mock tracking database"""
    db = Mock()
    return db


@pytest.fixture
def company_scanner(mock_ecus_connector, mock_tracking_db):
    """Create CompanyScanner instance"""
    return CompanyScanner(mock_ecus_connector, mock_tracking_db)


@pytest.fixture
def preview_manager(mock_ecus_connector):
    """Create PreviewManager instance"""
    return PreviewManager(mock_ecus_connector)


@pytest.fixture
def root():
    """Create Tkinter root window"""
    root = tk.Tk()
    yield root
    root.destroy()


@pytest.fixture
def panel(root, company_scanner, preview_manager):
    """Create EnhancedManualPanel instance"""
    return EnhancedManualPanel(
        root,
        company_scanner,
        preview_manager
    )


def test_preview_workflow_complete(panel, mock_ecus_connector):
    """Test complete preview workflow from start to finish"""
    # Setup mock data
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    declarations = [
        Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=yesterday,
            customs_office_code="1801",
            transport_method="4",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        ),
        Declaration(
            declaration_number="123457",
            tax_code="0123456789",
            declaration_date=today,
            customs_office_code="1801",
            transport_method="4",
            channel="Xanh",
            status="T",
            goods_description="Test goods 2"
        )
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Set date range
    panel.from_date_var.set(yesterday.strftime("%d/%m/%Y"))
    panel.to_date_var.set(today.strftime("%d/%m/%Y"))
    
    # Trigger preview (simulate button click)
    # We need to wait for the thread to complete, so we'll call the internal logic directly
    from_date = panel._parse_date(panel.from_date_var.get())
    to_date = panel._parse_date(panel.to_date_var.get())
    
    # Get preview
    result = panel.preview_manager.get_declarations_preview(from_date, to_date)
    
    # Verify results
    assert len(result) == 2
    assert result[0].declaration_number == "123456"
    assert result[1].declaration_number == "123457"
    
    # Verify none are selected by default (Requirement 4.1)
    selected_count, total_count = panel.preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == 2


def test_cancel_preview_workflow(panel, mock_ecus_connector):
    """Test cancelling preview operation"""
    # Setup mock to simulate slow query
    def slow_query(*args, **kwargs):
        import time
        time.sleep(0.1)
        return []
    
    mock_ecus_connector.get_declarations_by_date_range.side_effect = slow_query
    
    # Start preview
    panel.preview_manager.clear_preview()
    
    # Cancel immediately
    panel.preview_manager.cancel_preview()
    
    # Verify cancel flag is set
    assert panel.preview_manager.is_cancelled()


def test_checkbox_selection_workflow(panel, mock_ecus_connector):
    """Test checkbox selection logic"""
    # Setup mock data
    today = datetime.now()
    
    declarations = [
        Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=today,
            customs_office_code="1801",
            transport_method="4",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        ),
        Declaration(
            declaration_number="123457",
            tax_code="0123456789",
            declaration_date=today,
            customs_office_code="1801",
            transport_method="4",
            channel="Xanh",
            status="T",
            goods_description="Test goods 2"
        )
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Get preview
    from_date = today - timedelta(days=1)
    to_date = today
    panel.preview_manager.get_declarations_preview(from_date, to_date)
    
    # Verify none selected by default (Requirement 4.1)
    selected_count, total_count = panel.preview_manager.get_selection_count()
    assert selected_count == 0
    assert total_count == 2
    
    # Select one
    decl_id = declarations[0].id
    panel.preview_manager.toggle_selection(decl_id)
    selected_count, total_count = panel.preview_manager.get_selection_count()
    assert selected_count == 1
    assert total_count == 2
    
    # Select all
    panel.preview_manager.select_all()
    selected_count, total_count = panel.preview_manager.get_selection_count()
    assert selected_count == 2
    assert total_count == 2
    
    # Get selected declarations
    selected = panel.preview_manager.get_selected_declarations()
    assert len(selected) == 2


def test_get_declaration_id_by_number(panel, mock_ecus_connector):
    """Test helper method to get declaration ID by number"""
    # Setup mock data
    today = datetime.now()
    
    declarations = [
        Declaration(
            declaration_number="123456",
            tax_code="0123456789",
            declaration_date=today,
            customs_office_code="1801",
            transport_method="4",
            channel="Xanh",
            status="T",
            goods_description="Test goods"
        )
    ]
    
    mock_ecus_connector.get_declarations_by_date_range.return_value = declarations
    
    # Get preview
    from_date = today - timedelta(days=1)
    to_date = today
    panel.preview_manager.get_declarations_preview(from_date, to_date)
    
    # Test getting ID by number
    decl_id = panel._get_declaration_id_by_number("123456")
    assert decl_id is not None
    assert decl_id == declarations[0].id
    
    # Test with non-existent number
    decl_id = panel._get_declaration_id_by_number("999999")
    assert decl_id is None


def test_date_validation_in_preview(panel):
    """Test date validation before preview"""
    # Test future start date
    future_date = datetime.now() + timedelta(days=1)
    today = datetime.now()
    
    error = panel._validate_date_range(future_date, today)
    assert error is not None
    assert "tương lai" in error.lower()
    
    # Test end before start
    yesterday = today - timedelta(days=1)
    error = panel._validate_date_range(today, yesterday)
    assert error is not None
    assert "trước" in error.lower()
    
    # Test valid range
    error = panel._validate_date_range(yesterday, today)
    assert error is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
