"""
Update module for GitHub Auto-Update functionality.

This module provides automatic update checking and downloading from GitHub Releases.
"""

from update.models import UpdateInfo, DownloadProgress
from update.version_comparator import VersionComparator
from update.update_checker import UpdateChecker
from update.download_manager import DownloadManager

__all__ = [
    'UpdateInfo',
    'DownloadProgress',
    'VersionComparator',
    'UpdateChecker',
    'DownloadManager',
]
