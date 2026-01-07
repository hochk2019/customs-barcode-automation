import unittest
from unittest.mock import MagicMock, patch
from gui.enhanced_manual_panel import EnhancedManualPanel
from models.declaration_models import Declaration
from datetime import datetime

import tkinter as tk

class TestKeyMismatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        # Mock dependencies
        self.barcode_retriever = MagicMock()
        self.file_manager = MagicMock()
        self.tracking_db = MagicMock()
        
        self.panel = EnhancedManualPanel(
            self.root, 
            self.barcode_retriever,
            self.file_manager,
            self.tracking_db
        )
        # Mock retrieve_barcode to return success
        self.barcode_retriever.retrieve_barcode.return_value = MagicMock(success=True, content=b'pdf')

    def test_execute_direct_download_with_declaration_date_key(self):
        """Test with 'declaration_date' key (from customs_gui.py)"""
        data = [{
            'declaration_number': '100',
            'tax_code': 'TAX001',
            'declaration_date': '2023-01-01', # Using the key that caused error
            'customs_office_code': 'HQ01'
        }]
        
        # Should not raise KeyError
        try:
            self.panel.execute_direct_download(data)
        except KeyError as e:
            self.fail(f"KeyError raised: {e}")
            
        # Verify perform_download was called with correct object
        # Note: execute_direct_download calls perform_download(declarations)
        # But perform_download runs in a thread. 
        # We need to wait or mock perform_download?
        # execute_direct_download calls it directly?
        # Line 3239: self.perform_download(declarations)
        # So we can mock perform_download on the instance.
        
    @patch('gui.enhanced_manual_panel.EnhancedManualPanel.perform_download')
    def test_perform_download_called_correctly(self, mock_perform):
        data = [{
            'declaration_number': '100',
            'tax_code': 'TAX001',
            'declaration_date': '2023-01-01',
            'customs_office_code': 'HQ01'
        }]
        
        self.panel.execute_direct_download(data)
        
        mock_perform.assert_called_once()
        args = mock_perform.call_args[0][0] # First arg check
        self.assertEqual(len(args), 1)
        self.assertIsInstance(args[0], Declaration)
        self.assertEqual(args[0].declaration_number, '100')
        self.assertEqual(args[0].customs_office_code, 'HQ01')
        # Date should be datetime due to __post_init__
        self.assertIsInstance(args[0].declaration_date, datetime)

    @patch('gui.enhanced_manual_panel.EnhancedManualPanel.perform_download')
    def test_perform_download_with_legacy_date_key(self, mock_perform):
        """Test with 'date' key (legacy/test behavior)"""
        data = [{
            'declaration_number': '100',
            'tax_code': 'TAX001',
            'date': '2023-01-01',
            'customs_office_code': 'HQ01'
        }]
        
        self.panel.execute_direct_download(data)
        
        mock_perform.assert_called_once()
        args = mock_perform.call_args[0][0]
        self.assertIsInstance(args[0], Declaration)
        self.assertIsInstance(args[0].declaration_date, datetime)

if __name__ == '__main__':
    unittest.main()
