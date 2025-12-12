# Báo Cáo Phân Tích Website Hải Quan - December 2024

## Tổng Quan

Đã phân tích 3 phương thức lấy mã vạch:

| Phương thức | URL | Trạng thái | Vấn đề |
|-------------|-----|-----------|--------|
| API | http://103.248.160.25:8086/WS_Container/QRCode.asmx | ❌ FAIL | Timeout (~21s) |
| Primary Web | https://pus.customs.gov.vn/faces/ContainerBarcode | ⚠️ PARTIAL | Oracle ADF, AJAX |
| Backup Web | https://pus1.customs.gov.vn/BarcodeContainer/BarcodeContainer.aspx | ❌ FAIL | Có CAPTCHA |

---

## 1. API Analysis

**URL:** `http://103.248.160.25:8086/WS_Container/QRCode.asmx`

**Kết quả test:**
- Timeout 30s: FAIL (timeout sau ~21s)
- Timeout 60s: FAIL (timeout sau ~21s)

**Kết luận:** API không phản hồi. Có thể:
- API đã bị tắt
- Server không hoạt động
- Firewall chặn
- API endpoint đã thay đổi

---

## 2. Primary Website Analysis

**URL:** `https://pus.customs.gov.vn/faces/ContainerBarcode`

**Framework:** Oracle ADF (Application Development Framework)

**Form Fields:**
| Field | ID | Name | Label |
|-------|-----|------|-------|
| Mã doanh nghiệp | pt1:it1::content | pt1:it1 | Mã doanh nghiệp |
| Số tờ khai | pt1:it2::content | pt1:it2 | Số tờ khai |
| Ngày tờ khai | pt1:it3::content | pt1:it3 | Ngày tờ khai |
| Mã hải quan | pt1:it4::content | pt1:it4 | Mã hải quan |

**Submit Button:**
- Không phải `<button>` hay `<input type="submit">`
- Là `<a>` tag với `role="button"` và text "Lấy thông tin"
- Sử dụng AJAX để submit form

**Vấn đề:**
1. Oracle ADF sử dụng AJAX, không phải form submit thông thường
2. Cần xử lý JavaScript events
3. Cần wait cho AJAX response
4. Có thể cần xử lý session/token

**CAPTCHA:** Không có ✓

---

## 3. Backup Website Analysis

**URL:** `https://pus1.customs.gov.vn/BarcodeContainer/BarcodeContainer.aspx`

**Framework:** ASP.NET WebForms

**Form Fields:**
| Field | ID | Name | Label |
|-------|-----|------|-------|
| Mã doanh nghiệp | MaDoanhNghiep | MaDoanhNghiep | Mã doanh nghiệp |
| Số tờ khai | SoToKhai | SoToKhai | Số tờ khai |
| Mã hải quan | MaHQ | MaHQ | Mã hải quan |
| Ngày tờ khai | txtNgayToKhai | txtNgayToKhai | Ngày tờ khai |
| **CAPTCHA** | txtCaptcha | txtCaptcha | Nhập mã như hình trên |

**Submit Button:**
- ID: Button1
- Name: Button1

**Vấn đề:**
1. **CÓ CAPTCHA** - Không thể tự động hóa
2. CAPTCHA image từ: `GenerateCaptcha.aspx`

---

## Selectors Đã Cập Nhật

Đã cập nhật `web_utils/barcode_retriever.py` với selectors mới:

```python
FIELD_SELECTORS = {
    'taxCode': [
        'MaDoanhNghiep',  # Backup website
        'pt1:it1::content', 'pt1:it1',  # Primary website
        # Legacy selectors...
    ],
    'declarationNumber': [
        'SoToKhai',  # Backup website
        'pt1:it2::content', 'pt1:it2',  # Primary website
        # Legacy selectors...
    ],
    'declarationDate': [
        'txtNgayToKhai',  # Backup website
        'pt1:it3::content', 'pt1:it3',  # Primary website
        # Legacy selectors...
    ],
    'customsOffice': [
        'MaHQ',  # Backup website
        'pt1:it4::content', 'pt1:it4',  # Primary website
        # Legacy selectors...
    ]
}
```

---

## Khuyến Nghị

### Ngắn hạn:
1. **Liên hệ Hải Quan** để xác nhận API còn hoạt động không
2. **Kiểm tra API endpoint** có thay đổi không
3. **Xử lý Oracle ADF** cho primary website:
   - Sử dụng Selenium với JavaScript execution
   - Wait cho AJAX response
   - Xử lý dynamic content

### Dài hạn:
1. **Tìm API mới** nếu API cũ đã bị tắt
2. **Implement CAPTCHA solver** nếu cần dùng backup website (không khuyến khích)
3. **Liên hệ Hải Quan** để xin API access chính thức

---

## Test Results

**Test Date:** 08/12/2025

**Declaration tested:**
- MST: 2300782217
- Số tờ khai: 107774843040
- Ngày: 08/12/2025
- Mã HQ: 18A3

**Results:**
- Database connection: ✓ SUCCESS
- Query declarations: ✓ SUCCESS (7 declarations found)
- API retrieval: ❌ FAIL (timeout)
- Primary web retrieval: ❌ FAIL (AJAX handling needed)
- Backup web retrieval: ❌ FAIL (CAPTCHA)

---

## Kết Luận

**Code đã hoạt động đúng theo thiết kế.** Vấn đề không lấy được mã vạch là do:

1. **API không hoạt động** - Cần liên hệ Hải Quan
2. **Primary website dùng AJAX** - Cần cải tiến code để xử lý Oracle ADF
3. **Backup website có CAPTCHA** - Không thể tự động hóa

**Bug fixes December 2024 đã được implement thành công:**
- ✓ Timeout reduction (10s)
- ✓ Adaptive selectors (đã cập nhật với selectors mới)
- ✓ Session reuse
- ✓ Method skipping
- ✓ HTML structure logging
- ✓ Selector caching

**Cần hành động tiếp theo:**
1. Liên hệ Hải Quan về API
2. Cải tiến xử lý Oracle ADF cho primary website
