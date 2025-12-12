# Design Document - Bug Fixes December 2024

## Overview

Tài liệu này mô tả thiết kế chi tiết cho việc sửa 6 bugs quan trọng được phát hiện sau khi testing Enhanced Manual Mode. Các bugs ảnh hưởng đến khả năng lấy mã vạch, hiệu suất, và trải nghiệm người dùng.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Enhanced Manual Panel                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Output Dir   │  │ Date Picker  │  │ Company      │      │
│  │ Selector     │  │ (Calendar)   │  │ Dropdown     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Preview Manager                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Query with DISTINCT to prevent duplicates          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Barcode Retriever                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ API Method   │→ │ Primary Web  │→ │ Backup Web   │      │
│  │ (10s timeout)│  │ (Fallback)   │  │ (Fallback)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - Adaptive selectors with fallbacks                 │   │
│  │  - Session reuse for performance                     │   │
│  │  - Detailed error logging with HTML structure        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. BarcodeRetriever Enhancements

**Purpose:** Fix API timeout, improve selector robustness, optimize performance

**Key Changes:**

```python
class BarcodeRetriever:
    # Configuration
    API_TIMEOUT = 10  # Reduced from 30
    WEB_TIMEOUT = 15  # Separate timeout for web scraping
    
    # Adaptive selectors with fallbacks
    FIELD_SELECTORS = {
        'taxCode': [
            'taxCode', 'ma_dv', 'maDoanhnghiep', 
            'mst', 'tax_code', 'MaDV'
        ],
        'declarationNumber': [
            'declarationNumber', 'so_tk', 'soToKhai', 
            'so_to_khai', 'SoTK'
        ],
        'declarationDate': [
            'declarationDate', 'ngay_dk', 'ngayToKhai',
            'ngay_to_khai', 'NgayDK'
        ],
        'customsOffice': [
            'customsOffice', 'ma_hq', 'maHaiQuan',
            'ma_hai_quan', 'MaHQ'
        ]
    }
    
    # Session reuse for performance
    def __init__(self, config, logger):
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(
            max_retries=1,
            pool_connections=10,
            pool_maxsize=10
        ))
```

**New Methods:**

- `_try_adaptive_selectors()`: Try multiple selector variations
- `_log_html_structure()`: Log page structure when selectors fail
- `_cache_working_selectors()`: Cache successful selectors for reuse
- `_skip_failed_method()`: Skip consistently failing methods

### 2. PreviewManager Duplicate Prevention

**Purpose:** Ensure unique declarations in preview

**Key Changes:**

```python
class PreviewManager:
    def get_declarations_for_preview(self, company_code, from_date, to_date):
        """Get unique declarations for preview"""
        query = """
            SELECT DISTINCT
                SO_TOKHAI,
                MA_DV,
                NGAY_DK,
                MA_HQ,
                MIN(ROWID) as ROWID
            FROM DTOKHAIMD
            WHERE MA_DV = ?
                AND NGAY_DK BETWEEN ? AND ?
            GROUP BY SO_TOKHAI, MA_DV, NGAY_DK, MA_HQ
            ORDER BY NGAY_DK DESC, SO_TOKHAI
        """
```

### 3. EnhancedManualPanel UI Improvements

**Purpose:** Add output directory selector, calendar picker, searchable dropdown

**New Components:**

```python
class EnhancedManualPanel:
    def _create_output_directory_section(self):
        """Create output directory selection UI"""
        frame = ttk.Frame(self)
        
        ttk.Label(frame, text="Thư mục lưu:").pack(side=tk.LEFT)
        
        self.output_var = tk.StringVar(value=self.config.output_path)
        entry = ttk.Entry(frame, textvariable=self.output_var, width=50)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(frame, text="Chọn...", 
                               command=self._browse_output_directory)
        browse_btn.pack(side=tk.LEFT)
        
        return frame
    
    def _create_date_picker(self, parent, variable):
        """Create date picker with calendar"""
        from tkcalendar import DateEntry
        
        date_entry = DateEntry(
            parent,
            textvariable=variable,
            date_pattern='dd/mm/yyyy',
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            locale='vi_VN'
        )
        return date_entry
    
    def _create_searchable_company_dropdown(self):
        """Create company dropdown with search/filter"""
        self.company_combo = ttk.Combobox(
            self,
            textvariable=self.company_var,
            state='normal',  # Allow typing
            width=50
        )
        
        # Bind key release to filter
        self.company_combo.bind('<KeyRelease>', self._filter_companies)
        
        return self.company_combo
    
    def _filter_companies(self, event):
        """Filter company list based on typed text"""
        typed = self.company_var.get().lower()
        
        if not typed:
            # Show all companies
            self.company_combo['values'] = self.all_companies
            return
        
        # Filter by tax code or company name
        filtered = [
            company for company in self.all_companies
            if typed in company.lower()
        ]
        
        if filtered:
            self.company_combo['values'] = filtered
        else:
            self.company_combo['values'] = ["Không tìm thấy"]
```

