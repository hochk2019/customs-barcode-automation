"""
Property-based tests for Error Log Exporter

These tests use Hypothesis to verify correctness properties across many random inputs.

**Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
**Validates: Requirements 1.1, 1.2**
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings
import os
import tempfile
import shutil

from file_utils.error_log_exporter import ErrorLogExporter, ErrorEntry


# Strategy for generating valid error types
error_types = st.sampled_from([
    'api_error', 'network_error', 'file_error', 'database_error', 
    'validation_error', 'timeout_error', 'connection_error'
])

# Strategy for generating valid declaration numbers
declaration_numbers = st.text(
    min_size=1, 
    max_size=30, 
    alphabet=st.characters(
        whitelist_categories=('Nd', 'Lu', 'Ll'),
        min_codepoint=48,
        max_codepoint=122
    )
)

# Strategy for generating error messages (printable ASCII, no control chars)
error_messages = st.text(
    min_size=1, 
    max_size=200,
    alphabet=st.characters(
        whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
        blacklist_characters='\x00\r'
    )
)

# Strategy for generating timestamps
timestamps = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31)
)


# Strategy for generating a single ErrorEntry
@st.composite
def error_entry_strategy(draw):
    """Generate a random ErrorEntry."""
    return ErrorEntry(
        timestamp=draw(timestamps),
        declaration_number=draw(declaration_numbers),
        error_type=draw(error_types),
        error_message=draw(error_messages)
    )


# Strategy for generating a list of ErrorEntries
error_entries_list = st.lists(error_entry_strategy(), min_size=1, max_size=20)


# Feature: v1.3-enhancements, Property 1: Error Log Export Completeness
@given(entries=error_entries_list)
@settings(max_examples=100, deadline=None)
def test_property_error_log_export_completeness(entries):
    """
    For any list of error entries, exporting to file and reading back should 
    contain all original entries with all required fields (timestamp, error_type, 
    declaration_number, error_message).
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.1, 1.2**
    """
    # Create a temporary directory for the test
    temp_dir = tempfile.mkdtemp()
    try:
        # Create exporter with entries
        exporter = ErrorLogExporter(entries)
        
        # Generate filepath
        filepath = os.path.join(temp_dir, exporter.get_default_filename())
        
        # Export to file
        result = exporter.export_to_file(filepath)
        
        # Verify export succeeded
        assert result is True, "Export should succeed"
        assert os.path.exists(filepath), "Export file should exist"
        
        # Read back the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify all entries are present in the exported content
        for entry in entries:
            # Check timestamp is present (formatted as YYYY-MM-DD HH:MM:SS)
            timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            assert timestamp_str in content, \
                f"Timestamp '{timestamp_str}' should be in exported content"
            
            # Check error_type is present (uppercase)
            assert entry.error_type.upper() in content, \
                f"Error type '{entry.error_type.upper()}' should be in exported content"
            
            # Check declaration_number is present
            assert entry.declaration_number in content, \
                f"Declaration number '{entry.declaration_number}' should be in exported content"
            
            # Check error_message is present
            assert entry.error_message in content, \
                f"Error message '{entry.error_message}' should be in exported content"
        
        # Verify the total count in header matches
        assert f"Total Errors: {len(entries)}" in content, \
            f"Header should show correct total count: {len(entries)}"
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@given(entries=error_entries_list)
@settings(max_examples=100)
def test_property_format_entry_contains_all_fields(entries):
    """
    For any error entry, the formatted string should contain all required fields.
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.2**
    """
    exporter = ErrorLogExporter(entries)
    
    for entry in entries:
        formatted = exporter.format_entry(entry)
        
        # Check timestamp is present
        timestamp_str = entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        assert timestamp_str in formatted, \
            f"Formatted entry should contain timestamp '{timestamp_str}'"
        
        # Check error_type is present (uppercase)
        assert entry.error_type.upper() in formatted, \
            f"Formatted entry should contain error type '{entry.error_type.upper()}'"
        
        # Check declaration_number is present
        assert entry.declaration_number in formatted, \
            f"Formatted entry should contain declaration number '{entry.declaration_number}'"
        
        # Check error_message is present
        assert entry.error_message in formatted, \
            f"Formatted entry should contain error message"


@given(entries=error_entries_list)
@settings(max_examples=100)
def test_property_error_count_consistency(entries):
    """
    For any list of error entries, the error count should match the list length.
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.1**
    """
    exporter = ErrorLogExporter(entries)
    
    assert exporter.get_error_count() == len(entries), \
        f"Error count should be {len(entries)}, got {exporter.get_error_count()}"
    
    assert exporter.has_errors() == (len(entries) > 0), \
        "has_errors() should return True when there are entries"


@given(
    declaration_number=declaration_numbers,
    error_type=error_types,
    error_message=error_messages
)
@settings(max_examples=100)
def test_property_add_error_from_values(declaration_number, error_type, error_message):
    """
    For any error values, adding via add_error_from_values should create 
    a valid entry with all fields.
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.1, 1.2**
    """
    exporter = ErrorLogExporter()
    
    # Add error from values
    exporter.add_error_from_values(
        declaration_number=declaration_number,
        error_type=error_type,
        error_message=error_message
    )
    
    # Verify entry was added
    assert exporter.get_error_count() == 1, "Should have exactly one entry"
    
    # Get the entry
    entry = exporter.error_entries[0]
    
    # Verify all fields match
    assert entry.declaration_number == declaration_number, \
        "Declaration number should match"
    assert entry.error_type == error_type, \
        "Error type should match"
    assert entry.error_message == error_message, \
        "Error message should match"
    assert entry.timestamp is not None, \
        "Timestamp should be set"


def test_default_filename_format():
    """
    Test that default filename follows the format error_log_YYYYMMDD_HHMMSS.txt
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.3**
    """
    exporter = ErrorLogExporter()
    filename = exporter.get_default_filename()
    
    # Check format
    assert filename.startswith('error_log_'), \
        f"Filename should start with 'error_log_', got '{filename}'"
    assert filename.endswith('.txt'), \
        f"Filename should end with '.txt', got '{filename}'"
    
    # Extract date/time part
    date_time_part = filename[10:-4]  # Remove 'error_log_' and '.txt'
    
    # Should be in format YYYYMMDD_HHMMSS (15 characters)
    assert len(date_time_part) == 15, \
        f"Date/time part should be 15 characters, got {len(date_time_part)}"
    assert date_time_part[8] == '_', \
        f"Should have underscore separator at position 8"


def test_empty_error_list_export():
    """
    Test that exporting empty error list still creates valid file.
    
    **Feature: v1.3-enhancements, Property 1: Error Log Export Completeness**
    **Validates: Requirements 1.1**
    """
    temp_dir = tempfile.mkdtemp()
    try:
        exporter = ErrorLogExporter([])
        filepath = os.path.join(temp_dir, 'empty_log.txt')
        
        result = exporter.export_to_file(filepath)
        
        assert result is True, "Export should succeed even with empty list"
        assert os.path.exists(filepath), "File should be created"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Total Errors: 0" in content, \
            "Header should show zero errors"
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
