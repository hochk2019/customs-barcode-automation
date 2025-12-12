"""
Preview Table Controller

This module provides the controller for the preview table with filtering,
sorting, and double-click to open PDF functionality.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
"""

import os
import subprocess
import platform
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum


class FilterStatus(Enum):
    """Filter status options for preview table"""
    ALL = "all"
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class PreviewItem:
    """Data class representing a preview table item"""
    stt: int
    checkbox: str
    declaration_number: str
    tax_code: str
    date: str
    status: str
    declaration_type: str
    bill_of_lading: str
    invoice_number: str
    result: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    
    @property
    def result_status(self) -> FilterStatus:
        """Get the result status for filtering"""
        if self.result == "✔":
            return FilterStatus.SUCCESS
        elif self.result == "✘":
            return FilterStatus.FAILED
        else:
            return FilterStatus.PENDING


class PreviewTableController:
    """
    Controller for preview table with filter, sort, and double-click functionality.
    
    Provides:
    - Filter by status (all, success, failed, pending)
    - Sort by column with toggle (ascending/descending)
    - Double-click to open PDF file
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
    """
    
    # Column indices
    COL_STT = 0
    COL_CHECKBOX = 1
    COL_DECLARATION_NUMBER = 2
    COL_TAX_CODE = 3
    COL_DATE = 4
    COL_STATUS = 5
    COL_DECLARATION_TYPE = 6
    COL_BILL_OF_LADING = 7
    COL_INVOICE_NUMBER = 8
    COL_RESULT = 9
    
    # Column names for sorting
    COLUMN_NAMES = [
        "stt", "checkbox", "declaration_number", "tax_code", 
        "date", "status", "declaration_type", "bill_of_lading",
        "invoice_number", "result"
    ]
    
    def __init__(
        self,
        treeview: ttk.Treeview,
        on_filter_change: Optional[Callable[[FilterStatus], None]] = None,
        on_sort_change: Optional[Callable[[str, bool], None]] = None
    ):
        """
        Initialize PreviewTableController.
        
        Args:
            treeview: The ttk.Treeview widget to control
            on_filter_change: Optional callback when filter changes
            on_sort_change: Optional callback when sort changes
        """
        self.treeview = treeview
        self.on_filter_change = on_filter_change
        self.on_sort_change = on_sort_change
        
        # State
        self._current_filter = FilterStatus.ALL
        self._sort_column: Optional[str] = None
        self._sort_descending = False
        
        # Store all items for filtering
        self._all_items: List[Dict[str, Any]] = []
        
        # Store file paths for double-click
        self._file_paths: Dict[str, str] = {}
        
        # Store error messages for tooltips
        self._error_messages: Dict[str, str] = {}
    
    def set_filter(self, status: str) -> None:
        """
        Set the filter status and update the table.
        
        Args:
            status: Filter status ('all', 'success', 'failed', 'pending')
            
        Requirements: 3.1, 3.2
        """
        try:
            self._current_filter = FilterStatus(status)
        except ValueError:
            self._current_filter = FilterStatus.ALL
        
        self._apply_filter()
        
        if self.on_filter_change:
            self.on_filter_change(self._current_filter)
    
    def get_filter(self) -> str:
        """Get the current filter status"""
        return self._current_filter.value
    
    def _apply_filter(self) -> None:
        """Apply the current filter to the table"""
        # Clear current items
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Filter items
        filtered_items = self._filter_items(self._all_items, self._current_filter)
        
        # Re-apply sort if active
        if self._sort_column:
            filtered_items = self._sort_items(filtered_items, self._sort_column, self._sort_descending)
        
        # Re-populate table
        self._populate_table(filtered_items)
    
    def _filter_items(
        self, 
        items: List[Dict[str, Any]], 
        filter_status: FilterStatus
    ) -> List[Dict[str, Any]]:
        """
        Filter items by status.
        
        Args:
            items: List of item dictionaries
            filter_status: Filter status to apply
            
        Returns:
            Filtered list of items
            
        Requirements: 3.2
        """
        if filter_status == FilterStatus.ALL:
            return items
        
        filtered = []
        for item in items:
            result = item.get('result', '')
            
            if filter_status == FilterStatus.SUCCESS and result == "✔":
                filtered.append(item)
            elif filter_status == FilterStatus.FAILED and result == "✘":
                filtered.append(item)
            elif filter_status == FilterStatus.PENDING and result not in ("✔", "✘"):
                filtered.append(item)
        
        return filtered
    
    def sort_by_column(self, column: str, reverse: bool = False) -> None:
        """
        Sort the table by the specified column.
        
        Args:
            column: Column name to sort by
            reverse: True for descending, False for ascending
            
        Requirements: 3.3
        """
        if column not in self.COLUMN_NAMES:
            return
        
        self._sort_column = column
        self._sort_descending = reverse
        
        # Re-apply filter and sort
        self._apply_filter()
        
        if self.on_sort_change:
            self.on_sort_change(column, reverse)
    
    def toggle_sort(self, column: str) -> None:
        """
        Toggle sort direction for a column.
        
        If already sorting by this column, toggle direction.
        If sorting by different column, sort ascending.
        
        Args:
            column: Column name to sort by
            
        Requirements: 3.3, 3.4
        """
        if self._sort_column == column:
            # Toggle direction
            self._sort_descending = not self._sort_descending
        else:
            # New column, start ascending
            self._sort_column = column
            self._sort_descending = False
        
        self._apply_filter()
        
        if self.on_sort_change:
            self.on_sort_change(column, self._sort_descending)
    
    def _sort_items(
        self, 
        items: List[Dict[str, Any]], 
        column: str, 
        reverse: bool
    ) -> List[Dict[str, Any]]:
        """
        Sort items by column.
        
        Args:
            items: List of item dictionaries
            column: Column name to sort by
            reverse: True for descending
            
        Returns:
            Sorted list of items
            
        Requirements: 3.3, 3.4
        """
        if not column or column not in self.COLUMN_NAMES:
            return items
        
        def sort_key(item: Dict[str, Any]):
            value = item.get(column, '')
            
            # Handle numeric columns
            if column == 'stt':
                try:
                    return int(value) if value else 0
                except (ValueError, TypeError):
                    return 0
            
            # Handle date column (DD/MM/YYYY format)
            if column == 'date':
                try:
                    parts = str(value).split('/')
                    if len(parts) == 3:
                        # Convert to YYYYMMDD for proper sorting
                        return f"{parts[2]}{parts[1]}{parts[0]}"
                except:
                    pass
                return str(value)
            
            # Default string comparison
            return str(value).lower() if value else ''
        
        return sorted(items, key=sort_key, reverse=reverse)
    
    def on_double_click(self, event) -> None:
        """
        Handle double-click event to open PDF file.
        
        Args:
            event: Tkinter event
            
        Requirements: 3.5, 3.6
        """
        # Get clicked item
        item = self.treeview.identify_row(event.y)
        if not item:
            return
        
        # Get declaration number
        values = self.treeview.item(item, "values")
        if len(values) <= self.COL_DECLARATION_NUMBER:
            return
        
        declaration_number = values[self.COL_DECLARATION_NUMBER]
        result = values[self.COL_RESULT] if len(values) > self.COL_RESULT else ""
        
        # Check if file exists
        file_path = self._file_paths.get(declaration_number)
        
        if result == "✔" and file_path and os.path.exists(file_path):
            # Open PDF file (Requirement 3.5)
            self._open_file(file_path)
        else:
            # Show message for files not downloaded (Requirement 3.6)
            messagebox.showinfo(
                "Thông báo",
                "File chưa được tải"
            )
    
    def _open_file(self, file_path: str) -> None:
        """
        Open file with default application.
        
        Args:
            file_path: Path to file to open
        """
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            messagebox.showerror(
                "Lỗi",
                f"Không thể mở file:\n{str(e)}"
            )
    
    def get_visible_items(self) -> List[str]:
        """
        Get list of declaration numbers for visible items.
        
        Returns:
            List of declaration numbers
        """
        visible = []
        for item in self.treeview.get_children():
            values = self.treeview.item(item, "values")
            if len(values) > self.COL_DECLARATION_NUMBER:
                visible.append(values[self.COL_DECLARATION_NUMBER])
        return visible
    
    def get_sort_state(self) -> Tuple[Optional[str], bool]:
        """
        Get current sort state.
        
        Returns:
            Tuple of (column_name, is_descending)
        """
        return (self._sort_column, self._sort_descending)
    
    def store_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Store items for filtering.
        
        Args:
            items: List of item dictionaries with keys matching column names
        """
        self._all_items = items.copy()
    
    def set_file_path(self, declaration_number: str, file_path: str) -> None:
        """
        Set file path for a declaration.
        
        Args:
            declaration_number: Declaration number
            file_path: Path to PDF file
        """
        self._file_paths[declaration_number] = file_path
    
    def get_file_path(self, declaration_number: str) -> Optional[str]:
        """
        Get file path for a declaration.
        
        Args:
            declaration_number: Declaration number
            
        Returns:
            File path or None
        """
        return self._file_paths.get(declaration_number)
    
    def set_error_message(self, declaration_number: str, error_message: str) -> None:
        """
        Set error message for a declaration (for tooltip display).
        
        Args:
            declaration_number: Declaration number
            error_message: Error message
            
        Requirements: 4.1
        """
        self._error_messages[declaration_number] = error_message
    
    def get_error_message(self, declaration_number: str) -> Optional[str]:
        """
        Get error message for a declaration.
        
        Args:
            declaration_number: Declaration number
            
        Returns:
            Error message or None
        """
        return self._error_messages.get(declaration_number)
    
    def clear(self) -> None:
        """Clear all stored data and reset state"""
        self._all_items.clear()
        self._file_paths.clear()
        self._error_messages.clear()
        self._current_filter = FilterStatus.ALL
        self._sort_column = None
        self._sort_descending = False
        
        # Clear treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
    
    def _populate_table(self, items: List[Dict[str, Any]]) -> None:
        """
        Populate the treeview with items.
        
        Args:
            items: List of item dictionaries
        """
        for index, item in enumerate(items):
            # Determine row tag for alternating colors
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            # Get result for additional tag
            result = item.get('result', '')
            tags = [row_tag]
            if result == "✔":
                tags.append('success_result')
            elif result == "✘":
                tags.append('error_result')
            
            self.treeview.insert(
                "",
                "end",
                values=(
                    index + 1,  # Re-number STT
                    item.get('checkbox', '☐'),
                    item.get('declaration_number', ''),
                    item.get('tax_code', ''),
                    item.get('date', ''),
                    item.get('status', ''),
                    item.get('declaration_type', ''),
                    item.get('bill_of_lading', ''),
                    item.get('invoice_number', ''),
                    item.get('result', '')
                ),
                tags=tuple(tags)
            )
    
    def get_failed_declarations(self) -> List[str]:
        """
        Get list of declaration numbers that failed download.
        
        Returns:
            List of failed declaration numbers
            
        Requirements: 4.2
        """
        failed = []
        for item in self._all_items:
            if item.get('result') == "✘":
                failed.append(item.get('declaration_number', ''))
        return [d for d in failed if d]  # Filter out empty strings
    
    def update_result(self, declaration_number: str, success: bool) -> None:
        """
        Update the result for a declaration.
        
        Args:
            declaration_number: Declaration number to update
            success: True for success, False for failure
            
        Requirements: 4.3
        """
        result = "✔" if success else "✘"
        
        # Update stored items
        for item in self._all_items:
            if item.get('declaration_number') == declaration_number:
                item['result'] = result
                break
        
        # Update treeview
        for tree_item in self.treeview.get_children():
            values = list(self.treeview.item(tree_item, "values"))
            if len(values) > self.COL_DECLARATION_NUMBER and values[self.COL_DECLARATION_NUMBER] == declaration_number:
                values[self.COL_RESULT] = result
                self.treeview.item(tree_item, values=values)
                
                # Update tags
                current_tags = list(self.treeview.item(tree_item, "tags"))
                current_tags = [t for t in current_tags if t not in ('success_result', 'error_result')]
                current_tags.append('success_result' if success else 'error_result')
                self.treeview.item(tree_item, tags=tuple(current_tags))
                break
