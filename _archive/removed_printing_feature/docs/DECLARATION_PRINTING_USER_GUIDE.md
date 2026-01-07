# Hướng dẫn sử dụng tính năng In Tờ Khai Hải Quan

## Tổng quan

Tính năng In Tờ Khai Hải Quan cho phép bạn tạo file Excel tờ khai hải quan trực tiếp từ ứng dụng mà không cần truy cập vào hệ thống ECUS cho từng tờ khai riêng lẻ.

### Lợi ích chính

✅ **Tự động hóa quy trình** - Không cần in thủ công từng tờ khai trên ECUS  
✅ **Tiết kiệm thời gian** - In hàng loạt nhiều tờ khai cùng lúc  
✅ **Định dạng chuẩn** - Sử dụng template Excel theo quy định Hải quan  
✅ **Tự động phân loại** - Hệ thống tự động chọn template phù hợp  
✅ **Đặt tên thông minh** - File được đặt tên theo quy ước chuẩn  
✅ **Tích hợp hoàn toàn** - Hoạt động ngay trong giao diện hiện tại

### Yêu cầu hệ thống

- Kết nối database ECUS5/VNACCS
- Template Excel đã được cài đặt
- Thư mục output có quyền ghi
- Python packages: openpyxl, lxml

---

## Cách sử dụng cơ bản

### 1. Truy cập tính năng

**Vị trí**: Nút **"In TKTQ"** trong Preview Panel, bên cạnh nút "Lấy mã vạch"

```
[Lấy mã vạch] [In TKTQ] [Dừng] [Tải lại lỗi] [Xuất Excel]
```

### 2. Điều kiện sử dụng

**Nút "In TKTQ" chỉ được kích hoạt khi:**
- ✅ Đã chọn ít nhất 1 tờ khai
- ✅ Tờ khai đã thông quan (TTTK = "T")
- ✅ Kết nối database thành công

**Nút bị vô hiệu hóa khi:**
- ❌ Chưa chọn tờ khai nào
- ❌ Tờ khai chưa thông quan
- ❌ Mất kết nối database

### 3. Quy trình in tờ khai

#### Bước 1: Chọn tờ khai
1. Sử dụng Enhanced Manual Mode hoặc Standard Mode để hiển thị danh sách tờ khai
2. Chọn các tờ khai cần in bằng checkbox
3. Đảm bảo tờ khai đã thông quan (cột TTTK = "T")

#### Bước 2: Nhấn nút "In TKTQ"
1. Click nút **"In TKTQ"** trong Preview Panel
2. Hệ thống sẽ hiển thị dialog xác nhận
3. Xem lại danh sách tờ khai sẽ được in
4. Click **"Xác nhận"** để bắt đầu

#### Bước 3: Theo dõi tiến trình
```
[▓▓▓▓▓▓░░░░] Đang in tờ khai 6/10: 302934380950
```

**Thông tin hiển thị:**
- Thanh tiến trình với phần trăm hoàn thành
- Số tờ khai đang xử lý / Tổng số tờ khai
- Số tờ khai hiện tại đang được xử lý

#### Bước 4: Xem kết quả
```
✓ Hoàn thành: 8 thành công, 2 lỗi
```

**Chi tiết kết quả:**
- Số tờ khai in thành công
- Số tờ khai gặp lỗi
- Đường dẫn thư mục chứa file Excel
- Danh sách file đã tạo

---

## Các loại tờ khai được hỗ trợ

### 1. Tờ khai xuất khẩu (30...)

**Số tờ khai bắt đầu bằng "30"**
- Ví dụ: 305254403660, 302934380950
- **Template sử dụng**: `ToKhaiHQ7X_QDTQ.xlsx`
- **Tên file**: `ToKhaiHQ7X_QDTQ_305254403660.xlsx`

### 2. Tờ khai nhập khẩu (10...)

**Số tờ khai bắt đầu bằng "10"**
- Ví dụ: 107772836360, 105205185850
- **Template sử dụng**: `ToKhaiHQ7N_QDTQ.xlsx`
- **Tên file**: `ToKhaiHQ7N_QDTQ_107772836360.xlsx`

