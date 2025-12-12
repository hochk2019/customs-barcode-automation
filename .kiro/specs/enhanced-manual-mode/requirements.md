# Requirements Document - Enhanced Manual Mode

## Introduction

Tính năng Enhanced Manual Mode là một cải tiến quan trọng cho hệ thống Customs Barcode Automation, cho phép người dùng có quyền kiểm soát chi tiết hơn trong việc chọn lọc và xử lý tờ khai hải quan. Thay vì chỉ có thể chọn số ngày quét, người dùng giờ đây có thể:
- Quét và lưu trữ danh sách công ty từ database
- Chọn khoảng thời gian cụ thể (từ ngày - đến ngày)
- Xem trước danh sách tờ khai trước khi lấy mã vạch
- Chọn lọc từng tờ khai cụ thể để xử lý

## Glossary

- **CompanyScanner**: Chức năng quét database để lấy danh sách tất cả công ty có tờ khai
- **DateRangePicker**: Widget cho phép chọn khoảng thời gian từ ngày đến ngày
- **DeclarationPreview**: Giao diện hiển thị danh sách tờ khai trước khi xử lý
- **SelectiveDownload**: Chức năng cho phép chọn lọc tờ khai cụ thể để tải mã vạch
- **CompanyDatabase**: Bảng lưu trữ thông tin công ty (mã số thuế, tên công ty)

## Requirements

### Requirement 1

**User Story:** Là một nhân viên hải quan, tôi muốn quét và lưu trữ danh sách tất cả công ty có tờ khai trong database, để tôi có thể chọn công ty cụ thể cho các lần xử lý sau.

#### Acceptance Criteria

1. WHEN the user clicks the "Quét công ty" button, THE CompanyScanner SHALL query the ECUS5 database for all unique tax codes from declarations
2. WHEN the CompanyScanner retrieves tax codes, THE CompanyScanner SHALL attempt to retrieve company names from the DaiLy_DoanhNghiep table
3. WHEN a company name is not found, THE CompanyScanner SHALL use the format "Công ty [tax_code]" as the default name
4. WHEN the scan completes, THE CompanyScanner SHALL save all companies to the CompanyDatabase
5. WHEN companies are saved, THE CompanyScanner SHALL update the company dropdown list in the GUI

### Requirement 2

**User Story:** Là một nhân viên hải quan, tôi muốn chọn khoảng thời gian cụ thể (từ ngày - đến ngày) thay vì chỉ số ngày, để tôi có thể kiểm soát chính xác phạm vi tờ khai cần xử lý.

#### Acceptance Criteria

1. WHEN the Manual Mode is active, THE DateRangePicker SHALL display two date input fields labeled "Từ ngày" and "Đến ngày"
2. WHEN the user selects a start date, THE DateRangePicker SHALL validate that it is not in the future
3. WHEN the user selects an end date, THE DateRangePicker SHALL validate that it is not before the start date
4. WHEN both dates are valid, THE DateRangePicker SHALL enable the "Xem trước" button
5. WHEN the date range exceeds 90 days, THE DateRangePicker SHALL display a warning message

### Requirement 3

**User Story:** Là một nhân viên hải quan, tôi muốn xem trước danh sách tờ khai sẽ được xử lý, để tôi có thể xác nhận trước khi tải mã vạch.

#### Acceptance Criteria

1. WHEN the user clicks "Xem trước", THE DeclarationPreview SHALL query declarations based on selected company and date range
2. WHEN declarations are retrieved, THE DeclarationPreview SHALL display them in a table with columns: checkbox, declaration number, tax code, date
3. WHEN the preview displays declarations, THE DeclarationPreview SHALL show a "Chọn tất cả" checkbox at the top
4. WHEN the user clicks "Chọn tất cả", THE DeclarationPreview SHALL select or deselect all declaration checkboxes
5. WHEN declarations are selected, THE DeclarationPreview SHALL display the count "Đã chọn: X/Y tờ khai"

### Requirement 4

**User Story:** Là một nhân viên hải quan, tôi muốn chọn lọc từng tờ khai cụ thể để tải mã vạch, để tôi không phải xử lý những tờ khai không cần thiết.

