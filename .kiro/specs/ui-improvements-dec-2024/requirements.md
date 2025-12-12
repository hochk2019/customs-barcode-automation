# Requirements Document

## Introduction

Tài liệu này mô tả các yêu cầu cải tiến giao diện người dùng (UI) cho ứng dụng Customs Barcode Automation. Các cải tiến tập trung vào:
1. Đơn giản hóa giao diện bằng cách loại bỏ chế độ Automatic không cần thiết
2. Thêm tính năng tìm kiếm nhanh công ty theo mã số thuế
3. Cải thiện bố cục chọn ngày theo chiều ngang
4. Hiện đại hóa giao diện với màu sắc, styling và visual design tốt hơn

## Glossary

- **Customs Barcode Automation System**: Hệ thống tự động hóa lấy mã vạch hải quan
- **Manual Mode**: Chế độ thủ công cho phép người dùng chọn công ty, khoảng thời gian và tờ khai cụ thể để lấy mã vạch
- **Automatic Mode**: Chế độ tự động lấy mã vạch hàng loạt (sẽ bị loại bỏ)
- **Tax Code (Mã số thuế)**: Mã định danh duy nhất của công ty
- **Company Dropdown**: Danh sách thả xuống chứa các công ty để lọc
- **Date Range Picker**: Bộ chọn khoảng thời gian từ ngày đến ngày

## Requirements

### Requirement 1: Loại bỏ chế độ Automatic

**User Story:** As a user, I want the application to only have Manual mode, so that I can avoid system overload from batch processing.

#### Acceptance Criteria

1. WHEN the application starts THEN the Customs Barcode Automation System SHALL display only Manual mode without any mode selection radio buttons
2. WHEN the user views the Control Panel THEN the Customs Barcode Automation System SHALL hide the Automatic/Manual radio button group
3. WHEN the application initializes THEN the Customs Barcode Automation System SHALL set the operation mode to Manual by default
4. WHEN the user views the Control Panel THEN the Customs Barcode Automation System SHALL hide the Start, Stop, and Run Once buttons associated with Automatic mode

### Requirement 2: Thêm ô tìm kiếm mã số thuế cho Company Dropdown

**User Story:** As a user, I want to quickly search for a company by tax code, so that I can find the desired company without scrolling through a long list.

#### Acceptance Criteria

1. WHEN the user types in the company dropdown THEN the Customs Barcode Automation System SHALL filter the company list to show only companies matching the input text
2. WHEN the user enters a partial tax code THEN the Customs Barcode Automation System SHALL display companies whose tax code contains the entered text
3. WHEN the user enters a partial company name THEN the Customs Barcode Automation System SHALL display companies whose name contains the entered text
4. WHEN the filter matches no companies THEN the Customs Barcode Automation System SHALL display an empty list with the "Tất cả công ty" option still available
5. WHEN the user clears the search input THEN the Customs Barcode Automation System SHALL restore the full company list

### Requirement 3: Chuyển bố cục chọn ngày sang chiều ngang

**User Story:** As a user, I want the date range picker to be displayed horizontally, so that the interface is more compact and easier to read.

#### Acceptance Criteria

1. WHEN the user views the date range section THEN the Customs Barcode Automation System SHALL display "Từ ngày" and "Đến ngày" on the same horizontal row
2. WHEN the date range section is displayed THEN the Customs Barcode Automation System SHALL show the format "Từ ngày [date picker] đến ngày [date picker]" in a single line
3. WHEN the user interacts with date pickers THEN the Customs Barcode Automation System SHALL maintain all existing date validation functionality
4. WHEN the user selects dates THEN the Customs Barcode Automation System SHALL preserve the calendar popup behavior for both date pickers


### Requirement 4: Hiện đại hóa giao diện

**User Story:** As a user, I want a modern and visually appealing interface, so that the application feels professional and is pleasant to use.

#### Acceptance Criteria

1. WHEN the application displays THEN the Customs Barcode Automation System SHALL use a modern color scheme with primary accent color (blue #0078D4) for interactive elements
2. WHEN the user views buttons THEN the Customs Barcode Automation System SHALL display buttons with rounded corners, hover effects, and consistent padding
3. WHEN the user views input fields THEN the Customs Barcode Automation System SHALL display inputs with subtle borders, focus highlights, and consistent styling
4. WHEN the user views section frames THEN the Customs Barcode Automation System SHALL display frames with subtle shadows or borders to create visual hierarchy
5. WHEN the user hovers over interactive elements THEN the Customs Barcode Automation System SHALL provide visual feedback through color changes or subtle animations
6. WHEN the application displays status indicators THEN the Customs Barcode Automation System SHALL use color-coded badges (green for success, red for error, blue for info, orange for warning)
7. WHEN the user views the progress bar THEN the Customs Barcode Automation System SHALL display a styled progress bar with gradient fill and rounded corners
8. WHEN the application displays tables THEN the Customs Barcode Automation System SHALL use alternating row colors and hover highlighting for better readability
