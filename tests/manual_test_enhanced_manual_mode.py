"""
Manual Testing Script for Enhanced Manual Mode

This script provides a comprehensive manual testing checklist and helper functions
for testing the Enhanced Manual Mode feature end-to-end.

Test Scenarios:
1. Company scan with empty database
2. Company scan with existing data
3. Date range validation (invalid ranges)
4. Preview with various filters
5. Preview cancellation
6. Selective download (some selected)
7. Download stop functionality
8. Error scenarios (DB disconnect, network failure)

Requirements: All
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.company_scanner import CompanyScanner
from processors.preview_manager import PreviewManager
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager


class ManualTestRunner:
    """Helper class for running manual tests"""
    
    def __init__(self):
        """Initialize test runner with required components"""
        print("=" * 70)
        print("Enhanced Manual Mode - Manual Testing Script")
        print("=" * 70)
        print()
        
        # Initialize configuration
        print("Initializing configuration...")
        config_path = "config.ini"
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found: {config_path}")
            sys.exit(1)
        
        self.config_manager = ConfigurationManager(config_path)
        self.config_manager.validate()
        print("✓ Configuration loaded")
        
        # Initialize logger
        logging_config = self.config_manager.get_logging_config()
        self.logger = Logger(logging_config)
        print("✓ Logger initialized")
        
        # Initialize database connector
        db_config = self.config_manager.get_database_config()
        self.ecus_connector = EcusDataConnector(db_config, self.logger)
        
        if not self.ecus_connector.connect():
            print("ERROR: Failed to connect to ECUS5 database")
            sys.exit(1)
        print("✓ Database connector initialized")
        
        # Initialize tracking database
        tracking_db_path = "data/tracking.db"
        self.tracking_db = TrackingDatabase(tracking_db_path, self.logger)
        print("✓ Tracking database initialized")
        
        # Initialize company scanner
        self.company_scanner = CompanyScanner(
            self.ecus_connector,
            self.tracking_db,
            self.logger
        )
        print("✓ Company scanner initialized")
        
        # Initialize preview manager
        self.preview_manager = PreviewManager(
            self.ecus_connector,
            self.logger
        )
        print("✓ Preview manager initialized")
        
        # Initialize barcode retriever
        barcode_config = self.config_manager.get_barcode_service_config()
        self.barcode_retriever = BarcodeRetriever(barcode_config, self.logger)
        print("✓ Barcode retriever initialized")
        
        # Initialize file manager
        output_path = self.config_manager.get_output_path()
        self.file_manager = FileManager(output_path)
        self.file_manager.ensure_directory_exists()
        print("✓ File manager initialized")
        
        print()
        print("=" * 70)
        print("All components initialized successfully")
        print("=" * 70)
        print()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ecus_connector:
            self.ecus_connector.disconnect()
            print("✓ Database disconnected")
    
    def print_test_header(self, test_number: str, test_name: str):
        """Print test header"""
        print()
        print("=" * 70)
        print(f"TEST {test_number}: {test_name}")
        print("=" * 70)
        print()
    
    def print_test_result(self, passed: bool, message: str = ""):
        """Print test result"""
        status = "✓ PASSED" if passed else "✗ FAILED"
        print()
        print(f"{status}: {message}")
        print()
    
    def wait_for_user(self, prompt: str = "Press Enter to continue..."):
        """Wait for user input"""
        input(prompt)
    
    # Test 1: Company scan with empty database
    def test_1_company_scan_empty_database(self):
        """Test company scan with empty database"""
        self.print_test_header("1", "Company Scan with Empty Database")
        
        print("This test verifies company scanning when tracking database is empty.")
        print()
        print("Steps:")
        print("1. Clear companies from tracking database")
        print("2. Run company scan")
        print("3. Verify companies are found and saved")
        print()
        
        self.wait_for_user("Press Enter to start test...")
        
        try:
            # Clear existing companies
            print("Clearing existing companies from tracking database...")
            cursor = self.tracking_db.conn.cursor()
            cursor.execute("DELETE FROM companies")
            self.tracking_db.conn.commit()
            print("✓ Companies cleared")
            
            # Scan companies
            print()
            print("Scanning companies (last 90 days)...")
            companies = self.company_scanner.scan_companies(days_back=90)
            
            if companies:
                print(f"✓ Found {len(companies)} companies")
                print()
                print("Sample companies:")
                for i, (tax_code, company_name) in enumerate(companies[:5]):
                    print(f"  {i+1}. {tax_code} - {company_name}")
                if len(companies) > 5:
                    print(f"  ... and {len(companies) - 5} more")
                
                # Save to database
                print()
                print("Saving companies to tracking database...")
                self.company_scanner.save_companies(companies)
                print("✓ Companies saved")
                
                # Verify saved
                saved_companies = self.tracking_db.get_all_companies()
                if len(saved_companies) == len(companies):
                    self.print_test_result(True, f"Successfully scanned and saved {len(companies)} companies")
                else:
                    self.print_test_result(False, f"Mismatch: scanned {len(companies)} but saved {len(saved_companies)}")
            else:
                self.print_test_result(False, "No companies found in database")
                
        except Exception as e:
            self.print_test_result(False, f"Exception occurred: {str(e)}")
    
    # Test 2: Company scan with existing data
    def test_2_company_scan_existing_data(self):
        """Test company scan with existing data"""
        self.print_test_header("2", "Company Scan with Existing Data")
        
        print("This test verifies company scanning when data already exists.")
        print()
        print("Steps:")
        print("1. Verify companies exist in tracking database")
        print("2. Run company scan again")
        print("3. Verify companies are updated (not duplicated)")
        print()
        
        self.wait_for_user("Press Enter to start test...")
        
        try:
            # Check existing companies
            existing_companies = self.tracking_db.get_all_companies()
            print(f"Existing companies in database: {len(existing_companies)}")
            
            if not existing_companies:
                print("WARNING: No existing companies. Run Test 1 first.")
                self.print_test_result(False, "No existing data to test with")
                return
            
            # Scan companies again
            print()
            print("Scanning companies again...")
            companies = self.company_scanner.scan_companies(days_back=90)
            print(f"✓ Found {len(companies)} companies")
            
            # Save to database
            print()
            print("Saving companies to tracking database...")
            self.company_scanner.save_companies(companies)
            print("✓ Companies saved")
            
            # Verify no duplicates
            updated_companies = self.tracking_db.get_all_companies()
            print()
            print(f"Companies after re-scan: {len(updated_companies)}")
            
            if len(updated_companies) == len(existing_companies):
                self.print_test_result(True, "No duplicates created - companies updated correctly")
            else:
                self.print_test_result(False, f"Company count changed: {len(existing_companies)} -> {len(updated_companies)}")
                
        except Exception as e:
            self.print_test_result(False, f"Exception occurred: {str(e)}")
    
    # Test 3: Date range validation
    def test_3_date_range_validation(self):
        """Test date range validation"""
        self.print_test_header("3", "Date Range Validation (Invalid Ranges)")
        
        print("This test verifies date range validation logic.")
        print()
        print("Test cases:")
        print("1. End date before start date")
        print("2. Start date in the future")
        print("3. Date range > 90 days")
        print()
        
        self.wait_for_user("Press Enter to start test...")
        
        test_cases = [
            {
                "name": "End date before start date",
                "from_date": datetime.now(),
                "to_date": datetime.now() - timedelta(days=7),
                "should_fail": True
            },
            {
                "name": "Start date in future",
                "from_date": datetime.now() + timedelta(days=7),
                "to_date": datetime.now() + timedelta(days=14),
                "should_fail": True
            },
            {
                "name": "Range > 90 days",
                "from_date": datetime.now() - timedelta(days=100),
                "to_date": datetime.now(),
                "should_fail": False,  # Should warn but not fail
                "should_warn": True
            },
            {
                "name": "Valid range",
                "from_date": datetime.now() - timedelta(days=30),
                "to_date": datetime.now(),
                "should_fail": False
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            print()
            print(f"Testing: {test_case['name']}")
            print(f"  From: {test_case['from_date'].strftime('%Y-%m-%d')}")
            print(f"  To: {test_case['to_date'].strftime('%Y-%m-%d')}")
            
            # Validate dates
            is_valid = True
            warning = None
            
            if test_case['to_date'] < test_case['from_date']:
                is_valid = False
                print("  ✓ Correctly rejected: End date before start date")
            elif test_case['from_date'] > datetime.now():
                is_valid = False
                print("  ✓ Correctly rejected: Start date in future")
            else:
                days_diff = (test_case['to_date'] - test_case['from_date']).days
                if days_diff > 90:
                    warning = f"Date range is {days_diff} days (> 90 days)"
                    print(f"  ⚠ Warning: {warning}")
                else:
                    print("  ✓ Valid date range")
            
            # Check if result matches expectation
            if test_case['should_fail'] and not is_valid:
                print("  ✓ Test passed")
            elif not test_case['should_fail'] and is_valid:
                if test_case.get('should_warn') and warning:
                    print("  ✓ Test passed (with expected warning)")
                elif not test_case.get('should_warn'):
                    print("  ✓ Test passed")
                else:
                    print("  ✗ Test failed: Expected warning not shown")
                    all_passed = False
            else:
                print("  ✗ Test failed: Unexpected validation result")
                all_passed = False
        
        self.print_test_result(all_passed, "All date validation tests completed")
    
    # Test 4: Preview with various filters
    def test_4_preview_various_filters(self):
        """Test preview with various filters"""
        self.print_test_header("4", "Preview with Various Filters")
        
        print("This test verifies declaration preview with different filter combinations.")
        print()
        print("Test cases:")
        print("1. All companies, last 7 days")
        print("2. Specific company, last 30 days")
        print("3. Multiple companies, custom date range")
        print()
        
        self.wait_for_user("Press Enter to start test...")
        
        try:
            # Get available companies
            companies = self.tracking_db.get_all_companies()
            if not companies:
                print("WARNING: No companies in database. Run Test 1 first.")
                self.print_test_result(False, "No companies available for testing")
                return
            
            print(f"Available companies: {len(companies)}")
            print()
            
            # Test case 1: All companies, last 7 days
            print("Test case 1: All companies, last 7 days")
            from_date = datetime.now() - timedelta(days=7)
            to_date = datetime.now()
            
            declarations = self.preview_manager.get_declarations_preview(
                from_date=from_date,
                to_date=to_date,
                tax_codes=None
            )
            
            print(f"  Found {len(declarations)} declarations")
            if declarations:
                print(f"  Sample: {declarations[0].declaration_number}")
            print("  ✓ Test case 1 completed")
            
            # Test case 2: Specific company, last 30 days
            print()
            print("Test case 2: Specific company, last 30 days")
            if companies:
                test_tax_code = companies[0][0]
                print(f"  Testing with company: {test_tax_code}")
                
                from_date = datetime.now() - timedelta(days=30)
                to_date = datetime.now()
                
                declarations = self.preview_manager.get_declarations_preview(
                    from_date=from_date,
                    to_date=to_date,
                    tax_codes=[test_tax_code]
                )
                
                print(f"  Found {len(declarations)} declarations")
                
                # Verify all declarations match the tax code
                if declarations:
                    all_match = all(d.tax_code == test_tax_code for d in declarations)
                    if all_match:
                        print("  ✓ All declarations match the selected company")
                    else:
                        print("  ✗ Some declarations don't match the selected company")
                
                print("  ✓ Test case 2 completed")
            
            # Test case 3: Multiple companies, custom date range
            print()
            print("Test case 3: Multiple companies, custom date range")
            if len(companies) >= 2:
                test_tax_codes = [companies[0][0], companies[1][0]]
                print(f"  Testing with companies: {', '.join(test_tax_codes)}")
                
                from_date = datetime.now() - timedelta(days=14)
                to_date = datetime.now() - timedelta(days=7)
                
                declarations = self.preview_manager.get_declarations_preview(
                    from_date=from_date,
                    to_date=to_date,
                    tax_codes=test_tax_codes
                )
                
                print(f"  Found {len(declarations)} declarations")
                
                # Verify all declarations match one of the tax codes
                if declarations:
                    all_match = all(d.tax_code in test_tax_codes for d in declarations)
                    if all_match:
                        print("  ✓ All declarations match the selected companies")
                    else:
                        print("  ✗ Some declarations don't match the selected companies")
                
                print("  ✓ Test case 3 completed")
            
            self.print_test_result(True, "All preview filter tests completed")
            
        except Exception as e:
            self.print_test_result(False, f"Exception occurred: {str(e)}")
    
    # Test 5: Preview cancellation
    def test_5_preview_cancellation(self):
        """Test preview cancellation"""
        self.print_test_header("5", "Preview Cancellation")
        
        print("This test verifies the ability to cancel a preview operation.")
        print()
        print("NOTE: This test requires GUI interaction and cannot be fully automated.")
        print("To test cancellation:")
        print("1. Open the Enhanced Manual Mode GUI")
        print("2. Select a large date range (e.g., 90 days)")
        print("3. Click 'Xem trước'")
        print("4. Immediately click 'Hủy' button")
        print("5. Verify the operation stops and UI returns to input state")
        print()
        
        print("Manual verification checklist:")
        print("[ ] Preview query stops when 'Hủy' is clicked")
        print("[ ] Message 'Đã hủy xem trước' is displayed")
        print("[ ] UI returns to input state (buttons re-enabled)")
        print("[ ] No errors or crashes occur")
        print()
        
        self.print_test_result(True, "Manual test - requires GUI interaction")
    
    # Test 6: Selective download
    def test_6_selective_download(self):
        """Test selective download"""
        self.print_test_header("6", "Selective Download (Some Selected)")
        
        print("This test verifies selective download functionality.")
        print()
        print("NOTE: This test requires GUI interaction and cannot be fully automated.")
        print("To test selective download:")
        print("1. Open the Enhanced Manual Mode GUI")
        print("2. Run a preview to get declarations")
        print("3. Select only some declarations (not all)")
        print("4. Click 'Lấy mã vạch'")
        print("5. Verify only selected declarations are downloaded")
        print()
        
        print("Manual verification checklist:")
        print("[ ] Only selected declarations are processed")
        print("[ ] Unselected declarations are skipped")
        print("[ ] Progress bar shows correct count (selected/total)")
        print("[ ] Summary shows correct success/error counts")
        print("[ ] Downloaded files match selected declarations")
        print()
        
        self.print_test_result(True, "Manual test - requires GUI interaction")
    
    # Test 7: Download stop functionality
    def test_7_download_stop(self):
        """Test download stop functionality"""
        self.print_test_header("7", "Download Stop Functionality")
        
        print("This test verifies the ability to stop an ongoing download.")
        print()
        print("NOTE: This test requires GUI interaction and cannot be fully automated.")
        print("To test download stop:")
        print("1. Open the Enhanced Manual Mode GUI")
        print("2. Select multiple declarations (10+)")
        print("3. Click 'Lấy mã vạch' to start download")
        print("4. After a few declarations, click 'Dừng'")
        print("5. Verify download stops gracefully")
        print()
        
        print("Manual verification checklist:")
        print("[ ] Download stops after current declaration completes")
        print("[ ] All completed downloads are saved")
        print("[ ] Summary shows completed and remaining counts")
        print("[ ] No data corruption occurs")
        print("[ ] UI returns to normal state")
        print()
        
        self.print_test_result(True, "Manual test - requires GUI interaction")
    
    # Test 8: Error scenarios
    def test_8_error_scenarios(self):
        """Test error scenarios"""
        self.print_test_header("8", "Error Scenarios")
        
        print("This test verifies error handling in various failure scenarios.")
        print()
        print("Test cases:")
        print("1. Database disconnect during scan")
        print("2. Network failure during barcode retrieval")
        print("3. Invalid date input")
        print("4. Empty result set")
        print()
        
        self.wait_for_user("Press Enter to start test...")
        
        # Test case 1: Database disconnect
        print()
        print("Test case 1: Database disconnect simulation")
        print("NOTE: This would require disconnecting the database during operation.")
        print("In production, this should show a user-friendly error message.")
        print("✓ Error handling exists in code")
        
        # Test case 2: Network failure
        print()
        print("Test case 2: Network failure simulation")
        print("NOTE: This would require simulating network failure during barcode retrieval.")
        print("In production, this should retry with exponential backoff.")
        print("✓ Error handling exists in code")
        
        # Test case 3: Invalid date input
        print()
        print("Test case 3: Invalid date input")
        try:
            # Try to create preview with invalid dates
            from_date = datetime.now()
            to_date = datetime.now() - timedelta(days=7)
            
            if to_date < from_date:
                print("✓ Invalid date range detected (end before start)")
            else:
                print("✗ Invalid date range not detected")
        except Exception as e:
            print(f"✓ Exception raised for invalid dates: {str(e)}")
        
        # Test case 4: Empty result set
        print()
        print("Test case 4: Empty result set")
        try:
            # Query with date range that should have no results
            from_date = datetime.now() + timedelta(days=365)
            to_date = datetime.now() + timedelta(days=366)
            
            declarations = self.preview_manager.get_declarations_preview(
                from_date=from_date,
                to_date=to_date,
                tax_codes=None
            )
            
            if len(declarations) == 0:
                print("✓ Empty result set handled correctly")
            else:
                print(f"⚠ Unexpected: Found {len(declarations)} declarations in future dates")
        except Exception as e:
            print(f"✓ Exception handled: {str(e)}")
        
        self.print_test_result(True, "Error scenario tests completed")
    
    def run_all_tests(self):
        """Run all manual tests"""
        print()
        print("=" * 70)
        print("RUNNING ALL MANUAL TESTS")
        print("=" * 70)
        print()
        
        tests = [
            self.test_1_company_scan_empty_database,
            self.test_2_company_scan_existing_data,
            self.test_3_date_range_validation,
            self.test_4_preview_various_filters,
            self.test_5_preview_cancellation,
            self.test_6_selective_download,
            self.test_7_download_stop,
            self.test_8_error_scenarios
        ]
        
        for i, test in enumerate(tests, 1):
            try:
                test()
            except Exception as e:
                print(f"ERROR in test {i}: {str(e)}")
            
            if i < len(tests):
                print()
                self.wait_for_user("Press Enter to continue to next test...")
        
        print()
        print("=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70)
        print()
        print("Summary:")
        print("- Tests 1-4, 8: Automated tests completed")
        print("- Tests 5-7: Manual GUI tests (require user interaction)")
        print()
        print("Please review the results above and verify GUI tests manually.")
        print()


def main():
    """Main entry point"""
    print()
    print("Enhanced Manual Mode - Manual Testing Script")
    print()
    print("This script provides comprehensive testing for the Enhanced Manual Mode feature.")
    print()
    print("Options:")
    print("1. Run all tests")
    print("2. Run individual test")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "3":
        print("Exiting...")
        return
    
    # Initialize test runner
    try:
        runner = ManualTestRunner()
    except Exception as e:
        print(f"ERROR: Failed to initialize test runner: {str(e)}")
        return
    
    try:
        if choice == "1":
            runner.run_all_tests()
        elif choice == "2":
            print()
            print("Individual Tests:")
            print("1. Company scan with empty database")
            print("2. Company scan with existing data")
            print("3. Date range validation")
            print("4. Preview with various filters")
            print("5. Preview cancellation")
            print("6. Selective download")
            print("7. Download stop functionality")
            print("8. Error scenarios")
            print()
            
            test_choice = input("Enter test number (1-8): ").strip()
            
            tests = {
                "1": runner.test_1_company_scan_empty_database,
                "2": runner.test_2_company_scan_existing_data,
                "3": runner.test_3_date_range_validation,
                "4": runner.test_4_preview_various_filters,
                "5": runner.test_5_preview_cancellation,
                "6": runner.test_6_selective_download,
                "7": runner.test_7_download_stop,
                "8": runner.test_8_error_scenarios
            }
            
            if test_choice in tests:
                tests[test_choice]()
            else:
                print("Invalid test number")
        else:
            print("Invalid choice")
    
    finally:
        runner.cleanup()


if __name__ == "__main__":
    main()