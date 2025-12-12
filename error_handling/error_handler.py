"""
Error handler module for customs barcode automation.

This module provides error handling capabilities including:
- Retry with exponential backoff
- Graceful error handling
- Error categorization
- Error logging
"""

import time
import logging
from typing import Callable, Any, Tuple, Type, Optional
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors that can occur in the system."""
    DATABASE = "database"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATA = "data"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Handles errors with retry logic and graceful degradation.
    
    Provides methods for:
    - Retrying operations with exponential backoff
    - Handling errors gracefully with default values
    - Categorizing errors for appropriate handling
    - Logging errors with context
    """
    
    def __init__(self, max_retries: int = 3, base_delay: int = 5, logger: Optional[logging.Logger] = None):
        """
        Initialize the error handler.
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 5)
            logger: Logger instance for error logging (default: creates new logger)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logger or logging.getLogger(__name__)
    
    def handle_with_retry(
        self, 
        operation: Callable[[], Any], 
        error_types: Tuple[Type[Exception], ...] = (Exception,),
        operation_name: str = "Operation"
    ) -> Any:
        """
        Execute operation with exponential backoff retry.
        
        For any network error during barcode retrieval, the system should retry 
        up to max_retries times with exponentially increasing delays.
        
        Args:
            operation: Callable to execute
            error_types: Tuple of exception types to catch and retry
            operation_name: Name of the operation for logging
            
        Returns:
            Result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = operation()
                if attempt > 0:
                    self.logger.info(
                        f"{operation_name} succeeded on attempt {attempt + 1}"
                    )
                return result
                
            except error_types as e:
                last_exception = e
                
                # If this was the last attempt, raise the exception
                if attempt == self.max_retries - 1:
                    self.logger.error(
                        f"{operation_name} failed after {self.max_retries} attempts: {e}",
                        exc_info=True
                    )
                    raise
                
                # Calculate exponential backoff delay
                delay = self.base_delay * (2 ** attempt)
                
                self.logger.warning(
                    f"{operation_name} attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def handle_gracefully(
        self, 
        operation: Callable[[], Any], 
        default: Any = None,
        operation_name: str = "Operation"
    ) -> Any:
        """
        Execute operation and return default value on error.
        
        For any unhandled exception during workflow execution, the system should 
        log the error and continue without terminating.
        
        Args:
            operation: Callable to execute
            default: Default value to return on error
            operation_name: Name of the operation for logging
            
        Returns:
            Result of the operation or default value on error
        """
        try:
            return operation()
        except Exception as e:
            self.logger.error(
                f"{operation_name} failed: {e}",
                exc_info=True
            )
            return default
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error for appropriate handling.
        
        Args:
            error: Exception to categorize
            
        Returns:
            ErrorCategory enum value
        """
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()
        
        # Network errors (check first to avoid confusion with connection-related database errors)
        if any(keyword in error_type for keyword in ['connectionerror', 'timeouterror', 'httperror', 'urlerror', 'sslerror']):
            return ErrorCategory.NETWORK
        if any(keyword in error_message for keyword in ['network', 'connection refused', 'ssl', 'certificate', 'http']):
            return ErrorCategory.NETWORK
        
        # Database errors
        if any(keyword in error_type for keyword in ['database', 'sql', 'pyodbc']):
            return ErrorCategory.DATABASE
        if any(keyword in error_message for keyword in ['database', 'sql', 'query']):
            return ErrorCategory.DATABASE
        
        # File system errors
        if any(keyword in error_type for keyword in ['file', 'ioerror', 'oserror', 'permission']):
            return ErrorCategory.FILE_SYSTEM
        if any(keyword in error_message for keyword in ['file', 'directory', 'permission', 'disk', 'path']):
            return ErrorCategory.FILE_SYSTEM
        
        # Data errors
        if any(keyword in error_type for keyword in ['valueerror', 'typeerror', 'attributeerror', 'keyerror', 'indexerror']):
            return ErrorCategory.DATA
        if any(keyword in error_message for keyword in ['invalid', 'format', 'parse']):
            return ErrorCategory.DATA
        
        # Configuration errors
        if any(keyword in error_type for keyword in ['config', 'setting']):
            return ErrorCategory.CONFIGURATION
        if any(keyword in error_message for keyword in ['configuration', 'config', 'setting']):
            return ErrorCategory.CONFIGURATION
        
        return ErrorCategory.UNKNOWN
    
    def log_error_with_category(self, error: Exception, context: str = "") -> None:
        """
        Log an error with its category and context.
        
        Args:
            error: Exception to log
            context: Additional context about where the error occurred
        """
        category = self.categorize_error(error)
        
        log_message = f"[{category.value.upper()}] {context}: {error}" if context else f"[{category.value.upper()}] {error}"
        
        self.logger.error(log_message, exc_info=True)
