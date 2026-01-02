# Phần Mềm Lấy Mã Vạch Tờ Khai Hải Quan Tự Động - Customs Barcode Automation v1.5.0

> **Giải pháp tối ưu** giúp doanh nghiệp xuất nhập khẩu lấy mã vạch tờ khai hải quan nhanh chóng, chính xác và hoàn toàn tự động. Tiết kiệm thời gian, giảm sai sót, tăng hiệu suất làm việc.

---

## 📌 Giới Thiệu

**Customs Barcode Automation** là phần mềm chuyên dụng hỗ trợ các doanh nghiệp làm thủ tục hải quan tự động hóa quy trình lấy mã vạch từ hệ thống ECUS. Phần mềm kết nối trực tiếp với database ECUS5VNACCS, tự động truy vấn tờ khai và tạo file PDF chứa mã vạch chuẩn theo quy định hải quan.

### 🎯 Phần Mềm Dành Cho Ai?

- **Đại lý hải quan** cần xử lý nhiều tờ khai mỗi ngày
- **Doanh nghiệp xuất nhập khẩu** muốn đơn giản hóa thủ tục
- **Nhân viên logistics** cần theo dõi trạng thái thông quan
- **Công ty dịch vụ hải quan** muốn nâng cao hiệu quả làm việc

---

## 📸 Giao Diện Ứng Dụng

### Giao Diện Chính - Tab Xem Trước Tờ Khai

![Giao diện chính với tab xem trước tờ khai](C:/Users/PC/.gemini/antigravity/brain/0eea5335-6b37-41a1-bdef-9359a6f2a22f/screenshot_main_preview.png)

Giao diện 2 cột trực quan:
- **Panel trái**: Quản lý công ty, chọn ngày, công ty gần đây
- **Panel phải**: Xem trước danh sách tờ khai với bộ lọc

### Tab Theo Dõi Thông Quan

![Tab theo dõi thông quan tự động](C:/Users/PC/.gemini/antigravity/brain/0eea5335-6b37-41a1-bdef-9359a6f2a22f/screenshot_tracking.png)

Theo dõi trạng thái thông quan real-time:
- ⏰ **Countdown 02:01** - Thời gian còn lại đến lần kiểm tra tiếp
- 🟢 **Tự động: BẬT** - Trạng thái tự động kiểm tra
- 📋 Danh sách tờ khai đang theo dõi với trạng thái

---

## ✨ Tính Năng Nổi Bật

### 1. 🔄 Lấy Mã Vạch Tự Động

Tự động quét và lấy mã vạch cho tất cả tờ khai trong khoảng thời gian chọn.

**Ưu điểm:**
- Quét đa công ty cùng lúc (tối đa 15 công ty)
- Chọn khoảng ngày linh hoạt
- Hiển thị tiến trình chi tiết
- Tự động bỏ qua tờ khai đã có mã vạch

### 2. 📊 Xem Trước Tờ Khai (Preview)

Xem danh sách tờ khai trước khi lấy mã vạch:
- STT, Số tờ khai, Mã hải quan
- Ngày đăng ký, Tên công ty
- Trạng thái thông quan
- Loại hình, Vận đơn, Số hóa đơn

### 3. 🔔 Theo Dõi Thông Quan Tự Động (MỚI v1.5.0)

Tự động kiểm tra trạng thái thông quan định kỳ. Thông báo ngay khi tờ khai đã thông quan.

### 4. 💾 Quản Lý File PDF

Xuất mã vạch ra file PDF theo nhiều định dạng đặt tên tùy chọn.

### 5. ⚙️ Cài Đặt Linh Hoạt

![Dialog cài đặt ứng dụng](C:/Users/PC/.gemini/antigravity/brain/0eea5335-6b37-41a1-bdef-9359a6f2a22f/screenshot_settings.png)

Tùy chỉnh mọi thông số:
- **Phương thức lấy mã vạch**: Auto/API/Web
- **Định dạng tên file PDF**: MST, Hóa đơn, Vận đơn
- **Giao diện**: Sáng/Tối
- **Chu kỳ kiểm tra**: 1-60 phút
- **Số ngày lưu trữ**: 1-365 ngày
- **Số công ty tối đa**: 1-15 công ty

### 6. 🔍 Tìm Kiếm Thông Minh

Tìm kiếm công ty theo tên hoặc mã số thuế với gợi ý tự động.

---

