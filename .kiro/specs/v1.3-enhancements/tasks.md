# Implementation Plan

- [x] 1. Setup and Configuration Extensions





  - [x] 1.1 Add UIConfig dataclass to models/config_models.py


    - Add theme, notifications_enabled, sound_enabled, batch_limit, window position fields
    - _Requirements: 2.3, 2.6, 6.1, 7.5, 10.5_
  - [x] 1.2 Extend ConfigurationManager with UI settings methods


    - Add get/set methods for theme, notifications, sound, batch_limit, window state
    - Add [UI] section handling in config.ini
    - _Requirements: 2.3, 2.6, 6.1, 7.5, 10.5_
  - [x] 1.3 Write property test for settings round-trip


    - **Property 2: Settings Persistence Round-Trip**
    - **Validates: Requirements 2.3, 2.6, 7.5, 10.5**

- [x] 2. Theme Manager Implementation





  - [x] 2.1 Create gui/theme_manager.py with ThemeManager class


    - Implement LIGHT_THEME and DARK_THEME color dictionaries
    - Implement apply_theme(), toggle_theme(), get_current_theme(), get_color()


    - _Requirements: 7.1, 7.2, 7.4_
  - [x] 2.2 Implement contrast ratio calculation


    - Add calculate_contrast_ratio() method

    - Validate all dark theme color pairs meet 4.5:1 ratio
    - _Requirements: 7.3_
  - [x] 2.3 Write property test for color contrast
    - **Property 8: Theme Color Contrast**
    - **Validates: Requirements 7.3**
  - [x] 2.4 Integrate ThemeManager into CustomsAutomationGUI

    - Apply theme on startup from config
    - Add theme toggle to settings dialog
    - _Requirements: 7.5, 7.6_

- [x] 3. Notification Manager Implementation





  - [x] 3.1 Create gui/notification_manager.py with NotificationManager class


    - Implement Windows toast notifications using win10toast or plyer
    - Implement sound playback using winsound
    - _Requirements: 2.1, 2.2, 2.5_

  - [x] 3.2 Add notification settings to SettingsDialog

    - Add checkboxes for notifications and sound enable/disable
    - Save preferences to config
    - _Requirements: 2.3, 2.4, 2.6_

  - [x] 3.3 Integrate notifications into download workflow

    - Show notification on batch download complete
    - Show notification on database connection error
    - Play sound on completion if enabled
    - _Requirements: 2.1, 2.2, 2.5_

- [x] 4. Error Log Export Implementation





  - [x] 4.1 Create file_utils/error_log_exporter.py


    - Implement ErrorEntry dataclass
    - Implement ErrorLogExporter with export_to_file(), format_entry()
    - Generate default filename with timestamp
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 4.2 Write property test for error log completeness

    - **Property 1: Error Log Export Completeness**
    - **Validates: Requirements 1.1, 1.2**
  - [x] 4.3 Add "Xuất log lỗi" button to EnhancedManualPanel


    - Open file save dialog
    - Handle empty error list case
    - _Requirements: 1.3, 1.4_

- [x] 5. Error Tracker Implementation





  - [x] 5.1 Create error_handling/error_tracker.py


    - Implement ErrorTracker class with record_error(), get_error_history()
    - Add error_history table to tracking database schema
    - _Requirements: 4.4, 4.5_

  - [x] 5.2 Write property test for error storage

    - **Property 5: Error Storage Completeness**
    - **Validates: Requirements 4.4**

  - [x] 5.3 Integrate ErrorTracker into download workflow

    - Record errors during barcode retrieval
    - Store detailed error information
    - _Requirements: 4.4_

- [x] 6. Preview Table UX Improvements





  - [x] 6.1 Create gui/preview_table_controller.py


    - Implement filter by status (all, success, failed, pending)
    - Implement sort by column with toggle
    - Implement double-click to open PDF
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [x] 6.2 Write property test for filter correctness


    - **Property 3: Filter Correctness**
    - **Validates: Requirements 3.2**
  - [x] 6.3 Write property test for sort ordering

    - **Property 4: Sort Ordering**
    - **Validates: Requirements 3.3, 3.4**
  - [x] 6.4 Add filter dropdown to preview section


    - Add combobox with filter options
    - Wire up to PreviewTableController
    - _Requirements: 3.1, 3.2_
  - [x] 6.5 Add column header click handlers for sorting


    - Add visual indicator for sort direction
    - _Requirements: 3.3, 3.4_
  - [x] 6.6 Add tooltip for failed rows with error details


    - Show error message on hover
    - _Requirements: 4.1_
  - [x] 6.7 Add "Tải lại thất bại" button


    - Retry download for failed declarations only
    - Update result column after retry
    - _Requirements: 4.2, 4.3_

