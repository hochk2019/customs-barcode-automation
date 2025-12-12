"""
Property-based tests for SmartCompanySearch

This module contains property-based tests for the SmartCompanySearch component.
Tests verify filtering and auto-select behavior according to Requirements 3.1, 3.2, 3.3.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from gui.smart_company_search import SmartCompanySearchLogic, Company


# Strategies for generating test data
company_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

tax_code_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('N',)),
    min_size=10,
    max_size=13
).filter(lambda x: x.strip() and len(x) >= 10)

search_text_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
    min_size=0,
    max_size=30
)


def generate_company_tuples(num_companies: int) -> list:
    """Generate a list of unique company tuples (tax_code, name)"""
    companies = []
    for i in range(num_companies):
        tax_code = f"{1000000000 + i}"
        name = f"Company {i}"
        companies.append((tax_code, name))
    return companies


# **Feature: v1.1-ui-enhancements, Property 3: Smart Search Filtering**
# **Validates: Requirements 3.1, 3.2, 3.3**
@given(
    num_companies=st.integers(min_value=0, max_value=50),
    search_text=search_text_strategy
)
@settings(max_examples=100)
def test_property_smart_search_filtering(num_companies, search_text):
    """
    Property 3: Smart Search Filtering
    
    *For any* search text and list of companies, the filtered results should 
    only contain companies where either the company name or tax code contains 
    the search text (case-insensitive).
    
    **Validates: Requirements 3.1, 3.2, 3.3**
    """
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance (no UI required)
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Filter companies
    filtered = search.filter_companies(search_text)
    
    # Property 1: All filtered companies should match the search text
    search_lower = search_text.lower().strip() if search_text else ""
    
    for company in filtered:
        if search_lower:
            matches = (search_lower in company.tax_code.lower() or 
                      search_lower in company.name.lower())
            assert matches, (
                f"Company {company.display_text} does not match search '{search_text}'"
            )
    
    # Property 2: No matching company should be excluded from results
    if search_lower:
        for tc, name in companies:
            should_match = (search_lower in tc.lower() or search_lower in name.lower())
            if should_match:
                found = any(c.tax_code == tc and c.name == name for c in filtered)
                assert found, (
                    f"Company ({tc}, {name}) should match '{search_text}' but was excluded"
                )
    else:
        # Empty search should return all companies
        assert len(filtered) == num_companies, (
            f"Empty search should return all {num_companies} companies, got {len(filtered)}"
        )


# **Feature: v1.1-ui-enhancements, Property 4: Smart Search Auto-Select**
# **Validates: Requirements 3.2**
@given(
    num_companies=st.integers(min_value=1, max_value=50),
    company_index=st.integers(min_value=0, max_value=49)
)
@settings(max_examples=100)
def test_property_smart_search_auto_select_exact_tax_code(num_companies, company_index):
    """
    Property 4: Smart Search Auto-Select (Tax Code)
    
    *For any* search text that exactly matches a single company's tax code,
    the system should auto-select that company.
    
    **Validates: Requirements 3.2**
    """
    # Ensure company_index is within bounds
    assume(company_index < num_companies)
    
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Get the target company's tax code
    target_tax_code, target_name = companies[company_index]
    
    # Try auto-select with exact tax code
    result = search.auto_select_if_exact_match(target_tax_code)
    
    # Property: Should auto-select when exact match exists
    assert result is True, (
        f"Should auto-select company with tax code '{target_tax_code}'"
    )
    
    # Verify the correct company was selected
    selected = search.get_selected_company()
    assert selected is not None, "A company should be selected"
    assert selected.tax_code == target_tax_code, (
        f"Selected company tax code should be '{target_tax_code}', got '{selected.tax_code}'"
    )


@given(
    num_companies=st.integers(min_value=1, max_value=50),
    company_index=st.integers(min_value=0, max_value=49)
)
@settings(max_examples=100)
def test_property_smart_search_auto_select_exact_name(num_companies, company_index):
    """
    Property 4: Smart Search Auto-Select (Company Name)
    
    *For any* search text that exactly matches a single company's name,
    the system should auto-select that company.
    
    **Validates: Requirements 3.2**
    """
    # Ensure company_index is within bounds
    assume(company_index < num_companies)
    
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Get the target company's name
    target_tax_code, target_name = companies[company_index]
    
    # Try auto-select with exact name
    result = search.auto_select_if_exact_match(target_name)
    
    # Property: Should auto-select when exact match exists
    assert result is True, (
        f"Should auto-select company with name '{target_name}'"
    )
    
    # Verify the correct company was selected
    selected = search.get_selected_company()
    assert selected is not None, "A company should be selected"
    assert selected.name == target_name, (
        f"Selected company name should be '{target_name}', got '{selected.name}'"
    )


@given(
    num_companies=st.integers(min_value=0, max_value=50),
    partial_text=st.text(min_size=1, max_size=5)
)
@settings(max_examples=100)
def test_property_smart_search_no_auto_select_partial_match(num_companies, partial_text):
    """
    Property 4: Smart Search Auto-Select (No partial match)
    
    *For any* search text that does not exactly match any company's name or 
    tax code, the system should NOT auto-select.
    
    **Validates: Requirements 3.2, 3.3**
    """
    # Generate test companies with predictable format
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Use a partial text that won't exactly match any company
    # Our companies have format "Company N" and tax codes "100000000N"
    # So "Comp" or "100" won't be exact matches
    test_text = f"partial_{partial_text}"
    
    # Try auto-select with partial text
    result = search.auto_select_if_exact_match(test_text)
    
    # Property: Should NOT auto-select when no exact match
    assert result is False, (
        f"Should NOT auto-select with partial text '{test_text}'"
    )


# Additional property tests for edge cases

@given(
    num_companies=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_property_empty_search_returns_all(num_companies):
    """
    Property: Empty search returns all companies
    
    *For any* list of companies, an empty search should return all companies.
    
    **Validates: Requirements 3.5**
    """
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Filter with empty string
    filtered_empty = search.filter_companies("")
    filtered_whitespace = search.filter_companies("   ")
    
    # Property: Both should return all companies
    assert len(filtered_empty) == num_companies, (
        f"Empty search should return {num_companies} companies, got {len(filtered_empty)}"
    )
    assert len(filtered_whitespace) == num_companies, (
        f"Whitespace search should return {num_companies} companies, got {len(filtered_whitespace)}"
    )


@given(
    num_companies=st.integers(min_value=1, max_value=50),
    company_index=st.integers(min_value=0, max_value=49)
)
@settings(max_examples=100)
def test_property_case_insensitive_filtering(num_companies, company_index):
    """
    Property: Case-insensitive filtering
    
    *For any* search text, filtering should be case-insensitive.
    
    **Validates: Requirements 3.1**
    """
    assume(company_index < num_companies)
    
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Get a company name and search with different cases
    _, target_name = companies[company_index]
    
    filtered_lower = search.filter_companies(target_name.lower())
    filtered_upper = search.filter_companies(target_name.upper())
    filtered_original = search.filter_companies(target_name)
    
    # Property: All case variations should return the same results
    assert len(filtered_lower) == len(filtered_upper) == len(filtered_original), (
        f"Case-insensitive filtering failed: lower={len(filtered_lower)}, "
        f"upper={len(filtered_upper)}, original={len(filtered_original)}"
    )


@given(
    num_companies=st.integers(min_value=0, max_value=50)
)
@settings(max_examples=100)
def test_property_no_match_returns_empty(num_companies):
    """
    Property: No match returns empty list
    
    *For any* search text that matches no companies, filtering should return 
    an empty list.
    
    **Validates: Requirements 3.4**
    """
    # Generate test companies
    companies = generate_company_tuples(num_companies)
    
    # Create SmartCompanySearchLogic instance
    search = SmartCompanySearchLogic()
    search.set_companies(companies)
    
    # Search with text that won't match any company
    # Our companies have format "Company N" and tax codes "100000000N"
    impossible_search = "ZZZZZZZZZZZZZZZ_IMPOSSIBLE_MATCH"
    
    filtered = search.filter_companies(impossible_search)
    
    # Property: Should return empty list
    assert len(filtered) == 0, (
        f"Search '{impossible_search}' should return 0 companies, got {len(filtered)}"
    )
