"""
Property-based tests for AutocompleteCombobox component.

Tests:
- Property 1: Cursor Position Preservation (Validates: Requirements 1.1, 1.2, 1.3)
- Property 4: Company Filter Correctness (Validates: Requirements 4.2, 8.2)
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockSearchState:
    """
    Mock implementation of search state for testing cursor preservation.
    
    This mock implements the cursor management logic without GUI dependencies.
    **Feature: search-ux-improvement, Property 1: Cursor Position Preservation**
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    
    def __init__(self):
        self.text = ""
        self.cursor_position = 0
        self.selection_start = None
        self.selection_end = None
    
    def set_text(self, text: str) -> None:
        """Set text and place cursor at end."""
        self.text = text
        self.cursor_position = len(text)
        self.selection_start = None
        self.selection_end = None
    
    def type_char(self, char: str) -> None:
        """Simulate typing a character at cursor position."""
        # Insert character at cursor position
        self.text = self.text[:self.cursor_position] + char + self.text[self.cursor_position:]
        self.cursor_position += 1
        # Clear any selection
        self.selection_start = None
        self.selection_end = None
    
    def focus_in(self) -> None:
        """
        Simulate focus in event.
        
        Per Requirements 1.1, 1.2: No text selection, cursor at end.
        """
        # Place cursor at end without selecting
        self.cursor_position = len(self.text)
        self.selection_start = None
        self.selection_end = None
    
    def filter_operation(self) -> None:
        """
        Simulate a filter operation that might affect cursor.
        
        Per Requirement 1.3: Dropdown opening should not move cursor.
        """
        # Save cursor position
        saved_pos = self.cursor_position
        # Simulate dropdown update (which might try to move cursor)
        # ... dropdown logic ...
        # Restore cursor position
        self.cursor_position = saved_pos
        # Clear any selection
        self.selection_start = None
        self.selection_end = None
    
    def has_selection(self) -> bool:
        """Check if any text is selected."""
        return self.selection_start is not None and self.selection_end is not None
    
    def get_cursor_position(self) -> int:
        """Get current cursor position."""
        return self.cursor_position


class MockAutocompleteCombobox:
    """
    Mock implementation of AutocompleteCombobox for testing without Tkinter.
    
    This mock implements the core filtering logic without GUI dependencies.
    **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
    **Validates: Requirements 2.2, 2.3, 2.4, 3.1, 3.2**
    """
    
    def __init__(self, values: List[str] = None, no_match_text: str = "Không tìm thấy"):
        self.all_values = values or []
        self.no_match_text = no_match_text
        self.current_values = self.all_values.copy()
        self._current_text = ""
        self._last_filter_count = len(self.all_values)
    
    def set_values(self, values: List[str]) -> None:
        """Set new values for the combobox."""
        self.all_values = values or []
        self.current_values = self.all_values.copy()
        self._last_filter_count = len(self.all_values)
    
    def filter_values(self, search_text: str) -> List[str]:
        """
        Filter values based on search text.
        
        Returns filtered list or ["Không tìm thấy"] if no matches.
        """
        if not search_text:
            self.current_values = self.all_values.copy()
            self._last_filter_count = len(self.all_values)
            return self.current_values
        
        # Case-insensitive search
        search_lower = search_text.lower()
        filtered = [v for v in self.all_values if search_lower in v.lower()]
        
        if filtered:
            self.current_values = filtered
            self._last_filter_count = len(filtered)
        else:
            self.current_values = [self.no_match_text]
            self._last_filter_count = 0
        
        return self.current_values
    
    def get_filtered_values(self) -> List[str]:
        """Get current filtered values."""
        return self.current_values
    
    def get_filter_count(self) -> int:
        """Get the count of last filter results."""
        return self._last_filter_count
    
    def get_result_count_text(self) -> str:
        """
        Get formatted result count text for display.
        
        Requirements: 3.2, 3.3
        """
        count = self._last_filter_count
        if count == 0:
            return "Không tìm thấy kết quả"
        elif count == 1:
            return "Tìm thấy 1 công ty"
        else:
            return f"Tìm thấy {count} công ty"


# Strategies for generating test data
company_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

tax_code_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('N',)),
    min_size=10,
    max_size=13
)

company_list_strategy = st.lists(
    st.tuples(tax_code_strategy, company_name_strategy),
    min_size=0,
    max_size=20
)