### 3. Tự động phân loại

Hệ thống tự động:
- Phát hiện loại tờ khai dựa trên số tờ khai
- Chọn template phù hợp
- Đặt tên file theo quy ước
- Không cần can thiệp thủ công

---

## Cấu trúc file Excel được tạo

### Thông tin cơ bản
- **Số tờ khai**: Mã số tờ khai hải quan
- **Ngày tờ khai**: Ngày khai báo (DD/MM/YYYY)
- **Cơ quan hải quan**: Cơ quan tiếp nhận tờ khai

### Thông tin doanh nghiệp
- **Tên công ty**: Tên đầy đủ của doanh nghiệp
- **Mã số thuế**: Mã số thuế doanh nghiệp
- **Địa chỉ**: Địa chỉ trụ sở chính

### Thông tin đối tác
- **Tên đối tác**: Tên nhà cung cấp/khách hàng
- **Địa chỉ đối tác**: Địa chỉ của đối tác
- **Nước xuất xứ/đích**: Nước liên quan đến hàng hóa

### Thông tin tài chính
- **Tổng trị giá**: Tổng giá trị hàng hóa
- **Đơn vị tiền tệ**: USD, VND, EUR, etc.
- **Tỷ giá**: Tỷ giá quy đổi (nếu có)

### Thông tin hàng hóa
- **Tổng trọng lượng**: Trọng lượng tổng cộng
- **Tổng số kiện**: Số lượng kiện hàng
- **Phương tiện vận chuyển**: Đường biển, hàng không, etc.
- **Số vận đơn**: Số Bill of Lading hoặc Airway Bill

---

## Nguồn dữ liệu

### 1. Database ECUS5 (Ưu tiên)

**Ưu điểm:**
- Dữ liệu đầy đủ và chính xác
- Cập nhật real-time
- Tốc độ truy xuất nhanh

**Bảng dữ liệu chính:**
- `ToKhai`: Thông tin tờ khai
- `DaiLy_DoanhNghiep`: Thông tin doanh nghiệp
- `HangHoa`: Chi tiết hàng hóa

### 2. File XML (Dự phòng)

**Khi nào sử dụng:**
- Database không khả dụng
- Dữ liệu database không đầy đủ
- Cần dữ liệu từ file backup

**Vị trí file XML:**
- Thư mục `sample/` trong ứng dụng
- Format: `ECUS5VNACCS2018_ToKhai_[SoToKhai]_STT[So].xml`

### 3. Thứ tự ưu tiên

```
1. Database ECUS5 (Ưu tiên cao nhất)
   ↓ (Nếu thất bại)
2. File XML tương ứng
   ↓ (Nếu thất bại)
3. Template với thông tin cơ bản
```

---

## Cài đặt và cấu hình

### 1. Cài đặt template

**Tự động (Khuyến nghị):**
```bash
python scripts/setup_templates.py
```

**Thủ công:**
1. Copy file template vào thư mục `templates/`
2. Đảm bảo có đủ 4 file:
   - `ToKhaiHQ7X_QDTQ.xlsx`
   - `ToKhaiHQ7X_QDTQ_mapping.json`
   - `ToKhaiHQ7N_QDTQ.xlsx`
   - `ToKhaiHQ7N_QDTQ_mapping.json`

### 2. Kiểm tra template

```bash
python scripts/validate_templates.py --verbose
```

**Kết quả mong đợi:**
```
✓ Template ToKhaiHQ7X_QDTQ.xlsx: OK
✓ Mapping ToKhaiHQ7X_QDTQ_mapping.json: OK
✓ Template ToKhaiHQ7N_QDTQ.xlsx: OK
✓ Mapping ToKhaiHQ7N_QDTQ_mapping.json: OK
✓ Tất cả template hợp lệ
```

### 3. Cấu hình thư mục output

**Cách 1: Qua Enhanced Manual Mode**
1. Mở Enhanced Manual Mode
2. Tìm "Thư mục lưu:" ở phần trên
3. Click **"Chọn..."**
4. Chọn thư mục mong muốn

**Cách 2: Qua config.ini**
```ini
[DeclarationPrinting]
output_directory = C:\CustomsDeclarations
template_directory = templates
```

