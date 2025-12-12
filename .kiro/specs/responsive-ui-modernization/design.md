# Design Document: Responsive UI Modernization

## Overview

Nâng cấp giao diện ứng dụng Customs Barcode Automation để có layout responsive, hiện đại và dễ sử dụng. Giải quyết vấn đề các panel bị ẩn khi cửa sổ không full screen.

**Framework**: Tkinter (giữ nguyên)
**Approach**: Sử dụng `pack()` với `fill` và `expand` options để tạo responsive layout

## Architecture

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER (Fixed 105px)                                        │
│ Logo | Company Name | Status | Buttons                      │
├─────────────────────────────────────────────────────────────┤
│ OUTPUT DIRECTORY PANEL (Fixed ~50px)                        │
│ [Path Entry                    ] [Chọn...] [Mở]             │
├─────────────────────────────────────────────────────────────┤
│ COMPANY & DATE PANEL (Fixed ~180px)                         │
│ [Quét công ty] [Làm mới]                                    │
│ Công ty: [Autocomplete Combobox                        ▼]   │
│ Gần đây: [MST1] [MST2] [MST3] [MST4] [MST5]                │
│ Từ ngày [DD/MM/YYYY] đến ngày [DD/MM/YYYY]                 │
├─────────────────────────────────────────────────────────────┤
│ PREVIEW TABLE PANEL (Expandable - fills remaining space)    │
│ ☐ Chọn tất cả | Đã chọn: 0/0 | ☐ Chưa thông quan | ☐ XNK TC│
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☐ │ Số tờ khai │ MST │ Ngày │ Trạng thái │ Loại hình │ │ │
│ │───┼────────────┼─────┼──────┼────────────┼───────────┼─│ │
│ │   │            │     │      │            │           │▲│ │
│ │   │            │     │      │            │           │ │ │
│ │   │            │     │      │            │           │▼│ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ ACTION BUTTONS (Fixed ~60px)                                │
│ [Xem trước] [Lấy mã vạch] [Hủy] [Dừng] [====Progress====]  │
├─────────────────────────────────────────────────────────────┤
│ STATISTICS BAR (Fixed ~35px)                                │
│ Processed: 0 | Retrieved: 0 | Errors: 0 | Last: Never      │
├─────────────────────────────────────────────────────────────┤
│ FOOTER (Fixed 30px)                                         │
│ Designer: Học HK | Email | Phone                            │
└─────────────────────────────────────────────────────────────┘
```

### Responsive Behavior

1. **Fixed Panels**: Header, Output Directory, Company Panel, Action Buttons, Statistics, Footer
   - Use `pack(fill=tk.X)` - expand horizontally only
   - Use `pack_propagate(False)` with fixed height

2. **Expandable Panel**: Preview Table
   - Use `pack(fill=tk.BOTH, expand=True)` - expand both directions
   - Treeview with scrollbars handles overflow

3. **Minimum Window Size**: 900x600 pixels
   - Prevents layout breakage
   - Ensures all controls visible

## Components and Interfaces

### 1. ResponsiveMainWindow (Modified CustomsAutomationGUI)

```python
class CustomsAutomationGUI:
    def __init__(self, root, ...):
        # Set minimum window size
        self.root.minsize(900, 600)
        
        # Create layout in order (top to bottom)
        self._create_header_banner()      # Fixed 105px
        self._create_main_content_area()  # Contains all panels
        self._create_footer()             # Fixed 30px
    
    def _create_main_content_area(self):
        # Main scrollable container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Fixed panels
        self._create_output_directory_panel()  # ~50px
        self._create_company_panel()           # ~180px
        
        # Expandable panel
        self._create_preview_panel()           # Fills remaining
        
        # Fixed panels at bottom
        self._create_action_buttons()          # ~60px
        self._create_statistics_bar()          # ~35px
```

### 2. AutocompleteCombobox (New Component)

```python
class AutocompleteCombobox(ttk.Combobox):
    """
    Combobox with autocomplete/filter functionality.
    Combines search and dropdown into single control.
    """
    def __init__(self, parent, values=[], **kwargs):
        super().__init__(parent, **kwargs)
        self.all_values = values
        self.bind('<KeyRelease>', self._on_key_release)
    
    def _on_key_release(self, event):
        # Filter values based on typed text
        typed = self.get().lower()
        filtered = [v for v in self.all_values if typed in v.lower()]
        self['values'] = filtered if filtered else ['Không tìm thấy']
    
    def set_values(self, values):
        self.all_values = values
        self['values'] = values
