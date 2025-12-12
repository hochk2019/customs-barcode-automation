"""
Error Tracker

This module provides functionality to track and store error history in the database.
Supports recording errors during barcode retrieval and viewing error history.

Requirements: 4.4, 4.5
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import sqlite3
import logging


logger = logging.getLogger(__name__)


@dataclass
class ErrorEntry:
    """
    Represents a single error entry for tracking.
    
    Attributes:
        id: Database ID (None for new entries)
        timestamp: When the error occurred
        declaration_number: The declaration number associated with the error
        error_type: Category of error (e.g., 'api_error', 'network_error', 'file_error')
        error_message: Detailed error message
        resolved: Whether the error has been resolved
    """
    timestamp: datetime
    declaration_number: str
    error_type: str
    error_message: str
    id: Optional[int] = None
    resolved: bool = False


class ErrorTracker:
    """
    Tracks and stores error history in the tracking database.
    
    Provides functionality to:
    - Record errors during barcode retrieval
    - Retrieve error history for a specified time period
    - Get errors for a specific declaration
    - Clear old errors
    
    Requirements: 4.4, 4.5
    """
    
    def __init__(self, tracking_db):
        """
        Initialize ErrorTracker with a tracking database.
        
        Args:
            tracking_db: TrackingDatabase instance for storing errors
        """
        self._tracking_db = tracking_db
        self._ensure_error_table_exists()
    
    def _ensure_error_table_exists(self) -> None:
        """
        Ensure the error_history table exists in the database.
        
        Creates the table if it doesn't exist.
        """
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            # Create error_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    declaration_number TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_timestamp 
                ON error_history(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_declaration 
                ON error_history(declaration_number)
            """)
            
            conn.commit()
            logger.info("Error history table initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize error history table: {e}")
            raise
        finally:
            conn.close()
    
    def record_error(
        self,
        declaration_number: str,
        error_type: str,
        message: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record an error in the database.
        
        Args:
            declaration_number: The declaration number associated with the error
            error_type: Category of error (e.g., 'api_error', 'network_error')
            message: Detailed error message
            timestamp: When the error occurred (defaults to now)
            
        Requirements: 4.4
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_history 
                (timestamp, declaration_number, error_type, error_message, resolved)
                VALUES (?, ?, ?, ?, 0)
            """, (
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                declaration_number,
                error_type,
                message
            ))
            
            conn.commit()
            logger.debug(f"Recorded error for {declaration_number}: {error_type}")
            
        except Exception as e:
            logger.error(f"Failed to record error: {e}")
            raise
        finally:
            conn.close()
    
    def get_error_history(self, days: int = 30) -> List[ErrorEntry]:
        """
        Get error history for the specified number of days.
        
        Args:
            days: Number of days to look back (default: 30)
            
        Returns:
            List of ErrorEntry objects ordered by timestamp descending
            
        Requirements: 4.5
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, declaration_number, error_type, error_message, resolved
                FROM error_history
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
            
            errors = []
            for row in cursor.fetchall():
                id_val, timestamp_str, declaration_number, error_type, error_message, resolved = row
                
                # Parse timestamp
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                entry = ErrorEntry(
                    id=id_val,
                    timestamp=timestamp,
                    declaration_number=declaration_number,
                    error_type=error_type,
                    error_message=error_message,
                    resolved=bool(resolved)
                )
                errors.append(entry)
            
            return errors
            
        except Exception as e:
            logger.error(f"Failed to get error history: {e}")
            raise
        finally:
            conn.close()
    
    def get_errors_for_declaration(self, declaration_number: str) -> List[ErrorEntry]:
        """
        Get all errors for a specific declaration.
        
        Args:
            declaration_number: The declaration number to look up
            
        Returns:
            List of ErrorEntry objects for the declaration
        """
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, declaration_number, error_type, error_message, resolved
                FROM error_history
                WHERE declaration_number = ?
                ORDER BY timestamp DESC
            """, (declaration_number,))
            
            errors = []
            for row in cursor.fetchall():
                id_val, timestamp_str, declaration_number, error_type, error_message, resolved = row
                
                # Parse timestamp
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                entry = ErrorEntry(
                    id=id_val,
                    timestamp=timestamp,
                    declaration_number=declaration_number,
                    error_type=error_type,
                    error_message=error_message,
                    resolved=bool(resolved)
                )
                errors.append(entry)
            
            return errors
            
        except Exception as e:
            logger.error(f"Failed to get errors for declaration {declaration_number}: {e}")
            raise
        finally:
            conn.close()
    
    def clear_old_errors(self, days: int = 30) -> int:
        """
        Delete errors older than the specified number of days.
        
        Args:
            days: Number of days to keep (default: 30)
            
        Returns:
            Number of errors deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute("""
                SELECT COUNT(*) FROM error_history
                WHERE timestamp < ?
            """, (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
            count = cursor.fetchone()[0]
            
            # Delete old errors
            cursor.execute("""
                DELETE FROM error_history
                WHERE timestamp < ?
            """, (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
            
            conn.commit()
            logger.info(f"Cleared {count} old errors (older than {days} days)")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear old errors: {e}")
            raise
        finally:
            conn.close()
    
    def mark_resolved(self, error_id: int) -> bool:
        """
        Mark an error as resolved.
        
        Args:
            error_id: Database ID of the error to mark
            
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE error_history
                SET resolved = 1
                WHERE id = ?
            """, (error_id,))
            
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to mark error {error_id} as resolved: {e}")
            return False
        finally:
            conn.close()
    
    def get_error_count(self, days: int = 30) -> int:
        """
        Get the count of errors in the specified time period.
        
        Args:
            days: Number of days to look back (default: 30)
            
        Returns:
            Number of errors
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self._tracking_db.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM error_history
                WHERE timestamp >= ?
            """, (cutoff_date.strftime('%Y-%m-%d %H:%M:%S'),))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Failed to get error count: {e}")
            return 0
        finally:
            conn.close()
