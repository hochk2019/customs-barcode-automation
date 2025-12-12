# Requirements Document

## Introduction

Tài liệu này mô tả các yêu cầu cho phiên bản 1.3 của phần mềm Customs Barcode Automation. Phiên bản này tập trung vào cải thiện trải nghiệm người dùng, quản lý lỗi tốt hơn, tối ưu hiệu suất và thêm các tính năng tiện ích mới.

## Glossary

- **System**: Phần mềm Customs Barcode Automation
- **User**: Người dùng phần mềm
- **Declaration**: Tờ khai hải quan
- **Barcode**: Mã vạch của tờ khai
- **Preview_Table**: Bảng xem trước danh sách tờ khai
- **Batch_Download**: Quá trình tải nhiều mã vạch cùng lúc
- **Error_Log**: Nhật ký lỗi
- **Desktop_Notification**: Thông báo hiển thị trên desktop Windows
- **Tracking_Database**: Cơ sở dữ liệu theo dõi tờ khai đã xử lý (tracking.db)
- **Batch_Limit**: Giới hạn số tờ khai tối đa trong một lần tải

## Requirements

### Requirement 1: Export/Báo cáo

**User Story:** As a user, I want to export error logs to a file, so that I can troubleshoot issues more easily.

#### Acceptance Criteria

1. WHEN a user clicks the "Xuất log lỗi" button THEN the System SHALL export all error entries from the current session to a text file
2. WHEN exporting error logs THEN the System SHALL include timestamp, error type, declaration number, and error message for each entry
3. WHEN the export completes THEN the System SHALL open a file save dialog with default filename format "error_log_YYYYMMDD_HHMMSS.txt"
4. WHEN no errors exist in the current session THEN the System SHALL display a message "Không có lỗi để xuất"

### Requirement 2: Desktop Notifications

**User Story:** As a user, I want to receive desktop notifications for important events, so that I can be informed even when the application is minimized.

#### Acceptance Criteria

1. WHEN a Batch_Download completes THEN the System SHALL display a Desktop_Notification showing success count and error count
2. WHEN the database connection fails THEN the System SHALL display a Desktop_Notification with error message
3. WHEN a user enables/disables notifications in settings THEN the System SHALL persist this preference to config.ini
4. WHEN notifications are disabled THEN the System SHALL NOT display any Desktop_Notification
5. WHEN a Batch_Download completes and sound is enabled THEN the System SHALL play a completion sound
6. WHEN a user enables/disables sound in settings THEN the System SHALL persist this preference to config.ini

### Requirement 3: Preview Table UX Improvements

**User Story:** As a user, I want to filter, sort, and interact with the preview table more efficiently, so that I can manage declarations better.

#### Acceptance Criteria

1. WHEN a user clicks on a filter dropdown THEN the System SHALL display options: "Tất cả", "Thành công", "Thất bại", "Chưa xử lý"
2. WHEN a filter is selected THEN the System SHALL display only declarations matching that status
3. WHEN a user clicks on a column header THEN the System SHALL sort the table by that column in ascending order
4. WHEN a user clicks the same column header again THEN the System SHALL sort in descending order
5. WHEN a user double-clicks on a row with successful download THEN the System SHALL open the PDF file in default viewer
6. WHEN a user double-clicks on a row without downloaded file THEN the System SHALL display message "File chưa được tải"

### Requirement 4: Error Management

**User Story:** As a user, I want to see detailed error information and retry failed downloads, so that I can resolve issues efficiently.

#### Acceptance Criteria

1. WHEN a user hovers over a failed declaration row THEN the System SHALL display a tooltip with detailed error message
2. WHEN a user clicks "Tải lại thất bại" button THEN the System SHALL retry download for all failed declarations in the current batch
3. WHEN retrying failed downloads THEN the System SHALL update the result column for each retried declaration
4. WHEN an error occurs THEN the System SHALL store error details including timestamp, declaration number, error type, and full message in Tracking_Database
5. WHEN viewing error history THEN the System SHALL display errors from the last 30 days

### Requirement 5: Keyboard Shortcuts

**User Story:** As a user, I want to use keyboard shortcuts for common actions, so that I can work more efficiently.

