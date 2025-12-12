"""
Backup Service

This module provides automatic backup functionality for the tracking database.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path


class BackupService:
    """
    Service for automatic database backup.
    
    Provides:
    - Check if backup is needed (last backup > 24 hours)
    - Create backup with timestamp filename
    - Cleanup old backups (keep max 7)
    
    Requirements: 8.1, 8.2, 8.3, 8.4
    """
    
    MAX_BACKUPS = 7
    BACKUP_INTERVAL_HOURS = 24
    
    def __init__(self, db_path: str, backup_dir: str = None):
        """
        Initialize BackupService.
        
        Args:
            db_path: Path to the database file
            backup_dir: Directory for backups (defaults to 'backups' in db directory)
        """
        self.db_path = db_path
        
        if backup_dir is None:
            db_dir = os.path.dirname(db_path) or '.'
            self.backup_dir = os.path.join(db_dir, 'backups')
        else:
            self.backup_dir = backup_dir
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Track last backup time
        self._last_backup_file = os.path.join(self.backup_dir, '.last_backup')
    
    def check_and_backup(self) -> bool:
        """
        Check if backup is needed and create one if so.
        
        Returns:
            True if backup was created, False otherwise
            
        Requirements: 8.1
        """
        if not os.path.exists(self.db_path):
            return False
        
        last_backup = self.get_last_backup_time()
        
        if last_backup is None:
            # No previous backup, create one
            self.create_backup()
            return True
        
        # Check if backup interval has passed
        hours_since_backup = (datetime.now() - last_backup).total_seconds() / 3600
        
        if hours_since_backup >= self.BACKUP_INTERVAL_HOURS:
            self.create_backup()
            return True
        
        return False
    
    def create_backup(self) -> str:
        """
        Create a backup of the database.
        
        Returns:
            Path to the backup file
            
        Requirements: 8.2
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        # Generate backup filename
        backup_filename = self.get_backup_filename()
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        # Update last backup time
        self._update_last_backup_time()
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        return backup_path
    
    def cleanup_old_backups(self) -> int:
        """
        Remove old backup files, keeping only MAX_BACKUPS most recent.
        
        Returns:
            Number of files deleted
            
        Requirements: 8.3
        """
        # Get all backup files
        backup_files = self._get_backup_files()
        
        if len(backup_files) <= self.MAX_BACKUPS:
            return 0
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        # Delete oldest files
        files_to_delete = backup_files[self.MAX_BACKUPS:]
        deleted_count = 0
        
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
            except OSError:
                pass
        
        return deleted_count
    
    def get_last_backup_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last backup.
        
        Returns:
            Datetime of last backup, or None if no backup exists
        """
        if os.path.exists(self._last_backup_file):
            try:
                with open(self._last_backup_file, 'r') as f:
                    timestamp_str = f.read().strip()
                    return datetime.fromisoformat(timestamp_str)
            except (ValueError, IOError):
                pass
        
        # Fall back to checking backup files
        backup_files = self._get_backup_files()
        if backup_files:
            # Get most recent backup
            newest = max(backup_files, key=lambda f: os.path.getmtime(f))
            return datetime.fromtimestamp(os.path.getmtime(newest))
        
        return None
    
    def get_backup_filename(self) -> str:
        """
        Generate backup filename with timestamp.
        
        Returns:
            Filename in format "tracking_backup_YYYYMMDD.db"
            
        Requirements: 8.2
        """
        date_str = datetime.now().strftime("%Y%m%d")
        return f"tracking_backup_{date_str}.db"
    
    def get_backup_count(self) -> int:
        """Get the number of existing backup files"""
        return len(self._get_backup_files())
    
    def _get_backup_files(self) -> List[str]:
        """Get list of backup file paths"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backup_files = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('tracking_backup_') and filename.endswith('.db'):
                backup_files.append(os.path.join(self.backup_dir, filename))
        
        return backup_files
    
    def _update_last_backup_time(self) -> None:
        """Update the last backup timestamp file"""
        try:
            with open(self._last_backup_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except IOError:
            pass