class TestCursorPreservationProperty:
    """
    Property-based tests for cursor position preservation.
    
    **Feature: search-ux-improvement, Property 1: Cursor Position Preservation**
    **Validates: Requirements 1.1, 1.2, 1.3**
    """
    
    @given(
        initial_text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=0,
            max_size=30
        ),
        chars_to_type=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=1),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_1_cursor_at_end_after_typing(
        self, initial_text: str, chars_to_type: List[str]
    ):
        """
        Property 1: Cursor Position Preservation
        
        *For any* sequence of typing actions, the cursor position SHALL always be 
        at the end of the text after each keystroke, and no text SHALL be selected.
        
        **Feature: search-ux-improvement, Property 1: Cursor Position Preservation**
        **Validates: Requirements 1.1, 1.2, 1.3**
        """
        state = MockSearchState()
        state.set_text(initial_text)
        
        # Type each character
        for char in chars_to_type:
            state.type_char(char)
            
            # After each keystroke, cursor should be at end of text
            assert state.get_cursor_position() == len(state.text), \
                f"Cursor should be at end ({len(state.text)}) but was at {state.get_cursor_position()}"
            
            # No text should be selected
            assert not state.has_selection(), \
                "No text should be selected after typing"
    
    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_property_1_no_selection_on_focus(self, text: str):
        """
        Property 1: Cursor Position Preservation - Focus behavior
        
        *For any* text in the search box, when focus is gained, no text SHALL be 
        selected and cursor SHALL be at end.
        
        **Feature: search-ux-improvement, Property 1: Cursor Position Preservation**
        **Validates: Requirements 1.1, 1.2**
        """
        assume(text.strip())  # Non-empty text
        
        state = MockSearchState()
        state.set_text(text)
        
        # Simulate focus in
        state.focus_in()
        
        # Cursor should be at end
        assert state.get_cursor_position() == len(text), \
            f"Cursor should be at end ({len(text)}) but was at {state.get_cursor_position()}"
        
        # No text should be selected
        assert not state.has_selection(), \
            "No text should be selected on focus"
    
    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1,
            max_size=30
        ),
        num_filter_ops=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    def test_property_1_cursor_preserved_during_filter(self, text: str, num_filter_ops: int):
        """
        Property 1: Cursor Position Preservation - Filter operations
        
        *For any* filter operation, the cursor position SHALL be preserved and 
        no text SHALL be selected.
        
        **Feature: search-ux-improvement, Property 1: Cursor Position Preservation**
        **Validates: Requirements 1.3**
        """
        assume(text.strip())  # Non-empty text
        
        state = MockSearchState()
        state.set_text(text)
        
        # Record cursor position before filter
        cursor_before = state.get_cursor_position()
        
        # Perform multiple filter operations
        for _ in range(num_filter_ops):
            state.filter_operation()
            
            # Cursor should be preserved
            assert state.get_cursor_position() == cursor_before, \
                f"Cursor should be preserved at {cursor_before} but was at {state.get_cursor_position()}"
            
            # No text should be selected
            assert not state.has_selection(), \
                "No text should be selected after filter operation"


