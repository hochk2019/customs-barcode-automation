# Requirements Document

## Introduction

Tính năng in tờ khai hải quan từ database ECUS5VNACCS. Hệ thống sẽ lấy dữ liệu tờ khai từ database và tạo file Excel giống 100% với file ECUS gốc về cấu trúc, định dạng, vị trí ô, kích thước cột/hàng.

## Glossary

- **ECUS5VNACCS**: Hệ thống khai báo hải quan điện tử của Việt Nam
- **Tờ khai Nhập khẩu**: Tờ khai có số bắt đầu bằng "10" (12 ký tự), ví dụ: 107808761432
- **Tờ khai Xuất khẩu**: Tờ khai có số bắt đầu bằng "30" (12 ký tự), ví dụ: 308064365030
- **Template**: File Excel mẫu từ ECUS gốc dùng làm cơ sở để tạo tờ khai mới
- **Cell mapping**: Bản đồ vị trí các trường dữ liệu trong template

## Requirements

### Requirement 1

**User Story:** As a customs officer, I want to print import declarations from database, so that I can have physical copies matching ECUS format exactly.

#### Acceptance Criteria

1. WHEN a user provides an import declaration number (starting with "10", 12 digits) THEN the system SHALL retrieve all declaration data from DTOKHAIMD table
2. WHEN the system retrieves import declaration data THEN the system SHALL also retrieve all goods items from DHANGMDDK table ordered by STTHANG
3. WHEN generating import declaration file THEN the system SHALL use template "ToKhaiHQ7N_QDTQ_107807186540.xlsx" as base
4. WHEN the import declaration is generated THEN the system SHALL replace declaration number at positions E4, E79, E142 and barcode at AA3
5. WHEN the import declaration is generated THEN the system SHALL replace company info (tax code at H10, name at H11, address at H14)

### Requirement 2

**User Story:** As a customs officer, I want to print export declarations from database, so that I can have physical copies matching ECUS format exactly.

#### Acceptance Criteria

1. WHEN a user provides an export declaration number (starting with "30", 12 digits) THEN the system SHALL retrieve all declaration data from DTOKHAIMD table
2. WHEN the system retrieves export declaration data THEN the system SHALL also retrieve all goods items from DHANGMDDK table ordered by STTHANG
3. WHEN generating export declaration file THEN the system SHALL use template "ToKhaiHQ7X_QDTQ_308064365030.xlsx" as base
4. WHEN the export declaration is generated THEN the system SHALL replace declaration number at all page positions (E4, E85, E148, E205, E262, E319, E376)
5. WHEN the export declaration is generated THEN the system SHALL replace company info and exporter info at correct positions

### Requirement 3

**User Story:** As a developer, I want the generated file to match ECUS original exactly, so that the output is professional and compliant.

#### Acceptance Criteria

1. WHEN a declaration file is generated THEN the system SHALL preserve 100% of column widths from template
2. WHEN a declaration file is generated THEN the system SHALL preserve 100% of row heights from template
3. WHEN a declaration file is generated THEN the system SHALL preserve 100% of merged cells from template
4. WHEN a declaration file is generated THEN the system SHALL preserve 100% of cell formatting (font, border, fill) from template
5. WHEN a declaration file is generated THEN the system SHALL preserve page structure (page breaks at correct rows)

### Requirement 4

**User Story:** As a user, I want to verify the generated file matches the original, so that I can trust the output quality.

#### Acceptance Criteria

1. WHEN verification is requested THEN the system SHALL compare worksheet dimensions (rows x columns)
2. WHEN verification is requested THEN the system SHALL compare all column widths
3. WHEN verification is requested THEN the system SHALL compare all row heights
4. WHEN verification is requested THEN the system SHALL compare all merged cell ranges
5. WHEN verification is requested THEN the system SHALL report pass/fail status for each check

### Requirement 5

**User Story:** As a user, I want to replace all relevant data fields, so that the declaration contains correct information.

#### Acceptance Criteria

1. WHEN generating declaration THEN the system SHALL replace declaration number in all occurrences
2. WHEN generating declaration THEN the system SHALL replace barcode string (*declaration_number*)
3. WHEN generating declaration THEN the system SHALL replace company tax code if different from template
4. WHEN generating declaration THEN the system SHALL replace company name if different from template
5. WHEN generating declaration THEN the system SHALL replace company address if different from template
6. WHEN generating declaration THEN the system SHALL replace exporter/importer name if different from template

### Requirement 6

**User Story:** As a developer, I want comprehensive cell mapping for both import and export templates, so that all data fields are correctly positioned.

#### Acceptance Criteria

1. WHEN analyzing import template THEN the system SHALL identify all data field positions on page 1 (rows 1-75)
2. WHEN analyzing import template THEN the system SHALL identify all data field positions on page 2 (rows 76-138)
3. WHEN analyzing import template THEN the system SHALL identify all data field positions on page 3+ (goods detail pages)
4. WHEN analyzing export template THEN the system SHALL identify all data field positions on each page
5. WHEN cell mapping is complete THEN the system SHALL document all positions in a JSON mapping file

### Requirement 7

**User Story:** As a user, I want the declaration to automatically adjust pages based on goods count, so that all goods items are included correctly.

#### Acceptance Criteria

1. WHEN the goods count increases compared to template THEN the system SHALL add additional goods pages automatically
2. WHEN the goods count decreases compared to template THEN the system SHALL remove unused goods pages automatically
3. WHEN adding goods pages THEN the system SHALL copy page structure from template goods page (formatting, merged cells, row heights)
4. WHEN adding goods pages THEN the system SHALL update page numbers correctly (e.g., "1/5", "2/5", etc.)
5. WHEN goods pages change THEN the system SHALL update total pages count in header/footer
6. WHEN each goods item is added THEN the system SHALL populate all goods fields (HS code, description, quantity, unit price, total value, origin country)

### Requirement 8

**User Story:** As a developer, I want to understand the page structure of ECUS templates, so that I can correctly add/remove pages.

#### Acceptance Criteria

1. WHEN analyzing import template THEN the system SHALL identify page boundaries (page 1: rows 1-75, page 2: rows 76-138, goods pages: 63 rows each)
2. WHEN analyzing export template THEN the system SHALL identify page boundaries (page 1: rows 1-81, subsequent pages: 57 rows each)
3. WHEN analyzing templates THEN the system SHALL identify goods section start row and rows per goods item
4. WHEN analyzing templates THEN the system SHALL identify page number cell positions (e.g., AF1 for "1/3")
5. WHEN analyzing templates THEN the system SHALL identify total items count cell position
