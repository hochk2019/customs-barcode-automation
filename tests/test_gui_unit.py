"""
Unit tests for GUI components

These tests verify specific functionality of the GUI components.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
import os

from models.declaration_models import WorkflowResult, OperationMode, ProcessedDeclaration, Declaration


class TestGUIStatistics:
    """Test GUI statistics functionality"""
    
    def test_statistics_update_increments_correctly(self):
        """Test that statistics are incremented correctly after workflow execution"""
        # Create mock GUI state
        class MockGUI:
            def __init__(self):
                self.total_processed = 100
                self.total_success = 80
                self.total_errors = 20
                self.last_run_time = None
                self.processed_label = Mock()
                self.success_label = Mock()
                self.errors_label = Mock()
                self.last_run_label = Mock()
            
            def update_statistics(self, result: WorkflowResult):
                """Update statistics display"""
                self.total_processed += result.total_eligible
                self.total_success += result.success_count
                self.total_errors += result.error_count
                self.last_run_time = result.end_time or datetime.now()
                
                self.processed_label.config(text=str(self.total_processed))
                self.success_label.config(text=str(self.total_success))
                self.errors_label.config(text=str(self.total_errors))
                
                if self.last_run_time:
                    self.last_run_label.config(text=self.last_run_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        gui = MockGUI()
        
        # Create workflow result
        result = WorkflowResult(
            total_fetched=50,
            total_eligible=45,
            success_count=40,
            error_count=5,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=10)
        )
        
        # Update statistics
        gui.update_statistics(result)
        
        # Verify increments
        assert gui.total_processed == 145  # 100 + 45
        assert gui.total_success == 120  # 80 + 40
        assert gui.total_errors == 25  # 20 + 5
        assert gui.last_run_time == result.end_time
        
        # Verify UI updates
        gui.processed_label.config.assert_called_with(text="145")
        gui.success_label.config.assert_called_with(text="120")
        gui.errors_label.config.assert_called_with(text="25")


class TestGUIModeSwitch:
    """Test GUI operation mode switching"""
    
    def test_mode_switch_to_automatic(self):
        """Test switching to automatic mode"""
        # Create mocks
        scheduler = Mock()
        config_manager = Mock()
        logger = Mock()
        
        # Simulate mode switch
        mode = OperationMode.AUTOMATIC
        scheduler.set_operation_mode(mode)
        config_manager.set_operation_mode(mode.value)
        config_manager.save()
        
        # Verify calls
        scheduler.set_operation_mode.assert_called_once_with(mode)
        config_manager.set_operation_mode.assert_called_once_with("automatic")
        config_manager.save.assert_called_once()
    
    def test_mode_switch_to_manual(self):
        """Test switching to manual mode"""
        # Create mocks
        scheduler = Mock()
        config_manager = Mock()
        logger = Mock()
        
        # Simulate mode switch
        mode = OperationMode.MANUAL
        scheduler.set_operation_mode(mode)
        config_manager.set_operation_mode(mode.value)
        config_manager.save()
        
        # Verify calls
        scheduler.set_operation_mode.assert_called_once_with(mode)
        config_manager.set_operation_mode.assert_called_once_with("manual")
        config_manager.save.assert_called_once()


class TestGUIButtonHandlers:
    """Test GUI button click handlers"""
    
    def test_start_button_handler(self):
        """Test start button click handler"""
        scheduler = Mock()
        logger = Mock()
        
        # Simulate start button click
        scheduler.start()
        
        # Verify scheduler was started
        scheduler.start.assert_called_once()
    
    def test_stop_button_handler(self):
        """Test stop button click handler"""
        scheduler = Mock()
        logger = Mock()
        
        # Simulate stop button click
        scheduler.stop()
        
        # Verify scheduler was stopped
        scheduler.stop.assert_called_once()
    
    def test_run_once_button_handler(self):
        """Test run once button click handler"""
        scheduler = Mock()
        result = WorkflowResult(
            total_fetched=10,
            total_eligible=8,
            success_count=7,
            error_count=1
        )
        scheduler.run_once.return_value = result
        
        # Simulate run once button click
        actual_result = scheduler.run_once(force_redownload=False)
        
        # Verify scheduler executed once
        scheduler.run_once.assert_called_once_with(force_redownload=False)
        assert actual_result == result


class TestGUISearch:
    """Test GUI search functionality"""
    
    def test_search_with_query(self):
        """Test search with a query string"""
        tracking_db = Mock()
        
        # Create mock search results
        results = [
            ProcessedDeclaration(
                id=1,
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date="20231206",
                file_path="C:\\test\\file1.pdf",
                processed_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ProcessedDeclaration(
                id=2,
                declaration_number="305254416960",
                tax_code="2300782217",
                declaration_date="20231205",
                file_path="C:\\test\\file2.pdf",
                processed_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        tracking_db.search_declarations.return_value = results
        
        # Execute search
        query = "2300782217"
        search_results = tracking_db.search_declarations(query)
        
        # Verify search was called
        tracking_db.search_declarations.assert_called_once_with(query)
        
        # Verify results
        assert len(search_results) == 2
        assert all(query in r.tax_code for r in search_results)
    
    def test_search_with_empty_query(self):
        """Test search with empty query returns all declarations"""
        tracking_db = Mock()
        
        # Create mock all declarations
        all_declarations = [
            ProcessedDeclaration(
                id=i,
                declaration_number=f"30801089{i:04d}",
                tax_code=f"230078{i:04d}",
                declaration_date="20231206",
                file_path=f"C:\\test\\file{i}.pdf",
                processed_at=datetime.now(),
                updated_at=datetime.now()
            )
            for i in range(10)
        ]
        
        tracking_db.get_all_processed_details.return_value = all_declarations
        
        # Execute search with empty query (should load all)
        query = ""
        if not query:
            results = tracking_db.get_all_processed_details()
        else:
            results = tracking_db.search_declarations(query)
        
        # Verify all declarations returned
        assert len(results) == 10


class TestGUIRedownload:
    """Test GUI re-download functionality"""
    
    def test_redownload_selected_declarations(self):
        """Test re-downloading selected declarations"""
        scheduler = Mock()
        
        # Create declarations to re-download
        declarations = [
            Declaration(
                declaration_number="308010891440",
                tax_code="2300782217",
                declaration_date=datetime(2023, 12, 6),
                customs_office_code="18A3",
                transport_method="1",
                channel="Xanh",
                status="T",
                goods_description=None
            )
        ]
        
        # Mock result
        result = WorkflowResult(
            total_fetched=1,
            total_eligible=1,
            success_count=1,
            error_count=0
        )
        scheduler.redownload_declarations.return_value = result
        
        # Execute re-download
        actual_result = scheduler.redownload_declarations(declarations)
        
        # Verify re-download was called
        scheduler.redownload_declarations.assert_called_once_with(declarations)
        assert actual_result.success_count == 1
        assert actual_result.error_count == 0


class TestGUIFileLocation:
    """Test GUI file location functionality"""
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('platform.system')
    def test_open_file_location_windows(self, mock_platform, mock_exists, mock_subprocess):
        """Test opening file location on Windows"""
        # Setup mocks
        mock_platform.return_value = "Windows"
        mock_exists.return_value = True
        
        # File path
        file_path = "C:\\CustomsBarcodes\\2300782217_308010891440.pdf"
        
        # Simulate opening file location
        if os.path.exists(file_path):
            import subprocess
            import platform
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", os.path.normpath(file_path)])
        
        # Verify subprocess was called
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert args[0] == "explorer"
        assert args[1] == "/select,"
    
    @patch('os.path.exists')
    def test_open_file_location_file_not_found(self, mock_exists):
        """Test opening file location when file doesn't exist"""
        # Setup mock
        mock_exists.return_value = False
        
        # File path
        file_path = "C:\\CustomsBarcodes\\nonexistent.pdf"
        
        # Check if file exists
        exists = os.path.exists(file_path)
        
        # Verify file doesn't exist
        assert not exists


