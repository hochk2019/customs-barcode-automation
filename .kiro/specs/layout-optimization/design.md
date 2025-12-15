# Design Document: Layout Optimization

## Overview

Tài liệu này mô tả thiết kế kỹ thuật cho việc tối ưu hóa bố cục giao diện ứng dụng Customs Barcode Automation. Mục tiêu chính là chuyển từ layout dọc (vertical stacking) sang layout 2 cột (two-column) với Control Panel bên trái và Preview Panel bên phải, đồng thời thu gọn các section điều khiển để tối ưu không gian hiển thị.

## Architecture

### Current Layout Structure
```
┌─────────────────────────────────────────┐
│            Header Banner                │
├─────────────────────────────────────────┤
│            Control Panel                │
│  ┌─────────────────────────────────┐    │
│  │ Status + Statistics             │    │
│  ├─────────────────────────────────┤    │
│  │ EnhancedManualPanel             │    │
│  │  - Output Directory             │    │
│  │  - Company & Time               │    │
│  │  - Action Buttons               │    │
│  │  - Preview Table                │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│       Processed Declarations            │
├─────────────────────────────────────────┤
│              Footer                     │
└─────────────────────────────────────────┘
```

### New Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│                    Header Banner                        │
│              (Unchanged - 105px height)                 │
├─────────────────────────┬───────────────────────────────┤
│    Control Panel        │       Preview Panel           │
│    (35-40% width)       │       (60-65% width)          │
│    min: 400px           │       min: 500px              │
│  ┌───────────────────┐  │  ┌─────────────────────────┐  │
│  │ Compact Status    │  │  │ Action Buttons Row      │  │
│  │ (40px)            │  │  │ (Xem trước, Lấy mã vạch)│  │
│  ├───────────────────┤  │  ├─────────────────────────┤  │
│  │ Output Directory  │  │  │ Filter & Selection Row  │  │
│  │ (50px)            │  │  │ (Chọn tất cả, Lọc...)   │  │
│  ├───────────────────┤  │  ├─────────────────────────┤  │
│  │ Company & Time    │  │  │                         │  │
│  │ (150px)           │  │  │   Preview Treeview      │  │
│  │ - Buttons inline  │  │  │   (expand to fill)      │  │
│  │ - Company combo   │  │  │                         │  │
│  │ - Recent pills    │  │  │                         │  │
│  │ - Date pickers    │  │  │                         │  │
│  └───────────────────┘  │  ├─────────────────────────┤  │
│                         │  │ Status Label            │  │
│  [Vertical space]       │  └─────────────────────────┘  │
│                         │                               │
├─────────────────────────┴───────────────────────────────┤
│                      Footer                             │
│              (Unchanged - 30px height)                  │
└─────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
CustomsAutomationGUI (root)
├── Header Banner (tk.Frame, fixed height=105px)
├── Main Content (ttk.PanedWindow, horizontal, sashwidth=6)
│   ├── Left Pane - Control Panel (ttk.Frame, min_width=400px)
│   │   ├── CompactStatusBar (ttk.Frame, height=40px)
│   │   ├── CompactOutputSection (ttk.LabelFrame, height=50px)
│   │   └── CompactCompanySection (ttk.LabelFrame, height=150px)
│   │       ├── ButtonRow (inline: Quét công ty, Làm mới)
│   │       ├── CompanyComboRow (AutocompleteCombobox + Xóa)
│   │       ├── RecentCompaniesPills (horizontal flow)
│   │       └── DateRangeRow (Từ ngày ... đến ngày)
│   └── Right Pane - Preview Panel (ttk.Frame, min_width=500px)
│       ├── ActionButtonsRow (Xem trước, Lấy mã vạch, Hủy, Dừng, Xuất log)
│       ├── FilterSelectionRow (Chọn tất cả, filters, Lọc dropdown)
│       ├── PreviewTreeview (expand to fill)
│       └── PreviewStatusLabel
└── Footer (tk.Frame, fixed height=30px)
```

## Components and Interfaces

### 1. TwoColumnLayout Class

```python
class TwoColumnLayout:
    """
    Manages the two-column layout using ttk.PanedWindow.
    
    Responsibilities:
    - Create and configure PanedWindow with horizontal orientation
    - Manage left (Control) and right (Preview) panes
    - Handle sash dragging and position persistence
    - Enforce minimum width constraints
    """
    
    def __init__(self, parent: tk.Widget, config_manager: ConfigurationManager):
        """Initialize two-column layout."""
        
    def get_left_pane(self) -> ttk.Frame:
        """Get the left pane (Control Panel) frame."""
        
    def get_right_pane(self) -> ttk.Frame:
        """Get the right pane (Preview Panel) frame."""
        
    def save_split_position(self) -> None:
        """Save current sash position to config."""
        
    def restore_split_position(self) -> None:
        """Restore sash position from config."""
        
    def set_split_ratio(self, ratio: float) -> None:
        """Set split ratio (0.0 to 1.0 for left pane width)."""
