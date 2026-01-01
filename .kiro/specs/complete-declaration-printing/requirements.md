# Complete Declaration Printing - Requirements

## Overview
Cải tiến hệ thống in tờ khai để tạo ra file Excel hoàn thiện giống hệt như file mẫu từ ECUS, thay vì file Excel đơn giản hiện tại.

## Problem Statement
Hệ thống hiện tại tạo file Excel đơn giản từ template 2-sheet (TKX + HANG), nhưng người dùng cần file Excel hoàn thiện như ECUS tạo ra:
- File mẫu xuất khẩu: `ToKhaiHQ7X_QDTQ_305254403660.xls` (1568 hàng)
- File mẫu nhập khẩu: `ToKhaiHQ7N_QDTQ_107772836360.xlsx` (509 hàng)
- Kết hợp 2 sheet thành 1 sheet duy nhất với nhiều trang lặp lại

## User Stories

### US1: Complete Excel File Generation
**As a** customs officer  
**I want** the "In TKTQ" button to generate complete Excel files identical to ECUS samples  
**So that** I can use them directly for official customs procedures  

**Acceptance Criteria:**
- File Excel được tạo phải giống hệt file mẫu hoàn thiện
- Kết hợp thông tin từ 2 sheet TKX + HANG thành 1 sheet duy nhất
- Lặp lại cấu trúc tờ khai cho từng hàng hóa (mỗi ~57 hàng/trang)
- Sử dụng dữ liệu từ database thay vì XML
- Tên file theo format: `ToKhaiHQ7[X/N]_QDTQ_[DeclarationNumber].xlsx`

### US2: Multi-Page Layout System
**As a** system  
**I want** to automatically calculate number of pages needed based on goods count  
**So that** each goods item gets its own page in the declaration  

**Acceptance Criteria:**
- Tự động tính số trang cần thiết dựa trên số lượng hàng hóa
- Mỗi trang chứa thông tin tờ khai + 1 hàng hóa chi tiết
- Lặp lại header và footer cho mỗi trang
- Đảm bảo tính toàn vẹn dữ liệu trên tất cả các trang

### US3: Database-Driven Data Population
**As a** system  
**I want** to extract all required data from ECUS database  
**So that** the generated files contain complete and accurate information  

**Acceptance Criteria:**
- Lấy dữ liệu từ database ECUS thay vì XML
- Bao gồm tất cả thông tin cần thiết: công ty, hàng hóa, vận tải, thuế
- Xử lý đúng định dạng tiền tệ, ngày tháng theo chuẩn Việt Nam
- Hỗ trợ ký tự tiếng Việt đầy đủ

### US4: Template Combination Engine
**As a** system  
**I want** to combine TKX and HANG sheet data into single comprehensive sheet  
**So that** the output matches ECUS complete declaration format  

**Acceptance Criteria:**
- Đọc và phân tích template 2-sheet (TKX + HANG)
- Kết hợp layout và dữ liệu thành 1 sheet duy nhất
- Duy trì formatting và style từ template gốc
- Xử lý merge cells và complex layouts

## Technical Requirements

### TR1: Enhanced Template System
- Phân tích cấu trúc file mẫu hoàn thiện (1568 hàng vs 142 hàng template)
- Tạo engine kết hợp 2-sheet thành multi-page single sheet
- Hỗ trợ dynamic page generation dựa trên số lượng hàng hóa
- Maintain cell formatting, borders, fonts từ template gốc

### TR2: Advanced Data Mapping
- Map dữ liệu database vào các vị trí chính xác trên template
- Xử lý repeating sections cho multiple goods items
- Format số liệu, ngày tháng theo chuẩn customs Việt Nam
- Handle Vietnamese characters và special symbols

### TR3: Performance Optimization
- Xử lý hiệu quả file Excel lớn (1000+ hàng)
- Memory management cho batch processing
- Progress tracking cho operations lâu
- Error recovery và rollback capabilities

### TR4: Integration Requirements
- Tích hợp với nút "In TKTQ" hiện tại trong Preview Panel
- Maintain backward compatibility với hệ thống cũ
- Logging và audit trail đầy đủ
- Error handling và user feedback

## Business Rules

### BR1: Declaration Type Detection
- Tự động detect loại tờ khai (xuất/nhập, thông quan/phân luồng)
- Sử dụng template tương ứng cho mỗi loại
- Validate dữ liệu phù hợp với loại tờ khai

### BR2: Data Validation
- Chỉ in tờ khai đã thông quan (TTTK = 'T')
- Validate completeness của dữ liệu trước khi tạo file
- Check template availability và permissions

### BR3: File Management
- Tạo file trong thư mục output với naming convention chuẩn
- Overwrite existing files nếu cần
- Maintain file permissions và security

## Success Metrics
- File Excel được tạo giống 100% với file mẫu ECUS
- Thời gian tạo file < 10 giây cho tờ khai có 50 hàng hóa
- 0% lỗi trong quá trình tạo file với dữ liệu hợp lệ
- User satisfaction với chất lượng file output

## Dependencies
- Existing declaration printing system
- ECUS database connection
- Template files in sample/ directory
- Preview Panel integration

## Constraints
- Phải maintain compatibility với hệ thống hiện tại
- File output phải readable bởi Excel và LibreOffice
- Hỗ trợ Windows file system limitations
- Memory usage < 500MB cho batch operations

## Out of Scope
- XML-based processing (chỉ focus database)
- Template editing capabilities
- Custom report formats
- Integration với hệ thống khác ngoài ECUS