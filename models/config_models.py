"""
Configuration data models

This module contains data classes for configuration management.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    server: str
    database: str
    username: str
    password: str
    timeout: int = 30
    
    @property
    def connection_string(self) -> str:
        """Generate SQL Server connection string"""
        return (
            f"DRIVER={{SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Connection Timeout={self.timeout};"
        )


@dataclass
class DatabaseProfile:
    """
    Database profile for storing multiple database configurations.
    
    Allows users to save and switch between different database connections
    (e.g., production, test, different branches).
    """
    name: str
    server: str
    database: str
    username: str
    password: str  # Will be encrypted when stored
    timeout: int = 30
    
    def to_database_config(self) -> DatabaseConfig:
        """Convert profile to DatabaseConfig"""
        return DatabaseConfig(
            server=self.server,
            database=self.database,
            username=self.username,
            password=self.password,
            timeout=self.timeout
        )
    
    @classmethod
    def from_database_config(cls, name: str, config: DatabaseConfig) -> 'DatabaseProfile':
        """Create profile from DatabaseConfig"""
        return cls(
            name=name,
            server=config.server,
            database=config.database,
            username=config.username,
            password=config.password,
            timeout=config.timeout
        )


@dataclass
class BarcodeServiceConfig:
    """Barcode service configuration"""
    api_url: str
    primary_web_url: str
    backup_web_url: str  # Deprecated in V2.0 - kept for backward compatibility
    timeout: int  # Legacy field, kept for backward compatibility
    max_retries: int
    retry_delay: int
    api_timeout: int = 10  # Reduced from 30s
    web_timeout: int = 15  # Separate timeout for web scraping
    session_reuse: bool = True  # Enable session reuse for performance
    output_path: Optional[str] = None  # User-configurable output directory
    # V2.0: Retrieval method - 'api', 'web', or 'auto' (default)
    retrieval_method: str = "auto"
    # V1.1: PDF naming format - 'tax_code', 'invoice', or 'bill_of_lading'
    pdf_naming_format: str = "tax_code"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str
    log_file: str
    max_log_size: int
    backup_count: int


@dataclass
class SelectorCache:
    """Cache for working selectors to improve performance"""
    tax_code_selector: Optional[str] = None
    declaration_number_selector: Optional[str] = None
    declaration_date_selector: Optional[str] = None
    customs_office_selector: Optional[str] = None
    submit_button_selector: Optional[str] = None
    last_updated: Optional[datetime] = None
    
    def is_valid(self, max_age_hours: int = 24) -> bool:
        """
        Check if cache is still valid
        
        Args:
            max_age_hours: Maximum age in hours before cache expires
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not self.last_updated:
            return False
        age = datetime.now() - self.last_updated
        return age.total_seconds() < (max_age_hours * 3600)


@dataclass
class UIConfig:
    """
    UI configuration settings for the application.
    
    Stores user preferences for theme, notifications, sound, batch limits,
    window position/size, panel split position, and recent companies count.
    """
    theme: str = 'light'  # 'light' or 'dark'
    notifications_enabled: bool = True
    sound_enabled: bool = True
    batch_limit: int = 20  # Max declarations per batch (1-50)
    window_x: int = -1  # -1 = center on screen
    window_y: int = -1
    window_width: int = 1200
    window_height: int = 850
    # Layout optimization settings (Requirements 8.3, 8.4, 6.3, 6.4)
    panel_split_position: float = 0.38  # Left panel ratio (0.25-0.50)
    recent_companies_count: int = 5  # Number of recent companies to display (3-10)
    
    def validate(self) -> bool:
        """
        Validate UI configuration values.
        
        Returns:
            True if all values are valid
        """
        if self.theme not in ('light', 'dark'):
            return False
        if not (1 <= self.batch_limit <= 50):
            return False
        if self.window_width < 800 or self.window_height < 600:
            return False
        if not (0.25 <= self.panel_split_position <= 0.50):
            return False
        if not (3 <= self.recent_companies_count <= 10):
            return False
        return True
    
    @classmethod
    def get_default(cls) -> 'UIConfig':
        """Get default UI configuration."""
        return cls()