#### Acceptance Criteria

1. WHEN the user selects specific declarations in the preview, THE SelectiveDownload SHALL enable the "Lấy mã vạch" button
2. WHEN the user clicks "Lấy mã vạch", THE SelectiveDownload SHALL process only the selected declarations
3. WHEN processing selected declarations, THE SelectiveDownload SHALL skip unselected declarations
4. WHEN a declaration is processed successfully, THE SelectiveDownload SHALL update the progress bar
5. WHEN all selected declarations are processed, THE SelectiveDownload SHALL display a summary with success and error counts

### Requirement 5

**User Story:** Là một nhân viên hải quan, tôi muốn danh sách công ty được lưu trữ lâu dài, để tôi không phải quét lại mỗi lần mở ứng dụng.

#### Acceptance Criteria

1. WHEN companies are scanned, THE CompanyDatabase SHALL store tax_code and company_name in the SQLite tracking database
2. WHEN the application starts, THE CompanyDatabase SHALL load all saved companies into the dropdown
3. WHEN a company already exists in the database, THE CompanyDatabase SHALL update the last_seen timestamp
4. WHEN the user clicks "Làm mới", THE CompanyDatabase SHALL reload companies from the database
5. WHEN the database is empty, THE CompanyDatabase SHALL display only "Tất cả công ty" option

### Requirement 6

**User Story:** Là một nhân viên hải quan, tôi muốn giao diện hiển thị rõ ràng workflow từng bước, để tôi biết cần làm gì tiếp theo.

#### Acceptance Criteria

1. WHEN no companies are in the database, THE GUI SHALL display a message "Vui lòng quét công ty trước"
2. WHEN companies are loaded, THE GUI SHALL enable the company dropdown
3. WHEN company and date range are selected, THE GUI SHALL enable the "Xem trước" button
4. WHEN preview is displayed, THE GUI SHALL enable the "Lấy mã vạch" button only if declarations are selected
5. WHEN processing is in progress, THE GUI SHALL disable all input controls until completion

### Requirement 7

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống xử lý nhanh khi quét công ty, để tôi không phải chờ lâu.

#### Acceptance Criteria

1. WHEN scanning companies, THE CompanyScanner SHALL display a progress indicator
2. WHEN scanning companies, THE CompanyScanner SHALL run in a background thread to avoid blocking the GUI
3. WHEN scanning completes, THE CompanyScanner SHALL display the number of companies found
4. WHEN scanning fails, THE CompanyScanner SHALL display an error message with details
5. WHEN scanning is in progress, THE CompanyScanner SHALL disable the "Quét công ty" button

### Requirement 8

**User Story:** Là một nhân viên hải quan, tôi muốn có thể hủy bỏ quá trình xem trước nếu mất quá nhiều thời gian, để tôi có thể điều chỉnh bộ lọc.

#### Acceptance Criteria

1. WHEN preview is loading, THE DeclarationPreview SHALL display a "Hủy" button
2. WHEN the user clicks "Hủy", THE DeclarationPreview SHALL stop the query and return to the input state
3. WHEN preview is cancelled, THE DeclarationPreview SHALL display a message "Đã hủy xem trước"
4. WHEN preview completes, THE DeclarationPreview SHALL hide the "Hủy" button
5. WHEN preview returns zero results, THE DeclarationPreview SHALL display "Không tìm thấy tờ khai nào"

### Requirement 9

**User Story:** Là một nhân viên hải quan, tôi muốn có thể dừng quá trình lấy mã vạch đang chạy, để tôi có thể hủy bỏ nếu phát hiện sai sót hoặc mất quá nhiều thời gian.

#### Acceptance Criteria

1. WHEN barcode download is in progress, THE SelectiveDownload SHALL display a "Dừng" button
2. WHEN the user clicks "Dừng", THE SelectiveDownload SHALL stop processing remaining declarations
3. WHEN download is stopped, THE SelectiveDownload SHALL save all successfully processed declarations
4. WHEN download is stopped, THE SelectiveDownload SHALL display a summary showing completed and remaining declarations
5. WHEN download completes or is stopped, THE SelectiveDownload SHALL hide the "Dừng" button and enable all input controls
