"""
Property-based tests for Error Tracker

These tests use Hypothesis to verify correctness properties across many random inputs.

**Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
**Validates: Requirements 4.4**
"""

from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
import os
import tempfile
import shutil

from error_handling.error_tracker import ErrorTracker, ErrorEntry
from database.tracking_database import TrackingDatabase


# Strategy for generating valid error types
error_types = st.sampled_from([
    'api_error', 'network_error', 'file_error', 'database_error', 
    'validation_error', 'timeout_error', 'connection_error', 'exception'
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

# Strategy for generating timestamps within the last 30 days
timestamps = st.datetimes(
    min_value=datetime.now() - timedelta(days=29),
    max_value=datetime.now()
)


class TestErrorTrackerProperties:
    """Property-based tests for ErrorTracker."""
    
    @given(
        declaration_number=declaration_numbers,
        error_type=error_types,
        error_message=error_messages,
        timestamp=timestamps
    )
    @settings(max_examples=100, deadline=None)
    def test_property_error_storage_completeness(
        self, declaration_number, error_type, error_message, timestamp
    ):
        """
        For any error that occurs, the stored error entry should contain 
        timestamp, declaration_number, error_type, and error_message.
        
        **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
        **Validates: Requirements 4.4**
        """
        # Create fresh database for each example to avoid interference
        temp_dir = tempfile.mkdtemp()
        try:
            db_path = os.path.join(temp_dir, 'test_tracking.db')
            tracking_db = TrackingDatabase(db_path)
            error_tracker = ErrorTracker(tracking_db)
            
            # Record the error
            error_tracker.record_error(
                declaration_number=declaration_number,
                error_type=error_type,
                message=error_message,
                timestamp=timestamp
            )
            
            # Retrieve errors for this declaration
            errors = error_tracker.get_errors_for_declaration(declaration_number)
            
            # Should have exactly one error
            assert len(errors) == 1, \
                f"Should have exactly one error for declaration {declaration_number}"
            
            # Get the error we just recorded
            recorded_error = errors[0]
            
            # Verify all required fields are present and match
            assert recorded_error.declaration_number == declaration_number, \
                f"Declaration number should match: expected '{declaration_number}', got '{recorded_error.declaration_number}'"
            
            assert recorded_error.error_type == error_type, \
                f"Error type should match: expected '{error_type}', got '{recorded_error.error_type}'"
            
            assert recorded_error.error_message == error_message, \
                f"Error message should match"
            
            assert recorded_error.timestamp is not None, \
                "Timestamp should not be None"
            
            # Verify timestamp is close to what we provided (within 1 second due to formatting)
            time_diff = abs((recorded_error.timestamp - timestamp).total_seconds())
            assert time_diff < 1, \
                f"Timestamp should be close to provided value, diff: {time_diff}s"
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    @given(
        declaration_number=declaration_numbers,
        error_type=error_types,
        error_message=error_messages
    )
    @settings(max_examples=100, deadline=None)
    def test_property_error_appears_in_history(
        self, declaration_number, error_type, error_message
    ):
        """
        For any recorded error, it should appear in the error history.
        
        **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
        **Validates: Requirements 4.4**
        """
        # Create fresh database for each example
        temp_dir = tempfile.mkdtemp()
        try:
            db_path = os.path.join(temp_dir, 'test_tracking.db')
            tracking_db = TrackingDatabase(db_path)
            error_tracker = ErrorTracker(tracking_db)
            
            # Record the error
            error_tracker.record_error(
                declaration_number=declaration_number,
                error_type=error_type,
                message=error_message
            )
            
            # Get error history
            history = error_tracker.get_error_history(days=30)
            
            # Should have exactly one error
            assert len(history) == 1, \
                "Error history should contain exactly one error"
            
            # Verify the error matches
            error = history[0]
            assert error.declaration_number == declaration_number, \
                "Declaration number should match"
            assert error.error_type == error_type, \
                "Error type should match"
            assert error.error_message == error_message, \
                "Error message should match"
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    @given(
        declaration_number=declaration_numbers,
        error_type=error_types,
        error_message=error_messages
    )
    @settings(max_examples=100, deadline=None)
    def test_property_error_count_increases(
        self, declaration_number, error_type, error_message
    ):
        """
        For any recorded error, the error count should increase by 1.
        
        **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
        **Validates: Requirements 4.4**
        """
        # Create fresh database for each example
        temp_dir = tempfile.mkdtemp()
        try:
            db_path = os.path.join(temp_dir, 'test_tracking.db')
            tracking_db = TrackingDatabase(db_path)
            error_tracker = ErrorTracker(tracking_db)
            
            # Get initial count (should be 0)
            initial_count = error_tracker.get_error_count(days=30)
            assert initial_count == 0, "Initial count should be 0"
            
            # Record the error
            error_tracker.record_error(
                declaration_number=declaration_number,
                error_type=error_type,
                message=error_message
            )
            
            # Get new count
            new_count = error_tracker.get_error_count(days=30)
            
            # Count should be 1
            assert new_count == 1, \
                f"Error count should be 1 after recording one error, got {new_count}"
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


# Feature: v1.3-enhancements, Property 5: Error Storage Completeness
@given(
    declaration_number=declaration_numbers,
    error_type=error_types,
    error_message=error_messages,
    timestamp=timestamps
)
@settings(max_examples=100, deadline=None)
def test_property_error_storage_completeness_standalone(
    declaration_number, error_type, error_message, timestamp
):
    """
    For any error that occurs, the stored error entry should contain 
    timestamp, declaration_number, error_type, and error_message.
    
    **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
    **Validates: Requirements 4.4**
    """
    temp_dir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        tracking_db = TrackingDatabase(db_path)
        error_tracker = ErrorTracker(tracking_db)
        
        # Record the error
        error_tracker.record_error(
            declaration_number=declaration_number,
            error_type=error_type,
            message=error_message,
            timestamp=timestamp
        )
        
        # Retrieve errors for this declaration
        errors = error_tracker.get_errors_for_declaration(declaration_number)
        
        # Should have at least one error
        assert len(errors) >= 1, \
            f"Should have at least one error for declaration {declaration_number}"
        
        # Find the error we just recorded (most recent one)
        recorded_error = errors[0]
        
        # Verify all required fields are present and match
        assert recorded_error.declaration_number == declaration_number, \
            f"Declaration number should match"
        
        assert recorded_error.error_type == error_type, \
            f"Error type should match"
        
        assert recorded_error.error_message == error_message, \
            f"Error message should match"
        
        assert recorded_error.timestamp is not None, \
            "Timestamp should not be None"
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_error_entry_dataclass():
    """
    Test that ErrorEntry dataclass has all required fields.
    
    **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
    **Validates: Requirements 4.4**
    """
    now = datetime.now()
    entry = ErrorEntry(
        timestamp=now,
        declaration_number="TEST123",
        error_type="api_error",
        error_message="Test error message"
    )
    
    # Verify all fields exist
    assert hasattr(entry, 'timestamp'), "ErrorEntry should have timestamp field"
    assert hasattr(entry, 'declaration_number'), "ErrorEntry should have declaration_number field"
    assert hasattr(entry, 'error_type'), "ErrorEntry should have error_type field"
    assert hasattr(entry, 'error_message'), "ErrorEntry should have error_message field"
    assert hasattr(entry, 'id'), "ErrorEntry should have id field"
    assert hasattr(entry, 'resolved'), "ErrorEntry should have resolved field"
    
    # Verify values
    assert entry.timestamp == now
    assert entry.declaration_number == "TEST123"
    assert entry.error_type == "api_error"
    assert entry.error_message == "Test error message"
    assert entry.id is None  # Default value
    assert entry.resolved is False  # Default value


def test_clear_old_errors():
    """
    Test that clear_old_errors removes errors older than specified days.
    
    **Feature: v1.3-enhancements, Property 5: Error Storage Completeness**
    **Validates: Requirements 4.5**
    """
    temp_dir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(temp_dir, 'test_tracking.db')
        tracking_db = TrackingDatabase(db_path)
        error_tracker = ErrorTracker(tracking_db)
        
        # Record an old error (35 days ago)
        old_timestamp = datetime.now() - timedelta(days=35)
        error_tracker.record_error(
            declaration_number="OLD123",
            error_type="api_error",
            message="Old error",
            timestamp=old_timestamp
        )
        
        # Record a recent error
        error_tracker.record_error(
            declaration_number="NEW123",
            error_type="api_error",
            message="New error"
        )
        
        # Clear errors older than 30 days
        deleted_count = error_tracker.clear_old_errors(days=30)
        
        # Should have deleted 1 error
        assert deleted_count == 1, f"Should delete 1 old error, deleted {deleted_count}"
        
        # Recent error should still exist
        history = error_tracker.get_error_history(days=30)
        assert len(history) == 1, "Should have 1 error remaining"
        assert history[0].declaration_number == "NEW123", "Recent error should remain"
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