```

### 3. RecentCompaniesPanel (New Component)

```python
class RecentCompaniesPanel(ttk.Frame):
    """
    Displays up to 5 recently used tax codes as quick-select buttons.
    """
    def __init__(self, parent, on_select_callback):
        super().__init__(parent)
        self.on_select = on_select_callback
        self.buttons = []
        self.max_recent = 5
    
    def update_recent(self, tax_codes: List[str]):
        # Clear existing buttons
        for btn in self.buttons:
            btn.destroy()
        self.buttons.clear()
        
        # Create new buttons for recent tax codes
        for tax_code in tax_codes[:self.max_recent]:
            btn = ttk.Button(self, text=tax_code, 
                           command=lambda tc=tax_code: self.on_select(tc))
            btn.pack(side=tk.LEFT, padx=2)
            self.buttons.append(btn)
        
        # Hide if no recent companies
        if not tax_codes:
            self.pack_forget()
        else:
            self.pack(fill=tk.X, pady=2)
```

### 4. StatisticsBar (New Component)

```python
class StatisticsBar(ttk.Frame):
    """
    Bottom status bar showing download statistics.
    """
    def __init__(self, parent):
        super().__init__(parent, height=35)
        self.pack_propagate(False)
        
        self.processed_var = tk.StringVar(value="0")
        self.retrieved_var = tk.StringVar(value="0")
        self.errors_var = tk.StringVar(value="0")
        self.last_run_var = tk.StringVar(value="Never")
        
        self._create_labels()
    
    def update_stats(self, processed, retrieved, errors, last_run):
        self.processed_var.set(str(processed))
        self.retrieved_var.set(str(retrieved))
        self.errors_var.set(str(errors))
        self.last_run_var.set(last_run or "Never")
```

## Data Models

### RecentCompanies Storage

```python
# Store in tracking.db or config.ini
recent_companies = {
    "tax_codes": ["2300944637", "0101234567", ...],  # Max 5
    "last_updated": "2024-12-11T10:30:00"
}
```

### Statistics State

```python
# In-memory during session
statistics = {
    "total_processed": 0,
    "total_retrieved": 0,
    "total_errors": 0,
    "last_run": None  # datetime
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Header Height Invariant
*For any* window resize operation, the header height SHALL remain exactly 105 pixels.
**Validates: Requirements 2.2**

### Property 2: Preview Table Expansion
*For any* window height increase, the preview table height SHALL increase by the same amount (minus fixed panel heights).
**Validates: Requirements 5.1, 5.2**

### Property 3: Action Buttons Visibility
*For any* window size >= minimum (900x600), all action buttons SHALL be visible within the window bounds.
**Validates: Requirements 6.2**

### Property 4: Company Filter Correctness
*For any* search string typed in the autocomplete combobox, all displayed options SHALL contain the search string (case-insensitive).
**Validates: Requirements 4.2, 8.2**

### Property 5: Statistics Counter Accuracy
*For any* successful barcode download, the "Barcodes Retrieved" counter SHALL increment by exactly 1.
**Validates: Requirements 10.1**

### Property 6: Error Counter Accuracy
*For any* failed barcode download, the "Errors" counter SHALL increment by exactly 1.
**Validates: Requirements 10.2**

### Property 7: Recent Companies Update
*For any* successful barcode download for a company, that company's tax code SHALL appear in the recent companies list.
**Validates: Requirements 11.3**

### Property 8: Company Panel Height Invariant
*For any* window resize operation, the company panel height SHALL remain approximately 180 pixels (±10px).
**Validates: Requirements 4.5**

## Error Handling

1. **Window Too Small**: Enforce minimum size 900x600, prevent resize below
2. **No Companies Found**: Display "Không tìm thấy" in combobox
3. **Statistics Update Failure**: Log error, continue operation
4. **Recent Companies Load Failure**: Start with empty list, don't block startup

## Testing Strategy

### Unit Tests
- AutocompleteCombobox filtering logic
- RecentCompaniesPanel button creation
- StatisticsBar update methods
- Layout component creation

### Property-Based Tests (using Hypothesis)
- Property 1: Header height invariant after random resize operations
- Property 4: Company filter correctness with random search strings
- Property 5-6: Statistics counter accuracy with random download results
- Property 7: Recent companies update with random tax codes

### Integration Tests
- Full window resize behavior
- Statistics update from EnhancedManualPanel to StatisticsBar
- Recent companies persistence across simulated restarts
