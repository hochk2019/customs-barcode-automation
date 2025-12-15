# HƯỚNG DẪN SỬ DỤNG
## Customs Barcode Automation v1.3.1
### Phần mềm tự động lấy mã vạch tờ khai Hải quan

---

## GIỚI THIỆU

**Customs Barcode Automation** là phần mềm hỗ trợ các doanh nghiệp xuất nhập khẩu và đại lý hải quan tự động hóa quy trình lấy mã vạch tờ khai từ Tổng cục Hải quan Việt Nam.

### Tính năng chính

✅ **Kết nối trực tiếp ECUS5** - Đọc dữ liệu tờ khai từ phần mềm khai báo hải quan ECUS5/VNACCS  
✅ **Tải mã vạch tự động** - Lấy mã vạch từ hệ thống Hải quan qua API hoặc Web  
✅ **Tải hàng loạt** - Tải nhiều mã vạch cùng lúc, tiết kiệm thời gian  
✅ **Quản lý theo công ty** - Lọc và quản lý tờ khai theo từng doanh nghiệp  
✅ **Đặt tên file thông minh** - Tự động đặt tên file theo mã số thuế, số hóa đơn hoặc vận đơn  
✅ **Giao diện thân thiện** - Hỗ trợ giao diện Sáng/Tối, dễ sử dụng  
✅ **Cập nhật tự động** - Tự động kiểm tra và cập nhật phiên bản mới từ GitHub

### Yêu cầu hệ thống

- **Hệ điều hành:** Windows 10/11 (64-bit)
- **Database:** SQL Server với ECUS5/VNACCS
- **Kết nối:** Internet để lấy mã vạch từ Hải quan
- **Dung lượng:** ~100MB ổ cứng

### Phát triển bởi

**GOLDEN LOGISTICS Co.,Ltd**  
*"Chuyên làm thủ tục HQ - Vận chuyển hàng toàn quốc"*

---

