# Hướng dẫn Tùy chỉnh Template Excel

Tài liệu này hướng dẫn cách tùy chỉnh template Excel cho chức năng in tờ khai hải quan.

## Tổng quan

Hệ thống sử dụng template Excel để tạo tờ khai hải quan với định dạng chuẩn. Mỗi template có:
- File Excel (.xlsx hoặc .xls) chứa layout và định dạng
- File mapping JSON định nghĩa vị trí các trường dữ liệu

## Cấu trúc Template

### Các Template được hỗ trợ

| Loại tờ khai | Tên file template | File mapping |
|--------------|-------------------|--------------|
| Xuất khẩu QDTQ | `ToKhaiHQ7X_QDTQ.xlsx` | `ToKhaiHQ7X_QDTQ_mapping.json` |
| Nhập khẩu QDTQ | `ToKhaiHQ7N_QDTQ.xlsx` | `ToKhaiHQ7N_QDTQ_mapping.json` |
| Xuất khẩu PL | `ToKhaiHQ7X_PL.xlsx` | `ToKhaiHQ7X_PL_mapping.json` |
| Nhập khẩu PL | `ToKhaiHQ7N_PL.xlsx` | `ToKhaiHQ7N_PL_mapping.json` |

### Thư mục Template

Tất cả template được lưu trong thư mục `templates/` của ứng dụng:
```
templates/
├── ToKhaiHQ7X_QDTQ.xlsx
├── ToKhaiHQ7X_QDTQ_mapping.json
├── ToKhaiHQ7N_QDTQ.xlsx
├── ToKhaiHQ7N_QDTQ_mapping.json
└── ...
```

## Tùy chỉnh Template Excel

### 1. Sao lưu Template gốc

Trước khi chỉnh sửa, hãy sao lưu template gốc:
```bash
copy templates\ToKhaiHQ7N_QDTQ.xlsx templates\ToKhaiHQ7N_QDTQ_backup.xlsx
```

### 2. Chỉnh sửa Layout

1. Mở file template bằng Microsoft Excel
2. Chỉnh sửa layout, định dạng, màu sắc theo yêu cầu
3. **Lưu ý**: Không thay đổi vị trí các ô dữ liệu quan trọng
4. Lưu file với định dạng Excel (.xlsx)

### 3. Cập nhật File Mapping

File mapping định nghĩa vị trí các trường dữ liệu trong Excel:

```json
{
  "declaration_number": "B5",
  "declaration_date": "C5",
  "company_name": "B10",
  "company_tax_code": "B11",
  "company_address": "B12",
  "partner_name": "B15",
  "partner_address": "B16",
  "country_of_origin": "B18",
  "total_value": "F20",
  "currency": "G20",
  "total_weight": "H20",
  "total_packages": "I20",
  "transport_method": "B22",
  "bill_of_lading": "C22"
}
```

#### Các trường dữ liệu có sẵn

| Trường | Mô tả | Kiểu dữ liệu |
|--------|-------|--------------|
| `declaration_number` | Số tờ khai | Text |
| `declaration_date` | Ngày tờ khai | Date (DD/MM/YYYY) |
| `company_name` | Tên công ty | Text |
| `company_tax_code` | Mã số thuế | Text |
| `company_address` | Địa chỉ công ty | Text |
| `partner_name` | Tên đối tác | Text |
| `partner_address` | Địa chỉ đối tác | Text |
| `country_of_origin` | Nước xuất xứ | Text |
| `country_of_destination` | Nước đích | Text |
| `total_value` | Tổng trị giá | Number |
| `currency` | Đơn vị tiền tệ | Text |
| `exchange_rate` | Tỷ giá | Number |
| `total_weight` | Tổng trọng lượng | Number |
| `total_packages` | Tổng số kiện | Number |
| `transport_method` | Phương tiện vận chuyển | Text |
| `bill_of_lading` | Số vận đơn | Text |
| `customs_office` | Cơ quan hải quan | Text |

### 4. Kiểm tra Template

Sau khi chỉnh sửa, sử dụng script kiểm tra:
```bash
python scripts/validate_templates.py --verbose
```

## Tạo Template mới

### 1. Tạo file Excel

1. Tạo file Excel mới với layout mong muốn
2. Đặt tên theo quy ước: `ToKhaiHQ[7X/7N]_[QDTQ/PL].xlsx`
3. Lưu vào thư mục `templates/`

### 2. Tạo file Mapping

