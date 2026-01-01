# Design Document

## Overview

Hệ thống in tờ khai hải quan từ database ECUS5VNACCS. Sử dụng phương pháp **template-based generation** - copy file ECUS gốc và thay thế dữ liệu, đảm bảo giữ nguyên 100% định dạng.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Declaration Printer System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Database   │───▶│  Generator   │───▶│   Verifier   │       │
│  │  Connector   │    │              │    │              │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ ECUS5VNACCS  │    │  Templates   │    │   Reports    │       │
│  │   Database   │    │  (sample/)   │    │              │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. DeclarationGenerator Class

```python
class DeclarationGenerator:
    """Generator chính để tạo tờ khai từ database"""
    
    # Templates
    IMPORT_TEMPLATE = "sample/ToKhaiHQ7N_QDTQ_107807186540.xlsx"
    EXPORT_TEMPLATE = "sample/ToKhaiHQ7X_QDTQ_308064365030.xlsx"
    
    # Template numbers (để thay thế)
    IMPORT_TEMPLATE_NUMBER = "107807186540"
    EXPORT_TEMPLATE_NUMBER = "308064365030"
    
    def generate(self, declaration_number: str) -> Optional[str]:
        """Tạo file tờ khai từ database"""
        pass
    
    def _detect_declaration_type(self, declaration_number: str) -> str:
        """Xác định loại tờ khai: 'import' hoặc 'export'"""
        pass
    
    def _get_declaration_from_db(self, declaration_number: str) -> Tuple[Dict, List[Dict]]:
        """Lấy dữ liệu từ database"""
        pass
    
    def _adjust_pages_for_goods(self, ws, goods_count: int, template_goods_count: int) -> None:
        """Điều chỉnh số trang theo số lượng hàng"""
        pass
    
    def _replace_all_data(self, ws, declaration: Dict, goods_list: List[Dict]) -> int:
        """Thay thế tất cả dữ liệu"""
        pass
```

### 2. TemplateAnalyzer Class

```python
class TemplateAnalyzer:
    """Phân tích cấu trúc template ECUS"""
    
    def analyze_import_template(self) -> Dict:
        """Phân tích template nhập khẩu"""
        pass
    
    def analyze_export_template(self) -> Dict:
        """Phân tích template xuất khẩu"""
        pass
    
    def get_page_boundaries(self, template_type: str) -> List[int]:
        """Lấy ranh giới các trang"""
        pass
    
    def get_goods_section_info(self, template_type: str) -> Dict:
        """Lấy thông tin phần hàng hóa"""
        pass
```

### 3. CellMapping Class

```python
class CellMapping:
    """Quản lý vị trí các trường dữ liệu"""
    
    IMPORT_MAPPING = {
        # Page 1 (rows 1-75)
        'declaration_number': [(4, 5)],  # E4
        'barcode': [(3, 27)],  # AA3
        'customs_office': [(7, 12)],  # L7
        'registration_date': [(8, 7)],  # G8
        'tax_code': [(10, 8)],  # H10
        'company_name': [(11, 8)],  # H11
        'postal_code': [(13, 8)],  # H13
        'company_address': [(14, 8)],  # H14
        'phone': [(16, 8)],  # H16
        'exporter_name': [(23, 8)],  # H23
        'exporter_address': [(25, 8)],  # H25
        'exporter_country': [(27, 8)],  # H27
        'bill_of_lading': [(31, 4)],  # D31
        'arrival_date': [(35, 21)],  # U35
        'package_count': [(36, 11)],  # K36
        'gross_weight': [(37, 11)],  # K37
        'invoice_number': [(41, 10)],  # J41
        'total_pages': [(75, 21)],  # U75
        'total_items': [(75, 32)],  # AF75
        'page_number': [(1, 32)],  # AF1
        
        # Page 2 (rows 76-138)
        'page2_declaration_number': [(79, 5)],  # E79
        
        # Page 3+ (goods detail)
        'page3_declaration_number': [(142, 5)],  # E142
        'goods_start_row': 149,
        'goods_rows_per_item': 25,  # Số dòng mỗi item hàng hóa
    }
    
    EXPORT_MAPPING = {
        # Page 1 (rows 1-81)
        'declaration_number': [(4, 5)],  # E4
        'barcode': [(3, 23)],  # W3
        # ... các trường khác
        
        # Subsequent pages
        'page_boundaries': [1, 82, 145, 202, 259, 316, 373],
    }
```

### 4. PageManager Class

```python
class PageManager:
    """Quản lý thêm/xóa trang theo số lượng hàng"""
    
    def calculate_required_pages(self, goods_count: int, template_type: str) -> int:
        """Tính số trang cần thiết"""
        pass
    
    def add_goods_page(self, ws, page_number: int, template_ws) -> None:
        """Thêm một trang hàng hóa mới"""
        pass
    
    def remove_goods_page(self, ws, page_number: int) -> None:
        """Xóa một trang hàng hóa"""
        pass
    
    def update_page_numbers(self, ws, total_pages: int) -> None:
        """Cập nhật số trang trên tất cả các trang"""
        pass
    
    def copy_page_structure(self, source_ws, target_ws, source_start: int, target_start: int, rows: int) -> None:
        """Copy cấu trúc trang (formatting, merged cells, row heights)"""
        pass
```

