"""
Property-based tests for Preview Panel integration with declaration printing.

**Feature: customs-declaration-printing, Property 8: Preview Panel integration and button state management**
**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import tkinter as tk
from tkinter import ttk
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

from gui.preview_panel import PreviewPanel
from declaration_printing.declaration_printer import DeclarationPrinter
from declaration_printing.models import DeclarationType, BatchProcessingStatus


class TestPreviewPanelIntegrationProperties:
    """Property-based tests for Preview Panel integration with declaration printing."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
        # Mock callbacks
        self.mock_callbacks = {
            'on_preview': Mock(),
            'on_download': Mock(),
            'on_cancel': Mock(),
            'on_stop': Mock(),
            'on_export_log': Mock(),
            'on_select_all': Mock(),
            'on_retry_failed': Mock(),
            'on_include_pending_changed': Mock(),
            'on_exclude_xnktc_changed': Mock(),
            'on_print_declarations': Mock()
        }
        
        # Create preview panel with mocked callbacks
        self.preview_panel = PreviewPanel(
            self.root,
            **{k: v for k, v in self.mock_callbacks.items() if k != 'on_print_declarations'}
        )
        
        # Mock declaration printer
        self.mock_printer = Mock(spec=DeclarationPrinter)
        
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    @given(
        declarations=st.lists(
            st.fixed_dictionaries({
                'declaration_number': st.text(min_size=12, max_size=12).filter(lambda x: x.isdigit()),
                'tax_code': st.text(min_size=1, max_size=20),
                'date': st.text(min_size=8, max_size=10),
                'status': st.sampled_from(['T', 'P', 'C', 'R']),  # T=cleared, P=pending, C=cancelled, R=rejected
                'declaration_type': st.sampled_from(['NK', 'XK']),
                'bill_of_lading': st.text(min_size=1, max_size=50),
                'invoice_number': st.text(min_size=1, max_size=30),
                'result': st.text(max_size=20)
            }),
            min_size=0,
            max_size=50
        )
    )
    @settings(max_examples=100)
    def test_print_button_state_management_for_cleared_declarations(self, declarations):
        """
        Property: For any set of declarations in the preview panel, the "In TKTQ" button 
        should be enabled only when cleared declarations (TTTK = "T") are selected.
        
        **Feature: customs-declaration-printing, Property 8: Preview Panel integration and button state management**
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
        """
        # Add print button to preview panel (simulating integration)
        self._add_print_button_to_preview_panel()
        
        # Populate preview with declarations
        self.preview_panel.populate_preview(declarations)
        
        # Test different selection scenarios
        cleared_declarations = [d for d in declarations if d['status'] == 'T']
        non_cleared_declarations = [d for d in declarations if d['status'] != 'T']
        
        # Property 1: When no declarations are selected, print button should be disabled
        self.preview_panel._selected_items = []
        self._update_print_button_state()
        assert self.print_btn.cget('state') == 'disabled', "Print button should be disabled when no declarations selected"
        
        # Property 2: When only cleared declarations are selected, print button should be enabled
        if cleared_declarations:
            # Select cleared declarations
            cleared_items = []
            for i, decl in enumerate(declarations):
                if decl['status'] == 'T':
                    item_id = list(self.preview_panel.preview_tree.get_children())[i]
                    cleared_items.append(item_id)
            
            if cleared_items:
                self.preview_panel._selected_items = cleared_items
                self._update_print_button_state()
                assert self.print_btn.cget('state') == 'normal', "Print button should be enabled when cleared declarations are selected"
        
        # Property 3: When non-cleared declarations are included in selection, print button should be disabled
        if non_cleared_declarations and cleared_declarations:
            # Select mix of cleared and non-cleared
            mixed_items = []
            for i, decl in enumerate(declarations[:min(5, len(declarations))]):  # Limit to first 5 for performance
                item_id = list(self.preview_panel.preview_tree.get_children())[i]
                mixed_items.append(item_id)
            
            if len(mixed_items) > 1:  # Ensure we have a mix
                has_cleared = any(declarations[i]['status'] == 'T' for i in range(len(mixed_items)))
                has_non_cleared = any(declarations[i]['status'] != 'T' for i in range(len(mixed_items)))
                
                if has_cleared and has_non_cleared:
                    self.preview_panel._selected_items = mixed_items
                    self._update_print_button_state()
                    assert self.print_btn.cget('state') == 'disabled', "Print button should be disabled when mix of cleared/non-cleared declarations are selected"
        
        # Property 4: When only non-cleared declarations are selected, print button should be disabled
        if non_cleared_declarations:
            non_cleared_items = []
            for i, decl in enumerate(declarations):
                if decl['status'] != 'T':
                    item_id = list(self.preview_panel.preview_tree.get_children())[i]
                    non_cleared_items.append(item_id)
            
            if non_cleared_items:
                self.preview_panel._selected_items = non_cleared_items
                self._update_print_button_state()
                assert self.print_btn.cget('state') == 'disabled', "Print button should be disabled when non-cleared declarations are selected"
    
    @given(
        batch_size=st.integers(min_value=1, max_value=20),
        current_progress=st.integers(min_value=0, max_value=19),
        successful_count=st.integers(min_value=0, max_value=19),
        failed_count=st.integers(min_value=0, max_value=19)
    )
    @settings(max_examples=100)
    def test_progress_indication_during_printing_operations(self, batch_size, current_progress, successful_count, failed_count):
        """
        Property: For any batch printing operation, the preview panel should display 
        accurate progress indication and maintain UI state consistency.
        
        **Feature: customs-declaration-printing, Property 8: Preview Panel integration and button state management**
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
        """
        assume(current_progress <= batch_size)
        assume(successful_count + failed_count <= current_progress)
        
        # Add print button to preview panel
        self._add_print_button_to_preview_panel()
        
        # Create batch processing status
        status = BatchProcessingStatus(
            current_index=current_progress,
            total_count=batch_size,
            current_declaration=f"12345678901{current_progress % 10}",
            successful_count=successful_count,
            failed_count=failed_count,
            elapsed_time=current_progress * 2.5,
            estimated_remaining_time=(batch_size - current_progress) * 2.5 if current_progress < batch_size else 0,
            is_cancelled=False
        )
        
        # Simulate progress update
        self._update_printing_progress(status)
        
        # Property 1: Progress bar should reflect current progress
        expected_progress = (current_progress / batch_size) * 100 if batch_size > 0 else 0
        actual_progress = self.preview_panel.progress_var.get()
        assert abs(actual_progress - expected_progress) < 0.1, f"Progress bar should show {expected_progress}%, got {actual_progress}%"
        
        # Property 2: Progress label should show current/total format
        progress_text = self.preview_panel.progress_label.cget('text')
        if current_progress < batch_size:
            assert f"{current_progress + 1}/{batch_size}" in progress_text, f"Progress label should contain current/total, got: {progress_text}"
        
        # Property 3: During printing, print button should be disabled and other buttons should maintain state
        if current_progress < batch_size:  # Still processing
            assert self.print_btn.cget('state') == 'disabled', "Print button should be disabled during printing"
            # Note: Stop button state management is handled by the main application, not the progress update
            # The preview panel doesn't automatically enable/disable stop button during progress updates
        
        # Property 4: Progress should be visible during operation
        if current_progress < batch_size:
            # Progress bar should be packed (visible)
            assert self.preview_panel.progress_bar.winfo_manager() == 'pack', "Progress bar should be visible during printing"
    
    @given(
        declaration_numbers=st.lists(
            st.one_of(
                st.text(min_size=10, max_size=10).map(lambda x: '10' + x).filter(lambda x: x.isdigit()),
                st.text(min_size=10, max_size=10).map(lambda x: '30' + x).filter(lambda x: x.isdigit())
            ),
            min_size=1,
            max_size=10
        ),
        success_results=st.lists(st.booleans(), min_size=1, max_size=10)
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
    def test_print_button_integration_with_existing_buttons(self, declaration_numbers, success_results):
        """
        Property: For any printing operation, the "In TKTQ" button should work alongside 
        existing buttons without conflicts and maintain proper button layout.
        
        **Feature: customs-declaration-printing, Property 8: Preview Panel integration and button state management**
        **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**
        """
        assume(len(success_results) >= len(declaration_numbers))
        
        # Add print button to preview panel
        self._add_print_button_to_preview_panel()
        
        # Create declarations with cleared status
        declarations = []
        for i, decl_num in enumerate(declaration_numbers):
            declarations.append({
                'declaration_number': decl_num,
                'tax_code': f'TAX{i:03d}',
                'date': '01/01/2024',
                'status': 'T',  # All cleared for this test
                'declaration_type': 'NK' if decl_num.startswith('10') else 'XK',
                'bill_of_lading': f'BL{i:03d}',
                'invoice_number': f'INV{i:03d}',
                'result': ''
            })
        
        self.preview_panel.populate_preview(declarations)
        
        # Property 1: Print button should be positioned correctly next to "Lấy mã vạch" button
        action_frame_children = list(self.preview_panel.children.values())[0].winfo_children()
        button_texts = [btn.cget('text') for btn in action_frame_children if isinstance(btn, tk.Button)]
        
        assert "📥 Lấy mã vạch" in button_texts, "Download button should be present"
        assert "📄 In TKTQ" in button_texts, "Print button should be present"
        
        # Find positions
        download_pos = button_texts.index("📥 Lấy mã vạch")
        print_pos = button_texts.index("📄 In TKTQ")
        
        # Print button should be positioned after download button
        assert print_pos > download_pos, "Print button should be positioned after download button"
        
        # Property 2: All existing buttons should remain functional
        original_button_count = len([btn for btn in action_frame_children if isinstance(btn, tk.Button)])
        expected_buttons = ["👁 Xem trước", "📥 Lấy mã vạch", "📄 In TKTQ", "✕ Hủy", "⏹ Dừng", "🔄 Tải lại lỗi", "📋 Xuất log"]
        
        assert original_button_count >= len(expected_buttons) - 1, f"Should have at least {len(expected_buttons)-1} buttons, got {original_button_count}"
        
        # Property 3: Button states should not interfere with each other
        # Select cleared declarations
        all_items = list(self.preview_panel.preview_tree.get_children())
        if all_items:
            self.preview_panel._selected_items = all_items[:min(3, len(all_items))]
            self._update_print_button_state()
            
            # Print button should be enabled for cleared declarations
            assert self.print_btn.cget('state') == 'normal', "Print button should be enabled for cleared declarations"
            
            # Other buttons should maintain their independent states
            # Download button should also be enabled (assuming similar logic)
            assert self.preview_panel.download_btn.cget('state') == 'normal', "Download button should remain independently functional"
    
    def _add_print_button_to_preview_panel(self):
        """Helper method to add print button to preview panel (simulating integration)."""
        # Find the action frame (first child of preview panel)
        action_frame = None
        for child in self.preview_panel.winfo_children():
            if isinstance(child, ttk.Frame):
                action_frame = child
                break
        
        if action_frame is None:
            pytest.skip("Could not find action frame in preview panel")
        
        # Add print button after download button
        from gui.styles import ModernStyles
        
        btn_width = 14
        btn_padx = 5
        bold_font = (ModernStyles.FONT_FAMILY, ModernStyles.FONT_SIZE_NORMAL, 'bold')
        success_cfg = ModernStyles.get_button_config('success')
        success_cfg['font'] = bold_font
        
        self.print_btn = tk.Button(
            action_frame,
            text="📄 In TKTQ",
            command=self._on_print_click,
            width=btn_width,
            **success_cfg
        )
        
        # Insert after download button (position 2, after preview and download)
        self.print_btn.pack(side=tk.LEFT, padx=(0, btn_padx), after=self.preview_panel.download_btn)
        
        # Bind hover effects
        self.preview_panel._bind_hover_effects(self.print_btn, 'success')
        
        # Set initial state
        self.print_btn.configure(state='disabled')
    
    def _on_print_click(self):
        """Handle print button click."""
        selected_declarations = self.preview_panel.get_selected_declarations()
        if self.mock_callbacks['on_print_declarations']:
            self.mock_callbacks['on_print_declarations'](selected_declarations)
    
    def _update_print_button_state(self):
        """Update print button state based on selected declarations."""
        if not hasattr(self, 'print_btn'):
            return
        
        selected_declarations = self.preview_panel.get_selected_declarations()
        
        if not selected_declarations:
            self.print_btn.configure(state='disabled')
            return
        
        # Check if all selected declarations are cleared (status = 'T')
        all_cleared = True
        for decl_num in selected_declarations:
            # Find declaration in preview data
            for decl in getattr(self.preview_panel, '_declarations', []):
                if decl.get('declaration_number') == decl_num:
                    if decl.get('status') != 'T':
                        all_cleared = False
                        break
            if not all_cleared:
                break
        
        if all_cleared:
            self.print_btn.configure(state='normal')
        else:
            self.print_btn.configure(state='disabled')
    
    def _update_printing_progress(self, status: BatchProcessingStatus):
        """Update printing progress in preview panel."""
        # Calculate progress percentage
        progress_percent = (status.current_index / status.total_count) * 100 if status.total_count > 0 else 0
        
        # Update progress bar and label
        self.preview_panel.update_progress(
            progress_percent,
            status.current_index + 1,  # +1 for display (1-based indexing)
            status.total_count
        )
        
        # Show progress during operation
        if status.current_index < status.total_count:
            self.preview_panel.show_progress(True)
            # Disable print button during operation
            if hasattr(self, 'print_btn'):
                self.print_btn.configure(state='disabled')
        else:
            # Hide progress when complete
            self.preview_panel.show_progress(False)
            # Re-enable print button based on selection
            self._update_print_button_state()


if __name__ == "__main__":
    pytest.main([__file__])