# Design Document - Enhanced Manual Mode

## Overview

Enhanced Manual Mode là một tính năng cải tiến cho phép người dùng kiểm soát chi tiết hơn trong việc xử lý tờ khai hải quan. Thiết kế tập trung vào:
- Workflow rõ ràng từng bước
- UI/UX trực quan với date pickers và preview
- Performance tốt với background threading
- Khả năng hủy/dừng các thao tác dài

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                  GUI Layer                          │
│  ┌──────────────────────────────────────────────┐  │
│  │  EnhancedManualPanel                         │  │
│  │  - Company Scanner Button                    │  │
│  │  - Company Dropdown                          │  │
│  │  - Date Range Pickers (From/To)             │  │
│  │  - Preview Button                            │  │
│  │  - Declaration Preview Table                 │  │
│  │  - Download Button                           │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Business Logic Layer                   │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ CompanyScanner│  │PreviewManager│               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐               │
│  │EcusConnector │  │TrackingDB    │               │
│  └──────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. EnhancedManualPanel (GUI Component)

**Responsibility**: Hiển thị UI cho Enhanced Manual Mode

**Key Methods**:
- `scan_companies()`: Trigger company scan
- `preview_declarations()`: Show declaration preview
- `download_selected()`: Download barcodes for selected declarations
- `cancel_operation()`: Cancel ongoing operation

**UI Elements**:
- Button: "Quét công ty", "Làm mới"
- Combobox: Company selection
- DateEntry: From date, To date
- Button: "Xem trước", "Lấy mã vạch", "Dừng"
- Treeview: Declaration preview with checkboxes
- Label: Status and count display

### 2. CompanyScanner (Business Logic)

**Responsibility**: Quét và lưu trữ danh sách công ty

**Methods**:
```python
def scan_companies(days_back: int = 90) -> List[Tuple[str, str]]:
    """Scan database for unique companies"""
    
def save_companies_to_db(companies: List[Tuple[str, str]]) -> None:
    """Save companies to tracking database"""
```

### 3. PreviewManager (Business Logic)

**Responsibility**: Quản lý preview và selection của tờ khai

**Methods**:
```python
def get_declarations_preview(
    from_date: datetime,
    to_date: datetime,
    tax_codes: Optional[List[str]] = None
) -> List[Declaration]:
    """Get declarations for preview"""
    
def get_selected_declarations() -> List[Declaration]:
    """Get user-selected declarations"""
```

### 4. Database Extensions

**EcusConnector additions**:
- `scan_all_companies(days_back)` ✅ (already added)
- `get_declarations_by_date_range(from_date, to_date, tax_codes)` ✅ (already added)

**TrackingDatabase additions**:
- `add_or_update_company(tax_code, company_name)` ✅ (already exists)
- `get_all_companies()` ✅ (already exists)

## Data Models

### Company (already exists in tracking DB)
```python
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    tax_code TEXT UNIQUE,
    company_name TEXT,
    last_seen TIMESTAMP,
    created_at TIMESTAMP
)
```

### DeclarationSelection (new, in-memory only)
```python
@dataclass
class DeclarationSelection:
    declaration: Declaration
    selected: bool = True
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system.*

### Property 1: Company scan completeness
*For any* time period, scanning companies should return all unique tax codes that have declarations in that period
**Validates: Requirements 1.1**

### Property 2: Date range validation
*For any* date range where end_date < start_date, the system should reject the input and display an error
**Validates: Requirements 2.3**

### Property 3: Preview accuracy
*For any* selected company and date range, the preview should show exactly the declarations that match those criteria
**Validates: Requirements 3.1, 3.2**

### Property 4: Selection consistency
*For any* set of selected declarations, downloading should process exactly those declarations and no others
**Validates: Requirements 4.2, 4.3**

### Property 5: Stop operation safety
*For any* ongoing download operation, stopping should save all completed downloads and not corrupt any data
**Validates: Requirements 9.2, 9.3**

## Error Handling

### Company Scan Errors
- Database connection failure → Display error, allow retry
- No companies found → Display "Không tìm thấy công ty nào"
- Timeout → Cancel scan, display partial results

### Preview Errors
- Invalid date range → Display validation error
- Query timeout → Allow cancel, display error
- No declarations found → Display "Không tìm thấy tờ khai nào"

### Download Errors
- Network failure → Retry with exponential backoff
- User cancellation → Save progress, display summary
- Individual declaration failure → Continue with others, log error

## Testing Strategy

### Unit Tests
- Date range validation logic
- Company scan and save
- Declaration selection tracking
- Cancel/stop flag handling

### Property-Based Tests
- Property 1: Company scan completeness (using Hypothesis)
- Property 2: Date range validation (using Hypothesis)
- Property 3: Preview accuracy (using Hypothesis)
- Property 4: Selection consistency (using Hypothesis)
- Property 5: Stop operation safety (using Hypothesis)

### Integration Tests
- End-to-end workflow: Scan → Select → Preview → Download
- Cancel operations at each stage
- Database persistence across sessions

## UI/UX Design

### Workflow States

```
State 1: Initial
- "Quét công ty" enabled
- All other controls disabled
- Message: "Vui lòng quét công ty trước"

State 2: Companies Loaded
- Company dropdown enabled
- Date pickers enabled
- "Xem trước" enabled when company + dates selected

State 3: Preview Displayed
- Declaration table visible with checkboxes
- "Lấy mã vạch" enabled when declarations selected
- "Xem trước" can be clicked again to refresh

State 4: Downloading
- All inputs disabled
- "Dừng" button visible
- Progress bar updating

State 5: Complete
- All inputs enabled
- Results displayed
- Ready for next operation
```

### Layout

```
┌─────────────────────────────────────────────────────┐
│ Manual Mode Settings                                │
│                                                     │
│ [Quét công ty]  [Làm mới]                         │
│                                                     │
│ Lọc theo công ty: [Dropdown ▼]                    │
│                                                     │
│ Từ ngày: [📅 DD/MM/YYYY]                          │
│ Đến ngày: [📅 DD/MM/YYYY]                         │
│                                                     │
│ [Xem trước]  [Lấy mã vạch]  [Dừng]               │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ Preview: Đã chọn 15/20 tờ khai              │   │
│ │ ☑ Chọn tất cả                               │   │
│ │ ─────────────────────────────────────────── │   │
│ │ ☑ 302934380950 | 0700809357 | 01/12/2024  │   │
│ │ ☑ 302934380951 | 0700809357 | 02/12/2024  │   │
│ │ ☐ 302934380952 | 0700809357 | 03/12/2024  │   │
│ │ ...                                         │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ [▓▓▓▓▓▓░░░░] Đang xử lý 6/15...                   │
└─────────────────────────────────────────────────────┘
```

## Performance Considerations

### Background Threading
- Company scan: Run in background thread
- Preview query: Run in background thread
- Download: Run in background thread with progress updates

### Caching
- Cache company list in memory after load
- Cache preview results until parameters change

### Optimization
- Limit preview to 1000 declarations max
- Use pagination if needed
- Index database queries properly

## Security Considerations

- Validate all date inputs to prevent SQL injection
- Sanitize company names before display
- Limit query result size to prevent memory issues
- Validate file paths before saving barcodes