## 📖 Hướng Dẫn Sử Dụng

### Bước 1: Cấu Hình Database

![Dialog cấu hình kết nối database](C:/Users/PC/.gemini/antigravity/brain/0eea5335-6b37-41a1-bdef-9359a6f2a22f/screenshot_db_config.png)

1. Click nút **"Cấu hình DB"**
2. Nhập thông tin kết nối:
   - **Server**: Địa chỉ server SQL
   - **Database**: ECUS5VNACCS
   - **Username/Password**: Tài khoản đăng nhập
3. Click **"Kiểm tra kết nối"** để test
4. Click **"Lưu & Kết nối lại"**

### Bước 2: Quét Công Ty

1. Click nút **"Quét công ty"**
2. Danh sách công ty gần đây hiển thị dạng nút bấm nhanh
3. Tìm kiếm công ty bằng ô tìm kiếm

### Bước 3: Chọn Công Ty & Ngày

1. Chọn công ty từ dropdown hoặc nút công ty gần đây
2. Chọn **"Từ ngày"** và **"Đến ngày"**
3. Click **"+ Thêm"** để thêm công ty vào danh sách đã chọn

### Bước 4: Xem Trước & Lấy Mã Vạch

1. Click **"Xem trước"** để hiển thị danh sách tờ khai
2. Tick chọn các tờ khai cần xử lý
3. Click **"Lấy mã vạch"** để bắt đầu
4. File PDF được lưu vào thư mục đã cấu hình

### Bước 5: Theo Dõi Thông Quan

1. Chuyển sang tab **"Theo dõi thông quan"**
2. Thêm tờ khai bằng nút **"+ Thêm TK thủ công"**

![Dialog thêm tờ khai thủ công](C:/Users/PC/.gemini/antigravity/brain/0eea5335-6b37-41a1-bdef-9359a6f2a22f/screenshot_add_declaration.png)

3. Nhập thông tin: Công ty, Số tờ khai, Mã Hải quan, Ngày
4. Hệ thống tự động kiểm tra theo chu kỳ đã cài đặt

---

## 💾 Yêu Cầu Hệ Thống

| Thành phần | Yêu cầu |
|------------|---------|
| **Hệ điều hành** | Windows 10/11 (64-bit) |
| **RAM** | 4 GB trở lên |
| **Ổ cứng** | 200 MB trống |
| **Kết nối** | Mạng LAN/VPN đến server ECUS |
| **Database** | SQL Server (ECUS5VNACCS) |

---

## 📥 Tải Về & Cài Đặt

### Phiên Bản Mới Nhất: v1.5.0

[📥 **Tải về CustomsAutomation-v1.5.0.zip**](#) (56 MB)

### Hướng Dẫn Cài Đặt

1. **Giải nén** file ZIP vào thư mục tùy chọn
2. **Chạy** file `CustomsAutomation.exe`
3. **Cấu hình** kết nối database
4. **Bắt đầu** sử dụng!

> ⚠️ **Lưu ý:** Không cần cài đặt Python. File EXE đã đóng gói đầy đủ.

---

## 🆕 Có Gì Mới Trong v1.5.0?

✅ **Trạng thái Tự động BẬT/TẮT** - Hiển thị ngay trên toolbar  
✅ **Countdown timer** - Đếm ngược đến lần kiểm tra tiếp  
✅ **Ghi nhớ Mã Hải quan** - Dropdown 10 mã gần nhất  
✅ **Cài đặt số công ty tối đa** - Chọn từ 1-15 công ty  
✅ **Tooltips hướng dẫn** - Di chuột qua nút để xem mô tả  

---

## 📞 Liên Hệ Hỗ Trợ

**GOLDEN LOGISTICS Co.,Ltd**

> *"Thích thì thuê - Không thích thì chê"*

Liên hệ để được tư vấn thủ tục hải quan **miễn phí** - đúng quy định - có lợi nhất cho doanh nghiệp.

- 📧 **Email:** Hochk2019@gmail.com
- 📱 **Điện thoại:** 0868.333.606

---

## 🔖 Tags

`phần mềm hải quan` `lấy mã vạch tờ khai` `ECUS5` `tự động hóa hải quan` `thông quan tự động` `barcode hải quan` `phần mềm xuất nhập khẩu` `customs automation` `quản lý tờ khai` `đại lý hải quan`

---

**© 2026 Golden Logistics - Customs Barcode Automation v1.5.0**
