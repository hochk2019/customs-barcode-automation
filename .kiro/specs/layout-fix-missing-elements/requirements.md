# Requirements Document

## Introduction

Tài liệu này mô tả yêu cầu sửa lỗi và bổ sung các thành phần còn thiếu trong giao diện hai cột mới của ứng dụng Customs Barcode Automation. Sau khi chuyển từ layout dọc sang layout hai cột, một số thành phần UI bị thiếu hoặc trùng lặp cần được khắc phục.

## Glossary

- **CompactStatusBar**: Thanh trạng thái compact ở đầu Control Panel, hiển thị Status và DB connection
- **StatisticsBar**: Thanh thống kê riêng biệt hiển thị Processed, Retrieved, Errors, Last Run
- **PreviewPanel**: Panel bên phải chứa bảng xem trước tờ khai và các nút action
- **ProgressBar**: Thanh tiến trình hiển thị % hoàn thành khi download
- **ProgressLabel**: Label hiển thị "Đang xử lý X/Y..." khi download

## Requirements

### Requirement 1: Loại bỏ Statistics trùng lặp trong CompactStatusBar

**User Story:** As a user, I want to see statistics in only one place, so that the interface is not confusing with duplicate information.

#### Acceptance Criteria

1. WHEN the CompactStatusBar is displayed THEN the System SHALL show only Status indicator and DB indicator, NOT the statistics (Processed/Retrieved/Errors/Last)
2. WHEN the StatisticsBar is displayed THEN the System SHALL show statistics in format "Declarations Processed: X | Barcodes Retrieved: Y | Errors: Z | Last Run: HH:MM"
3. WHILE the interface is displayed THEN the System SHALL ensure statistics appear in only ONE location (StatisticsBar)

### Requirement 2: Bổ sung nút Tải lại thất bại vào PreviewPanel

**User Story:** As a user, I want to retry failed downloads directly from the preview panel, so that I can quickly fix download errors.

#### Acceptance Criteria

1. WHEN the PreviewPanel is displayed THEN the System SHALL show a "Tải lại thất bại" button in the action buttons row
2. WHEN the user clicks "Tải lại thất bại" THEN the System SHALL retry downloading barcodes for declarations that previously failed
3. WHILE no failed declarations exist THEN the System SHALL disable the "Tải lại thất bại" button
4. WHEN retry completes THEN the System SHALL update the result column for retried declarations

### Requirement 3: Bổ sung Progress Bar vào PreviewPanel

**User Story:** As a user, I want to see download progress visually, so that I know how much work remains.

#### Acceptance Criteria

1. WHEN download starts THEN the System SHALL display a progress bar in the PreviewPanel status area
2. WHILE downloading THEN the System SHALL update the progress bar value from 0 to 100 based on completion percentage
3. WHEN download completes or stops THEN the System SHALL hide the progress bar
4. WHILE progress bar is visible THEN the System SHALL display it with minimum width of 200px

### Requirement 4: Bổ sung Progress Label vào PreviewPanel

**User Story:** As a user, I want to see detailed progress text, so that I know exactly which declaration is being processed.

#### Acceptance Criteria

1. WHEN download starts THEN the System SHALL display a progress label showing "Đang xử lý X/Y..."
2. WHILE downloading THEN the System SHALL update the progress label with current item number and total
3. WHEN download completes THEN the System SHALL update the label to show completion status
4. WHEN download is stopped THEN the System SHALL update the label to show stopped status

### Requirement 5: Cập nhật layout Action Buttons trong PreviewPanel

**User Story:** As a user, I want all action buttons to be visible and properly organized, so that I can easily access all functions.

#### Acceptance Criteria

1. WHEN the PreviewPanel action row is displayed THEN the System SHALL show buttons in order: [Xem trước] [Lấy mã vạch] [Hủy] [Dừng] [Xuất log] [Tải lại thất bại]
2. WHILE buttons are displayed THEN the System SHALL use consistent styling (28px height for primary, 24px for secondary)
3. WHEN window is resized THEN the System SHALL maintain button visibility and not truncate button text

### Requirement 6: Kết nối Progress từ EnhancedManualPanel đến PreviewPanel

**User Story:** As a user, I want progress updates to appear in the preview panel, so that I can see download status in the right location.

#### Acceptance Criteria

1. WHEN EnhancedManualPanel updates progress THEN the System SHALL forward progress to external PreviewPanel
2. WHEN EnhancedManualPanel changes download state THEN the System SHALL update PreviewPanel button states accordingly
3. WHEN download completes with errors THEN the System SHALL enable "Tải lại thất bại" button in PreviewPanel

### Requirement 7: Sửa lỗi nút Xem trước không hoạt động

**User Story:** As a user, I want the Preview button to work correctly, so that I can see declarations before downloading.

#### Acceptance Criteria

1. WHEN user clicks "Xem trước" button in PreviewPanel THEN the System SHALL call preview_declarations() method in EnhancedManualPanel
2. WHEN preview completes THEN the System SHALL populate the PreviewPanel treeview with declaration data
3. WHEN preview fails THEN the System SHALL show error message and update status label
4. WHILE previewing THEN the System SHALL disable the "Xem trước" button and show loading status

### Requirement 8: Sửa lỗi nút Lấy mã vạch không hoạt động

**User Story:** As a user, I want the Download button to work correctly, so that I can download barcodes for selected declarations.

#### Acceptance Criteria

1. WHEN user clicks "Lấy mã vạch" button in PreviewPanel THEN the System SHALL call download_selected() method in EnhancedManualPanel
2. WHEN download starts THEN the System SHALL update button states (disable Preview/Download, enable Stop)
3. WHEN download completes THEN the System SHALL restore button states and show result summary
4. WHILE downloading THEN the System SHALL update progress bar and progress label in PreviewPanel