1. Tạo file JSON với tên tương ứng: `ToKhaiHQ[7X/7N]_[QDTQ/PL]_mapping.json`
2. Định nghĩa vị trí các trường dữ liệu
3. Sử dụng định dạng ô Excel (ví dụ: "B5", "C10")

### 3. Đăng ký Template

Cập nhật file `declaration_printing/template_manager.py`:
```python
TEMPLATE_FILENAMES = {
    DeclarationType.EXPORT_CLEARANCE: "ToKhaiHQ7X_QDTQ.xlsx",
    DeclarationType.IMPORT_CLEARANCE: "ToKhaiHQ7N_QDTQ.xlsx",
    DeclarationType.EXPORT_ROUTING: "ToKhaiHQ7X_PL.xlsx",
    DeclarationType.IMPORT_ROUTING: "ToKhaiHQ7N_PL.xlsx",
    # Thêm template mới ở đây
}
```

## Định dạng Dữ liệu

### Số

- Số nguyên: `123456`
- Số thập phân: `123.45` (dấu chấm làm phân cách thập phân)
- Tiền tệ: Theo chuẩn Việt Nam, không có ký hiệu tiền tệ

### Ngày tháng

- Định dạng: `DD/MM/YYYY`
- Ví dụ: `15/12/2024`

### Văn bản

- Mã hóa: UTF-8
- Độ dài tối đa: Tùy theo trường (thường 255 ký tự)
- Tự động cắt bớt nếu quá dài

## Xử lý Lỗi

### Lỗi thường gặp

1. **Template không tìm thấy**
   - Kiểm tra tên file và đường dẫn
   - Đảm bảo file có trong thư mục `templates/`

2. **File mapping không hợp lệ**
   - Kiểm tra cú pháp JSON
   - Đảm bảo tất cả trường bắt buộc có mặt

3. **Ô Excel không hợp lệ**
   - Sử dụng định dạng ô đúng (ví dụ: "B5", không phải "b5")
   - Đảm bảo ô tồn tại trong worksheet

### Debug Template

Sử dụng script kiểm tra để debug:
```bash
# Kiểm tra chi tiết
python scripts/validate_templates.py --verbose

# Tự động sửa lỗi
python scripts/validate_templates.py --fix

# Cài đặt template mẫu
python scripts/validate_templates.py --install-samples
```

## Ví dụ Thực tế

### Thêm trường mới

1. **Thêm vào template Excel**:
   - Chọn ô trống (ví dụ: D25)
   - Nhập nhãn: "Ghi chú:"

2. **Cập nhật mapping**:
   ```json
   {
     "declaration_number": "B5",
     "company_name": "B10",
     "notes": "D25"
   }
   ```

3. **Kiểm tra**:
   ```bash
   python scripts/validate_templates.py
   ```

### Thay đổi vị trí trường

1. **Di chuyển trong Excel**:
   - Cắt ô "Tên công ty" từ B10
   - Dán vào vị trí mới C15

2. **Cập nhật mapping**:
   ```json
   {
     "company_name": "C15"
   }
   ```

## Backup và Phục hồi

### Sao lưu

```bash
# Sao lưu toàn bộ thư mục templates
xcopy templates templates_backup /E /I

# Sao lưu template cụ thể
copy templates\ToKhaiHQ7N_QDTQ.xlsx backups\
copy templates\ToKhaiHQ7N_QDTQ_mapping.json backups\
```

### Phục hồi

```bash
# Phục hồi từ backup
copy backups\ToKhaiHQ7N_QDTQ.xlsx templates\
copy backups\ToKhaiHQ7N_QDTQ_mapping.json templates\
```

## Hỗ trợ

Nếu gặp vấn đề:

1. Chạy script kiểm tra: `python scripts/validate_templates.py --verbose`
2. Kiểm tra log ứng dụng trong thư mục `logs/`
3. Tham khảo file mẫu trong thư mục `sample/`
4. Liên hệ nhóm phát triển để được hỗ trợ

## Lưu ý Quan trọng

- ⚠️ **Luôn sao lưu trước khi chỉnh sửa**
- ⚠️ **Kiểm tra template sau mỗi thay đổi**
- ⚠️ **Không thay đổi cấu trúc cơ bản của template ECUS**
- ⚠️ **Đảm bảo file mapping luôn đồng bộ với template Excel**
- ⚠️ **Sử dụng mã hóa UTF-8 cho file JSON**