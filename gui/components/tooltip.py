"""
Tooltip Module

Provides reusable tooltip functionality with configurable delay.
Designed to be used across the application for button descriptions.

Usage:
    from gui.components.tooltip import ToolTip
    
    button = tk.Button(parent, text="Click me")
    ToolTip(button, "This button does something useful", delay=500)
"""

import tkinter as tk
from typing import Optional


class ToolTip:
    """
    Creates a tooltip for a given widget with configurable delay.
    
    Attributes:
        widget: The widget to attach the tooltip to
        text: The tooltip text to display
        delay: Milliseconds to wait before showing tooltip (default: 500ms)
        wrap_length: Maximum width of tooltip text before wrapping (default: 300px)
    """
    
    def __init__(
        self, 
        widget: tk.Widget, 
        text: str, 
        delay: int = 500,
        wrap_length: int = 300,
        bg_color: str = "#ffffe0",  # Light yellow
        fg_color: str = "#000000",  # Black
        font: tuple = ("Arial", 9)
    ):
        """
        Initialize tooltip for a widget.
        
        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
            delay: Delay in milliseconds before showing tooltip
            wrap_length: Maximum width before text wraps
            bg_color: Background color of tooltip
            fg_color: Foreground (text) color
            font: Font tuple (family, size)
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font = font
        
        self._tooltip_window: Optional[tk.Toplevel] = None
        self._schedule_id: Optional[str] = None
        
        # Bind events
        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
    
    def _on_enter(self, event=None) -> None:
        """Schedule tooltip display after delay."""
        self._cancel_schedule()
        self._schedule_id = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event=None) -> None:
        """Cancel scheduled tooltip and hide if visible."""
        self._cancel_schedule()
        self._hide_tooltip()
    
    def _cancel_schedule(self) -> None:
        """Cancel any scheduled tooltip display."""
        if self._schedule_id:
            self.widget.after_cancel(self._schedule_id)
            self._schedule_id = None
    
    def _show_tooltip(self) -> None:
        """Display the tooltip window."""
        if self._tooltip_window or not self.text:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self._tooltip_window = tk.Toplevel(self.widget)
        self._tooltip_window.wm_overrideredirect(True)  # No window decorations
        self._tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Make tooltip appear on top
        self._tooltip_window.wm_attributes("-topmost", True)
        
        # Create tooltip frame with border
        frame = tk.Frame(
            self._tooltip_window,
            background=self.bg_color,
            borderwidth=1,
            relief=tk.SOLID
        )
        frame.pack()
        
        # Create tooltip label
        label = tk.Label(
            frame,
            text=self.text,
            justify=tk.LEFT,
            background=self.bg_color,
            foreground=self.fg_color,
            font=self.font,
            wraplength=self.wrap_length,
            padx=6,
            pady=4
        )
        label.pack()
    
    def _hide_tooltip(self) -> None:
        """Hide and destroy the tooltip window."""
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None
    
    def update_text(self, new_text: str) -> None:
        """Update tooltip text."""
        self.text = new_text
        # If tooltip is currently visible, hide and reschedule
        if self._tooltip_window:
            self._hide_tooltip()
    
    def destroy(self) -> None:
        """Clean up tooltip bindings and windows."""
        self._cancel_schedule()
        self._hide_tooltip()
        try:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
            self.widget.unbind("<ButtonPress>")
        except tk.TclError:
            pass  # Widget already destroyed


def add_tooltip(widget: tk.Widget, text: str, delay: int = 500) -> ToolTip:
    """
    Convenience function to add a tooltip to a widget.
    
    Args:
        widget: Widget to attach tooltip to
        text: Tooltip text
        delay: Delay in ms before showing (default: 500)
        
    Returns:
        ToolTip instance
    """
    return ToolTip(widget, text, delay=delay)


# Predefined tooltip texts for common buttons (Vietnamese)
BUTTON_TOOLTIPS = {
    # Preview Panel buttons
    "preview": "Xem trước danh sách tờ khai từ database (F5)",
    "download": "Lấy mã vạch cho các tờ khai đã chọn",
    "add_tracking": "Thêm tờ khai vào danh sách theo dõi thông quan",
    "cancel": "Hủy thao tác xem trước đang thực hiện",
    "stop": "Dừng quá trình tải mã vạch (chờ tờ khai hiện tại hoàn tất)",
    "export_log": "Xuất nhật ký lỗi ra file",
    "retry_failed": "Thử lại các tờ khai tải thất bại",
    
    # Tracking Panel buttons
    "get_barcode": "Lấy mã vạch cho các tờ khai đã chọn",
    "check_now": "Kiểm tra trạng thái thông quan ngay",
    "delete": "Xóa các tờ khai đã chọn khỏi danh sách theo dõi",
    "refresh": "Làm mới danh sách theo dõi",
    "add_manual": "Thêm tờ khai thủ công vào danh sách",
    
    # Company Section buttons
    "scan_companies": "Quét công ty từ database ECUS5",
    "add_company": "Thêm công ty mới",
    "remove_company": "Xóa công ty đã chọn",
    
    # Settings buttons
    "save_config": "Lưu cấu hình và kết nối lại",
    "test_connection": "Kiểm tra kết nối database",
}
