# Complete Declaration Printing - Design Document

## Architecture Overview

### Current vs Target System

**Current System:**
```
Database → Simple Template (2 sheets) → Basic Excel (142 rows)
```

**Target System:**
```
Database → Template Analyzer → Multi-Page Generator → Complete Excel (1500+ rows)
```

## Component Design

### 1. Complete Template Analyzer
Phân tích file mẫu hoàn thiện để hiểu cấu trúc multi-page.

```python
class CompleteTemplateAnalyzer:
    """Phân tích cấu trúc file mẫu hoàn thiện"""
    
    def analyze_complete_sample(self, sample_path: str) -> TemplateStructure:
        """Phân tích file mẫu để extract pattern lặp lại"""
        
    def detect_page_boundaries(self, worksheet) -> List[PageBoundary]:
        """Tìm ranh giới giữa các trang trong file mẫu"""
        
    def extract_repeating_pattern(self) -> PagePattern:
        """Extract pattern lặp lại cho mỗi trang/hàng hóa"""
```

**Key Findings từ Analysis:**
- File xuất khẩu: 1568 hàng = ~27 trang x 57 hàng/trang
- File nhập khẩu: 509 hàng = ~9 trang x 57 hàng/trang  
- Mỗi trang chứa: Header (thông tin tờ khai) + Goods section (thông tin hàng hóa)
- Pattern lặp lại: Hàng 1-57, 58-114, 115-171, etc.

### 2. Multi-Page Excel Generator
Tạo file Excel multi-page từ template pattern.

```python
class MultiPageExcelGenerator:
    """Tạo file Excel multi-page giống ECUS"""
    
    def __init__(self, template_analyzer: CompleteTemplateAnalyzer):
        self.template_analyzer = template_analyzer
        self.page_pattern = None
        
    def generate_complete_declaration(self, 
                                    declaration_data: DeclarationData,
                                    output_path: str) -> str:
        """Tạo file Excel hoàn thiện"""
        
        # 1. Load template pattern
        self.page_pattern = self.template_analyzer.get_page_pattern(
            declaration_data.declaration_type
        )
        
        # 2. Calculate pages needed
        pages_needed = len(declaration_data.goods_list)
        
        # 3. Create workbook with single sheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        
        # 4. Generate each page
        for page_num, goods_item in enumerate(declaration_data.goods_list):
            self._generate_page(worksheet, page_num, declaration_data, goods_item)
            
        # 5. Save workbook
        workbook.save(output_path)
        return output_path
        
    def _generate_page(self, worksheet, page_num: int, 
                      declaration_data: DeclarationData, 
                      goods_item: GoodsItem) -> None:
        """Tạo một trang trong file Excel"""
        
        start_row = page_num * self.page_pattern.rows_per_page + 1
        
        # Copy template structure for this page
        self._copy_template_structure(worksheet, start_row)
        
        # Populate declaration data (same for all pages)
        self._populate_declaration_data(worksheet, start_row, declaration_data)
        
        # Populate goods data (specific for this page)
        self._populate_goods_data(worksheet, start_row, goods_item, page_num + 1)
```

### 3. Enhanced Data Extractor
Cải tiến data extractor để lấy đầy đủ dữ liệu từ database.

```python
class EnhancedDataExtractor(DeclarationDataExtractor):
    """Enhanced extractor cho complete declaration data"""
    
    def extract_complete_declaration_data(self, declaration_number: str) -> CompleteDeclarationData:
        """Extract đầy đủ dữ liệu cho complete declaration"""
        
        # 1. Basic declaration info
        basic_data = self.extract_from_database(declaration_number)
        
        # 2. Detailed goods information
        goods_details = self._extract_detailed_goods(declaration_number)
        
        # 3. Tax and duty information
        tax_info = self._extract_tax_information(declaration_number)
        
        # 4. Transport and container details
        transport_details = self._extract_transport_details(declaration_number)
        
        # 5. Customs processing info
        customs_info = self._extract_customs_processing_info(declaration_number)
        
        return CompleteDeclarationData(
            basic_info=basic_data,
            goods_details=goods_details,
            tax_info=tax_info,
            transport_details=transport_details,
            customs_info=customs_info
        )
```

### 4. Template Structure Models
Định nghĩa cấu trúc template để handle multi-page layout.

```python
@dataclass
class PagePattern:
    """Pattern cho một trang trong template"""
    rows_per_page: int = 57
    header_rows: range = field(default_factory=lambda: range(1, 25))
    goods_section: range = field(default_factory=lambda: range(25, 45))
    footer_rows: range = field(default_factory=lambda: range(45, 57))
    
@dataclass
class TemplateStructure:
    """Cấu trúc tổng thể của template"""
    declaration_type: DeclarationType
    total_pages_in_sample: int
    page_pattern: PagePattern
    field_mappings: Dict[str, CellMapping]
    
@dataclass
class CellMapping:
    """Mapping cho một field trong template"""
    relative_row: int  # Vị trí tương đối trong page
    column: int
    format_type: str  # 'text', 'number', 'date', 'currency'
    repeats_per_page: bool = False  # True nếu field này lặp lại mỗi trang
```

