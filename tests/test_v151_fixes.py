from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
from models.declaration_models import Declaration
from gui.enhanced_manual_panel import EnhancedManualPanel
from gui.recent_companies_panel import RecentCompaniesPanel

class TestV151Fixes(unittest.TestCase):
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw() # Hide window
        
    def tearDown(self):
        self.root.destroy()

    def test_declaration_date_parsing_iso_T(self):
        """Test parsing 'YYYY-MM-DDTHH:MM:SS'"""
        decl = Declaration(
            declaration_number="123", tax_code="010",
            declaration_date="2023-01-01T12:00:00",
            customs_office_code="01", transport_method="sea", 
            channel="Green", status="P", goods_description="Test"
        )
        self.assertIsInstance(decl.declaration_date, datetime)
        self.assertEqual(decl.declaration_date.year, 2023)

    def test_declaration_date_parsing_iso_simple(self):
        """Test parsing 'YYYY-MM-DD'"""
        decl = Declaration(
            declaration_number="123", tax_code="010",
            declaration_date="2023-01-01",
            customs_office_code="01", transport_method="sea", 
            channel="Green", status="P", goods_description="Test"
        )
        self.assertIsInstance(decl.declaration_date, datetime)
        self.assertEqual(decl.declaration_date.month, 1)

    def test_declaration_date_parsing_slash(self):
        """Test parsing 'DD/MM/YYYY'"""
        decl = Declaration(
            declaration_number="123", tax_code="010",
            declaration_date="31/12/2023",
            customs_office_code="01", transport_method="sea", 
            channel="Green", status="P", goods_description="Test"
        )
        self.assertIsInstance(decl.declaration_date, datetime)
        self.assertEqual(decl.declaration_date.day, 31)

    def test_perform_download_exists(self):
        """Test that EnhancedManualPanel now has perform_download method"""
        self.assertTrue(hasattr(EnhancedManualPanel, 'perform_download'), 
                       "EnhancedManualPanel is missing 'perform_download' method")

    def test_download_selected_removed(self):
        """Test that problematic download_selected is NOT called by execute_direct_download anymore (indirect check)"""
        # We check if execute_direct_download calls perform_download
        panel = EnhancedManualPanel(self.root, MagicMock(), MagicMock(), MagicMock(), barcode_retriever=MagicMock(), file_manager=MagicMock())
        
        with patch.object(panel, 'perform_download') as mock_perform:
             panel.execute_direct_download([{'declaration_number':'1','tax_code':'1','date':datetime.now()}])
             mock_perform.assert_called_once()

    def test_recent_companies_layout_stability(self):
        """Test that pack_forget is NOT used in RecentCompaniesPanel when list is empty (checking source code approach preferred, but runtime check: methods shouldn't raise error)"""
        panel = RecentCompaniesPanel(self.root)
        panel.update_recent([])
        # If we replaced pack_forget with just pack(), it should still be mapped or at least not raise errors.
        # Ideally check if it's mapped.
        self.assertTrue(panel.winfo_exists())
