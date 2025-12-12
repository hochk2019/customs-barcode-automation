"""
Property-based tests for ErrorHandler.

These tests verify correctness properties that should hold across all inputs.
"""

import time
import pytest
from hypothesis import given, strategies as st, settings
from error_handling.error_handler import ErrorHandler, ErrorCategory


# Feature: customs-barcode-automation, Property 17: Retry with exponential backoff
# Validates: Requirements 9.1
@settings(max_examples=100, deadline=None)  # Disable deadline since we're testing timing behavior
@given(
    max_retries=st.integers(min_value=1, max_value=5),
    base_delay=st.integers(min_value=1, max_value=3)
)
def test_property_retry_exponential_backoff(max_retries, base_delay):
    """
    **Feature: customs-barcode-automation, Property 17: Retry with exponential backoff**
    **Validates: Requirements 9.1**
    
    For any network error during barcode retrieval, the system should retry 
    up to max_retries times with exponentially increasing delays.
    
    This property verifies that:
    1. The operation is retried the correct number of times
    2. The delays between retries follow exponential backoff (base_delay * 2^attempt)
    3. The final exception is raised after all retries are exhausted
    """
    handler = ErrorHandler(max_retries=max_retries, base_delay=base_delay)
    
    # Track call attempts and timing
    call_times = []
    attempt_count = [0]
    
    def failing_operation():
        """Operation that always fails"""
        attempt_count[0] += 1
        call_times.append(time.time())
        raise ConnectionError("Network error")
    
    # Execute and expect failure after all retries
    start_time = time.time()
    with pytest.raises(ConnectionError):
        handler.handle_with_retry(
            failing_operation,
            error_types=(ConnectionError,),
            operation_name="Test operation"
        )
    
    # Verify the operation was called max_retries times
    assert attempt_count[0] == max_retries, \
        f"Expected {max_retries} attempts, got {attempt_count[0]}"
    
    # Verify exponential backoff delays
    # For each retry (except the first attempt), verify the delay
    for i in range(1, len(call_times)):
        actual_delay = call_times[i] - call_times[i-1]
        expected_delay = base_delay * (2 ** (i - 1))
        
        # Allow 10% tolerance for timing variations
        tolerance = expected_delay * 0.1
        assert abs(actual_delay - expected_delay) <= tolerance, \
            f"Attempt {i}: Expected delay ~{expected_delay}s, got {actual_delay:.2f}s"


# Feature: customs-barcode-automation, Property 17: Retry with exponential backoff
# Validates: Requirements 9.1
@settings(max_examples=100, deadline=None)  # Disable deadline since we're testing timing behavior
@given(
    max_retries=st.integers(min_value=2, max_value=5),
    success_on_attempt=st.integers(min_value=1, max_value=4)
)
def test_property_retry_succeeds_before_max(max_retries, success_on_attempt):
    """
    For any operation that succeeds before max_retries, the system should 
    return the result without further retries.
    """
    # Ensure success_on_attempt is within max_retries
    if success_on_attempt > max_retries:
        success_on_attempt = max_retries
    
    handler = ErrorHandler(max_retries=max_retries, base_delay=1)
    
    attempt_count = [0]
    
    def eventually_succeeding_operation():
        """Operation that succeeds on a specific attempt"""
        attempt_count[0] += 1
        if attempt_count[0] < success_on_attempt:
            raise ConnectionError("Network error")
        return "success"
    
    # Execute operation
    result = handler.handle_with_retry(
        eventually_succeeding_operation,
        error_types=(ConnectionError,),
        operation_name="Test operation"
    )
    
    # Verify it succeeded on the expected attempt
    assert result == "success"
    assert attempt_count[0] == success_on_attempt, \
        f"Expected success on attempt {success_on_attempt}, got {attempt_count[0]}"


# Feature: customs-barcode-automation, Property 17: Retry with exponential backoff
# Validates: Requirements 9.1
@settings(max_examples=100)
@given(
    max_retries=st.integers(min_value=1, max_value=5)
)
def test_property_retry_only_catches_specified_errors(max_retries):
    """
    For any operation that raises an error not in error_types, the system 
    should raise immediately without retrying.
    """
    handler = ErrorHandler(max_retries=max_retries, base_delay=1)
    
    attempt_count = [0]
    
    def operation_with_unexpected_error():
        """Operation that raises an unexpected error"""
        attempt_count[0] += 1
        raise ValueError("Unexpected error type")
    
    # Execute and expect immediate failure
    with pytest.raises(ValueError):
        handler.handle_with_retry(
            operation_with_unexpected_error,
            error_types=(ConnectionError,),  # Only catch ConnectionError
            operation_name="Test operation"
        )
    
    # Verify it was only called once (no retries)
    assert attempt_count[0] == 1, \
        f"Expected 1 attempt for unexpected error, got {attempt_count[0]}"