```

### 2. CompactStatusBar Class

```python
class CompactStatusBar(ttk.Frame):
    """
    Compact single-row status bar with inline statistics.
    
    Layout: [Status: ● Ready | DB: ● Connected] [Processed: X | Retrieved: Y | Errors: Z | Last: HH:MM] [⚙ Cấu hình DB] [⚙ Cài đặt]
    Height: 40px max
    """
    
    def __init__(self, parent: tk.Widget):
        """Initialize compact status bar."""
        
    def update_status(self, status: str, is_connected: bool) -> None:
        """Update status indicators."""
        
    def update_statistics(self, processed: int, retrieved: int, errors: int, last_run: datetime) -> None:
        """Update statistics display in inline format."""
```

### 3. CompactOutputSection Class

```python
class CompactOutputSection(ttk.LabelFrame):
    """
    Compact output directory section.
    
    Layout: [Thư mục lưu:] [Path Entry (truncated)] [Chọn...] [Mở]
    Height: 50px max
    """
    
    def __init__(self, parent: tk.Widget, config_manager: ConfigurationManager):
        """Initialize compact output section."""
        
    def get_output_path(self) -> str:
        """Get current output path."""
        
    def set_output_path(self, path: str) -> None:
        """Set output path with truncation for display."""
```

### 4. CompactCompanySection Class

```python
class CompactCompanySection(ttk.LabelFrame):
    """
    Compact company and time management section.
    
    Layout:
    Row 1: [Quét công ty] [Làm mới] [Company Combo (expanded)] [Xóa]
    Row 2: [Recent: pill1 pill2 pill3 pill4 pill5]
    Row 3: [Từ ngày] [DatePicker] [đến ngày] [DatePicker]
    
    Height: 150px max
    """
    
    def __init__(self, parent: tk.Widget, company_scanner: CompanyScanner, 
                 config_manager: ConfigurationManager):
        """Initialize compact company section."""
```

### 5. PreviewPanel Class

```python
class PreviewPanel(ttk.Frame):
    """
    Right-side preview panel containing action buttons and preview table.
    
    Layout:
    - Action buttons row (top)
    - Filter/selection row
    - Preview Treeview (expandable)
    - Status label (bottom)
    """
    
    def __init__(self, parent: tk.Widget, preview_manager: PreviewManager,
                 barcode_retriever, file_manager, tracking_db):
        """Initialize preview panel."""
```

### 6. Updated RecentCompaniesPanel

```python
class RecentCompaniesPanel(ttk.Frame):
    """
    Updated to support configurable max count.
    
    Changes:
    - MAX_RECENT now loaded from config (default 5, range 3-10)
    - Pill-shaped button styling
    - Horizontal flow layout
    """
    
    def __init__(self, parent: tk.Widget, config_manager: ConfigurationManager,
                 on_select: Optional[Callable[[str], None]] = None):
        """Initialize with configurable max count."""
        
    def set_max_recent(self, count: int) -> None:
        """Update max recent count and refresh display."""
```

### 7. Updated SettingsDialog

```python
class SettingsDialog:
    """
    Updated to include recent companies count setting.
    
    New section:
    - "Số lượng mã số thuế gần đây" spinbox (3-10, default 5)
    """
    
    def _create_recent_companies_section(self, parent: tk.Frame) -> None:
        """Create recent companies count setting section."""
