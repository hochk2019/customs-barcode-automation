"""
User Preferences Manager for v2.0

REFACTORED: Now delegates to PreferencesService (JSON-based).
This file is kept for backwards compatibility.

Previous implementation used config.ini directly, which caused:
1. Race conditions with ConfigurationManager
2. Potential password overwrites
3. Thread-unsafe access
"""

from typing import List, Optional
from config.preferences_service import get_preferences_service, PreferencesService


class UserPreferences:
    """
    Backwards-compatible wrapper around PreferencesService.
    
    All methods delegate to the new JSON-based service.
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize preferences manager.
        
        Args:
            config_path: Ignored - kept for backwards compatibility
        """
        # Delegate to new service
        self._service = get_preferences_service()
    
    # =====================
    # Checkbox Settings
    # =====================
    
    @property
    def include_pending(self) -> bool:
        """Get 'include pending' checkbox state."""
        return self._service.include_pending
    
    @include_pending.setter
    def include_pending(self, value: bool) -> None:
        """Set and save 'include pending' checkbox state."""
        self._service.include_pending = value
    
    @property
    def exclude_xnktc(self) -> bool:
        """Get 'exclude XNK TC' checkbox state."""
        return self._service.exclude_xnktc
    
    @exclude_xnktc.setter
    def exclude_xnktc(self, value: bool) -> None:
        """Set and save 'exclude XNK TC' checkbox state."""
        self._service.exclude_xnktc = value
    
    # =====================
    # Multi-Select Settings
    # =====================
    
    @property
    def max_companies(self) -> int:
        """Get max number of companies that can be selected."""
        return self._service.max_companies
    
    @max_companies.setter
    def max_companies(self, value: int) -> None:
        """Set max companies (capped at hard limit)."""
        self._service.max_companies = value
    
    @property
    def selected_companies(self) -> List[str]:
        """Get list of selected company tax codes."""
        return self._service.selected_companies
    
    @selected_companies.setter
    def selected_companies(self, companies: List[str]) -> None:
        """Set and save selected companies."""
        self._service.selected_companies = companies
    
    # =====================
    # Tracking Settings
    # =====================
    
    @property
    def auto_check_enabled(self) -> bool:
        """Get auto-check enabled state."""
        return self._service.auto_check_enabled
    
    @auto_check_enabled.setter
    def auto_check_enabled(self, value: bool) -> None:
        """Set and save auto-check enabled state."""
        self._service.auto_check_enabled = value
    
    @property
    def auto_check_interval(self) -> int:
        """Get auto-check interval in minutes."""
        return self._service.auto_check_interval
    
    @auto_check_interval.setter
    def auto_check_interval(self, value: int) -> None:
        """Set and save auto-check interval (minutes)."""
        self._service.auto_check_interval = value
    
    @property
    def retention_days(self) -> int:
        """Get retention days for tracking data."""
        return self._service.retention_days
    
    @retention_days.setter
    def retention_days(self, value: int) -> None:
        """Set and save retention days."""
        self._service.retention_days = value
    
    @property
    def notification_popup(self) -> bool:
        """Get popup notification enabled state."""
        return self._service.notification_popup
    
    @notification_popup.setter
    def notification_popup(self, value: bool) -> None:
        """Set and save popup notification state."""
        self._service.notification_popup = value
    
    @property
    def notification_sound(self) -> bool:
        """Get sound notification enabled state."""
        return self._service.notification_sound
    
    @notification_sound.setter
    def notification_sound(self, value: bool) -> None:
        """Set and save sound notification state."""
        self._service.notification_sound = value

    @property
    def api_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self._service.api_timeout
    
    @api_timeout.setter
    def api_timeout(self, value: int) -> None:
        """Set and save API timeout."""
        self._service.api_timeout = value


# Global instance (lazy initialization)
_preferences: Optional[UserPreferences] = None


def get_preferences() -> UserPreferences:
    """Get global preferences instance."""
    global _preferences
    if _preferences is None:
        _preferences = UserPreferences()
    return _preferences