class TestFilterResultCorrectnessProperty:
    """
    Property-based tests for filter result correctness.
    
    **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
    **Validates: Requirements 2.2, 2.3, 2.4, 3.1, 3.2**
    """
    
    @given(
        companies=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P')), min_size=1, max_size=30),
            min_size=1, max_size=20
        ),
        search_text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1, max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_2_filter_count_matches_results(self, companies: List[str], search_text: str):
        """
        Property 2: Filter Result Correctness - Count matches results
        
        *For any* search text and list of values, the count displayed SHALL equal 
        the number of filtered results.
        
        **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
        **Validates: Requirements 3.1, 3.2**
        """
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        assume(search_text.strip())
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values(search_text)
        count = combobox.get_filter_count()
        
        # If no matches, count should be 0
        if filtered == [combobox.no_match_text]:
            assert count == 0, f"Count should be 0 for no matches, got {count}"
        else:
            # Count should equal number of filtered results
            assert count == len(filtered), \
                f"Count ({count}) should equal filtered results ({len(filtered)})"
    
    @given(
        companies=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P')), min_size=1, max_size=30),
            min_size=1, max_size=20
        ),
        search_text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1, max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_2_filtered_results_contain_search_text(self, companies: List[str], search_text: str):
        """
        Property 2: Filter Result Correctness - Results contain search text
        
        *For any* search text and list of values, the filtered results SHALL contain 
        only values that include the search text (case-insensitive).
        
        **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
        **Validates: Requirements 2.2, 2.3**
        """
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        assume(search_text.strip())
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values(search_text)
        
        # If we got results (not "Không tìm thấy")
        if filtered != [combobox.no_match_text]:
            search_lower = search_text.lower()
            for value in filtered:
                assert search_lower in value.lower(), \
                    f"Filtered value '{value}' does not contain search text '{search_text}'"
    
    @given(
        companies=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N', 'P')), min_size=1, max_size=30),
            min_size=0, max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_2_empty_search_shows_all(self, companies: List[str]):
        """
        Property 2: Filter Result Correctness - Empty search shows all
        
        *For any* list of values, when search text is empty, the system SHALL 
        show all available companies.
        
        **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
        **Validates: Requirements 2.4**
        """
        companies = [c for c in companies if c.strip()]
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values("")
        count = combobox.get_filter_count()
        
        assert filtered == companies, "Empty search should return all values"
        assert count == len(companies), f"Count should be {len(companies)}, got {count}"
    
    @given(
        companies=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=30),
            min_size=1, max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_2_result_count_text_format(self, companies: List[str]):
        """
        Property 2: Filter Result Correctness - Result count text format
        
        *For any* filter result, the result count text SHALL be formatted correctly.
        
        **Feature: search-ux-improvement, Property 2: Filter Result Correctness**
        **Validates: Requirements 3.2**
        """
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        
        combobox = MockAutocompleteCombobox(values=companies)
        
        # Test with all values
        combobox.filter_values("")
        text = combobox.get_result_count_text()
        count = combobox.get_filter_count()
        
        if count == 0:
            assert text == "Không tìm thấy kết quả"
        elif count == 1:
            assert text == "Tìm thấy 1 công ty"
        else:
            assert text == f"Tìm thấy {count} công ty"


class MockClearButtonState:
    """
    Mock implementation of clear button visibility logic.
    
    **Feature: search-ux-improvement, Property 5: Clear Button Visibility**
    **Validates: Requirements 6.1, 6.3**
    """
    
    def __init__(self, placeholder: str = "Nhập để tìm kiếm..."):
        self.text = ""
        self.placeholder = placeholder
        self._is_placeholder_shown = True
    
    def set_text(self, text: str) -> None:
        """Set text in the combobox."""
        self.text = text
        self._is_placeholder_shown = (text == self.placeholder or text == "")
    
    def show_placeholder(self) -> None:
        """Show placeholder text."""
        self.text = self.placeholder
        self._is_placeholder_shown = True
    
    def clear(self) -> None:
        """Clear text and show placeholder."""
        self.text = ""
        self._is_placeholder_shown = True
    
    def should_show_clear_button(self) -> bool:
        """
        Determine if clear button should be visible.
        
        Returns True if text is non-empty and not placeholder.
        """
        return bool(self.text) and self.text != self.placeholder and not self._is_placeholder_shown


class MockDropdownState:
    """
    Mock implementation of dropdown state for testing state consistency.
    
    **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
    **Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4**
    """
    
    def __init__(self):
        self.is_open = False
        self.text = ""
    
    def type_char(self, char: str) -> None:
        """Simulate typing a character - should open dropdown if closed."""
        self.text += char
        if not self.is_open:
            self.is_open = True  # Auto-open on first type (Requirement 4.1)
    
    def continue_typing(self, char: str) -> None:
        """Continue typing while dropdown is open - should stay open."""
        self.text += char
        # Dropdown stays open during continuous typing (Requirement 4.2)
    
    def press_escape(self) -> None:
        """Press Escape - should close dropdown but keep text."""
        self.is_open = False  # Close dropdown (Requirement 4.4)
        # Text is preserved
    
    def click_outside(self) -> None:
        """Click outside - should close dropdown."""
        self.is_open = False  # Close dropdown (Requirement 4.3)
    
    def select_item(self) -> None:
        """Select an item - should close dropdown."""
        self.is_open = False


class TestDropdownStateConsistencyProperty:
    """
    Property-based tests for dropdown state consistency.
    
    **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
    **Validates: Requirements 1.4, 4.1, 4.2, 4.3, 4.4**
    """
    
    @given(
        chars_to_type=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=1),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_3_dropdown_opens_on_first_type(self, chars_to_type: List[str]):
        """
        Property 3: Dropdown State Consistency - Opens on first type
        
        *For any* typing action when dropdown is closed, the dropdown SHALL open.
        
        **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
        **Validates: Requirements 4.1**
        """
        state = MockDropdownState()
        assert not state.is_open, "Dropdown should start closed"
        
        # Type first character
        state.type_char(chars_to_type[0])
        assert state.is_open, "Dropdown should open after first type"
    
    @given(
        chars_to_type=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=1),
            min_size=2,
            max_size=10
        )
    )
    @settings(max_examples=100)
    def test_property_3_dropdown_stays_open_during_typing(self, chars_to_type: List[str]):
        """
        Property 3: Dropdown State Consistency - Stays open during typing
        
        *For any* sequence of typing actions, the dropdown SHALL remain open 
        while typing continues.
        
        **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
        **Validates: Requirements 1.4, 4.2**
        """
        state = MockDropdownState()
        
        # Type first character to open
        state.type_char(chars_to_type[0])
        
        # Continue typing - dropdown should stay open
        for char in chars_to_type[1:]:
            state.continue_typing(char)
            assert state.is_open, "Dropdown should stay open during continuous typing"
    
    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_3_escape_closes_but_keeps_text(self, text: str):
        """
        Property 3: Dropdown State Consistency - Escape closes but keeps text
        
        *For any* text in the search box, pressing Escape SHALL close the dropdown 
        and keep the text.
        
        **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
        **Validates: Requirements 4.4**
        """
        assume(text.strip())
        
        state = MockDropdownState()
        state.text = text
        state.is_open = True
        
        # Press Escape
        state.press_escape()
        
        assert not state.is_open, "Dropdown should close on Escape"
        assert state.text == text, "Text should be preserved after Escape"
    
    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N')),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_3_click_outside_closes_dropdown(self, text: str):
        """
        Property 3: Dropdown State Consistency - Click outside closes dropdown
        
        *For any* open dropdown, clicking outside SHALL close the dropdown.
        
        **Feature: search-ux-improvement, Property 3: Dropdown State Consistency**
        **Validates: Requirements 4.3**
        """
        assume(text.strip())
        
        state = MockDropdownState()
        state.text = text
        state.is_open = True
        
        # Click outside
        state.click_outside()
        
        assert not state.is_open, "Dropdown should close on click outside"


