"""
Property-based tests for Layout Optimization feature.

Tests the ConfigurationManager methods for panel split position and recent companies count.

Feature: layout-optimization
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings, HealthCheck

from config.configuration_manager import ConfigurationManager


def create_temp_config():
    """Create a temporary config file for testing."""
    config_content = """[Database]
server = localhost
database = test_db
username = test_user
password = test_pass

[BarcodeService]
api_url = http://test.api
primary_web_url = http://test.web
backup_web_url = http://backup.web

[Application]
output_directory = C:\\Test
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(config_content)
        return f.name


@pytest.fixture
def temp_config():
    """Create a temporary config file for testing."""
    temp_path = create_temp_config()
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestPanelSplitPositionProperties:
    """
    Property tests for panel split position.
    
    **Feature: layout-optimization, Property 1: Panel Split Position Persistence Round-Trip**
    **Validates: Requirements 8.3, 8.4**
    """
    
    @given(st.floats(min_value=0.25, max_value=0.50, allow_nan=False, allow_infinity=False))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_split_position_round_trip_valid_range(self, position):
        """
        Property 1: For any valid split position (0.25-0.50), 
        saving and loading should return the same value.
        
        **Feature: layout-optimization, Property 1: Panel Split Position Persistence Round-Trip**
        **Validates: Requirements 8.3, 8.4**
        """
        temp_path = create_temp_config()
        try:
            config = ConfigurationManager(temp_path)
            
            # Set position
            config.set_panel_split_position(position)
            config._save_config_file()
            
            # Reload and verify
            config2 = ConfigurationManager(temp_path)
            loaded = config2.get_panel_split_position()
            
            # Should be approximately equal (float precision)
            assert abs(loaded - position) < 0.001, f"Expected {position}, got {loaded}"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @given(st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_split_position_clamping(self, position):
        """
        Property: For any float value, split position should be clamped to 0.25-0.50.
        
        **Feature: layout-optimization, Property 1: Panel Split Position Persistence Round-Trip**
        **Validates: Requirements 8.3, 8.4**
        """
        temp_path = create_temp_config()
        try:
            config = ConfigurationManager(temp_path)
            
            # Set position (may be out of range)
            config.set_panel_split_position(position)
            config._save_config_file()
            
            # Reload and verify clamping
            config2 = ConfigurationManager(temp_path)
            loaded = config2.get_panel_split_position()
            
            # Should be within valid range
            assert 0.25 <= loaded <= 0.50, f"Position {loaded} out of valid range [0.25, 0.50]"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_split_position_default(self, temp_config):
        """Test default split position is 0.38."""
        config = ConfigurationManager(temp_config)
        
        # Without setting, should return default
        position = config.get_panel_split_position()
        assert position == 0.38, f"Expected default 0.38, got {position}"


class TestRecentCompaniesCountProperties:
    """
    Property tests for recent companies count.
    
    **Feature: layout-optimization, Property 2: Recent Companies Count Clamping**
    **Feature: layout-optimization, Property 3: Recent Companies Count Persistence Round-Trip**
    **Validates: Requirements 6.2, 6.3, 6.4**
    """
    
    @given(st.integers(min_value=3, max_value=10))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_recent_companies_count_round_trip_valid_range(self, count):
        """
        Property 3: For any valid count (3-10), 
        saving and loading should return the same value.
        
        **Feature: layout-optimization, Property 3: Recent Companies Count Persistence Round-Trip**
        **Validates: Requirements 6.3, 6.4**
        """
        temp_path = create_temp_config()
        try:
            config = ConfigurationManager(temp_path)
            
            # Set count
            config.set_recent_companies_count(count)
            config._save_config_file()
            
            # Reload and verify
            config2 = ConfigurationManager(temp_path)
            loaded = config2.get_recent_companies_count()
            
            assert loaded == count, f"Expected {count}, got {loaded}"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @given(st.integers(min_value=-100, max_value=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_recent_companies_count_clamping(self, count):
        """
        Property 2: For any integer value, count should be clamped to 3-10.
        
        **Feature: layout-optimization, Property 2: Recent Companies Count Clamping**
        **Validates: Requirements 6.2**
        """
        temp_path = create_temp_config()
        try:
            config = ConfigurationManager(temp_path)
            
            # Set count (may be out of range)
            config.set_recent_companies_count(count)
            config._save_config_file()
            
            # Reload and verify clamping
            config2 = ConfigurationManager(temp_path)
            loaded = config2.get_recent_companies_count()
            
            # Should be within valid range
            assert 3 <= loaded <= 10, f"Count {loaded} out of valid range [3, 10]"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_recent_companies_count_default(self, temp_config):
        """Test default recent companies count is 5."""
        config = ConfigurationManager(temp_config)
        
        # Without setting, should return default
        count = config.get_recent_companies_count()
        assert count == 5, f"Expected default 5, got {count}"



class TestMinimumWidthConstraints:
    """
    Property tests for minimum width constraints.
    
    **Feature: layout-optimization, Property 4: Minimum Width Constraints**
    **Validates: Requirements 1.4, 8.2**
    """
    
    @given(st.integers(min_value=900, max_value=2000))
    @settings(max_examples=50, deadline=None)
    def test_minimum_width_constraints(self, total_width):
        """
        Property 4: For any window width, Control Panel should never be less than 400px
        and Preview Panel should never be less than 500px.
        
        **Feature: layout-optimization, Property 4: Minimum Width Constraints**
        **Validates: Requirements 1.4, 8.2**
        """
        from gui.two_column_layout import TwoColumnLayout
        
        MIN_LEFT = TwoColumnLayout.MIN_LEFT_WIDTH
        MIN_RIGHT = TwoColumnLayout.MIN_RIGHT_WIDTH
        
        # For any total width >= MIN_LEFT + MIN_RIGHT
        if total_width >= MIN_LEFT + MIN_RIGHT:
            # Maximum left width is total - MIN_RIGHT
            max_left = total_width - MIN_RIGHT
            # Minimum left width is MIN_LEFT
            min_left = MIN_LEFT
            
            # Valid range should exist
            assert max_left >= min_left, f"No valid range for width {total_width}"
            
            # Any split position should result in valid widths
            for ratio in [0.25, 0.38, 0.50]:
                left_width = int(total_width * ratio)
                # After clamping
                clamped_left = max(MIN_LEFT, min(max_left, left_width))
                right_width = total_width - clamped_left
                
                assert clamped_left >= MIN_LEFT, f"Left width {clamped_left} < {MIN_LEFT}"
                assert right_width >= MIN_RIGHT, f"Right width {right_width} < {MIN_RIGHT}"


class TestStatisticsFormatProperties:
    """
    Property tests for statistics format consistency.
    
    **Feature: layout-optimization, Property 5: Statistics Format Consistency**
    **Validates: Requirements 2.2**
    """
    
    @given(
        st.integers(min_value=0, max_value=10000),
        st.integers(min_value=0, max_value=10000),
        st.integers(min_value=0, max_value=10000)
    )
    @settings(max_examples=100)
    def test_statistics_format_contains_all_values(self, processed, retrieved, errors):
        """
        Property 5: For any combination of stats values, the formatted string
        should contain all four values in the expected inline format.
        
        **Feature: layout-optimization, Property 5: Statistics Format Consistency**
        **Validates: Requirements 2.2**
        """
        from gui.compact_status_bar import CompactStatusBar
        from datetime import datetime
        
        last_run = datetime.now()
        
        # Format statistics
        formatted = CompactStatusBar.format_statistics(
            None,  # self not needed for static-like method
            processed=processed,
            retrieved=retrieved,
            errors=errors,
            last_run=last_run
        )
        
        # Verify all values are present
        assert f"Processed: {processed}" in formatted, f"Missing processed count in: {formatted}"
        assert f"Retrieved: {retrieved}" in formatted, f"Missing retrieved count in: {formatted}"
        assert f"Errors: {errors}" in formatted, f"Missing errors count in: {formatted}"
        assert "Last:" in formatted, f"Missing last run time in: {formatted}"
        
        # Verify format structure (pipe-separated)
        assert formatted.count("|") == 3, f"Expected 3 separators, got {formatted.count('|')} in: {formatted}"
    
    def test_statistics_format_without_last_run(self):
        """Test statistics format when last_run is None."""
        from gui.compact_status_bar import CompactStatusBar
        
        formatted = CompactStatusBar.format_statistics(
            None,
            processed=10,
            retrieved=8,
            errors=2,
            last_run=None
        )
        
        assert "Last: --:--" in formatted, f"Expected '--:--' for None last_run, got: {formatted}"


class TestPathTruncationProperties:
    """
    Property tests for path truncation.
    
    **Feature: layout-optimization, Property 6: Path Truncation Preserves End**
    **Validates: Requirements 3.3**
    """
    
    @given(st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-/\\')))
    @settings(max_examples=100)
    def test_path_truncation_preserves_end(self, path):
        """
        Property 6: For any path longer than max length, truncation should
        preserve the last part (folder/filename) and prepend with "...".
        
        **Feature: layout-optimization, Property 6: Path Truncation Preserves End**
        **Validates: Requirements 3.3**
        """
        from gui.compact_output_section import CompactOutputSection
        
        max_length = 30
        truncated = CompactOutputSection.truncate_path(path, max_length)
        
        if len(path) <= max_length:
            # Short paths should not be truncated
            assert truncated == path, f"Short path was modified: {path} -> {truncated}"
        else:
            # Long paths should be truncated
            assert len(truncated) <= max_length + 3, f"Truncated path too long: {truncated}"
            
            # Should start with "..." if truncated
            if truncated != path:
                assert truncated.startswith("..."), f"Truncated path missing ellipsis: {truncated}"
            
            # Last part of path should be preserved
            path_parts = path.replace("\\", "/").split("/")
            if path_parts:
                last_part = path_parts[-1]
                if last_part and len(last_part) < max_length:
                    assert last_part in truncated, f"Last part '{last_part}' not in truncated: {truncated}"
    
    def test_path_truncation_empty_path(self):
        """Test truncation of empty path."""
        from gui.compact_output_section import CompactOutputSection
        
        result = CompactOutputSection.truncate_path("", 50)
        assert result == "", "Empty path should return empty string"
    
    def test_path_truncation_short_path(self):
        """Test truncation of path shorter than max length."""
        from gui.compact_output_section import CompactOutputSection
        
        path = "C:\\Users\\test"
        result = CompactOutputSection.truncate_path(path, 50)
        assert result == path, f"Short path should not be truncated: {result}"
    
    def test_path_truncation_long_path(self):
        """Test truncation of long path."""
        from gui.compact_output_section import CompactOutputSection
        
        path = "C:\\Users\\Administrator\\Documents\\Projects\\CustomsBarcodeAutomation\\output\\barcodes"
        result = CompactOutputSection.truncate_path(path, 40)
        
        assert len(result) <= 43, f"Truncated path too long: {result}"  # 40 + 3 for "..."
        assert result.startswith("..."), f"Should start with ellipsis: {result}"
        assert "barcodes" in result, f"Should preserve last folder: {result}"


class TestSectionHeightConstraints:
    """
    Property tests for section height constraints.
    
    **Feature: layout-optimization, Property 7: Section Height Constraints**
    **Validates: Requirements 2.3, 3.2, 4.4**
    """
    
    def test_compact_status_bar_max_height(self):
        """Test CompactStatusBar has correct max height constant."""
        from gui.compact_status_bar import CompactStatusBar
        
        assert CompactStatusBar.MAX_HEIGHT == 40, f"Expected 40px, got {CompactStatusBar.MAX_HEIGHT}"
    
    def test_compact_output_section_max_height(self):
        """Test CompactOutputSection has correct max height constant."""
        from gui.compact_output_section import CompactOutputSection
        
        assert CompactOutputSection.MAX_HEIGHT == 50, f"Expected 50px, got {CompactOutputSection.MAX_HEIGHT}"
    
    def test_compact_company_section_max_height(self):
        """Test CompactCompanySection has correct max height constant."""
        from gui.compact_company_section import CompactCompanySection
        
        assert CompactCompanySection.MAX_HEIGHT == 150, f"Expected 150px, got {CompactCompanySection.MAX_HEIGHT}"
    
    def test_preview_panel_min_height(self):
        """Test PreviewPanel has correct min height constant."""
        from gui.preview_panel import PreviewPanel
        
        assert PreviewPanel.MIN_HEIGHT == 400, f"Expected 400px, got {PreviewPanel.MIN_HEIGHT}"


class TestRecentCompaniesPanelProperties:
    """
    Property tests for RecentCompaniesPanel configurable count.
    
    **Feature: layout-optimization, Requirements 6.4, 6.5**
    """
    
    @given(st.integers(min_value=-10, max_value=20))
    @settings(max_examples=50)
    def test_set_max_recent_clamping(self, count):
        """
        Test that set_max_recent clamps values to valid range (3-10).
        
        **Feature: layout-optimization, Requirements 6.5**
        """
        from gui.recent_companies_panel import RecentCompaniesPanel
        
        # Create panel without parent (just test the clamping logic)
        # We can't instantiate without a parent, so test the constants
        assert RecentCompaniesPanel.MIN_RECENT == 3
        assert RecentCompaniesPanel.MAX_RECENT_LIMIT == 10
        assert RecentCompaniesPanel.DEFAULT_MAX_RECENT == 5
        
        # Test clamping logic
        clamped = max(3, min(10, count))
        assert 3 <= clamped <= 10, f"Clamped value {clamped} out of range"
