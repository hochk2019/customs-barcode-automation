# Enhanced Manual Mode - Testing Checklist

## Tổng quan
Tất cả các tasks trong Enhanced Manual Mode spec đã hoàn thành (100%). Document này cung cấp checklist để kiểm thử toàn diện.

## ✅ Trạng thái Implementation

### Core Components
- [x] CompanyScanner (processors/company_scanner.py)
- [x] PreviewManager (processors/preview_manager.py)
- [x] EnhancedManualPanel (gui/enhanced_manual_panel.py)
- [x] Database extensions (EcusConnector, TrackingDatabase)

### Tests
- [x] Unit tests (test_company_scanner_unit.py, test_preview_manager_unit.py, test_enhanced_manual_panel_unit.py)
- [x] Property-based tests (test_company_scanner_properties.py, test_preview_manager_properties.py, test_enhanced_manual_panel_properties.py)
- [x] Integration tests (test_preview_workflow_integration.py)

### Documentation
- [x] USER_GUIDE.md - Enhanced Manual Mode section
- [x] WHATS_NEW.md - New features documentation
- [x] FEATURES_GUIDE.md - Detailed tutorials and troubleshooting

---

## 🧪 Checklist Kiểm Thử

### A. Kiểm tra môi trường

#### A1. Database Connection
```bash
python test_db_connection.py
```
- [ ] Kết nối thành công đến ECUS5 database
- [ ] Tracking database (data/tracking.db) tồn tại
- [ ] Có quyền truy cập bảng DaiLy_DoanhNghiep

#### A2. Dependencies
```bash
pip list | findstr "tkinter\|tkcalendar\|hypothesis"
```
- [ ] tkinter có sẵn
- [ ] tkcalendar đã cài đặt
- [ ] hypothesis đã cài đặt (cho property tests)

---

### B. Chạy Automated Tests

#### B1. Unit Tests
```bash
pytest tests/test_company_scanner_unit.py -v
pytest tests/test_preview_manager_unit.py -v
pytest tests/test_enhanced_manual_panel_unit.py -v
```
**Kết quả mong đợi:**
- [ ] Tất cả unit tests pass
- [ ] Không có warnings nghiêm trọng

#### B2. Property-Based Tests
```bash
pytest tests/test_company_scanner_properties.py -v
pytest tests/test_preview_manager_properties.py -v
pytest tests/test_enhanced_manual_panel_properties.py -v
```
**Kết quả mong đợi:**
- [ ] Property 1: Company scan completeness - PASS
- [ ] Property 2: Date range validation - PASS
- [ ] Property 3: Preview accuracy - PASS
- [ ] Property 4: Selection consistency - PASS
- [ ] Property 5: Stop operation safety - PASS

#### B3. Integration Tests
```bash
pytest tests/test_preview_workflow_integration.py -v
```
**Kết quả mong đợi:**
- [ ] End-to-end workflow tests pass
- [ ] Preview workflow integration pass

---

### C. Manual Testing - GUI

#### C1. Khởi động ứng dụng
```bash
python main.py
```
**Kiểm tra:**
- [ ] Ứng dụng khởi động không lỗi
- [ ] GUI hiển thị đầy đủ
- [ ] DB Status hiển thị "Connected"
- [ ] Enhanced Manual Mode panel hiển thị

---

### D. Workflow 1: Company Scanning

#### D1. Quét công ty lần đầu (Database trống)
**Các bước:**
1. [ ] Nhấn nút "Quét công ty"
2. [ ] Quan sát thanh tiến trình
3. [ ] Đợi hoàn thành

**Kết quả mong đợi:**
- [ ] Hiển thị "Đang quét công ty..."
- [ ] Thanh tiến trình chạy
- [ ] Hiển thị "Đã quét và lưu X công ty"
- [ ] Dropdown "Lọc theo công ty" có danh sách công ty
- [ ] Format: "Tên Công Ty (Mã số thuế)"

#### D2. Làm mới danh sách công ty
**Các bước:**
1. [ ] Nhấn nút "Làm mới"

**Kết quả mong đợi:**
- [ ] Dropdown reload danh sách
- [ ] Không có lỗi

#### D3. Tìm kiếm công ty
**Các bước:**
1. [ ] Click vào dropdown
2. [ ] Gõ tên công ty hoặc mã số thuế

**Kết quả mong đợi:**
- [ ] Tìm kiếm hoạt động
- [ ] Hiển thị kết quả phù hợp

---

### E. Workflow 2: Date Range Selection

#### E1. Validation - Ngày bắt đầu trong tương lai
**Các bước:**
1. [ ] Chọn "Từ ngày" là ngày mai
2. [ ] Chọn "Đến ngày" hợp lệ
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Hiển thị lỗi: "Ngày bắt đầu không được là tương lai"
- [ ] Không cho phép xem trước

#### E2. Validation - Ngày kết thúc trước ngày bắt đầu
**Các bước:**
1. [ ] Chọn "Từ ngày": 10/12/2024
2. [ ] Chọn "Đến ngày": 05/12/2024
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Hiển thị lỗi: "Ngày kết thúc không được trước ngày bắt đầu"
- [ ] Không cho phép xem trước

