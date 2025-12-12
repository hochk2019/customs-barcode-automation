"""
Unit tests for ErrorHandler.

These tests verify specific examples and edge cases for error handling functionality.
"""

import time
import pytest
import logging
from error_handling.error_handler import ErrorHandler, ErrorCategory


class TestErrorHandlerRetry:
    """Test retry logic with exponential backoff."""
    
    def test_retry_succeeds_on_first_attempt(self):
        """Test that successful operations don't retry."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_count = [0]
        
        def successful_operation():
            call_count[0] += 1
            return "success"
        
        result = handler.handle_with_retry(successful_operation)
        
        assert result == "success"
        assert call_count[0] == 1
    
    def test_retry_fails_after_max_retries(self):
        """Test that operation fails after max retries."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_count = [0]
        
        def failing_operation():
            call_count[0] += 1
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            handler.handle_with_retry(
                failing_operation,
                error_types=(ConnectionError,)
            )
        
        assert call_count[0] == 3
    
    def test_retry_exponential_backoff_timing(self):
        """Test that delays follow exponential backoff pattern."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_times = []
        
        def failing_operation():
            call_times.append(time.time())
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            handler.handle_with_retry(
                failing_operation,
                error_types=(ConnectionError,)
            )
        
        # Verify delays: 1s, 2s, 4s
        assert len(call_times) == 3
        
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        # Allow 10% tolerance
        assert 0.9 <= delay1 <= 1.1, f"First delay should be ~1s, got {delay1:.2f}s"
        assert 1.8 <= delay2 <= 2.2, f"Second delay should be ~2s, got {delay2:.2f}s"
    
    def test_retry_succeeds_on_second_attempt(self):
        """Test that operation succeeds if it works before max retries."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_count = [0]
        
        def eventually_succeeding_operation():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Network error")
            return "success"
        
        result = handler.handle_with_retry(
            eventually_succeeding_operation,
            error_types=(ConnectionError,)
        )
        
        assert result == "success"
        assert call_count[0] == 2
    
    def test_retry_only_catches_specified_errors(self):
        """Test that unexpected errors are not retried."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_count = [0]
        
        def operation_with_unexpected_error():
            call_count[0] += 1
            raise ValueError("Unexpected error")
        
        with pytest.raises(ValueError):
            handler.handle_with_retry(
                operation_with_unexpected_error,
                error_types=(ConnectionError,)
            )
        
        # Should only be called once (no retries)
        assert call_count[0] == 1
    
    def test_retry_with_multiple_error_types(self):
        """Test that multiple error types can be caught."""
        handler = ErrorHandler(max_retries=3, base_delay=1)
        
        call_count = [0]
        
        def operation_with_various_errors():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ConnectionError("Network error")
            elif call_count[0] == 2:
                raise TimeoutError("Timeout")
            return "success"
        
        result = handler.handle_with_retry(
            operation_with_various_errors,
            error_types=(ConnectionError, TimeoutError)
        )
        
        assert result == "success"
        assert call_count[0] == 3


class TestErrorHandlerGraceful:
    """Test graceful error handling."""
    
    def test_graceful_returns_default_on_error(self):
        """Test that default value is returned on error."""
        handler = ErrorHandler()
        
        def failing_operation():
            raise RuntimeError("Error")
        
        result = handler.handle_gracefully(
            failing_operation,
            default="default_value"
        )
        
        assert result == "default_value"
    
    def test_graceful_returns_result_on_success(self):
        """Test that result is returned on success."""
        handler = ErrorHandler()
        
        def successful_operation():
            return "success"
        
        result = handler.handle_gracefully(
            successful_operation,
            default="default_value"
        )
        
        assert result == "success"
    
    def test_graceful_returns_none_by_default(self):
        """Test that None is returned when no default is specified."""
        handler = ErrorHandler()
        
        def failing_operation():
            raise RuntimeError("Error")
        
        result = handler.handle_gracefully(failing_operation)
        
        assert result is None
    
    def test_graceful_handles_any_exception(self):
        """Test that any exception is handled gracefully."""
        handler = ErrorHandler()
        
        exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            KeyError("Key error"),
            AttributeError("Attribute error"),
            RuntimeError("Runtime error")
        ]
        
        for exc in exceptions:
            def failing_operation():
                raise exc
            
            result = handler.handle_gracefully(
                failing_operation,
                default="default"
            )
            
            assert result == "default"


class TestErrorCategorization:
    """Test error categorization."""
    
    def test_categorize_database_errors(self):
        """Test that database errors are categorized correctly."""
        handler = ErrorHandler()
        
        # Test by error message
        db_error = Exception("Database connection failed")
        category = handler.categorize_error(db_error)
        assert category == ErrorCategory.DATABASE
        
        sql_error = Exception("SQL query failed")
        category = handler.categorize_error(sql_error)
        assert category == ErrorCategory.DATABASE
    
    def test_categorize_network_errors(self):
        """Test that network errors are categorized correctly."""
        handler = ErrorHandler()
        
        network_errors = [
            ConnectionError("Connection refused"),
            TimeoutError("Request timeout"),
            Exception("ssl certificate error")
        ]
        
        for error in network_errors:
            category = handler.categorize_error(error)
            assert category == ErrorCategory.NETWORK
    
    def test_categorize_file_system_errors(self):
        """Test that file system errors are categorized correctly."""
        handler = ErrorHandler()
        
        fs_errors = [
            FileNotFoundError("File not found"),
            PermissionError("Permission denied"),
            IOError("Disk full"),
            Exception("path does not exist")
        ]
        
        for error in fs_errors:
            category = handler.categorize_error(error)
            assert category == ErrorCategory.FILE_SYSTEM
    
    def test_categorize_data_errors(self):
        """Test that data errors are categorized correctly."""
        handler = ErrorHandler()
        
        data_errors = [
            ValueError("Invalid value"),
            TypeError("Wrong type"),
            KeyError("Missing key"),
            Exception("invalid format")
        ]
        
        for error in data_errors:
            category = handler.categorize_error(error)
            assert category == ErrorCategory.DATA
    
    def test_categorize_configuration_errors(self):
        """Test that configuration errors are categorized correctly."""
        handler = ErrorHandler()
        
        config_error = Exception("configuration missing")
        category = handler.categorize_error(config_error)
        assert category == ErrorCategory.CONFIGURATION
    
    def test_categorize_unknown_errors(self):
        """Test that unknown errors are categorized as UNKNOWN."""
        handler = ErrorHandler()
        
        unknown_error = Exception("Some random error")
        category = handler.categorize_error(unknown_error)
        assert category == ErrorCategory.UNKNOWN


class TestErrorLogging:
    """Test error logging functionality."""
    
    def test_log_error_with_category(self):
        """Test that errors are logged with their category."""
        import logging
        from io import StringIO
        
        # Create a string buffer to capture log output
        log_buffer = StringIO()
        test_logger = logging.getLogger("test_error_handler")
        test_logger.setLevel(logging.ERROR)
        handler_obj = logging.StreamHandler(log_buffer)
        handler_obj.setLevel(logging.ERROR)
        test_logger.addHandler(handler_obj)
        
        error_handler = ErrorHandler(logger=test_logger)
        
        # Log a network error
        error = ConnectionError("Network timeout")
        error_handler.log_error_with_category(error, context="API call")
        
        log_output = log_buffer.getvalue()
        
        # Verify category is in log
        assert "[NETWORK]" in log_output
        assert "API call" in log_output
        assert "Network timeout" in log_output
        
        # Clean up
        test_logger.removeHandler(handler_obj)
    
    def test_retry_logs_warnings(self):
        """Test that retry attempts are logged as warnings."""
        import logging
        from io import StringIO
        
        # Create a string buffer to capture log output
        log_buffer = StringIO()
        test_logger = logging.getLogger("test_retry_logger")
        test_logger.setLevel(logging.WARNING)
        handler_obj = logging.StreamHandler(log_buffer)
        handler_obj.setLevel(logging.WARNING)
        test_logger.addHandler(handler_obj)
        
        error_handler = ErrorHandler(max_retries=2, base_delay=1, logger=test_logger)
        
        call_count = [0]
        
        def failing_operation():
            call_count[0] += 1
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            error_handler.handle_with_retry(
                failing_operation,
                error_types=(ConnectionError,),
                operation_name="Test operation"
            )
        
        log_output = log_buffer.getvalue()
        
        # Verify retry warnings are logged
        assert "Test operation attempt 1 failed" in log_output
        assert "Retrying in" in log_output
        
        # Clean up
        test_logger.removeHandler(handler_obj)
    
    def test_graceful_logs_errors(self):
        """Test that graceful handling logs errors."""
        import logging
        from io import StringIO
        
        # Create a string buffer to capture log output
        log_buffer = StringIO()
        test_logger = logging.getLogger("test_graceful_logger")
        test_logger.setLevel(logging.ERROR)
        handler_obj = logging.StreamHandler(log_buffer)
        handler_obj.setLevel(logging.ERROR)
        test_logger.addHandler(handler_obj)
        
        error_handler = ErrorHandler(logger=test_logger)
        
        def failing_operation():
            raise RuntimeError("Test error")
        
        error_handler.handle_gracefully(
            failing_operation,
            default="default",
            operation_name="Test operation"
        )
        
        log_output = log_buffer.getvalue()
        
        # Verify error is logged
        assert "Test operation failed" in log_output
        assert "Test error" in log_output
        
        # Clean up
        test_logger.removeHandler(handler_obj)


class TestErrorHandlerConfiguration:
    """Test ErrorHandler configuration."""
    
    def test_custom_max_retries(self):
        """Test that custom max_retries is respected."""
        handler = ErrorHandler(max_retries=5, base_delay=1)
        
        call_count = [0]
        
        def failing_operation():
            call_count[0] += 1
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            handler.handle_with_retry(
                failing_operation,
                error_types=(ConnectionError,)
            )
        
        assert call_count[0] == 5
    
    def test_custom_base_delay(self):
        """Test that custom base_delay is used for backoff."""
        handler = ErrorHandler(max_retries=2, base_delay=2)
        
        call_times = []
        
        def failing_operation():
            call_times.append(time.time())
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            handler.handle_with_retry(
                failing_operation,
                error_types=(ConnectionError,)
            )
        
        # Verify first delay is ~2s (base_delay * 2^0)
        delay1 = call_times[1] - call_times[0]
        assert 1.8 <= delay1 <= 2.2, f"First delay should be ~2s, got {delay1:.2f}s"
    
    def test_custom_logger(self):
        """Test that custom logger is used."""
        import logging
        from io import StringIO
        
        log_buffer = StringIO()
        custom_logger = logging.getLogger("custom_logger")
        custom_logger.setLevel(logging.ERROR)
        handler_obj = logging.StreamHandler(log_buffer)
        handler_obj.setLevel(logging.ERROR)
        custom_logger.addHandler(handler_obj)
        
        error_handler = ErrorHandler(logger=custom_logger)
        
        def failing_operation():
            raise RuntimeError("Test error")
        
        error_handler.handle_gracefully(failing_operation)
        
        log_output = log_buffer.getvalue()
        assert "Test error" in log_output
        
        # Clean up
        custom_logger.removeHandler(handler_obj)
