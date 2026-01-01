"""
Async Database Wrapper v2.0

Provides background thread execution for SQLite queries.
Prevents UI freezing from slow database operations.

Usage:
    result = await async_db.execute(tracking_db.get_all_processed_details)
"""

import threading
import queue
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps

from logging_system.logger import Logger


class AsyncDatabaseWrapper:
    """
    Wrapper for executing database queries in background threads.
    
    Uses ThreadPoolExecutor for efficient thread management.
    Provides callback-based and future-based async patterns.
    """
    
    def __init__(self, max_workers: int = 2, logger: Optional[Logger] = None):
        """
        Initialize async database wrapper.
        
        Args:
            max_workers: Maximum number of worker threads
            logger: Optional logger
        """
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="AsyncDB")
        self.logger = logger
    
    def execute(self, func: Callable, *args, **kwargs) -> Future:
        """
        Execute a function in background thread.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Future that resolves to function result
        """
        return self._executor.submit(func, *args, **kwargs)
    
    def execute_with_callback(
        self, 
        func: Callable, 
        callback: Callable[[Any], None],
        error_callback: Callable[[Exception], None] = None,
        *args, 
        **kwargs
    ) -> None:
        """
        Execute function with callbacks on completion.
        
        Args:
            func: Function to execute
            callback: Called with result on success
            error_callback: Called with exception on error
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        def task():
            try:
                result = func(*args, **kwargs)
                callback(result)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Async DB error: {e}")
                if error_callback:
                    error_callback(e)
        
        self._executor.submit(task)
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor."""
        self._executor.shutdown(wait=wait)
        if self.logger:
            self.logger.info("AsyncDatabaseWrapper shutdown")


def run_in_background(callback_attr: str = None):
    """
    Decorator to run a method in background thread.
    
    Args:
        callback_attr: Name of instance attribute for callback function
        
    Usage:
        class MyClass:
            def on_data_loaded(self, data):
                # Update UI
                pass
            
            @run_in_background(callback_attr='on_data_loaded')
            def load_data(self):
                return db.get_all_data()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            def task():
                result = func(self, *args, **kwargs)
                if callback_attr:
                    callback = getattr(self, callback_attr, None)
                    if callback:
                        callback(result)
                return result
            
            thread = threading.Thread(target=task, daemon=True)
            thread.start()
            return thread
        return wrapper
    return decorator


# Global instance
_async_db: Optional[AsyncDatabaseWrapper] = None


def get_async_db(logger: Logger = None) -> AsyncDatabaseWrapper:
    """Get global async database wrapper."""
    global _async_db
    if _async_db is None:
        _async_db = AsyncDatabaseWrapper(logger=logger)
    return _async_db
