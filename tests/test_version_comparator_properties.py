"""
Property-based tests for version comparator.

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from update.version_comparator import VersionComparator


# Strategy for generating valid version components (non-negative integers)
version_component = st.integers(min_value=0, max_value=999)

# Strategy for generating valid version tuples
version_tuple = st.tuples(version_component, version_component, version_component)


def version_tuple_to_string(v: tuple, with_prefix: bool = False) -> str:
    """Convert a version tuple to a string."""
    version_str = f"{v[0]}.{v[1]}.{v[2]}"
    if with_prefix:
        return f"v{version_str}"
    return version_str


# **Feature: github-auto-update, Property 1: Version Comparison Correctness**
# **Validates: Requirements 6.1**
@given(
    v1=version_tuple,
    v2=version_tuple
)
@settings(max_examples=100)
def test_property_version_comparison_correctness(v1, v2):
    """
    For any two valid semantic version strings, comparing them SHALL return consistent
    results where a newer version is always greater than an older version.
    
    **Feature: github-auto-update, Property 1: Version Comparison Correctness**
    **Validates: Requirements 6.1**
    """
    version1 = version_tuple_to_string(v1)
    version2 = version_tuple_to_string(v2)
    
    result = VersionComparator.compare(version1, version2)
    
    # Verify comparison is consistent with tuple comparison
    if v1 < v2:
        assert result == -1, f"Expected {version1} < {version2}, but got result {result}"
    elif v1 > v2:
        assert result == 1, f"Expected {version1} > {version2}, but got result {result}"
    else:
        assert result == 0, f"Expected {version1} == {version2}, but got result {result}"
    
    # Verify is_newer is consistent with compare
    is_newer = VersionComparator.is_newer(version1, version2)
    assert is_newer == (result > 0), \
        f"is_newer({version1}, {version2}) should be {result > 0}, but got {is_newer}"


# **Feature: github-auto-update, Property 1: Version Comparison Transitivity**
# **Validates: Requirements 6.1**
@given(
    v1=version_tuple,
    v2=version_tuple,
    v3=version_tuple
)
@settings(max_examples=100)
def test_property_version_comparison_transitivity(v1, v2, v3):
    """
    For any three valid semantic version strings, if v1 < v2 and v2 < v3, then v1 < v3.
    
    **Feature: github-auto-update, Property 1: Version Comparison Correctness**
    **Validates: Requirements 6.1**
    """
    version1 = version_tuple_to_string(v1)
    version2 = version_tuple_to_string(v2)
    version3 = version_tuple_to_string(v3)
    
    cmp_1_2 = VersionComparator.compare(version1, version2)
    cmp_2_3 = VersionComparator.compare(version2, version3)
    cmp_1_3 = VersionComparator.compare(version1, version3)
    
    # If v1 < v2 and v2 < v3, then v1 < v3
    if cmp_1_2 == -1 and cmp_2_3 == -1:
        assert cmp_1_3 == -1, \
            f"Transitivity violated: {version1} < {version2} < {version3}, but {version1} not < {version3}"
    
    # If v1 > v2 and v2 > v3, then v1 > v3
    if cmp_1_2 == 1 and cmp_2_3 == 1:
        assert cmp_1_3 == 1, \
            f"Transitivity violated: {version1} > {version2} > {version3}, but {version1} not > {version3}"


# **Feature: github-auto-update, Property 1: Version Comparison Symmetry**
# **Validates: Requirements 6.1**
@given(
    v1=version_tuple,
    v2=version_tuple
)
@settings(max_examples=100)
def test_property_version_comparison_symmetry(v1, v2):
    """
    For any two valid semantic version strings, compare(v1, v2) == -compare(v2, v1).
    
    **Feature: github-auto-update, Property 1: Version Comparison Correctness**
    **Validates: Requirements 6.1**
    """
    version1 = version_tuple_to_string(v1)
    version2 = version_tuple_to_string(v2)
    
    result_1_2 = VersionComparator.compare(version1, version2)
    result_2_1 = VersionComparator.compare(version2, version1)
    
    assert result_1_2 == -result_2_1, \
        f"Symmetry violated: compare({version1}, {version2}) = {result_1_2}, " \
        f"but compare({version2}, {version1}) = {result_2_1}"



# **Feature: github-auto-update, Property 2: Version Prefix Normalization**
# **Validates: Requirements 6.2**
@given(v=version_tuple)
@settings(max_examples=100)
def test_property_version_prefix_normalization(v):
    """
    For any version string with or without "v" prefix, parsing SHALL produce the same
    numeric tuple (e.g., "v1.2.3" and "1.2.3" both yield (1, 2, 3)).
    
    **Feature: github-auto-update, Property 2: Version Prefix Normalization**
    **Validates: Requirements 6.2**
    """
    version_without_prefix = version_tuple_to_string(v, with_prefix=False)
    version_with_v_prefix = version_tuple_to_string(v, with_prefix=True)
    version_with_V_prefix = f"V{v[0]}.{v[1]}.{v[2]}"  # uppercase V
    
    # Parse all versions
    parsed_without = VersionComparator.parse_version(version_without_prefix)
    parsed_with_v = VersionComparator.parse_version(version_with_v_prefix)
    parsed_with_V = VersionComparator.parse_version(version_with_V_prefix)
    
    # All should produce the same tuple
    assert parsed_without == v, \
        f"parse_version('{version_without_prefix}') should be {v}, but got {parsed_without}"
    assert parsed_with_v == v, \
        f"parse_version('{version_with_v_prefix}') should be {v}, but got {parsed_with_v}"
    assert parsed_with_V == v, \
        f"parse_version('{version_with_V_prefix}') should be {v}, but got {parsed_with_V}"
    
    # Comparison should also be equal
    assert VersionComparator.compare(version_without_prefix, version_with_v_prefix) == 0, \
        f"'{version_without_prefix}' should equal '{version_with_v_prefix}'"
    assert VersionComparator.compare(version_without_prefix, version_with_V_prefix) == 0, \
        f"'{version_without_prefix}' should equal '{version_with_V_prefix}'"


# **Feature: github-auto-update, Property 2: Version Prefix Normalization with Whitespace**
# **Validates: Requirements 6.2**
@given(
    v=version_tuple,
    leading_spaces=st.integers(min_value=0, max_value=3),
    trailing_spaces=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=100)
def test_property_version_prefix_normalization_whitespace(v, leading_spaces, trailing_spaces):
    """
    For any version string with leading/trailing whitespace, parsing SHALL strip
    whitespace and produce the correct tuple.
    
    **Feature: github-auto-update, Property 2: Version Prefix Normalization**
    **Validates: Requirements 6.2**
    """
    base_version = version_tuple_to_string(v)
    version_with_spaces = " " * leading_spaces + base_version + " " * trailing_spaces
    
    parsed = VersionComparator.parse_version(version_with_spaces)
    
    assert parsed == v, \
        f"parse_version('{version_with_spaces}') should be {v}, but got {parsed}"


# **Feature: github-auto-update, Property 3: Invalid Version Handling**
# **Validates: Requirements 6.3**
@given(
    invalid_version=st.one_of(
        # Missing parts
        st.integers(min_value=0, max_value=999).map(str),  # Just "1"
        st.tuples(version_component, version_component).map(lambda t: f"{t[0]}.{t[1]}"),  # "1.2"
        # Too many parts
        st.tuples(version_component, version_component, version_component, version_component).map(
            lambda t: f"{t[0]}.{t[1]}.{t[2]}.{t[3]}"
        ),  # "1.2.3.4"
        # Non-numeric parts
        st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=('L',))).map(
            lambda s: f"{s}.0.0"
        ),  # "abc.0.0"
        st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=('L',))).map(
            lambda s: f"0.{s}.0"
        ),  # "0.abc.0"
        st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=('L',))).map(
            lambda s: f"0.0.{s}"
        ),  # "0.0.abc"
        # Empty string
        st.just(""),
        # Just dots
        st.just(".."),
        st.just("..."),
    )
)
@settings(max_examples=100)
def test_property_invalid_version_handling(invalid_version):
    """
    For any malformed version string, parsing SHALL raise ValueError.
    
    **Feature: github-auto-update, Property 3: Invalid Version Handling**
    **Validates: Requirements 6.3**
    """
    with pytest.raises(ValueError):
        VersionComparator.parse_version(invalid_version)


# **Feature: github-auto-update, Property 3: Negative Version Handling**
# **Validates: Requirements 6.3**
@given(
    major=st.integers(min_value=-999, max_value=-1),
    minor=st.integers(min_value=0, max_value=999),
    patch=st.integers(min_value=0, max_value=999)
)
@settings(max_examples=100)
def test_property_negative_major_version_handling(major, minor, patch):
    """
    For any version string with negative major component, parsing SHALL raise ValueError.
    
    **Feature: github-auto-update, Property 3: Invalid Version Handling**
    **Validates: Requirements 6.3**
    """
    invalid_version = f"{major}.{minor}.{patch}"
    with pytest.raises(ValueError):
        VersionComparator.parse_version(invalid_version)


@given(
    major=st.integers(min_value=0, max_value=999),
    minor=st.integers(min_value=-999, max_value=-1),
    patch=st.integers(min_value=0, max_value=999)
)
@settings(max_examples=100)
def test_property_negative_minor_version_handling(major, minor, patch):
    """
    For any version string with negative minor component, parsing SHALL raise ValueError.
    
    **Feature: github-auto-update, Property 3: Invalid Version Handling**
    **Validates: Requirements 6.3**
    """
    invalid_version = f"{major}.{minor}.{patch}"
    with pytest.raises(ValueError):
        VersionComparator.parse_version(invalid_version)


@given(
    major=st.integers(min_value=0, max_value=999),
    minor=st.integers(min_value=0, max_value=999),
    patch=st.integers(min_value=-999, max_value=-1)
)
@settings(max_examples=100)
def test_property_negative_patch_version_handling(major, minor, patch):
    """
    For any version string with negative patch component, parsing SHALL raise ValueError.
    
    **Feature: github-auto-update, Property 3: Invalid Version Handling**
    **Validates: Requirements 6.3**
    """
    invalid_version = f"{major}.{minor}.{patch}"
    with pytest.raises(ValueError):
        VersionComparator.parse_version(invalid_version)
