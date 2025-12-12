# Design Document: Search UX Improvement

## Overview

Cải tiến component AutocompleteCombobox để cung cấp trải nghiệm tìm kiếm mượt mà như Google Search. Các thay đổi chính bao gồm:
- Loại bỏ việc select text khi focus
- Giảm debounce delay để phản hồi nhanh hơn
- Cập nhật dropdown mà không đóng/mở lại
- Thêm visual feedback về số kết quả
- Cải thiện keyboard navigation
- Thêm nút clear (X)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  EnhancedSearchCombobox                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Entry Widget                              [X]      │    │
│  │  "Nhập mã số thuế hoặc tên công ty..."              │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Result Count Label: "Tìm thấy 5 công ty"           │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Dropdown Listbox                                    │    │
│  │  ├─ 2300944637 - GOLDEN LOGISTICS CO.,LTD           │    │
│  │  ├─ 2301138516 - ABC COMPANY                        │    │
│  │  └─ ...                                              │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### EnhancedSearchCombobox

Thay thế AutocompleteCombobox hiện tại với các cải tiến:

```python
class EnhancedSearchCombobox(ttk.Frame):
    """
    Enhanced search combobox with smooth UX.
    
    Features:
    - No text selection on focus
    - Fast debounce (150ms)
    - Smooth dropdown updates
    - Result count display
    - Clear button
    - Keyboard navigation
    """
    
    DEBOUNCE_DELAY = 150  # Reduced from 300ms
    
    def __init__(
        self,
        parent: tk.Widget,
        values: List[str] = None,
        on_select: Optional[Callable[[str], None]] = None,
        placeholder: str = "Nhập để tìm kiếm...",
        no_match_text: str = "Không tìm thấy",
        show_result_count: bool = True,
        **kwargs
    ):
        ...
    
    # Core methods
    def _on_key_press(self, event) -> None: ...
    def _on_key_release(self, event) -> None: ...
    def _do_filter(self) -> None: ...
    def _update_dropdown(self, values: List[str]) -> None: ...
    def _update_result_count(self, count: int) -> None: ...
    
    # Cursor management
    def _preserve_cursor(self) -> None: ...
    def _restore_cursor(self, position: int) -> None: ...
    
    # Dropdown management
    def _open_dropdown(self) -> None: ...
    def _close_dropdown(self) -> None: ...
    def _is_dropdown_open(self) -> bool: ...
    
    # Clear button
    def _show_clear_button(self) -> None: ...
    def _hide_clear_button(self) -> None: ...
    def _on_clear_click(self) -> None: ...
    
    # Keyboard navigation
    def _on_down_arrow(self) -> None: ...
    def _on_up_arrow(self) -> None: ...
    def _on_enter(self) -> None: ...
    def _on_escape(self) -> None: ...
    def _on_tab(self) -> None: ...
```

### Key Changes from Current Implementation

1. **Sử dụng ttk.Frame thay vì kế thừa ttk.Combobox**
   - Cho phép kiểm soát tốt hơn layout và behavior
   - Có thể thêm clear button và result count label

2. **Tách biệt Entry và Listbox**
   - Entry widget cho input
   - Toplevel window với Listbox cho dropdown
   - Kiểm soát hoàn toàn việc mở/đóng dropdown

3. **Cursor Management**
   - Lưu cursor position trước mỗi thao tác
   - Restore cursor sau khi filter/update

4. **Dropdown State Machine**
   - CLOSED → OPEN (khi gõ hoặc click)
   - OPEN → OPEN (khi tiếp tục gõ - chỉ update content)
   - OPEN → CLOSED (khi click outside, Escape, hoặc select)

## Data Models

```python
@dataclass
class SearchState:
    """State of the search combobox"""
    text: str = ""
    cursor_position: int = 0
    dropdown_open: bool = False
    selected_index: int = -1
    filtered_values: List[str] = field(default_factory=list)
    all_values: List[str] = field(default_factory=list)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Cursor Position Preservation
*For any* sequence of typing actions, the cursor position SHALL always be at the end of the text after each keystroke, and no text SHALL be selected.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Filter Result Correctness
*For any* search text and list of values, the filtered results SHALL contain only values that include the search text (case-insensitive), and the count displayed SHALL equal the number of filtered results.
**Validates: Requirements 2.2, 2.3, 2.4, 3.1, 3.2**

### Property 3: Dropdown State Consistency
*For any* sequence of user interactions, the dropdown SHALL remain open while typing continues, and SHALL only close on explicit close actions (click outside, Escape, selection).
**Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4**

### Property 4: Keyboard Navigation Correctness
*For any* dropdown with N items, pressing Down arrow K times SHALL highlight item at index min(K-1, N-1), and pressing Up arrow SHALL move highlight in reverse.
**Validates: Requirements 5.1, 5.2**

### Property 5: Clear Button Visibility
*For any* text state, the clear button SHALL be visible if and only if the text is non-empty and not the placeholder.
**Validates: Requirements 6.1, 6.3**

## Error Handling

1. **Empty values list**: Show placeholder, disable dropdown
2. **No matches**: Show "Không tìm thấy kết quả" message
3. **Widget destroyed during async operation**: Check widget existence before updating
4. **Invalid callback**: Catch and log exceptions from on_select callback

## Testing Strategy

### Unit Tests
- Test cursor position after various typing patterns
- Test filter logic with different search texts
- Test dropdown state transitions
- Test keyboard navigation
- Test clear button visibility

### Property-Based Tests (using Hypothesis)
- Property 1: Cursor position preservation
- Property 2: Filter result correctness
- Property 3: Dropdown state consistency
- Property 4: Keyboard navigation correctness
- Property 5: Clear button visibility

Each property test will use `@settings(max_examples=100)` as per project standards.
