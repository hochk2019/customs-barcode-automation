"""
Property-based tests for Preview Table Controller

These tests use Hypothesis to verify correctness properties for the preview table
controller, including filter correctness and sort ordering.

**Feature: v1.3-enhancements**
"""

import tkinter as tk
from tkinter import ttk
from hypothesis import given, strategies as st, settings, assume, HealthCheck
import pytest
from typing import List, Dict, Any

from gui.preview_table_controller import PreviewTableController, FilterStatus


# Strategy for generating result values
result_strategy = st.sampled_from(["✔", "✘", ""])

# Strategy for generating declaration numbers
declaration_number_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
    min_size=5,
    max_size=20
)

# Strategy for generating tax codes
tax_code_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Nd',)),
    min_size=10,
    max_size=13
)

# Strategy for generating dates in DD/MM/YYYY format
date_strategy = st.builds(
    lambda d, m, y: f"{d:02d}/{m:02d}/{y}",
    d=st.integers(min_value=1, max_value=28),
    m=st.integers(min_value=1, max_value=12),
    y=st.integers(min_value=2020, max_value=2025)
)

# Strategy for generating status values
status_strategy = st.sampled_from(["Thông quan", "Đã phân luồng", "Nhập mới", ""])

# Strategy for generating declaration types
declaration_type_strategy = st.sampled_from(["A11", "A12", "B11", "B12", "C11", ""])


def create_item(
    stt: int,
    declaration_number: str,
    tax_code: str,
    date: str,
    status: str,
    declaration_type: str,
    result: str
) -> Dict[str, Any]:
    """Create a preview item dictionary"""
    return {
        'stt': stt,
        'checkbox': '☐',
        'declaration_number': declaration_number,
        'tax_code': tax_code,
        'date': date,
        'status': status,
        'declaration_type': declaration_type,
        'bill_of_lading': '',
        'invoice_number': '',
        'result': result
    }


# Strategy for generating a list of preview items
@st.composite
def items_strategy(draw, min_size=0, max_size=50):
    """Generate a list of preview items with unique declaration numbers"""
    size = draw(st.integers(min_value=min_size, max_value=max_size))
    items = []
    used_numbers = set()
    
    for i in range(size):
        # Generate unique declaration number
        while True:
            decl_num = draw(declaration_number_strategy)
            if decl_num and decl_num not in used_numbers:
                used_numbers.add(decl_num)
                break
        
        item = create_item(
            stt=i + 1,
            declaration_number=decl_num,
            tax_code=draw(tax_code_strategy),
            date=draw(date_strategy),
            status=draw(status_strategy),
            declaration_type=draw(declaration_type_strategy),
            result=draw(result_strategy)
        )
        items.append(item)
    
    return items


# Strategy for filter status
filter_status_strategy = st.sampled_from([
    FilterStatus.ALL,
    FilterStatus.SUCCESS,
    FilterStatus.FAILED,
    FilterStatus.PENDING
])


class MockTreeview:
    """Mock Treeview for testing without Tk"""
    
    def __init__(self):
        self._items = {}
        self._counter = 0
    
    def get_children(self):
        return list(self._items.keys())
    
    def delete(self, item):
        if item in self._items:
            del self._items[item]
    
    def insert(self, parent, index, values=None, tags=None):
        self._counter += 1
        item_id = f"I{self._counter:04d}"
        self._items[item_id] = {'values': values, 'tags': tags}
        return item_id
    
    def item(self, item, option=None, **kwargs):
        if option == "values":
            return self._items.get(item, {}).get('values', ())
        elif option == "tags":
            return self._items.get(item, {}).get('tags', ())
        elif kwargs:
            if item in self._items:
                if 'values' in kwargs:
                    self._items[item]['values'] = kwargs['values']
                if 'tags' in kwargs:
                    self._items[item]['tags'] = kwargs['tags']
        return self._items.get(item, {})
    
    def identify_row(self, y):
        return None


# **Feature: v1.3-enhancements, Property 3: Filter Correctness**
# **Validates: Requirements 3.2**
@given(
    items=items_strategy(min_size=1, max_size=30),
    filter_status=filter_status_strategy
)
@settings(max_examples=100)
def test_property_filter_correctness(items, filter_status):
    """
    For any list of declarations and filter status, all visible items after
    filtering should match the selected status.
    
    **Feature: v1.3-enhancements, Property 3: Filter Correctness**
    **Validates: Requirements 3.2**
    """
    # Create controller with mock treeview
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    
    # Store items
    controller.store_items(items)
    
    # Apply filter
    controller.set_filter(filter_status.value)
    
    # Get visible items from mock treeview
    visible_items = []
    for item_id in mock_tree.get_children():
        values = mock_tree.item(item_id, "values")
        if values:
            visible_items.append({
                'declaration_number': values[2],  # COL_DECLARATION_NUMBER
                'result': values[9]  # COL_RESULT
            })
    
    # Verify all visible items match the filter
    for visible in visible_items:
        result = visible['result']
        
        if filter_status == FilterStatus.ALL:
            # All items should be visible
            pass
        elif filter_status == FilterStatus.SUCCESS:
            assert result == "✔", \
                f"Filter SUCCESS should only show items with result '✔', got '{result}'"
        elif filter_status == FilterStatus.FAILED:
            assert result == "✘", \
                f"Filter FAILED should only show items with result '✘', got '{result}'"
        elif filter_status == FilterStatus.PENDING:
            assert result not in ("✔", "✘"), \
                f"Filter PENDING should only show items without result, got '{result}'"


