# Tài liệu hướng dẫn tính năng In Tờ Khai Hải Quan

## Tổng quan

Bộ tài liệu này cung cấp hướng dẫn toàn diện cho tính năng In Tờ Khai Hải Quan, bao gồm hướng dẫn sử dụng, khắc phục sự cố, tùy chỉnh template và trợ giúp trực tiếp trong giao diện.

## Cấu trúc tài liệu

### 1. Tài liệu chính

#### 📖 [DECLARATION_PRINTING_USER_GUIDE.md](DECLARATION_PRINTING_USER_GUIDE.md)
**Hướng dẫn sử dụng chi tiết**

**Nội dung:**
- Tổng quan tính năng và lợi ích
- Hướng dẫn sử dụng từng bước
- Các loại tờ khai được hỗ trợ
- Cấu trúc file Excel được tạo
- Nguồn dữ liệu và thứ tự ưu tiên
- Cài đặt và cấu hình
- Tính năng nâng cao (batch processing, xử lý xung đột)
- Workflow thực tế cho các tình huống khác nhau
- Tips và best practices
- Thông tin hỗ trợ

**Đối tượng:** Người dùng cuối, nhân viên hải quan, quản trị viên

#### 🔧 [DECLARATION_PRINTING_TROUBLESHOOTING.md](DECLARATION_PRINTING_TROUBLESHOOTING.md)
**Hướng dẫn khắc phục sự cố**

**Nội dung:**
- Lỗi kết nối và cấu hình
- Lỗi template và file
- Lỗi dữ liệu và xử lý
- Lỗi giao diện và tương tác
- Lỗi hiệu suất và tài nguyên
- Công cụ chẩn đoán tự động
- Script khắc phục nhanh

**Đối tượng:** Người dùng gặp sự cố, nhân viên IT, quản trị hệ thống

#### 📝 [TEMPLATE_CUSTOMIZATION_GUIDE.md](TEMPLATE_CUSTOMIZATION_GUIDE.md)
**Hướng dẫn tùy chỉnh template Excel**

**Nội dung:**
- Cấu trúc template và file mapping
- Cách chỉnh sửa layout Excel
- Cập nhật file mapping JSON
- Tạo template mới
- Định dạng dữ liệu
- Xử lý lỗi template
- Backup và phục hồi

**Đối tượng:** Quản trị viên, người tùy chỉnh template

### 2. Trợ giúp trực tiếp trong giao diện

#### 🖱️ Tooltip System
**File:** `gui/declaration_printing_tooltips.py`

**Tính năng:**
- Tooltip động cho nút "In TKTQ" giải thích tại sao nút được kích hoạt/vô hiệu hóa
- Tooltip tiến trình hiển thị thông tin chi tiết về quá trình xử lý
- Tooltip lỗi với hướng dẫn khắc phục cụ thể
- Tooltip thông tin về loại tờ khai và template

**Các loại tooltip:**

```python
# Trạng thái nút In TKTQ
'print_button_enabled'           # Nút có thể sử dụng
'print_button_no_selection'      # Chưa chọn tờ khai
'print_button_not_cleared'       # Tờ khai chưa thông quan
'print_button_db_error'          # Lỗi kết nối database
'print_button_template_error'    # Lỗi template
'print_button_permission_error'  # Lỗi quyền truy cập

# Tiến trình xử lý
'progress_initializing'          # Đang khởi tạo
'progress_processing'            # Đang xử lý
'progress_completed'             # Hoàn thành
'progress_stopped'               # Đã dừng

# Thông tin lỗi
'error_template_not_found'       # Template không tìm thấy
'error_database_connection'      # Lỗi kết nối database
'error_permission_denied'        # Lỗi quyền truy cập
'error_invalid_data'             # Dữ liệu không hợp lệ
```

#### 💡 Inline Help Panel
**File:** `gui/declaration_printing_help_panel.py`