### 4. Kiểm tra quyền truy cập

**Thư mục output:**
- Phải có quyền ghi
- Đủ dung lượng trống (ít nhất 100MB)
- Đường dẫn không chứa ký tự đặc biệt

**Thư mục template:**
- Phải có quyền đọc
- Chứa đầy đủ file template và mapping

---

## Tính năng nâng cao

### 1. In hàng loạt (Batch Processing)

**Ưu điểm:**
- Xử lý nhiều tờ khai cùng lúc
- Tiết kiệm thời gian
- Tự động xử lý lỗi

**Cách sử dụng:**
1. Chọn nhiều tờ khai trong Preview Panel
2. Click **"In TKTQ"**
3. Hệ thống xử lý tuần tự từng tờ khai
4. Hiển thị tiến trình real-time

**Giới hạn:**
- Tối đa 100 tờ khai mỗi lần
- Có thể dừng giữa chừng
- Tự động retry khi gặp lỗi tạm thời

### 2. Dừng quá trình in

**Khi nào cần dừng:**
- Phát hiện sai sót
- Cần xử lý công việc khác
- Quá trình mất quá nhiều thời gian

**Cách dừng:**
1. Click nút **"Dừng"** trong Preview Panel
2. Hệ thống hoàn thành tờ khai hiện tại
3. Dừng xử lý các tờ khai còn lại
4. Lưu tất cả kết quả đã hoàn thành

**Lưu ý:**
- ✅ Không mất dữ liệu đã xử lý
- ✅ Có thể tiếp tục sau
- ✅ File Excel đã tạo được giữ nguyên

### 3. Xử lý xung đột file

**Khi file đã tồn tại:**
```
File ToKhaiHQ7X_QDTQ_305254403660.xlsx đã tồn tại.
Bạn muốn:
[ Ghi đè ] [ Đổi tên ] [ Bỏ qua ]
```

**Các lựa chọn:**
- **Ghi đè**: Thay thế file cũ
- **Đổi tên**: Tạo file mới với tên khác (thêm số thứ tự)
- **Bỏ qua**: Không tạo file, tiếp tục tờ khai khác

### 4. Audit logging

**Thông tin được ghi log:**
- Thời gian bắt đầu/kết thúc
- Danh sách tờ khai được xử lý
- Kết quả thành công/thất bại
- Đường dẫn file được tạo
- Lỗi chi tiết (nếu có)

**Vị trí log:**
- File: `logs/declaration_printing.log`
- Format: JSON với timestamp

---

## Workflow thực tế

### Workflow 1: In tờ khai hàng ngày

**Mục tiêu:** In tất cả tờ khai đã thông quan trong ngày

```
1. Mở Enhanced Manual Mode
2. Chọn "Tất cả công ty"
3. Từ ngày: Hôm nay
4. Đến ngày: Hôm nay
5. Click "Xem trước"
6. Chọn tất cả tờ khai có TTTK = "T"
7. Click "In TKTQ"
8. Theo dõi tiến trình
9. Kiểm tra kết quả
```

**Thời gian:** 5-10 phút cho 20-50 tờ khai

### Workflow 2: In tờ khai công ty cụ thể

**Mục tiêu:** In tờ khai của một công ty trong tuần

```
1. Mở Enhanced Manual Mode
2. Chọn công ty cụ thể từ dropdown
3. Từ ngày: 7 ngày trước
4. Đến ngày: Hôm nay
5. Click "Xem trước"
6. Xem lại danh sách tờ khai
7. Bỏ chọn tờ khai đã in (nếu có)
8. Click "In TKTQ"
9. Kiểm tra file Excel được tạo
```

**Thời gian:** 3-5 phút cho 10-20 tờ khai

### Workflow 3: In lại tờ khai bị lỗi

**Mục tiêu:** In lại các tờ khai gặp lỗi trước đó

```
1. Xem log để tìm tờ khai bị lỗi
2. Ghi chú số tờ khai bị lỗi
3. Sử dụng Enhanced Manual Mode
4. Tìm và chọn các tờ khai bị lỗi
5. Click "In TKTQ"
6. Theo dõi kỹ để phát hiện nguyên nhân lỗi
7. Kiểm tra file được tạo
```

