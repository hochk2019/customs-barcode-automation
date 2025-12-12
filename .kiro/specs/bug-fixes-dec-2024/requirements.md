# Requirements Document - Bug Fixes December 2024

## Introduction

Sau khi testing Enhanced Manual Mode, phát hiện 6 vấn đề quan trọng cần sửa ngay:
1. Không có UI để chọn output directory
2. API timeout và không tìm thấy form fields
3. Duplicate declarations trong preview
4. Date picker không có calendar
5. Company dropdown không thể gõ để tìm
6. Download quá chậm

## Glossary

- **BarcodeRetriever**: Component lấy mã vạch từ website Hải Quan
- **PreviewManager**: Component quản lý preview tờ khai
- **EnhancedManualPanel**: GUI component cho Enhanced Manual Mode
- **DateEntry**: Widget cho phép chọn ngày từ calendar

## Requirements

### Requirement 1: Output Directory Selection

**User Story:** Là một nhân viên hải quan, tôi muốn chọn thư mục lưu file PDF mã vạch, để tôi có thể tổ chức files theo ý muốn.

#### Acceptance Criteria

1. WHEN the Enhanced Manual Panel is displayed, THE GUI SHALL show the current output directory path
2. WHEN the user clicks a "Browse" button, THE GUI SHALL open a directory selection dialog
3. WHEN the user selects a new directory, THE GUI SHALL update the output path
4. WHEN downloading barcodes, THE System SHALL save PDFs to the selected directory
5. WHEN the application restarts, THE System SHALL remember the last selected directory

### Requirement 2: API Timeout and Form Field Detection

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống lấy được mã vạch từ website Hải Quan, ngay cả khi website thay đổi cấu trúc.

#### Acceptance Criteria

1. WHEN the API times out after 30 seconds, THE BarcodeRetriever SHALL reduce timeout to 15 seconds and retry
2. WHEN form fields are not found with current selectors, THE BarcodeRetriever SHALL try alternative selectors
3. WHEN all methods fail, THE BarcodeRetriever SHALL log detailed error information including HTML structure
4. WHEN the website structure changes, THE BarcodeRetriever SHALL adapt by trying multiple field name variations
5. WHEN a barcode is successfully retrieved, THE BarcodeRetriever SHALL cache the working selectors

### Requirement 3: Duplicate Declaration Prevention

**User Story:** Là một nhân viên hải quan, tôi muốn mỗi tờ khai chỉ xuất hiện một lần trong preview, để tôi không phải xử lý trùng lặp.

#### Acceptance Criteria

1. WHEN querying declarations from database, THE PreviewManager SHALL use DISTINCT on declaration number
2. WHEN multiple records exist for same declaration, THE PreviewManager SHALL return only one record
3. WHEN displaying preview, THE GUI SHALL show unique declarations only
4. WHEN user selects one declaration, THE System SHALL process it only once
5. WHEN counting declarations, THE System SHALL count unique declarations only

### Requirement 4: Calendar Date Picker

**User Story:** Là một nhân viên hải quan, tôi muốn chọn ngày từ calendar thay vì phải nhập thủ công, để thao tác nhanh hơn.

#### Acceptance Criteria

1. WHEN the date input field is displayed, THE GUI SHALL show a calendar icon button next to it
2. WHEN the user clicks the calendar icon, THE GUI SHALL open a calendar popup
3. WHEN the user selects a date from calendar, THE GUI SHALL populate the date field in DD/MM/YYYY format
4. WHEN the user types a date manually, THE GUI SHALL validate the format
5. WHEN an invalid date is entered, THE GUI SHALL display an error message

### Requirement 5: Company Dropdown Search

**User Story:** Là một nhân viên hải quan, tôi muốn gõ mã số thuế hoặc tên công ty vào dropdown để tìm nhanh, thay vì phải scroll.

#### Acceptance Criteria

1. WHEN the company dropdown is displayed, THE GUI SHALL allow typing into the combobox
2. WHEN the user types text, THE GUI SHALL filter the company list to show matching entries
3. WHEN typing a tax code, THE GUI SHALL match companies with that tax code
4. WHEN typing a company name, THE GUI SHALL match companies with that name
5. WHEN no matches are found, THE GUI SHALL display "Không tìm thấy"

### Requirement 6: Download Performance Optimization

**User Story:** Là một nhân viên hải quan, tôi muốn download mã vạch nhanh hơn, để không phải chờ lâu.

#### Acceptance Criteria

1. WHEN the API method is attempted, THE BarcodeRetriever SHALL timeout after 10 seconds instead of 30
2. WHEN the API fails, THE BarcodeRetriever SHALL immediately try the next method without delay
3. WHEN using web scraping, THE BarcodeRetriever SHALL use faster HTTP client with connection pooling
4. WHEN multiple declarations are being processed, THE BarcodeRetriever SHALL reuse HTTP sessions
5. WHEN a method consistently fails, THE BarcodeRetriever SHALL skip it for subsequent declarations in the same batch