**Tính năng:**
- Panel trợ giúp tích hợp trong giao diện chính
- Nội dung thay đổi theo ngữ cảnh hiện tại
- Hướng dẫn từng bước cho các workflow
- Liên kết đến tài liệu chi tiết
- Công cụ chẩn đoán tích hợp

**Các ngữ cảnh trợ giúp:**

```python
"overview"        # Tổng quan tính năng
"selection"       # Hướng dẫn chọn tờ khai
"processing"      # Thông tin quá trình xử lý
"completed"       # Kết quả hoàn thành
"error"           # Xử lý lỗi
"templates"       # Thông tin template
"troubleshooting" # Khắc phục sự cố
```

### 3. Công cụ chẩn đoán

#### 🔍 Script chẩn đoán tổng thể
**File:** `diagnosis.py` (được tạo từ troubleshooting guide)

**Chức năng:**
- Kiểm tra template files
- Kiểm tra thư mục output và quyền truy cập
- Test kết nối database
- Kiểm tra Python dependencies
- Báo cáo tổng hợp trạng thái hệ thống

#### 🛠️ Script sửa lỗi nhanh
**File:** `quick_fix.py` (được tạo từ troubleshooting guide)

**Chức năng:**
- Tự động sửa lỗi template
- Tạo thư mục output với quyền phù hợp
- Tạo file config.ini mẫu
- Khôi phục cấu hình cơ bản

#### 📊 Script phân tích log
**File:** `analyze_logs.py` (được tạo từ troubleshooting guide)

**Chức năng:**
- Phân tích log 24h gần nhất
- Thống kê lỗi theo loại
- Hiển thị lỗi gần nhất
- Đưa ra khuyến nghị khắc phục

## Cách sử dụng tài liệu

### Cho người dùng mới

1. **Bắt đầu với:** [DECLARATION_PRINTING_USER_GUIDE.md](DECLARATION_PRINTING_USER_GUIDE.md)
2. **Đọc phần:** "Cách sử dụng cơ bản" và "Quy trình in tờ khai"
3. **Thực hành với:** Workflow 1 - In tờ khai hàng ngày
4. **Tham khảo:** Inline help panel trong ứng dụng

### Cho người dùng có kinh nghiệm

1. **Tham khảo:** Phần "Tính năng nâng cao" trong User Guide
2. **Sử dụng:** Enhanced Manual Mode với các workflow phức tạp
3. **Tùy chỉnh:** Template theo [TEMPLATE_CUSTOMIZATION_GUIDE.md](TEMPLATE_CUSTOMIZATION_GUIDE.md)
4. **Tối ưu:** Theo "Tips và Best Practices"

### Khi gặp sự cố

1. **Kiểm tra:** Tooltip trong giao diện để biết nguyên nhân
2. **Xem:** Inline help panel cho hướng dẫn nhanh
3. **Chạy:** `python diagnosis.py` để chẩn đoán tổng thể
4. **Tham khảo:** [DECLARATION_PRINTING_TROUBLESHOOTING.md](DECLARATION_PRINTING_TROUBLESHOOTING.md)
5. **Sử dụng:** `python quick_fix.py` để sửa lỗi cơ bản

### Cho quản trị viên

1. **Cài đặt:** Theo phần "Cài đặt và cấu hình" trong User Guide
2. **Tùy chỉnh:** Template theo Template Customization Guide
3. **Giám sát:** Sử dụng analyze_logs.py để theo dõi hệ thống
4. **Bảo trì:** Theo "Bảo mật" và "Maintenance Tasks" trong User Guide

## Tích hợp với ứng dụng

### Tooltip Integration

```python
from gui.declaration_printing_tooltips import DeclarationPrintingTooltips

# Khởi tạo tooltip system
tooltip_system = DeclarationPrintingTooltips()

# Tạo tooltip cho nút
tooltip_system.create_tooltip(print_button, 'print_button_enabled')

# Tạo tooltip động
tooltip_system.create_dynamic_tooltip(
    progress_bar, 
    lambda: get_current_progress_status()
)
```

### Help Panel Integration

