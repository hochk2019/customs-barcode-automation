# Requirements Document

## Introduction

Phiên bản V1.1 tập trung vào cải tiến trải nghiệm người dùng (UX) cho ứng dụng Customs Barcode Automation. Các cải tiến bao gồm: hợp nhất giao diện quản lý công ty, tìm kiếm thông minh, tùy chọn đặt tên file PDF, và cấu hình phương thức lấy mã vạch trong giao diện Settings.

## Glossary

- **System**: Ứng dụng Customs Barcode Automation
- **Company_Panel**: Khu vực giao diện quản lý công ty và thời gian
- **Smart_Search**: Chức năng tìm kiếm tự động khớp công ty theo tên hoặc mã số thuế
- **PDF_Naming**: Cấu trúc đặt tên file PDF khi lưu
- **Retrieval_Method**: Phương thức lấy mã vạch (API/Web/Auto)
- **Preview_Panel**: Khu vực xem trước danh sách tờ khai
- **Declaration**: Tờ khai hải quan
- **Tax_Code**: Mã số thuế công ty
- **Invoice_Number**: Số hóa đơn
- **Bill_of_Lading**: Số vận đơn

## Requirements

### Requirement 1: Cấu hình phương thức lấy mã vạch trong Settings

**User Story:** As a user, I want to configure the barcode retrieval method in the Settings dialog, so that I can choose between API, Web, or Auto mode without editing config files.

#### Acceptance Criteria

1. WHEN a user opens the Settings dialog THEN the System SHALL display a dropdown to select Retrieval_Method with options: Auto, API, Web
2. WHEN a user selects a Retrieval_Method and saves THEN the System SHALL persist the selection to config.ini
3. WHEN the System starts THEN the System SHALL load and apply the saved Retrieval_Method setting
4. WHEN Retrieval_Method is set to Auto THEN the System SHALL try API first and fallback to Web on failure

### Requirement 2: Hợp nhất khu vực Quản lý công ty và Chọn thời gian

**User Story:** As a user, I want a unified Company_Panel that combines company management and date selection, so that I have a streamlined workflow in one area.

#### Acceptance Criteria

1. WHEN the main window loads THEN the System SHALL display a single Company_Panel containing both company selection and date range controls
2. WHEN the Company_Panel is displayed THEN the System SHALL arrange controls in logical groups: company selection on top, date range below
3. WHEN the user interacts with Company_Panel THEN the System SHALL maintain visual consistency with glossy black theme and gold accents
4. WHEN the Company_Panel layout changes THEN the System SHALL preserve all existing functionality for company and date selection

### Requirement 3: Tìm kiếm công ty thông minh

**User Story:** As a user, I want to search for companies by typing name or tax code in a single input field, so that I can quickly find and select companies without multiple steps.

#### Acceptance Criteria

1. WHEN a user types in the Smart_Search field THEN the System SHALL filter the company dropdown to show matching companies
2. WHEN the typed text exactly matches a single company name or Tax_Code THEN the System SHALL auto-select that company
3. WHEN multiple companies match the search text THEN the System SHALL display all matches in the dropdown for manual selection
4. WHEN no companies match the search text THEN the System SHALL display an empty dropdown with no selection change
5. WHEN the Smart_Search field is cleared THEN the System SHALL reset the dropdown to show all companies

### Requirement 4: Mặc định không chọn tờ khai khi xem trước

**User Story:** As a user, I want declarations to be unchecked by default in the Preview_Panel, so that I can manually select only the declarations I need.

#### Acceptance Criteria

1. WHEN declarations are loaded into Preview_Panel THEN the System SHALL display all declarations with unchecked checkboxes
2. WHEN the "Select All" checkbox is clicked THEN the System SHALL check all visible declarations
3. WHEN individual declaration checkboxes are clicked THEN the System SHALL toggle only that declaration's selection state
4. WHEN the filter changes visible declarations THEN the System SHALL maintain the unchecked default for newly visible items

### Requirement 5: Tùy chọn đặt tên file PDF

**User Story:** As a user, I want to choose the PDF file naming format, so that I can organize downloaded barcodes according to my workflow needs.

#### Acceptance Criteria

1. WHEN a user opens Settings THEN the System SHALL display PDF_Naming options: Tax_Code + Declaration_Number, Invoice_Number + Declaration_Number, Bill_of_Lading + Declaration_Number
2. WHEN a user selects a PDF_Naming format and saves THEN the System SHALL persist the selection to config.ini
3. WHEN the System generates a PDF file THEN the System SHALL name the file according to the selected PDF_Naming format
4. WHEN the selected naming field is empty for a declaration THEN the System SHALL fallback to Tax_Code + Declaration_Number format
5. WHEN PDF_Naming uses Invoice_Number THEN the System SHALL format filename as {Invoice_Number}_{Declaration_Number}.pdf
6. WHEN PDF_Naming uses Bill_of_Lading THEN the System SHALL format filename as {Bill_of_Lading}_{Declaration_Number}.pdf

### Requirement 6: Build và Release V1.1

**User Story:** As a developer, I want to test, backup, and build V1.1 release, so that I have a stable production version with all enhancements.

#### Acceptance Criteria

1. WHEN all V1.1 features are implemented THEN the System SHALL pass all existing and new tests
2. WHEN V1.1 is ready for release THEN the developer SHALL create a backup zip file named CustomsBarcodeAutomation_V1.1_Backup.zip
3. WHEN building the exe THEN the build process SHALL produce a minimal production executable with all dependencies
4. WHEN the exe is built THEN the version number SHALL display as V1.1 in the application header
