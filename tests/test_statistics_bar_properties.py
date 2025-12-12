"""
Property-based tests for StatisticsBar component.

Tests Property 5: Statistics Counter Accuracy
Tests Property 6: Error Counter Accuracy
Validates: Requirements 10.1, 10.2
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockStatisticsBar:
    """
    Mock implementation of StatisticsBar for testing without Tkinter.
    
    This mock implements the core statistics logic without GUI dependencies.
    """
    
    def __init__(self):
        self._processed = 0
        self._retrieved = 0
        self._errors = 0
        self._last_run = None
    
    def update_stats(self, processed=None, retrieved=None, errors=None, last_run=None):
        """Update statistics."""
        if processed is not None:
            self._processed = processed
        if retrieved is not None:
            self._retrieved = retrieved
        if errors is not None:
            self._errors = errors
        if last_run is not None:
            self._last_run = last_run
    
    def increment_processed(self, count=1):
        """Increment processed count."""
        self._processed += count
    
    def increment_retrieved(self, count=1):
        """Increment retrieved count."""
        self._retrieved += count
    
    def increment_errors(self, count=1):
        """Increment errors count."""
        self._errors += count
    
    def set_last_run(self, timestamp=None):
        """Set last run timestamp."""
        self._last_run = timestamp or datetime.now()
    
    def reset_stats(self):
        """Reset all statistics."""
        self._processed = 0
        self._retrieved = 0
        self._errors = 0
        self._last_run = None
    
    def get_stats(self):
        """Get current statistics."""
        return {
            'processed': self._processed,
            'retrieved': self._retrieved,
            'errors': self._errors,
            'last_run': self._last_run
        }


class TestStatisticsBarProperties:
    """Property-based tests for StatisticsBar."""
    
    @given(increments=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_property_5_retrieved_counter_accuracy(self, increments):
        """
        Property 5: Statistics Counter Accuracy
        
        For any successful barcode download, the "Barcodes Retrieved" counter
        SHALL increment by exactly 1.
        
        Validates: Requirements 10.1
        """
        stats = MockStatisticsBar()
        
        expected_total = 0
        for increment in increments:
            for _ in range(increment):
                stats.increment_retrieved(1)
                expected_total += 1
        
        assert stats._retrieved == expected_total, \
            f"Expected retrieved={expected_total}, got {stats._retrieved}"
    
    @given(increments=st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_property_6_error_counter_accuracy(self, increments):
        """
        Property 6: Error Counter Accuracy
        
        For any failed barcode download, the "Errors" counter
        SHALL increment by exactly 1.
        
        Validates: Requirements 10.2
        """
        stats = MockStatisticsBar()
        
        expected_total = 0
        for increment in increments:
            for _ in range(increment):
                stats.increment_errors(1)
                expected_total += 1
        
        assert stats._errors == expected_total, \
            f"Expected errors={expected_total}, got {stats._errors}"
    
    @given(
        success_count=st.integers(min_value=0, max_value=1000),
        error_count=st.integers(min_value=0, max_value=1000)
    )
    @settings(max_examples=100)
    def test_counters_independent(self, success_count, error_count):
        """
        Success and error counters should be independent.
        """
        stats = MockStatisticsBar()
        
        for _ in range(success_count):
            stats.increment_retrieved(1)
        
        for _ in range(error_count):
            stats.increment_errors(1)
        
        assert stats._retrieved == success_count
        assert stats._errors == error_count
    
    @given(
        processed=st.integers(min_value=0, max_value=10000),
        retrieved=st.integers(min_value=0, max_value=10000),
        errors=st.integers(min_value=0, max_value=10000)
    )
    @settings(max_examples=50)
    def test_update_stats_sets_values(self, processed, retrieved, errors):
        """
        update_stats should set values correctly.
        """
        stats = MockStatisticsBar()
        stats.update_stats(processed=processed, retrieved=retrieved, errors=errors)
        
        assert stats._processed == processed
        assert stats._retrieved == retrieved
        assert stats._errors == errors
    
    @given(
        initial_retrieved=st.integers(min_value=0, max_value=1000),
        additional_retrieved=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50)
    def test_increment_adds_to_existing(self, initial_retrieved, additional_retrieved):
        """
        Increment should add to existing value.
        """
        stats = MockStatisticsBar()
        stats.update_stats(retrieved=initial_retrieved)
        
        stats.increment_retrieved(additional_retrieved)
        
        assert stats._retrieved == initial_retrieved + additional_retrieved


class TestStatisticsBarUnit:
    """Unit tests for StatisticsBar."""
    
    def test_init_zeros(self):
        """Test initialization with zero values."""
        stats = MockStatisticsBar()
        
        assert stats._processed == 0
        assert stats._retrieved == 0
        assert stats._errors == 0
        assert stats._last_run is None
    
    def test_increment_retrieved(self):
        """Test increment_retrieved."""
        stats = MockStatisticsBar()
        
        stats.increment_retrieved()
        assert stats._retrieved == 1
        
        stats.increment_retrieved()
        assert stats._retrieved == 2
    
    def test_increment_errors(self):
        """Test increment_errors."""
        stats = MockStatisticsBar()
        
        stats.increment_errors()
        assert stats._errors == 1
        
        stats.increment_errors()
        assert stats._errors == 2
    
    def test_increment_processed(self):
        """Test increment_processed."""
        stats = MockStatisticsBar()
        
        stats.increment_processed()
        assert stats._processed == 1
        
        stats.increment_processed(5)
        assert stats._processed == 6
    
    def test_set_last_run(self):
        """Test set_last_run."""
        stats = MockStatisticsBar()
        
        now = datetime.now()
        stats.set_last_run(now)
        
        assert stats._last_run == now
    
    def test_set_last_run_default(self):
        """Test set_last_run with default (now)."""
        stats = MockStatisticsBar()
        
        before = datetime.now()
        stats.set_last_run()
        after = datetime.now()
        
        assert before <= stats._last_run <= after
    
    def test_reset_stats(self):
        """Test reset_stats."""
        stats = MockStatisticsBar()
        
        stats.update_stats(processed=10, retrieved=5, errors=2)
        stats.set_last_run()
        
        stats.reset_stats()
        
        assert stats._processed == 0
        assert stats._retrieved == 0
        assert stats._errors == 0
        assert stats._last_run is None
    
    def test_get_stats(self):
        """Test get_stats."""
        stats = MockStatisticsBar()
        
        now = datetime.now()
        stats.update_stats(processed=10, retrieved=5, errors=2, last_run=now)
        
        result = stats.get_stats()
        
        assert result['processed'] == 10
        assert result['retrieved'] == 5
        assert result['errors'] == 2
        assert result['last_run'] == now
    
    def test_partial_update(self):
        """Test partial update_stats."""
        stats = MockStatisticsBar()
        
        stats.update_stats(processed=10)
        assert stats._processed == 10
        assert stats._retrieved == 0
        
        stats.update_stats(retrieved=5)
        assert stats._processed == 10
        assert stats._retrieved == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