# **Feature: v1.3-enhancements, Property 3: Filter Correctness - Count Verification**
# **Validates: Requirements 3.2**
@given(items=items_strategy(min_size=1, max_size=30))
@settings(max_examples=100)
def test_property_filter_count_correctness(items):
    """
    For any list of declarations, the sum of filtered counts should equal total count.
    
    **Feature: v1.3-enhancements, Property 3: Filter Correctness**
    **Validates: Requirements 3.2**
    """
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Count items by status
    success_count = sum(1 for item in items if item['result'] == "✔")
    failed_count = sum(1 for item in items if item['result'] == "✘")
    pending_count = sum(1 for item in items if item['result'] not in ("✔", "✘"))
    
    # Verify counts
    assert success_count + failed_count + pending_count == len(items), \
        "Sum of filtered counts should equal total count"
    
    # Verify filter ALL shows all items
    controller.set_filter("all")
    assert len(mock_tree.get_children()) == len(items), \
        f"Filter ALL should show {len(items)} items, got {len(mock_tree.get_children())}"
    
    # Verify filter SUCCESS shows correct count
    controller.set_filter("success")
    assert len(mock_tree.get_children()) == success_count, \
        f"Filter SUCCESS should show {success_count} items, got {len(mock_tree.get_children())}"
    
    # Verify filter FAILED shows correct count
    controller.set_filter("failed")
    assert len(mock_tree.get_children()) == failed_count, \
        f"Filter FAILED should show {failed_count} items, got {len(mock_tree.get_children())}"
    
    # Verify filter PENDING shows correct count
    controller.set_filter("pending")
    assert len(mock_tree.get_children()) == pending_count, \
        f"Filter PENDING should show {pending_count} items, got {len(mock_tree.get_children())}"


# Strategy for sortable columns (excluding stt which is always re-numbered)
sortable_column_strategy = st.sampled_from([
    "declaration_number", "tax_code", "date", "status", "declaration_type"
])


# **Feature: v1.3-enhancements, Property 4: Sort Ordering**
# **Validates: Requirements 3.3, 3.4**
@given(
    items=items_strategy(min_size=2, max_size=30),
    column=sortable_column_strategy,
    reverse=st.booleans()
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example])
def test_property_sort_ordering(items, column, reverse):
    """
    For any list of declarations and sort column, after sorting ascending,
    each item should be less than or equal to the next item by that column's value.
    
    **Feature: v1.3-enhancements, Property 4: Sort Ordering**
    **Validates: Requirements 3.3, 3.4**
    """
    assume(len(items) >= 2)
    
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Apply sort
    controller.sort_by_column(column, reverse=reverse)
    
    # Get sorted values from treeview
    sorted_values = []
    col_index = PreviewTableController.COLUMN_NAMES.index(column)
    
    for item_id in mock_tree.get_children():
        values = mock_tree.item(item_id, "values")
        if values and len(values) > col_index:
            sorted_values.append(values[col_index])
    
    # Verify ordering
    for i in range(len(sorted_values) - 1):
        current = sorted_values[i]
        next_val = sorted_values[i + 1]
        
        # Convert to comparable values
        if column == 'stt':
            try:
                current = int(current) if current else 0
                next_val = int(next_val) if next_val else 0
            except (ValueError, TypeError):
                current = 0
                next_val = 0
        elif column == 'date':
            # Convert DD/MM/YYYY to YYYYMMDD for comparison
            try:
                parts = str(current).split('/')
                if len(parts) == 3:
                    current = f"{parts[2]}{parts[1]}{parts[0]}"
                parts = str(next_val).split('/')
                if len(parts) == 3:
                    next_val = f"{parts[2]}{parts[1]}{parts[0]}"
            except:
                pass
        else:
            current = str(current).lower() if current else ''
            next_val = str(next_val).lower() if next_val else ''
        
        if reverse:
            assert current >= next_val, \
                f"Sort descending by {column}: {current} should be >= {next_val}"
        else:
            assert current <= next_val, \
                f"Sort ascending by {column}: {current} should be <= {next_val}"


# **Feature: v1.3-enhancements, Property 4: Sort Toggle**
# **Validates: Requirements 3.3, 3.4**
@given(
    items=items_strategy(min_size=2, max_size=20),
    column=sortable_column_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example])
