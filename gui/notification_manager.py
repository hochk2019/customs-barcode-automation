"""
Notification Manager for Customs Barcode Automation

This module provides desktop notifications and sound playback functionality
for important events like batch download completion and database errors.

Implements Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
"""

import os
import sys
import threading
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from config.configuration_manager import ConfigurationManager


class NotificationManager:
    """
    Manages desktop notifications and sound playback.
    
    Provides:
    - Windows toast notifications for important events
    - Sound playback for completion and error events
    - Settings persistence through ConfigurationManager
    
    Requirements:
    - 2.1: Show notification on batch download complete
    - 2.2: Show notification on database connection error
    - 2.3: Persist notification preferences to config.ini
    - 2.4: Respect disabled notifications setting
    - 2.5: Play completion sound when enabled
    - 2.6: Persist sound preferences to config.ini
    """
    
    # Sound types
    SOUND_COMPLETE = 'complete'
    SOUND_ERROR = 'error'
    SOUND_WARNING = 'warning'
    
    def __init__(self, config_manager: Optional['ConfigurationManager'] = None):
        """
        Initialize NotificationManager.
        
        Args:
            config_manager: Optional ConfigurationManager instance for settings persistence
        """
        self._config_manager = config_manager
        self._notifications_enabled = True
        self._sound_enabled = True
        self._toast_available = False
        
        # Load settings from config if available
        if config_manager:
            self._notifications_enabled = config_manager.get_notifications_enabled()
            self._sound_enabled = config_manager.get_sound_enabled()
        
        # Check if toast notifications are available (Windows only)
        self._init_toast_notifications()
    
    def _init_toast_notifications(self) -> None:
        """Initialize toast notification support."""
        if sys.platform != 'win32':
            self._toast_available = False
            return
        
        try:
            # Try to import plyer for cross-platform notifications
            from plyer import notification
            self._toast_available = True
            self._notification_backend = 'plyer'
        except ImportError:
            try:
                # Fallback to win10toast
                from win10toast import ToastNotifier
                self._toaster = ToastNotifier()
                self._toast_available = True
                self._notification_backend = 'win10toast'
            except ImportError:
                # No notification library available
                self._toast_available = False
                self._notification_backend = None
    
    def show_notification(self, title: str, message: str, icon: str = 'info') -> bool:
        """
        Display a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message body
            icon: Icon type ('info', 'warning', 'error')
            
        Returns:
            True if notification was shown, False otherwise
            
        Requirements: 2.1, 2.2, 2.4
        """
        # Check if notifications are enabled (Requirement 2.4)
        if not self._notifications_enabled:
            return False
        
        # Check if toast notifications are available
        if not self._toast_available:
            return False
        
        try:
            # Show notification in a separate thread to avoid blocking
            def show_toast():
                try:
                    if self._notification_backend == 'plyer':
                        from plyer import notification
                        notification.notify(
                            title=title,
                            message=message,
                            app_name='Customs Barcode Automation',
                            timeout=5
                        )
                    elif self._notification_backend == 'win10toast':
                        self._toaster.show_toast(
                            title=title,
                            msg=message,
                            duration=5,
                            threaded=True
                        )
                except Exception:
                    pass  # Silently fail for notifications
            
            thread = threading.Thread(target=show_toast, daemon=True)
            thread.start()
            return True
            
        except Exception:
            return False
    
    def play_sound(self, sound_type: str = SOUND_COMPLETE) -> bool:
        """
        Play a notification sound.
        
        Args:
            sound_type: Type of sound ('complete', 'error', 'warning')
            
        Returns:
            True if sound was played, False otherwise
            
        Requirements: 2.5
        """
        # Check if sound is enabled
        if not self._sound_enabled:
            return False
        
        # Only play sounds on Windows
        if sys.platform != 'win32':
            return False
        
        try:
            import winsound
            
            # Map sound types to Windows system sounds
            sound_map = {
                self.SOUND_COMPLETE: winsound.MB_OK,
                self.SOUND_ERROR: winsound.MB_ICONHAND,
                self.SOUND_WARNING: winsound.MB_ICONEXCLAMATION
            }
            
            sound_flag = sound_map.get(sound_type, winsound.MB_OK)
            
            # Play sound in a separate thread to avoid blocking
            def play():
                try:
                    winsound.MessageBeep(sound_flag)
                except Exception:
                    pass
            
            thread = threading.Thread(target=play, daemon=True)
            thread.start()
            return True
            
        except ImportError:
            return False
        except Exception:
            return False
    
    def notify_batch_complete(self, success_count: int, error_count: int) -> None:
        """
        Show notification for batch download completion.
        
        Args:
            success_count: Number of successful downloads
            error_count: Number of failed downloads
            
        Requirements: 2.1, 2.5
        """
        total = success_count + error_count
        
        if error_count == 0:
            title = "Tải mã vạch hoàn tất"
            message = f"Đã tải thành công {success_count}/{total} mã vạch"
            icon = 'info'
            sound_type = self.SOUND_COMPLETE
        else:
            title = "Tải mã vạch hoàn tất"
            message = f"Thành công: {success_count}, Lỗi: {error_count}"
            icon = 'warning'
            sound_type = self.SOUND_WARNING
        
        # Show notification (Requirement 2.1)
        self.show_notification(title, message, icon)
        
        # Play sound (Requirement 2.5)
        self.play_sound(sound_type)
    
    def notify_database_error(self, error_message: str) -> None:
        """
        Show notification for database connection error.
        
        Args:
            error_message: Error message to display
            
        Requirements: 2.2
        """
        title = "Lỗi kết nối cơ sở dữ liệu"
        message = error_message[:100] if len(error_message) > 100 else error_message
        
        self.show_notification(title, message, 'error')
        self.play_sound(self.SOUND_ERROR)
    
    def is_notifications_enabled(self) -> bool:
        """
        Check if notifications are enabled.
        
        Returns:
            True if notifications are enabled
        """
        return self._notifications_enabled
    
    def is_sound_enabled(self) -> bool:
        """
        Check if sound is enabled.
        
        Returns:
            True if sound is enabled
        """
        return self._sound_enabled
    
    def set_notifications_enabled(self, enabled: bool) -> None:
        """
        Enable or disable notifications.
        
        Args:
            enabled: True to enable notifications
            
        Requirements: 2.3
        """
        self._notifications_enabled = enabled
        
        # Persist to config (Requirement 2.3)
        if self._config_manager:
            self._config_manager.set_notifications_enabled(enabled)
    
    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Enable or disable sound.
        
        Args:
            enabled: True to enable sound
            
        Requirements: 2.6
        """
        self._sound_enabled = enabled
        
        # Persist to config (Requirement 2.6)
        if self._config_manager:
            self._config_manager.set_sound_enabled(enabled)
    
    def is_toast_available(self) -> bool:
        """
        Check if toast notifications are available on this system.
        
        Returns:
            True if toast notifications can be shown
        """
        return self._toast_available
    
    def get_notification_backend(self) -> Optional[str]:
        """
        Get the notification backend being used.
        
        Returns:
            Backend name ('plyer', 'win10toast') or None if unavailable
        """
        return getattr(self, '_notification_backend', None)
