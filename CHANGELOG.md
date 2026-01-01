# Changelog

## [1.5.0] - 2026-01-01

### ✨ New Features

#### 1. Theo dõi thông quan tự động
- **Trạng thái Tự động BẬT/TẮT**: Hiển thị trạng thái tự động kiểm tra thông quan ngay trên toolbar
- **Cập nhật ngay lập tức**: Khi thay đổi trong Cài đặt, trạng thái cập nhật ngay không cần khởi động lại
- **Countdown timer**: Hiển thị thời gian còn lại đến lần kiểm tra tiếp theo
- **Sắp xếp danh sách**: Dropdown sắp xếp theo nhiều tiêu chí (Chờ thông quan trước, Ngày mới/cũ, Công ty)

#### 2. Ghi nhớ Mã Hải quan gần đây
- **Dropdown Mã HQ**: Trong popup "Thêm TK thủ công", mã hải quan giờ là Combobox với dropdown
- **Ghi nhớ 10 mã gần nhất**: Tự động lưu mã HQ khi thêm tờ khai mới
- **Ưu tiên mã gần nhất**: Mã HQ được dùng gần nhất hiển thị đầu tiên

#### 3. Cài đặt "Số công ty tối đa"
- **Spinbox mới trong Cài đặt**: Cho phép chọn từ 1-15 công ty
- **Cập nhật ngay lập tức**: Thay đổi có hiệu lực ngay sau khi Lưu
- **Mặc định 5 công ty**: Giá trị mặc định phù hợp với đa số người dùng

#### 4. Tooltips hướng dẫn sử dụng
- **Panel trái**: Quét công ty, Làm mới, Cấu hình DB, Xóa tất cả, Cài đặt
- **Tab Theo dõi thông quan**: Làm mới, Thêm TK thủ công
- **Delay 0.5s**: Tooltip xuất hiện sau 0.5 giây di chuột qua nút

### 🎨 UI/UX Improvements

#### 1. Sửa đổi Branding
- **Slogan header**: Rút gọn từ "Thích thì thuê - Không thích thì chê - Nhưng đừng bỏ!" thành "Thích thì thuê - Không thích thì chê"
- **Footer text**: Rút gọn từ "...có lợi nhất cho DN về lâu dài!" thành "...có lợi nhất cho DN"
- **Đồng bộ**: About dialog sử dụng chung text với footer

#### 2. Visual Feedback cho nút Làm mới
- **Log output**: In số lượng tờ khai sau khi làm mới
- **Hiệu ứng**: Style thay đổi tạm thời khi đang làm mới

### 🔧 Technical Improvements

#### 1. Callback System cải tiến
- **on_auto_check_changed**: Callback khi thay đổi cài đặt tự động kiểm tra
- **on_max_companies_changed**: Callback khi thay đổi số công ty tối đa
- **Constructor injection**: Tất cả callback được truyền vào constructor thay vì gán sau

#### 2. Preferences mới
- **recent_customs_codes**: Danh sách mã HQ gần đây (max 10)
- **max_companies**: Số công ty tối đa (1-15, default 5)
- **auto_check_interval_minutes**: Đổi default từ 10 → 6 phút
- **retention_days**: Đổi default từ 30 → 5 ngày

### 🐛 Bug Fixes

#### 1. Fixed: Trạng thái Tự động không cập nhật ngay
- **Vấn đề**: Khi thay đổi trong Cài đặt, cần khởi động lại để thấy thay đổi
- **Nguyên nhân**: Có 2 function `_show_settings_dialog` trùng tên, chỉ 1 được wired callback
- **Giải pháp**: Thêm callback vào cả 2 function

#### 2. Fixed: Xóa tờ khai không đúng
- **Vấn đề**: Nút Xóa xóa dựa trên highlight thay vì checkbox
- **Giải pháp**: Đọc giá trị checkbox (☑/☐) thay vì tree.selection()

#### 3. Fixed: Countdown không reset
- **Vấn đề**: Countdown kẹt ở "Đang kiểm tra..." khi không có tờ khai pending
- **Giải pháp**: Gọi on_status_changed() cả khi pending_list rỗng

### 📁 Files Changed

