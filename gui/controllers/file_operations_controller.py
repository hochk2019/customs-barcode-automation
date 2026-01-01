"""
File Operations Controller v2.0

Handles file-related operations extracted from customs_gui.py.
- Open file location in explorer
- File path utilities
"""

import os
import subprocess
import platform
from typing import Optional

from logging_system.logger import Logger


class FileOperationsController:
    """
    Controller for file operations.
    
    Handles opening files in explorer, file path resolution, etc.
    """
    
    def __init__(self, config_manager, tracking_db, logger: Logger):
        """
        Initialize file operations controller.
        
        Args:
            config_manager: Configuration manager
            tracking_db: Tracking database for file paths
            logger: Logger instance
        """
        self.config_manager = config_manager
        self.tracking_db = tracking_db
        self.logger = logger
    
    def open_file_location(self, decl_number: str, tax_code: str) -> bool:
        """
        Open file location in file explorer.
        
        Args:
            decl_number: Declaration number
            tax_code: Tax code
            
        Returns:
            True if file was opened successfully
        """
        try:
            # Try to get file path from tracking database
            file_path = self._get_file_path_from_db(decl_number, tax_code)
            
            # Fallback to constructing path from config
            if not file_path:
                file_path = self._construct_file_path(decl_number, tax_code)
            
            # Normalize path
            file_path = os.path.normpath(file_path)
            
            if os.path.exists(file_path):
                return self._open_in_explorer(file_path)
            else:
                # File not found, try to open output directory
                return self._open_output_directory()
                
        except Exception as e:
            self.logger.error(f"Failed to open file location: {e}")
            return False
    
    def _get_file_path_from_db(self, decl_number: str, tax_code: str) -> Optional[str]:
        """Get file path from tracking database."""
        try:
            processed_list = self.tracking_db.get_all_processed_details()
            for processed in processed_list:
                if processed.declaration_number == decl_number and processed.tax_code == tax_code:
                    return processed.file_path
        except Exception as e:
            self.logger.warning(f"Could not get file path from tracking DB: {e}")
        return None
    
    def _construct_file_path(self, decl_number: str, tax_code: str) -> str:
        """Construct file path from config."""
        output_dir = self.config_manager.get_output_path()
        return os.path.join(output_dir, f"{tax_code}_{decl_number}.pdf")
    
    def _open_in_explorer(self, file_path: str) -> bool:
        """Open file in system explorer."""
        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
            
            self.logger.info(f"Opened file location: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open explorer: {e}")
            return False
    
    def _open_output_directory(self) -> bool:
        """Open output directory in explorer."""
        try:
            output_dir = self.config_manager.get_output_path()
            if os.path.exists(output_dir):
                if platform.system() == "Windows":
                    os.startfile(output_dir)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", output_dir])
                else:
                    subprocess.run(["xdg-open", output_dir])
                
                self.logger.info(f"Opened output directory: {output_dir}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to open output directory: {e}")
        return False
