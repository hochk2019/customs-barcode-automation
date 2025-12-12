# Design Document - V1.3 Enhancements

## Overview

Phiên bản 1.3 của Customs Barcode Automation tập trung vào cải thiện trải nghiệm người dùng thông qua các tính năng mới: export log lỗi, thông báo desktop, cải thiện UX bảng preview, quản lý lỗi tốt hơn, phím tắt, nhớ vị trí cửa sổ, dark mode, backup tự động, tối ưu hiệu suất và giới hạn batch download.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUI Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ ThemeManager│  │NotifyManager│  │  EnhancedManualPanel    │  │
│  │ (Dark Mode) │  │ (Desktop)   │  │  (Preview Table UX)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │KeyboardMgr  │  │WindowState  │  │  ErrorLogExporter       │  │
│  │ (Shortcuts) │  │ (Position)  │  │  (Export Logs)          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Service Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │BackupService│  │CacheManager │  │  ParallelDownloader     │  │
│  │ (Auto DB)   │  │ (Preview)   │  │  (Concurrent DL)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │ErrorTracker │  │BatchLimiter │                               │
│  │ (History)   │  │ (Limit DL)  │                               │
│  └─────────────┘  └─────────────┘                               │
├─────────────────────────────────────────────────────────────────┤
│                      Data Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  ConfigurationManager                        ││
│  │  (Theme, Notifications, Window State, Batch Limit)          ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  TrackingDatabase                            ││
│  │  (Error History, Backup Management)                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. ThemeManager (gui/theme_manager.py)

Quản lý chế độ sáng/tối cho ứng dụng.

```python
class ThemeManager:
    LIGHT_THEME = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#f5f5f5',
        'bg_card': '#ffffff',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'accent': '#1976d2',
        'success': '#4caf50',
        'error': '#f44336',
        'warning': '#ff9800',
        'border': '#e0e0e0'
    }
    
    DARK_THEME = {
        'bg_primary': '#1e1e1e',
        'bg_secondary': '#2d2d2d',
        'bg_card': '#383838',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'accent': '#4fc3f7',
        'success': '#66bb6a',
        'error': '#ef5350',
        'warning': '#ffca28',
        'border': '#555555'
    }
    
    def __init__(self, root: tk.Tk, config_manager: ConfigurationManager)
    def apply_theme(self, theme: str) -> None  # 'light' or 'dark'
    def toggle_theme(self) -> None
    def get_current_theme(self) -> str
    def get_color(self, color_name: str) -> str
```

### 2. NotificationManager (gui/notification_manager.py)

Quản lý thông báo desktop và âm thanh.

```python
class NotificationManager:
    def __init__(self, config_manager: ConfigurationManager)
    def show_notification(self, title: str, message: str, icon: str = 'info') -> None
    def play_sound(self, sound_type: str = 'complete') -> None  # 'complete', 'error'
    def is_notifications_enabled(self) -> bool
    def is_sound_enabled(self) -> bool
    def set_notifications_enabled(self, enabled: bool) -> None
    def set_sound_enabled(self, enabled: bool) -> None
```

### 3. ErrorLogExporter (file_utils/error_log_exporter.py)

Xuất log lỗi ra file.

```python
@dataclass
class ErrorEntry:
    timestamp: datetime
    declaration_number: str
    error_type: str
    error_message: str

class ErrorLogExporter:
    def __init__(self, error_entries: List[ErrorEntry])
    def export_to_file(self, filepath: str) -> bool
    def get_default_filename(self) -> str  # "error_log_YYYYMMDD_HHMMSS.txt"
    def format_entry(self, entry: ErrorEntry) -> str
```

### 4. PreviewTableController (gui/preview_table_controller.py)

Điều khiển bảng preview với filter, sort, double-click.

```python
class PreviewTableController:
    def __init__(self, treeview: ttk.Treeview)
    def set_filter(self, status: str) -> None  # 'all', 'success', 'failed', 'pending'
    def sort_by_column(self, column: str, reverse: bool = False) -> None
    def toggle_sort(self, column: str) -> None
    def on_double_click(self, event) -> None
    def get_visible_items(self) -> List[str]
    def get_sort_state(self) -> Tuple[str, bool]  # (column, is_descending)
```

### 5. ErrorTracker (error_handling/error_tracker.py)

Theo dõi và lưu trữ lịch sử lỗi.