**Modified:**
- `gui/branding.py` - Sửa COMPANY_MOTTO và DESIGNER_NAME
- `gui/components/header_banner.py` - Sửa motto_lines
- `gui/settings_dialog.py` - Thêm max_companies spinbox, callback parameter
- `gui/customs_gui.py` - Wire callbacks cho settings dialog
- `gui/tracking_panel.py` - Thêm auto_status_label, tooltips, refresh feedback
- `gui/add_tracking_dialog.py` - Đổi customs_entry sang Combobox với recent codes
- `gui/enhanced_manual_panel.py` - Thêm tooltips
- `gui/compact_status_bar.py` - Thêm tooltips
- `gui/company_tag_picker.py` - Thêm tooltip, sửa max_companies
- `gui/clearance_checker.py` - Gọi callback khi pending_list rỗng
- `config/preferences_service.py` - Thêm recent_customs_codes, sửa defaults
- `database/tracking_database.py` - Thêm delete_by_id method

**Added:**
- `tests/test_auto_status_update.py` - Test callback flow cho auto status
- `tests/test_countdown_timer.py` - Test countdown timer behavior
- `tests/test_max_companies_setting.py` - Test max companies setting

---

## [1.3.4] - 2024-12-16

### 🔄 Code Formatting & Maintenance
- **Code Formatting**: Áp dụng Kiro IDE autofix và formatting cho tất cả files
- **Code Quality**: Cải thiện chất lượng code với consistent formatting
- **Maintenance Release**: Phiên bản bảo trì với code cleanup

### 🔧 Technical Improvements
- **Consistent Formatting**: Tất cả Python files được format theo chuẩn
- **Better Readability**: Code dễ đọc và maintain hơn
- **Version Sync**: Đồng bộ version number across modules

## [1.3.3] - 2024-12-16

### 🎯 HD Display Optimization
- **Default Window Size**: Giảm kích thước mặc định từ 1200x850 xuống 1100x680 pixels
- **HD Compatibility**: Tối ưu cho màn hình HD (1280x720) và các độ phân giải nhỏ hơn
- **Smart Centering**: Cửa sổ tự động căn giữa màn hình khi mở lần đầu
- **Responsive Design**: Vẫn hiển thị đầy đủ chức năng trên màn hình nhỏ

### 🔧 Technical Improvements
- **WindowStateManager**: Cập nhật DEFAULT_WIDTH=1100, DEFAULT_HEIGHT=680
- **Config Template**: Cập nhật config.ini.sample với kích thước mới
- **Auto-Update Fix**: Sửa lỗi cấu trúc ZIP release để auto-update hoạt động đúng
- **Build Process**: Loại bỏ config.ini khỏi release, chỉ giữ config.ini.sample

### 📦 Release Improvements
- **Flat ZIP Structure**: File release giờ có cấu trúc phẳng thay vì thư mục con
- **Clean Config**: Không bao gồm config.ini có dữ liệu cũ trong release
- **Better Compatibility**: Auto-update hoạt động chính xác với cấu trúc mới

## [1.3.2] - 2024-12-15

### ✨ New Features
- **Two-Column Layout**: Giao diện 2 cột tối ưu với Control Panel (trái) và Preview Panel (phải)
- **Enhanced Preview Panel**: Thêm cột STT, Loại hình, Vận đơn, Số hóa đơn
- **Button Improvements**: Font in đậm, hiệu ứng hover rõ ràng với tk.Button
- **Smart Button States**: Nút "Dừng" và "Tải lại lỗi" có trạng thái chìm/nổi thông minh
- **Recent Companies Grid**: Layout 5 nút/hàng tránh chồng lấn khi hiển thị 10 MST

