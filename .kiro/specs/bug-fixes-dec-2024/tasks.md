# Implementation Plan - Bug Fixes December 2024

- [x] 1. Fix API timeout and selector robustness (P0)





  - Update BarcodeRetriever with reduced timeouts and adaptive selectors
  - Add detailed error logging with HTML structure capture
  - Implement selector caching mechanism
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 1.1 Reduce API and web timeouts


  - Change API timeout from 30s to 10s
  - Add separate web scraping timeout of 15s
  - Update timeout configuration in BarcodeServiceConfig
  - _Requirements: 2.1_

- [x] 1.2 Implement adaptive selector system


  - Create FIELD_SELECTORS dictionary with multiple variations for each field
  - Implement `_try_adaptive_selectors()` method to try all variations
  - Add fallback logic to try alternative selectors when primary fails
  - _Requirements: 2.2, 2.4_

- [x] 1.3 Add HTML structure logging on selector failure


  - Implement `_log_html_structure_on_failure()` method
  - Log page title, URL, all forms, and all input fields
  - Include HTML snippets in error logs for debugging
  - _Requirements: 2.3_

- [x] 1.4 Implement selector caching


  - Create SelectorCache dataclass
  - Implement `_cache_working_selectors()` method
  - Add cache validation with 24-hour expiry
  - Use cached selectors first before trying alternatives
  - _Requirements: 2.5_

- [x] 1.5 Write property test for timeout reduction


  - **Property 2: Timeout reduction effectiveness**
  - **Validates: Requirements 2.1**

- [x] 1.6 Write property test for selector fallback


  - **Property 3: Selector fallback completeness**
  - **Validates: Requirements 2.2, 2.4**

- [x] 1.7 Write unit tests for adaptive selectors


  - Test each selector variation works independently
  - Test fallback chain is executed in correct order
  - Test HTML logging captures correct information
  - Test selector caching saves and loads correctly
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Fix duplicate declarations in preview (P0)





  - Update PreviewManager query to use DISTINCT and GROUP BY
  - Add duplicate detection validation
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


- [x] 2.1 Update database query with DISTINCT

  - Modify `get_declarations_for_preview()` query to use DISTINCT
  - Add GROUP BY clause on SO_TOKHAI, MA_DV, NGAY_DK, MA_HQ
  - Use MIN(ROWID) to select one record per unique declaration
  - _Requirements: 3.1, 3.2_

- [x] 2.2 Add duplicate detection validation


  - Implement `_validate_unique_declarations()` method
  - Check for duplicates in result set
  - Log warning if duplicates found
  - _Requirements: 3.3, 3.4, 3.5_

- [x] 2.3 Write property test for declaration uniqueness


  - **Property 4: Declaration uniqueness**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 2.4 Write unit tests for duplicate prevention


  - Test query returns unique declarations only
  - Test duplicate detection identifies duplicates correctly
  - Test counting returns correct unique count
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Optimize download performance (P1)





  - Implement HTTP session reuse
  - Reduce retry attempts
  - Add method skipping for consistently failing methods
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Implement HTTP session reuse


  - Create session in `__init__` with connection pooling
  - Configure HTTPAdapter with max_retries=1, pool_connections=10
  - Reuse session across all requests in a batch
  - _Requirements: 6.3, 6.4_

- [x] 3.2 Reduce timeout and retry attempts


  - Set API timeout to 10s (from 30s)
  - Set max_retries to 1 (from 3)
  - Remove delays between retry attempts
  - _Requirements: 6.1, 6.2_

- [x] 3.3 Implement method skipping


  - Track failed methods per batch
  - Skip methods that fail consistently (3+ times)
  - Reset skip list for new batches
  - _Requirements: 6.5_

- [x] 3.4 Write property test for session reuse


  - **Property 7: Session reuse efficiency**
  - **Validates: Requirements 6.4**

- [x] 3.5 Write unit tests for performance optimizations


  - Test session is reused across multiple requests
  - Test timeout occurs within new limits
  - Test method skipping works correctly
  - Test retry logic respects new max_retries
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 4. Checkpoint - Ensure all P0/P1 fixes work





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Add calendar date picker (P2)




  - Replace text Entry with tkcalendar DateEntry widget
  - Configure date format and locale
  - Add date validation
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.1 Install and import tkcalendar


  - Add tkcalendar>=1.6.1 to requirements.txt
  - Import DateEntry in enhanced_manual_panel.py
  - _Requirements: 4.1_

