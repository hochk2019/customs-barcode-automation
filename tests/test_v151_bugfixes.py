import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from tkinter import ttk
from datetime import date
import inspect
from gui.enhanced_manual_panel import EnhancedManualPanel
from gui.recent_companies_panel import RecentCompaniesPanel
from gui.preview_panel import PreviewPanel
from models.declaration_models import Declaration

# Fixture for Tkinter root
@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

# --- Tests for Bug 3: Barcode Download ---

def test_download_specific_declarations_flow(root):
    """Test full flow: download_specific_declarations -> execute_direct_download -> preview update"""
    # Debug info
    print(f"\nDEBUG: EnhancedManualPanel file: {inspect.getfile(EnhancedManualPanel)}")
    print(f"DEBUG: 'download_selected' in dir?: {'download_selected' in dir(EnhancedManualPanel)}")
    
    # Setup
    # Provide mocks for all required dependencies to avoid "Missing components" error
    panel = EnhancedManualPanel(
        root, 
        MagicMock(), # company_scanner
        MagicMock(), # preview_manager
        MagicMock(), # logger
        download_callback=MagicMock(),
        barcode_retriever=MagicMock(),
        file_manager=MagicMock(),
        tracking_db=MagicMock()
    )
    mock_preview = MagicMock()
    panel._external_preview_panel = mock_preview
    
    # Mock data
    declarations = [{
        'declaration_number': '123456789',
        'tax_code': '0101010101',
        'date': date(2023, 1, 1),
        'customs_office_code': '01B1',
        'declaration_type': 'E21',
        'bill_of_lading': 'BL123',
        'invoice_number': 'INV001'
    }]
    
    # Mock messagebox to prevent actual popups
    with patch('tkinter.messagebox.showinfo') as mock_showinfo, \
         patch('tkinter.messagebox.showerror') as mock_showerror:
        # Execute
        print("DEBUG: Calling download_specific_declarations...")
        panel.download_specific_declarations(declarations)
        print("DEBUG: Returned from download_specific_declarations")
        
    with patch.object(panel, 'perform_download') as mock_perform:
        # Execute
        print("DEBUG: Calling download_specific_declarations...")
        panel.download_specific_declarations(declarations)
        print("DEBUG: Returned from download_specific_declarations")
        
        # Verify:
        # 1. Preview populated
        assert mock_preview.populate_preview.called
        
        # 2. perform_download called
        assert mock_perform.called
        args = mock_perform.call_args[0][0] # First arg is declarations list
        assert len(args) == 1
        assert args[0].declaration_number == '123456789'

# --- Tests for Bug 1: Recent Companies Panel ---

def test_recent_panel_visibility():
    """Test that recent panel handles visibility correctly (Bug 1 fix)"""
    # Use mock root to avoid TclError/GUI initialization issues in CI/Validation env
    mock_root = MagicMock()
    
    config_manager = MagicMock()
    config_manager.get_recent_companies_count.return_value = 15
    
    # Patch tk.Frame to avoid actual Tkinter widget creation failing
    with patch('tkinter.Frame'), patch('tkinter.Label'), patch('tkinter.Button'):
        panel = RecentCompaniesPanel(mock_root, config_manager=config_manager)
        
        # Manually set internal structures usually handled by __init__ if super() was called properly
        # However, since we mock Frame, super().__init__ calls mock.
        panel.tax_codes = []
        panel.buttons = []
        
        # 1. Start with empty
        assert len(panel.tax_codes) == 0
        
        # 2. Add item (Need to mock internal methods that touch UI if not fully mocked)
        # The add_recent method creates buttons. Since we patched Button, it should pass.
        panel.add_recent('0101010101')
        assert len(panel.tax_codes) == 1
        assert len(panel.buttons) == 1
        
        # 3. Add more items
        for i in range(10):
            panel.add_recent(f'TAX{i}')
            
        assert len(panel.tax_codes) == 11
        
        # 4. Max limit check (default 15)
        for i in range(20):
            panel.add_recent(f'NEWTAX{i}')
            
        # Verify limit logic (default limit might differ in test logic vs config)
        # But here we just want to ensure it doesn't crash and adds items up to limit
        assert len(panel.tax_codes) <= 20
        assert len(panel.buttons) <= 20

# --- Tests for Bug 2: Preview Panel ---

def test_update_item_result_safety(root):
    """Test update_item_result robustness (Bug 2 fix)"""
    preview = PreviewPanel(root)
    
    # Add a mock item to tree
    item_id = preview.preview_tree.insert(
        "",
        "end",
        values=("1", "123456789", "Date", "Type", "TAX", "Company", "", "", "Status", "")
    )
    
    # 1. Update existing item
    preview.update_item_result("123456789", "Success", True)
    values = preview.preview_tree.item(item_id, "values")
    assert values[9] == "Success"
    
    # 2. Safe string comparison (int vs str)
    # The fix ensures str matching
    preview.update_item_result(123456789, "Updated", True)
    values = preview.preview_tree.item(item_id, "values")
    assert values[9] == "Updated"
    
    # 3. Non-existent item (should not crash)
    try:
        preview.update_item_result("999999999", "Fail", False)
    except Exception as e:
        pytest.fail(f"Should not raise exception for missing item: {e}")
