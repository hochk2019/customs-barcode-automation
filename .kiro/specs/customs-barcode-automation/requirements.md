# Requirements Document

## Introduction

Hệ thống tự động hóa khai báo hải quan là một ứng dụng Windows được thiết kế để tự động trích xuất thông tin tờ khai từ cơ sở dữ liệu ECUS5, kiểm tra trạng thái thông quan, và tự động lấy mã vạch từ hệ thống Tổng Cục Hải Quan. Ứng dụng giúp giảm thiểu công việc thủ công, tăng tốc độ xử lý và đảm bảo tính chính xác trong quá trình quản lý tờ khai hải quan.

## Glossary

- **ECUS5System**: Hệ thống cơ sở dữ liệu SQL Server 2008 R2 chứa thông tin tờ khai hải quan
- **CustomsDeclaration**: Tờ khai hải quan chứa thông tin về hàng hóa xuất nhập khẩu
- **BarcodeService**: Dịch vụ web của Tổng Cục Hải Quan cung cấp mã vạch cho tờ khai
- **GreenChannel**: Luồng xanh - tờ khai được thông quan nhanh không cần kiểm tra (mã 1)
- **YellowChannel**: Luồng vàng - tờ khai cần kiểm tra hồ sơ trước khi thông quan (mã 2)
- **ClearedStatus**: Trạng thái đã thông quan của tờ khai
- **TaxCode**: Mã số thuế của doanh nghiệp
- **DeclarationNumber**: Số tờ khai duy nhất
- **CustomsOfficeCode**: Mã đơn vị hải quan xử lý tờ khai
- **TransportMethod**: Phương thức vận chuyển hàng hóa
- **InternalManagementCode**: Mã quản lý nội bộ trong mô tả hàng hóa
- **PDFBarcode**: Tệp PDF chứa mã vạch của tờ khai
- **PollingInterval**: Khoảng thời gian giữa các lần quét dữ liệu (5 phút)
- **QRCodeAPI**: API web service để lấy mã vạch tờ khai

## Requirements

### Requirement 1

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống tự động trích xuất thông tin tờ khai từ ECUS5, để tôi không phải thủ công tra cứu từng tờ khai.

#### Acceptance Criteria

1. WHEN the PollingInterval elapses, THE ECUS5System SHALL query the database for CustomsDeclaration records
2. WHEN querying the database, THE ECUS5System SHALL extract DeclarationNumber, TaxCode, declaration date, CustomsOfficeCode, TransportMethod, channel classification, and goods description
3. WHEN the database connection fails, THE ECUS5System SHALL log the error and attempt reconnection after 30 seconds
4. WHEN extracting data, THE ECUS5System SHALL retrieve records from all registered TaxCode values
5. THE ECUS5System SHALL execute queries every 5 minutes

### Requirement 2

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống chỉ xử lý các tờ khai đã thông quan thuộc luồng xanh hoặc vàng, để tránh xử lý các tờ khai không hợp lệ.

#### Acceptance Criteria

1. WHEN a CustomsDeclaration has GreenChannel classification, THE ECUS5System SHALL mark it as eligible for barcode retrieval
2. WHEN a CustomsDeclaration has YellowChannel classification, THE ECUS5System SHALL mark it as eligible for barcode retrieval
3. WHEN a CustomsDeclaration has ClearedStatus, THE ECUS5System SHALL mark it as eligible for barcode retrieval
4. WHEN a CustomsDeclaration does not have GreenChannel or YellowChannel classification, THE ECUS5System SHALL exclude it from processing
5. WHEN a CustomsDeclaration does not have ClearedStatus, THE ECUS5System SHALL exclude it from processing

### Requirement 3

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống loại trừ các tờ khai có phương thức vận chuyển "Loại khác" và mã quản lý nội bộ đặc biệt, để chỉ xử lý các tờ khai tiêu chuẩn.

#### Acceptance Criteria

