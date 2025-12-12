# Company Name Display Fix

## 🎯 Vấn đề

Sau khi quét công ty, dropdown chỉ hiển thị "Công ty [mã số thuế]" thay vì tên công ty thật từ database.

**Nguyên nhân:**
- Query cũ JOIN với bảng `DaiLy_DoanhNghiep` nhưng cột `MA_SO_THUE` trong bảng này **rỗng**
- Không match được với `MA_DV` trong `DTOKHAIMD`

## ✅ Giải pháp

Thay vì JOIN với bảng `DaiLy_DoanhNghiep`, lấy tên công ty trực tiếp từ cột `_Ten_DV_L1` trong bảng `DTOKHAIMD`.

### Phát hiện

Sau khi kiểm tra database:
1. ✅ Bảng `DaiLy_DoanhNghiep` có 975 rows
2. ❌ Cột `MA_SO_THUE` trong bảng này **rỗng** (length: 0)
3. ✅ Bảng `DTOKHAIMD` có cột `_Ten_DV_L1` chứa tên công ty
4. ✅ Mỗi tờ khai đã có sẵn tên công ty

### Ví dụ dữ liệu

```
MA_DV: 0700809357 → _Ten_DV_L1: "CôNG TY TNHH DMR VINA"
MA_DV: 0700801485 → _Ten_DV_L1: "CôNG TY TNHH KOMOS VINA"
MA_DV: 2300782217 → _Ten_DV_L1: "Công ty TNHH Sanchine (Việt Nam)"
```

## 🔧 Thay đổi kỹ thuật

### File: `database/ecus_connector.py`

#### Query cũ (KHÔNG hoạt động)
```python
query = """
    SELECT DISTINCT 
        tk.MA_DV as tax_code,
        dn.TEN_DAI_LY as company_name
    FROM DTOKHAIMD tk
    LEFT JOIN DaiLy_DoanhNghiep dn ON tk.MA_DV = dn.MA_SO_THUE
    WHERE tk.NGAY_DK >= DATEADD(day, ?, GETDATE())
        AND tk.MA_DV IS NOT NULL
        AND tk.MA_DV != ''
    ORDER BY tk.MA_DV
"""
```

**Vấn đề:** `dn.MA_SO_THUE` rỗng → không match → `company_name` = NULL

#### Query mới (Hoạt động)
```python
query = """
    SELECT DISTINCT 
        MA_DV as tax_code,
        _Ten_DV_L1 as company_name
    FROM DTOKHAIMD
    WHERE NGAY_DK >= DATEADD(day, ?, GETDATE())
        AND MA_DV IS NOT NULL
        AND MA_DV != ''
    ORDER BY MA_DV
"""
```

**Lợi ích:**
- ✅ Không cần JOIN
- ✅ Lấy tên công ty trực tiếp từ tờ khai
- ✅ Nhanh hơn (không JOIN)
- ✅ Chính xác hơn (tên công ty từ tờ khai)

## 📊 Kết quả

### Trước
```
Dropdown hiển thị:
  Công ty 0700809357
  Công ty 0700801485
  Công ty 2300782217
```

### Sau
```
Dropdown hiển thị:
  0700809357 - CôNG TY TNHH DMR VINA
  0700801485 - CôNG TY TNHH KOMOS VINA
  2300782217 - Công ty TNHH Sanchine (Việt Nam)
```

### Test Results

**Query test:**
```
Found 245 unique companies
All companies have real names ✓
Format: 'TaxCode - Company Name' ✓
```

**Unit tests:**
```bash
pytest tests/test_company_scanner_unit.py -v
Result: 10/10 tests passed ✓
```

## ✅ Testing

### Automated Tests
```bash
# Unit tests
pytest tests/test_company_scanner_unit.py -v
# Result: ✅ All 10 tests passed
```

### Manual Testing
```bash
python main.py
```

**Test steps:**
1. ✅ Nhấn "Quét công ty"
2. ✅ Kiểm tra dropdown hiển thị: "Mã số thuế - Tên Công Ty"
3. ✅ Verify tên công ty là tên thật (không phải "Công ty [mã]")
4. ✅ Gõ tên công ty vào combobox để tìm kiếm
5. ✅ Chọn công ty và xem trước tờ khai
6. ✅ Verify hoạt động bình thường

## 📝 Database Schema Notes

### Bảng DTOKHAIMD (Tờ khai)
- `MA_DV`: Mã số thuế (10-13 digits)
- `_Ten_DV_L1`: Tên công ty ✅ **Sử dụng cột này**
- `_Ten_DV_L2`: Tên công ty phụ (thường NULL)
- `_Ten_DV_L3`: Tên công ty phụ (thường NULL)

### Bảng DaiLy_DoanhNghiep (Danh sách đại lý)
- `MA_SO_THUE`: Mã số thuế ❌ **Rỗng, không sử dụng**
- `USERNAME`: Username (10 digits) - Có thể là mã số thuế
- `TEN_DAI_LY`: Tên đại lý

**Kết luận:** Bảng `DaiLy_DoanhNghiep` không phù hợp cho mục đích này.

## 🚀 Deployment

### Changes
- Modified: `database/ecus_connector.py` - Method `scan_all_companies()`
- No GUI changes needed (already supports the format)
- No database schema changes

### Impact
- ✅ Positive: Users can now see real company names
- ✅ Performance: Faster (no JOIN)
- ✅ Accuracy: Company names from actual declarations
- ✅ No breaking changes

### Rollout
1. ✅ Code changes completed
2. ✅ Tests passed
3. ⏭️ Ready for user testing

## 🎓 Lessons Learned

1. **Always verify database schema** - Don't assume column names match their purpose
2. **Check data quality** - Columns can exist but be empty
3. **Look for alternative sources** - Sometimes data exists in unexpected places
4. **Test with real data** - Mock data won't reveal schema issues

## ✨ Summary

**Trước:**
- ❌ Hiển thị: "Công ty [mã số thuế]"
- ❌ Không có tên công ty thật
- ❌ JOIN với bảng sai

**Sau:**
- ✅ Hiển thị: "Mã số thuế - Tên Công Ty"
- ✅ Tên công ty thật từ tờ khai
- ✅ Query đơn giản, nhanh hơn
- ✅ Có thể tìm kiếm bằng tên công ty

**Status:** ✅ READY FOR TESTING

---

*Fix completed: December 8, 2024*