## Data Flow Design

### 1. Template Analysis Phase
```
Sample Files → CompleteTemplateAnalyzer → TemplateStructure → Cache
```

### 2. Data Extraction Phase  
```
Declaration Number → EnhancedDataExtractor → CompleteDeclarationData
```

### 3. Excel Generation Phase
```
CompleteDeclarationData + TemplateStructure → MultiPageExcelGenerator → Complete Excel File
```

## Database Schema Extensions

### Enhanced Queries
```sql
-- Detailed goods query with all fields
SELECT 
    dh.STT, dh.MA_HANG, dh.TEN_HANG, dh.SL_HANG, dh.DVT,
    dh.DON_GIA, dh.TRI_GIA, dh.NUOC_SX, dh.XUAT_XU,
    dh.THUE_NK, dh.THUE_TTDB, dh.THUE_VAT, dh.THUE_BVMT,
    dh.TRONG_LUONG, dh.TRONG_LUONG_TINH_THUE
FROM DHANGMDDK dh 
WHERE dh.SOTK = ?
ORDER BY dh.STT

-- Tax calculation details
SELECT 
    dt.LOAI_THUE, dt.TY_LE_THUE, dt.TIEN_THUE, dt.TIEN_GIAM_THUE
FROM DTHUEMDDK dt
WHERE dt.SOTK = ?

-- Container and transport details  
SELECT 
    dc.SO_CONTAINER, dc.LOAI_CONTAINER, dc.TRONG_LUONG_CONTAINER,
    dvt.SO_VAN_DON, dvt.NGAY_VAN_DON, dvt.PHUONG_TIEN
FROM DCONTAINERMD dc, DVANTAIMD dvt
WHERE dc.SOTK = ? AND dvt.SOTK = ?
```

## File Structure Design

### Output File Naming
```
ToKhaiHQ7X_QDTQ_305254403660.xlsx  # Export clearance
ToKhaiHQ7N_QDTQ_107772836360.xlsx  # Import clearance  
ToKhaiHQ7X_PL_308003563620.xlsx    # Export routing
ToKhaiHQ7N_PL_105205185850.xlsx    # Import routing
```

### Excel Sheet Structure
```
Single Sheet: "TKN" or "TKX" (combined)
├── Page 1 (Rows 1-57): Declaration Header + Goods Item 1
├── Page 2 (Rows 58-114): Declaration Header + Goods Item 2  
├── Page 3 (Rows 115-171): Declaration Header + Goods Item 3
└── ... (repeat for each goods item)
```

## Integration Design

### Preview Panel Integration
```python
class CompleteDeclarationPrinter(DeclarationPrinter):
    """Enhanced printer cho complete declarations"""
    
    def __init__(self):
        super().__init__()
        self.template_analyzer = CompleteTemplateAnalyzer()
        self.multi_page_generator = MultiPageExcelGenerator(self.template_analyzer)
        self.enhanced_extractor = EnhancedDataExtractor()
        
    def print_complete_declaration(self, declaration_number: str) -> str:
        """Print complete declaration giống ECUS"""
        
        # 1. Extract complete data
        complete_data = self.enhanced_extractor.extract_complete_declaration_data(
            declaration_number
        )
        
        # 2. Generate complete Excel file
        output_path = self.multi_page_generator.generate_complete_declaration(
            complete_data,
            self._get_output_path(declaration_number, complete_data.declaration_type)
        )
        
        return output_path
```

### Backward Compatibility
- Giữ nguyên interface của DeclarationPrinter hiện tại
- Thêm flag `use_complete_format: bool = True` để switch giữa old/new format
- Fallback về simple format nếu complete format fails

## Performance Considerations

### Memory Management
- Stream processing cho file Excel lớn
- Lazy loading của template patterns
- Garbage collection sau mỗi page generation

### Optimization Strategies
- Cache template structures sau first analysis
- Batch database queries cho multiple declarations
- Parallel processing cho independent pages

### Progress Tracking
```python
def generate_with_progress(self, declaration_data: CompleteDeclarationData, 
                          progress_callback: Callable[[int, int], None]) -> str:
    """Generate với progress tracking"""
    
    total_pages = len(declaration_data.goods_list)
    
    for page_num, goods_item in enumerate(declaration_data.goods_list):
        self._generate_page(worksheet, page_num, declaration_data, goods_item)
        progress_callback(page_num + 1, total_pages)
```

## Error Handling Design

### Validation Layers
1. **Template Validation**: Verify sample files exist và readable
2. **Data Validation**: Check completeness của database data  
3. **Generation Validation**: Verify Excel file structure
4. **Output Validation**: Check file size và format

### Recovery Strategies
- Fallback to simple format nếu complete generation fails
- Partial generation với warning cho missing data
- Detailed error logging với specific failure points

## Testing Strategy

### Unit Tests
- Template analysis accuracy
- Data extraction completeness  
- Excel generation correctness
- Performance benchmarks

### Integration Tests
- End-to-end complete declaration generation
- Database connectivity và query performance
- File output validation against samples

### Performance Tests
- Large declaration handling (100+ goods items)
- Memory usage monitoring
- Concurrent generation testing