1. WHEN a CustomsDeclaration has TransportMethod code 9, THE ECUS5System SHALL exclude it from processing
2. WHEN a CustomsDeclaration contains InternalManagementCode starting with "#&NKTC", THE ECUS5System SHALL exclude it from processing
3. WHEN a CustomsDeclaration contains InternalManagementCode starting with "#&XKTC", THE ECUS5System SHALL exclude it from processing
4. WHEN a CustomsDeclaration passes all exclusion rules, THE ECUS5System SHALL include it in the processing queue
5. THE ECUS5System SHALL check InternalManagementCode in the goods description field

### Requirement 4

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống tự động lấy mã vạch từ QRCodeAPI hoặc website Tổng Cục Hải Quan, để tiết kiệm thời gian truy cập thủ công.

#### Acceptance Criteria

1. WHEN a CustomsDeclaration is eligible, THE BarcodeService SHALL attempt to retrieve the barcode via QRCodeAPI first
2. WHEN QRCodeAPI is unavailable, THE BarcodeService SHALL attempt to retrieve the barcode from the primary website
3. WHEN the primary website is unavailable, THE BarcodeService SHALL attempt to retrieve the barcode from the backup website
4. WHEN retrieving via API, THE BarcodeService SHALL send DeclarationNumber, TaxCode, declaration date, and CustomsOfficeCode
5. WHEN retrieving via website, THE BarcodeService SHALL fill the web form with required fields and submit
6. WHEN barcode retrieval fails after all attempts, THE BarcodeService SHALL log the error and retry in the next polling cycle
7. THE BarcodeService SHALL return the barcode content as PDF bytes

### Requirement 5

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống lưu mã vạch theo định dạng tên file chuẩn, để dễ dàng tìm kiếm và quản lý.

#### Acceptance Criteria

1. WHEN saving a PDFBarcode, THE ECUS5System SHALL format the filename as "TaxCode_DeclarationNumber.pdf"
2. WHEN the output directory does not exist, THE ECUS5System SHALL create it before saving
3. WHEN a PDFBarcode file already exists with the same name, THE ECUS5System SHALL skip saving and log a warning
4. WHEN saving fails due to file system errors, THE ECUS5System SHALL log the error with full details
5. THE ECUS5System SHALL save PDFBarcode files to the user-configured output directory

### Requirement 6

**User Story:** Là một quản trị viên hệ thống, tôi muốn cấu hình các thông số kết nối và đường dẫn lưu trữ, để hệ thống hoạt động trong môi trường khác nhau.

#### Acceptance Criteria

1. WHEN the application starts, THE ECUS5System SHALL read configuration from a configuration file
2. THE ECUS5System SHALL support configuration of database server address, database name, username, and password
3. THE ECUS5System SHALL support configuration of BarcodeService URLs
4. THE ECUS5System SHALL support configuration of output directory path
5. THE ECUS5System SHALL support configuration of PollingInterval
6. WHEN sensitive configuration data is stored, THE ECUS5System SHALL encrypt passwords
7. WHEN configuration is invalid or missing, THE ECUS5System SHALL display an error message and prevent startup

### Requirement 7

**User Story:** Là một quản trị viên hệ thống, tôi muốn hệ thống ghi log chi tiết về các hoạt động, để dễ dàng theo dõi và khắc phục sự cố.

#### Acceptance Criteria

1. WHEN any operation occurs, THE ECUS5System SHALL log the event with timestamp and module name
2. WHEN an error occurs, THE ECUS5System SHALL log the error with full stack trace
3. THE ECUS5System SHALL support multiple log levels including DEBUG, INFO, WARNING, ERROR, and CRITICAL
4. THE ECUS5System SHALL save logs to rotating log files
5. THE ECUS5System SHALL display log messages in the console during execution
6. WHEN log files exceed a configured size, THE ECUS5System SHALL rotate to a new log file

### Requirement 8