#### E3. Warning - Khoảng thời gian > 90 ngày
**Các bước:**
1. [ ] Chọn "Từ ngày": 01/09/2024
2. [ ] Chọn "Đến ngày": 08/12/2024
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Hiển thị cảnh báo: "Khoảng thời gian > 90 ngày"
- [ ] Vẫn cho phép xem trước

#### E4. Valid date range
**Các bước:**
1. [ ] Chọn "Từ ngày": 01/12/2024
2. [ ] Chọn "Đến ngày": 08/12/2024
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Không có lỗi
- [ ] Tiến hành xem trước

---

### F. Workflow 3: Declaration Preview

#### F1. Preview với "Tất cả công ty"
**Các bước:**
1. [ ] Chọn "Lọc theo công ty": "Tất cả công ty"
2. [ ] Chọn khoảng thời gian hợp lệ (7 ngày)
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Hiển thị "Đang truy vấn..."
- [ ] Nút "Hủy" xuất hiện
- [ ] Bảng preview hiển thị tờ khai
- [ ] Các cột: Checkbox, Số tờ khai, Mã số thuế, Ngày
- [ ] Hiển thị "Đã chọn: 0/X tờ khai"

#### F2. Preview với công ty cụ thể
**Các bước:**
1. [ ] Chọn một công ty cụ thể từ dropdown
2. [ ] Chọn khoảng thời gian hợp lệ
3. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Chỉ hiển thị tờ khai của công ty đó
- [ ] Mã số thuế trong bảng khớp với công ty đã chọn

#### F3. Preview không có kết quả
**Các bước:**
1. [ ] Chọn khoảng thời gian không có tờ khai (ví dụ: 1 năm trước)
2. [ ] Nhấn "Xem trước"

**Kết quả mong đợi:**
- [ ] Hiển thị "Không tìm thấy tờ khai nào"
- [ ] Bảng preview trống

#### F4. Hủy preview
**Các bước:**
1. [ ] Chọn khoảng thời gian lớn (90 ngày)
2. [ ] Nhấn "Xem trước"
3. [ ] Ngay lập tức nhấn "Hủy"

**Kết quả mong đợi:**
- [ ] Query dừng lại
- [ ] Hiển thị "Đã hủy xem trước"
- [ ] Trở về trạng thái nhập liệu

---

### G. Workflow 4: Selection Logic

#### G1. Chọn từng tờ khai
**Các bước:**
1. [ ] Xem trước để có danh sách tờ khai
2. [ ] Click checkbox của 3 tờ khai bất kỳ

**Kết quả mong đợi:**
- [ ] Checkbox được tích: ☑
- [ ] Số đếm cập nhật: "Đã chọn: 3/X tờ khai"
- [ ] Nút "Lấy mã vạch" được enable

#### G2. Chọn tất cả
**Các bước:**
1. [ ] Xem trước để có danh sách tờ khai
2. [ ] Click checkbox "Chọn tất cả"

**Kết quả mong đợi:**
- [ ] Tất cả checkbox được tích
- [ ] Số đếm: "Đã chọn: X/X tờ khai"
- [ ] Nút "Lấy mã vạch" được enable

#### G3. Bỏ chọn tất cả
**Các bước:**
1. [ ] Sau khi chọn tất cả
2. [ ] Click lại checkbox "Chọn tất cả"

**Kết quả mong đợi:**
- [ ] Tất cả checkbox bị bỏ tích
- [ ] Số đếm: "Đã chọn: 0/X tờ khai"
- [ ] Nút "Lấy mã vạch" bị disable

---

### H. Workflow 5: Selective Download

#### H1. Download tờ khai đã chọn
**Các bước:**
1. [ ] Xem trước và chọn 5 tờ khai
2. [ ] Nhấn "Lấy mã vạch"

**Kết quả mong đợi:**
- [ ] Hiển thị thanh tiến trình
- [ ] Hiển thị "Đang xử lý X/5: [số tờ khai]"
- [ ] Nút "Dừng" xuất hiện
- [ ] Tất cả inputs bị disable
- [ ] Sau khi hoàn thành: "Hoàn thành: X thành công, Y lỗi"

#### H2. Dừng download giữa chừng
**Các bước:**
1. [ ] Xem trước và chọn 20 tờ khai
2. [ ] Nhấn "Lấy mã vạch"
3. [ ] Khi đang xử lý tờ khai thứ 5, nhấn "Dừng"

**Kết quả mong đợi:**
- [ ] Tờ khai thứ 5 hoàn thành
- [ ] Dừng xử lý các tờ khai còn lại
- [ ] Hiển thị: "Đã dừng: 5 thành công, 15 còn lại"
- [ ] 5 tờ khai đã xử lý được lưu
- [ ] Tất cả controls được enable lại

#### H3. Download với lỗi
**Các bước:**
1. [ ] Ngắt kết nối mạng
2. [ ] Chọn và download tờ khai