## Data Models

### Configuration Extension

```python
@dataclass
class BarcodeServiceConfig:
    """Extended configuration for barcode service"""
    api_url: str
    api_timeout: int = 10  # Reduced from 30
    web_timeout: int = 15  # Separate timeout for web
    primary_web_url: str
    backup_web_url: str
    output_path: str  # User-configurable output directory
    max_retries: int = 1  # Reduced from 3
    session_reuse: bool = True  # Enable session reuse
```

### Selector Cache

```python
@dataclass
class SelectorCache:
    """Cache for working selectors"""
    tax_code_selector: Optional[str] = None
    declaration_number_selector: Optional[str] = None
    declaration_date_selector: Optional[str] = None
    customs_office_selector: Optional[str] = None
    submit_button_selector: Optional[str] = None
    last_updated: Optional[datetime] = None
    
    def is_valid(self, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        if not self.last_updated:
            return False
        age = datetime.now() - self.last_updated
        return age.total_seconds() < (max_age_hours * 3600)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Output directory persistence
*For any* selected output directory path, when the application restarts, the system should load the same output directory path from configuration
**Validates: Requirements 1.5**

### Property 2: Timeout reduction effectiveness
*For any* API call that would timeout, the system should fail faster (within 10 seconds) than the old timeout (30 seconds)
**Validates: Requirements 2.1**

### Property 3: Selector fallback completeness
*For any* form field that needs to be filled, if the primary selector fails, the system should try all alternative selectors before giving up
**Validates: Requirements 2.2, 2.4**

### Property 4: Declaration uniqueness
*For any* query result set, each declaration number should appear at most once in the preview list
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Date format consistency
*For any* date selected from the calendar, the resulting string should match the DD/MM/YYYY format
**Validates: Requirements 4.3**

### Property 6: Company filter correctness
*For any* typed text in the company dropdown, all displayed companies should contain that text (case-insensitive) in either tax code or company name
**Validates: Requirements 5.2, 5.3, 5.4**

### Property 7: Session reuse efficiency
*For any* batch of declarations being processed, the HTTP session should be reused across all requests rather than creating new sessions
**Validates: Requirements 6.4**

## Error Handling

### 1. API Timeout Handling

```python
def _try_api_with_timeout(self, declaration):
    """Try API with reduced timeout and proper error handling"""
    try:
        response = self.session.post(
            self.config.api_url,
            data=soap_request,
            headers=headers,
            timeout=self.config.api_timeout
        )
        return self._parse_soap_response(response.text)
    except requests.Timeout:
        self.logger.error(
            f"API timeout after {self.config.api_timeout}s for {declaration.id}"
        )
        return None
    except requests.RequestException as e:
        self.logger.error(f"API request failed: {e}")
        return None
```

### 2. Selector Failure Logging

```python
def _log_html_structure_on_failure(self, driver, field_name):
    """Log HTML structure when selectors fail"""
    try:
        # Get page source
        html = driver.page_source
        
        # Log relevant parts
        self.logger.error(f"Failed to find field: {field_name}")
        self.logger.debug(f"Page title: {driver.title}")
        self.logger.debug(f"Current URL: {driver.current_url}")
        
        # Log all form fields
        forms = driver.find_elements(By.TAG_NAME, 'form')
        for i, form in enumerate(forms):
            self.logger.debug(f"Form {i}: {form.get_attribute('outerHTML')[:500]}")
        
        # Log all input fields
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        for inp in inputs:
            self.logger.debug(
                f"Input: id={inp.get_attribute('id')}, "
                f"name={inp.get_attribute('name')}, "
                f"type={inp.get_attribute('type')}"
            )
    except Exception as e:
        self.logger.error(f"Failed to log HTML structure: {e}")
```

### 3. Duplicate Detection

```python
def _validate_unique_declarations(self, declarations):
    """Validate that declarations are unique"""
    seen = set()
    duplicates = []
    
    for decl in declarations:
        key = (decl.declaration_number, decl.tax_code, decl.declaration_date)
        if key in seen:
            duplicates.append(decl)
        seen.add(key)
    
    if duplicates:
        self.logger.warning(
            f"Found {len(duplicates)} duplicate declarations: "
            f"{[d.declaration_number for d in duplicates]}"
        )
    
    return len(duplicates) == 0
```

### 4. Invalid Date Handling

```python
def _validate_date_format(self, date_string):
    """Validate date format DD/MM/YYYY"""
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        self.logger.error(f"Invalid date format: {date_string}")
        messagebox.showerror(
            "Lỗi",
            f"Ngày không hợp lệ: {date_string}\n"
            "Định dạng đúng: DD/MM/YYYY"
        )
        return False