```

## Data Models

### UIConfig Updates (models/config_models.py)

```python
@dataclass
class UIConfig:
    """UI configuration settings."""
    theme: str = 'light'
    notifications_enabled: bool = True
    sound_enabled: bool = True
    batch_limit: int = 20
    window_x: int = -1
    window_y: int = -1
    window_width: int = 1200
    window_height: int = 850
    # New fields for layout optimization
    panel_split_position: float = 0.38  # Left panel ratio (0.0-1.0)
    recent_companies_count: int = 5     # Range: 3-10
```

### ConfigurationManager Updates

```python
class ConfigurationManager:
    """Add methods for new UI settings."""
    
    def get_panel_split_position(self) -> float:
        """Get saved panel split position (default 0.38)."""
        
    def set_panel_split_position(self, position: float) -> None:
        """Save panel split position (clamped to 0.25-0.50)."""
        
    def get_recent_companies_count(self) -> int:
        """Get recent companies count (default 5, range 3-10)."""
        
    def set_recent_companies_count(self, count: int) -> None:
        """Save recent companies count (clamped to 3-10)."""
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Panel Split Position Persistence Round-Trip
*For any* valid split position value (0.25 to 0.50), saving to config and then loading should return the same value.
**Validates: Requirements 8.3, 8.4**

### Property 2: Recent Companies Count Clamping
*For any* integer value, setting recent companies count should clamp to valid range (3-10) and return a value within that range.
**Validates: Requirements 6.2**

### Property 3: Recent Companies Count Persistence Round-Trip
*For any* valid recent companies count (3-10), saving to config and then loading should return the same value.
**Validates: Requirements 6.3, 6.4**

### Property 4: Minimum Width Constraints
*For any* window width, the Control Panel width should never be less than 400px and Preview Panel width should never be less than 500px.
**Validates: Requirements 1.4, 8.2**

### Property 5: Statistics Format Consistency
*For any* combination of processed, retrieved, errors counts and last run time, the formatted statistics string should contain all four values in the expected inline format.
**Validates: Requirements 2.2**

### Property 6: Path Truncation Preserves End
*For any* file path longer than display width, truncation should preserve the last N characters (folder/filename) and prepend with "...".
**Validates: Requirements 3.3**

### Property 7: Section Height Constraints
*For any* content in compact sections, Status section height should not exceed 40px, Output section should not exceed 50px, and Company section should not exceed 150px.
**Validates: Requirements 2.3, 3.2, 4.4**

### Property 8: Split Ratio Proportionality
*For any* window resize, the ratio between Control Panel width and total content width should remain approximately equal to the saved split position (within 5% tolerance).
**Validates: Requirements 9.1**

## Error Handling

1. **Config Load Failure**: If panel_split_position or recent_companies_count cannot be loaded from config, use default values (0.38 and 5 respectively).

2. **Invalid Split Position**: If saved split position would violate minimum width constraints at current window size, adjust to nearest valid position.

3. **Window Too Small**: If window width is below 1000px, switch to single-column stacked layout instead of two-column.

4. **Sash Drag Beyond Limits**: Prevent sash from being dragged beyond minimum width constraints by using PanedWindow's minsize option.

## Testing Strategy

### Unit Tests
- Test ConfigurationManager methods for new settings (get/set panel_split_position, get/set recent_companies_count)
- Test path truncation logic with various path lengths
- Test statistics formatting with various input values
- Test clamping logic for split position and recent companies count

### Property-Based Tests
Using `hypothesis` library:

1. **Split Position Round-Trip**: Generate random floats in valid range, verify save/load consistency
2. **Recent Companies Count Clamping**: Generate random integers, verify clamping behavior
3. **Statistics Format**: Generate random stats values, verify format contains all values
4. **Path Truncation**: Generate random paths, verify truncation preserves filename

### Integration Tests
- Test two-column layout creation and sash functionality
- Test settings dialog saves and applies recent companies count
- Test layout responds correctly to window resize
- Test minimum width constraints are enforced