**Thời gian:** 2-3 phút cho mỗi tờ khai

### Workflow 4: In tờ khai cho báo cáo

**Mục tiêu:** Tạo file Excel cho báo cáo định kỳ

```
1. Xác định khoảng thời gian báo cáo
2. Chọn thư mục output riêng cho báo cáo
3. Sử dụng Enhanced Manual Mode
4. Chọn khoảng thời gian cụ thể
5. Chọn "Tất cả công ty"
6. Click "Xem trước"
7. Chọn tất cả tờ khai cần thiết
8. Click "In TKTQ"
9. Sao chép file Excel vào thư mục báo cáo
```

**Thời gian:** 10-15 phút cho báo cáo tháng

---

## Tips và Best Practices

### Tối ưu hiệu suất

**Kích thước batch:**
- ✅ Tốt: 10-50 tờ khai
- ⚠️ Chấp nhận được: 50-100 tờ khai
- ❌ Tránh: >100 tờ khai

**Thời gian xử lý:**
- Mỗi tờ khai: 2-5 giây
- 20 tờ khai: ~1-2 phút
- 50 tờ khai: ~3-5 phút

**Tối ưu database:**
- Đảm bảo kết nối ổn định
- Tránh chạy đồng thời với ECUS
- Sử dụng giờ ít tải

### Quản lý file

**Tổ chức thư mục:**
```
C:\CustomsDeclarations\
├── 2024-12\
│   ├── Export\
│   └── Import\
├── 2024-11\
└── Archive\
```

**Đặt tên file:**
- Giữ nguyên format mặc định
- Không đổi tên thủ công
- Sử dụng thư mục để phân loại

**Backup:**
- Backup định kỳ thư mục output
- Lưu trữ template gốc
- Backup file mapping JSON

### Xử lý lỗi

**Lỗi thường gặp:**
1. **Template không tìm thấy** → Kiểm tra thư mục templates
2. **Không có quyền ghi** → Kiểm tra quyền thư mục output
3. **Dữ liệu không đầy đủ** → Kiểm tra kết nối database
4. **File đã tồn tại** → Chọn hành động phù hợp

**Cách debug:**
1. Xem log chi tiết trong `logs/declaration_printing.log`
2. Chạy script kiểm tra: `python scripts/validate_templates.py`
3. Test với 1-2 tờ khai trước khi chạy batch lớn
4. Kiểm tra kết nối database

### Bảo mật

**Quyền truy cập:**
- Chỉ cho phép user có quyền in tờ khai
- Bảo vệ thư mục template
- Mã hóa thư mục output nếu cần

**Dữ liệu nhạy cảm:**
- Không lưu mật khẩu trong log
- Mã hóa kết nối database
- Xóa file tạm sau khi hoàn thành

---

## Hỗ trợ và liên hệ

### Tự khắc phục

**Bước 1: Kiểm tra cơ bản**
- Kết nối database: DB Status = "Connected"
- Template: Chạy `python scripts/validate_templates.py`
- Quyền thư mục: Thử tạo file test trong output directory

**Bước 2: Xem log**
- File log: `logs/declaration_printing.log`
- Tìm ERROR hoặc WARNING gần nhất
- Ghi chú thông báo lỗi chính xác

**Bước 3: Test đơn giản**
- Thử in 1 tờ khai đơn lẻ
- Kiểm tra file Excel được tạo
- Xác minh dữ liệu trong file

### Liên hệ hỗ trợ

**Thông tin cần cung cấp:**
- Thông báo lỗi chính xác
- File log (50-100 dòng cuối)
- Số tờ khai gặp vấn đề
- Các bước đã thực hiện
- Screenshot giao diện (nếu có)

**Kênh hỗ trợ:**
- Email: Hochk2019@gmail.com
- Điện thoại: 0868.333.606
- Tài liệu: Xem thêm trong `docs/TEMPLATE_CUSTOMIZATION_GUIDE.md`

---

*Phiên bản: 1.3.4 - Cập nhật: Tháng 12/2024*