**Kết quả mong đợi:**
- [ ] Hiển thị lỗi cho từng tờ khai thất bại
- [ ] Tiếp tục xử lý các tờ khai khác
- [ ] Tổng kết: "X thành công, Y lỗi"
- [ ] Xem logs để biết chi tiết lỗi

---

### I. Workflow States

#### I1. State 1 - Initial
**Kiểm tra:**
- [ ] Chỉ nút "Quét công ty" enabled
- [ ] Tất cả controls khác disabled
- [ ] Hiển thị "Vui lòng quét công ty trước"

#### I2. State 2 - Companies Loaded
**Kiểm tra:**
- [ ] Dropdown công ty enabled
- [ ] Date pickers enabled
- [ ] Nút "Xem trước" enabled (khi đã chọn công ty và dates)

#### I3. State 3 - Preview Displayed
**Kiểm tra:**
- [ ] Bảng preview hiển thị
- [ ] Checkboxes hoạt động
- [ ] Nút "Lấy mã vạch" enabled (khi có tờ khai được chọn)

#### I4. State 4 - Downloading
**Kiểm tra:**
- [ ] Tất cả inputs disabled
- [ ] Nút "Dừng" hiển thị
- [ ] Thanh tiến trình cập nhật

#### I5. State 5 - Complete
**Kiểm tra:**
- [ ] Tất cả controls enabled lại
- [ ] Hiển thị kết quả
- [ ] Có thể bắt đầu workflow mới

---

### J. Error Handling

#### J1. Database disconnect
**Các bước:**
1. [ ] Stop SQL Server
2. [ ] Thử quét công ty hoặc xem trước

**Kết quả mong đợi:**
- [ ] Hiển thị lỗi kết nối database
- [ ] Không crash ứng dụng
- [ ] Có thể retry sau khi reconnect

#### J2. Network failure
**Các bước:**
1. [ ] Ngắt kết nối mạng
2. [ ] Thử download mã vạch

**Kết quả mong đợi:**
- [ ] Hiển thị lỗi network
- [ ] Tiếp tục xử lý các tờ khai khác
- [ ] Logs ghi lại lỗi

#### J3. Invalid data
**Các bước:**
1. [ ] Nhập ngày không hợp lệ (nếu có thể)

**Kết quả mong đợi:**
- [ ] Validation bắt lỗi
- [ ] Hiển thị thông báo lỗi rõ ràng

---

### K. Performance Testing

#### K1. Large dataset
**Các bước:**
1. [ ] Chọn khoảng thời gian 90 ngày
2. [ ] Chọn "Tất cả công ty"
3. [ ] Xem trước

**Kết quả mong đợi:**
- [ ] Preview load trong thời gian chấp nhận được (< 30s)
- [ ] UI không bị đơ
- [ ] Có thể hủy nếu quá lâu

#### K2. Many companies
**Các bước:**
1. [ ] Quét công ty với database có > 100 công ty

**Kết quả mong đợi:**
- [ ] Quét hoàn thành trong thời gian hợp lý
- [ ] Dropdown hiển thị đầy đủ
- [ ] Tìm kiếm vẫn hoạt động tốt

---

### L. Integration với existing features

#### L1. Automatic Mode vẫn hoạt động
**Các bước:**
1. [ ] Chuyển sang Automatic Mode
2. [ ] Start scheduler

**Kết quả mong đợi:**
- [ ] Automatic Mode hoạt động bình thường
- [ ] Không bị ảnh hưởng bởi Enhanced Manual Mode

#### L2. Old Manual Mode vẫn hoạt động
**Các bước:**
1. [ ] Sử dụng Manual Mode cũ (nếu còn)
2. [ ] Chọn số ngày và Run Once

**Kết quả mong đợi:**
- [ ] Manual Mode cũ vẫn hoạt động
- [ ] Backward compatibility được duy trì

---

## 📊 Test Results Summary

### Automated Tests
- Unit Tests: _____ / _____ passed
- Property Tests: _____ / _____ passed
- Integration Tests: _____ / _____ passed

### Manual Tests
- Company Scanning: _____ / _____ passed
- Date Range Selection: _____ / _____ passed
- Declaration Preview: _____ / _____ passed
- Selection Logic: _____ / _____ passed
- Selective Download: _____ / _____ passed
- Workflow States: _____ / _____ passed
- Error Handling: _____ / _____ passed
- Performance: _____ / _____ passed
- Integration: _____ / _____ passed

### Overall Status
- [ ] All tests passed - Ready for production
- [ ] Some tests failed - Need fixes
- [ ] Major issues found - Need rework

---

## 🐛 Issues Found

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| 1  |          |             |        |
| 2  |          |             |        |
| 3  |          |             |        |

---

## 📝 Notes

### Testing Environment
- OS: Windows
- Python Version: _______
- Database: ECUS5 (SQL Server)
- Test Date: _______
- Tester: _______

### Additional Comments
_______________________________________
_______________________________________
_______________________________________

