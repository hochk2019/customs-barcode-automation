"""
PDF Naming Service

This module provides filename generation for PDF barcode files based on
configurable naming formats. Supports multiple naming patterns with
automatic fallback logic for empty fields.

Requirements: 5.3, 5.4, 5.5, 5.6
"""

import re
import logging
from enum import Enum
from typing import Optional

from models.declaration_models import Declaration


logger = logging.getLogger(__name__)


class PdfNamingFormat(Enum):
    """
    PDF file naming format options
    
    TAX_CODE: {tax_code}_{declaration_number}.pdf
    INVOICE: {invoice_number}_{declaration_number}.pdf
    BILL_OF_LADING: {bill_of_lading}_{declaration_number}.pdf
    """
    TAX_CODE = "tax_code"
    INVOICE = "invoice"
    BILL_OF_LADING = "bill_of_lading"


class PdfNamingService:
    """
    Service for generating PDF filenames based on configurable naming format.
    
    Supports three naming formats:
    - tax_code: {tax_code}_{declaration_number}.pdf
    - invoice: {invoice_number}_{declaration_number}.pdf
    - bill_of_lading: {bill_of_lading}_{declaration_number}.pdf
    
    Implements fallback logic: if the selected field is empty, falls back
    to tax_code format.
    
    Requirements: 5.3, 5.4, 5.5, 5.6
    """
    
    # Valid naming format values
    VALID_FORMATS = {"tax_code", "invoice", "bill_of_lading"}
    
    # Characters not allowed in filenames (Windows restrictions)
    INVALID_FILENAME_CHARS = r'[<>:"/\\|?*]'
    
    def __init__(self, naming_format: str = "tax_code"):
        """
        Initialize PdfNamingService with specified naming format.
        
        Args:
            naming_format: Naming format to use. One of:
                - "tax_code": Use tax code + declaration number
                - "invoice": Use invoice number + declaration number
                - "bill_of_lading": Use bill of lading + declaration number
                
        If invalid format is provided, defaults to "tax_code".
        """
        if naming_format not in self.VALID_FORMATS:
            logger.warning(
                f"Invalid naming format '{naming_format}', defaulting to 'tax_code'"
            )
            naming_format = "tax_code"
        
        self.naming_format = naming_format
        logger.info(f"PdfNamingService initialized with format: {naming_format}")
    
    def _sanitize_filename_part(self, value: Optional[str]) -> str:
        """
        Sanitize a string for use in a filename.
        
        Removes or replaces characters that are invalid in filenames.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string safe for use in filenames
        """
        if not value:
            return ""
        
        # Remove invalid characters
        sanitized = re.sub(self.INVALID_FILENAME_CHARS, '_', value)
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip().strip('.')
        
        return sanitized
    
    def _is_empty_or_whitespace(self, value: Optional[str]) -> bool:
        """
        Check if a value is None, empty, or contains only whitespace.
        
        Args:
            value: Value to check
            
        Returns:
            True if value is empty or whitespace-only, False otherwise
        """
        return not value or not value.strip()
    
    def _get_prefix_for_format(self, declaration: Declaration, format_type: str) -> Optional[str]:
        """
        Get the prefix value for a specific naming format.
        
        Args:
            declaration: Declaration object
            format_type: Naming format type
            
        Returns:
            Prefix value or None if empty
        """
        if format_type == "tax_code":
            return declaration.tax_code if not self._is_empty_or_whitespace(declaration.tax_code) else None
        elif format_type == "invoice":
            return declaration.invoice_number if not self._is_empty_or_whitespace(declaration.invoice_number) else None
        elif format_type == "bill_of_lading":
            return declaration.bill_of_lading if not self._is_empty_or_whitespace(declaration.bill_of_lading) else None
        return None
    
    def generate_filename(self, declaration: Declaration) -> str:
        """
        Generate filename for a declaration based on the configured naming format.
        
        Format patterns:
        - tax_code: {tax_code}_{declaration_number}.pdf
        - invoice: {invoice_number}_{declaration_number}.pdf  
        - bill_of_lading: {bill_of_lading}_{declaration_number}.pdf
        
        Fallback logic (Requirement 5.4):
        If the selected naming field is empty, falls back to tax_code format.
        
        Args:
            declaration: Declaration object containing the data
            
        Returns:
            Generated filename string (e.g., "2300944637_107784915560.pdf")
            
        Requirements: 5.3, 5.4, 5.5, 5.6
        """
        # Get declaration number (required)
        declaration_number = self._sanitize_filename_part(declaration.declaration_number)
        
        if not declaration_number:
            logger.error("Declaration number is empty, cannot generate filename")
            raise ValueError("Declaration number cannot be empty")
        
        # Try to get prefix based on selected format
        prefix = self._get_prefix_for_format(declaration, self.naming_format)
        
        # Fallback to tax_code if selected format field is empty (Requirement 5.4)
        if prefix is None and self.naming_format != "tax_code":
            logger.info(
                f"Field for format '{self.naming_format}' is empty, "
                f"falling back to tax_code format"
            )
            prefix = self._get_prefix_for_format(declaration, "tax_code")
        
        # If still no prefix (tax_code is also empty), use declaration number only
        if prefix is None:
            logger.warning(
                f"All naming fields are empty for declaration {declaration_number}, "
                f"using declaration number only"
            )
            filename = f"MV_{declaration_number}.pdf"
        else:
            # Sanitize prefix
            prefix = self._sanitize_filename_part(prefix)
            filename = f"MV_{prefix}_{declaration_number}.pdf"
        
        logger.debug(f"Generated filename: {filename} (format: {self.naming_format})")
        return filename
    
    def set_naming_format(self, naming_format: str) -> None:
        """
        Update the naming format.
        
        Args:
            naming_format: New naming format to use
            
        Raises:
            ValueError: If naming_format is not valid
        """
        if naming_format not in self.VALID_FORMATS:
            raise ValueError(
                f"Invalid naming format: {naming_format}. "
                f"Must be one of: {', '.join(self.VALID_FORMATS)}"
            )
        
        self.naming_format = naming_format
        logger.info(f"PDF naming format changed to: {naming_format}")