### 🎨 UI/UX Improvements
- **Responsive Layout**: Tự động điều chỉnh theo kích thước cửa sổ
- **Better Spacing**: Cải thiện khoảng cách giữa các nút (padx=5, width=14)
- **Color Consistency**: Text tư vấn hải quan dùng màu vàng sẫm (#d4a853)
- **Visual Feedback**: Trạng thái nút rõ ràng hơn với sunken/raised effects

### 🔧 Technical Improvements
- **Grid Layout**: Recent companies sử dụng grid thay vì pack để tránh overflow
- **Hover Effects**: Custom hover binding cho tk.Button với màu sắc phù hợp
- **State Management**: Cải thiện quản lý trạng thái nút với _is_sunken flag

## [1.2.6] - 2024-12-12

### Fixed
- Fixed version mismatch between main.py and branding.py causing update check to fail
- Fixed theme manager preserving branding colors when switching themes

### Changed
- Synchronized APP_VERSION across all modules

## [1.2.5] - 2024-12-12

### Changed
- Test version for auto-update feature verification - Customs Barcode Automation

## Version 1.2.4 - GitHub Auto-Update (December 12, 2024)

### ✨ New Features

#### 1. GitHub Auto-Update
- **Feature**: Tự động kiểm tra và tải cập nhật từ GitHub Releases
- **Implementation**:
  - Kiểm tra cập nhật tự động khi khởi động ứng dụng
  - Nút "Cập nhật" trong header để kiểm tra thủ công
  - Dialog hiển thị thông tin phiên bản mới và release notes
  - Tải xuống với progress bar và tốc độ download
  - Tùy chọn "Cài đặt ngay" hoặc "Cài đặt sau"
  - Tùy chọn "Bỏ qua phiên bản này" để không nhắc lại
- **Benefits**: Người dùng luôn được thông báo khi có phiên bản mới

#### 2. Version Comparator
- **Feature**: So sánh phiên bản theo semantic versioning (X.Y.Z)
- **Implementation**:
  - Hỗ trợ prefix "v" hoặc "V" (v1.2.3 = 1.2.3)
  - Xử lý lỗi khi format không hợp lệ

### 🔧 Technical Changes

**New Files**:
- `update/version_comparator.py` - So sánh phiên bản
- `update/update_checker.py` - Kiểm tra cập nhật từ GitHub API
- `update/download_manager.py` - Quản lý tải file
- `update/models.py` - Data models (UpdateInfo, DownloadProgress)
- `gui/update_dialog.py` - Các dialog UI cho update

**main.py**:
- Thêm APP_VERSION constant
- Kiểm tra cập nhật tự động khi khởi động (background thread)

**gui/customs_gui.py**:
- Thêm nút "Cập nhật" trong header
- Method `_check_for_updates()` để kiểm tra thủ công

**config.ini.sample**:
- Thêm section [Update] với github_repo, skipped_versions, pending_installer

### 🧪 Property-Based Tests
- 24 property tests mới cho update module
- Tests cho version comparison, GitHub response parsing, download progress, etc.

---

## Version 1.2.3 - Graceful Database Connection (December 11, 2024)

### ✨ New Features

#### 1. Graceful Startup Without Database Connection
- **Feature**: Application now starts even if database connection fails
- **Implementation**:
  - Application no longer exits when database connection fails at startup
  - Shows warning message instead of error and allows GUI to start
  - Users can configure database settings from GUI and reconnect
- **Benefits**: Better user experience, especially for first-time setup

#### 2. Database Reconnect from GUI
- **Feature**: "Lưu & Kết nối" button in Database Config dialog
- **Implementation**:
  - After saving database configuration, automatically attempts to reconnect
  - Updates database status indicator immediately
  - Shows success/failure message
- **Benefits**: No need to restart application after changing database settings

### 🔧 Technical Changes

**main.py**:
- Removed `sys.exit(1)` when database connection fails
- Application continues to initialize GUI even without database
- Shows warning message in console

**gui/customs_gui.py**:
- Renamed "Lưu" button to "Lưu & Kết nối" in database config dialog
- Added `save_and_reconnect()` function to save config and reconnect immediately
- Added `_update_db_status()` method to update database status indicator
- Database status updates in real-time after reconnection

---

## Version 1.2.2 - Settings Hot Reload Fix (December 11, 2024)

### 🐛 Bug Fixes

#### 1. Fixed Retrieval Method Not Applied Immediately (Critical)
- **Problem**: When changing barcode retrieval method (Auto/API/Web) in Settings dialog and clicking "Lưu", the new method was not applied until application restart
- **Root Cause**: `BarcodeRetriever` was initialized once at startup with the config value, and never updated when settings changed
- **Solution**: 
  - Added `set_retrieval_method()` method to `BarcodeRetriever` class for runtime updates
  - Added callback mechanism to `SettingsDialog` to notify when settings are saved
  - `CustomsAutomationGUI` now passes callback to update `BarcodeRetriever` immediately after settings save
- **Impact**: Settings changes now take effect immediately without requiring application restart

### 🔧 Technical Changes

**web_utils/barcode_retriever.py**:
- Added `set_retrieval_method(method: str)` method to update retrieval method at runtime
- Method validates input and resets failed method counters

**gui/settings_dialog.py**:
- Added `on_settings_changed` callback parameter to `__init__`
- `save_settings()` now calls callback after saving to config file
- Updated success message to indicate immediate application

**gui/customs_gui.py**:
- `_show_settings_dialog()` now creates callback function
- Callback updates both `BarcodeRetriever` and `FileManager` with new settings

---

## Version 1.2.1 - Container PDF Layout Fixes (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed Container PDF Layout Issues
- **Removed "- 2" indicator**: Removed redundant "- 2" text below "Hải quan Bắc Ninh" in header
- **Added complete notes section**: Added full notes for columns (1) and (2) including:
  - Hàng nhập khẩu: lấy từ Danh sách container do người khai hải quan gửi đến hệ thống
  - Hàng xuất khẩu: lấy từ tiêu chí "Số container" trên tờ khai xuất
  - Trường hợp thay đổi số container, công chức hải quan cập nhật vào hệ thống
- **Increased table size**: Enlarged container table to match original MV_container.pdf layout
- **Fixed SoSeal display**: Now displays "NA" in column (2) when seal value is "NA" instead of empty

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- Removed ptvc_indicator from container PDF header
- Added complete notes section with column (1) and (2) explanations
- Increased column widths and font sizes for better readability
- Changed SoSeal display logic to show "NA" value

---

## Version 1.2.0 - Container Barcode PDF Support (December 10, 2024)

### ✨ New Features

#### 1. Container Declaration PDF Support (MaPTVC = 2)
- **Feature**: Automatic detection and rendering of container declarations
- **Implementation**:
  - When MaPTVC = 2, system generates container-specific PDF layout
  - Title changes to "DANH SÁCH CONTAINER" instead of "DANH SÁCH HÀNG HÓA"
  - 6-column table: STT, SỐ HIỆU CONTAINER, SỐ SEAL CONTAINER, SỐ SEAL HẢI QUAN, XÁC NHẬN, MÃ VẠCH
  - QR code for each container decoded from BarcodeImage field (base64 PNG)
  - Multiple containers per declaration supported
- **Benefits**: Complete support for container cargo declarations

#### 2. Enhanced BangKe Parsing
- **Feature**: Full parsing of container data from API response
- **Implementation**:
  - Parse Table_BangKe elements with all fields: Stt, SoContainer, SoSeal, SoSealHQ, BarcodeImage, GhiChu
  - Automatic whitespace trimming for SoContainer and SoSeal
  - Handle "#####" SoSealHQ as empty value
- **Benefits**: Accurate container data extraction

### 🔧 Technical Changes

**qrcode_api_client.py**:
- Updated `ContainerInfo` dataclass with new fields: stt, so_seal_hq, barcode_image, ghi_chu
- Added `is_container_declaration` property to `ContainerDeclarationInfo`
- Enhanced `_parse_bang_ke()` to parse all container fields

**barcode_pdf_generator.py**:
- Added `_decode_qr_image()` method for base64 PNG decoding
- Added `_build_container_table()` method for 6-column container table
- Added `_build_container_content()` method for container PDF layout
- Updated `generate_pdf()` to route based on `is_container_declaration`
- Added `qr_code_size` config (2cm x 2cm)

### 🧪 Testing

**Property-Based Tests Added**:
- Property 1: Container Declaration Detection
- Property 2: PDF Layout Selection
- Property 3: Container Row Count
- Property 4: Seal Value Display
- Property 5: Base64 Image Decoding
- Property 6: BangKe Parsing Completeness
- Property 7: Whitespace Trimming

---

## Version 1.1.5 - PDF Layout Final Fix (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed "Hải quan Bắc Ninh" Centering (Critical)
- **Problem**: "Hải quan Bắc Ninh" was not properly centered under "Chi cục Hải quan khu vực V"
- **Solution**: 
  - Line 1 ("Chi cục Hải quan khu vực V"): LEFT aligned
  - Line 2 ("Hải quan Bắc Ninh"): CENTER aligned within the same fixed width (160pt)
  - Now uses dynamic values from API: `TenCucHaiQuan` and `TenChiCucHaiQuan`
- **Impact**: Header layout now matches ECUS PDF format exactly

#### 2. Fixed Long Text Wrapping for Item 1 (Critical)
- **Problem**: "1. Chi cục hải quan giám sát:" line was truncated, missing " - 1" at end
- **Solution**: Added `wordWrap='CJK'` to info style for proper text wrapping
- **Impact**: Long content now wraps to next line instead of being cut off

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- Header uses `TenCucHaiQuan` and `TenChiCucHaiQuan` from API response
- Line 1: LEFT aligned, Line 2: CENTER aligned in nested table
- Increased header_text_width to 160pt
- Added `wordWrap='CJK'` to info style for long text handling

---

## Version 1.1.4 - PDF Header Centering Fix (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed "Hải quan Bắc Ninh" Centering (Critical)
- **Problem**: "Hải quan Bắc Ninh" was still left-aligned, not properly centered under "Chi cục Hải quan khu vực V"
- **Solution**: Changed both header lines to use CENTER alignment within a fixed-width table (155pt)
- **Impact**: Both lines now visually centered and aligned properly

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- Changed header_line1 and header_line2 to use `header_bold_center` style
- Increased header_text_width from 145pt to 155pt
- Both lines now CENTER aligned in nested table

---

## Version 1.1.3 - PDF Bold Labels & Layout Fix (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed Bold Labels for Items 1-9 (Critical)
- **Problem**: Labels "1. Chi cục hải quan giám sát:", "2. Đơn vị XNK:", etc. were not bold
- **Solution**: Changed from `<b>` HTML tags to `<font name='Arial-Bold'>` tags for proper bold rendering
- **Impact**: All item labels (1-9) now display in bold font

#### 2. Fixed "Hải quan Bắc Ninh" Alignment (Updated)
- **Problem**: "Hải quan Bắc Ninh" was left-aligned, not centered under "Chi cục Hải quan khu vực V"
- **Solution**: Created nested table with fixed width (145pt) to properly center the second line
- **Impact**: "Hải quan Bắc Ninh" now centered within the width of "Chi cục Hải quan khu vực V"

#### 3. Fixed MaPTVC Value Display (Critical)
- **Problem**: The number at end of "1. Chi cục hải quan giám sát:" was using wrong field (IsContainer instead of MaPTVC)
- **Solution**: Changed from `is_container` to `ma_ptvc` (Mã phương tiện vận chuyển)
- **Example**: Now shows "CC HQ CK Sân bay QT Nội Bài - 01B1A02: CT DVHH NOI BAI NCTS - 1"
- **Impact**: Full content with correct MaPTVC value (- 1, - 2, - 3, etc.) now displays correctly

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- Changed `<b>` tags to `<font name='{self.font_bold}'>` for items 1-9
- Created nested table for header alignment with fixed width
- Changed from `is_container` to `ma_ptvc` for the number at end of Chi cục GS line

---

## Version 1.1.2 - PDF Layout & Open Folder Fix (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed Barcode Style to Match ECUS (Critical)
- **Problem**: Barcode had text below it and was too large compared to ECUS version
- **Solution**: 
  - Removed text below barcode (write_text=False)
  - Reduced barcode height from 25mm to 15mm
  - Reduced barcode width from 65mm to 50mm
  - Adjusted module_height from 20 to 12
- **Impact**: Barcode now matches ECUS style (no text, smaller size)

#### 2. Fixed "Chi cục Hải quan khu vực V" Not Bold
- **Problem**: Header text "Chi cục Hải quan khu vực V" was not bold
- **Solution**: Changed to use bold style for both header lines
- **Impact**: Header now matches ECUS PDF format

#### 3. Fixed Missing Địa Điểm Giám Sát Info (Critical)
- **Problem**: "1. Chi cục hải quan giám sát:" was truncated, missing địa điểm giám sát info
- **Solution**: Added MaDDGS and TenDDGS to display full location info
- **Example**: Now shows "CC HQ CK Sân bay QT Nội Bài - 01B1A02: CT DVHH NOI BAI NCTS-1"
- **Impact**: Full customs supervision location is now displayed

#### 4. Fixed "Mở" Button Not Opening Correct Folder
- **Problem**: "Mở" button in GUI and popup didn't open the selected output folder
- **Solution**: 
  - Changed from subprocess.run(["explorer", path]) to os.startfile(path) on Windows
  - Added path normalization with os.normpath()
  - Fixed customs_gui.py to get file_path from tracking database
  - Added fallback to open output directory if file not found
- **Impact**: "Mở" button now correctly opens the selected output folder

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- BarcodeRenderConfig: barcode_height 25mm → 15mm, barcode_width 65mm → 50mm
- _generate_barcode_image: write_text=False, module_height 20 → 12
- Header: Both "Chi cục Hải quan khu vực V" and "Hải quan Bắc Ninh" now bold
- Added chi_cuc_gs_full with MaDDGS and TenDDGS

**enhanced_manual_panel.py**:
- _open_output_directory: Changed to os.startfile() on Windows
- Added os.normpath() for path normalization

**customs_gui.py**:
- open_file_location: Now gets file_path from tracking database
- Added fallback to open output directory if file not found

---

## Version 1.1.1 - Barcode Height Fix (December 10, 2024)

### 🐛 Bug Fixes

#### 1. Fixed Barcode Height Issue (Critical)
- **Problem**: Barcode generated from API was compressed/shorter than web/ECUS version
- **Solution**: 
  - Increased barcode height from 20mm to 25mm
  - Increased barcode width from 60mm to 65mm
  - Increased module_height from 15 to 20
  - Increased module_width from 0.3 to 0.35
  - Added higher DPI (300) for better quality
- **Impact**: Barcode now matches the height and quality of web/ECUS version

#### 2. Fixed Barcode Missing in EXE Build (Critical)
- **Problem**: Barcode was completely missing (cut off) when running from CustomsAutomation.exe
- **Solution**:
  - Added explicit imports for barcode.code128 and barcode.code39 in PyInstaller spec
  - Added fallback import mechanism for Code128 class
  - Added PIL.ImageOps and PIL.ImageFilter to hidden imports
  - Added validation to check if barcode library is available
  - Added detailed logging for barcode generation debugging
- **Impact**: Barcode now renders correctly in both Python script and EXE build

### 🔧 Technical Changes

**barcode_pdf_generator.py**:
- BarcodeRenderConfig: barcode_height 20mm → 25mm, barcode_width 60mm → 65mm
- _generate_barcode_image: module_height 15 → 20, module_width 0.3 → 0.35
- Added fallback import for Code128 from barcode.codex
- Added barcode data validation before creating Image
- Added detailed debug logging

**customs_automation.spec**:
- Added 'barcode.code128' and 'barcode.code39' to hiddenimports
- Added 'PIL.ImageOps' and 'PIL.ImageFilter' to hiddenimports
- Added 'io' module to hiddenimports

---

## Version 1.1 - UI Enhancements (December 2024)

### ✨ New Features

#### 1. Settings Dialog (Requirement 1)
- **Feature**: New Settings dialog accessible from main GUI
- **Implementation**:
  - Added "⚙ Cài đặt" button next to "Cấu hình DB" button
  - Retrieval method dropdown: Auto, API, Web
  - PDF naming format dropdown: 3 options
  - Settings persist to config.ini
- **Benefits**: Configure barcode retrieval and PDF naming without editing config files

#### 2. Unified Company Panel (Requirement 2)
- **Feature**: Merged company management and date selection into single panel
- **Implementation**:
  - Combined "Quản lý công ty" and "Chọn khoảng thời gian" sections
  - Renamed to "Quản lý công ty & Thời gian"
  - Optimized layout: buttons → search → dropdown → dates
- **Benefits**: Streamlined workflow, reduced visual clutter

#### 3. Smart Company Search (Requirement 3)
- **Feature**: Intelligent search that filters and auto-selects companies
- **Implementation**:
  - Single search field for name or tax code
  - Real-time filtering as you type
  - Auto-select on exact match
  - Case-insensitive matching
- **Benefits**: Faster company selection, no scrolling through long lists

#### 4. Default Unchecked Declarations (Requirement 4)
- **Feature**: Declarations unchecked by default in preview
- **Implementation**:
  - Preview loads with all checkboxes unchecked
  - "Select All" checkbox to check all at once
  - Individual toggle for each declaration
  - Selection count display: "Đã chọn: X/Y tờ khai"
- **Benefits**: Manual selection prevents accidental processing

#### 5. PDF Naming Options (Requirement 5)
- **Feature**: Choose PDF filename format
- **Implementation**:
  - Three formats available:
    - Mã số thuế + Số tờ khai (default)
    - Số hóa đơn + Số tờ khai
    - Số vận đơn + Số tờ khai
  - Automatic fallback to tax_code format if field is empty
  - Configurable via Settings dialog
- **Benefits**: Organize PDFs according to your workflow needs

### 🔧 Configuration Changes

**New config.ini settings**:
```ini
[BarcodeService]
pdf_naming_format = tax_code  # Options: tax_code, invoice, bill_of_lading
```

### 📝 UI Changes

- Settings button added to control panel
- Unified company and date panel layout
- Smart search component with auto-select
- Preview panel shows unchecked declarations by default
- Selection counter in preview header

### 🧪 Testing

**Property-Based Tests Added**:
- Property 1: Config Persistence Round-Trip (Retrieval Method)
- Property 2: Config Persistence Round-Trip (PDF Naming)
- Property 3: Smart Search Filtering
- Property 4: Smart Search Auto-Select
- Property 5: Default Unchecked State
- Property 6: Select All Behavior
- Property 7: Individual Toggle Behavior
- Property 8: PDF Filename Generation

**Unit Tests Added**:
- SettingsDialog creation and save functionality
- SmartCompanySearch filtering and auto-select
- PdfNamingService filename generation
- Unified panel layout verification

### 🔄 Migration Guide

**For existing users**:
1. Update to V1.1
2. Open Settings dialog to configure new options
3. Existing config.ini settings are preserved
4. New settings use sensible defaults

**No data migration required** - All existing data remains compatible.

---

## Version 2.1 - Bug Fixes and Performance Improvements (December 2024)

### 🐛 Bug Fixes

#### 1. Fixed API Timeout and Selector Robustness (P0 - Critical)
- **Problem**: API calls timing out after 30 seconds, form fields not found due to website changes
- **Solution**: 
  - Reduced API timeout from 30s to 10s for faster failure detection
  - Implemented adaptive selector system with multiple variations for each field
  - Added HTML structure logging on selector failure for debugging
  - Implemented selector caching with 24-hour expiry
- **Impact**: 67% faster timeout detection, more reliable barcode retrieval
- **Requirements**: 2.1, 2.2, 2.3, 2.4, 2.5

#### 2. Fixed Duplicate Declarations in Preview (P0 - Critical)
- **Problem**: Same declaration appearing multiple times in preview list
- **Solution**:
  - Updated database query to use DISTINCT on declaration number
  - Added GROUP BY clause on SO_TOKHAI, MA_DV, NGAY_DK, MA_HQ
  - Implemented duplicate detection validation
- **Impact**: Each declaration now appears only once in preview
- **Requirements**: 3.1, 3.2, 3.3, 3.4, 3.5

#### 3. Optimized Download Performance (P1 - High Priority)
- **Problem**: Downloads taking too long, especially for large batches
- **Solution**:
  - Implemented HTTP session reuse with connection pooling
  - Reduced retry attempts from 3 to 1
  - Added method skipping for consistently failing methods
  - Configured HTTPAdapter with max_retries=1, pool_connections=10
- **Impact**: Significantly faster batch processing, less time wasted on failures
- **Requirements**: 6.1, 6.2, 6.3, 6.4, 6.5

### ✨ New Features

#### 4. Calendar Date Picker (P2 - Medium Priority)
- **Feature**: Visual calendar widget for date selection
- **Implementation**:
  - Replaced text Entry with tkcalendar DateEntry widget
  - Configured date format DD/MM/YYYY with Vietnamese locale
  - Added date format validation
- **Benefits**: Faster date selection, no typing errors, automatic format validation
- **Requirements**: 4.1, 4.2, 4.3, 4.4, 4.5

#### 5. Searchable Company Dropdown (P2 - Medium Priority)
- **Feature**: Real-time search/filter in company dropdown
- **Implementation**:
  - Made combobox editable to allow typing
  - Implemented real-time filtering on keypress
  - Filter by both tax code and company name (case-insensitive)
  - Show "Không tìm thấy" when no matches
- **Benefits**: Fast company lookup, no scrolling through long lists
- **Requirements**: 5.1, 5.2, 5.3, 5.4, 5.5

#### 6. Output Directory Selection UI (P3 - Low Priority)
- **Feature**: UI for selecting output directory
- **Implementation**:
  - Added output directory display and browse button
  - Implemented directory selection dialog
  - Save selected directory to config
  - Load directory from config on startup
- **Benefits**: No need to edit config.ini, change output location on the fly
- **Requirements**: 1.1, 1.2, 1.3, 1.4, 1.5

### 🚀 Performance Improvements

**API and Web Scraping**:
- API timeout: 30s → 10s (67% faster)
- Web timeout: Added separate 15s timeout
- Max retries: 3 → 1 (faster failure handling)
- Session reuse: Enabled for batch processing

**Selector System**:
- Multiple selector variations per field
- Automatic fallback to alternative selectors
- Selector caching for reuse
- ~80% reduction in selector attempts

**Overall Impact**:
- Average retrieval time: ~5-10 seconds per declaration
- Better success rate with adaptive selectors
- Faster batch processing with session reuse
- Less waiting time for users

### 🔧 Configuration Changes

**New config.ini settings**:
```ini
[BarcodeService]
api_timeout = 10          # Reduced from 30
web_timeout = 15          # New setting
max_retries = 1           # Reduced from 3
session_reuse = true      # New setting
output_path = C:\CustomsData\Barcodes  # New setting
```

**New dependencies**:
```
tkcalendar>=1.6.1  # For calendar date picker
```

### 📝 Breaking Changes

**None** - All changes are backward compatible. Old config files will use default values.

### 🧪 Testing

**Property-Based Tests Added**:
- Property 1: Output directory persistence
- Property 2: Timeout reduction effectiveness
- Property 3: Selector fallback completeness
- Property 4: Declaration uniqueness
- Property 5: Date format consistency
- Property 6: Company filter correctness
- Property 7: Session reuse efficiency

**Unit Tests Updated**:
- BarcodeRetriever: Adaptive selectors, timeout, session reuse
- PreviewManager: Duplicate prevention, unique declarations
- EnhancedManualPanel: Date picker, company filter, output directory

### 📚 Documentation Updates

- Updated USER_GUIDE.md with new features
- Updated FEATURES_GUIDE.md with Enhanced Manual Mode improvements
- Added troubleshooting for new features
- Updated configuration examples

### 🔄 Migration Guide

**For existing users**:
1. Update dependencies: `pip install -r requirements.txt`
2. Update config.ini with new settings (optional, defaults will be used)
3. Restart application
4. Test with small batch first
5. Monitor logs for any issues

**No data migration required** - All existing data remains compatible.

### 🙏 Acknowledgments

Thanks to all users who reported these issues and provided feedback during testing.

---

## Version 2.0 - Enhanced Features

### Các tính năng mới:

#### 1. Hiển thị trạng thái kết nối Database
- Hiển thị trạng thái kết nối đến cơ sở dữ liệu ECUS5VNACC trong thời gian thực
- Tự động kiểm tra kết nối khi khởi động ứng dụng
- Màu sắc trực quan: Xanh (Connected), Đỏ (Disconnected), Cam (Checking)

#### 2. Tối ưu hóa số ngày quét
- **Chế độ Automatic**: Tự động quét 3 ngày gần nhất (giảm từ 7 ngày)
- **Chế độ Manual**: Cho phép cấu hình số ngày quét từ 1-90 ngày

#### 3. Quản lý danh sách công ty
- Tự động lưu trữ tên công ty và mã số thuế từ các tờ khai đã xử lý
- Hiển thị danh sách công ty trong dropdown để lọc nhanh
- Tự động cập nhật danh sách công ty khi phát hiện công ty mới

#### 4. Lọc theo công ty (Manual Mode)
- Cho phép chọn công ty cụ thể để chỉ lấy mã vạch của công ty đó
- Hỗ trợ tìm kiếm công ty theo tên hoặc mã số thuế
- Tùy chọn "Tất cả công ty" để quét toàn bộ

#### 5. Thanh tiến trình chi tiết
- Hiển thị tiến trình xử lý theo thời gian thực
- Thông báo từng bước: Đang truy vấn, đang lọc, đang xử lý
- Hiển thị số tờ khai đang xử lý (ví dụ: "Đang xử lý tờ khai 5/20")
- Thông báo kết quả cuối cùng

### Sửa lỗi:

#### 1. Lỗi kết nối Database
- Cải thiện xử lý lỗi khi kết nối database thất bại
- Thêm thông báo lỗi chi tiết hơn
- Tự động retry khi mất kết nối

#### 2. Lỗi query declarations
- Sửa lỗi "Failed to query declarations" khi chạy manual mode
- Thêm hỗ trợ filter theo tax_code trong SQL query
- Cải thiện error handling

### Cải tiến giao diện:

1. **Manual Mode Settings Panel**
   - Gom nhóm các cài đặt cho chế độ manual
   - Dễ dàng cấu hình số ngày và công ty cần quét

2. **Progress Bar**
   - Thanh tiến trình trực quan
   - Label hiển thị trạng thái chi tiết

3. **Database Status Indicator**
   - Hiển thị ngay trên control panel
   - Cập nhật real-time

### Cách sử dụng các tính năng mới:

#### Chế độ Automatic:
1. Chọn "Automatic" mode
2. Nhấn "Start"
3. Hệ thống sẽ tự động quét 3 ngày gần nhất mỗi 5 phút

#### Chế độ Manual với lọc công ty:
1. Chọn "Manual" mode
2. Cấu hình "Số ngày quét" (ví dụ: 7, 15, 30 ngày)
3. Chọn công ty từ dropdown hoặc chọn "Tất cả công ty"
4. Nhấn "Run Once"
5. Theo dõi tiến trình trên thanh progress bar

#### Quản lý danh sách công ty:
- Danh sách công ty tự động cập nhật sau mỗi lần quét
- Nhấn "Làm mới" để reload danh sách công ty
- Công ty được lưu với format: "Tên Công Ty (Mã số thuế)"

### Yêu cầu kỹ thuật:

- Python 3.8+
- Tất cả dependencies trong requirements.txt
- Kết nối đến ECUS5 SQL Server database
- ODBC Driver for SQL Server

### Lưu ý:

- Chế độ automatic giờ chỉ quét 3 ngày để tối ưu hiệu suất
- Nếu cần quét nhiều ngày hơn, sử dụng chế độ manual
- Danh sách công ty được lưu trong tracking database (data/tracking.db)
