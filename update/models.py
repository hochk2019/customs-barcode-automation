"""
Data models for the update module.
"""

from dataclasses import dataclass


@dataclass
class UpdateInfo:
    """Information about an available update."""
    current_version: str
    latest_version: str
    release_notes: str
    download_url: str
    file_size: int
    release_date: str
    checksum_url: str = ""


@dataclass
class DownloadProgress:
    """Download progress state."""
    downloaded_bytes: int
    total_bytes: int
    speed_bps: float  # bytes per second
    
    @property
    def percentage(self) -> float:
        """Calculate download percentage (0-100)."""
        if self.total_bytes == 0:
            return 0.0
        return (self.downloaded_bytes / self.total_bytes) * 100.0
    
    @property
    def speed_text(self) -> str:
        """Format speed as human-readable string (e.g., '1.5 MB/s')."""
        if self.speed_bps < 1024:
            return f"{self.speed_bps:.1f} B/s"
        elif self.speed_bps < 1024 * 1024:
            return f"{self.speed_bps / 1024:.1f} KB/s"
        else:
            return f"{self.speed_bps / (1024 * 1024):.1f} MB/s"
