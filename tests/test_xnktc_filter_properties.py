"""
Property-based tests for XNK TC filter functionality

Tests the is_xnktc property on Declaration model and filter_xnktc_declarations
method on PreviewManager using hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from datetime import datetime
from unittest.mock import MagicMock
from models.declaration_models import Declaration
from processors.preview_manager import PreviewManager


def create_test_declaration(so_hstk: str = None) -> Declaration:
    """Helper to create a Declaration with minimal required fields"""
    return Declaration(
        declaration_number="308010891440",
        tax_code="2300782217",
        declaration_date=datetime(2023, 12, 6, 14, 30, 25),
        customs_office_code="18A3",
        transport_method="1",
        channel="Xanh",
        status="T",
        goods_description="Test goods",
        so_hstk=so_hstk
    )


class TestXNKTCPatternDetectionProperty:
    """
    **Feature: filter-xnktc-declarations, Property 1: XNK TC Pattern Detection**
    
    *For any* string value in the SoHSTK field, the `is_xnktc` property SHALL return 
    True if and only if the string contains at least one of the patterns "#&NKTC", 
    "#&XKTC", or "#&GCPTQ" (case-insensitive).
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.5**
    """
    
    XNKTC_PATTERNS = ['#&NKTC', '#&XKTC', '#&GCPTQ']
    
    @given(st.text())
    @settings(max_examples=100)
    def test_is_xnktc_matches_pattern_presence(self, so_hstk: str):
        """
        Property: is_xnktc returns True iff SoHSTK contains XNK TC pattern (case-insensitive)
        """
        declaration = create_test_declaration(so_hstk)
        
        # Expected: True if any pattern is found (case-insensitive)
        so_hstk_upper = so_hstk.upper()
        expected = any(pattern in so_hstk_upper for pattern in self.XNKTC_PATTERNS)
        
        assert declaration.is_xnktc == expected
    
    @given(st.sampled_from(['#&NKTC', '#&XKTC', '#&GCPTQ']))
    @settings(max_examples=100)
    def test_is_xnktc_true_for_exact_patterns(self, pattern: str):
        """
        Property: is_xnktc returns True for exact XNK TC patterns
        """
        declaration = create_test_declaration(pattern)
        assert declaration.is_xnktc is True
    
    @given(
        st.sampled_from(['#&NKTC', '#&XKTC', '#&GCPTQ']),
        st.text(min_size=0, max_size=20),
        st.text(min_size=0, max_size=20)
    )
    @settings(max_examples=100)
    def test_is_xnktc_true_with_surrounding_text(self, pattern: str, prefix: str, suffix: str):
        """
        Property: is_xnktc returns True when pattern is embedded in other text
        """
        so_hstk = f"{prefix}{pattern}{suffix}"
        declaration = create_test_declaration(so_hstk)
        assert declaration.is_xnktc is True
    
    @given(
        st.sampled_from(['#&nktc', '#&xktc', '#&gcptq', '#&Nktc', '#&Xktc', '#&Gcptq'])
    )
    @settings(max_examples=100)
    def test_is_xnktc_case_insensitive(self, pattern: str):
        """
        Property: is_xnktc performs case-insensitive matching
        """
        declaration = create_test_declaration(pattern)
        assert declaration.is_xnktc is True
    
    @given(st.text())
    @settings(max_examples=100)
    def test_is_xnktc_false_without_patterns(self, so_hstk: str):
        """
        Property: is_xnktc returns False when no XNK TC pattern is present
        """
        # Assume the text doesn't contain any XNK TC pattern
        so_hstk_upper = so_hstk.upper()
        assume(not any(pattern in so_hstk_upper for pattern in self.XNKTC_PATTERNS))
        
        declaration = create_test_declaration(so_hstk)
        assert declaration.is_xnktc is False


class TestNullEmptySoHSTKHandlingProperty:
    """
    **Feature: filter-xnktc-declarations, Property 4: Null/Empty SoHSTK Handling**
    
    *For any* declaration with null or empty SoHSTK field, the `is_xnktc` property 
    SHALL return False (treated as normal declaration).
    
    **Validates: Requirements 2.4**
    """
    
    def test_is_xnktc_false_for_none(self):
        """
        Property: is_xnktc returns False when SoHSTK is None
        """
        declaration = create_test_declaration(so_hstk=None)
        assert declaration.is_xnktc is False
    
    def test_is_xnktc_false_for_empty_string(self):
        """
        Property: is_xnktc returns False when SoHSTK is empty string
        """
        declaration = create_test_declaration(so_hstk="")
        assert declaration.is_xnktc is False
    
    @given(st.text(alphabet=st.characters(whitelist_categories=['Zs']), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_is_xnktc_false_for_whitespace_only(self, whitespace: str):
        """
        Property: is_xnktc returns False when SoHSTK contains only whitespace
        (whitespace doesn't contain XNK TC patterns)
        """
        declaration = create_test_declaration(so_hstk=whitespace)
        # Whitespace-only strings don't contain XNK TC patterns
        assert declaration.is_xnktc is False
    
    @given(st.none() | st.just(""))
    @settings(max_examples=100)
    def test_is_xnktc_false_for_null_or_empty(self, so_hstk):
        """
        Property: is_xnktc returns False for both None and empty string
        """
        declaration = create_test_declaration(so_hstk=so_hstk)
        assert declaration.is_xnktc is False


# Strategy to generate Declaration objects with optional XNK TC patterns
@st.composite
def declaration_strategy(draw, force_xnktc: bool = None):
    """
    Generate a Declaration with random or forced XNK TC status
    
    Args:
        force_xnktc: If True, force XNK TC pattern. If False, force no pattern. 
                     If None, random.
    """
    XNKTC_PATTERNS = ['#&NKTC', '#&XKTC', '#&GCPTQ']
    
    if force_xnktc is True:
        # Force XNK TC pattern
        pattern = draw(st.sampled_from(XNKTC_PATTERNS))
        prefix = draw(st.text(min_size=0, max_size=10))
        suffix = draw(st.text(min_size=0, max_size=10))
        so_hstk = f"{prefix}{pattern}{suffix}"
    elif force_xnktc is False:
        # Force no XNK TC pattern - generate text without patterns
        so_hstk = draw(st.text(min_size=0, max_size=30))
        # Ensure no XNK TC pattern is present
        so_hstk_upper = so_hstk.upper()
        if any(p in so_hstk_upper for p in XNKTC_PATTERNS):
            so_hstk = "NORMAL_DECLARATION"
    else:
        # Random - could be XNK TC or not
        is_xnktc = draw(st.booleans())
        if is_xnktc:
            pattern = draw(st.sampled_from(XNKTC_PATTERNS))
            prefix = draw(st.text(min_size=0, max_size=10))
            suffix = draw(st.text(min_size=0, max_size=10))
            so_hstk = f"{prefix}{pattern}{suffix}"
        else:
            so_hstk = draw(st.one_of(st.none(), st.text(min_size=0, max_size=30)))
            if so_hstk:
                so_hstk_upper = so_hstk.upper()
                if any(p in so_hstk_upper for p in XNKTC_PATTERNS):
                    so_hstk = "NORMAL_DECLARATION"
    
    return Declaration(
        declaration_number=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=['Nd', 'Lu']))),
        tax_code=draw(st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=['Nd']))),
        declaration_date=datetime(2023, 12, 6, 14, 30, 25),
        customs_office_code=draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=['Lu', 'Nd']))),
        transport_method="1",
        channel=draw(st.sampled_from(["Xanh", "Vang"])),
        status="T",
        goods_description="Test goods",
        so_hstk=so_hstk
    )


@st.composite
def declaration_list_strategy(draw, min_size=0, max_size=20):
    """Generate a list of declarations with mixed XNK TC status"""
    return draw(st.lists(declaration_strategy(), min_size=min_size, max_size=max_size))


def create_preview_manager():
    """Create a PreviewManager with mocked dependencies"""
    mock_connector = MagicMock()
    mock_logger = MagicMock()
    return PreviewManager(ecus_connector=mock_connector, logger=mock_logger)


class TestFilterExclusionCompletenessProperty:
    """
    **Feature: filter-xnktc-declarations, Property 2: Filter Exclusion Completeness**
    
    *For any* list of declarations and filter enabled (exclude_xnktc=True), 
    the filtered result SHALL NOT contain any declaration where `is_xnktc` 
    property returns True.
    
    **Validates: Requirements 1.3**
    """
    
    @given(declaration_list_strategy(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_filter_excludes_all_xnktc_declarations(self, declarations):
        """
        Property: When filter is enabled, no XNK TC declarations remain in result
        """
        preview_manager = create_preview_manager()
        
        # Apply filter with exclude_xnktc=True
        filtered = preview_manager.filter_xnktc_declarations(declarations, exclude_xnktc=True)
        
        # Verify: No declaration in filtered result should be XNK TC
        for decl in filtered:
            assert decl.is_xnktc is False, f"XNK TC declaration found in filtered result: {decl.so_hstk}"
    
    @given(st.lists(declaration_strategy(force_xnktc=True), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_filter_removes_all_when_all_are_xnktc(self, xnktc_declarations):
        """
        Property: When all declarations are XNK TC, filter returns empty list
        """
        preview_manager = create_preview_manager()
        
        # Apply filter
        filtered = preview_manager.filter_xnktc_declarations(xnktc_declarations, exclude_xnktc=True)
        
        # All should be removed
        assert len(filtered) == 0


class TestFilterInclusionCompletenessProperty:
    """
    **Feature: filter-xnktc-declarations, Property 3: Filter Inclusion Completeness**
    
    *For any* list of declarations and filter disabled (exclude_xnktc=False), 
    the filtered result SHALL contain all declarations from the original list 
    (no declarations removed).
    
    **Validates: Requirements 1.4**
    """
    
    @given(declaration_list_strategy(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_filter_disabled_returns_all_declarations(self, declarations):
        """
        Property: When filter is disabled, all declarations are returned unchanged
        """
        preview_manager = create_preview_manager()
        
        # Apply filter with exclude_xnktc=False
        filtered = preview_manager.filter_xnktc_declarations(declarations, exclude_xnktc=False)
        
        # Verify: All original declarations should be in result
        assert len(filtered) == len(declarations)
        
        # Verify: Same declarations (by reference)
        for original in declarations:
            assert original in filtered
    
    @given(st.lists(declaration_strategy(force_xnktc=True), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_filter_disabled_keeps_xnktc_declarations(self, xnktc_declarations):
        """
        Property: When filter is disabled, XNK TC declarations are kept
        """
        preview_manager = create_preview_manager()
        
        # Apply filter with exclude_xnktc=False
        filtered = preview_manager.filter_xnktc_declarations(xnktc_declarations, exclude_xnktc=False)
        
        # All XNK TC declarations should remain
        assert len(filtered) == len(xnktc_declarations)
        for decl in filtered:
            assert decl.is_xnktc is True


class TestFilterStateConsistencyProperty:
    """
    **Feature: filter-xnktc-declarations, Property 5: Filter State Consistency**
    
    *For any* sequence of preview operations within a session, the filter SHALL be 
    applied consistently according to the current checkbox state.
    
    **Validates: Requirements 4.1, 4.2**
    """
    
    @given(
        st.lists(declaration_strategy(), min_size=1, max_size=10),
        st.lists(st.booleans(), min_size=1, max_size=5)
    )
    @settings(max_examples=100)
    def test_filter_state_applied_consistently(self, declarations, filter_states):
        """
        Property: For any sequence of filter state changes, the filter is applied 
        consistently according to the current state
        """
        preview_manager = create_preview_manager()
        
        for exclude_xnktc in filter_states:
            # Apply filter with current state
            filtered = preview_manager.filter_xnktc_declarations(
                declarations, 
                exclude_xnktc=exclude_xnktc
            )
            
            if exclude_xnktc:
                # When filter is enabled, no XNK TC declarations should remain
                for decl in filtered:
                    assert decl.is_xnktc is False, \
                        f"XNK TC declaration found when filter enabled: {decl.so_hstk}"
            else:
                # When filter is disabled, all declarations should remain
                assert len(filtered) == len(declarations), \
                    "All declarations should be present when filter disabled"
    
    @given(
        st.lists(declaration_strategy(), min_size=1, max_size=10),
        st.booleans()
    )
    @settings(max_examples=100)
    def test_filter_state_remembered_within_session(self, declarations, initial_state):
        """
        Property: Filter state is remembered and applied consistently within a session
        """
        preview_manager = create_preview_manager()
        
        # Apply filter multiple times with same state
        for _ in range(3):
            filtered = preview_manager.filter_xnktc_declarations(
                declarations, 
                exclude_xnktc=initial_state
            )
            
            # Results should be consistent
            if initial_state:
                xnktc_count = sum(1 for d in filtered if d.is_xnktc)
                assert xnktc_count == 0, "Filter should consistently exclude XNK TC"
            else:
                assert len(filtered) == len(declarations), \
                    "Filter should consistently include all declarations"
    
    @given(
        st.lists(declaration_strategy(force_xnktc=True), min_size=1, max_size=5),
        st.lists(declaration_strategy(force_xnktc=False), min_size=1, max_size=5)
    )
    @settings(max_examples=100)
    def test_filter_toggle_produces_correct_results(self, xnktc_decls, normal_decls):
        """
        Property: Toggling filter state produces correct results each time
        """
        preview_manager = create_preview_manager()
        all_declarations = xnktc_decls + normal_decls
        
        # Test with filter enabled
        filtered_enabled = preview_manager.filter_xnktc_declarations(
            all_declarations, 
            exclude_xnktc=True
        )
        
        # Should only contain normal declarations
        assert len(filtered_enabled) == len(normal_decls), \
            f"Expected {len(normal_decls)} normal declarations, got {len(filtered_enabled)}"
        
        # Test with filter disabled
        filtered_disabled = preview_manager.filter_xnktc_declarations(
            all_declarations, 
            exclude_xnktc=False
        )
        
        # Should contain all declarations
        assert len(filtered_disabled) == len(all_declarations), \
            f"Expected {len(all_declarations)} declarations, got {len(filtered_disabled)}"
        
        # Toggle back to enabled
        filtered_enabled_again = preview_manager.filter_xnktc_declarations(
            all_declarations, 
            exclude_xnktc=True
        )
        
        # Should produce same result as first enabled filter
        assert len(filtered_enabled_again) == len(filtered_enabled), \
            "Filter should produce consistent results when toggled back"
