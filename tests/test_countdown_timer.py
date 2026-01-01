"""
Test module for Countdown Timer Reset Issue

This test simulates the ClearanceChecker behavior and verifies:
1. Countdown starts correctly
2. Countdown decrements every second
3. Shows "Đang kiểm tra..." when reaching 00:00
4. Resets to initial value after check completes (even with empty list)

Run with: py tests/test_countdown_timer.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
import time
import threading


class TestCountdownTimer:
    """Test harness for countdown timer functionality."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Countdown Timer Test")
        self.root.geometry("500x300")
        
        # Simulate the countdown variables
        self._countdown_seconds = 0
        self._countdown_interval_id = None
        self.check_interval_minutes = 1  # 1 minute
        
        self._create_ui()
        
    def _create_ui(self):
        """Create test UI."""
        # Info label
        tk.Label(
            self.root,
            text="Test Countdown Timer Reset",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Countdown display
        self.countdown_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 24, "bold"),
            fg="blue"
        )
        self.countdown_label.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Status: Ready",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Start Countdown (1 min)",
            command=self._start_countdown_test,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Simulate Check Complete",
            command=self._simulate_check_complete,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Stop",
            command=self._stop_countdown,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Log area
        tk.Label(self.root, text="Log:").pack(anchor=tk.W, padx=10)
        self.log_text = tk.Text(self.root, height=6, width=60)
        self.log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
    def _log(self, msg):
        """Add message to log."""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        
    def _start_countdown_test(self):
        """Start countdown timer (simulates TrackingPanel.start_countdown)."""
        self._log("Starting countdown...")
        self.start_countdown(self.check_interval_minutes)
        
    def start_countdown(self, interval_minutes: int):
        """
        Start countdown timer display.
        (Copy of TrackingPanel.start_countdown)
        """
        self.stop_countdown()  # Stop any existing countdown
        self._countdown_seconds = interval_minutes * 60
        
        # Immediately update label to show starting time
        minutes = self._countdown_seconds // 60
        seconds = self._countdown_seconds % 60
        self.countdown_label.config(text=f"⏱ {minutes:02d}:{seconds:02d}")
        self.root.update_idletasks()  # Force UI refresh
        
        self._log(f"Countdown set to {minutes:02d}:{seconds:02d}")
        
        # Start countdown loop
        self._countdown_seconds -= 1
        self._countdown_interval_id = self.root.after(1000, self._update_countdown)
        
    def _update_countdown(self):
        """Update countdown display every second."""
        if self._countdown_seconds > 0:
            minutes = self._countdown_seconds // 60
            seconds = self._countdown_seconds % 60
            time_str = f"⏱ {minutes:02d}:{seconds:02d}"
            
            self.countdown_label.config(text=time_str)
            
            self._countdown_seconds -= 1
            self._countdown_interval_id = self.root.after(1000, self._update_countdown)
        else:
            # Timer reached zero - show checking message
            self.countdown_label.config(text="⏱ Đang kiểm tra...")
            self._log("Countdown reached 00:00 - showing 'Đang kiểm tra...'")
            self.status_label.config(text="Status: Waiting for check to complete...")
            
            # Simulate check starting
            self._simulate_clearance_check()
            
    def stop_countdown(self):
        """Stop countdown timer."""
        if self._countdown_interval_id:
            self.root.after_cancel(self._countdown_interval_id)
            self._countdown_interval_id = None
        self._countdown_seconds = 0
        
    def reset_countdown(self, interval_minutes: int):
        """Reset countdown after check completes."""
        self._log(f"Resetting countdown to {interval_minutes} minutes")
        self.start_countdown(interval_minutes)
        
    def _simulate_clearance_check(self):
        """
        Simulate ClearanceChecker behavior.
        This runs in background thread like the real checker.
        """
        def check_thread():
            self._log("ClearanceChecker: Starting check (background thread)")
            
            # Simulate check taking 2 seconds
            time.sleep(2)
            
            self._log("ClearanceChecker: Check complete, calling on_status_changed")
            
            # This is how the real code calls the callback
            # root.after(0, callback) schedules on main thread
            self.root.after(0, self._on_clearance_status_changed)
            
        threading.Thread(target=check_thread, daemon=True).start()
        
    def _on_clearance_status_changed(self):
        """
        Callback from ClearanceChecker.
        (Copy of CustomsGUI._on_clearance_status_changed)
        """
        self._log("_on_clearance_status_changed called")
        self._refresh_tracking_panel()
        
    def _refresh_tracking_panel(self):
        """
        Refresh and reset countdown.
        (Copy of CustomsGUI._refresh_tracking_panel)
        """
        self._log("_refresh_tracking_panel called")
        self.status_label.config(text="Status: Check complete, resetting countdown")
        
        # Reset countdown timer
        self.reset_countdown(self.check_interval_minutes)
        self._log(f"Countdown timer reset to {self.check_interval_minutes} minutes")
        
    def _simulate_check_complete(self):
        """Manually trigger check complete (for testing)."""
        self._log("Manual trigger: simulating check complete")
        self._on_clearance_status_changed()
        
    def _stop_countdown(self):
        """Stop button handler."""
        self.stop_countdown()
        self.countdown_label.config(text="⏱ Stopped")
        self._log("Countdown stopped manually")
        
    def run(self):
        """Run the test application."""
        self._log("Test application started")
        self._log("Click 'Start Countdown' to begin test")
        self._log("Or click 'Simulate Check Complete' to test reset")
        self.root.mainloop()


def main():
    """Run the test."""
    print("=" * 50)
    print("Countdown Timer Reset Test")
    print("=" * 50)
    print()
    print("This test verifies:")
    print("1. Countdown starts and decrements correctly")
    print("2. Shows 'Đang kiểm tra...' at 00:00")
    print("3. Resets to initial value after check completes")
    print()
    print("Starting test window...")
    
    test = TestCountdownTimer()
    test.run()


if __name__ == "__main__":
    main()
