# Implementation Plan

## Overview
Nâng cấp giao diện Customs Barcode Automation để có layout responsive và hiện đại hơn.

---

- [x] 1. Create AutocompleteCombobox Component
  - [x] 1.1 Create `gui/autocomplete_combobox.py` with AutocompleteCombobox class
    - Extend ttk.Combobox with filtering on KeyRelease
    - Support case-insensitive search
    - Display "Không tìm thấy" when no matches
    - _Requirements: 4.1, 4.2, 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x] 1.2 Write property test for autocomplete filtering
    - **Property 4: Company Filter Correctness**
    - **Validates: Requirements 4.2, 8.2**

- [x] 2. Create RecentCompaniesPanel Component
  - [x] 2.1 Create `gui/recent_companies_panel.py` with RecentCompaniesPanel class
    - Display up to 5 recent tax codes as buttons
    - Callback on button click to select company
    - Hide panel when no recent companies
    - _Requirements: 11.1, 11.2, 11.5_
  - [x] 2.2 Add recent companies storage to TrackingDatabase
    - Create table `recent_companies` with tax_code, last_used timestamp
    - Methods: save_recent_company(), get_recent_companies(limit=5)
    - _Requirements: 11.3, 11.4_
  - [x] 2.3 Write property test for recent companies update
    - **Property 7: Recent Companies Update**
    - **Validates: Requirements 11.3**

- [x] 3. Create StatisticsBar Component
  - [x] 3.1 Create `gui/statistics_bar.py` with StatisticsBar class
    - Fixed height 35px
    - Display: Processed, Retrieved, Errors, Last Run
    - Methods: update_stats(), reset_stats()
    - _Requirements: 7.1, 7.2_
  - [x] 3.2 Write property tests for statistics counters
    - **Property 5: Statistics Counter Accuracy**
    - **Property 6: Error Counter Accuracy**
    - **Validates: Requirements 10.1, 10.2**

- [x] 4. Refactor CustomsAutomationGUI Layout


  - [x] 4.1 Set minimum window size to 900x600


    - Add `self.root.minsize(900, 600)` in __init__
    - _Requirements: 1.4_
  - [x] 4.2 Refactor header to fixed height 105px

    - Use `pack_propagate(False)` with height=105
    - Move status indicators and buttons to header
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 4.3 Create compact output directory panel (~50px)

    - Single row: path entry + Chọn + Mở buttons
    - Entry expands horizontally with window
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 4.4 Refactor company panel to use new components

    - Replace separate search + dropdown with AutocompleteCombobox
    - Add RecentCompaniesPanel below combobox
    - Keep date pickers in compact horizontal layout
    - Fixed height ~180px
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 11.1_
  - [x] 4.5 Make preview table panel expandable

    - Use `pack(fill=tk.BOTH, expand=True)`
    - Ensure scrollbars work correctly
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 4.6 Create fixed action buttons panel (~60px)

    - Keep all existing buttons: Xem trước, Lấy mã vạch, Hủy, Dừng
    - Progress bar in same row
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  - [x] 4.7 Add StatisticsBar above footer

    - Replace inline statistics with StatisticsBar component
    - _Requirements: 7.1, 7.2_
  - [x] 4.8 Remove Recent Logs panel


    - Delete _create_log_panel() call
    - Remove log_text widget
    - _Requirements: 9.1_
  - [x] 4.9 Write property tests for layout invariants


    - **Property 1: Header Height Invariant**
    - **Property 2: Preview Table Expansion**
    - **Property 3: Action Buttons Visibility**
    - **Property 8: Company Panel Height Invariant**
    - **Validates: Requirements 2.2, 5.1, 5.2, 6.2, 4.5**

- [x] 5. Fix Statistics Update from EnhancedManualPanel
  - [x] 5.1 Add callback mechanism to EnhancedManualPanel
    - Add `on_download_complete` callback parameter
    - Call callback with (success_count, error_count) after each download
    - _Requirements: 10.1, 10.2, 10.3_
  - [x] 5.2 Connect EnhancedManualPanel to StatisticsBar
    - Pass callback from CustomsAutomationGUI to EnhancedManualPanel
    - Update StatisticsBar when callback is invoked
    - _Requirements: 10.4_
  - [x] 5.3 Update recent companies after successful download
    - Call tracking_db.save_recent_company() after each successful download
    - Refresh RecentCompaniesPanel
    - _Requirements: 11.3_

- [x] 6. Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Integration and Polish
  - [x] 7.1 Test responsive behavior at various window sizes
    - Test at 900x600 (minimum) ✓
    - Test at 1200x800 (medium) ✓
    - Test at 1920x1080 (full HD) ✓
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  - [x] 7.2 Verify all existing functionality preserved
    - Test Quét công ty button ✓
    - Test Làm mới button ✓
    - Test Xem trước button ✓
    - Test Lấy mã vạch button ✓
    - Test Hủy button ✓
    - Test Dừng button ✓
    - _Requirements: 6.4_
  - [x] 7.3 Apply consistent styling
    - Verify padding 8-12px between elements ✓ (ModernStyles.PADDING_NORMAL=8, PADDING_LARGE=12)
    - Verify Segoe UI font ✓ (ModernStyles.FONT_FAMILY="Segoe UI")
    - Verify color scheme ✓ (ModernStyles color palette)
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 8. Final Checkpoint - Ensure all tests pass
  - All 45 responsive UI property tests passed ✓
  - Fixed Unicode edge case in test_case_insensitive_search ✓