```python
class ErrorTracker:
    def __init__(self, tracking_db: TrackingDatabase)
    def record_error(self, declaration_number: str, error_type: str, message: str) -> None
    def get_error_history(self, days: int = 30) -> List[ErrorEntry]
    def get_errors_for_declaration(self, declaration_number: str) -> List[ErrorEntry]
    def clear_old_errors(self, days: int = 30) -> int  # Returns count deleted
```

### 6. KeyboardShortcutManager (gui/keyboard_shortcuts.py)

Quản lý phím tắt.

```python
class KeyboardShortcutManager:
    def __init__(self, root: tk.Tk)
    def register_shortcut(self, key: str, callback: Callable) -> None
    def unregister_shortcut(self, key: str) -> None
    def get_shortcuts_help(self) -> Dict[str, str]
    
    # Default shortcuts:
    # F5 -> refresh_preview
    # Ctrl+A -> select_all
    # Ctrl+Shift+A -> deselect_all
    # Escape -> stop_download
```

### 7. WindowStateManager (gui/window_state.py)

Quản lý vị trí và kích thước cửa sổ.

```python
@dataclass
class WindowState:
    x: int
    y: int
    width: int
    height: int

class WindowStateManager:
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 850
    
    def __init__(self, root: tk.Tk, config_manager: ConfigurationManager)
    def save_state(self) -> None
    def restore_state(self) -> None
    def is_position_valid(self, x: int, y: int) -> bool
    def get_centered_position(self) -> Tuple[int, int]
```

### 8. BackupService (database/backup_service.py)

Tự động backup tracking database.

```python
class BackupService:
    MAX_BACKUPS = 7
    BACKUP_INTERVAL_HOURS = 24
    
    def __init__(self, db_path: str, backup_dir: str)
    def check_and_backup(self) -> bool  # Returns True if backup was created
    def create_backup(self) -> str  # Returns backup filepath
    def cleanup_old_backups(self) -> int  # Returns count deleted
    def get_last_backup_time(self) -> Optional[datetime]
    def get_backup_filename(self) -> str  # "tracking_backup_YYYYMMDD.db"
```

### 9. CacheManager (processors/cache_manager.py)

Quản lý cache cho preview data.

```python
@dataclass
class CacheEntry:
    data: List[Declaration]
    timestamp: datetime
    company_filter: str
    date_range: Tuple[datetime, datetime]

class CacheManager:
    CACHE_TTL_MINUTES = 5
    
    def __init__(self)
    def get(self, key: str) -> Optional[CacheEntry]
    def set(self, key: str, data: List[Declaration], filters: dict) -> None
    def is_valid(self, key: str) -> bool
    def invalidate(self, key: str = None) -> None  # None = invalidate all
    def generate_key(self, company: str, from_date: datetime, to_date: datetime) -> str
```

### 10. ParallelDownloader (web_utils/parallel_downloader.py)

Tải song song nhiều mã vạch.

```python
class ParallelDownloader:
    MAX_CONCURRENT = 3
    
    def __init__(self, barcode_retriever, file_manager, max_concurrent: int = 3)
    def download_batch(self, declarations: List[Declaration], 
                       progress_callback: Callable[[int, int], None]) -> Dict[str, bool]
    def stop(self) -> None
    def get_active_count(self) -> int
```

### 11. BatchLimiter (processors/batch_limiter.py)

Giới hạn số tờ khai trong một batch.

```python
class BatchLimiter:
    MIN_LIMIT = 1
    MAX_LIMIT = 50
    DEFAULT_LIMIT = 20
    
    def __init__(self, config_manager: ConfigurationManager)
    def get_limit(self) -> int
    def set_limit(self, limit: int) -> bool  # Returns False if invalid
    def validate_selection(self, count: int) -> Tuple[bool, str]  # (is_valid, message)
```

## Data Models

### Config Extensions (models/config_models.py)

```python
@dataclass
class UIConfig:
    theme: str = 'light'  # 'light' or 'dark'
    notifications_enabled: bool = True
    sound_enabled: bool = True
    batch_limit: int = 20
    window_x: int = -1  # -1 = center
    window_y: int = -1
    window_width: int = 1200
    window_height: int = 850
```

### Error Entry (models/error_models.py)

```python
@dataclass
class ErrorEntry:
    id: int
    timestamp: datetime
    declaration_number: str
    error_type: str  # 'api_error', 'network_error', 'file_error', etc.
    error_message: str
    resolved: bool = False
```

