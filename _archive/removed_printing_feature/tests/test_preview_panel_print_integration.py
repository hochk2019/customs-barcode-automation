"""
Integration test for Preview Panel declaration printing functionality.

Tests the complete integration between Preview Panel UI and Declaration Printer.
"""

import importlib.util
import sys

if "pytest" in sys.modules and importlib.util.find_spec("declaration_printing") is None:
    import pytest
    pytest.skip("declaration_printing package not installed", allow_module_level=True)

import tkinter as tk
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from gui.preview_panel import PreviewPanel
from gui.preview_panel_integration import PreviewPanelIntegration
from declaration_printing.models import BatchPrintResult, PrintResult, BatchProcessingStatus


class TestPreviewPanelPrintIntegration:
    """Integration tests for Preview Panel declaration printing."""
    
    def setup_method(self):
        """Set up test environment."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during testing
        
        # Create preview panel
        self.preview_panel = PreviewPanel(self.root)
        
        # Mock dependencies
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_output_path.return_value = "test_output"
        
        self.mock_logger = Mock()
        
        # Create integration with mocked dependencies
        with patch('gui.preview_panel_integration.DeclarationPrinter') as mock_printer_class:
            self.mock_printer = Mock()
            mock_printer_class.return_value = self.mock_printer
            
            self.integration = PreviewPanelIntegration(
                preview_panel=self.preview_panel,
                config_manager=self.mock_config_manager,
                logger=self.mock_logger,
                output_directory="test_output"
            )
    
    def teardown_method(self):
        """Clean up after test."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_print_button_added_to_preview_panel(self):
        """Test that the print button is properly added to the preview panel."""
        # Check that print button exists
        assert hasattr(self.preview_panel, 'print_btn'), "Print button should be added to preview panel"
        
        # Check button properties
        assert self.preview_panel.print_btn.cget('text') == "📄 In TKTQ", "Print button should have correct text"
        assert self.preview_panel.print_btn.cget('state') == 'disabled', "Print button should start disabled"
    
    def test_print_button_state_management_with_cleared_declarations(self):
        """Test print button state management with cleared declarations."""
        # Add test declarations
        declarations = [
            {
                'declaration_number': '305254403660',
                'tax_code': 'TAX001',
                'date': '01/01/2024',
                'status': 'T',  # Cleared
                'declaration_type': 'XK',
                'bill_of_lading': 'BL001',
                'invoice_number': 'INV001',
                'result': ''
            },
            {
                'declaration_number': '107772836360',
                'tax_code': 'TAX002',
                'date': '02/01/2024',
                'status': 'P',  # Pending
                'declaration_type': 'NK',
                'bill_of_lading': 'BL002',
                'invoice_number': 'INV002',
                'result': ''
            }
        ]
        
        self.preview_panel.populate_preview(declarations)
        
        # Test: No selection - button should be disabled
        self.preview_panel._selected_items = []
        self.preview_panel._update_print_button_state()
        assert self.preview_panel.print_btn.cget('state') == 'disabled'
        
        # Test: Select cleared declaration - button should be enabled
        cleared_item = list(self.preview_panel.preview_tree.get_children())[0]
        self.preview_panel._selected_items = [cleared_item]
        self.preview_panel._update_print_button_state()
        assert self.preview_panel.print_btn.cget('state') == 'normal'
        
        # Test: Select non-cleared declaration - button should be disabled
        pending_item = list(self.preview_panel.preview_tree.get_children())[1]
        self.preview_panel._selected_items = [pending_item]
        self.preview_panel._update_print_button_state()
        assert self.preview_panel.print_btn.cget('state') == 'disabled'
        
        # Test: Select mix of cleared and non-cleared - button should be disabled
        self.preview_panel._selected_items = [cleared_item, pending_item]
        self.preview_panel._update_print_button_state()
        assert self.preview_panel.print_btn.cget('state') == 'disabled'
    
    @patch('gui.preview_panel_integration.messagebox')
    def test_print_declarations_validation(self, mock_messagebox):
        """Test validation when printing declarations."""
        # Test: No declarations selected
        self.integration.handle_print_declarations([])
        mock_messagebox.showwarning.assert_called_with(
            "Chưa chọn tờ khai",
            "Vui lòng chọn ít nhất một tờ khai để in."
        )
        
        # Test: Non-cleared declarations selected
        declarations = [
            {
                'declaration_number': '107772836360',
                'tax_code': 'TAX002',
                'date': '02/01/2024',
                'status': 'P',  # Pending
                'declaration_type': 'NK',
                'bill_of_lading': 'BL002',
                'invoice_number': 'INV002',
                'result': ''
            }
        ]
        self.preview_panel.populate_preview(declarations)
        
        mock_messagebox.reset_mock()
        self.integration.handle_print_declarations(['107772836360'])
        mock_messagebox.showwarning.assert_called()
        args = mock_messagebox.showwarning.call_args[0]
        assert "Tờ khai chưa thông quan" in args[0]
    
    @patch('gui.preview_panel_integration.messagebox')
    @patch('gui.preview_panel_integration.threading.Thread')
    def test_successful_print_operation(self, mock_thread, mock_messagebox):
        """Test successful print operation flow."""
        # Setup cleared declarations
        declarations = [
            {
                'declaration_number': '305254403660',
                'tax_code': 'TAX001',
                'date': '01/01/2024',
                'status': 'T',  # Cleared
                'declaration_type': 'XK',
                'bill_of_lading': 'BL001',
                'invoice_number': 'INV001',
                'result': ''
            }
        ]
        self.preview_panel.populate_preview(declarations)
        
        # Mock user confirmation
        mock_messagebox.askyesno.return_value = True
        
        # Mock successful print result
        mock_result = BatchPrintResult(
            total_processed=1,
            successful=1,
            failed=0,
            results=[PrintResult(
                success=True,
                declaration_number='305254403660',
                output_file_path='test_output/ToKhaiHQ7X_QDTQ_305254403660.xlsx',
                processing_time=2.5
            )],
            total_time=2.5,
            summary_report="Success",
            cancelled=False
        )
        
        # Start print operation
        self.integration.handle_print_declarations(['305254403660'])
        
        # Verify confirmation dialog was shown
        mock_messagebox.askyesno.assert_called()
        
        # Verify thread was started
        mock_thread.assert_called_once()
        
        # Verify printing state was set
        assert self.integration._is_printing == True
    
    def test_progress_indication_during_printing(self):
        """Test progress indication during printing operations."""
        # Create batch processing status
        status = BatchProcessingStatus(
            current_index=2,
            total_count=5,
            current_declaration="305254403660",
            successful_count=1,
            failed_count=1,
            elapsed_time=5.0,
            estimated_remaining_time=7.5,
            is_cancelled=False
        )
        
        # Update progress
        self.integration._update_print_progress_ui(status)
        
        # Verify progress bar was updated
        expected_progress = (2 / 5) * 100  # 40%
        actual_progress = self.preview_panel.progress_var.get()
        assert abs(actual_progress - expected_progress) < 0.1
        
        # Verify progress label was updated
        progress_text = self.preview_panel.progress_label.cget('text')
        assert "3/5" in progress_text  # current_index + 1 for display
        
        # Verify status was updated
        status_text = self.preview_panel.status_label.cget('text')
        assert "Đang in tờ khai" in status_text
        assert "305254403660" in status_text
    
    def test_print_operation_completion(self):
        """Test print operation completion handling."""
        # Mock successful result
        result = BatchPrintResult(
            total_processed=2,
            successful=2,
            failed=0,
            results=[
                PrintResult(
                    success=True,
                    declaration_number='305254403660',
                    output_file_path='test_output/ToKhaiHQ7X_QDTQ_305254403660.xlsx',
                    processing_time=2.5
                ),
                PrintResult(
                    success=True,
                    declaration_number='107772836360',
                    output_file_path='test_output/ToKhaiHQ7N_QDTQ_107772836360.xlsx',
                    processing_time=3.0
                )
            ],
            total_time=5.5,
            summary_report="All successful",
            cancelled=False
        )
        
        # Setup preview with declarations
        declarations = [
            {
                'declaration_number': '305254403660',
                'tax_code': 'TAX001',
                'date': '01/01/2024',
                'status': 'T',
                'declaration_type': 'XK',
                'bill_of_lading': 'BL001',
                'invoice_number': 'INV001',
                'result': ''
            },
            {
                'declaration_number': '107772836360',
                'tax_code': 'TAX002',
                'date': '02/01/2024',
                'status': 'T',
                'declaration_type': 'NK',
                'bill_of_lading': 'BL002',
                'invoice_number': 'INV002',
                'result': ''
            }
        ]
        self.preview_panel.populate_preview(declarations)
        
        # Set printing state
        self.integration._is_printing = True
        self.preview_panel.set_printing_state(True)
        
        # Complete operation
        with patch('gui.preview_panel_integration.messagebox') as mock_messagebox:
            self.integration._on_print_completed(result)
        
        # Verify state was reset
        assert self.integration._is_printing == False
        
        # Verify success message was shown
        mock_messagebox.showinfo.assert_called()
        args = mock_messagebox.showinfo.call_args[0]
        assert "Hoàn thành in" in args[0]
        assert "2 tờ khai" in args[1]
    
    def test_cancel_printing_operation(self):
        """Test cancelling print operation."""
        # Set printing state
        self.integration._is_printing = True
        
        # Cancel operation
        self.integration.cancel_printing()
        
        # Verify cancellation was requested
        self.mock_printer.cancel_batch_processing.assert_called_once()
    
    def test_tooltip_generation(self):
        """Test print button tooltip generation."""
        # Setup declarations
        declarations = [
            {
                'declaration_number': '305254403660',
                'tax_code': 'TAX001',
                'date': '01/01/2024',
                'status': 'T',  # Cleared
                'declaration_type': 'XK',
                'bill_of_lading': 'BL001',
                'invoice_number': 'INV001',
                'result': ''
            },
            {
                'declaration_number': '107772836360',
                'tax_code': 'TAX002',
                'date': '02/01/2024',
                'status': 'P',  # Pending
                'declaration_type': 'NK',
                'bill_of_lading': 'BL002',
                'invoice_number': 'INV002',
                'result': ''
            }
        ]
        self.preview_panel.populate_preview(declarations)
        
        # Test: No selection
        tooltip = self.integration.get_print_button_tooltip([])
        assert "Chọn tờ khai đã thông quan để in" in tooltip
        
        # Test: Only cleared declarations
        tooltip = self.integration.get_print_button_tooltip(['305254403660'])
        assert "In 1 tờ khai thông quan" in tooltip
        
        # Test: Mix of cleared and non-cleared
        tooltip = self.integration.get_print_button_tooltip(['305254403660', '107772836360'])
        assert "chưa thông quan" in tooltip
        assert "TTTK = T" in tooltip


if __name__ == "__main__":
    pytest.main([__file__])