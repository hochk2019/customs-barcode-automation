# Implementation Plan - Enhanced Manual Mode

- [x] 1. Extend database layer with new methods





  - Add methods to support date range queries and company scanning
  - _Requirements: 1.1, 1.2, 2.1, 3.1_


- [x] 1.1 Verify database methods already added

  - Confirm `scan_all_companies()` exists in EcusConnector
  - Confirm `get_declarations_by_date_range()` exists in EcusConnector
  - Confirm company methods exist in TrackingDatabase
  - _Requirements: 1.1, 2.1_

- [x] 2. Create CompanyScanner business logic





  - Implement company scanning and saving logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.1 Implement CompanyScanner class


  - Create `scan_companies()` method to call database
  - Create `save_companies()` method to persist to tracking DB
  - Add progress callback support
  - Handle errors gracefully
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.2 Write property test for company scan completeness


  - **Property 1: Company scan completeness**
  - **Validates: Requirements 1.1**

- [x] 3. Create PreviewManager business logic





  - Implement declaration preview and selection logic
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3_

- [x] 3.1 Implement PreviewManager class


  - Create `get_declarations_preview()` method
  - Create `get_selected_declarations()` method
  - Add selection tracking
  - Support cancellation
  - _Requirements: 3.1, 3.2, 4.1, 4.2_

- [x] 3.2 Write property test for preview accuracy


  - **Property 3: Preview accuracy**
  - **Validates: Requirements 3.1, 3.2**

- [x] 3.3 Write property test for selection consistency


  - **Property 4: Selection consistency**
  - **Validates: Requirements 4.2, 4.3**

- [x] 4. Create EnhancedManualPanel GUI component





  - Build the complete UI for enhanced manual mode
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.2, 3.3, 3.4, 3.5, 6.1, 6.2, 6.3, 6.4, 6.5_


- [x] 4.1 Create basic panel layout

  - Add "Quét công ty" and "Làm mới" buttons
  - Add company dropdown (Combobox)
  - Add date pickers for from/to dates
  - Add "Xem trước" and "Lấy mã vạch" buttons
  - _Requirements: 2.1, 6.1, 6.2_

- [x] 4.2 Implement date range picker with validation


  - Add DateEntry widgets (or Entry with date format)
  - Validate start date not in future
  - Validate end date not before start date
  - Display warning if range > 90 days
  - _Requirements: 2.2, 2.3, 2.4, 2.5_

- [x] 4.3 Write property test for date range validation


  - **Property 2: Date range validation**
  - **Validates: Requirements 2.3**

- [x] 4.4 Create declaration preview table


  - Add Treeview with columns: checkbox, declaration number, tax code, date
  - Add "Chọn tất cả" checkbox
  - Implement checkbox selection logic
  - Display "Đã chọn: X/Y tờ khai" counter
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [x] 4.5 Implement workflow state management


  - State 1: Initial (only scan button enabled)
  - State 2: Companies loaded (enable dropdown and dates)
  - State 3: Preview displayed (enable download button)
  - State 4: Downloading (disable inputs, show stop button)
  - State 5: Complete (re-enable all)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 5. Implement company scanning workflow





  - Connect UI to CompanyScanner logic
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.1 Implement scan_companies() handler


  - Run scan in background thread
  - Display progress indicator
  - Update company dropdown on completion
  - Show count of companies found
  - Handle errors with user-friendly messages
  - _Requirements: 1.1, 1.4, 1.5, 7.1, 7.2, 7.3, 7.4_

- [x] 5.2 Implement load_companies() on startup


  - Load saved companies from tracking DB
  - Populate dropdown
  - Handle empty database case
  - _Requirements: 5.2, 5.5_

- [x] 5.3 Implement refresh_companies() handler


  - Reload companies from database
  - Update dropdown
  - _Requirements: 5.4_