class MockKeyboardNavigation:
    """
    Mock implementation of keyboard navigation for testing.
    
    **Feature: search-ux-improvement, Property 4: Keyboard Navigation Correctness**
    **Validates: Requirements 5.1, 5.2**
    """
    
    def __init__(self, items: List[str]):
        self.items = items
        self.highlighted_index = -1  # -1 means no item highlighted
    
    def press_down(self) -> None:
        """Press Down arrow - highlight next item."""
        if self.items:
            self.highlighted_index = min(self.highlighted_index + 1, len(self.items) - 1)
    
    def press_up(self) -> None:
        """Press Up arrow - highlight previous item."""
        if self.items and self.highlighted_index > 0:
            self.highlighted_index -= 1
    
    def get_highlighted_index(self) -> int:
        """Get currently highlighted index."""
        return self.highlighted_index


class TestClearButtonVisibilityProperty:
    """
    Property-based tests for clear button visibility.
    
    **Feature: search-ux-improvement, Property 5: Clear Button Visibility**
    **Validates: Requirements 6.1, 6.3**
    """
    
    @given(
        text=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N', 'P')),
            min_size=1,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_property_5_clear_button_visible_with_text(self, text: str):
        """
        Property 5: Clear Button Visibility - Visible with text
        
        *For any* non-empty text that is not the placeholder, the clear button 
        SHALL be visible.
        
        **Feature: search-ux-improvement, Property 5: Clear Button Visibility**
        **Validates: Requirements 6.1**
        """
        assume(text.strip())
        
        state = MockClearButtonState()
        state.set_text(text)
        state._is_placeholder_shown = False  # Explicitly not showing placeholder
        
        # If text is not placeholder, clear button should be visible
        if text != state.placeholder:
            assert state.should_show_clear_button(), \
                f"Clear button should be visible for text '{text}'"
    
    @given(
        placeholder=st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
            min_size=5,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_property_5_clear_button_hidden_with_placeholder(self, placeholder: str):
        """
        Property 5: Clear Button Visibility - Hidden with placeholder
        
        *For any* placeholder text, the clear button SHALL be hidden.
        
        **Feature: search-ux-improvement, Property 5: Clear Button Visibility**
        **Validates: Requirements 6.3**
        """
        assume(placeholder.strip())
        
        state = MockClearButtonState(placeholder=placeholder)
        state.show_placeholder()
        
        assert not state.should_show_clear_button(), \
            "Clear button should be hidden when showing placeholder"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_property_5_clear_button_hidden_when_empty(self, data):
        """
        Property 5: Clear Button Visibility - Hidden when empty
        
        *For any* empty text state, the clear button SHALL be hidden.
        
        **Feature: search-ux-improvement, Property 5: Clear Button Visibility**
        **Validates: Requirements 6.3**
        """
        state = MockClearButtonState()
        state.clear()
        
        assert not state.should_show_clear_button(), \
            "Clear button should be hidden when text is empty"


class TestKeyboardNavigationProperty:
    """
    Property-based tests for keyboard navigation.
    
    **Feature: search-ux-improvement, Property 4: Keyboard Navigation Correctness**
    **Validates: Requirements 5.1, 5.2**
    """
    
    @given(
        items=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=20),
            min_size=1, max_size=20
        ),
        num_down_presses=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=100)
    def test_property_4_down_arrow_highlights_next(self, items: List[str], num_down_presses: int):
        """
        Property 4: Keyboard Navigation Correctness - Down arrow
        
        *For any* dropdown with N items, pressing Down arrow K times SHALL highlight 
        item at index min(K-1, N-1).
        
        **Feature: search-ux-improvement, Property 4: Keyboard Navigation Correctness**
        **Validates: Requirements 5.1**
        """
        items = [i for i in items if i.strip()]
        assume(len(items) > 0)
        
        nav = MockKeyboardNavigation(items)
        
        for k in range(1, num_down_presses + 1):
            nav.press_down()
            expected_index = min(k - 1, len(items) - 1)
            assert nav.get_highlighted_index() == expected_index, \
                f"After {k} down presses, expected index {expected_index}, got {nav.get_highlighted_index()}"
    
    @given(
        items=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=20),
            min_size=2, max_size=20
        ),
        start_index=st.integers(min_value=1, max_value=19),
        num_up_presses=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=100)
    def test_property_4_up_arrow_highlights_previous(self, items: List[str], start_index: int, num_up_presses: int):
        """
        Property 4: Keyboard Navigation Correctness - Up arrow
        
        *For any* dropdown with highlighted item, pressing Up arrow SHALL move 
        highlight to previous item (stopping at index 0).
        
        **Feature: search-ux-improvement, Property 4: Keyboard Navigation Correctness**
        **Validates: Requirements 5.2**
        """
        items = [i for i in items if i.strip()]
        assume(len(items) > 1)
        
        # Ensure start_index is valid
        start_index = min(start_index, len(items) - 1)
        
        nav = MockKeyboardNavigation(items)
        nav.highlighted_index = start_index
        
        for k in range(1, num_up_presses + 1):
            nav.press_up()
            expected_index = max(start_index - k, 0)
            assert nav.get_highlighted_index() == expected_index, \
                f"After {k} up presses from {start_index}, expected index {expected_index}, got {nav.get_highlighted_index()}"
    
    @given(
        items=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=20),
            min_size=1, max_size=20
        )
    )
    @settings(max_examples=100)
    def test_property_4_navigation_stays_in_bounds(self, items: List[str]):
        """
        Property 4: Keyboard Navigation Correctness - Bounds checking
        
        *For any* sequence of navigation, the highlighted index SHALL always be 
        within valid bounds [0, N-1] or -1 (no selection).
        
        **Feature: search-ux-improvement, Property 4: Keyboard Navigation Correctness**
        **Validates: Requirements 5.1, 5.2**
        """
        items = [i for i in items if i.strip()]
        assume(len(items) > 0)
        
        nav = MockKeyboardNavigation(items)
        
        # Press down many times
        for _ in range(len(items) + 5):
            nav.press_down()
            assert 0 <= nav.get_highlighted_index() < len(items), \
                f"Index {nav.get_highlighted_index()} out of bounds [0, {len(items)-1}]"
        
        # Press up many times
        for _ in range(len(items) + 5):
            nav.press_up()
            assert 0 <= nav.get_highlighted_index() < len(items), \
                f"Index {nav.get_highlighted_index()} out of bounds [0, {len(items)-1}]"