- [x] 5.2 Replace date Entry widgets with DateEntry


  - Create `_create_date_picker()` helper method
  - Replace from_date Entry with DateEntry widget
  - Replace to_date Entry with DateEntry widget
  - Configure date_pattern='dd/mm/yyyy'
  - Set locale='vi_VN' for Vietnamese
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 5.3 Add date format validation


  - Implement `_validate_date_format()` method
  - Validate dates before processing
  - Show error message for invalid dates
  - _Requirements: 4.4, 4.5_

- [x] 5.4 Write property test for date format consistency


  - **Property 5: Date format consistency**
  - **Validates: Requirements 4.3**

- [x] 5.5 Write unit tests for date picker


  - Test DateEntry widget is created correctly
  - Test date format is DD/MM/YYYY
  - Test date validation accepts valid dates
  - Test date validation rejects invalid dates
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6. Add company dropdown search/filter (P2)





  - Make combobox editable and add filter functionality
  - Implement real-time filtering on keypress
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6.1 Make company combobox searchable


  - Set combobox state='normal' to allow typing
  - Store all companies in self.all_companies list
  - Bind '<KeyRelease>' event to filter function
  - _Requirements: 5.1, 5.2_

- [x] 6.2 Implement company filtering logic


  - Create `_filter_companies()` method
  - Filter by both tax code and company name (case-insensitive)
  - Update combobox values with filtered results
  - Show "Không tìm thấy" when no matches
  - _Requirements: 5.2, 5.3, 5.4, 5.5_

- [x] 6.3 Write property test for company filter correctness


  - **Property 6: Company filter correctness**
  - **Validates: Requirements 5.2, 5.3, 5.4**

- [x] 6.4 Write unit tests for company dropdown


  - Test combobox allows typing
  - Test filtering by tax code works
  - Test filtering by company name works
  - Test case-insensitive matching
  - Test "Không tìm thấy" shown when no matches
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Add output directory selection UI (P3)





  - Add output directory display and browse button
  - Implement directory selection dialog
  - Save selected directory to config
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 7.1 Create output directory UI section


  - Create `_create_output_directory_section()` method
  - Add label "Thư mục lưu:"
  - Add Entry widget to display current path
  - Add "Chọn..." button
  - Pack in appropriate location in panel
  - _Requirements: 1.1, 1.2_

- [x] 7.2 Implement directory selection


  - Create `_browse_output_directory()` method
  - Use tkinter.filedialog.askdirectory()
  - Update output_var with selected path
  - Validate selected directory exists and is writable
  - _Requirements: 1.2, 1.3_

- [x] 7.3 Implement directory persistence


  - Save selected directory to config.ini
  - Load directory from config on startup
  - Use selected directory when downloading barcodes
  - _Requirements: 1.4, 1.5_

- [x] 7.4 Write property test for output directory persistence


  - **Property 1: Output directory persistence**
  - **Validates: Requirements 1.5**

- [x] 7.5 Write unit tests for output directory selection


  - Test UI section is created correctly
  - Test browse button opens directory dialog
  - Test selected directory updates UI
  - Test directory is saved to config
  - Test directory is loaded from config on startup
  - Test invalid directory shows error
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 8. Update configuration and dependencies





  - Update config.ini with new settings
  - Update requirements.txt with tkcalendar
  - Update configuration models
  - _Requirements: All_

- [x] 8.1 Update BarcodeServiceConfig model


  - Add api_timeout field (default 10)
  - Add web_timeout field (default 15)
  - Add max_retries field (default 1)
  - Add session_reuse field (default True)
  - Add output_path field
  - _Requirements: 1.4, 2.1, 6.1, 6.4_


- [x] 8.2 Update config.ini.sample

  - Add [BarcodeService] section with new settings
  - Add [UI] section with feature flags
  - Document all new configuration options
  - _Requirements: All_



- [x] 8.3 Update requirements.txt





  - Add tkcalendar>=1.6.1
  - _Requirements: 4.1_

- [x] 9. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Update documentation





  - Update USER_GUIDE.md with new features
  - Update CHANGELOG.md with bug fixes
  - Update FEATURES_GUIDE.md
  - _Requirements: All_

- [x] 10.1 Update USER_GUIDE.md


  - Document output directory selection
  - Document calendar date picker usage
  - Document company dropdown search
  - Document performance improvements
  - _Requirements: 1.1, 4.1, 5.1, 6.1_


- [x] 10.2 Update CHANGELOG.md

  - Add entry for bug fixes release
  - List all 6 bugs fixed
  - Document performance improvements
  - Note breaking changes (if any)
  - _Requirements: All_

- [x] 10.3 Update FEATURES_GUIDE.md


  - Add section on Enhanced Manual Mode improvements
  - Document new UI features
  - Add screenshots (if applicable)
  - _Requirements: 1.1, 4.1, 5.1_
