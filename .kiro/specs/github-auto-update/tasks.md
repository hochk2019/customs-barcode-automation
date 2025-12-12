# Implementation Plan

- [x] 1. Create Update Module Structure





  - [x] 1.1 Create update module directory and files


    - Create `update/` directory
    - Create `update/__init__.py`, `update/models.py`, `update/version_comparator.py`
    - Create `update/update_checker.py`, `update/download_manager.py`
    - _Requirements: All_

  - [x] 1.2 Define data models

    - Implement `UpdateInfo` dataclass with version, release_notes, download_url, file_size
    - Implement `DownloadProgress` dataclass with percentage and speed_text properties
    - _Requirements: 2.1, 3.2_

- [x] 2. Implement Version Comparator






  - [x] 2.1 Implement parse_version function

    - Parse "X.Y.Z" format to tuple (major, minor, patch)
    - Strip "v" prefix if present
    - Raise ValueError for invalid formats
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 2.2 Write property test for version comparison

    - **Property 1: Version Comparison Correctness**
    - **Validates: Requirements 6.1**

  - [x] 2.3 Write property test for version prefix normalization
    - **Property 2: Version Prefix Normalization**
    - **Validates: Requirements 6.2**

  - [x] 2.4 Write property test for invalid version handling
    - **Property 3: Invalid Version Handling**
    - **Validates: Requirements 6.3**

- [x] 3. Implement Update Checker



  - [x] 3.1 Implement GitHub API client

    - Query GitHub releases API for latest release
    - Parse response to extract version, release notes, assets
    - Handle network errors gracefully
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 3.2 Write property test for GitHub response parsing

    - **Property 4: GitHub Response Parsing**
    - **Validates: Requirements 1.2**

  - [x] 3.3 Implement update detection logic
    - Compare current version with latest version
    - Return UpdateInfo if newer version available
    - Cache result for session
    - _Requirements: 1.3, 1.5_
  - [x] 3.4 Write property test for update detection
    - **Property 5: Update Detection**
    - **Validates: Requirements 1.3**
  - [x] 3.5 Implement skipped version management
    - Store skipped versions in config
    - Check skipped versions before notifying
    - _Requirements: 2.4_
  - [x] 3.6 Write property test for skipped version persistence
    - **Property 6: Skipped Version Persistence**
    - **Validates: Requirements 2.4**

- [x] 4. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Download Manager

  - [x] 5.1 Implement file download with progress
    - Download file from URL with streaming
    - Track progress (bytes downloaded, total, speed)
    - Support cancellation via flag
    - _Requirements: 3.1, 3.2, 3.5_
  - [x] 5.2 Write property test for download progress calculation
    - **Property 7: Download Progress Calculation**
    - **Validates: Requirements 3.2**
  - [x] 5.3 Implement file verification
    - Verify downloaded file size matches expected
    - Delete partial files on failure
    - _Requirements: 3.3_
  - [x] 5.4 Write property test for file size verification
    - **Property 8: File Size Verification**
    - **Validates: Requirements 3.3**
  - [x] 5.5 Write property test for download cancellation
    - **Property 9: Download Cancellation**
    - **Validates: Requirements 3.5**
  - [x] 5.6 Implement pending installer management

    - Save installer path to config when user chooses "install later"
    - Load pending installer on startup
    - _Requirements: 4.4_

  - [x] 5.7 Write property test for pending installer persistence
    - **Property 10: Pending Installer Persistence**
    - **Validates: Requirements 4.4**

- [x] 6. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement Update Dialog



  - [x] 7.1 Create UpdateDialog UI

    - Display current version and new version
    - Display release notes in scrollable text area
    - Add 3 buttons: "Cập nhật ngay", "Nhắc lại sau", "Bỏ qua phiên bản này"
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 7.2 Create Download Progress Dialog

    - Show progress bar with percentage
    - Show download speed (MB/s)
    - Add cancel button
    - _Requirements: 3.2, 3.4, 3.5_
  - [x] 7.3 Create Install Prompt Dialog

    - Prompt "Cài đặt ngay" or "Cài đặt sau"
    - Launch installer and close app if "Cài đặt ngay"
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 8. Integrate with Main Application


  - [x] 8.1 Add version constant to application


    - Create `APP_VERSION = "1.2.3"` constant
    - Use in UpdateChecker initialization
    - _Requirements: 1.1_

  - [x] 8.2 Add update check on startup
    - Call UpdateChecker.check_for_updates() after GUI init
    - Show UpdateDialog if update available
    - Run in background thread to not block startup
    - _Requirements: 1.1, 1.3_
  - [x] 8.3 Add "Kiểm tra cập nhật" menu item
    - Add to Help menu in GUI
    - Show loading indicator during check
    - Show "Bạn đang sử dụng phiên bản mới nhất" if no update
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 8.4 Add Update config section
    - Add [Update] section to config.ini.sample
    - Add github_repo, skipped_versions, pending_installer settings
    - _Requirements: All_

- [x] 9. Final Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.
