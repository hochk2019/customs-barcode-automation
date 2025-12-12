# Requirements Document

## Introduction

Nâng cấp giao diện ứng dụng "Customs Barcode Automation – GOLDEN LOGISTICS" để có layout responsive, hiện đại và dễ sử dụng hơn. Hiện tại giao diện có vấn đề khi không mở full màn hình - các phần phía dưới (như "Xem trước tờ khai", nút Lấy mã vạch…) bị ẩn khuất, phải kéo/resize mới thấy.

**Framework**: Tkinter (giữ nguyên)
**Nguyên tắc**: Không thay đổi logic nghiệp vụ, chỉ cải thiện UI/UX

## Glossary

- **Responsive Layout**: Bố cục tự động co giãn theo kích thước cửa sổ
- **PanedWindow**: Widget Tkinter cho phép chia vùng có thể resize
- **Scrollable Frame**: Frame có thanh cuộn để hiển thị nội dung dài
- **Min-size**: Kích thước tối thiểu của cửa sổ để tránh vỡ layout
- **Fixed Height Panel**: Panel có chiều cao cố định không thay đổi khi resize
- **Expandable Panel**: Panel tự động mở rộng chiếm không gian còn lại

## Requirements

### Requirement 1: Responsive Window Layout

**User Story:** As a user, I want the application window to resize properly, so that I can see all controls without scrolling when the window is smaller than full screen.

#### Acceptance Criteria

1. WHEN the user resizes the window THEN the System SHALL maintain visibility of all essential controls without clipping
2. WHEN the window width decreases THEN the System SHALL allow horizontal scrolling for wide content areas only
3. WHEN the window height decreases THEN the System SHALL prioritize showing action buttons and preview table with scrollbar
4. THE System SHALL set a minimum window size of 900x600 pixels to prevent layout breakage
5. WHEN the window is maximized THEN the System SHALL expand the preview table area proportionally

### Requirement 2: Fixed Header Panel

**User Story:** As a user, I want the header to remain visible and consistent, so that I always see the app branding and status.

#### Acceptance Criteria

1. THE System SHALL display a fixed-height header (105px) containing logo, company name, slogan, and version
2. WHEN the window is resized THEN the header height SHALL remain constant at 105 pixels
3. THE System SHALL display status indicators (Ready/DB Connected) in the header area
4. THE System SHALL display "Cấu hình DB" and "Cài đặt" buttons in the header area

### Requirement 3: Collapsible Output Directory Panel

**User Story:** As a user, I want the output directory section to be compact, so that it doesn't take too much vertical space.

#### Acceptance Criteria

1. THE System SHALL display the output directory panel with minimal height (approximately 50px)
2. THE System SHALL display the directory path, "Chọn..." button, and "Mở" button in a single row
3. WHEN the window is resized horizontally THEN the directory path entry SHALL expand to fill available width

### Requirement 4: Compact Company & Date Filter Panel

**User Story:** As a user, I want the company and date filter section to be organized efficiently, so that I can quickly filter declarations.

#### Acceptance Criteria

1. THE System SHALL combine company search and dropdown into a single autocomplete combobox
2. WHEN the user types in the company combobox THEN the System SHALL filter and show matching companies in real-time
3. THE System SHALL display date pickers (Từ ngày, đến ngày) in a compact horizontal layout
4. THE System SHALL display action buttons (Quét công ty, Làm mới, Xem trước) in a single row
5. WHEN the window is resized THEN the company panel height SHALL remain relatively fixed (approximately 150px)

### Requirement 5: Expandable Preview Table Panel

**User Story:** As a user, I want the preview table to expand and show as many declarations as possible, so that I can review them without excessive scrolling.

#### Acceptance Criteria

1. THE System SHALL allocate remaining vertical space to the preview table panel after fixed panels
2. WHEN the window height increases THEN the preview table SHALL expand to show more rows
3. THE System SHALL display vertical scrollbar for the preview table when content exceeds visible area
4. THE System SHALL display horizontal scrollbar when table columns exceed visible width
5. WHEN the window is at minimum size THEN the preview table SHALL show at least 5 rows with scrollbar

