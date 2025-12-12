# Design Document - V1.1 UI Enhancements

## Overview

Phiên bản V1.1 tập trung vào cải tiến trải nghiệm người dùng (UX) cho ứng dụng Customs Barcode Automation. Các cải tiến chính bao gồm:

1. **Cấu hình phương thức lấy mã vạch trong Settings** - Cho phép người dùng chọn API/Web/Auto
2. **Hợp nhất giao diện** - Gộp "Quản lý công ty" và "Chọn khoảng thời gian" thành một panel thống nhất
3. **Tìm kiếm công ty thông minh** - Gõ tên/MST tự động khớp và chọn công ty
4. **Mặc định không chọn tờ khai** - Khi xem trước, các tờ khai không được chọn sẵn
5. **Tùy chọn đặt tên file PDF** - Hỗ trợ 3 định dạng: MST_SốTK, SốHĐ_SốTK, SốVĐ_SốTK

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CustomsAutomationGUI                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Header Banner                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Control Panel                         │   │
│  │  ┌─────────────────────────────────────────────────────┐│   │
│  │  │         UnifiedCompanyPanel (NEW)                   ││   │
│  │  │  ┌─────────────────────────────────────────────┐   ││   │
│  │  │  │  Smart Search + Company Dropdown            │   ││   │
│  │  │  │  [Search: ___________] [Dropdown: ▼]        │   ││   │
│  │  │  └─────────────────────────────────────────────┘   ││   │
│  │  │  ┌─────────────────────────────────────────────┐   ││   │
│  │  │  │  Date Range (inline)                        │   ││   │
│  │  │  │  Từ ngày [__/__/____] đến ngày [__/__/____] │   ││   │
│  │  │  └─────────────────────────────────────────────┘   ││   │
│  │  │  [Quét công ty] [Làm mới] [Xem trước] [Lấy mã vạch]││   │
│  │  └─────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Preview Panel (unchecked default)          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. SettingsDialog Enhancement

```python
class SettingsDialog:
    """Enhanced Settings dialog with retrieval method and PDF naming options"""
    
    def __init__(self, parent, config_manager):
        self.retrieval_method_var: tk.StringVar  # "auto", "api", "web"
        self.pdf_naming_var: tk.StringVar  # "tax_code", "invoice", "bill_of_lading"
    
    def _create_retrieval_method_section(self) -> None:
        """Create dropdown for barcode retrieval method selection"""
        pass
    
    def _create_pdf_naming_section(self) -> None:
        """Create dropdown for PDF file naming format"""
        pass
    
    def save_settings(self) -> None:
        """Save all settings to config.ini"""
        pass
```

### 2. SmartCompanySearch Component

```python
class SmartCompanySearch:
    """Smart search component that filters and auto-selects companies"""
    
    def __init__(self, parent, companies: List[Company]):
        self.search_var: tk.StringVar
        self.company_var: tk.StringVar
        self.all_companies: List[Company]
    
    def filter_companies(self, search_text: str) -> List[Company]:
        """Filter companies by name or tax code"""
        pass
    
    def auto_select_if_exact_match(self, search_text: str) -> bool:
        """Auto-select company if exact match found"""
        pass
    
    def on_search_changed(self, event) -> None:
        """Handle search text change - filter and auto-select"""
        pass
```

### 3. UnifiedCompanyPanel

```python
class UnifiedCompanyPanel(ttk.Frame):
    """Unified panel combining company management and date selection"""
    
    def __init__(self, parent, company_scanner, preview_manager, logger):
        self.smart_search: SmartCompanySearch
        self.from_date_entry: DateEntry
        self.to_date_entry: DateEntry
    
    def _create_company_row(self) -> None:
        """Create company search and selection row"""
        pass
    
    def _create_date_row(self) -> None:
        """Create date range selection row (inline)"""
        pass
    
    def _create_action_buttons(self) -> None:
        """Create action buttons row"""
        pass
```

### 4. PDF Naming Service

```python
class PdfNamingService:
    """Service for generating PDF filenames based on naming format"""
    
    NAMING_FORMATS = {
        "tax_code": "{tax_code}_{declaration_number}.pdf",
        "invoice": "{invoice_number}_{declaration_number}.pdf",
        "bill_of_lading": "{bill_of_lading}_{declaration_number}.pdf"
    }
    
    def __init__(self, naming_format: str = "tax_code"):
        self.naming_format = naming_format
    
    def generate_filename(self, declaration: Declaration) -> str:
        """Generate filename based on selected format with fallback"""
        pass
```

## Data Models

### Configuration Extensions

```python
@dataclass
class BarcodeServiceConfig:
    # Existing fields...
    retrieval_method: str = "auto"  # "auto", "api", "web"
    pdf_naming_format: str = "tax_code"  # "tax_code", "invoice", "bill_of_lading"
```

### PDF Naming Format Enum