#### Acceptance Criteria

1. WHEN a user presses F5 THEN the System SHALL refresh the preview table
2. WHEN a user presses Ctrl+A in the preview table THEN the System SHALL select all visible declarations
3. WHEN a user presses Ctrl+Shift+A THEN the System SHALL deselect all declarations
4. WHEN a user presses Escape during download THEN the System SHALL stop the current download process
5. WHEN the application starts THEN the System SHALL display a tooltip showing available shortcuts on hover over relevant buttons

### Requirement 6: Window State Persistence

**User Story:** As a user, I want the application to remember my window position and size, so that I don't have to resize it every time.

#### Acceptance Criteria

1. WHEN the application closes THEN the System SHALL save window position (x, y) and size (width, height) to config.ini
2. WHEN the application starts THEN the System SHALL restore window position and size from config.ini
3. WHEN saved position is outside visible screen area THEN the System SHALL reset to default centered position
4. WHEN no saved position exists THEN the System SHALL use default size 1200x850 centered on screen

### Requirement 7: Dark Mode

**User Story:** As a user, I want to switch to dark mode, so that I can reduce eye strain when working in low-light conditions.

#### Acceptance Criteria

1. WHEN a user enables dark mode in settings THEN the System SHALL apply dark color scheme to all UI components
2. WHEN dark mode is enabled THEN the System SHALL use high-contrast color palette:
   - Primary background: #1e1e1e (dark gray)
   - Secondary background: #2d2d2d (lighter gray for panels)
   - Card/Frame background: #383838 (elevated surfaces)
   - Primary text: #ffffff (white)
   - Secondary text: #b0b0b0 (light gray)
   - Accent color: #4fc3f7 (bright cyan for highlights)
   - Success color: #66bb6a (bright green)
   - Error color: #ef5350 (bright red)
   - Warning color: #ffca28 (bright yellow)
   - Border color: #555555 (visible borders)
3. WHEN dark mode is enabled THEN the System SHALL ensure minimum contrast ratio of 4.5:1 between text and background
4. WHEN a user disables dark mode THEN the System SHALL restore the default light color scheme
5. WHEN the application starts THEN the System SHALL apply the saved theme preference from config.ini
6. WHEN switching themes THEN the System SHALL update all visible components immediately without restart

### Requirement 8: Automatic Backup

**User Story:** As a user, I want the tracking database to be backed up automatically, so that I don't lose data.

#### Acceptance Criteria

1. WHEN the application starts THEN the System SHALL check if backup is needed (last backup > 24 hours)
2. WHEN backup is needed THEN the System SHALL create a copy of tracking.db with filename format "tracking_backup_YYYYMMDD.db"
3. WHEN more than 7 backup files exist THEN the System SHALL delete the oldest backup files
4. WHEN backup completes THEN the System SHALL log the backup timestamp

### Requirement 9: Performance Optimization

**User Story:** As a user, I want faster downloads and cached preview results, so that I can work more efficiently.

#### Acceptance Criteria

1. WHEN downloading multiple barcodes THEN the System SHALL process up to 3 downloads in parallel
2. WHEN a user returns to a previously loaded preview THEN the System SHALL use cached results if less than 5 minutes old
3. WHEN cache is older than 5 minutes THEN the System SHALL refresh data from database
4. WHEN a user clicks "Xem trước" THEN the System SHALL display cached data immediately while refreshing in background

### Requirement 10: Batch Download Limit

**User Story:** As a user, I want to limit the number of declarations per batch, so that I don't overload the API server.

#### Acceptance Criteria

1. WHEN a user selects more declarations than Batch_Limit THEN the System SHALL display warning "Bạn đã chọn X tờ khai, vượt quá giới hạn Y. Vui lòng bỏ chọn bớt."
2. WHEN Batch_Limit is exceeded THEN the System SHALL disable the "Lấy mã vạch" button
3. WHEN a user changes Batch_Limit in settings THEN the System SHALL validate value is between 1 and 50
4. WHEN Batch_Limit setting is empty or invalid THEN the System SHALL use default value of 20
5. WHEN the application starts THEN the System SHALL load Batch_Limit from config.ini with default value 20
