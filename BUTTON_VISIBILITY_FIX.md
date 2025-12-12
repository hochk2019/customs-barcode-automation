# Button Visibility Fix

## 🎯 Vấn đề

Từ screenshot mới nhất, tôi xác nhận:
- ✅ Enhanced Manual Mode **ĐÃ HOẠT ĐỘNG**
- ✅ Company dropdown hiển thị tên công ty đầy đủ
- ✅ Date pickers hoạt động
- ✅ Preview table hiển thị
- ❌ **Nhưng các nút "Xem trước", "Lấy mã vạch", "Dừng" KHÔNG THẤY**

## 🔍 Nguyên nhân

Các nút **ĐÃ ĐƯỢC TẠO** trong code nhưng nằm **BÊN DƯỚI** preview table. 

Preview table đang dùng `expand=True` nên chiếm hết không gian, đẩy các nút xuống dưới ngoài màn hình.

## ✅ Giải pháp

### Fix đã thực hiện:

Đổi thứ tự tạo UI components:

**Trước:**
```python
self._create_company_section()
self._create_date_range_section()
self._create_preview_section()      # Preview table trước
self._create_action_buttons()       # Nút sau → bị đẩy xuống
```

**Sau:**
```python
self._create_company_section()
self._create_date_range_section()
self._create_action_buttons()       # Nút trước → luôn hiển thị
self._create_preview_section()      # Preview table sau
```

## 🚀 Để áp dụng fix:

### Bước 1: Cleanup cache
```powershell
Remove-Item -Recurse -Force gui/__pycache__
```

### Bước 2: Restart application
```powershell
python main.py
```

### Bước 3: Verify

Sau khi restart, bạn sẽ thấy layout mới:

```
┌─────────────────────────────────────────┐
│ Quản lý công ty                         │
│ [Quét công ty] [Làm mới]               │
│ Lọc theo công ty: [Dropdown ▼]        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Chọn khoảng thời gian                   │
│ Từ ngày: [DD/MM/YYYY]                  │
│ Đến ngày: [DD/MM/YYYY]                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ [Xem trước] [Lấy mã vạch] [Hủy] [Dừng]│  ← NÚT HIỂN THỊ TRƯỚC
│ [▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Xem trước tờ khai                       │
│ ☐ Chọn tất cả  Đã chọn: 0/0           │
│ ┌───────────────────────────────────┐ │
│ │ ☐ | Số tờ khai | MST | Ngày      │ │  ← PREVIEW TABLE SAU
│ └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 📊 Lợi ích

1. ✅ **Các nút luôn hiển thị** - Không bị đẩy xuống dưới
2. ✅ **UX tốt hơn** - Nút action ở vị trí dễ thấy
3. ✅ **Workflow rõ ràng** - Chọn công ty → Chọn ngày → Nhấn "Xem trước"

## 🎯 Test Workflow

Sau khi restart:

### 1. Test "Xem trước"
- [ ] Chọn công ty từ dropdown
- [ ] Chọn khoảng thời gian
- [ ] Nhấn **"Xem trước"** (phải thấy nút này!)
- [ ] Verify preview table hiển thị tờ khai

### 2. Test "Lấy mã vạch"
- [ ] Tích checkbox của vài tờ khai
- [ ] Verify "Đã chọn: X/Y tờ khai"
- [ ] Nhấn **"Lấy mã vạch"** (phải thấy nút này!)
- [ ] Verify thanh tiến trình chạy

### 3. Test "Dừng"
- [ ] Trong khi đang download
- [ ] Nhấn **"Dừng"** (phải thấy nút này!)
- [ ] Verify dừng an toàn

## ✨ Summary

**Vấn đề:** Nút bị ẩn dưới preview table
**Giải pháp:** Đổi thứ tự UI components
**Kết quả:** Nút luôn hiển thị ở vị trí dễ thấy

**Status:** ✅ FIXED - Restart để áp dụng

---

*Fix completed: December 8, 2024*