def test_property_sort_toggle(items, column):
    """
    For any column, toggling sort twice should reverse the order.
    
    **Feature: v1.3-enhancements, Property 4: Sort Ordering**
    **Validates: Requirements 3.3, 3.4**
    """
    assume(len(items) >= 2)
    
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # First toggle - should be ascending
    controller.toggle_sort(column)
    sort_col, is_desc = controller.get_sort_state()
    assert sort_col == column, f"Sort column should be {column}"
    assert is_desc == False, "First toggle should be ascending"
    
    # Second toggle - should be descending
    controller.toggle_sort(column)
    sort_col, is_desc = controller.get_sort_state()
    assert sort_col == column, f"Sort column should still be {column}"
    assert is_desc == True, "Second toggle should be descending"
    
    # Third toggle - should be ascending again
    controller.toggle_sort(column)
    sort_col, is_desc = controller.get_sort_state()
    assert is_desc == False, "Third toggle should be ascending again"


# **Feature: v1.3-enhancements, Property 4: Sort Stability**
# **Validates: Requirements 3.3, 3.4**
@given(items=items_strategy(min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_sort_preserves_items(items):
    """
    Sorting should not add or remove items, only reorder them.
    
    **Feature: v1.3-enhancements, Property 4: Sort Ordering**
    **Validates: Requirements 3.3, 3.4**
    """
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Get original declaration numbers
    original_numbers = {item['declaration_number'] for item in items}
    
    # Sort by various columns
    for column in ["stt", "declaration_number", "date"]:
        controller.sort_by_column(column, reverse=False)
        
        # Get sorted declaration numbers
        sorted_numbers = set()
        for item_id in mock_tree.get_children():
            values = mock_tree.item(item_id, "values")
            if values and len(values) > 2:
                sorted_numbers.add(values[2])  # declaration_number
        
        assert sorted_numbers == original_numbers, \
            f"Sorting by {column} should preserve all items"


# Test for filter and sort combination
@given(
    items=items_strategy(min_size=5, max_size=30),
    filter_status=filter_status_strategy,
    column=sortable_column_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.large_base_example])
def test_property_filter_and_sort_combination(items, filter_status, column):
    """
    Filtering and sorting should work correctly together.
    
    **Feature: v1.3-enhancements, Property 3: Filter Correctness**
    **Feature: v1.3-enhancements, Property 4: Sort Ordering**
    **Validates: Requirements 3.2, 3.3, 3.4**
    """
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Apply filter first
    controller.set_filter(filter_status.value)
    filtered_count = len(mock_tree.get_children())
    
    # Then apply sort
    controller.sort_by_column(column, reverse=False)
    sorted_count = len(mock_tree.get_children())
    
    # Count should remain the same after sorting
    assert filtered_count == sorted_count, \
        "Sorting should not change the number of filtered items"
    
    # Verify all visible items still match the filter
    for item_id in mock_tree.get_children():
        values = mock_tree.item(item_id, "values")
        if values and len(values) > 9:
            result = values[9]  # COL_RESULT
            
            if filter_status == FilterStatus.SUCCESS:
                assert result == "✔"
            elif filter_status == FilterStatus.FAILED:
                assert result == "✘"
            elif filter_status == FilterStatus.PENDING:
                assert result not in ("✔", "✘")


# Test for get_failed_declarations
@given(items=items_strategy(min_size=1, max_size=30))
@settings(max_examples=100)
def test_property_get_failed_declarations(items):
    """
    get_failed_declarations should return exactly the items with result '✘'.
    
    **Feature: v1.3-enhancements, Property 3: Filter Correctness**
    **Validates: Requirements 4.2**
    """
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Get failed declarations
    failed = controller.get_failed_declarations()
    
    # Count expected failures
    expected_failed = [
        item['declaration_number'] 
        for item in items 
        if item['result'] == "✘"
    ]
    
    assert set(failed) == set(expected_failed), \
        f"get_failed_declarations should return {expected_failed}, got {failed}"


# Test for clear functionality
@given(items=items_strategy(min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_clear_resets_state(items):
    """
    Clearing the controller should reset all state.
    
    **Feature: v1.3-enhancements, Property 3: Filter Correctness**
    **Validates: Requirements 3.2**
    """
    mock_tree = MockTreeview()
    controller = PreviewTableController(mock_tree)
    controller.store_items(items)
    
    # Set some state
    controller.set_filter("success")
    controller.sort_by_column("date", reverse=True)
    controller.set_file_path("test", "/path/to/file.pdf")
    controller.set_error_message("test", "Error message")
    
    # Clear
    controller.clear()
    
    # Verify state is reset
    assert controller.get_filter() == "all"
    sort_col, is_desc = controller.get_sort_state()
    assert sort_col is None
    assert is_desc == False
    assert controller.get_file_path("test") is None
    assert controller.get_error_message("test") is None
    assert len(mock_tree.get_children()) == 0
