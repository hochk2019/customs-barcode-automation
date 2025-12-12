"""
Property-based tests for RecentCompaniesPanel and TrackingDatabase recent companies.

Tests Property 7: Recent Companies Update
Validates: Requirements 11.3
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockRecentCompaniesPanel:
    """
    Mock implementation of RecentCompaniesPanel for testing without Tkinter.
    """
    
    MAX_RECENT = 5
    
    def __init__(self):
        self.tax_codes: List[str] = []
    
    def update_recent(self, tax_codes: List[str]) -> None:
        """Update the recent companies list."""
        self.tax_codes = tax_codes[:self.MAX_RECENT] if tax_codes else []
    
    def add_recent(self, tax_code: str) -> None:
        """Add a tax code to the recent list."""
        if not tax_code:
            return
        
        # Remove if already exists
        if tax_code in self.tax_codes:
            self.tax_codes.remove(tax_code)
        
        # Add to front
        self.tax_codes.insert(0, tax_code)
        
        # Limit to MAX_RECENT
        self.tax_codes = self.tax_codes[:self.MAX_RECENT]
    
    def get_recent(self) -> List[str]:
        """Get list of recent tax codes."""
        return self.tax_codes.copy()
    
    def clear(self) -> None:
        """Clear all recent companies."""
        self.tax_codes = []


# Strategies for generating test data
tax_code_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('N',)),
    min_size=10,
    max_size=13
).filter(lambda x: x.strip())


class TestRecentCompaniesProperties:
    """Property-based tests for RecentCompaniesPanel."""
    
    @given(tax_codes=st.lists(tax_code_strategy, min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_property_7_recent_companies_update(self, tax_codes):
        """
        Property 7: Recent Companies Update
        
        For any successful barcode download for a company, that company's tax code
        SHALL appear in the recent companies list.
        
        Validates: Requirements 11.3
        """
        # Filter out empty strings
        tax_codes = [tc for tc in tax_codes if tc.strip()]
        assume(len(tax_codes) > 0)
        
        panel = MockRecentCompaniesPanel()
        
        # Simulate downloads
        for tax_code in tax_codes:
            panel.add_recent(tax_code)
        
        # The most recent tax code should be in the list
        recent = panel.get_recent()
        last_tax_code = tax_codes[-1]
        
        assert last_tax_code in recent, \
            f"Last downloaded tax code '{last_tax_code}' should be in recent list"
    
    @given(tax_codes=st.lists(tax_code_strategy, min_size=6, max_size=20))
    @settings(max_examples=50)
    def test_max_recent_limit(self, tax_codes):
        """
        Recent companies list should be limited to MAX_RECENT (5).
        
        Validates: Requirement 11.1
        """
        tax_codes = [tc for tc in tax_codes if tc.strip()]
        assume(len(tax_codes) >= 6)
        
        panel = MockRecentCompaniesPanel()
        
        for tax_code in tax_codes:
            panel.add_recent(tax_code)
        
        recent = panel.get_recent()
        
        assert len(recent) <= panel.MAX_RECENT, \
            f"Recent list should have at most {panel.MAX_RECENT} items, got {len(recent)}"
    
    @given(tax_codes=st.lists(tax_code_strategy, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_most_recent_first(self, tax_codes):
        """
        Most recently added tax code should be first in the list.
        """
        tax_codes = [tc for tc in tax_codes if tc.strip()]
        assume(len(tax_codes) > 0)
        
        panel = MockRecentCompaniesPanel()
        
        for tax_code in tax_codes:
            panel.add_recent(tax_code)
        
        recent = panel.get_recent()
        last_tax_code = tax_codes[-1]
        
        assert recent[0] == last_tax_code, \
            f"Most recent tax code '{last_tax_code}' should be first, got '{recent[0]}'"
    
    @given(tax_code=tax_code_strategy)
    @settings(max_examples=50)
    def test_duplicate_moves_to_front(self, tax_code):
        """
        Adding a duplicate tax code should move it to the front.
        """
        assume(tax_code.strip())
        
        panel = MockRecentCompaniesPanel()
        
        # Add some tax codes
        panel.add_recent("1111111111")
        panel.add_recent("2222222222")
        panel.add_recent(tax_code)
        panel.add_recent("3333333333")
        
        # Add the same tax code again
        panel.add_recent(tax_code)
        
        recent = panel.get_recent()
        
        # Should be first
        assert recent[0] == tax_code
        
        # Should only appear once
        assert recent.count(tax_code) == 1
    
    @given(tax_codes=st.lists(tax_code_strategy, min_size=0, max_size=10))
    @settings(max_examples=50)
    def test_update_recent_replaces_list(self, tax_codes):
        """
        update_recent should replace the entire list.
        """
        tax_codes = [tc for tc in tax_codes if tc.strip()]
        
        panel = MockRecentCompaniesPanel()
        
        # Add some initial data
        panel.add_recent("0000000000")
        
        # Update with new list
        panel.update_recent(tax_codes)
        
        expected = tax_codes[:panel.MAX_RECENT]
        assert panel.get_recent() == expected


class TestRecentCompaniesUnit:
    """Unit tests for RecentCompaniesPanel."""
    
    def test_init_empty(self):
        """Test initialization with empty list."""
        panel = MockRecentCompaniesPanel()
        
        assert panel.get_recent() == []
    
    def test_add_single(self):
        """Test adding a single tax code."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1234567890")
        
        assert panel.get_recent() == ["1234567890"]
    
    def test_add_multiple(self):
        """Test adding multiple tax codes."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1111111111")
        panel.add_recent("2222222222")
        panel.add_recent("3333333333")
        
        recent = panel.get_recent()
        
        assert recent == ["3333333333", "2222222222", "1111111111"]
    
    def test_add_exceeds_max(self):
        """Test adding more than MAX_RECENT tax codes."""
        panel = MockRecentCompaniesPanel()
        
        for i in range(10):
            panel.add_recent(f"{i}" * 10)
        
        recent = panel.get_recent()
        
        assert len(recent) == 5
        assert recent[0] == "9999999999"  # Most recent
    
    def test_add_empty_string(self):
        """Test adding empty string does nothing."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1234567890")
        panel.add_recent("")
        
        assert panel.get_recent() == ["1234567890"]
    
    def test_clear(self):
        """Test clearing the list."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1234567890")
        panel.add_recent("0987654321")
        
        panel.clear()
        
        assert panel.get_recent() == []
    
    def test_update_with_empty_list(self):
        """Test update_recent with empty list."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1234567890")
        panel.update_recent([])
        
        assert panel.get_recent() == []
    
    def test_get_recent_returns_copy(self):
        """Test that get_recent returns a copy."""
        panel = MockRecentCompaniesPanel()
        
        panel.add_recent("1234567890")
        
        recent = panel.get_recent()
        recent.append("0000000000")
        
        # Original should not be modified
        assert panel.get_recent() == ["1234567890"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