**User Story:** Là một nhân viên hải quan, tôi muốn hệ thống tránh xử lý lại các tờ khai đã lấy mã vạch thành công, để tiết kiệm tài nguyên và tránh trùng lặp.

#### Acceptance Criteria

1. WHEN a CustomsDeclaration is processed successfully, THE ECUS5System SHALL record it in a tracking database
2. WHEN querying for new declarations, THE ECUS5System SHALL exclude declarations already in the tracking database
3. THE ECUS5System SHALL store DeclarationNumber, TaxCode, and declaration date as the unique identifier
4. WHEN the tracking database is corrupted, THE ECUS5System SHALL rebuild it from the output directory
5. THE ECUS5System SHALL use SQLite for the tracking database

### Requirement 9

**User Story:** Là một quản trị viên hệ thống, tôi muốn hệ thống có khả năng phục hồi sau lỗi, để đảm bảo hoạt động liên tục.

#### Acceptance Criteria

1. WHEN a network error occurs, THE ECUS5System SHALL retry the operation up to 3 times with exponential backoff
2. WHEN a database connection is lost, THE ECUS5System SHALL attempt to reconnect automatically
3. WHEN the BarcodeService is temporarily unavailable, THE ECUS5System SHALL queue the request for retry
4. WHEN an unhandled exception occurs, THE ECUS5System SHALL log the error and continue with the next polling cycle
5. THE ECUS5System SHALL not terminate due to transient errors

### Requirement 10

**User Story:** Là một người dùng, tôi muốn có giao diện để xem trạng thái hoạt động và điều khiển ứng dụng, để theo dõi và quản lý hệ thống dễ dàng.

#### Acceptance Criteria

1. WHEN the application starts, THE ECUS5System SHALL display a user interface showing current status
2. THE ECUS5System SHALL display the number of declarations processed in the current session
3. THE ECUS5System SHALL display the number of barcodes successfully retrieved
4. THE ECUS5System SHALL display the number of errors encountered
5. THE ECUS5System SHALL provide buttons to start and stop the automated processing
6. THE ECUS5System SHALL provide a button to manually trigger a polling cycle
7. THE ECUS5System SHALL display recent log messages in the interface
8. THE ECUS5System SHALL allow users to configure the output directory through the interface

### Requirement 11

**User Story:** Là một người dùng, tôi muốn chọn chế độ hoạt động tự động hoặc thủ công, để linh hoạt kiểm soát khi nào hệ thống chạy.

#### Acceptance Criteria

1. WHEN the application starts, THE ECUS5System SHALL load the saved operation mode from configuration
2. THE ECUS5System SHALL support two operation modes: automatic and manual
3. WHEN automatic mode is enabled, THE ECUS5System SHALL execute polling cycles at the configured interval
4. WHEN manual mode is enabled, THE ECUS5System SHALL only execute when the user triggers manually
5. THE ECUS5System SHALL provide a toggle control to switch between automatic and manual modes
6. WHEN the operation mode changes, THE ECUS5System SHALL save the new mode to configuration
7. THE ECUS5System SHALL display the current operation mode in the user interface

### Requirement 12

**User Story:** Là một người dùng, tôi muốn có chức năng lấy lại mã vạch cho các tờ khai đã xử lý, để cập nhật hoặc thay thế file bị lỗi.

#### Acceptance Criteria

1. THE ECUS5System SHALL display a list of all processed declarations with their status
2. WHEN a user selects one or more processed declarations, THE ECUS5System SHALL enable the re-download button
3. WHEN the user clicks re-download, THE ECUS5System SHALL retrieve barcodes for selected declarations regardless of existing files
4. WHEN re-downloading, THE ECUS5System SHALL overwrite existing PDF files with the same name
5. WHEN re-downloading completes, THE ECUS5System SHALL update the processed timestamp in the tracking database
6. THE ECUS5System SHALL provide a search function to find declarations by DeclarationNumber or TaxCode
7. THE ECUS5System SHALL display the file path and last processed date for each declaration in the list
