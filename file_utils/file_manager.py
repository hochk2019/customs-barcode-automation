"""
File Manager for PDF barcode operations

This module handles all file operations including filename generation,
directory management, and PDF saving with overwrite support.
"""

import os
import logging
from typing import Optional
from models.declaration_models import Declaration
from file_utils.pdf_naming_service import PdfNamingService


logger = logging.getLogger(__name__)


class FileManager:
    """
    Manages PDF file operations for customs barcode automation.
    
    Responsibilities:
    - Generate standardized filenames using PdfNamingService
    - Create output directories as needed
    - Save PDF content to disk
    - Check for existing files
    - Support file overwriting for re-downloads
    - Handle file system errors gracefully
    """
    
    def __init__(self, output_directory: str, pdf_naming_service: Optional[PdfNamingService] = None):
        """
        Initialize FileManager with output directory.
        
        Args:
            output_directory: Path to directory where PDF files will be saved
            pdf_naming_service: Optional PdfNamingService for custom filename generation.
                               If not provided, defaults to tax_code format.
        """
        self.output_directory = output_directory
        self._pdf_naming_service = pdf_naming_service or PdfNamingService("tax_code")
        logger.info(f"FileManager initialized with output directory: {output_directory}")
    
    @property
    def pdf_naming_service(self) -> PdfNamingService:
        """Get the PDF naming service"""
        return self._pdf_naming_service
    
    @pdf_naming_service.setter
    def pdf_naming_service(self, service: PdfNamingService) -> None:
        """Set the PDF naming service"""
        self._pdf_naming_service = service
        logger.info(f"PDF naming service updated to format: {service.naming_format}")
    
    def generate_filename(self, declaration: Declaration) -> str:
        """
        Generate filename for a declaration using the configured naming service.
        
        The filename format depends on the PdfNamingService configuration:
        - tax_code: {tax_code}_{declaration_number}.pdf
        - invoice: {invoice_number}_{declaration_number}.pdf
        - bill_of_lading: {bill_of_lading}_{declaration_number}.pdf
        
        Args:
            declaration: Declaration object
            
        Returns:
            Filename string based on configured naming format
            
        Requirements: 5.3, 5.4, 5.5, 5.6
        """
        filename = self._pdf_naming_service.generate_filename(declaration)
        logger.debug(f"Generated filename: {filename} (format: {self._pdf_naming_service.naming_format})")
        return filename
    
    def get_file_path(self, declaration: Declaration) -> str:
        """
        Get full file path for a declaration.
        
        Args:
            declaration: Declaration object
            
        Returns:
            Full path to the PDF file
        """
        filename = self.generate_filename(declaration)
        file_path = os.path.join(self.output_directory, filename)
        return file_path
    
    def file_exists(self, declaration: Declaration) -> bool:
        """
        Check if PDF file already exists for a declaration.
        
        Args:
            declaration: Declaration object
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.get_file_path(declaration)
        exists = os.path.exists(file_path)
        logger.debug(f"File exists check for {file_path}: {exists}")
        return exists
    
    def ensure_directory_exists(self) -> None:
        """
        Create output directory if it doesn't exist.
        
        Creates all intermediate directories as needed.
        
        Raises:
            OSError: If directory creation fails due to permissions or other errors
        """
        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(self.output_directory, exist_ok=True)
                logger.info(f"Created output directory: {self.output_directory}")
            except OSError as e:
                logger.error(f"Failed to create directory {self.output_directory}: {e}")
                raise
        else:
            logger.debug(f"Output directory already exists: {self.output_directory}")
    
    def save_barcode(
        self, 
        declaration: Declaration, 
        pdf_content: bytes, 
        overwrite: bool = False
    ) -> Optional[str]:
        """
        Save PDF barcode content to disk.
        
        Args:
            declaration: Declaration object
            pdf_content: PDF file content as bytes
            overwrite: If True, overwrite existing file; if False, skip if exists
            
        Returns:
            Full path to saved file if successful, None if skipped or failed
            
        Raises:
            OSError: If file system operations fail
        """
        try:
            # Ensure directory exists before saving
            self.ensure_directory_exists()
            
            file_path = self.get_file_path(declaration)
            
            # Check if file already exists
            if os.path.exists(file_path) and not overwrite:
                logger.warning(
                    f"File already exists and overwrite=False, skipping: {file_path}"
                )
                return None
            
            # Write PDF content to file
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            action = "Overwrote" if (os.path.exists(file_path) and overwrite) else "Saved"
            logger.info(f"{action} barcode PDF: {file_path}")
            
            return file_path
            
        except OSError as e:
            logger.error(
                f"File system error saving barcode for {declaration.id}: {e}",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error saving barcode for {declaration.id}: {e}",
                exc_info=True
            )
            raise