- [x] 7. Keyboard Shortcuts Implementation



  - [x] 7.1 Create gui/keyboard_shortcuts.py

    - Implement KeyboardShortcutManager class
    - Register F5, Ctrl+A, Ctrl+Shift+A, Escape shortcuts
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 7.2 Write property test for selection shortcuts

    - **Property 6: Selection Shortcuts**
    - **Validates: Requirements 5.2, 5.3**
  - [x] 7.3 Integrate shortcuts into EnhancedManualPanel


    - Bind shortcuts to appropriate actions
    - Add tooltip hints to buttons
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_



- [x] 8. Window State Manager Implementation

  - [x] 8.1 Create gui/window_state.py

    - Implement WindowStateManager class
    - Save/restore window position and size
    - Validate position is on visible screen
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 8.2 Write property test for window state round-trip

    - **Property 7: Window State Round-Trip**
    - **Validates: Requirements 6.1, 6.2**
  - [x] 8.3 Integrate WindowStateManager into CustomsAutomationGUI


    - Restore state on startup
    - Save state on close
    - _Requirements: 6.1, 6.2_

- [x] 9. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.



- [x] 10. Backup Service Implementation
  - [x] 10.1 Create database/backup_service.py

    - Implement BackupService class
    - Create backup with timestamp filename
    - Cleanup old backups (keep max 7)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 10.2 Write property test for backup file limit
    - **Property 9: Backup File Limit**
    - **Validates: Requirements 8.3**
  - [x] 10.3 Add backup_log table to tracking database

    - Track backup timestamps
    - _Requirements: 8.4_

  - [x] 10.4 Integrate BackupService into application startup
    - Check and backup on startup if needed
    - _Requirements: 8.1_

- [x] 11. Cache Manager Implementation
  - [x] 11.1 Create processors/cache_manager.py

    - Implement CacheManager class
    - Cache preview data with TTL (5 minutes)
    - Generate cache keys from filters
    - _Requirements: 9.2, 9.3, 9.4_

  - [x] 11.2 Write property test for cache validity
    - **Property 10: Cache Validity**
    - **Validates: Requirements 9.2, 9.3**
  - [x] 11.3 Integrate CacheManager into PreviewManager

    - Use cache for repeated preview requests
    - Refresh in background when cache used
    - _Requirements: 9.2, 9.3, 9.4_

- [x] 12. Parallel Downloader Implementation

  - [x] 12.1 Create web_utils/parallel_downloader.py
    - Implement ParallelDownloader class using ThreadPoolExecutor
    - Limit concurrent downloads to 3
    - Support stop/cancel operation

    - _Requirements: 9.1_
  - [x] 12.2 Write property test for parallel download limit
    - **Property 11: Parallel Download Limit**

    - **Validates: Requirements 9.1**
  - [x] 12.3 Integrate ParallelDownloader into EnhancedManualPanel


    - Replace sequential download with parallel
    - Update progress for each completed download
    - _Requirements: 9.1_

- [x] 13. Batch Limiter Implementation
  - [x] 13.1 Create processors/batch_limiter.py

    - Implement BatchLimiter class
    - Validate limit between 1-50
    - Default to 20 for invalid values
    - _Requirements: 10.3, 10.4, 10.5_

  - [x] 13.2 Write property test for batch limit validation
    - **Property 12: Batch Limit Validation**

    - **Validates: Requirements 10.3, 10.4**
  - [x] 13.3 Write property test for batch selection validation

    - **Property 13: Batch Selection Validation**
    - **Validates: Requirements 10.1, 10.2**
  - [x] 13.4 Add batch limit setting to SettingsDialog

    - Add spinbox for batch limit (1-50)
    - Save to config
    - _Requirements: 10.3_
  - [x] 13.5 Integrate BatchLimiter into EnhancedManualPanel
    - Check selection count against limit
    - Show warning and disable button when exceeded
    - _Requirements: 10.1, 10.2_

- [x] 14. Settings Dialog Updates

  - [x] 14.1 Add new settings sections to SettingsDialog

    - Theme selection (Light/Dark)
    - Notifications toggle
    - Sound toggle
    - Batch limit spinbox
    - _Requirements: 2.3, 2.6, 7.1, 10.3_

  - [x] 14.2 Wire up all new settings to ConfigurationManager
    - Save on OK button
    - Apply theme immediately
    - _Requirements: 2.3, 2.6, 7.5, 7.6, 10.5_

- [x] 15. Update Version and Documentation

  - [x] 15.1 Update version to 1.3 in gui/branding.py

    - _Requirements: All_
  - [x] 15.2 Update FEATURES_GUIDE.md with new features

    - Document all new features
    - Add keyboard shortcuts reference
    - _Requirements: All_
  - [x] 15.3 Update config.ini.sample with new settings


    - Add [UI] section with all new options
    - _Requirements: All_

- [x] 16. Final Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.