- [x] 6. Implement preview workflow





  - Connect UI to PreviewManager logic
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6.1 Implement preview_declarations() handler


  - Get selected company and date range
  - Run query in background thread
  - Display "Hủy" button during query
  - Populate preview table with results
  - Handle zero results case
  - _Requirements: 3.1, 3.2, 8.1, 8.4, 8.5_

- [x] 6.2 Implement cancel_preview() handler


  - Stop ongoing query
  - Return to input state
  - Display cancellation message
  - _Requirements: 8.2, 8.3_

- [x] 6.3 Implement checkbox selection logic


  - Handle individual checkbox clicks
  - Handle "Chọn tất cả" checkbox
  - Update selection counter
  - Enable/disable download button based on selection
  - _Requirements: 3.3, 3.4, 3.5, 6.4_

- [x] 7. Implement selective download workflow





  - Connect UI to download logic with selection support
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 7.1 Implement download_selected() handler


  - Get selected declarations from preview
  - Run download in background thread
  - Display "Dừng" button during download
  - Update progress bar for each declaration
  - Display summary on completion
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 9.1_

- [x] 7.2 Implement stop_download() handler

  - Set stop flag
  - Wait for current declaration to complete
  - Save all completed downloads
  - Display summary with completed/remaining counts
  - Re-enable all controls
  - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [x] 7.3 Write property test for stop operation safety


  - **Property 5: Stop operation safety**
  - **Validates: Requirements 9.2, 9.3**

- [x] 8. Integrate EnhancedManualPanel into main GUI




  - Replace or extend existing manual mode panel
  - _Requirements: All_



- [x] 8.1 Update CustomsAutomationGUI class
  - Replace old manual mode settings with EnhancedManualPanel
  - Maintain backward compatibility where possible
  - Update layout and positioning
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8.2 Update main.py if needed
  - Pass required dependencies to GUI
  - Ensure all components are initialized
  - _Requirements: All_

- [x] 9. Testing and validation




  - Test complete workflow end-to-end
  - _Requirements: All_

- [x] 9.1 Manual testing checklist



  - Test company scan with empty database
  - Test company scan with existing data
  - Test date range validation (invalid ranges)
  - Test preview with various filters
  - Test preview cancellation
  - Test selective download (some selected)
  - Test download stop functionality
  - Test error scenarios (DB disconnect, network failure)
  - _Requirements: All_

- [x] 9.2 Run all property-based tests


  - Run property tests with 100+ iterations
  - Verify all properties pass
  - Fix any failures
  - _Requirements: All_

- [-] 10. Documentation


  - Update user documentation with new features
  - _Requirements: All_


- [x] 10.1 Update USER_GUIDE.md with Enhanced Manual Mode section

  - Add new section "Enhanced Manual Mode" after "Basic Operations"
  - Document company scanning workflow (scan, save, refresh)
  - Document date range selection with validation rules
  - Document declaration preview workflow (filter, preview, select)
  - Document selective download workflow (download selected, stop, progress)
  - Document workflow states and UI behavior
  - Include examples and screenshots where helpful
  - _Requirements: 1.1-1.5, 2.1-2.5, 3.1-3.5, 4.1-4.5, 5.1-5.5, 6.1-6.5, 7.1-7.5, 8.1-8.5, 9.1-9.5_


- [x] 10.2 Update WHATS_NEW.md with Enhanced Manual Mode features






  - Add section for Enhanced Manual Mode under "New Features"
  - Document company scanning and management
  - Document date range picker with validation
  - Document declaration preview with checkboxes
  - Document selective download with stop functionality
  - Explain benefits over old manual mode
  - Add usage examples and workflows
  - _Requirements: All_

- [x] 10.3 Update FEATURES_GUIDE.md with Enhanced Manual Mode section







  - Add detailed Enhanced Manual Mode section to FEATURES_GUIDE.md
  - Include step-by-step tutorials for common workflows
  - Document all UI controls and their functions
  - Add troubleshooting section for common issues
  - Include tips and best practices
  - _Requirements: All_
