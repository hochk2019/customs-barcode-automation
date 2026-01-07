"""
Preferences Service v2.0

Thread-safe JSON-based user preferences with file locking.
Separates user preferences from deploy config (config.ini).

This replaces the config.ini-based approach to avoid:
1. Race conditions when multiple parsers write to config.ini
2. Accidental overwrite of encrypted passwords
3. Thread-unsafe access from different components
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional
from contextlib import contextmanager

# Windows file locking
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

# Unix file locking
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False


class PreferencesService:
    """
    Thread-safe preferences service with file locking.
    
    Uses JSON for storage instead of INI to:
    - Support complex data types (lists, nested objects)
    - Avoid conflicts with ConfigParser
    - Enable schema validation
    """
    
    # Schema definition with defaults
    SCHEMA = {
        # Checkbox states
        "include_pending": {"type": bool, "default": True},
        "exclude_xnktc": {"type": bool, "default": False},
        
        # Multi-select settings
        "max_companies": {"type": int, "default": 5, "min": 1, "max": 15},
        "selected_companies": {"type": list, "default": []},
        
        # Date range
        "default_date_days": {"type": int, "default": 1, "min": 1, "max": 30},
        
        # Tracking settings
        "auto_check_enabled": {"type": bool, "default": True},
        "auto_check_interval_minutes": {"type": int, "default": 6, "min": 1, "max": 60},
        "retention_days": {"type": int, "default": 5, "min": 1, "max": 365},
        "notification_popup": {"type": bool, "default": True},
        "notification_sound": {"type": bool, "default": True},
        "tracking_sort_order": {"type": str, "default": "pending_first"},  # Options: pending_first, date_desc, date_asc, company
        
        # Window state (v2.0)
        "window_geometry": {"type": str, "default": ""},
        "window_maximized": {"type": bool, "default": False},
        
        # Recent items
        "recent_companies": {"type": list, "default": []},
        "recent_customs_codes": {"type": list, "default": []},  # Max 10 recent customs codes
        
        # API settings (v1.5.1)
        "api_timeout_seconds": {"type": int, "default": 10, "min": 5, "max": 60},

        # Preview panel state (v1.5.2)
        "preview_filter_index": {"type": int, "default": 0, "min": 0, "max": 10},
        "preview_sort_column": {"type": str, "default": ""},
        "preview_sort_descending": {"type": bool, "default": False},
        "preview_column_widths": {"type": dict, "default": {}},
    }
    
    def __init__(self, preferences_path: str = "data/preferences.json"):
        """
        Initialize preferences service.
        
        Args:
            preferences_path: Path to JSON preferences file
        """
        self._path = Path(preferences_path)
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {}
        self._dirty = False
        
        # Ensure directory exists
        self._path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing preferences
        self._load()
    
    @contextmanager
    def _file_lock(self, file_handle):
        """
        Cross-platform file locking context manager.
        
        Uses msvcrt on Windows, fcntl on Unix.
        """
        try:
            if HAS_MSVCRT:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
            elif HAS_FCNTL:
                fcntl.flock(file_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally:
            try:
                if HAS_MSVCRT:
                    msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
                elif HAS_FCNTL:
                    fcntl.flock(file_handle.fileno(), fcntl.LOCK_UN)
            except Exception:
                pass  # Ignore unlock errors
    
    def _load(self) -> None:
        """Load preferences from JSON file."""
        with self._lock:
            if self._path.exists():
                try:
                    with open(self._path, 'r', encoding='utf-8') as f:
                        self._data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    # Corrupted file, start fresh
                    self._data = {}
            
            # Apply defaults for missing keys
            self._apply_defaults()
    
    def _apply_defaults(self) -> None:
        """Apply default values for missing keys."""
        for key, schema in self.SCHEMA.items():
            if key not in self._data:
                self._data[key] = schema["default"]
    
    def _validate(self, key: str, value: Any) -> Any:
        """
        Validate and coerce value according to schema.
        
        Args:
            key: Preference key
            value: Value to validate
            
        Returns:
            Validated/coerced value
            
        Raises:
            ValueError: If validation fails
        """
        if key not in self.SCHEMA:
            raise ValueError(f"Unknown preference key: {key}")
        
        schema = self.SCHEMA[key]
        expected_type = schema["type"]
        
        # Type coercion
        if expected_type == bool and not isinstance(value, bool):
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')
            else:
                value = bool(value)
        elif expected_type == int and not isinstance(value, int):
            value = int(value)
        elif expected_type == list and not isinstance(value, list):
            if isinstance(value, str):
                value = [v.strip() for v in value.split(',') if v.strip()]
            else:
                value = list(value)
        elif expected_type == dict and not isinstance(value, dict):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = {}
            else:
                value = dict(value)
        elif expected_type == str and not isinstance(value, str):
            value = str(value)
        
        # Range validation for integers
        if expected_type == int:
            if "min" in schema:
                value = max(value, schema["min"])
            if "max" in schema:
                value = min(value, schema["max"])
        
        return value
    
    def save(self) -> bool:
        """
        Save preferences to file with locking.
        
        Returns:
            True if save successful, False otherwise
        """
        with self._lock:
            try:
                # Write to temp file first
                temp_path = self._path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self._data, f, indent=2, ensure_ascii=False)
                
                # Atomic rename (Windows may need delete first)
                if self._path.exists():
                    try:
                        self._path.unlink()
                    except Exception:
                        pass
                        
                temp_path.rename(self._path)
                self._dirty = False
                return True
                
            except Exception as e:
                print(f"Failed to save preferences: {e}")
                return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value
        """
        with self._lock:
            if key in self._data:
                return self._data[key]
            elif key in self.SCHEMA:
                return self.SCHEMA[key]["default"]
            else:
                return default
    
    def set(self, key: str, value: Any, save_immediately: bool = True) -> None:
        """
        Set a preference value.
        
        Args:
            key: Preference key
            value: Value to set
            save_immediately: If True, save to disk immediately
        """
        with self._lock:
            validated_value = self._validate(key, value)
            
            if self._data.get(key) != validated_value:
                self._data[key] = validated_value
                self._dirty = True
                
                if save_immediately:
                    self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all preferences as a dictionary."""
        with self._lock:
            return self._data.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset all preferences to default values."""
        with self._lock:
            self._data = {}
            self._apply_defaults()
            self.save()
    
    # =====================
    # Convenience Properties
    # =====================
    
    @property
    def include_pending(self) -> bool:
        return self.get("include_pending")
    
    @include_pending.setter
    def include_pending(self, value: bool) -> None:
        self.set("include_pending", value)
    
    @property
    def exclude_xnktc(self) -> bool:
        return self.get("exclude_xnktc")
    
    @exclude_xnktc.setter
    def exclude_xnktc(self, value: bool) -> None:
        self.set("exclude_xnktc", value)
    
    @property
    def max_companies(self) -> int:
        return self.get("max_companies")
    
    @max_companies.setter
    def max_companies(self, value: int) -> None:
        self.set("max_companies", value)
    
    @property
    def selected_companies(self) -> list:
        return self.get("selected_companies")
    
    @selected_companies.setter
    def selected_companies(self, value: list) -> None:
        self.set("selected_companies", value)
    
    @property
    def auto_check_enabled(self) -> bool:
        return self.get("auto_check_enabled")
    
    @auto_check_enabled.setter
    def auto_check_enabled(self, value: bool) -> None:
        self.set("auto_check_enabled", value)
    
    @property
    def auto_check_interval(self) -> int:
        return self.get("auto_check_interval_minutes")
    
    @auto_check_interval.setter
    def auto_check_interval(self, value: int) -> None:
        self.set("auto_check_interval_minutes", value)
    
    @property
    def retention_days(self) -> int:
        return self.get("retention_days")
    
    @retention_days.setter
    def retention_days(self, value: int) -> None:
        self.set("retention_days", value)
    
    @property
    def notification_popup(self) -> bool:
        return self.get("notification_popup")
    
    @notification_popup.setter
    def notification_popup(self, value: bool) -> None:
        self.set("notification_popup", value)
    
    @property
    def notification_sound(self) -> bool:
        return self.get("notification_sound")
    
    @notification_sound.setter
    def notification_sound(self, value: bool) -> None:
        self.set("notification_sound", value)
    
    @property
    def tracking_sort_order(self) -> str:
        return self.get("tracking_sort_order")
    
    @tracking_sort_order.setter
    def tracking_sort_order(self, value: str) -> None:
        self.set("tracking_sort_order", value)

    @property
    def api_timeout(self) -> int:
        return self.get("api_timeout_seconds")
    
    @api_timeout.setter
    def api_timeout(self, value: int) -> None:
        self.set("api_timeout_seconds", value)


# Global instance with lazy initialization
_service: Optional[PreferencesService] = None
_service_lock = threading.Lock()


def get_preferences_service() -> PreferencesService:
    """
    Get the global preferences service instance.
    
    Thread-safe lazy initialization.
    """
    global _service
    if _service is None:
        with _service_lock:
            if _service is None:
                _service = PreferencesService()
    return _service


# Backwards compatibility alias
def get_preferences() -> PreferencesService:
    """Backwards compatible alias for get_preferences_service()."""
    return get_preferences_service()
