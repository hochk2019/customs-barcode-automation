# 🚀 HƯỚNG DẪN SỬ DỤNG NHANH - Customs Barcode Automation v1.5.3

## 📋 Bước 1: Chuẩn Bị File Cấu Hình

**Lần đầu sử dụng**, bạn cần tạo file cấu hình:

1. **Đổi tên** file `config.ini.sample` thành `config.ini`
2. **Mở** file `config.ini` bằng Notepad
3. **Sửa** thông tin database theo hướng dẫn bên dưới

---

## 📋 Bước 2: Cấu Hình Database

Mở file `config.ini` và sửa phần `[Database]`:

```ini
[Database]
server = TÊN_SERVER_CỦA_BẠN     ; Ví dụ: 192.168.1.100 hoặc localhost
database = ECUS5VNACCS          ; Ví dụ: ECUS5VNACCS hoặc đổi thành tên database của bạn
username = sa                   ; Tài khoản SQL Server
password = MẬT_KHẨU_CỦA_BẠN     ; Mật khẩu SQL Server
timeout = 30
```

**Lưu file** sau khi sửa.

---

## 📋 Bước 3: Khởi Động Ứng Dụng

1. **Double-click** file `CustomsAutomation.exe`
2. Nếu kết nối database thành công, bạn sẽ thấy:
   - Status bar hiển thị **"DB: ● Connected"**
3. Nếu lỗi kết nối:
   - Click nút **"Cấu hình DB"** để sửa thông tin
   - Nhấn **"Kiểm tra kết nối"** để test
   - Nhấn **"Lưu & Kết nối lại"**

---

## 🎯 Các Chức Năng Chính

### 1. Lấy Mã Vạch Tờ Khai

| Bước | Thao tác |
|------|----------|
| 1 | Click **"Quét công ty"** để lấy danh sách công ty |
| 2 | Chọn công ty từ dropdown hoặc nút công ty gần đây |
| 3 | Chọn **"Từ ngày"** và **"Đến ngày"** |
| 4 | Click **"Xem trước"** để hiển thị tờ khai |
| 5 | Tick chọn tờ khai cần lấy mã vạch |
| 6 | Click **"Lấy mã vạch"** |

### 2. Theo Dõi Thông Quan Tự Động

| Bước | Thao tác |
|------|----------|
| 1 | Chuyển sang tab **"Theo dõi thông quan"** |
| 2 | Click **"+ Thêm TK thủ công"** để thêm tờ khai |
| 3 | Hệ thống sẽ tự động kiểm tra theo chu kỳ |
| 4 | Nhận thông báo khi tờ khai thông quan |

### 3. Cài Đặt

Click nút **"⚙ Cài đặt"** để tùy chỉnh:
- Phương thức lấy mã vạch (API/Web/Auto)
- Định dạng tên file PDF
- Chu kỳ kiểm tra thông quan
- Thông báo desktop/âm thanh

---

## 📁 Thư Mục Lưu Mã Vạch

Mặc định, file PDF mã vạch được lưu tại: `C:\CustomsBarcodes`

Bạn có thể thay đổi trong phần **"Thư mục lưu file"** trên giao diện.

---

## ❓ Xử Lý Lỗi Thường Gặp

| Lỗi | Cách xử lý |
|-----|-----------|
| "Configuration file not found" | Đổi tên `config.ini.sample` → `config.ini` |
| "DB: ● Disconnected" | Kiểm tra thông tin server/username/password trong Cấu hình DB |
| Không lấy được mã vạch | Kiểm tra kết nối internet, thử đổi phương thức trong Cài đặt |

---

## 📞 Hỗ Trợ

**GOLDEN LOGISTICS Co.,Ltd**

- 📧 Email: Hochk2019@gmail.com
- 📱 Điện thoại: 0868.333.606

---

**© 2026 Golden Logistics - Customs Barcode Automation v1.5.3**
