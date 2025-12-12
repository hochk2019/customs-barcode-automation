# Bug Fixes Summary - December 8, 2024

## 🐛 Vấn đề phát hiện

Sau khi testing Enhanced Manual Mode, phát hiện 6 vấn đề nghiêm trọng:

### 1. ❌ Không có UI chọn output directory
**Hiện tại:** Output directory có trong config nhưng không có UI để thay đổi
**Cần:** Thêm Browse button và path display trong Enhanced Manual Panel

### 2. ❌ API timeout và không tìm thấy form fields
**Log:**
```
ERROR - API request timed out after 30s
WARNING - Could not find form field with names: ['taxCode', 'ma_dv', 'maDoanhnghiep']
WARNING - Could not find submit button
```

**Nguyên nhân:**
- Timeout quá dài (30s)
- Website Hải Quan đã thay đổi cấu trúc HTML
- Selectors cũ không còn hoạt động

**Cần:**
- Giảm timeout xuống 10-15s
- Update selectors
- Thêm fallback selectors
- Log HTML structure khi fail để debug

### 3. ❌ Duplicate declarations
**Hiện tại:** Tờ khai 308036947760 xuất hiện 3 lần trong preview
**Nguyên nhân:** Query không DISTINCT đúng
**Cần:** Fix query để chỉ trả về unique declarations

### 4. ❌ Date picker không có calendar
**Hiện tại:** Chỉ có text input, phải nhập thủ công
**Cần:** Thêm calendar popup button (dùng tkcalendar.DateEntry)

### 5. ❌ Company dropdown không thể gõ
**Hiện tại:** Đã set `state="normal"` nhưng không filter khi gõ
**Cần:** Implement autocomplete/filter functionality

### 6. ❌ Download quá chậm
**Hiện tại:** Mỗi tờ khai ~37 giây (30s timeout + 7s fallback)
**Cần:**
- Giảm timeout
- Optimize retry logic
- Reuse HTTP sessions
- Skip failed methods faster

## 📊 Priority

| Issue | Severity | Impact | Priority |
|-------|----------|--------|----------|
| #2 API timeout | Critical | Không lấy được mã vạch | P0 |
| #3 Duplicates | High | Xử lý trùng lặp | P0 |
| #6 Performance | High | UX kém | P1 |
| #4 Calendar | Medium | UX kém | P2 |
| #5 Dropdown search | Medium | UX kém | P2 |
| #1 Output dir | Low | Có workaround | P3 |

## 🔧 Giải pháp đề xuất

### Fix #2: API Timeout (P0)

**File:** `web_utils/barcode_retriever.py`

**Changes:**
1. Giảm timeout từ 30s → 10s
2. Update selectors cho form fields
3. Thêm logging HTML structure khi fail
4. Thêm fallback selectors

**Code location:**
```python
# Line ~100: Update timeout
timeout = 10  # Changed from 30

# Line ~150: Add fallback selectors
FIELD_SELECTORS = {
    'taxCode': ['taxCode', 'ma_dv', 'maDoanhnghiep', 'mst', 'tax_code'],
    'declarationNumber': ['declarationNumber', 'so_tk', 'soToKhai', 'so_to_khai'],
    # ... more
}
```

### Fix #3: Duplicates (P0)

**File:** `database/ecus_connector.py`

**Changes:**
```python
# Line ~200: Fix query
query = """
    SELECT DISTINCT 
        SO_TOKHAI,
        MA_DV,
        NGAY_DK,
        MA_HQ
    FROM DTOKHAIMD
    WHERE ...
    GROUP BY SO_TOKHAI, MA_DV, NGAY_DK, MA_HQ  -- Add GROUP BY
"""
```

### Fix #6: Performance (P1)

**File:** `web_utils/barcode_retriever.py`

**Changes:**
1. Reuse HTTP session
2. Reduce timeout
3. Skip failed methods

```python
# Add session reuse
self.session = requests.Session()

# Reduce retries
max_retries = 1  # Changed from 3
```

### Fix #4: Calendar (P2)

**File:** `gui/enhanced_manual_panel.py`

**Changes:**
```python
from tkcalendar import DateEntry

# Replace Entry with DateEntry
self.from_date_entry = DateEntry(
    from_row,
    textvariable=self.from_date_var,
    date_pattern='dd/mm/yyyy',
    width=15
)
```

### Fix #5: Dropdown Search (P2)

**File:** `gui/enhanced_manual_panel.py`

**Changes:**
```python
# Add filter on keypress
def _filter_companies(self, event):
    typed = self.company_var.get().lower()
    filtered = [c for c in self.all_companies if typed in c.lower()]
    self.company_combo['values'] = filtered
```

### Fix #1: Output Directory (P3)

**File:** `gui/enhanced_manual_panel.py`

**Changes:**
```python
# Add output directory section
output_frame = ttk.Frame(self)
output_frame.pack(fill=tk.X, pady=5)

ttk.Label(output_frame, text="Thư mục lưu:").pack(side=tk.LEFT)
self.output_var = tk.StringVar(value=config.output_path)
ttk.Entry(output_frame, textvariable=self.output_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
ttk.Button(output_frame, text="Chọn...", command=self.browse_output).pack(side=tk.LEFT)
```

## 📋 Spec Created

Full spec tại: `.kiro/specs/bug-fixes-dec-2024/requirements.md`

**Next steps:**
1. Review requirements
2. Create design.md
3. Create tasks.md
4. Implement fixes theo priority

## 🚨 Urgent Actions

**Cần fix ngay (P0):**
1. Fix API timeout (#2)
2. Fix duplicates (#3)

**Có thể fix sau:**
3. Performance (#6)
4. Calendar (#4)
5. Dropdown search (#5)
6. Output directory (#1)

## 📞 Cần thêm thông tin

Để fix #2 (API timeout), cần:
1. URL chính xác của website Hải Quan đang dùng
2. Screenshot của form trên website
3. HTML source của form (View Page Source)

Bạn có thể cung cấp được không?

---

*Analysis completed: December 8, 2024*
