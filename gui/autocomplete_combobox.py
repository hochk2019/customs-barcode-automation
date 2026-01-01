"""
AutocompleteCombobox Component

A combobox with autocomplete/filter functionality that combines search and dropdown
into a single control.

Requirements: 4.1, 4.2, 8.1, 8.2, 8.3, 8.4, 8.5
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable


class AutocompleteCombobox(ttk.Combobox):
    """
    Combobox with autocomplete/filter functionality.
    
    Combines search and dropdown into single control.
    Supports:
    - Real-time filtering as user types (with debounce)
    - Case-insensitive search
    - "Không tìm thấy" message when no matches
    - Both typing to filter and clicking dropdown to see all options
    - Auto-select text on focus for easy replacement
    
    Requirements: 4.1, 4.2, 8.1, 8.2, 8.3, 8.4, 8.5
    """
    
    MAX_RESULTS = 50
    # Debounce delay in milliseconds - tuned for user typing speed (Requirement 2.1)
    DEBOUNCE_DELAY = 600
    
    def __init__(
        self,
        parent: tk.Widget,
        values: List[str] = None,
        on_select: Optional[Callable[[str], None]] = None,
        on_filter: Optional[Callable[[int, bool], None]] = None,
        placeholder: str = "Nhập để tìm kiếm...",
        no_match_text: str = "Không tìm thấy",
        **kwargs
    ):
        """
        Initialize AutocompleteCombobox.
        
        Args:
            parent: Parent widget
            values: List of values for dropdown
            on_select: Callback when item is selected
            on_filter: Callback when filter completes (count, has_matches)
                       For displaying result count (Requirements 3.1, 3.2)
            placeholder: Placeholder text when empty
            no_match_text: Text to show when no matches found
            **kwargs: Additional arguments for ttk.Combobox
        """
        super().__init__(parent, **kwargs)
        
        self.all_values: List[str] = values or []
        self.on_select = on_select
        self.on_filter = on_filter  # Callback for result count (Requirement 3.1, 3.2)
        self.placeholder = placeholder
        self.no_match_text = no_match_text
        self._is_filtering = False
        self._last_search = ""
        self._debounce_id = None  # For debounce timer
        self._is_placeholder_shown = False
        self._dropdown_open = False
        self._saved_cursor_pos = 0  # For cursor preservation (Requirement 1.2, 1.3)
        self._last_filter_count = 0  # Track last filter result count
        
        # Set initial values
        self['values'] = self.all_values
        
        # Bind events
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        self.bind('<<ComboboxSelected>>', self._on_combobox_selected)
        self.bind('<Button-1>', self._on_click)
        self.bind('<Return>', self._on_return)
        self.bind('<Escape>', self._on_escape)
        self.bind('<Up>', self._on_arrow_key)
        self.bind('<Down>', self._on_arrow_key)
        self.bind('<Tab>', self._on_tab)
        
        # Show placeholder if empty
        if not self.get():
            self._show_placeholder()
    
    def _on_key_release(self, event) -> None:
        """
        Handle key release event for filtering with debounce.
        
        Uses debounce to wait for user to stop typing before filtering.
        This prevents the dropdown from interrupting typing.
        Requirements: 4.2, 8.2
        """
        # Ignore special keys
        if event.keysym in ('Return', 'Tab', 'Escape', 'Up', 'Down', 'Left', 'Right',
                           'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R',
                           'Caps_Lock', 'Num_Lock'):
            return
        
        # Cancel previous debounce timer
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
            self._debounce_id = None
        
        # Schedule new filter after debounce delay
        self._debounce_id = self.after(self.DEBOUNCE_DELAY, self._do_filter)
    
    def _do_filter(self) -> None:
        """
        Perform the actual filtering after debounce delay.
        """
        self._debounce_id = None
        
        typed = self.get().strip()
        
        # Skip if placeholder is shown
        if self._is_placeholder_shown:
            return
        
        # Skip if same as last search
        if typed == self._last_search:
            return
        
        self._last_search = typed
        self._filter_values(typed)
    
    def _filter_values(self, search_text: str) -> None:
        """
        Filter values based on search text.
        
        Args:
            search_text: Text to search for
            
        Requirements: 1.4, 4.2, 8.2, 8.5
        - Updates dropdown values without closing/reopening
        - Tracks dropdown state with _dropdown_open flag
        - Saves and restores cursor position (Requirements 1.2, 1.3)
        """
        self._is_filtering = True
        
        # Save cursor position before any operations (Requirement 2.1)
        try:
            self._saved_cursor_pos = self.index(tk.INSERT)
        except tk.TclError:
            self._saved_cursor_pos = len(self.get())
        
        has_matches = True
        filter_count = 0
        
        if not search_text:
            # Show all values when search is empty
            self['values'] = self.all_values
            filter_count = len(self.all_values)
        else:
            # Case-insensitive search
            search_lower = search_text.lower()
            filtered = [v for v in self.all_values if search_lower in v.lower()]
            
            if filtered:
                self['values'] = filtered
                filter_count = len(filtered)
            else:
                # Show "Không tìm thấy" when no matches (Requirement 8.5)
                self['values'] = [self.no_match_text]
                filter_count = 0
                has_matches = False
        
        # Store last filter count
        self._last_filter_count = filter_count
        
        # Notify callback about filter results (Requirements 3.1, 3.2)
        if self.on_filter:
            try:
                self.on_filter(filter_count, has_matches)
            except Exception:
                pass  # Ignore callback errors
        
        # Open dropdown only once, then just update values (Requirements 1.4, 4.2)
        if self['values'] and not self._dropdown_open:
            # Open dropdown for the first time
            self._open_dropdown()
        
        # Restore cursor position after update (Requirement 2.2)
        self.after(1, lambda: self._restore_cursor(self._saved_cursor_pos))
        
        self._is_filtering = False
    
    def _open_dropdown(self) -> None:
        """
        Open the dropdown list.
        
        Requirements: 4.1 - Open dropdown automatically when typing starts
        """
        if not self._dropdown_open:
            try:
                self.event_generate('<Down>')
                self._dropdown_open = True
            except tk.TclError:
                pass  # Widget may have been destroyed
    
    def _close_dropdown(self) -> None:
        """
        Close the dropdown list.
        
        Requirements: 4.3, 4.4 - Close dropdown on click outside or Escape
        """
        if self._dropdown_open:
            try:
                self.event_generate('<Escape>')
                self._dropdown_open = False
            except tk.TclError:
                pass  # Widget may have been destroyed
    
    def _restore_cursor(self, position: int) -> None:
        """Restore cursor position after dropdown opens."""
        try:
            self.focus_set()
            self.icursor(position)
            # Clear any selection to prevent text from being replaced
            self.selection_clear()
        except tk.TclError:
            pass  # Widget may have been destroyed
    
    def _place_cursor_at_end(self) -> None:
        """Place cursor at end of text without selecting."""
        try:
            self.icursor(tk.END)
            self.selection_clear()
        except tk.TclError:
            pass  # Widget may have been destroyed
    
    def _on_focus_in(self, event) -> None:
        """
        Handle focus in - place cursor at end without selecting text.
        
        When user clicks into the combobox, cursor is placed at the end
        so they can continue typing without losing existing text.
        This provides a Google-like search experience.
        
        Requirements: 1.1, 1.2 - No text selection on focus, preserve cursor position
        """
        current = self.get()
        
        if self._is_placeholder_shown or current == self.placeholder:
            # Clear placeholder
            self.set('')
            # Use default foreground from style instead of hardcoded color
            self.configure(foreground='')  # Reset to style default
            self._is_placeholder_shown = False
        
        # Always place cursor at end without selecting text
        # Use after() to ensure this happens after any default Tk behavior
        self.after(1, self._place_cursor_at_end)
    
    def _on_focus_out(self, event) -> None:
        """Handle focus out - show placeholder if empty."""
        # Cancel any pending debounce
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
            self._debounce_id = None
        
        self._dropdown_open = False
        
        if not self.get().strip():
            self._show_placeholder()
    
    def _on_click(self, event) -> None:
        """Handle click - show all values in dropdown (Requirement 8.4)."""
        current = self.get()
        
        # Clear placeholder on click
        if self._is_placeholder_shown or current == self.placeholder:
            self.set('')
            # Use default foreground from style instead of hardcoded color
            self.configure(foreground='')  # Reset to style default
            self._is_placeholder_shown = False
            self['values'] = self.all_values
        elif not self._is_filtering:
            # If clicking dropdown arrow area, show all values
            # Check if click is on the dropdown button (right side)
            widget_width = self.winfo_width()
            if event.x > widget_width - 20:  # Dropdown button area
                self['values'] = self.all_values
                self._last_search = ""
    
    def _on_return(self, event) -> None:
        """Handle Return key - select first matching item."""
        values = self['values']
        if values and values[0] != self.no_match_text:
            self.set(values[0])
            self._on_combobox_selected(event)
    
    def _on_escape(self, event) -> None:
        """
        Handle Escape key - close dropdown but keep text.
        
        Requirements: 4.4 - Close dropdown on Escape
        """
        self._dropdown_open = False
        # Keep the current text, just close dropdown
        return  # Let default behavior close the dropdown
    
    def _on_arrow_key(self, event) -> None:
        """
        Handle Up/Down arrow keys during keyboard navigation.
        
        Requirements: 2.3, 5.1, 5.2 - Keep cursor at end during navigation
        """
        # After arrow key navigation, restore cursor to end
        self.after(1, self._place_cursor_at_end)
    
    def _on_tab(self, event) -> None:
        """
        Handle Tab key - select first matching item and move focus.
        
        Requirements: 5.4 - Tab selects first match and moves focus
        """
        values = self['values']
        if values and values[0] != self.no_match_text:
            # Select first matching item
            self.set(values[0])
            self._dropdown_open = False
            self._last_search = ""
            self['values'] = self.all_values
            
            # Call callback if provided
            if self.on_select:
                try:
                    self.on_select(values[0])
                except Exception:
                    pass
        
        # Let default Tab behavior move focus to next widget
        return None
    
    def _on_combobox_selected(self, event) -> None:
        """
        Handle combobox selection.
        
        Populates combobox with selected company and calls callback.
        Requirements: 8.3
        """
        selected = self.get()
        
        # Ignore "Không tìm thấy" selection
        if selected == self.no_match_text:
            self.set('')
            self._last_search = ""
            return
        
        # Ignore placeholder
        if selected == self.placeholder:
            return
        
        # Reset values to all after selection
        self['values'] = self.all_values
        self._last_search = ""
        self._dropdown_open = False
        # Use default foreground from style instead of hardcoded color
        self.configure(foreground='')  # Reset to style default
        self._is_placeholder_shown = False
        
        # Call callback if provided
        if self.on_select and selected:
            self.on_select(selected)
    
    def _show_placeholder(self) -> None:
        """Show placeholder text."""
        self.set(self.placeholder)
        # Use a muted color for placeholder - this works for both themes
        # as ttk styles handle the actual color based on theme
        self.configure(foreground='#888888')  # Neutral gray that works in both themes
        self._is_placeholder_shown = True
        self._last_search = ""
    
    def set_values(self, values: List[str]) -> None:
        """
        Set new values for the combobox.
        
        Args:
            values: List of values
        """
        self.all_values = values or []
        self['values'] = self.all_values
        self._last_search = ""
    
    def get_all_values(self) -> List[str]:
        """
        Get all values (unfiltered).
        
        Returns:
            List of all values
        """
        return self.all_values.copy()
    
    def clear(self) -> None:
        """Clear the combobox and show placeholder."""
        self.set('')
        self._show_placeholder()
        self['values'] = self.all_values
        self._last_search = ""
        self._dropdown_open = False
    
    def get_selected(self) -> Optional[str]:
        """
        Get currently selected value.
        
        Returns:
            Selected value or None if placeholder/no match
        """
        value = self.get()
        if value in (self.placeholder, self.no_match_text, ''):
            return None
        return value
    
    def get_filter_count(self) -> int:
        """
        Get the count of last filter results.
        
        Returns:
            Number of matching items from last filter operation
            
        Requirements: 3.1, 3.2
        """
        return self._last_filter_count
    
    def get_result_count_text(self) -> str:
        """
        Get formatted result count text for display.
        
        Returns:
            Formatted string like "Tìm thấy X công ty" or "Không tìm thấy kết quả"
            
        Requirements: 3.2, 3.3
        """
        count = self._last_filter_count
        if count == 0:
            return "Không tìm thấy kết quả"
        elif count == 1:
            return "Tìm thấy 1 công ty"
        else:
            return f"Tìm thấy {count} công ty"
    
    def should_show_clear_button(self) -> bool:
        """
        Determine if clear button should be visible.
        
        Returns:
            True if text is non-empty and not placeholder
            
        Requirements: 6.1, 6.3
        """
        text = self.get()
        return bool(text) and text != self.placeholder and not self._is_placeholder_shown
    
    def clear_and_reset(self) -> None:
        """
        Clear text, show placeholder, and reset filter.
        
        This method is called when clear button is clicked.
        
        Requirements: 6.2
        """
        self.set('')
        self._show_placeholder()
        self['values'] = self.all_values
        self._last_search = ""
        self._dropdown_open = False
        self._last_filter_count = len(self.all_values)
        
        # Notify callback about reset
        if self.on_filter:
            try:
                self.on_filter(len(self.all_values), True)
            except Exception:
                pass