### 5. DeclarationVerifier Class

```python
class DeclarationVerifier:
    """Xác minh file tạo ra với file gốc"""
    
    def verify_structure(self, generated_file: str, reference_file: str) -> Dict:
        """Xác minh cấu trúc file"""
        pass
    
    def compare_dimensions(self, ws_gen, ws_ref) -> bool:
        """So sánh kích thước"""
        pass
    
    def compare_column_widths(self, ws_gen, ws_ref) -> List[Dict]:
        """So sánh độ rộng cột"""
        pass
    
    def compare_row_heights(self, ws_gen, ws_ref) -> List[Dict]:
        """So sánh chiều cao hàng"""
        pass
    
    def compare_merged_cells(self, ws_gen, ws_ref) -> bool:
        """So sánh merged cells"""
        pass
```

## Data Models

### Declaration Data (from DTOKHAIMD)

```python
@dataclass
class DeclarationData:
    # Identification
    declaration_number: str  # SOTK
    declaration_type: str  # _XorN ('N' = Import, 'X' = Export)
    form_type: str  # MA_LH (E11, E42, G13, etc.)
    
    # Customs info
    customs_office: str  # MA_HQ
    customs_office_name: str  # TEN_HQ
    registration_date: datetime  # NGAY_DK
    
    # Company info
    company_tax_code: str  # MA_DV
    company_name: str  # _Ten_DV_L1
    company_address: str  # DIA_CHI_DV
    company_postal_code: str  # MA_BC_DV
    company_phone: str  # SO_DT_DV
    
    # Partner info
    partner_name: str  # DV_DT
    partner_country: str  # NUOC_XK or NUOC_NK
    
    # Transport info
    bill_of_lading: str  # VAN_DON
    transport_method: str  # TEN_PTVT
    arrival_date: datetime  # NGAYDEN
    
    # Package info
    package_count: int  # SO_KIEN
    package_unit: str  # DVT_KIEN
    gross_weight: float  # TR_LUONG
    weight_unit: str  # DVT_TR_LUONG
    
    # Value info
    total_value: float  # TONGTGKB
    currency: str  # MA_NT
    exchange_rate: float  # TYGIA_VND
    
    # Counts
    goods_count: int  # SOHANG
```

### Goods Item Data (from DHANGMDDK)

```python
@dataclass
class GoodsItem:
    item_number: int  # STTHANG
    hs_code: str  # MA_HANGKB
    description: str  # TEN_HANG
    quantity: float  # LUONG
    unit: str  # MA_DVT
    unit_price: float  # DGIA_KB
    total_value: float  # TRIGIA_KB
    origin_country: str  # NUOC_XX
    
    # Tax info
    import_tax_rate: float  # TS_XNK
    vat_rate: float  # TS_VAT
    import_tax: float  # THUE_XNK
    vat: float  # THUE_VAT
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Declaration type detection consistency
*For any* declaration number, if it starts with "10" the system should detect it as import, if it starts with "30" the system should detect it as export
**Validates: Requirements 1.1, 2.1**

### Property 2: Template selection correctness
*For any* import declaration, the system should use IMPORT_TEMPLATE; for any export declaration, the system should use EXPORT_TEMPLATE
**Validates: Requirements 1.3, 2.3**

### Property 3: Structure preservation
*For any* generated file, the dimensions (rows x columns), column widths, row heights, and merged cells should match the template exactly
**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 4: Declaration number replacement completeness
*For any* generated file, all occurrences of the template declaration number should be replaced with the new declaration number
**Validates: Requirements 1.4, 2.4, 5.1**

### Property 5: Page count adjustment
*For any* declaration with N goods items, the generated file should have exactly ceil(N / items_per_page) goods pages
**Validates: Requirements 7.1, 7.2**

### Property 6: Page number consistency
*For any* generated file with P pages, each page should show correct page number (1/P, 2/P, ..., P/P)
**Validates: Requirements 7.4, 7.5**

### Property 7: Goods data completeness
*For any* goods item in the declaration, all required fields (HS code, description, quantity, unit price, total value, origin) should be populated in the generated file
**Validates: Requirements 7.6**

## Error Handling

1. **Database connection failure**: Log error and return None
2. **Declaration not found**: Log warning and return None
3. **Template file not found**: Raise FileNotFoundError with clear message
4. **Invalid declaration number format**: Raise ValueError with format requirements
5. **Goods count mismatch**: Log warning but continue with available data

## Testing Strategy

### Unit Tests
- Test declaration type detection with various inputs
- Test template selection logic
- Test cell mapping accuracy
- Test page calculation logic

### Property-Based Tests (using Hypothesis)
- Property 1: Declaration type detection with random 12-digit numbers
- Property 2: Template selection with random declaration types
- Property 3: Structure comparison with generated files
- Property 4: Declaration number replacement verification
- Property 5: Page count calculation with various goods counts
- Property 6: Page number format verification
- Property 7: Goods data completeness check

### Integration Tests
- End-to-end test with real database connection
- Test with import declaration (10...)
- Test with export declaration (30...)
- Test with varying goods counts (1, 5, 10, 20, 50 items)
- Verify generated file opens correctly in Excel
