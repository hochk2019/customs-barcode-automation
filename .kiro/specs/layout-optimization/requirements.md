# Requirements Document

## Introduction

Tài liệu này mô tả yêu cầu tối ưu hóa bố cục giao diện (Layout Optimization) cho ứng dụng Customs Barcode Automation. Mục tiêu là tái cấu trúc layout để cân đối hơn, thu gọn các khu vực điều khiển và di chuyển bảng xem trước tờ khai sang bên phải, tạo giao diện 2 cột hiện đại và dễ sử dụng hơn.

## Glossary

- **Header_Banner**: Khu vực header cố định ở trên cùng chứa logo, motto, tên công ty, slogan, và các nút Giới thiệu/Cập nhật (KHÔNG thay đổi)
- **Footer**: Khu vực footer cố định ở dưới cùng chứa thông tin designer và liên hệ (KHÔNG thay đổi)
- **Control_Panel**: Khu vực chứa các điều khiển chính bao gồm Status, Thư mục lưu file, Quản lý công ty & Thời gian
- **Preview_Panel**: Bảng xem trước danh sách tờ khai với checkbox để chọn tải mã vạch
- **Recent_Companies**: Danh sách các mã số thuế đã sử dụng gần đây, hiển thị dưới dạng nút bấm nhanh
- **Two_Column_Layout**: Bố cục 2 cột với Control_Panel bên trái và Preview_Panel bên phải
- **Compact_Mode**: Chế độ hiển thị thu gọn cho các section điều khiển
- **Settings_Dialog**: Hộp thoại cài đặt ứng dụng

## Requirements

### Requirement 1: Two-Column Layout Structure

**User Story:** As a user, I want the interface to have a balanced two-column layout, so that I can see both controls and preview data simultaneously without excessive scrolling.

#### Acceptance Criteria

1. WHEN the application window loads THEN the System SHALL display Header_Banner at top, Footer at bottom, and a two-column layout in the main content area with Control_Panel on the left (35-40% width) and Preview_Panel on the right (60-65% width)
2. WHILE the layout is displayed THEN the System SHALL keep Header_Banner and Footer unchanged from current design
3. WHEN the window is resized THEN the System SHALL maintain the proportional column widths while respecting minimum width constraints
4. WHEN the window width is below 1200 pixels THEN the System SHALL maintain minimum column widths of 400px for Control_Panel and 500px for Preview_Panel
5. WHILE the two-column layout is active THEN the System SHALL ensure both columns have equal visual weight with consistent padding and margins

### Requirement 2: Compact Status Section

**User Story:** As a user, I want the status section to be more compact, so that more screen space is available for the preview table.

#### Acceptance Criteria

1. WHEN displaying the status section THEN the System SHALL show status indicators (Ready/Connected) and statistics in a single horizontal row with reduced vertical padding
2. WHEN displaying statistics THEN the System SHALL use inline format "Processed: X | Retrieved: Y | Errors: Z | Last: HH:MM" instead of separate labels
3. WHEN the status section is rendered THEN the System SHALL occupy no more than 40 pixels in height
4. WHILE displaying status THEN the System SHALL use color-coded indicators (green for success, red for errors) without additional text labels

### Requirement 3: Compact Output Directory Section

**User Story:** As a user, I want the output directory section to be minimal, so that it doesn't take up unnecessary vertical space.

#### Acceptance Criteria

1. WHEN displaying the output directory section THEN the System SHALL show the path input and buttons in a single row with reduced padding
2. WHEN the output directory section is rendered THEN the System SHALL occupy no more than 50 pixels in height including the frame border
3. WHEN the path is too long to display THEN the System SHALL truncate with ellipsis from the beginning showing "...\\folder\\subfolder"

### Requirement 4: Compact Company & Time Management Section

**User Story:** As a user, I want the company and time management section to be more compact, so that the interface feels less cluttered.

#### Acceptance Criteria

1. WHEN displaying the company section THEN the System SHALL arrange "Quét công ty" and "Làm mới" buttons inline with the company dropdown
2. WHEN displaying the date range THEN the System SHALL show "Từ ngày" and "đến ngày" pickers in a single row with minimal spacing
3. WHEN displaying recent companies THEN the System SHALL show them as small pill-shaped buttons in a horizontal flow layout
4. WHEN the company section is rendered THEN the System SHALL occupy no more than 150 pixels in height including all sub-elements
5. WHILE displaying the company dropdown THEN the System SHALL use a compact height of 28 pixels for the input field

