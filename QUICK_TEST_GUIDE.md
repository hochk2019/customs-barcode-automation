# Quick Test Guide - Enhanced Manual Mode

## 🚀 Bắt đầu kiểm thử nhanh (5 phút)

### Bước 1: Kiểm tra môi trường (30 giây)
```bash
# Kiểm tra database connection
python test_db_connection.py
```
✅ Phải thấy: "Connection successful"

### Bước 2: Chạy automated tests (2 phút)
```bash
# Chạy tất cả tests
pytest tests/test_company_scanner_unit.py tests/test_preview_manager_unit.py tests/test_enhanced_manual_panel_unit.py -v
```
✅ Phải thấy: All tests passed

### Bước 3: Khởi động ứng dụng (10 giây)
```bash
python main.py
```
✅ Phải thấy: GUI hiển thị, DB Status = "Connected"

### Bước 4: Test workflow cơ bản (2 phút)

#### 4.1. Quét công ty
1. Nhấn nút **"Quét công ty"**
2. Đợi hoàn thành
3. ✅ Phải thấy: "Đã quét và lưu X công ty"

#### 4.2. Xem trước tờ khai
1. Chọn công ty từ dropdown (hoặc "Tất cả công ty")
2. Chọn "Từ ngày": 7 ngày trước
3. Chọn "Đến ngày": Hôm nay
4. Nhấn **"Xem trước"**
5. ✅ Phải thấy: Bảng hiển thị danh sách tờ khai

#### 4.3. Chọn và download
1. Tích checkbox của 2-3 tờ khai
2. ✅ Phải thấy: "Đã chọn: 3/X tờ khai"
3. Nhấn **"Lấy mã vạch"**
4. ✅ Phải thấy: Thanh tiến trình, "Đang xử lý..."
5. Đợi hoàn thành
6. ✅ Phải thấy: "Hoàn thành: X thành công, Y lỗi"

### ✅ Kết quả
Nếu tất cả các bước trên hoạt động → **Enhanced Manual Mode đã sẵn sàng!**

---

## 🧪 Test chi tiết (30 phút)

Sử dụng checklist đầy đủ trong: **`TESTING_CHECKLIST.md`**

---

## 📚 Tài liệu tham khảo

- **Hướng dẫn sử dụng**: `USER_GUIDE.md` - Section "Enhanced Manual Mode"
- **Hướng dẫn chi tiết**: `FEATURES_GUIDE.md` - Section 7
- **Checklist đầy đủ**: `TESTING_CHECKLIST.md`
- **Tổng kết hoàn thành**: `ENHANCED_MANUAL_MODE_COMPLETION_SUMMARY.md`

---

## 🐛 Nếu gặp lỗi

1. Xem `logs/app.log`
2. Kiểm tra `FEATURES_GUIDE.md` - Section "Troubleshooting"
3. Chạy lại `python test_db_connection.py`

---

## ✨ Các tính năng chính cần test

- [x] Quét công ty
- [x] Chọn khoảng thời gian
- [x] Xem trước tờ khai
- [x] Chọn lọc tờ khai
- [x] Download có chọn lọc
- [x] Dừng download giữa chừng
- [x] Validation ngày tháng
- [x] Hủy preview

**Tất cả đã implement và test! ✅**