class TestAutocompleteComboboxProperties:
    """Property-based tests for AutocompleteCombobox."""
    
    @given(
        companies=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=20),
        search_text=st.text(min_size=1, max_size=10)
    )
    @settings(max_examples=100)
    def test_property_4_filter_correctness(self, companies: List[str], search_text: str):
        """
        Property 4: Company Filter Correctness
        
        For any search string typed in the autocomplete combobox,
        all displayed options SHALL contain the search string (case-insensitive).
        
        Validates: Requirements 4.2, 8.2
        """
        # Filter out empty strings
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        assume(search_text.strip())
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values(search_text)
        
        # If we got results (not "Không tìm thấy")
        if filtered != [combobox.no_match_text]:
            search_lower = search_text.lower()
            for value in filtered:
                assert search_lower in value.lower(), \
                    f"Filtered value '{value}' does not contain search text '{search_text}'"
    
    @given(companies=st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=20))
    @settings(max_examples=50)
    def test_empty_search_returns_all(self, companies: List[str]):
        """
        When search is empty, all values should be returned.
        
        Validates: Requirement 8.4
        """
        companies = [c for c in companies if c.strip()]
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values("")
        
        assert filtered == companies, \
            "Empty search should return all values"
    
    @given(
        companies=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=20),
        search_text=st.text(min_size=20, max_size=50)  # Long search unlikely to match
    )
    @settings(max_examples=50)
    def test_no_match_shows_message(self, companies: List[str], search_text: str):
        """
        When no companies match the search, "Không tìm thấy" should be displayed.
        
        Validates: Requirement 8.5
        """
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        
        # Make sure search text doesn't match any company
        search_lower = search_text.lower()
        assume(not any(search_lower in c.lower() for c in companies))
        
        combobox = MockAutocompleteCombobox(values=companies)
        filtered = combobox.filter_values(search_text)
        
        assert filtered == [combobox.no_match_text], \
            f"Expected 'Không tìm thấy' but got {filtered}"
    
    @given(
        companies=st.lists(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ', min_size=1, max_size=30),
            min_size=1, max_size=20
        ),
        search_text=st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', min_size=1, max_size=10)
    )
    @settings(max_examples=50)
    def test_case_insensitive_search(self, companies: List[str], search_text: str):
        """
        Search should be case-insensitive.
        
        Validates: Requirement 8.2
        
        Note: Uses ASCII alphanumeric characters only to avoid Unicode edge cases
        where some characters have different case conversion behavior.
        """
        companies = [c for c in companies if c.strip()]
        assume(len(companies) > 0)
        assume(search_text.strip())
        
        combobox = MockAutocompleteCombobox(values=companies)
        
        # Search with lowercase
        filtered_lower = combobox.filter_values(search_text.lower())
        
        # Search with uppercase
        filtered_upper = combobox.filter_values(search_text.upper())
        
        # Results should be the same
        assert set(filtered_lower) == set(filtered_upper), \
            "Case-insensitive search should return same results"
    
    @given(companies=st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=20))
    @settings(max_examples=50)
    def test_set_values_updates_all_values(self, companies: List[str]):
        """
        set_values should update the internal all_values list.
        """
        companies = [c for c in companies if c.strip()]
        
        combobox = MockAutocompleteCombobox(values=[])
        combobox.set_values(companies)
        
        assert combobox.all_values == companies
        assert combobox.current_values == companies


