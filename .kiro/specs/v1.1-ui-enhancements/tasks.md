# Implementation Plan - V1.1 UI Enhancements

## Phase 1: Configuration & Settings

- [x] 1. Add new configuration options





  - [x] 1.1 Update BarcodeServiceConfig with pdf_naming_format field


    - Add `pdf_naming_format: str = "tax_code"` to config_models.py
    - Update config.ini.sample with new option
    - _Requirements: 5.1, 5.2_
  - [x] 1.2 Update ConfigurationManager to handle pdf_naming_format


    - Add getter/setter methods for pdf_naming_format
    - Ensure backward compatibility with existing configs
    - _Requirements: 5.2_
  - [x] 1.3 Write property test for config persistence


    - **Property 1: Config Persistence Round-Trip (Retrieval Method)**
    - **Property 2: Config Persistence Round-Trip (PDF Naming)**
    - **Validates: Requirements 1.2, 5.2**

- [x] 2. Create Settings Dialog





  - [x] 2.1 Create SettingsDialog class in gui/settings_dialog.py


    - Create dialog window with glossy black theme
    - Add retrieval method dropdown (Auto/API/Web)
    - Add PDF naming format dropdown (3 options)
    - Add save/cancel buttons
    - _Requirements: 1.1, 5.1_
  - [x] 2.2 Integrate Settings button into main GUI


    - Add "⚙ Cài đặt" button next to "Cấu hình DB" button
    - Wire up to open SettingsDialog
    - _Requirements: 1.1_
  - [x] 2.3 Write unit tests for SettingsDialog


    - Test dialog creation and option display
    - Test save functionality
    - _Requirements: 1.1, 5.1_

## Phase 2: PDF Naming Service

- [x] 3. Implement PDF Naming Service





  - [x] 3.1 Create PdfNamingService class


    - Create file_utils/pdf_naming_service.py
    - Implement generate_filename() with format selection
    - Implement fallback logic for empty fields
    - _Requirements: 5.3, 5.4, 5.5, 5.6_
  - [x] 3.2 Write property test for PDF filename generation


    - **Property 8: PDF Filename Generation**
    - **Validates: Requirements 5.3, 5.4, 5.5, 5.6**
  - [x] 3.3 Integrate PdfNamingService into barcode download workflow


    - Update EnhancedManualPanel to use PdfNamingService
    - Update file_manager to use new naming service
    - _Requirements: 5.3_

- [x] 4. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 3: Smart Company Search

- [x] 5. Implement Smart Search functionality





  - [x] 5.1 Create SmartCompanySearch component


    - Create gui/smart_company_search.py
    - Implement filter_companies() method
    - Implement auto_select_if_exact_match() method
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 5.2 Write property tests for Smart Search


    - **Property 3: Smart Search Filtering**
    - **Property 4: Smart Search Auto-Select**
    - **Validates: Requirements 3.1, 3.2, 3.3**
  - [x] 5.3 Integrate Smart Search into EnhancedManualPanel


    - Replace separate search entry with SmartCompanySearch
    - Wire up auto-select behavior
    - _Requirements: 3.1, 3.2, 3.5_

## Phase 4: Unified Company Panel

- [x] 6. Refactor to Unified Company Panel
  - [x] 6.1 Merge company section and date section in EnhancedManualPanel
    - Remove separate "Chọn khoảng thời gian" LabelFrame
    - Move date pickers into "Quản lý công ty" section
    - Rename section to "Quản lý công ty & Thời gian"
    - _Requirements: 2.1, 2.2, 2.4_
  - [x] 6.2 Optimize layout for better UX
    - Arrange: buttons row → search row → company dropdown → date row
    - Ensure consistent spacing and alignment
    - _Requirements: 2.2, 2.3_
  - [x] 6.3 Write unit tests for unified panel

    - Test all existing functionality still works
    - Test layout contains all required components
    - _Requirements: 2.4_

## Phase 5: Default Unchecked Declarations

- [x] 7. Change default selection behavior





  - [x] 7.1 Update preview loading to default unchecked


    - Modify _populate_preview_tree() to set checkboxes unchecked
    - Update select_all_var default to False
    - _Requirements: 4.1_

  - [x] 7.2 Update selection count display

    - Show "Đã chọn: 0/N tờ khai" initially
    - Update count when user selects items
    - _Requirements: 4.1_

  - [x] 7.3 Write property tests for selection behavior

    - **Property 5: Default Unchecked State**
    - **Property 6: Select All Behavior**
    - **Property 7: Individual Toggle Behavior**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [x] 8. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

## Phase 6: Version Update & Release

- [x] 9. Update version and branding





  - [x] 9.1 Update version number to 1.1


    - Update APP_VERSION in gui/branding.py to "1.1"
    - Update CHANGELOG.md with V1.1 changes
    - _Requirements: 6.4_
  - [x] 9.2 Add disclaimer to About dialog


    - Add disclaimer text to _show_about_dialog() in customs_gui.py
    - Text: "Phần mềm phục vụ cộng đồng lấy mã vạch thuận tiện hơn thay vì lấy thủ công, không nhằm mục đích thương mại. Người dùng cần tuân thủ luật pháp nước Cộng Hòa XHCN Việt Nam, nghiêm cấm sử dụng cho mục đích vi phạm pháp luật. Tự chịu trách nhiệm dân sự/hình sự về việc sử dụng phần mềm."
    - Style: smaller font, gray/accent color, positioned at bottom of dialog

  - [x] 9.3 Update documentation

    - Update README.md with new features
    - Update USER_GUIDE.md with new settings
    - _Requirements: 6.1_

- [-] 10. Testing and Release




  - [x] 10.1 Run full test suite

    - Execute all unit tests
    - Execute all property tests
    - Verify no regressions
    - _Requirements: 6.1_
  - [x] 10.2 Create backup zip


    - Create CustomsBarcodeAutomation_V1.1_Backup.zip
    - Include all source files, configs, and documentation
    - _Requirements: 6.2_

  - [x] 10.3 Build production exe






    - Run build_exe.ps1 with optimizations
    - Verify exe runs correctly
    - Test all new features in exe
    - _Requirements: 6.3_

- [ ] 11. Final Checkpoint - Ensure all tests pass




  - Ensure all tests pass, ask the user if questions arise.
