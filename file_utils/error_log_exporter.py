"""
Error Log Exporter

This module provides functionality to export error logs to text files.
Supports exporting error entries from the current session with timestamps,
error types, declaration numbers, and error messages.

Requirements: 1.1, 1.2, 1.3
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class ErrorEntry:
    """
    Represents a single error entry for logging.
    
    Attributes:
        timestamp: When the error occurred
        declaration_number: The declaration number associated with the error
        error_type: Category of error (e.g., 'api_error', 'network_error', 'file_error')
        error_message: Detailed error message
    """
    timestamp: datetime
    declaration_number: str
    error_type: str
    error_message: str


class ErrorLogExporter:
    """
    Exports error entries to text files.
    
    Provides functionality to:
    - Format error entries for human-readable output
    - Generate default filenames with timestamps
    - Export all errors to a text file
    
    Requirements: 1.1, 1.2, 1.3
    """
    
    def __init__(self, error_entries: Optional[List[ErrorEntry]] = None):
        """
        Initialize ErrorLogExporter with error entries.
        
        Args:
            error_entries: List of ErrorEntry objects to export.
                          If None, initializes with empty list.
        """
        self._error_entries = error_entries if error_entries is not None else []
    
    @property
    def error_entries(self) -> List[ErrorEntry]:
        """Get the list of error entries."""
        return self._error_entries
    
    @error_entries.setter
    def error_entries(self, entries: List[ErrorEntry]) -> None:
        """Set the list of error entries."""
        self._error_entries = entries if entries is not None else []
    
    def add_error(self, entry: ErrorEntry) -> None:
        """
        Add a single error entry to the list.
        
        Args:
            entry: ErrorEntry to add
        """
        self._error_entries.append(entry)
    
    def add_error_from_values(
        self,
        declaration_number: str,
        error_type: str,
        error_message: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Create and add an error entry from individual values.
        
        Args:
            declaration_number: The declaration number associated with the error
            error_type: Category of error
            error_message: Detailed error message
            timestamp: When the error occurred (defaults to now)
        """
        entry = ErrorEntry(
            timestamp=timestamp or datetime.now(),
            declaration_number=declaration_number,
            error_type=error_type,
            error_message=error_message
        )
        self._error_entries.append(entry)
    
    def clear(self) -> None:
        """Clear all error entries."""
        self._error_entries.clear()
    
    def get_error_count(self) -> int:
        """Get the number of error entries."""
        return len(self._error_entries)
    
    def has_errors(self) -> bool:
        """Check if there are any error entries."""
        return len(self._error_entries) > 0
    
    def format_entry(self, entry: ErrorEntry) -> str:
        """
        Format a single error entry as a human-readable string.
        
        Format:
        [YYYY-MM-DD HH:MM:SS] [ERROR_TYPE] Declaration: XXXXX
        Message: Error message here
        
        Args:
            entry: ErrorEntry to format
            
        Returns:
            Formatted string representation of the error entry
            
        Requirements: 1.2
        """
        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        lines = [
            f"[{timestamp_str}] [{entry.error_type.upper()}] Declaration: {entry.declaration_number}",
            f"Message: {entry.error_message}",
            ""  # Empty line for separation
        ]
        return "\n".join(lines)
    
    def get_default_filename(self) -> str:
        """
        Generate default filename with current timestamp.
        
        Format: error_log_YYYYMMDD_HHMMSS.txt
        
        Returns:
            Default filename string
            
        Requirements: 1.3
        """
        now = datetime.now()
        return f"error_log_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    
    def export_to_file(self, filepath: str) -> bool:
        """
        Export all error entries to a text file.
        
        The file will contain:
        - Header with export timestamp and total error count
        - Separator line
        - All error entries formatted with format_entry()
        
        Args:
            filepath: Path to the output file
            
        Returns:
            True if export was successful, False otherwise
            
        Requirements: 1.1, 1.2
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header
                export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"Error Log Export - {export_time}\n")
                f.write(f"Total Errors: {len(self._error_entries)}\n")
                f.write("=" * 60 + "\n\n")
                
                # Write each error entry
                for entry in self._error_entries:
                    f.write(self.format_entry(entry))
            
            logger.info(f"Exported {len(self._error_entries)} error entries to {filepath}")
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to export error log to {filepath}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error exporting error log: {e}")
            return False
    
    def export_to_string(self) -> str:
        """
        Export all error entries to a string.
        
        Returns:
            String containing all formatted error entries
        """
        lines = []
        
        # Header
        export_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines.append(f"Error Log Export - {export_time}")
        lines.append(f"Total Errors: {len(self._error_entries)}")
        lines.append("=" * 60)
        lines.append("")
        
        # Error entries
        for entry in self._error_entries:
            lines.append(self.format_entry(entry))
        
        return "\n".join(lines)
