# Design Document: UI Improvements December 2024

## Overview

Tài liệu này mô tả thiết kế chi tiết cho các cải tiến giao diện người dùng của ứng dụng Customs Barcode Automation. Các thay đổi bao gồm:

1. **Loại bỏ chế độ Automatic**: Đơn giản hóa giao diện bằng cách chỉ giữ Manual mode
2. **Tìm kiếm công ty**: Thêm khả năng tìm kiếm nhanh theo mã số thuế hoặc tên công ty
3. **Bố cục ngày ngang**: Chuyển date range picker sang layout ngang
4. **Hiện đại hóa giao diện**: Áp dụng modern styling với màu sắc, effects và visual hierarchy

## Architecture

### Component Changes

```
┌─────────────────────────────────────────────────────────────┐
│                    CustomsAutomationGUI                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Control Panel (Simplified)                  ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │ Status: ● Connected    DB: ● Connected              │││
│  │  └─────────────────────────────────────────────────────┘││
│  │  [Statistics Panel - Unchanged]                         ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │         EnhancedManualPanel (Updated)               │││
│  │  │  ┌───────────────────────────────────────────────┐  ││
│  │  │  │ Output Directory Section                      │  ││
│  │  │  └───────────────────────────────────────────────┘  ││
│  │  │  ┌───────────────────────────────────────────────┐  ││
│  │  │  │ Company Section + Search Input                │  ││
│  │  │  │ [Search: ________] [Dropdown: ▼]              │  ││
│  │  │  └───────────────────────────────────────────────┘  ││
│  │  │  ┌───────────────────────────────────────────────┐  ││
│  │  │  │ Date Range (Horizontal)                       │  ││
│  │  │  │ Từ ngày [📅] đến ngày [📅]                    │  ││
│  │  │  └───────────────────────────────────────────────┘  ││
│  │  │  ┌───────────────────────────────────────────────┐  ││
│  │  │  │ Action Buttons + Progress                     │  ││
│  │  │  └───────────────────────────────────────────────┘  ││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
│  [Processed Declarations Panel - Unchanged]                  │
│  [Log Panel - Unchanged]                                     │
└─────────────────────────────────────────────────────────────┘
```

### Files to Modify

| File | Changes |
|------|---------|
| `gui/customs_gui.py` | Remove mode radio buttons, Start/Stop/Run Once buttons |
| `gui/enhanced_manual_panel.py` | Add company search, horizontal date layout, modern styling |
| `gui/styles.py` (new) | Centralized modern styling definitions |

## Components and Interfaces

### 1. ModernStyles Class (New)

```python
class ModernStyles:
    """Centralized styling for modern UI appearance"""
    
    # Color Palette
    PRIMARY_COLOR = "#0078D4"      # Microsoft Blue
    PRIMARY_HOVER = "#106EBE"      # Darker blue for hover
    SUCCESS_COLOR = "#107C10"      # Green
    ERROR_COLOR = "#D13438"        # Red
    WARNING_COLOR = "#FF8C00"      # Orange
    INFO_COLOR = "#0078D4"         # Blue
    
    # Background Colors
    BG_PRIMARY = "#FFFFFF"         # White
    BG_SECONDARY = "#F5F5F5"       # Light gray
    BG_HOVER = "#E8E8E8"           # Hover gray
    
    # Border Colors
    BORDER_COLOR = "#D1D1D1"       # Light border
    BORDER_FOCUS = "#0078D4"       # Focus border
    
    # Text Colors
    TEXT_PRIMARY = "#323130"       # Dark gray
    TEXT_SECONDARY = "#605E5C"     # Medium gray
    
    @staticmethod
    def configure_ttk_styles(root: tk.Tk) -> None:
        """Configure ttk styles for modern appearance"""
        pass
    
    @staticmethod
    def get_button_style() -> dict:
        """Get modern button styling"""
        pass
```

### 2. Company Search Filter

```python
class CompanySearchFilter:
    """Handles company filtering by tax code or name"""
    
    def __init__(self, companies: List[Tuple[str, str]]):
        """
        Args:
            companies: List of (tax_code, company_name) tuples
        """
        self.all_companies = companies
    
    def filter(self, query: str) -> List[Tuple[str, str]]:
        """
        Filter companies by query string
        
        Args:
            query: Search query (tax code or company name)
            
        Returns:
            Filtered list of companies
        """
        pass
```

### 3. Updated EnhancedManualPanel Methods

```python
# New/Modified methods in EnhancedManualPanel

def _create_company_section(self) -> None:
    """Create company section with search input"""
    # Add search entry above dropdown
    # Bind KeyRelease event for real-time filtering
    pass

def _filter_companies(self, event) -> None:
    """Filter company dropdown based on search input"""
    pass

def _create_date_range_section(self) -> None:
    """Create horizontal date range picker"""
    # Single row: "Từ ngày [picker] đến ngày [picker]"
    pass
```

## Data Models

### Company Display Format

```python
# Format: "TAX_CODE - COMPANY_NAME"
# Example: "0300391040 - CÔNG TY CỔ PHẦN BAO BÌ TÂN TIẾN"

company_display = f"{tax_code} - {company_name}"
```

### Style Configuration

```python
@dataclass
class StyleConfig:
    """Configuration for UI element styling"""
    background: str
    foreground: str
    border_color: str
    border_width: int
    padding: Tuple[int, int]
    font: Tuple[str, int, str]
    corner_radius: int  # For custom drawing
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Company Filter Completeness

*For any* search query and company list, the filtered result SHALL contain only companies where either the tax code OR company name contains the query string (case-insensitive).

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 2: Filter Preserves Default Option

*For any* filter operation, the "Tất cả công ty" option SHALL always be available in the dropdown regardless of filter results.

**Validates: Requirements 2.4**

### Property 3: Date Validation Consistency

*For any* date range selection, the validation logic SHALL reject ranges where from_date > to_date and accept ranges where from_date <= to_date.

**Validates: Requirements 3.3**

### Property 4: Status Color Mapping

*For any* status type (success, error, warning, info), the system SHALL apply the correct predefined color code consistently.

**Validates: Requirements 4.6**

## Error Handling

### Company Search Errors

| Error | Handling |
|-------|----------|
| Empty company list | Show "Không có công ty" message |
| Invalid characters in search | Ignore special regex characters |
| Database connection error | Show cached companies if available |

### Styling Errors

| Error | Handling |
|-------|----------|
| Style not found | Fall back to default ttk style |
| Invalid color code | Use default color |
| Font not available | Use system default font |

## Testing Strategy

### Unit Testing

Unit tests sẽ được viết để kiểm tra:
- Company filter logic với các input khác nhau
- Date validation logic
- Style configuration loading
- UI component initialization

### Property-Based Testing

Property-based tests sẽ sử dụng thư viện **Hypothesis** để kiểm tra:
- Company filtering với random queries và company lists
- Date validation với random date ranges
- Status color mapping với all status types

Mỗi property test sẽ:
- Chạy tối thiểu 100 iterations
- Được annotate với comment tham chiếu đến correctness property
- Sử dụng format: `**Feature: ui-improvements-dec-2024, Property {number}: {property_text}**`

### Test Files

| Test File | Purpose |
|-----------|---------|
| `tests/test_company_filter_unit.py` | Unit tests for company filtering |
| `tests/test_company_filter_properties.py` | Property tests for filtering |
| `tests/test_ui_styles_unit.py` | Unit tests for styling |
| `tests/test_date_validation_properties.py` | Property tests for date validation |
