"""
Logger Module

This module provides a centralized logging system with file and console handlers,
log rotation, and support for multiple log levels.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from models.config_models import LoggingConfig


class Logger:
    """
    Centralized logging system with file rotation and console output.
    
    Provides logging functionality with:
    - File logging with rotation
    - Console logging
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Consistent formatting with timestamp and module name
    """
    
    def __init__(self, config: LoggingConfig, name: str = "CustomsAutomation"):
        """
        Initialize the logger
        
        Args:
            config: LoggingConfig object with logging settings
            name: Logger name (default: "CustomsAutomation")
        """
        self.config = config
        self.name = name
        self._logger = logging.getLogger(name)
        
        # Set log level
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
        self._logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Create formatters
        self._formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set up file handler with rotation
        self._setup_file_handler()
        
        # Set up console handler
        self._setup_console_handler()
    
    def _setup_file_handler(self) -> None:
        """Set up rotating file handler"""
        # Ensure log directory exists
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            filename=self.config.log_file,
            maxBytes=self.config.max_log_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        file_handler.setFormatter(self._formatter)
        
        self._logger.addHandler(file_handler)
    
    def _setup_console_handler(self) -> None:
        """Set up console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Console gets INFO and above
        console_handler.setFormatter(self._formatter)
        
        self._logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log a debug message
        
        Args:
            message: Log message
            **kwargs: Additional keyword arguments for logging
        """
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log an info message
        
        Args:
            message: Log message
            **kwargs: Additional keyword arguments for logging
        """
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log a warning message
        
        Args:
            message: Log message
            **kwargs: Additional keyword arguments for logging
        """
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info=None, **kwargs) -> None:
        """
        Log an error message
        
        Args:
            message: Log message
            exc_info: Exception info (True to include current exception)
            **kwargs: Additional keyword arguments for logging
        """
        self._logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info=None, **kwargs) -> None:
        """
        Log a critical message
        
        Args:
            message: Log message
            exc_info: Exception info (True to include current exception)
            **kwargs: Additional keyword arguments for logging
        """
        self._logger.critical(message, exc_info=exc_info, **kwargs)
    
    def get_logger(self) -> logging.Logger:
        """
        Get the underlying Python logger instance
        
        Returns:
            logging.Logger instance
        """
        return self._logger
