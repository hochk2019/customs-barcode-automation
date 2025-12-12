"""
Property-based tests for Backup Service

**Feature: v1.3-enhancements**
"""

import os
import tempfile
import shutil
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
import pytest

from database.backup_service import BackupService


def create_test_db():
    """Create a temporary test database file"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.write(fd, b'test database content')
    os.close(fd)
    return path


# **Feature: v1.3-enhancements, Property 9: Backup File Limit**
# **Validates: Requirements 8.3**
@given(num_backups=st.integers(min_value=1, max_value=15))
@settings(max_examples=50)
def test_property_backup_file_limit(num_backups):
    """
    For any number of backup operations, the number of backup files
    should never exceed MAX_BACKUPS (7).
    
    **Feature: v1.3-enhancements, Property 9: Backup File Limit**
    **Validates: Requirements 8.3**
    """
    db_path = create_test_db()
    backup_dir = tempfile.mkdtemp()
    
    try:
        service = BackupService(db_path, backup_dir)
        
        # Create multiple backups with different dates
        for i in range(num_backups):
            # Create backup with unique filename
            backup_filename = f"tracking_backup_2024{i:02d}01.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(db_path, backup_path)
        
        # Run cleanup
        service.cleanup_old_backups()
        
        # Verify count doesn't exceed MAX_BACKUPS
        backup_count = service.get_backup_count()
        assert backup_count <= BackupService.MAX_BACKUPS, \
            f"Backup count {backup_count} exceeds MAX_BACKUPS {BackupService.MAX_BACKUPS}"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)


def test_property_backup_creates_file():
    """
    Creating a backup should create a file in the backup directory.
    
    **Feature: v1.3-enhancements, Property 9: Backup File Limit**
    **Validates: Requirements 8.2**
    """
    db_path = create_test_db()
    backup_dir = tempfile.mkdtemp()
    
    try:
        service = BackupService(db_path, backup_dir)
        
        # Create backup
        backup_path = service.create_backup()
        
        # Verify file exists
        assert os.path.exists(backup_path), "Backup file should exist"
        
        # Verify content matches
        with open(db_path, 'rb') as f:
            original_content = f.read()
        with open(backup_path, 'rb') as f:
            backup_content = f.read()
        
        assert original_content == backup_content, "Backup content should match original"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)


def test_property_backup_filename_format():
    """
    Backup filename should follow the format tracking_backup_YYYYMMDD.db.
    
    **Feature: v1.3-enhancements, Property 9: Backup File Limit**
    **Validates: Requirements 8.2**
    """
    db_path = create_test_db()
    backup_dir = tempfile.mkdtemp()
    
    try:
        service = BackupService(db_path, backup_dir)
        
        filename = service.get_backup_filename()
        
        # Verify format
        assert filename.startswith('tracking_backup_'), "Filename should start with 'tracking_backup_'"
        assert filename.endswith('.db'), "Filename should end with '.db'"
        
        # Verify date part
        date_part = filename[16:24]  # Extract YYYYMMDD
        assert date_part.isdigit(), "Date part should be numeric"
        assert len(date_part) == 8, "Date part should be 8 digits"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)


def test_property_check_and_backup_first_time():
    """
    First call to check_and_backup should create a backup.
    
    **Feature: v1.3-enhancements, Property 9: Backup File Limit**
    **Validates: Requirements 8.1**
    """
    db_path = create_test_db()
    backup_dir = tempfile.mkdtemp()
    
    try:
        service = BackupService(db_path, backup_dir)
        
        # First call should create backup
        result = service.check_and_backup()
        
        assert result == True, "First backup should be created"
        assert service.get_backup_count() >= 1, "Should have at least one backup"
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)


def test_property_cleanup_preserves_newest():
    """
    Cleanup should preserve the newest backups.
    
    **Feature: v1.3-enhancements, Property 9: Backup File Limit**
    **Validates: Requirements 8.3**
    """
    db_path = create_test_db()
    backup_dir = tempfile.mkdtemp()
    
    try:
        service = BackupService(db_path, backup_dir)
        
        # Create more than MAX_BACKUPS files
        for i in range(10):
            backup_filename = f"tracking_backup_2024{i+1:02d}01.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(db_path, backup_path)
            # Set modification time to ensure order
            import time
            time.sleep(0.01)
        
        # Run cleanup
        deleted = service.cleanup_old_backups()
        
        # Should have deleted some files
        assert deleted > 0, "Should have deleted some files"
        
        # Should have exactly MAX_BACKUPS remaining
        assert service.get_backup_count() == BackupService.MAX_BACKUPS
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