### Database Schema Extension

```sql
-- New table for error history
CREATE TABLE IF NOT EXISTS error_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    declaration_number TEXT NOT NULL,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);

-- New table for backup tracking
CREATE TABLE IF NOT EXISTS backup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    backup_file TEXT NOT NULL,
    file_size INTEGER
);
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Error Log Export Completeness
*For any* list of error entries, exporting to file and reading back should contain all original entries with all required fields (timestamp, error_type, declaration_number, error_message).
**Validates: Requirements 1.1, 1.2**

### Property 2: Settings Persistence Round-Trip
*For any* valid settings value (notifications_enabled, sound_enabled, theme, batch_limit), saving to config and loading back should return the same value.
**Validates: Requirements 2.3, 2.6, 7.5, 10.5**

### Property 3: Filter Correctness
*For any* list of declarations and filter status, all visible items after filtering should match the selected status.
**Validates: Requirements 3.2**

### Property 4: Sort Ordering
*For any* list of declarations and sort column, after sorting ascending, each item should be less than or equal to the next item by that column's value.
**Validates: Requirements 3.3, 3.4**

### Property 5: Error Storage Completeness
*For any* error that occurs, the stored error entry should contain timestamp, declaration_number, error_type, and error_message.
**Validates: Requirements 4.4**

### Property 6: Selection Shortcuts
*For any* list of visible declarations, after Ctrl+A all items should be selected, and after Ctrl+Shift+A no items should be selected.
**Validates: Requirements 5.2, 5.3**

### Property 7: Window State Round-Trip
*For any* valid window position and size, saving state and restoring should result in the same position and size.
**Validates: Requirements 6.1, 6.2**

### Property 8: Theme Color Contrast
*For any* text color and background color pair in dark theme, the contrast ratio should be at least 4.5:1.
**Validates: Requirements 7.3**

### Property 9: Backup File Limit
*For any* number of backup operations, the number of backup files should never exceed MAX_BACKUPS (7).
**Validates: Requirements 8.3**

### Property 10: Cache Validity
*For any* cached preview data, if cache age is less than CACHE_TTL_MINUTES (5), is_valid should return True; otherwise False.
**Validates: Requirements 9.2, 9.3**

### Property 11: Parallel Download Limit
*For any* batch download operation, the number of concurrent downloads should never exceed MAX_CONCURRENT (3).
**Validates: Requirements 9.1**

### Property 12: Batch Limit Validation
*For any* batch limit value, it should be clamped between MIN_LIMIT (1) and MAX_LIMIT (50), with DEFAULT_LIMIT (20) for invalid values.
**Validates: Requirements 10.3, 10.4**

### Property 13: Batch Selection Validation
*For any* selection count exceeding batch limit, the download button should be disabled and warning message displayed.
**Validates: Requirements 10.1, 10.2**

## Error Handling

### Error Categories

1. **Configuration Errors**: Invalid settings values, missing config keys
   - Fallback to default values
   - Log warning message

2. **File System Errors**: Cannot write export file, backup fails
   - Show user-friendly error message
   - Suggest alternative location

3. **Database Errors**: Cannot store error history, backup log
   - Retry operation once
   - Log error and continue

4. **Network Errors**: Notification service unavailable
   - Silently fail for notifications
   - Continue normal operation

5. **Theme Errors**: Invalid color values
   - Fallback to light theme
   - Log warning

## Testing Strategy

### Property-Based Testing Library
- **Library**: Hypothesis (Python)
- **Minimum iterations**: 100 per property test

### Unit Tests
- ThemeManager: Theme switching, color retrieval
- NotificationManager: Enable/disable, sound playback mock
- ErrorLogExporter: Format validation, file writing
- PreviewTableController: Filter, sort operations
- WindowStateManager: Position validation, state persistence
- BackupService: Backup creation, cleanup logic
- CacheManager: TTL validation, key generation
- BatchLimiter: Limit validation, selection check

### Property-Based Tests
- Settings round-trip persistence
- Filter correctness for all status values
- Sort ordering for all columns
- Window state round-trip
- Color contrast calculations
- Backup file count invariant
- Cache validity based on age
- Concurrent download limit
- Batch limit validation

### Integration Tests
- Full theme switch cycle
- Complete backup and restore flow
- End-to-end error tracking
- Parallel download with real files
