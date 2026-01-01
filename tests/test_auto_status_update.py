"""
Test module for Auto-Status Update Issue

This test simulates the SettingsDialog -> TrackingPanel callback flow
to verify if update_auto_status() properly updates the label.

Run with: py tests/test_auto_status_update.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from gui.styles import ModernStyles


class MockTrackingPanel(tk.Frame):
    """Mock version of TrackingPanel with auto_status_label."""
    
    def __init__(self, parent):
        super().__init__(parent, bg=ModernStyles.BG_SECONDARY)
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Countdown variables
        self._countdown_seconds = 0
        self._countdown_interval_id = None
        
        # Create toolbar
        toolbar = tk.Frame(self, bg=ModernStyles.BG_SECONDARY)
        toolbar.pack(fill=tk.X, pady=5)
        
        # Auto-tracking status label
        self.auto_status_label = tk.Label(
            toolbar,
            text="🔔 Tự động: BẬT",
            font=("Arial", 12, "bold"),
            fg=ModernStyles.SUCCESS_COLOR,
            bg=ModernStyles.BG_SECONDARY
        )
        self.auto_status_label.pack(side=tk.LEFT, padx=10)
        
        # Countdown label
        self.countdown_label = tk.Label(
            toolbar,
            text="⏱ 05:00",
            font=("Arial", 12, "bold"),
            fg=ModernStyles.TEXT_SECONDARY,
            bg=ModernStyles.BG_SECONDARY
        )
        self.countdown_label.pack(side=tk.LEFT, padx=10)
        
    def update_auto_status(self, enabled: bool) -> None:
        """
        Update the auto-tracking status label.
        This is the actual method from tracking_panel.py
        """
        print(f"[MockTrackingPanel] update_auto_status called with enabled={enabled}")
        
        if hasattr(self, 'auto_status_label'):
            if enabled:
                self.auto_status_label.config(
                    text="🔔 Tự động: BẬT",
                    fg=ModernStyles.SUCCESS_COLOR
                )
                print("[MockTrackingPanel] Label updated to BẬT (green)")
            else:
                self.auto_status_label.config(
                    text="🔕 Tự động: TẮT",
                    fg=ModernStyles.TEXT_SECONDARY
                )
                print("[MockTrackingPanel] Label updated to TẮT (gray)")
                # Also clear countdown when auto is disabled
                if hasattr(self, 'countdown_label'):
                    self.countdown_label.config(text="")
                    print("[MockTrackingPanel] Countdown label cleared")
        else:
            print("[MockTrackingPanel] ERROR: auto_status_label not found!")
            
    def start_countdown(self, interval_minutes: int):
        """Start countdown timer."""
        self._countdown_seconds = interval_minutes * 60
        minutes = self._countdown_seconds // 60
        seconds = self._countdown_seconds % 60
        self.countdown_label.config(text=f"⏱ {minutes:02d}:{seconds:02d}")
        print(f"[MockTrackingPanel] Countdown started: {minutes:02d}:{seconds:02d}")
        
    def stop_countdown(self):
        """Stop countdown timer."""
        if self._countdown_interval_id:
            self.after_cancel(self._countdown_interval_id)
            self._countdown_interval_id = None
        self._countdown_seconds = 0
        print("[MockTrackingPanel] Countdown stopped")


class MockSettingsDialog:
    """Mock version of SettingsDialog that simulates saving settings."""
    
    def __init__(self, parent, on_auto_check_changed=None):
        self.parent = parent
        self.on_auto_check_changed = on_auto_check_changed
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cài đặt (Test)")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Auto-check checkbox
        self.auto_check_var = tk.BooleanVar(value=True)
        
        frame = tk.Frame(self.dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Checkbutton(
            frame,
            text="Tự động kiểm tra trạng thái thông quan",
            variable=self.auto_check_var,
            font=("Arial", 11)
        ).pack(anchor=tk.W, pady=10)
        
        # Save button
        tk.Button(
            frame,
            text="Lưu",
            command=self._save,
            width=15,
            font=("Arial", 11)
        ).pack(pady=20)
        
        print("[MockSettingsDialog] Dialog created")
        print(f"[MockSettingsDialog] on_auto_check_changed = {on_auto_check_changed}")
        
    def _save(self):
        """Simulate save_settings."""
        auto_check_enabled = self.auto_check_var.get()
        interval = 5  # Fixed value for test
        
        print(f"\n[MockSettingsDialog] Saving...")
        print(f"[MockSettingsDialog] auto_check_enabled = {auto_check_enabled}")
        print(f"[MockSettingsDialog] on_auto_check_changed = {self.on_auto_check_changed}")
        
        # This is the actual code from settings_dialog.py
        if self.on_auto_check_changed:
            try:
                print("[MockSettingsDialog] Calling on_auto_check_changed callback...")
                self.on_auto_check_changed(auto_check_enabled, interval)
                print("[MockSettingsDialog] Callback executed successfully!")
            except Exception as e:
                print(f"[MockSettingsDialog] ERROR: Callback failed: {e}")
        else:
            print("[MockSettingsDialog] WARNING: on_auto_check_changed is None!")
            
        self.dialog.destroy()
        print("[MockSettingsDialog] Dialog closed\n")


class TestApp:
    """Test application to verify the callback flow."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto-Status Update Test")
        self.root.geometry("600x300")
        
        # Apply basic styling
        self.root.configure(bg=ModernStyles.BG_SECONDARY)
        
        # Create tracking panel (mock)
        self.tracking_panel = MockTrackingPanel(self.root)
        
        # Button to open settings
        btn_frame = tk.Frame(self.root, bg=ModernStyles.BG_SECONDARY)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Open Settings Dialog",
            command=self._show_settings,
            width=20,
            font=("Arial", 11)
        ).pack()
        
        # Status info
        tk.Label(
            self.root,
            text="1. Click 'Open Settings Dialog'\n2. Uncheck the checkbox\n3. Click 'Lưu'\n4. Observe: Label should change to '🔕 Tự động: TẮT'",
            font=("Arial", 10),
            bg=ModernStyles.BG_SECONDARY,
            fg=ModernStyles.TEXT_SECONDARY,
            justify=tk.LEFT
        ).pack(pady=10)
        
    def _show_settings(self):
        """Show settings dialog - same pattern as customs_gui._show_settings_dialog."""
        print("\n" + "="*50)
        print("[TestApp] Opening settings dialog...")
        
        def on_auto_check_changed(enabled: bool, interval: int):
            """Callback when auto-check settings change."""
            print(f"[TestApp] on_auto_check_changed called: enabled={enabled}, interval={interval}")
            
            # Update tracking panel status label
            if hasattr(self, 'tracking_panel') and self.tracking_panel:
                print("[TestApp] Calling tracking_panel.update_auto_status()...")
                self.tracking_panel.update_auto_status(enabled)
                
                if enabled:
                    self.tracking_panel.start_countdown(interval)
                else:
                    self.tracking_panel.stop_countdown()
            else:
                print("[TestApp] ERROR: tracking_panel not found!")
                
        # Create dialog with callback passed in constructor
        MockSettingsDialog(
            self.root,
            on_auto_check_changed=on_auto_check_changed
        )
        
        print("[TestApp] Settings dialog opened")
        print("="*50)
        
    def run(self):
        """Run the test application."""
        print("\n" + "="*50)
        print("AUTO-STATUS UPDATE TEST")
        print("="*50)
        print("This test verifies the callback flow from")
        print("SettingsDialog -> CustomsGUI -> TrackingPanel")
        print("="*50 + "\n")
        
        self.root.mainloop()


if __name__ == "__main__":
    app = TestApp()
    app.run()
