"""
Unit tests for CompanyScanner

This module contains unit tests for the CompanyScanner class.
"""

import pytest
from unittest.mock import Mock, MagicMock
from processors.company_scanner import CompanyScanner, CompanyScanError
from database.ecus_connector import EcusDataConnector, DatabaseConnectionError
from database.tracking_database import TrackingDatabase


def test_scan_companies_success():
    """Test successful company scanning"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock data
    test_companies = [
        ("0700809357", "Công ty ABC"),
        ("0123456789", "Công ty XYZ"),
        ("9876543210", "Công ty 123")
    ]
    mock_ecus_connector.scan_all_companies.return_value = test_companies
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Scan companies
    result = scanner.scan_companies(days_back=90)
    
    # Verify
    assert result == test_companies
    mock_ecus_connector.scan_all_companies.assert_called_once_with(90)


def test_scan_companies_with_progress_callback():
    """Test company scanning with progress callback"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock data
    test_companies = [("0700809357", "Công ty ABC")]
    mock_ecus_connector.scan_all_companies.return_value = test_companies
    
    # Create progress callback mock
    progress_callback = Mock()
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Scan companies with callback
    result = scanner.scan_companies(days_back=30, progress_callback=progress_callback)
    
    # Verify callback was called
    assert progress_callback.call_count >= 2  # At least start and end
    assert result == test_companies


def test_scan_companies_database_error():
    """Test company scanning with database error"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock database error
    mock_ecus_connector.scan_all_companies.side_effect = DatabaseConnectionError("Connection failed")
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Verify exception is raised
    with pytest.raises(CompanyScanError) as exc_info:
        scanner.scan_companies(days_back=90)
    
    assert "Database connection failed" in str(exc_info.value)


def test_save_companies_success():
    """Test successful company saving"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Test data
    companies = [
        ("0700809357", "Công ty ABC"),
        ("0123456789", "Công ty XYZ")
    ]
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Save companies
    saved_count = scanner.save_companies(companies)
    
    # Verify
    assert saved_count == 2
    assert mock_tracking_db.add_or_update_company.call_count == 2


def test_save_companies_with_progress_callback():
    """Test company saving with progress callback"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Test data
    companies = [("0700809357", "Công ty ABC")]
    
    # Create progress callback mock
    progress_callback = Mock()
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Save companies with callback
    saved_count = scanner.save_companies(companies, progress_callback=progress_callback)
    
    # Verify
    assert saved_count == 1
    assert progress_callback.call_count >= 1


def test_save_companies_partial_failure():
    """Test company saving with partial failures"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Test data
    companies = [
        ("0700809357", "Công ty ABC"),
        ("0123456789", "Công ty XYZ"),
        ("9876543210", "Công ty 123")
    ]
    
    # Mock to fail on second company
    call_count = 0
    def mock_add_or_update(tax_code, company_name):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise Exception("Database error")
    
    mock_tracking_db.add_or_update_company.side_effect = mock_add_or_update
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Save companies (should continue despite one failure)
    saved_count = scanner.save_companies(companies)
    
    # Verify - should save 2 out of 3
    assert saved_count == 2
    assert mock_tracking_db.add_or_update_company.call_count == 3


def test_scan_and_save_companies_success():
    """Test combined scan and save operation"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock data
    test_companies = [
        ("0700809357", "Công ty ABC"),
        ("0123456789", "Công ty XYZ")
    ]
    mock_ecus_connector.scan_all_companies.return_value = test_companies
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Scan and save
    saved_count, companies = scanner.scan_and_save_companies(days_back=60)
    
    # Verify
    assert saved_count == 2
    assert companies == test_companies
    mock_ecus_connector.scan_all_companies.assert_called_once_with(60)
    assert mock_tracking_db.add_or_update_company.call_count == 2


def test_load_companies_success():
    """Test loading companies from tracking database"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock data - get_all_companies returns (tax_code, company_name, last_seen)
    mock_tracking_db.get_all_companies.return_value = [
        ("0700809357", "Công ty ABC", "2024-12-01"),
        ("0123456789", "Công ty XYZ", "2024-12-02")
    ]
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Load companies
    companies = scanner.load_companies()
    
    # Verify - should return only (tax_code, company_name) tuples
    expected = [
        ("0700809357", "Công ty ABC"),
        ("0123456789", "Công ty XYZ")
    ]
    assert companies == expected
    mock_tracking_db.get_all_companies.assert_called_once()


def test_load_companies_empty_database():
    """Test loading companies from empty database"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock empty database
    mock_tracking_db.get_all_companies.return_value = []
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Load companies
    companies = scanner.load_companies()
    
    # Verify
    assert companies == []


def test_load_companies_database_error():
    """Test loading companies with database error"""
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock database error
    mock_tracking_db.get_all_companies.side_effect = Exception("Database error")
    
    # Create scanner
    scanner = CompanyScanner(mock_ecus_connector, mock_tracking_db, mock_logger)
    
    # Verify exception is raised
    with pytest.raises(CompanyScanError) as exc_info:
        scanner.load_companies()
    
    assert "Failed to load companies" in str(exc_info.value)