### Requirement 6: Sticky Action Buttons

**User Story:** As a user, I want the action buttons (Lấy mã vạch, Hủy, Dừng) to always be visible, so that I can control the download process at any time.

#### Acceptance Criteria

1. THE System SHALL display action buttons (Xem trước, Lấy mã vạch, Hủy, Dừng) in a fixed position below the preview table
2. WHEN the window is resized THEN the action buttons SHALL remain visible and accessible
3. THE System SHALL display the progress bar adjacent to action buttons
4. THE System SHALL preserve all existing button functionality (Quét công ty, Làm mới, Xem trước, Lấy mã vạch, Hủy, Dừng)

### Requirement 7: Compact Status Bar

**User Story:** As a user, I want to see summary statistics at a glance, so that I can monitor the download progress.

#### Acceptance Criteria

1. THE System SHALL display a status bar at the bottom showing: selected count, downloaded count, errors
2. THE System SHALL display the status bar with fixed height (approximately 30px)
3. WHEN download progress changes THEN the System SHALL update status bar statistics in real-time

### Requirement 8: Unified Company Search Combobox

**User Story:** As a user, I want to search and select company in a single control, so that I don't have to use separate search and dropdown fields.

#### Acceptance Criteria

1. THE System SHALL replace separate search entry and dropdown with a single editable combobox
2. WHEN the user types in the combobox THEN the System SHALL filter dropdown options in real-time
3. WHEN the user selects a filtered option THEN the System SHALL populate the combobox with the selected company
4. THE System SHALL support both typing to filter and clicking dropdown arrow to see all options
5. WHEN no companies match the search THEN the System SHALL display "Không tìm thấy" message

### Requirement 9: Remove Redundant Panels

**User Story:** As a user, I want a cleaner interface without duplicate information, so that I can focus on the main workflow.

#### Acceptance Criteria

1. THE System SHALL remove the "Recent Logs" panel from the main window to save vertical space
2. THE System SHALL keep the "Processed Declarations" panel but make it collapsible or move to a separate tab
3. THE System SHALL consolidate all controls into the main workflow panels
4. THE System SHALL maintain the footer with designer information

### Requirement 11: Recent Companies Quick Access

**User Story:** As a user, I want to quickly select from recently used companies, so that I don't have to search every time.

#### Acceptance Criteria

1. THE System SHALL display up to 5 most recently used tax codes as quick-select buttons below the company combobox
2. WHEN the user clicks a recent tax code button THEN the System SHALL select that company in the combobox
3. THE System SHALL update the recent companies list after each successful barcode download
4. THE System SHALL persist the recent companies list across application restarts
5. WHEN no recent companies exist THEN the System SHALL hide the quick-select buttons area

### Requirement 10: Fix Statistics Counter

**User Story:** As a user, I want to see accurate download statistics, so that I can track my progress.

#### Acceptance Criteria

1. WHEN a barcode is successfully downloaded THEN the System SHALL increment the "Barcodes Retrieved" counter
2. WHEN a barcode download fails THEN the System SHALL increment the "Errors" counter
3. WHEN a download batch completes THEN the System SHALL update the "Last Run" timestamp
4. THE System SHALL update statistics in real-time during download process
5. THE System SHALL persist statistics across the current session (reset on app restart is acceptable)

### Requirement 12: Modern Visual Styling

**User Story:** As a user, I want a modern and clean visual appearance, so that the application looks professional.

#### Acceptance Criteria

1. THE System SHALL use consistent padding (8-12px) between all UI elements
2. THE System SHALL use Segoe UI font family with sizes 9-10pt for all text
3. THE System SHALL use the existing color scheme (black header #0d0d0d, gold accent #FFD700)
4. THE System SHALL display alternating row colors in the preview table
5. THE System SHALL highlight the currently hovered row in the preview table
