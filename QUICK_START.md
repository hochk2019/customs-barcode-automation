# Quick Start Guide - Customs Barcode Automation v2.0

## Bước 1: Kiểm tra kết nối Database

Trước khi chạy ứng dụng, test kết nối database:

```bash
python test_db_connection.py
```

Nếu thành công, bạn sẽ thấy:
```
✓ ALL TESTS PASSED
```

Nếu thất bại, kiểm tra:
- SQL Server đang chạy
- Thông tin trong config.ini đúng
- ODBC Driver đã cài đặt

## Bước 2: Chạy ứng dụng

```bash
python main.py
```

## Bước 3: Kiểm tra trạng thái

Sau khi ứng dụng mở, kiểm tra:
- **Status**: Hiển thị trạng thái ứng dụng
- **DB**: Phải hiển thị "● Connected" (màu xanh)

Nếu DB hiển thị "● Disconnected", xem lại Bước 1.

## Bước 4: Chọn chế độ hoạt động

### Chế độ Automatic (Khuyến nghị cho sử dụng hàng ngày)
1. Chọn radio button "Automatic"
2. Nhấn "Start"
3. Hệ thống sẽ tự động quét 3 ngày gần nhất mỗi 5 phút

### Chế độ Manual (Cho trường hợp đặc biệt)
1. Chọn radio button "Manual"
2. Cấu hình:
   - **Số ngày quét**: Nhập số ngày (1-90)
   - **Lọc theo công ty**: Chọn công ty hoặc "Tất cả công ty"
3. Nhấn "Run Once"
4. Theo dõi thanh tiến trình

## Bước 5: Theo dõi kết quả

### Statistics Panel
- **Declarations Processed**: Tổng số tờ khai đã xử lý
- **Barcodes Retrieved**: Số mã vạch lấy thành công
- **Errors**: Số lỗi
- **Last Run**: Lần chạy cuối cùng

### Processed Declarations
- Danh sách tất cả tờ khai đã xử lý
- Có thể search theo số tờ khai hoặc mã số thuế
- Chọn và re-download nếu cần

### Recent Logs
- Hiển thị log real-time
- Màu sắc: INFO (đen), WARNING (cam), ERROR (đỏ)

## Các tính năng nổi bật v2.0

### 1. Trạng thái Database Real-time
```
Status: ● Running  |  DB: ● Connected
```

### 2. Cấu hình linh hoạt (Manual Mode)
```
Số ngày quét: [7] ngày
Lọc theo công ty: [Chọn công ty ▼]
```

### 3. Thanh tiến trình chi tiết
```
[▓▓▓▓▓▓░░░░] Đang xử lý tờ khai 15/25: 105/12345678
```

### 4. Quản lý công ty tự động
- Tự động lưu tên công ty từ tờ khai
- Dropdown để lọc nhanh
- Nút "Làm mới" để cập nhật

## Use Cases phổ biến

### Use Case 1: Sử dụng hàng ngày
```
Mode: Automatic → Start
```
Hệ thống tự động quét 3 ngày gần nhất mỗi 5 phút.

### Use Case 2: Quét lại tờ khai tuần trước
```
Mode: Manual
Số ngày quét: 7
Lọc theo công ty: Tất cả công ty
→ Run Once
```

### Use Case 3: Lấy tờ khai của công ty ABC trong tháng
```
Mode: Manual
Số ngày quét: 30
Lọc theo công ty: CÔNG TY ABC (0123456789)
→ Run Once
```

### Use Case 4: Tải lại mã vạch bị lỗi
```
1. Tìm tờ khai trong "Processed Declarations"
2. Chọn các tờ khai cần tải lại
3. Nhấn "Re-download Selected"
```

## Troubleshooting nhanh

### Vấn đề: DB Disconnected
```bash
# Chạy test
python test_db_connection.py

# Kiểm tra config
notepad config.ini
```

### Vấn đề: Không tìm thấy tờ khai
- Tăng số ngày quét
- Chọn "Tất cả công ty"
- Kiểm tra database có dữ liệu

### Vấn đề: Lỗi khi Run Once
- Xem "Recent Logs" để biết chi tiết
- Kiểm tra DB Status
- Restart ứng dụng

## Tips

1. **Automatic mode** cho hoạt động hàng ngày (3 ngày)
2. **Manual mode** khi cần quét nhiều ngày hoặc công ty cụ thể
3. Backup file `data/tracking.db` định kỳ
4. Kiểm tra logs nếu có vấn đề: `logs/app.log`
5. Không quét quá 90 ngày cùng lúc

## Tài liệu chi tiết

- **FEATURES_GUIDE.md**: Hướng dẫn chi tiết từng tính năng
- **CHANGELOG.md**: Danh sách thay đổi và cải tiến
- **USER_GUIDE.md**: Hướng dẫn sử dụng đầy đủ
- **BUILD.md**: Hướng dẫn build executable

## Phím tắt

Hiện tại không có phím tắt. Sử dụng chuột để thao tác.

## Yêu cầu hệ thống

- Windows 7/10/11
- Python 3.8+
- SQL Server 2008 R2+
- ODBC Driver for SQL Server
- Kết nối mạng đến ECUS5 database

## Cài đặt

```bash
# Cài đặt dependencies
.\install.ps1

# Hoặc
pip install -r requirements.txt

# Copy config mẫu
copy config.ini.sample config.ini

# Chỉnh sửa config
notepad config.ini
```

## Chạy

```bash
# Chạy từ source
python main.py

# Hoặc build executable
.\build_exe.ps1
.\dist\customs_automation.exe
```

---

**Chúc bạn sử dụng hiệu quả!**

Nếu cần hỗ trợ, xem file FEATURES_GUIDE.md hoặc liên hệ bộ phận IT.