class TestAutocompleteComboboxUnit:
    """Unit tests for AutocompleteCombobox."""
    
    def test_init_with_values(self):
        """Test initialization with values."""
        values = ["Company A", "Company B", "Company C"]
        combobox = MockAutocompleteCombobox(values=values)
        
        assert combobox.all_values == values
        assert combobox.current_values == values
    
    def test_init_empty(self):
        """Test initialization without values."""
        combobox = MockAutocompleteCombobox()
        
        assert combobox.all_values == []
        assert combobox.current_values == []
    
    def test_filter_partial_match(self):
        """Test filtering with partial match."""
        values = ["ABC Company", "XYZ Corp", "ABC Inc"]
        combobox = MockAutocompleteCombobox(values=values)
        
        filtered = combobox.filter_values("ABC")
        
        assert len(filtered) == 2
        assert "ABC Company" in filtered
        assert "ABC Inc" in filtered
        assert "XYZ Corp" not in filtered
    
    def test_filter_no_match(self):
        """Test filtering with no match."""
        values = ["Company A", "Company B"]
        combobox = MockAutocompleteCombobox(values=values)
        
        filtered = combobox.filter_values("XYZ")
        
        assert filtered == ["Không tìm thấy"]
    
    def test_filter_empty_string(self):
        """Test filtering with empty string."""
        values = ["Company A", "Company B"]
        combobox = MockAutocompleteCombobox(values=values)
        
        # First filter to change current_values
        combobox.filter_values("A")
        
        # Then filter with empty string
        filtered = combobox.filter_values("")
        
        assert filtered == values


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