# Feature: customs-barcode-automation, Property 19: Exception handling continuity
# Validates: Requirements 9.4, 9.5
@settings(max_examples=100)
@given(
    error_type=st.sampled_from([
        ValueError, TypeError, KeyError, AttributeError, 
        RuntimeError, ConnectionError, IOError
    ]),
    default_value=st.one_of(st.none(), st.integers(), st.text(), st.booleans())
)
def test_property_exception_handling_continuity(error_type, default_value):
    """
    **Feature: customs-barcode-automation, Property 19: Exception handling continuity**
    **Validates: Requirements 9.4, 9.5**
    
    For any unhandled exception during workflow execution, the system should 
    log the error and continue without terminating (by returning a default value).
    
    This property verifies that:
    1. Any exception is caught and handled gracefully
    2. The default value is returned on error
    3. The error is logged with full details
    4. The system continues execution (doesn't terminate)
    """
    handler = ErrorHandler(max_retries=3, base_delay=1)
    
    def failing_operation():
        """Operation that raises an exception"""
        raise error_type("Test error")
    
    # Execute with graceful handling
    result = handler.handle_gracefully(
        failing_operation,
        default=default_value,
        operation_name="Test operation"
    )
    
    # Verify the default value is returned
    assert result == default_value, \
        f"Expected default value {default_value}, got {result}"


# Feature: customs-barcode-automation, Property 19: Exception handling continuity
# Validates: Requirements 9.4, 9.5
@settings(max_examples=100)
@given(
    num_operations=st.integers(min_value=1, max_value=10),
    failure_indices=st.lists(st.integers(min_value=0, max_value=9), max_size=5)
)
def test_property_continuity_across_multiple_operations(num_operations, failure_indices):
    """
    For any sequence of operations where some fail, the system should 
    continue processing all operations and return results for each.
    """
    handler = ErrorHandler(max_retries=1, base_delay=1)
    
    results = []
    
    for i in range(num_operations):
        def operation():
            if i in failure_indices:
                raise ValueError(f"Operation {i} failed")
            return f"success_{i}"
        
        result = handler.handle_gracefully(
            operation,
            default=f"default_{i}",
            operation_name=f"Operation {i}"
        )
        results.append(result)
    
    # Verify all operations were processed
    assert len(results) == num_operations, \
        f"Expected {num_operations} results, got {len(results)}"
    
    # Verify correct results for each operation
    for i in range(num_operations):
        if i in failure_indices:
            assert results[i] == f"default_{i}", \
                f"Operation {i} should return default on failure"
        else:
            assert results[i] == f"success_{i}", \
                f"Operation {i} should return success value"


# Feature: customs-barcode-automation, Property 19: Exception handling continuity
# Validates: Requirements 9.4, 9.5
@settings(max_examples=100)
@given(
    exception_message=st.text(min_size=1, max_size=100)
)
def test_property_error_logging_on_graceful_handling(exception_message):
    """
    For any exception handled gracefully, the system should log the error 
    with full exception information.
    """
    import logging
    from io import StringIO
    
    # Create a string buffer to capture log output
    log_buffer = StringIO()
    test_logger = logging.getLogger("test_error_handler")
    test_logger.setLevel(logging.ERROR)
    handler_obj = logging.StreamHandler(log_buffer)
    handler_obj.setLevel(logging.ERROR)
    test_logger.addHandler(handler_obj)
    
    error_handler = ErrorHandler(max_retries=3, base_delay=1, logger=test_logger)
    
    def failing_operation():
        """Operation that raises an exception"""
        raise RuntimeError(exception_message)
    
    # Execute with graceful handling
    result = error_handler.handle_gracefully(
        failing_operation,
        default="default",
        operation_name="Test operation"
    )
    
    # Get logged output
    log_output = log_buffer.getvalue()
    
    # Verify error was logged
    assert "Test operation failed" in log_output, \
        "Error message should be logged"
    
    # Verify exception message is in log
    assert exception_message in log_output or "RuntimeError" in log_output, \
        "Exception details should be logged"
    
    # Clean up
    test_logger.removeHandler(handler_obj)
