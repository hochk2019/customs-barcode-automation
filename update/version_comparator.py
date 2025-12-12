"""
Version comparison utilities using semantic versioning.
"""

from typing import Tuple


class VersionComparator:
    """Compare versions using semantic versioning (major.minor.patch)."""
    
    @staticmethod
    def parse_version(version_str: str) -> Tuple[int, int, int]:
        """
        Parse version string to tuple (major, minor, patch).
        Automatically strips 'v' prefix if present.
        
        Args:
            version_str: Version string like "1.2.3" or "v1.2.3"
            
        Returns:
            Tuple of (major, minor, patch)
            
        Raises:
            ValueError: If format is invalid
        """
        # Strip 'v' or 'V' prefix if present
        version = version_str.strip()
        if version.lower().startswith('v'):
            version = version[1:]
        
        parts = version.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}. Expected X.Y.Z")
        
        try:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])
        except ValueError:
            raise ValueError(f"Invalid version format: {version_str}. Version parts must be integers")
        
        if major < 0 or minor < 0 or patch < 0:
            raise ValueError(f"Invalid version format: {version_str}. Version parts must be non-negative")
        
        return (major, minor, patch)
    
    @staticmethod
    def compare(version1: str, version2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2
            0 if version1 == version2
            1 if version1 > version2
        """
        v1 = VersionComparator.parse_version(version1)
        v2 = VersionComparator.parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    @staticmethod
    def is_newer(latest: str, current: str) -> bool:
        """
        Check if latest version is newer than current version.
        
        Args:
            latest: Latest version string
            current: Current version string
            
        Returns:
            True if latest > current, False otherwise
        """
        return VersionComparator.compare(latest, current) > 0