### Requirement 5: Preview Panel on Right Side

**User Story:** As a user, I want the preview table to be on the right side of the screen, so that I can see more declaration data while having controls accessible on the left.

#### Acceptance Criteria

1. WHEN the preview panel is displayed THEN the System SHALL position it on the right side of the two-column layout
2. WHEN the preview panel is rendered THEN the System SHALL expand to fill the available vertical space from below the header to above the footer
3. WHEN displaying the preview table THEN the System SHALL show action buttons (Xem trước, Lấy mã vạch, Hủy, Dừng) above the table within the Preview_Panel
4. WHEN the preview table has data THEN the System SHALL display filter controls and selection count in a compact header row
5. WHILE the preview panel is active THEN the System SHALL maintain a minimum height of 400 pixels for the table area

### Requirement 6: Configurable Recent Companies Count

**User Story:** As a user, I want to configure how many recent tax codes are displayed, so that I can customize the interface to my workflow.

#### Acceptance Criteria

1. WHEN opening the Settings_Dialog THEN the System SHALL display a "Số lượng mã số thuế gần đây" setting with a spinbox control
2. WHEN configuring recent companies count THEN the System SHALL allow values between 3 and 10 with a default of 5
3. WHEN the user saves settings THEN the System SHALL persist the recent companies count to config.ini under [UI] section
4. WHEN the application loads THEN the System SHALL read the recent companies count from config and apply it to Recent_Companies panel
5. WHEN the recent companies count is changed THEN the System SHALL immediately update the Recent_Companies panel display without requiring restart

### Requirement 7: Visual Harmony and Color Balance

**User Story:** As a user, I want the interface colors to be harmonious and balanced, so that the application looks professional and is easy on the eyes.

#### Acceptance Criteria

1. WHEN displaying the Control_Panel THEN the System SHALL use a subtle background color (#FAFAFA for light theme, #252525 for dark theme) to visually separate it from the Preview_Panel
2. WHEN displaying section frames THEN the System SHALL use consistent border colors (#E0E0E0 for light, #3A3A3A for dark) with 1px solid borders
3. WHEN displaying labels and text THEN the System SHALL use consistent font sizes (11px for labels, 10px for secondary text) across all sections
4. WHILE the interface is displayed THEN the System SHALL maintain consistent spacing of 8px between elements and 12px between sections
5. WHEN displaying buttons THEN the System SHALL use consistent button heights of 28px for primary actions and 24px for secondary actions

### Requirement 8: Resizable Panel Splitter

**User Story:** As a user, I want to drag the divider between Control_Panel and Preview_Panel to adjust their widths, so that I can customize the layout to my preference.

#### Acceptance Criteria

1. WHEN the two-column layout is displayed THEN the System SHALL show a draggable vertical splitter (sash) between Control_Panel and Preview_Panel
2. WHEN the user drags the splitter THEN the System SHALL resize both panels in real-time while respecting minimum width constraints (400px for Control_Panel, 500px for Preview_Panel)
3. WHEN the user releases the splitter THEN the System SHALL save the new panel widths to config.ini under [UI] section as "panel_split_position"
4. WHEN the application loads THEN the System SHALL restore the saved panel split position from config
5. WHILE dragging the splitter THEN the System SHALL display a visual indicator (cursor change to ew-resize) to show the splitter is active

### Requirement 9: Responsive Behavior

**User Story:** As a user, I want the layout to adapt gracefully when I resize the window, so that the interface remains usable at different sizes.

#### Acceptance Criteria

1. WHEN the window is resized horizontally THEN the System SHALL adjust column widths proportionally while maintaining minimum constraints and saved split ratio
2. WHEN the window is resized vertically THEN the System SHALL expand or contract the Preview_Panel table area while keeping Control_Panel sections at fixed heights
3. WHEN the window reaches minimum size (1000x700) THEN the System SHALL prevent further shrinking and show scrollbars if needed
4. IF the window width is below 1000 pixels THEN the System SHALL switch to a single-column stacked layout with Preview_Panel below Control_Panel

