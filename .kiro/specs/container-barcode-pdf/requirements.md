# Requirements Document

## Introduction

Tính năng này mở rộng khả năng tạo PDF mã vạch để hỗ trợ tờ khai hàng container (MaPTVC = 2). Khi phương thức vận chuyển là container, PDF sẽ có layout khác với bảng 6 cột bao gồm thông tin container và mã QR cho từng container. Layout phải giống với file MV_container.pdf gốc từ hệ thống ECUS.

## Glossary

- **MaPTVC**: Mã phương thức vận chuyển (1, 3, 4, 5, 9 = hàng thường; 2 = hàng container)
- **Container**: Đơn vị vận chuyển hàng hóa nguyên container
- **SoContainer**: Số hiệu container (ví dụ: BEAU6168370)
- **SoSeal**: Số seal container do doanh nghiệp đóng
- **SoSealHQ**: Số seal hải quan (nếu có)
- **BarcodeImage**: Mã QR dạng base64 encoded PNG cho từng container
- **BangKe**: Danh sách container trong tờ khai (Table_BangKe)
- **ECUS**: Hệ thống hải quan điện tử

## Requirements

### Requirement 1

**User Story:** As a customs officer, I want the system to detect container declarations (MaPTVC = 2), so that the appropriate PDF layout is generated.

#### Acceptance Criteria

1. WHEN the system receives declaration data with MaPTVC value of "2" THEN the system SHALL identify the declaration as a container declaration
2. WHEN the system receives declaration data with MaPTVC value other than "2" THEN the system SHALL identify the declaration as a regular cargo declaration
3. WHEN a container declaration is identified THEN the system SHALL use the container PDF layout instead of the regular cargo layout

### Requirement 2

**User Story:** As a customs officer, I want the container PDF header to match the ECUS format exactly, so that it looks professional and consistent.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL display "Chi cục Hải quan khu vực V" (from TenCucHaiQuan) on the left side, bold
2. WHEN generating PDF for a container declaration THEN the system SHALL display "Hải quan Bắc Ninh" (from TenChiCucHaiQuan) centered below the first line, bold
3. WHEN generating PDF for a container declaration THEN the system SHALL display "- 2" (MaPTVC indicator) on the left margin area
4. WHEN generating PDF for a container declaration THEN the system SHALL display "Ngày DD tháng MM năm YYYY" on the right side, italic (no barcode in header for container PDF)

### Requirement 3

**User Story:** As a customs officer, I want the container PDF to have the correct title section, so that I can identify it as a container declaration.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL display "DANH SÁCH CONTAINER" as the main title, bold, centered
2. WHEN generating PDF for a container declaration THEN the system SHALL display "ĐỦ ĐIỀU KIỆN QUA KHU VỰC GIÁM SÁT HẢI QUAN" as the subtitle, bold, centered
3. WHEN generating PDF for a container declaration THEN the system SHALL display the Ghi_Chu value (e.g., "Tờ khai không phải niêm phong") below the subtitle, bold, centered

### Requirement 4

**User Story:** As a customs officer, I want the container PDF to display declaration info items 1-9, so that I have all necessary declaration details.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL display "1. Chi cục hải quan giám sát:" with full location info (TenChiCucHaiQuanGS - MaDDGS: TenDDGS - MaPTVC)
2. WHEN generating PDF for a container declaration THEN the system SHALL display "2. Đơn vị XNK:" with company name (TenDonViXNK)
3. WHEN generating PDF for a container declaration THEN the system SHALL display items 3-5 on left column: "3. Mã số thuế:", "4. Số tờ khai:", "5. Trạng thái tờ khai:"
4. WHEN generating PDF for a container declaration THEN the system SHALL display items 6-8 on right column: "6. Ngày tờ khai:", "7. Loại hình:", "8. Luồng:"
5. WHEN generating PDF for a container declaration THEN the system SHALL display "9. Số quản lý hàng hóa:" with SoDinhDanh value
6. WHEN generating PDF for a container declaration THEN the system SHALL display all item labels in bold font

### Requirement 5

**User Story:** As a customs officer, I want the container PDF to display a table with 6 columns for container information, so that I can see all container details.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL display a table with 6 columns in order: STT, SỐ HIỆU CONTAINER (1), SỐ SEAL CONTAINER (Nếu có) (2), SỐ SEAL HẢI QUAN (Nếu có) (3), XÁC NHẬN CỦA CÔNG CHỨC HẢI QUAN (4), MÃ VẠCH (5)
2. WHEN the declaration contains multiple containers THEN the system SHALL display one row per container with sequential STT numbers starting from 1
3. WHEN a container has SoSeal value THEN the system SHALL display the seal number in column 2 (trimmed of whitespace)
4. WHEN a container has SoSealHQ value of "#####" THEN the system SHALL display empty cell in column 3
5. WHEN a container has valid SoSealHQ value THEN the system SHALL display the customs seal number in column 3
6. WHEN rendering the table THEN the system SHALL use appropriate column widths to fit all content including QR codes

### Requirement 6

**User Story:** As a customs officer, I want each container row to display a QR code, so that I can scan it for verification.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL decode the BarcodeImage field from base64 to PNG image
2. WHEN rendering the QR code THEN the system SHALL display it in column 6 (MÃ VẠCH (5)) of the container table
3. WHEN the BarcodeImage field is empty or invalid THEN the system SHALL display an empty cell in column 6
4. WHEN rendering the QR code THEN the system SHALL maintain appropriate size for scanning (approximately 2cm x 2cm)
5. WHEN rendering the QR code THEN the system SHALL center the image within the cell

### Requirement 7

**User Story:** As a customs officer, I want the container PDF to parse the BangKe data correctly, so that all containers are displayed.

#### Acceptance Criteria

1. WHEN parsing API response with MaPTVC = 2 THEN the system SHALL extract all Table_BangKe elements from the BangKe/diffgram/DocumentElement section
2. WHEN parsing each Table_BangKe element THEN the system SHALL extract Stt, SoContainer, SoSeal, SoSealHQ, BarcodeImage, and GhiChu fields
3. WHEN the BangKe section contains multiple Table_BangKe elements THEN the system SHALL create a list of container objects preserving the order
4. WHEN parsing is complete THEN the system SHALL provide the container list to the PDF generator
5. WHEN SoContainer or SoSeal contains trailing whitespace THEN the system SHALL trim the whitespace

### Requirement 8

**User Story:** As a customs officer, I want the container PDF to have a notes section, so that I understand how to fill in the form.

#### Acceptance Criteria

1. WHEN generating PDF for a container declaration THEN the system SHALL display "Ghi chú:" section at the bottom
2. WHEN generating PDF for a container declaration THEN the system SHALL display notes explaining each column (Cột số (1), etc.)
3. WHEN generating PDF for a container declaration THEN the system SHALL display the export timestamp "Kết xuất dữ liệu lúc: DD/MM/YYYY HH:MM AM/PM"