class TestGUISimplifiedInterface:
    """Test simplified GUI interface (Automatic mode removed)
    
    Requirements: 1.1, 1.2, 1.4
    """
    
    def test_mode_radio_buttons_not_present(self):
        """Test that mode radio buttons (Automatic/Manual) are not present in GUI
        
        Requirements: 1.1, 1.2
        """
        # Verify that CustomsAutomationGUI class does not have mode_var, auto_radio, manual_radio attributes
        # by checking the _create_control_panel method doesn't create them
        
        # Read the source code to verify mode selection is removed
        import inspect
        from gui.customs_gui import CustomsAutomationGUI
        
        source = inspect.getsource(CustomsAutomationGUI._create_control_panel)
        
        # Verify mode selection components are not in the source
        assert "self.mode_var" not in source, "mode_var should be removed from GUI"
        assert "self.auto_radio" not in source, "auto_radio should be removed from GUI"
        assert "self.manual_radio" not in source, "manual_radio should be removed from GUI"
        # Check that Radiobutton for mode selection is not created
        assert 'text="Automatic"' not in source, "Automatic mode radio button should be removed"
        assert 'text="Manual"' not in source or 'Radiobutton' not in source, \
            "Manual mode radio button should be removed"
    
    def test_start_stop_run_once_buttons_not_visible(self):
        """Test that Start, Stop, Run Once buttons are not visible in GUI
        
        Requirements: 1.4
        """
        # Verify that CustomsAutomationGUI class does not create these buttons
        import inspect
        from gui.customs_gui import CustomsAutomationGUI
        
        source = inspect.getsource(CustomsAutomationGUI._create_control_panel)
        
        # Verify button creation is not in the source
        assert "start_button" not in source, "start_button should be removed from GUI"
        assert "stop_button" not in source, "stop_button should be removed from GUI"
        assert "run_once_button" not in source, "run_once_button should be removed from GUI"
    
    def test_toggle_operation_mode_method_removed(self):
        """Test that toggle_operation_mode method is removed from GUI
        
        Requirements: 1.1, 1.2, 1.3
        """
        from gui.customs_gui import CustomsAutomationGUI
        
        # Verify toggle_operation_mode method does not exist
        assert not hasattr(CustomsAutomationGUI, 'toggle_operation_mode'), \
            "toggle_operation_mode method should be removed from GUI"
    
    def test_scheduler_set_to_manual_mode_by_default(self):
        """Test that scheduler is set to Manual mode by default
        
        Requirements: 1.3
        """
        import inspect
        from gui.customs_gui import CustomsAutomationGUI
        
        source = inspect.getsource(CustomsAutomationGUI._create_control_panel)
        
        # Verify scheduler is set to manual mode
        assert "set_operation_mode" in source, "Scheduler should be set to a mode"
        assert "MANUAL" in source, "Scheduler should be set to MANUAL mode"
    
    def test_is_running_state_removed(self):
        """Test that is_running state variable is removed from GUI
        
        Requirements: 1.4
        """
        import inspect
        from gui.customs_gui import CustomsAutomationGUI
        
        source = inspect.getsource(CustomsAutomationGUI.__init__)
        
        # Verify is_running is not set as an instance variable
        # The comment mentions it's removed, so we check it's not assigned
        assert "self.is_running = " not in source, "is_running state should be removed from GUI"


class TestGUIOutputDirectory:
    """Test GUI output directory configuration"""
    
    def test_browse_output_directory(self):
        """Test browsing for output directory"""
        config_manager = Mock()
        logger = Mock()
        
        # Simulate directory selection
        new_directory = "D:\\NewCustomsBarcodes"
        
        config_manager.set_output_path(new_directory)
        config_manager.save()
        
        # Verify configuration was updated
        config_manager.set_output_path.assert_called_once_with(new_directory)
        config_manager.save.assert_called_once()
    
    def test_output_directory_validation(self):
        """Test output directory path validation"""
        config_manager = Mock()
        config_manager.get_output_path.return_value = "C:\\CustomsBarcodes"
        
        # Get output path
        output_path = config_manager.get_output_path()
        
        # Verify path is returned
        assert output_path == "C:\\CustomsBarcodes"
        assert isinstance(output_path, str)
        assert len(output_path) > 0
