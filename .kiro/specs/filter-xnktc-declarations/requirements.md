# Requirements Document

## Introduction

Tính năng này cho phép người dùng lọc bỏ các tờ khai xuất nhập khẩu tại chỗ (XNK TC) trong khu vực xem trước tờ khai. Tờ khai XNK tại chỗ là loại tờ khai đặc biệt dùng cho giao dịch giữa các doanh nghiệp trong nước với doanh nghiệp chế xuất, thường không cần lấy mã vạch. Người dùng có thể bật/tắt bộ lọc này thông qua checkbox trong giao diện xem trước.

## Glossary

- **Tờ khai XNK TC (Xuất Nhập Khẩu Tại Chỗ)**: Tờ khai hải quan dùng cho giao dịch xuất nhập khẩu tại chỗ giữa doanh nghiệp nội địa và doanh nghiệp chế xuất
- **NKTC (Nhập Khẩu Tại Chỗ)**: Tờ khai nhập khẩu tại chỗ, nhận biết qua ký tự `#&NKTC` trong trường SoHSTK
- **XKTC (Xuất Khẩu Tại Chỗ)**: Tờ khai xuất khẩu tại chỗ, nhận biết qua ký tự `#&XKTC` trong trường SoHSTK
- **GCPTQ (Gia Công Phụ Trợ Quốc Tế)**: Tờ khai xuất nhập khẩu nguyên liệu doanh nghiệp nội địa gia công cho doanh nghiệp chế xuất, nhận biết qua ký tự `#&GCPTQ` trong trường SoHSTK
- **SoHSTK**: Trường dữ liệu trong database ECUS5 chứa số hồ sơ tờ khai, dùng để nhận biết loại tờ khai
- **Preview Panel**: Khu vực xem trước danh sách tờ khai trong Enhanced Manual Mode
- **Filter Checkbox**: Checkbox cho phép bật/tắt bộ lọc tờ khai XNK TC

## Requirements

### Requirement 1

**User Story:** Là người dùng, tôi muốn có checkbox để lọc bỏ tờ khai XNK tại chỗ trong khu vực xem trước, để tôi chỉ thấy các tờ khai xuất nhập khẩu thông thường cần lấy mã vạch.

#### Acceptance Criteria

1. WHEN the Preview Panel loads THEN the System SHALL display a checkbox labeled "Không lấy mã vạch tờ khai XNK TC" in the control row area
2. WHEN the application starts THEN the System SHALL set the filter checkbox to checked (enabled) by default
3. WHEN the filter checkbox is checked THEN the System SHALL exclude all declarations where SoHSTK field contains "#&NKTC", "#&XKTC", or "#&GCPTQ" patterns from the preview results
4. WHEN the filter checkbox is unchecked THEN the System SHALL include all declarations including XNK TC declarations in the preview results
5. WHEN the user toggles the filter checkbox THEN the System SHALL refresh the preview table to reflect the new filter state

### Requirement 2

**User Story:** Là người dùng, tôi muốn hệ thống nhận biết chính xác các tờ khai XNK tại chỗ dựa trên trường SoHSTK, để bộ lọc hoạt động đúng với tất cả các loại tờ khai XNK TC.

#### Acceptance Criteria

1. WHEN filtering declarations THEN the System SHALL identify NKTC declarations by checking if SoHSTK field contains the pattern "#&NKTC"
2. WHEN filtering declarations THEN the System SHALL identify XKTC declarations by checking if SoHSTK field contains the pattern "#&XKTC"
3. WHEN filtering declarations THEN the System SHALL identify GCPTQ declarations by checking if SoHSTK field contains the pattern "#&GCPTQ"
4. WHEN the SoHSTK field is null or empty THEN the System SHALL treat the declaration as a normal declaration (not XNK TC)
5. WHEN checking patterns THEN the System SHALL perform case-insensitive matching to handle variations in data entry

### Requirement 3

**User Story:** Là người dùng, tôi muốn thấy số lượng tờ khai đã lọc, để tôi biết có bao nhiêu tờ khai XNK TC đã bị loại bỏ.

#### Acceptance Criteria

1. WHEN the filter is applied THEN the System SHALL update the selection count label to show the filtered count
2. WHEN declarations are filtered THEN the System SHALL log the number of XNK TC declarations that were excluded
3. WHEN the preview completes with filter enabled THEN the System SHALL display a status message indicating how many declarations were found after filtering

### Requirement 4

**User Story:** Là người dùng, tôi muốn trạng thái bộ lọc được ghi nhớ trong phiên làm việc, để tôi không phải bật lại mỗi lần xem trước.

#### Acceptance Criteria

1. WHEN the user changes the filter checkbox state THEN the System SHALL remember this state for subsequent preview operations within the same session
2. WHEN performing multiple preview operations THEN the System SHALL apply the current filter state consistently