## MỤC LỤC
1. [Cài đặt lần đầu](#1-cài-đặt-lần-đầu)
2. [Cấu hình Database](#2-cấu-hình-database)
3. [Các chức năng cơ bản](#3-các-chức-năng-cơ-bản)
4. [Cài đặt ứng dụng](#4-cài-đặt-ứng-dụng)
5. [Xử lý lỗi thường gặp](#5-xử-lý-lỗi-thường-gặp)

---

## 1. CÀI ĐẶT LẦN ĐẦU

### Bước 1: Giải nén file
- Giải nén file `CustomsBarcodeAutomation_V1.3.0_Full.zip` vào thư mục bạn muốn cài đặt
- Ví dụ: `C:\CustomsBarcodeAutomation\`

### Bước 2: Tạo file cấu hình
- Copy file `config.ini.sample` và đổi tên thành `config.ini`
- Hoặc chạy ứng dụng lần đầu, ứng dụng sẽ hướng dẫn bạn cấu hình

### Bước 3: Chạy ứng dụng
- Double-click vào file `CustomsBarcodeAutomation.exe` để khởi động

---

## 2. CẤU HÌNH DATABASE

### Cách 1: Cấu hình qua giao diện (Khuyến nghị)

1. **Mở ứng dụng** - Nếu chưa có cấu hình database, ứng dụng vẫn khởi động được
2. **Click nút "Cấu hình DB"** ở góc trên bên phải
3. **Điền thông tin kết nối:**
   - **Server**: Địa chỉ SQL Server (ví dụ: `localhost` hoặc `192.168.1.100`)
   - **Database**: Tên database ECUS5 (thường là `ECUS5VNACCS`)
   - **Username**: Tên đăng nhập SQL Server (ví dụ: `sa`)
   - **Password**: Mật khẩu SQL Server
4. **Click "Test kết nối"** để kiểm tra
5. **Click "Lưu"** nếu kết nối thành công

### Cách 2: Cấu hình qua file config.ini

Mở file `config.ini` bằng Notepad và sửa phần `[Database]`:

```ini
[Database]
server = localhost
database = ECUS5VNACCS
username = sa
password = your_password_here
timeout = 30
```

**Lưu ý:** 
- Mật khẩu sẽ được mã hóa tự động khi lưu qua giao diện
- Nếu sửa trực tiếp file, mật khẩu sẽ ở dạng plain text

### Lưu Profile Database

Bạn có thể lưu nhiều profile database để chuyển đổi nhanh:
1. Cấu hình xong database
2. Nhập tên profile vào ô "Tên profile"
3. Click "Lưu profile"
4. Sau này chọn profile từ dropdown để load nhanh

---

## 3. CÁC CHỨC NĂNG CƠ BẢN

### 3.1. Quét công ty từ Database

1. Click nút **"Quét công ty"** để lấy danh sách công ty từ ECUS5
2. Danh sách công ty sẽ hiển thị trong dropdown
3. Chọn công ty cần lấy mã vạch

### 3.2. Xem trước tờ khai

1. Chọn công ty từ dropdown
2. Chọn khoảng thời gian (Từ ngày - Đến ngày)
3. Click **"Xem trước"** để xem danh sách tờ khai
4. Danh sách tờ khai sẽ hiển thị trong bảng

### 3.3. Tải mã vạch

**Cách 1: Tải từng tờ khai**
- Click vào dòng tờ khai trong bảng
- Click nút **"Tải mã vạch"**

**Cách 2: Tải hàng loạt**
1. Tick chọn các tờ khai cần tải (hoặc tick "Chọn tất cả")
2. Click nút **"Tải hàng loạt"**
3. Chờ quá trình tải hoàn tất

### 3.4. Mở thư mục lưu file

- Click nút **"Mở thư mục"** để mở thư mục chứa file PDF đã tải
- Mặc định: `C:\CustomsBarcodes\`

### 3.5. Chế độ tự động

1. Click nút **"Bắt đầu tự động"** để bật chế độ tự động
2. Ứng dụng sẽ tự động quét và tải mã vạch theo chu kỳ
3. Click **"Dừng"** để tắt chế độ tự động

---

## 4. CÀI ĐẶT ỨNG DỤNG

Click nút **"Cài đặt"** để mở cửa sổ cài đặt:

### Thư mục lưu file
- Chọn thư mục để lưu file PDF mã vạch
- Mặc định: `C:\CustomsBarcodes\`

### Phương thức lấy mã vạch
- **API** (Khuyến nghị): Nhanh, ổn định
- **Web**: Lấy từ website Hải quan
- **Tự động**: Thử API trước, nếu lỗi thì dùng Web

### Định dạng tên file PDF
- **Mã số thuế**: `{mã_số_thuế}_{số_tờ_khai}.pdf`
- **Số hóa đơn**: `{số_hóa_đơn}_{số_tờ_khai}.pdf`
- **Số vận đơn**: `{số_vận_đơn}_{số_tờ_khai}.pdf`

### Giao diện
- **Theme**: Chọn giao diện Sáng hoặc Tối
- **Thông báo**: Bật/tắt thông báo desktop
- **Âm thanh**: Bật/tắt âm thanh khi hoàn tất

### Giới hạn tải
- Số lượng tờ khai tối đa mỗi lần tải hàng loạt (1-50)

---

## 5. XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: "Không thể kết nối database"
**Nguyên nhân:** Thông tin kết nối sai hoặc SQL Server không chạy
**Cách khắc phục:**
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra lại Server, Username, Password
3. Kiểm tra firewall không chặn port 1433

### Lỗi: "Không tìm thấy tờ khai"
**Nguyên nhân:** Không có tờ khai trong khoảng thời gian đã chọn
**Cách khắc phục:**
1. Mở rộng khoảng thời gian tìm kiếm
2. Kiểm tra công ty đã chọn đúng chưa

### Lỗi: "Không thể tải mã vạch"
**Nguyên nhân:** Lỗi kết nối đến server Hải quan
**Cách khắc phục:**
1. Kiểm tra kết nối internet
2. Thử đổi phương thức lấy mã vạch (API ↔ Web)
3. Thử lại sau vài phút

### Lỗi: "Password decryption failed"
**Nguyên nhân:** File mã hóa bị thay đổi sau khi cập nhật
**Cách khắc phục:**
1. Mở "Cấu hình DB"
2. Nhập lại mật khẩu database
3. Click "Lưu"

---

## THÔNG TIN LIÊN HỆ

**Phát triển bởi:** GOLDEN LOGISTICS  
**Email:** Hochk2019@gmail.com  
**Điện thoại:** 0868.333.606

---

*Phiên bản: 1.3.1 - Cập nhật: Tháng 12/2024*