```python
from gui.declaration_printing_help_panel import create_help_panel

# Tạo help panel
help_panel = create_help_panel(parent_widget)
help_panel.pack(fill="x", padx=10, pady=5)

# Cập nhật theo ngữ cảnh
help_panel.update_context("processing", current=5, total=20)
```

### Preview Panel Integration

```python
from gui.preview_panel_integration import PreviewPanelIntegration

# Khởi tạo với tooltip support
integration = PreviewPanelIntegration(
    preview_panel=preview_panel,
    config_manager=config_manager,
    logger=logger
)

# Tooltip và help được tự động setup
```

## Cập nhật và bảo trì tài liệu

### Khi thêm tính năng mới

1. **Cập nhật:** User Guide với hướng dẫn sử dụng tính năng mới
2. **Thêm:** Tooltip messages cho UI elements mới
3. **Bổ sung:** Help panel content cho ngữ cảnh mới
4. **Kiểm tra:** Troubleshooting guide có cần cập nhật không

### Khi sửa lỗi

1. **Cập nhật:** Troubleshooting guide với lỗi mới và cách khắc phục
2. **Thêm:** Error tooltip messages nếu cần
3. **Cải thiện:** Diagnostic scripts để phát hiện lỗi tương tự

### Khi thay đổi UI

1. **Cập nhật:** Screenshot và mô tả trong User Guide
2. **Điều chỉnh:** Tooltip positioning và content
3. **Kiểm tra:** Help panel layout và navigation

## Feedback và cải thiện

### Thu thập feedback

- **Tooltip effectiveness:** Theo dõi user interaction với tooltips
- **Help panel usage:** Đo lường việc sử dụng các section khác nhau
- **Documentation gaps:** Xác định phần nào cần bổ sung

### Cải thiện liên tục

- **A/B testing:** Thử nghiệm các phiên bản tooltip khác nhau
- **User surveys:** Thu thập ý kiến về tính hữu ích của tài liệu
- **Analytics:** Theo dõi các lỗi thường gặp để cải thiện hướng dẫn

## Liên hệ và hỗ trợ

### Đóng góp tài liệu

- **Email:** Hochk2019@gmail.com
- **Điện thoại:** 0868.333.606
- **Format:** Markdown với cấu trúc rõ ràng
- **Review:** Tất cả thay đổi cần được review trước khi merge

### Báo cáo vấn đề

- **Lỗi tài liệu:** Thông tin không chính xác hoặc lỗi thời
- **Thiếu hướng dẫn:** Tình huống chưa được cover
- **Cải thiện UX:** Đề xuất cải thiện tooltip và help panel

---

## Checklist triển khai

### ✅ Tài liệu đã hoàn thành

- [x] User Guide chi tiết với workflow thực tế
- [x] Troubleshooting guide với công cụ chẩn đoán
- [x] Template customization guide
- [x] Tooltip system với messages đầy đủ
- [x] Inline help panel với contextual content
- [x] Integration với preview panel
- [x] Documentation README này

### 🔄 Cần triển khai

- [ ] Tích hợp tooltip system vào preview panel thực tế
- [ ] Thêm help panel vào giao diện chính
- [ ] Tạo các diagnostic scripts từ troubleshooting guide
- [ ] Test tooltip positioning trên các màn hình khác nhau
- [ ] Validate help panel navigation và links
- [ ] Setup documentation update workflow

### 📋 Testing checklist

- [ ] Tooltip hiển thị đúng cho tất cả trạng thái nút
- [ ] Help panel cập nhật đúng theo ngữ cảnh
- [ ] Links trong help panel hoạt động chính xác
- [ ] Diagnostic scripts chạy thành công
- [ ] Documentation coverage đầy đủ cho tất cả features
- [ ] User feedback positive về tính hữu ích

---

*Phiên bản: 1.3.4 - Cập nhật: Tháng 12/2024*

*Tài liệu này được tạo để hỗ trợ task 15: "Documentation and user guidance" trong implementation plan của tính năng In Tờ Khai Hải Quan.*