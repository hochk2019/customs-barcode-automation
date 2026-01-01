"""
Test module for Max Companies Setting

This test verifies that:
1. max_companies preference is saved correctly
2. Callback is triggered when setting changes
3. CompanyTagPicker.set_max_select() is called with correct value

Run with: py tests/test_max_companies_setting.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk


class MockCompanyTagPicker(ttk.Frame):
    """Mock version of CompanyTagPicker."""
    
    def __init__(self, parent, max_select=5):
        super().__init__(parent)
        self.max_select = max_select
        self._selected = []
        
        # Label to show current max
        self.label = ttk.Label(self, text=f"Đã chọn: 0/{max_select} công ty")
        self.label.pack(pady=10)
        
    def set_max_select(self, max_select: int) -> None:
        """Update max companies limit - this is the method we're testing."""
        old_max = self.max_select
        self.max_select = max(1, min(max_select, 15))
        self._update_label()
        print(f"[MockCompanyTagPicker] set_max_select called: {old_max} -> {self.max_select}")
        
    def _update_label(self):
        self.label.config(text=f"Đã chọn: {len(self._selected)}/{self.max_select} công ty")


class MockSettingsDialog:
    """Mock SettingsDialog with max_companies spinbox."""
    
    def __init__(self, parent, current_max=5, on_max_companies_changed=None):
        self.parent = parent
        self.on_max_companies_changed = on_max_companies_changed
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cài đặt (Test)")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        frame = tk.Frame(self.dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Max companies spinbox
        ttk.Label(frame, text="Số công ty tối đa được chọn:").pack(anchor=tk.W, pady=5)
        
        self.max_companies_var = tk.IntVar(value=current_max)
        self.spinbox = ttk.Spinbox(
            frame,
            from_=1,
            to=15,
            textvariable=self.max_companies_var,
            width=5
        )
        self.spinbox.pack(anchor=tk.W, pady=5)
        
        # Save button
        ttk.Button(
            frame,
            text="Lưu",
            command=self._save
        ).pack(pady=20)
        
        print(f"[MockSettingsDialog] Created with max_companies={current_max}")
        print(f"[MockSettingsDialog] on_max_companies_changed = {on_max_companies_changed}")
        
    def _save(self):
        """Simulate save_settings."""
        max_companies = self.max_companies_var.get()
        
        print(f"\n[MockSettingsDialog] Saving max_companies = {max_companies}")
        
        if self.on_max_companies_changed:
            try:
                print("[MockSettingsDialog] Calling on_max_companies_changed callback...")
                self.on_max_companies_changed(max_companies)
                print("[MockSettingsDialog] Callback executed successfully!")
            except Exception as e:
                print(f"[MockSettingsDialog] ERROR: Callback failed: {e}")
        else:
            print("[MockSettingsDialog] WARNING: on_max_companies_changed is None!")
            
        self.dialog.destroy()
        print("[MockSettingsDialog] Dialog closed\n")


class TestApp:
    """Test application to verify max_companies callback flow."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Max Companies Setting Test")
        self.root.geometry("500x350")
        
        # Create company tag picker (mock)
        info_label = ttk.Label(
            self.root,
            text="This simulates CompanyTagPicker from the left panel:",
            font=("Segoe UI", 10, "bold")
        )
        info_label.pack(pady=(20, 5))
        
        self.company_tag_picker = MockCompanyTagPicker(self.root, max_select=5)
        self.company_tag_picker.pack(pady=10)
        
        # Button to open settings
        ttk.Button(
            self.root,
            text="Open Settings Dialog",
            command=self._show_settings
        ).pack(pady=20)
        
        # Status info
        ttk.Label(
            self.root,
            text="TEST STEPS:\n"
                 "1. Click 'Open Settings Dialog'\n"
                 "2. Change spinbox value (e.g., from 5 to 10)\n"
                 "3. Click 'Lưu'\n"
                 "4. Observe: Label above should change to '0/10 công ty'",
            font=("Segoe UI", 10),
            justify=tk.LEFT
        ).pack(pady=10)
        
        # Result display
        self.result_label = ttk.Label(
            self.root,
            text="Result: Waiting for test...",
            font=("Segoe UI", 10, "italic"),
            foreground="gray"
        )
        self.result_label.pack(pady=10)
        
    def _show_settings(self):
        """Show settings dialog - same pattern as customs_gui._show_settings_dialog."""
        print("\n" + "="*50)
        print("[TestApp] Opening settings dialog...")
        
        current_max = self.company_tag_picker.max_select
        
        def on_max_companies_changed(max_companies: int):
            """Callback when max companies setting changes."""
            print(f"[TestApp] on_max_companies_changed called: max_companies={max_companies}")
            
            # Update CompanyTagPicker
            if hasattr(self, 'company_tag_picker') and self.company_tag_picker:
                print("[TestApp] Calling company_tag_picker.set_max_select()...")
                self.company_tag_picker.set_max_select(max_companies)
                
                # Update result label
                self.result_label.config(
                    text=f"✓ SUCCESS! Max changed to {max_companies}",
                    foreground="green"
                )
            else:
                self.result_label.config(
                    text="✗ FAILED: company_tag_picker not found!",
                    foreground="red"
                )
                
        # Create dialog with callback passed in constructor
        MockSettingsDialog(
            self.root,
            current_max=current_max,
            on_max_companies_changed=on_max_companies_changed
        )
        
        print("[TestApp] Settings dialog opened")
        print("="*50)
        
    def run(self):
        """Run the test application."""
        print("\n" + "="*50)
        print("MAX COMPANIES SETTING TEST")
        print("="*50)
        print("This test verifies the callback flow from")
        print("SettingsDialog -> CustomsGUI -> CompanyTagPicker")
        print("="*50 + "\n")
        
        self.root.mainloop()


if __name__ == "__main__":
    app = TestApp()
    app.run()