```

## Testing Strategy

### Unit Testing

**Framework:** pytest

**Test Files:**
- `tests/test_barcode_retriever_unit.py` - Update existing tests
- `tests/test_preview_manager_unit.py` - Update existing tests  
- `tests/test_enhanced_manual_panel_unit.py` - Update existing tests

**Key Test Cases:**

1. **Timeout Tests:**
   - Test API timeout occurs within 10 seconds
   - Test web scraping timeout occurs within 15 seconds

2. **Selector Tests:**
   - Test each selector variation works
   - Test fallback chain is tried in order
   - Test HTML logging on failure

3. **Duplicate Prevention:**
   - Test DISTINCT query returns unique declarations
   - Test duplicate detection validation

4. **UI Tests:**
   - Test output directory selection and persistence
   - Test date picker format
   - Test company dropdown filtering

### Property-Based Testing

**Framework:** Hypothesis

**Test Files:**
- `tests/test_barcode_retriever_properties.py` - Update existing
- `tests/test_preview_manager_properties.py` - Update existing
- `tests/test_enhanced_manual_panel_properties.py` - Update existing

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with property number from design doc

**Property Tests:**

1. **Property 1: Output directory persistence**
   - Generate random valid directory paths
   - Save to config, restart, verify loaded path matches

2. **Property 2: Timeout reduction effectiveness**
   - Generate scenarios that would timeout
   - Verify timeout occurs within new limit

3. **Property 3: Selector fallback completeness**
   - Generate random HTML structures
   - Verify all selectors are tried before failure

4. **Property 4: Declaration uniqueness**
   - Generate random declaration lists with duplicates
   - Verify query returns unique declarations only

5. **Property 5: Date format consistency**
   - Generate random valid dates
   - Select from calendar, verify format is DD/MM/YYYY

6. **Property 6: Company filter correctness**
   - Generate random company lists and search terms
   - Verify all results contain search term

7. **Property 7: Session reuse efficiency**
   - Generate batch of declarations
   - Verify same session object is used for all requests

### Integration Testing

**Test Scenarios:**

1. End-to-end barcode retrieval with all fallbacks
2. Preview with duplicate prevention
3. Complete UI workflow with all new features

## Performance Considerations

### 1. Timeout Optimization

**Before:**
- API timeout: 30s
- Total time per declaration: ~37s (30s API + 7s fallback)

**After:**
- API timeout: 10s
- Web timeout: 15s
- Total time per declaration: ~12s (10s API + 2s fallback)

**Improvement:** ~67% faster

### 2. Session Reuse

**Before:**
- New session per request
- Connection overhead: ~1-2s per request

**After:**
- Reuse session across batch
- Connection overhead: ~1-2s for entire batch

**Improvement:** Significant for large batches

### 3. Selector Caching

**Before:**
- Try all selectors every time
- ~10-15 selector attempts per field

**After:**
- Use cached working selector first
- ~1-2 selector attempts per field

**Improvement:** ~80% reduction in selector attempts

## Deployment Considerations

### Configuration Changes

**config.ini additions:**
```ini
[BarcodeService]
api_timeout = 10
web_timeout = 15
max_retries = 1
session_reuse = true
output_path = C:\CustomsData\Barcodes

[UI]
enable_calendar_picker = true
enable_company_search = true
```

### Dependencies

**New dependencies:**
```
tkcalendar>=1.6.1  # For calendar date picker
```

### Migration

1. Update config.ini with new settings
2. Clear selector cache (if exists)
3. Test with small batch first
4. Monitor logs for selector failures
5. Update selectors if needed based on logs

## Backward Compatibility

- All changes are backward compatible
- Old config files will use default values
- Existing functionality preserved
- New features are additive only

## Security Considerations

- Output directory path validation to prevent path traversal
- Sanitize user input in company search
- Validate date input to prevent injection
- Session cookies properly managed and cleared

## Monitoring and Logging

### Enhanced Logging

```python
# Log selector attempts
self.logger.debug(f"Trying selector: {selector} for field: {field_name}")

# Log HTML structure on failure
self.logger.error(f"All selectors failed for {field_name}")
self.logger.debug(f"Page HTML: {html_snippet}")

# Log performance metrics
self.logger.info(
    f"Barcode retrieved in {elapsed_time:.2f}s "
    f"using method: {method_name}"
)

# Log duplicate detection
self.logger.warning(f"Filtered {duplicate_count} duplicate declarations")
```

### Metrics to Track

- Average retrieval time per method
- Selector success rate
- Duplicate detection rate
- User interaction patterns (which features used most)

## Future Enhancements

1. **Intelligent Selector Learning:**
   - Machine learning to predict best selectors
   - Automatic selector discovery

2. **Parallel Processing:**
   - Process multiple declarations concurrently
   - Further performance improvements

3. **Advanced Caching:**
   - Cache barcode PDFs locally
   - Reduce redundant API calls

4. **User Preferences:**
   - Remember user's preferred date ranges
   - Save favorite companies

5. **Offline Mode:**
   - Queue requests when offline
   - Process when connection restored