```python
class PdfNamingFormat(Enum):
    TAX_CODE = "tax_code"           # {tax_code}_{declaration_number}.pdf
    INVOICE = "invoice"             # {invoice_number}_{declaration_number}.pdf
    BILL_OF_LADING = "bill_of_lading"  # {bill_of_lading}_{declaration_number}.pdf
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Config Persistence Round-Trip (Retrieval Method)
*For any* valid retrieval method value ("auto", "api", "web"), saving to config.ini and reloading should return the same value.
**Validates: Requirements 1.2**

### Property 2: Config Persistence Round-Trip (PDF Naming)
*For any* valid PDF naming format ("tax_code", "invoice", "bill_of_lading"), saving to config.ini and reloading should return the same value.
**Validates: Requirements 5.2**

### Property 3: Smart Search Filtering
*For any* search text and list of companies, the filtered results should only contain companies where either the company name or tax code contains the search text (case-insensitive).
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Smart Search Auto-Select
*For any* search text that exactly matches a single company's name or tax code, the system should auto-select that company.
**Validates: Requirements 3.2**

### Property 5: Default Unchecked State
*For any* set of declarations loaded into the preview panel, all declarations should have unchecked checkboxes by default.
**Validates: Requirements 4.1, 4.4**

### Property 6: Select All Behavior
*For any* preview panel state, clicking "Select All" should result in all visible declarations being checked.
**Validates: Requirements 4.2**

### Property 7: Individual Toggle Behavior
*For any* declaration in the preview panel, clicking its checkbox should toggle only that declaration's selection state without affecting others.
**Validates: Requirements 4.3**

### Property 8: PDF Filename Generation
*For any* declaration and naming format, the generated filename should follow the selected format pattern. If the required field is empty, it should fallback to tax_code format.
**Validates: Requirements 5.3, 5.4, 5.5, 5.6**

## Error Handling

### Smart Search Errors
- Empty company list: Display "Không có công ty nào" message
- Search with no results: Keep dropdown empty, don't change selection
- Invalid characters in search: Sanitize input before filtering

### PDF Naming Errors
- Missing invoice_number: Fallback to tax_code format
- Missing bill_of_lading: Fallback to tax_code format
- Invalid characters in filename: Sanitize to valid filename characters

### Config Errors
- Invalid retrieval_method value: Default to "auto"
- Invalid pdf_naming_format value: Default to "tax_code"
- Config file not found: Create with defaults

## Testing Strategy

### Unit Testing
- Test SmartCompanySearch filtering logic
- Test PdfNamingService filename generation
- Test config persistence for new settings
- Test fallback behavior for empty fields

### Property-Based Testing
Using `hypothesis` library for Python:

1. **Config Round-Trip Tests**
   - Generate random valid config values
   - Save and reload, verify equality
   - Minimum 100 iterations

2. **Smart Search Tests**
   - Generate random company lists and search strings
   - Verify filtering correctness
   - Verify auto-select on exact match

3. **PDF Naming Tests**
   - Generate random declarations with various field combinations
   - Verify filename format correctness
   - Verify fallback behavior

4. **Selection State Tests**
   - Generate random declaration lists
   - Verify default unchecked state
   - Verify select all/toggle behavior

### Test Annotations
Each property-based test must include:
```python
# **Feature: v1.1-ui-enhancements, Property {number}: {property_text}**
# **Validates: Requirements X.Y**
```

## UI Layout Design

### Unified Company Panel Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Quản lý công ty & Thời gian                                             │
├─────────────────────────────────────────────────────────────────────────┤
│ [Quét công ty] [Làm mới]                                                │
│                                                                         │
│ Tìm kiếm: [________________________] [Xóa]                              │
│ Công ty:  [▼ Tất cả công ty_______________________]                     │
│ Đã tìm thấy 246 công ty                                                 │
│                                                                         │
│ Từ ngày [09/12/2025 ▼]  đến ngày [10/12/2025 ▼]                        │
├─────────────────────────────────────────────────────────────────────────┤
│ [Xem trước] [Lấy mã vạch] [Hủy] [Dừng]                                 │
│ [████████████████████░░░░░░░░░░░░░░░░░░░░] 45%                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Settings Dialog Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Cài đặt                                                          [X]   │
├─────────────────────────────────────────────────────────────────────────┤
│ Phương thức lấy mã vạch:                                               │
│ [▼ Tự động (API ưu tiên, Web dự phòng)]                                │
│   • Tự động (API ưu tiên, Web dự phòng)                                │
│   • Chỉ dùng API                                                        │
│   • Chỉ dùng Web                                                        │
│                                                                         │
│ Định dạng tên file PDF:                                                │
│ [▼ Mã số thuế + Số tờ khai]                                            │
│   • Mã số thuế + Số tờ khai (VD: 2300944637_107784915560.pdf)          │
│   • Số hóa đơn + Số tờ khai (VD: JYE-VN-P-25-259_107784915560.pdf)     │
│   • Số vận đơn + Số tờ khai (VD: FCHAN2512025_107784915560.pdf)        │
│                                                                         │
│                                              [Lưu]  [Hủy]              │
└─────────────────────────────────────────────────────────────────────────┘
```
