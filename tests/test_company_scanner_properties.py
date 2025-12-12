"""
Property-based tests for CompanyScanner

This module contains property-based tests for the CompanyScanner class.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from processors.company_scanner import CompanyScanner, CompanyScanError
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase


# Feature: enhanced-manual-mode, Property 1: Company scan completeness
@given(
    days_back=st.integers(min_value=1, max_value=365),
    num_companies=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_property_company_scan_completeness(days_back, num_companies):
    """
    Property 1: Company scan completeness
    
    For any time period, scanning companies should return all unique tax codes 
    that have declarations in that period.
    
    Validates: Requirements 1.1
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Generate unique companies (tax_code, company_name)
    companies_in_db = []
    seen_tax_codes = set()
    
    for i in range(num_companies):
        # Generate unique tax codes
        tax_code = f"TC{i:010d}"
        company_name = f"Company {i}"
        
        # Ensure uniqueness
        if tax_code not in seen_tax_codes:
            companies_in_db.append((tax_code, company_name))
            seen_tax_codes.add(tax_code)
    
    # Mock the scan_all_companies method to return our test data
    mock_ecus_connector.scan_all_companies.return_value = companies_in_db
    
    # Create CompanyScanner instance
    scanner = CompanyScanner(
        ecus_connector=mock_ecus_connector,
        tracking_db=mock_tracking_db,
        logger=mock_logger
    )
    
    # Scan companies
    result = scanner.scan_companies(days_back=days_back)
    
    # Property: All unique tax codes from the database should be in the result
    result_tax_codes = {tax_code for tax_code, _ in result}
    expected_tax_codes = {tax_code for tax_code, _ in companies_in_db}
    
    # Verify completeness: all expected tax codes are present
    assert result_tax_codes == expected_tax_codes, \
        f"Expected {expected_tax_codes}, but got {result_tax_codes}"
    
    # Verify the scan was called with correct parameters
    mock_ecus_connector.scan_all_companies.assert_called_once_with(days_back)
    
    # Verify the result has the same length as input (no duplicates, no missing)
    assert len(result) == len(companies_in_db), \
        f"Expected {len(companies_in_db)} companies, but got {len(result)}"
    
    # Verify each company in result matches the input
    for tax_code, company_name in result:
        assert (tax_code, company_name) in companies_in_db, \
            f"Company ({tax_code}, {company_name}) not in original data"


# Feature: enhanced-manual-mode, Property: Save operation preserves all data
@given(
    num_companies=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_property_save_companies_preserves_data(num_companies):
    """
    Property: Save operation preserves all data
    
    For any list of companies, saving them to the database should preserve
    all company information without loss or corruption.
    
    Validates: Requirements 1.4
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Generate test companies
    companies = []
    for i in range(num_companies):
        tax_code = f"TC{i:010d}"
        company_name = f"Company {i}"
        companies.append((tax_code, company_name))
    
    # Track what was saved
    saved_companies = []
    
    def mock_add_or_update(tax_code, company_name):
        saved_companies.append((tax_code, company_name))
    
    mock_tracking_db.add_or_update_company.side_effect = mock_add_or_update
    
    # Create CompanyScanner instance
    scanner = CompanyScanner(
        ecus_connector=mock_ecus_connector,
        tracking_db=mock_tracking_db,
        logger=mock_logger
    )
    
    # Save companies
    saved_count = scanner.save_companies(companies)
    
    # Property: All companies should be saved
    assert saved_count == num_companies, \
        f"Expected to save {num_companies} companies, but saved {saved_count}"
    
    # Property: Saved data should match input data exactly
    assert len(saved_companies) == len(companies), \
        f"Expected {len(companies)} saved companies, but got {len(saved_companies)}"
    
    for original, saved in zip(companies, saved_companies):
        assert original == saved, \
            f"Company data mismatch: expected {original}, got {saved}"
    
    # Verify add_or_update_company was called for each company
    assert mock_tracking_db.add_or_update_company.call_count == num_companies


# Feature: enhanced-manual-mode, Property: Scan and save is idempotent
@given(
    days_back=st.integers(min_value=1, max_value=365),
    num_companies=st.integers(min_value=1, max_value=20)
)
@settings(max_examples=100)
def test_property_scan_and_save_idempotent(days_back, num_companies):
    """
    Property: Scan and save is idempotent
    
    For any time period, scanning and saving companies multiple times should
    produce the same result (same companies saved).
    
    Validates: Requirements 1.1, 1.4
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Generate test companies
    companies = []
    for i in range(num_companies):
        tax_code = f"TC{i:010d}"
        company_name = f"Company {i}"
        companies.append((tax_code, company_name))
    
    # Mock the scan to always return the same companies
    mock_ecus_connector.scan_all_companies.return_value = companies
    
    # Create CompanyScanner instance
    scanner = CompanyScanner(
        ecus_connector=mock_ecus_connector,
        tracking_db=mock_tracking_db,
        logger=mock_logger
    )
    
    # Scan and save companies first time
    saved_count_1, companies_1 = scanner.scan_and_save_companies(days_back)
    
    # Reset mocks
    mock_ecus_connector.scan_all_companies.reset_mock()
    mock_tracking_db.add_or_update_company.reset_mock()
    
    # Scan and save companies second time
    saved_count_2, companies_2 = scanner.scan_and_save_companies(days_back)
    
    # Property: Both operations should return the same results
    assert saved_count_1 == saved_count_2, \
        f"First scan saved {saved_count_1}, second scan saved {saved_count_2}"
    
    assert companies_1 == companies_2, \
        "Companies list should be identical across multiple scans"
    
    # Verify both scans called the database with same parameters
    assert mock_ecus_connector.scan_all_companies.call_count == 1


# Feature: enhanced-manual-mode, Property: Error handling preserves system state
@given(
    days_back=st.integers(min_value=1, max_value=365)
)
@settings(max_examples=100)
def test_property_error_handling_preserves_state(days_back):
    """
    Property: Error handling preserves system state
    
    For any database error during scanning, the system should raise an
    appropriate exception without corrupting state.
    
    Validates: Requirements 1.1, 7.4
    """
    # Create mock dependencies
    mock_ecus_connector = Mock(spec=EcusDataConnector)
    mock_tracking_db = Mock(spec=TrackingDatabase)
    mock_logger = Mock()
    
    # Mock the scan to raise an exception
    mock_ecus_connector.scan_all_companies.side_effect = Exception("Database error")
    
    # Create CompanyScanner instance
    scanner = CompanyScanner(
        ecus_connector=mock_ecus_connector,
        tracking_db=mock_tracking_db,
        logger=mock_logger
    )
    
    # Property: Scanning should raise CompanyScanError
    with pytest.raises(CompanyScanError) as exc_info:
        scanner.scan_companies(days_back=days_back)
    
    # Verify the error message is informative
    assert "Failed to scan companies" in str(exc_info.value)
    
    # Verify no data was saved to tracking database
    mock_tracking_db.add_or_update_company.assert_not_called()
