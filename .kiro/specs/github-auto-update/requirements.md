# Requirements Document

## Introduction

Tính năng Auto-Update cho phép ứng dụng Customs Barcode Automation tự động kiểm tra và tải về phiên bản mới từ GitHub Releases. Khi có bản cập nhật mới, ứng dụng sẽ thông báo cho người dùng, tải file cài đặt mới và hướng dẫn cài đặt.

## Glossary

- **Update_Checker**: Module kiểm tra phiên bản mới từ GitHub API
- **Version**: Chuỗi định danh phiên bản theo format semantic versioning (X.Y.Z)
- **GitHub_Release**: Bản phát hành trên GitHub chứa file .exe và release notes
- **Download_Manager**: Module quản lý việc tải file từ GitHub
- **Update_Dialog**: Giao diện hiển thị thông tin cập nhật cho người dùng

## Requirements

### Requirement 1

**User Story:** As a user, I want the application to check for updates on startup, so that I can be notified when a new version is available.

#### Acceptance Criteria

1. WHEN the application starts THEN the Update_Checker SHALL query GitHub API for the latest release version
2. WHEN the Update_Checker receives a response THEN the Update_Checker SHALL parse the version tag from the response
3. WHEN the latest version is newer than current version THEN the Update_Checker SHALL trigger the update notification flow
4. WHEN the GitHub API is unreachable THEN the Update_Checker SHALL log the error and continue application startup normally
5. WHEN the version check completes THEN the Update_Checker SHALL cache the result for the current session

### Requirement 2

**User Story:** As a user, I want to see update information clearly, so that I can decide whether to update.

#### Acceptance Criteria

1. WHEN a new version is available THEN the Update_Dialog SHALL display the current version and new version
2. WHEN displaying update info THEN the Update_Dialog SHALL show the release notes from GitHub
3. WHEN the Update_Dialog opens THEN the Update_Dialog SHALL provide "Cập nhật ngay", "Nhắc lại sau", and "Bỏ qua phiên bản này" buttons
4. WHEN user clicks "Bỏ qua phiên bản này" THEN the Update_Checker SHALL store the skipped version and not notify again for that version

### Requirement 3

**User Story:** As a user, I want to download updates automatically, so that I don't have to manually find and download the installer.

#### Acceptance Criteria

1. WHEN user clicks "Cập nhật ngay" THEN the Download_Manager SHALL download the .exe file from GitHub Release assets
2. WHILE downloading THEN the Download_Manager SHALL display download progress with percentage and speed
3. WHEN download completes THEN the Download_Manager SHALL verify the file integrity using file size
4. IF download fails THEN the Download_Manager SHALL display error message and offer retry option
5. WHEN download is in progress THEN the Download_Manager SHALL allow user to cancel the download

### Requirement 4

**User Story:** As a user, I want the update process to be smooth, so that I can easily install the new version.

#### Acceptance Criteria

1. WHEN download completes successfully THEN the Download_Manager SHALL prompt user to install now or later
2. WHEN user chooses "Cài đặt ngay" THEN the Download_Manager SHALL launch the downloaded installer
3. WHEN installer is launched THEN the application SHALL close itself to allow installation
4. WHEN user chooses "Cài đặt sau" THEN the Download_Manager SHALL save the installer path and remind on next startup

### Requirement 5

**User Story:** As a user, I want to manually check for updates, so that I can update at my convenience.

#### Acceptance Criteria

1. WHEN user clicks "Kiểm tra cập nhật" in Help menu THEN the Update_Checker SHALL check for updates immediately
2. WHEN no update is available THEN the Update_Dialog SHALL display "Bạn đang sử dụng phiên bản mới nhất"
3. WHEN checking manually THEN the Update_Checker SHALL show a loading indicator during the check

### Requirement 6

**User Story:** As a developer, I want version comparison to be accurate, so that updates are detected correctly.

#### Acceptance Criteria

1. WHEN comparing versions THEN the Update_Checker SHALL use semantic versioning comparison (major.minor.patch)
2. WHEN version string contains prefix "v" THEN the Update_Checker SHALL strip the prefix before comparison
3. WHEN version format is invalid THEN the Update_Checker SHALL log error and treat as no update available
