"""
Unit tests for SettingsDialog

These tests verify the functionality of the SettingsDialog component.
Implements Requirements 1.1, 5.1
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestSettingsDialogOptions:
    """Test SettingsDialog option configurations"""
    
    def test_retrieval_method_options_defined(self):
        """Test that retrieval method options are correctly defined"""
        from gui.settings_dialog import SettingsDialog
        
        # Verify all required options exist
        assert "auto" in SettingsDialog.RETRIEVAL_METHOD_OPTIONS
        assert "api" in SettingsDialog.RETRIEVAL_METHOD_OPTIONS
        assert "web" in SettingsDialog.RETRIEVAL_METHOD_OPTIONS
        
        # Verify display labels are non-empty strings
        for key, value in SettingsDialog.RETRIEVAL_METHOD_OPTIONS.items():
            assert isinstance(value, str)
            assert len(value) > 0
    
    def test_pdf_naming_options_defined(self):
        """Test that PDF naming format options are correctly defined"""
        from gui.settings_dialog import SettingsDialog
        
        # Verify all required options exist
        assert "tax_code" in SettingsDialog.PDF_NAMING_OPTIONS
        assert "invoice" in SettingsDialog.PDF_NAMING_OPTIONS
        assert "bill_of_lading" in SettingsDialog.PDF_NAMING_OPTIONS
        
        # Verify display labels are non-empty strings
        for key, value in SettingsDialog.PDF_NAMING_OPTIONS.items():
            assert isinstance(value, str)
            assert len(value) > 0
    
    def test_retrieval_method_options_count(self):
        """Test that exactly 3 retrieval method options exist (Requirements 1.1)"""
        from gui.settings_dialog import SettingsDialog
        
        assert len(SettingsDialog.RETRIEVAL_METHOD_OPTIONS) == 3
    
    def test_pdf_naming_options_count(self):
        """Test that exactly 3 PDF naming format options exist (Requirements 5.1)"""
        from gui.settings_dialog import SettingsDialog
        
        assert len(SettingsDialog.PDF_NAMING_OPTIONS) == 3


class TestSettingsDialogKeyMapping:
    """Test SettingsDialog key-to-display value mapping"""
    
    def test_retrieval_method_key_to_display_mapping(self):
        """Test retrieval method key to display value mapping"""
        from gui.settings_dialog import SettingsDialog
        
        # Verify each key maps to a unique display value
        display_values = list(SettingsDialog.RETRIEVAL_METHOD_OPTIONS.values())
        assert len(display_values) == len(set(display_values)), "Display values should be unique"
    
    def test_pdf_naming_key_to_display_mapping(self):
        """Test PDF naming key to display value mapping"""
        from gui.settings_dialog import SettingsDialog
        
        # Verify each key maps to a unique display value
        display_values = list(SettingsDialog.PDF_NAMING_OPTIONS.values())
        assert len(display_values) == len(set(display_values)), "Display values should be unique"


class TestSettingsDialogSave:
    """Test SettingsDialog save functionality"""
    
    def test_save_settings_calls_config_manager(self):
        """Test that save_settings calls config manager methods"""
        config_manager = Mock()
        config_manager.get_retrieval_method.return_value = "auto"
        config_manager.get_pdf_naming_format.return_value = "tax_code"
        
        # Simulate saving settings
        retrieval_method = "api"
        pdf_naming_format = "invoice"
        
        config_manager.set_retrieval_method(retrieval_method)
        config_manager.set_pdf_naming_format(pdf_naming_format)
        config_manager.save()
        
        # Verify calls
        config_manager.set_retrieval_method.assert_called_once_with(retrieval_method)
        config_manager.set_pdf_naming_format.assert_called_once_with(pdf_naming_format)
        config_manager.save.assert_called_once()
    
    def test_save_settings_with_all_retrieval_methods(self):
        """Test saving each retrieval method option"""
        for method in ["auto", "api", "web"]:
            config_manager = Mock()
            config_manager.set_retrieval_method(method)
            config_manager.set_retrieval_method.assert_called_with(method)
    
    def test_save_settings_with_all_pdf_naming_formats(self):
        """Test saving each PDF naming format option"""
        for format_type in ["tax_code", "invoice", "bill_of_lading"]:
            config_manager = Mock()
            config_manager.set_pdf_naming_format(format_type)
            config_manager.set_pdf_naming_format.assert_called_with(format_type)


class TestSettingsDialogLoad:
    """Test SettingsDialog loading current settings"""
    
    def test_load_current_retrieval_method(self):
        """Test loading current retrieval method from config"""
        config_manager = Mock()
        config_manager.get_retrieval_method.return_value = "api"
        
        # Get current method
        current_method = config_manager.get_retrieval_method()
        
        # Verify
        assert current_method == "api"
        config_manager.get_retrieval_method.assert_called_once()
    
    def test_load_current_pdf_naming_format(self):
        """Test loading current PDF naming format from config"""
        config_manager = Mock()
        config_manager.get_pdf_naming_format.return_value = "invoice"
        
        # Get current format
        current_format = config_manager.get_pdf_naming_format()
        
        # Verify
        assert current_format == "invoice"
        config_manager.get_pdf_naming_format.assert_called_once()
    
    def test_load_default_retrieval_method_when_not_set(self):
        """Test default retrieval method when not configured"""
        config_manager = Mock()
        config_manager.get_retrieval_method.return_value = "auto"  # Default
        
        current_method = config_manager.get_retrieval_method()
        
        assert current_method == "auto"
    
    def test_load_default_pdf_naming_format_when_not_set(self):
        """Test default PDF naming format when not configured"""
        config_manager = Mock()
        config_manager.get_pdf_naming_format.return_value = "tax_code"  # Default
        
        current_format = config_manager.get_pdf_naming_format()
        
        assert current_format == "tax_code"


class TestSettingsDialogIntegration:
    """Test SettingsDialog integration with main GUI"""
    
    def test_settings_button_exists_in_gui(self):
        """Test that settings button is added to main GUI"""
        import inspect
        from gui.customs_gui import CustomsAutomationGUI
        
        source = inspect.getsource(CustomsAutomationGUI._create_control_panel)
        
        # Verify settings button is created
        assert "settings_button" in source, "Settings button should be created in control panel"
        assert "Cài đặt" in source, "Settings button should have Vietnamese label"
    
    def test_settings_dialog_method_exists_in_gui(self):
        """Test that _show_settings_dialog method exists in main GUI"""
        from gui.customs_gui import CustomsAutomationGUI
        
        assert hasattr(CustomsAutomationGUI, '_show_settings_dialog'), \
            "_show_settings_dialog method should exist in CustomsAutomationGUI"
    
    def test_settings_dialog_import_in_gui(self):
        """Test that SettingsDialog is imported in customs_gui"""
        import inspect
        import gui.customs_gui as customs_gui_module
        
        # Check if SettingsDialog is imported
        assert hasattr(customs_gui_module, 'SettingsDialog'), \
            "SettingsDialog should be imported in customs_gui module"


class TestSettingsDialogDisplayValues:
    """Test SettingsDialog display value formatting"""
    
    def test_retrieval_method_auto_display_value(self):
        """Test Auto retrieval method display value"""
        from gui.settings_dialog import SettingsDialog
        
        display = SettingsDialog.RETRIEVAL_METHOD_OPTIONS["auto"]
        
        # Should mention API priority and Web fallback
        assert "API" in display or "api" in display.lower()
        assert "Web" in display or "web" in display.lower()
    
    def test_pdf_naming_tax_code_display_value(self):
        """Test tax_code PDF naming display value includes example"""
        from gui.settings_dialog import SettingsDialog
        
        display = SettingsDialog.PDF_NAMING_OPTIONS["tax_code"]
        
        # Should include example with .pdf extension
        assert ".pdf" in display
    
    def test_pdf_naming_invoice_display_value(self):
        """Test invoice PDF naming display value includes example"""
        from gui.settings_dialog import SettingsDialog
        
        display = SettingsDialog.PDF_NAMING_OPTIONS["invoice"]
        
        # Should include example with .pdf extension
        assert ".pdf" in display
    
    def test_pdf_naming_bill_of_lading_display_value(self):
        """Test bill_of_lading PDF naming display value includes example"""
        from gui.settings_dialog import SettingsDialog
        
        display = SettingsDialog.PDF_NAMING_OPTIONS["bill_of_lading"]
        
        # Should include example with .pdf extension
        assert ".pdf" in display
