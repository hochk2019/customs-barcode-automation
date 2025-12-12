# Implementation Plan

## UI Improvements December 2024

- [x] 1. Create ModernStyles module for centralized styling





  - [x] 1.1 Create `gui/styles.py` with ModernStyles class


    - Define color palette constants (PRIMARY_COLOR, SUCCESS_COLOR, ERROR_COLOR, etc.)
    - Define background and border colors
    - Define text colors
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 1.2 Implement `configure_ttk_styles()` method

    - Configure TButton style with rounded appearance and hover effects
    - Configure TEntry style with focus highlighting
    - Configure TCombobox style
    - Configure TLabelframe style with subtle borders
    - Configure Treeview style with alternating row colors
    - _Requirements: 4.2, 4.3, 4.4, 4.8_
  - [x] 1.3 Write unit tests for ModernStyles


    - Test color constants are valid hex codes
    - Test style configuration applies correctly
    - _Requirements: 4.1_

- [x] 2. Remove Automatic mode from main GUI





  - [x] 2.1 Modify `gui/customs_gui.py` to remove mode selection


    - Remove mode_frame with Automatic/Manual radio buttons
    - Remove mode_var, auto_radio, manual_radio variables
    - Remove toggle_operation_mode method
    - Set scheduler to Manual mode by default
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 Remove Start/Stop/Run Once buttons

    - Remove button_frame with Start, Stop, Run Once buttons
    - Remove start_automation, stop_automation, run_manual_cycle methods (or keep for internal use)
    - Remove is_running state variable
    - _Requirements: 1.4_

  - [x] 2.3 Write unit tests for simplified GUI

    - Test that mode radio buttons are not present
    - Test that Start/Stop/Run Once buttons are not visible
    - _Requirements: 1.1, 1.2, 1.4_

- [x] 3. Implement company search filter





  - [x] 3.1 Add search entry to company section in `gui/enhanced_manual_panel.py`


    - Add search entry field above company dropdown
    - Bind KeyRelease event for real-time filtering
    - Store all_companies list for filtering
    - _Requirements: 2.1_

  - [x] 3.2 Implement `_filter_companies()` method

    - Filter by tax code (case-insensitive contains)
    - Filter by company name (case-insensitive contains)
    - Update dropdown values with filtered results
    - Always include "Tất cả công ty" option
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 3.3 Write property test for company filtering


    - **Property 1: Company Filter Completeness**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 3.4 Implement clear search functionality

    - Clear search restores full company list
    - _Requirements: 2.5_

- [x] 4. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement horizontal date range layout



  - [x] 5.1 Modify `_create_date_range_section()` in `gui/enhanced_manual_panel.py`


    - Create single row frame for both date pickers
    - Layout: "Từ ngày [picker] đến ngày [picker]"
    - Remove separate from_row and to_row frames
    - _Requirements: 3.1, 3.2_
  - [x] 5.2 Ensure date validation still works


    - Verify existing validation logic is preserved
    - Test date range validation (from <= to)
    - _Requirements: 3.3_


  - [x] 5.3 Write property test for date validation

    - **Property 3: Date Validation Consistency**
    - **Validates: Requirements 3.3**

- [x] 6. Apply modern styling to EnhancedManualPanel





  - [x] 6.1 Apply ModernStyles to EnhancedManualPanel


    - Import and use ModernStyles in enhanced_manual_panel.py
    - Apply button styles to action buttons
    - Apply entry styles to search and date inputs
    - Apply frame styles to sections
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 6.2 Style progress bar with modern appearance


    - Apply gradient-like styling to progress bar
    - Add rounded corners effect
    - _Requirements: 4.7_

  - [x] 6.3 Style preview table with alternating rows

    - Configure Treeview with alternating row colors
    - Add hover highlighting
    - _Requirements: 4.8_
  - [x] 6.4 Write property test for status color mapping


    - **Property 4: Status Color Mapping**
    - **Validates: Requirements 4.6**

- [x] 7. Apply modern styling to main GUI





  - [x] 7.1 Apply ModernStyles to CustomsAutomationGUI


    - Import and configure styles at application startup
    - Apply styles to status labels
    - Apply styles to statistics panel
    - _Requirements: 4.1, 4.6_
  - [x] 7.2 Style processed declarations table


    - Apply alternating row colors
    - Apply hover highlighting
    - _Requirements: 4.8_

  - [x] 7.3 Style log panel

    - Apply modern font and colors
    - Improve log level color coding
    - _Requirements: 4.6_

- [x] 8. Final Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
