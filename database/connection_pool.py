"""
Connection Pool for ECUS5 Database v2.0

Provides thread-safe database connections using thread-local storage.
Fixes the thread-safety issue where a single pyodbc.Connection was shared
across scheduler, manual mode, and clearance checker threads.

pyodbc connections are NOT thread-safe, so each thread needs its own connection.
"""

import threading
import pyodbc
from typing import Optional
from datetime import datetime
from contextlib import contextmanager

from models.config_models import DatabaseConfig
from logging_system.logger import Logger


class ConnectionPool:
    """
    Thread-local connection pool for pyodbc connections.
    
    Each thread gets its own connection, stored in thread-local storage.
    Connections are created lazily on first access per thread.
    """
    
    def __init__(self, config: DatabaseConfig, logger: Optional[Logger] = None):
        """
        Initialize connection pool.
        
        Args:
            config: Database configuration
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger
        self._local = threading.local()
        self._lock = threading.Lock()
        
        # Connection tracking
        self._connection_count = 0
        self._busy_timeout = 30  # seconds
    
    def _log(self, level: str, message: str) -> None:
        """Log with thread info."""
        if self.logger:
            thread_name = threading.current_thread().name
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(f"[Pool/{thread_name}] {message}")
    
    def _create_connection(self) -> pyodbc.Connection:
        """
        Create a new database connection.
        
        Returns:
            New pyodbc.Connection
            
        Raises:
            pyodbc.Error: If connection fails
        """
        connection_string = self.config.connection_string
        
        # Add connection timeout
        if "Connection Timeout" not in connection_string:
            connection_string += ";Connection Timeout=30"
        
        conn = pyodbc.connect(connection_string)
        
        # Set connection options
        conn.timeout = self._busy_timeout
        
        with self._lock:
            self._connection_count += 1
        
        self._log('info', f"Created new connection (total: {self._connection_count})")
        return conn
    
    def get_connection(self) -> pyodbc.Connection:
        """
        Get a connection for the current thread.
        
        Creates a new connection if one doesn't exist for this thread.
        
        Returns:
            pyodbc.Connection for current thread
        """
        # Check if connection exists for this thread
        conn = getattr(self._local, 'connection', None)
        
        if conn is None:
            # Create new connection for this thread
            conn = self._create_connection()
            self._local.connection = conn
            self._local.created_at = datetime.now()
        else:
            # Validate existing connection
            try:
                # Simple test query
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            except (pyodbc.Error, Exception):
                # Connection is dead, recreate
                self._log('warning', "Connection stale, recreating")
                try:
                    conn.close()
                except Exception:
                    pass
                    
                conn = self._create_connection()
                self._local.connection = conn
                self._local.created_at = datetime.now()
        
        return conn
    
    @contextmanager
    def connection(self):
        """
        Context manager for getting a connection.
        
        Usage:
            with pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = self.get_connection()
        try:
            yield conn
        except pyodbc.Error as e:
            self._log('error', f"Database error: {e}")
            raise
    
    def close_thread_connection(self) -> None:
        """Close connection for current thread."""
        conn = getattr(self._local, 'connection', None)
        if conn:
            try:
                conn.close()
                self._log('info', "Closed thread connection")
            except Exception:
                pass
            finally:
                self._local.connection = None
                with self._lock:
                    self._connection_count -= 1
    
    def close_all(self) -> None:
        """
        Close all connections.
        
        Note: This only closes the current thread's connection.
        Other threads must close their own connections.
        """
        self.close_thread_connection()
        self._log('info', "Pool shutdown initiated")
    
    @property
    def active_connections(self) -> int:
        """Get count of active connections."""
        return self._connection_count
    
    def test_connection(self) -> bool:
        """
        Test if current thread's connection is valid.
        
        Returns:
            True if connection works, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            self._log('error', f"Connection test failed: {e}")
            return False


# Global pool instance
_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_connection_pool(config: DatabaseConfig = None, logger: Logger = None) -> ConnectionPool:
    """
    Get or create the global connection pool.
    
    Args:
        config: Database config (required on first call)
        logger: Optional logger
        
    Returns:
        ConnectionPool instance
    """
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                if config is None:
                    raise ValueError("Config required for first pool initialization")
                _pool = ConnectionPool(config, logger)
    return _pool
