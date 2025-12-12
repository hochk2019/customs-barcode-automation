"""
Preview Manager

This module provides business logic for previewing and selecting declarations
for the Enhanced Manual Mode feature.
"""

from typing import List, Optional, Callable, Set
from datetime import datetime
from threading import Event

from database.ecus_connector import EcusDataConnector, DatabaseConnectionError
from models.declaration_models import Declaration
from logging_system.logger import Logger


class PreviewError(Exception):
    """Exception raised for preview operation errors"""
    pass


class PreviewManager:
    """Business logic for declaration preview and selection"""
    
    def __init__(
        self,
        ecus_connector: EcusDataConnector,
        logger: Optional[Logger] = None
    ):
        """
        Initialize PreviewManager
        
        Args:
            ecus_connector: ECUS5 database connector
            logger: Optional logger instance
        """
        self.ecus_connector = ecus_connector
        self.logger = logger
        self._cancel_event = Event()
        self._selected_declarations: Set[str] = set()
        self._all_declarations: List[Declaration] = []
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Helper method to log messages if logger is available"""
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message, **kwargs)
    
    def _validate_unique_declarations(self, declarations: List[Declaration]) -> bool:
        """
        Validate that declarations list contains unique declarations only
        
        Args:
            declarations: List of declarations to validate
            
        Returns:
            True if all declarations are unique, False if duplicates found
        """
        seen = set()
        duplicates = []
        
        for decl in declarations:
            # Create unique key from declaration number, tax code, date, and customs office
            key = (decl.declaration_number, decl.tax_code, 
                   decl.declaration_date.date() if decl.declaration_date else None, 
                   decl.customs_office_code)
            
            if key in seen:
                duplicates.append(decl.declaration_number)
                self._log('warning', 
                         f"Duplicate declaration found: {decl.declaration_number} "
                         f"(tax_code: {decl.tax_code}, date: {decl.declaration_date})")
            else:
                seen.add(key)
        
        if duplicates:
            self._log('warning', 
                     f"Found {len(duplicates)} duplicate declarations: {duplicates}")
            return False
        
        return True
    
    def get_declarations_preview(
        self,
        from_date: datetime,
        to_date: datetime,
        tax_codes: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        include_pending: bool = False
    ) -> List[Declaration]:
        """
        Get declarations for preview based on date range and optional tax codes
        
        Args:
            from_date: Start date for query
            to_date: End date for query
            tax_codes: Optional list of tax codes to filter by
            progress_callback: Optional callback function(current, total, message)
                             for progress updates
            include_pending: If True, include declarations that are routed but not yet cleared
        
        Returns:
            List of Declaration objects
            
        Raises:
            PreviewError: If preview operation fails
            ValueError: If date range is invalid
        """
        try:
            # Check for cancellation before starting
            if self._cancel_event.is_set():
                self._log('info', "Preview cancelled by user")
                if progress_callback:
                    progress_callback(0, 100, "Đã hủy xem trước")
                return []
            
            # Validate date range
            if to_date < from_date:
                raise ValueError("End date cannot be before start date")
            
            if from_date > datetime.now():
                raise ValueError("Start date cannot be in the future")
            
            self._log('info', f"Getting preview from {from_date} to {to_date}" +
                     (f" for {len(tax_codes)} tax codes" if tax_codes else "") +
                     (f" (including pending)" if include_pending else ""))
            
            if progress_callback:
                progress_callback(0, 100, "Đang truy vấn database...")
            
            # Check for cancellation again
            if self._cancel_event.is_set():
                self._log('info', "Preview cancelled by user")
                if progress_callback:
                    progress_callback(0, 100, "Đã hủy xem trước")
                return []
            
            # Query declarations from database
            declarations = self.ecus_connector.get_declarations_by_date_range(
                from_date,
                to_date,
                tax_codes,
                include_pending=include_pending
            )
            
            # Check for cancellation after query
            if self._cancel_event.is_set():
                self._log('info', "Preview cancelled by user")
                if progress_callback:
                    progress_callback(0, 100, "Đã hủy xem trước")
                return []
            
            # Validate uniqueness of declarations
            is_unique = self._validate_unique_declarations(declarations)
            if not is_unique:
                self._log('warning', "Duplicate declarations detected in preview results")
            
            # Store declarations for selection tracking
            self._all_declarations = declarations
            
            # By default, no declarations are selected (Requirement 4.1)
            self._selected_declarations = set()
            
            self._log('info', f"Found {len(declarations)} declarations")
            
            if progress_callback:
                progress_callback(100, 100, f"Tìm thấy {len(declarations)} tờ khai")
            
            return declarations
            
        except ValueError:
            # Re-raise validation errors as-is
            raise
            
        except DatabaseConnectionError as e:
            error_msg = f"Database connection failed: {e}"
            self._log('error', error_msg, exc_info=True)
            raise PreviewError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Failed to get preview: {e}"
            self._log('error', error_msg, exc_info=True)
            raise PreviewError(error_msg) from e
    
    def get_selected_declarations(self) -> List[Declaration]:
        """
        Get list of declarations that are currently selected
        
        Returns:
            List of selected Declaration objects
        """
        selected = [
            decl for decl in self._all_declarations
            if decl.id in self._selected_declarations
        ]
        
        self._log('debug', f"Retrieved {len(selected)} selected declarations")
        
        return selected
    
    def set_selection(self, declaration_ids: Set[str]) -> None:
        """
        Set which declarations are selected
        
        Args:
            declaration_ids: Set of declaration IDs to select
        """
        # Only keep IDs that exist in current declarations
        valid_ids = {decl.id for decl in self._all_declarations}
        self._selected_declarations = declaration_ids & valid_ids
        
        self._log('debug', f"Selection updated: {len(self._selected_declarations)} selected")
    
    def select_all(self) -> None:
        """Select all declarations in current preview"""
        self._selected_declarations = {decl.id for decl in self._all_declarations}
        self._log('debug', "All declarations selected")
    
    def deselect_all(self) -> None:
        """Deselect all declarations"""
        self._selected_declarations.clear()
        self._log('debug', "All declarations deselected")
    
    def toggle_selection(self, declaration_id: str) -> bool:
        """
        Toggle selection state of a single declaration
        
        Args:
            declaration_id: ID of declaration to toggle
            
        Returns:
            True if now selected, False if now deselected
        """
        if declaration_id in self._selected_declarations:
            self._selected_declarations.remove(declaration_id)
            self._log('debug', f"Deselected declaration: {declaration_id}")
            return False
        else:
            self._selected_declarations.add(declaration_id)
            self._log('debug', f"Selected declaration: {declaration_id}")
            return True
    
    def get_selection_count(self) -> tuple:
        """
        Get selection count information
        
        Returns:
            Tuple of (selected_count, total_count)
        """
        return len(self._selected_declarations), len(self._all_declarations)
    
    def cancel_preview(self) -> None:
        """
        Cancel ongoing preview operation
        
        This sets a flag that will be checked during preview operations
        to allow graceful cancellation.
        """
        self._log('info', "Cancelling preview operation")
        self._cancel_event.set()
    
    def is_cancelled(self) -> bool:
        """
        Check if preview has been cancelled
        
        Returns:
            True if cancelled, False otherwise
        """
        return self._cancel_event.is_set()
    
    def clear_preview(self) -> None:
        """Clear current preview data and selections"""
        self._all_declarations.clear()
        self._selected_declarations.clear()
        self._cancel_event.clear()
        self._log('debug', "Preview data cleared")
    
    def filter_xnktc_declarations(
        self,
        declarations: List[Declaration],
        exclude_xnktc: bool = True
    ) -> List[Declaration]:
        """
        Lọc tờ khai XNK tại chỗ (NKTC, XKTC, GCPTQ)
        
        Args:
            declarations: Danh sách tờ khai cần lọc
            exclude_xnktc: True để loại bỏ tờ khai XNK TC, False để giữ tất cả
            
        Returns:
            Danh sách tờ khai đã lọc
        """
        if not exclude_xnktc:
            self._log('debug', "XNK TC filter disabled, returning all declarations")
            return declarations
        
        # Filter out XNK TC declarations
        filtered = [decl for decl in declarations if not decl.is_xnktc]
        
        excluded_count = len(declarations) - len(filtered)
        
        if excluded_count > 0:
            self._log('info', f"Đã lọc bỏ {excluded_count} tờ khai XNK tại chỗ")
        
        return filtered
