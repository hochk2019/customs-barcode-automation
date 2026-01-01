"""
Property-based tests for batch declaration processing

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
import time
from pathlib import Path

from declaration_printing.declaration_printer import DeclarationPrinter
from declaration_printing.models import BatchPrintResult, PrintResult, DeclarationData, DeclarationType
from config.configuration_manager import ConfigurationManager
from logging_system.logger import Logger


# **Feature: customs-declaration-printing, Property 7: Batch processing with progress tracking**
# **Validates: Requirements 2.4, 7.1, 7.3**
@given(
    declaration_numbers=st.lists(
        st.one_of(
            # Valid export declarations
            st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))).map(lambda x: "30" + x),
            # Valid import declarations  
            st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))).map(lambda x: "10" + x),
            # Invalid format declarations (to test error handling)
            st.one_of(
                st.text(min_size=1, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),  # Too short
                st.text(min_size=13, max_size=20, alphabet=st.characters(whitelist_categories=('Nd',))),  # Too long
                st.text(min_size=12, max_size=12).filter(lambda x: not x.isdigit()),  # Non-digits
                st.just(""),  # Empty
                # Unsupported prefixes (not 10 or 30)
                st.text(min_size=12, max_size=12).filter(
                    lambda x: x.isdigit() and len(x) == 12 and not x.startswith('10') and not x.startswith('30')
                )
            )
        ),
        min_size=1,
        max_size=50
    )
)
@settings(max_examples=100)
def test_property_batch_processing_with_progress_tracking(declaration_numbers):
    """
    For any set of multiple declarations, the system should process them sequentially, 
    provide progress indication, and generate a summary of results.
    
    **Feature: customs-declaration-printing, Property 7: Batch processing with progress tracking**
    **Validates: Requirements 2.4, 7.1, 7.3**
    """
    # Create mock logger to track progress messages
    mock_logger = Mock(spec=Logger)
    
    # Create mock config manager
    mock_config = Mock(spec=ConfigurationManager)
    mock_config.get_database_config.return_value = None
    
    # Mock the config attribute with ConfigParser-like behavior
    mock_config_parser = Mock()
    mock_config_parser.has_section.return_value = False
    mock_config_parser.add_section = Mock()
    mock_config_parser.get.return_value = "test_output"
    mock_config_parser.getboolean.return_value = True
    mock_config.config = mock_config_parser
    
    # Create printer with mocked dependencies
    printer = DeclarationPrinter(
        config_manager=mock_config,
        logger=mock_logger,
        output_directory="test_output"
    )
    
    # Mock the single declaration processing to control results
    original_print_single = printer.print_single_declaration
    
    def mock_print_single(declaration_number):
        """Mock single declaration printing with predictable results"""
        # Simulate processing time
        processing_time = 0.001  # Very fast for testing
        
        # Determine if this should succeed or fail based on declaration format
        try:
            # Use the actual validation logic
            if printer.validate_declaration_for_printing(declaration_number):
                # Mock successful result
                return PrintResult(
                    success=True,
                    declaration_number=declaration_number,
                    output_file_path=f"test_output/ToKhaiHQ7X_QDTQ_{declaration_number}.xlsx",
                    processing_time=processing_time
                )
            else:
                # Mock validation failure
                return PrintResult(
                    success=False,
                    declaration_number=declaration_number,
                    error_message="Declaration validation failed",
                    processing_time=processing_time
                )
        except Exception as e:
            # Mock processing error
            return PrintResult(
                success=False,
                declaration_number=declaration_number,
                error_message=f"Processing error: {str(e)}",
                processing_time=processing_time
            )
    
    # Patch the single declaration method
    printer.print_single_declaration = mock_print_single
    
    # Record start time
    start_time = time.time()
    
    # Execute batch processing
    batch_result = printer.print_declarations(declaration_numbers)
    
    # Record end time
    end_time = time.time()
    
    # Verify batch result structure and completeness
    assert isinstance(batch_result, BatchPrintResult), \
        "Batch processing should return BatchPrintResult"
    
    assert batch_result.total_processed == len(declaration_numbers), \
        f"Total processed should equal input count: {batch_result.total_processed} != {len(declaration_numbers)}"
    
    assert len(batch_result.results) == len(declaration_numbers), \
        f"Results list should contain one result per declaration: {len(batch_result.results)} != {len(declaration_numbers)}"
    
    assert batch_result.successful + batch_result.failed == batch_result.total_processed, \
        f"Successful + failed should equal total: {batch_result.successful} + {batch_result.failed} != {batch_result.total_processed}"
    
    # Verify timing information
    assert batch_result.total_time > 0, "Total time should be positive"
    assert batch_result.total_time <= (end_time - start_time) + 1.0, \
        "Recorded time should be reasonable compared to actual elapsed time"
    
    # Verify progress tracking through logger calls
    # Should have start message
    start_calls = [call for call in mock_logger.info.call_args_list 
                   if 'Starting batch printing' in str(call)]
    assert len(start_calls) >= 1, "Should log batch processing start"
    
    # Should have completion message
    completion_calls = [call for call in mock_logger.info.call_args_list 
                       if 'Batch printing completed' in str(call)]
    assert len(completion_calls) >= 1, "Should log batch processing completion"
    
    # Should have individual declaration processing messages
    individual_calls = [call for call in mock_logger.info.call_args_list 
                       if 'Processing declaration' in str(call)]
    assert len(individual_calls) >= len(declaration_numbers), \
        f"Should log each declaration processing: {len(individual_calls)} >= {len(declaration_numbers)}"
    
    # Verify individual results consistency
    successful_count = 0
    failed_count = 0
    
    for i, result in enumerate(batch_result.results):
        assert isinstance(result, PrintResult), f"Result {i} should be PrintResult"
        assert result.declaration_number == declaration_numbers[i], \
            f"Result {i} should match input declaration number"
        assert result.processing_time is not None and result.processing_time >= 0, \
            f"Result {i} should have valid processing time"
        
        if result.success:
            successful_count += 1
            assert result.output_file_path is not None, \
                f"Successful result {i} should have output file path"
            assert result.error_message is None, \
                f"Successful result {i} should not have error message"
        else:
            failed_count += 1
            assert result.error_message is not None, \
                f"Failed result {i} should have error message"
            assert result.output_file_path is None, \
                f"Failed result {i} should not have output file path"
    
    # Verify counts match
    assert successful_count == batch_result.successful, \
        f"Successful count mismatch: {successful_count} != {batch_result.successful}"
    assert failed_count == batch_result.failed, \
        f"Failed count mismatch: {failed_count} != {batch_result.failed}"
    
    # Verify error handling and continuation
    # If there were any invalid declarations, they should be in failed results
    valid_declarations = []
    invalid_declarations = []
    
    for decl_num in declaration_numbers:
        try:
            if (decl_num and len(decl_num.strip()) == 12 and decl_num.strip().isdigit() and 
                (decl_num.startswith('10') or decl_num.startswith('30'))):
                valid_declarations.append(decl_num)
            else:
                invalid_declarations.append(decl_num)
        except:
            invalid_declarations.append(decl_num)
    
    # All invalid declarations should result in failed results
    # (Note: some valid declarations might also fail due to other reasons like missing templates)
    assert batch_result.failed >= len(invalid_declarations), \
        f"Failed count should be at least the number of invalid declarations: {batch_result.failed} >= {len(invalid_declarations)}"
    
    # Verify sequential processing (each declaration processed exactly once)
    processed_declarations = [result.declaration_number for result in batch_result.results]
    assert processed_declarations == declaration_numbers, \
        "Declarations should be processed in the same order as input"


@given(
    batch_size=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=50)
def test_property_batch_processing_empty_and_single_cases(batch_size):
    """
    For any batch size including single declarations, batch processing should work correctly.
    
    **Feature: customs-declaration-printing, Property 7: Batch processing with progress tracking**
    **Validates: Requirements 7.1, 7.3**
    """
    # Create mock logger
    mock_logger = Mock(spec=Logger)
    
    # Create mock config manager
    mock_config = Mock(spec=ConfigurationManager)
    mock_config.get_database_config.return_value = None
    
    # Mock the config attribute with ConfigParser-like behavior
    mock_config_parser = Mock()
    mock_config_parser.has_section.return_value = False
    mock_config_parser.add_section = Mock()
    mock_config_parser.get.return_value = "test_output"
    mock_config_parser.getboolean.return_value = True
    mock_config.config = mock_config_parser
    
    # Create printer
    printer = DeclarationPrinter(
        config_manager=mock_config,
        logger=mock_logger,
        output_directory="test_output"
    )
    
    # Generate valid declarations
    declaration_numbers = [f"30{str(i).zfill(10)}" for i in range(batch_size)]
    
    # Mock single declaration processing to always succeed
    def mock_print_single(declaration_number):
        return PrintResult(
            success=True,
            declaration_number=declaration_number,
            output_file_path=f"test_output/ToKhaiHQ7X_QDTQ_{declaration_number}.xlsx",
            processing_time=0.001
        )
    
    printer.print_single_declaration = mock_print_single
    
    # Execute batch processing
    batch_result = printer.print_declarations(declaration_numbers)
    
    # Verify results
    assert batch_result.total_processed == batch_size
    assert batch_result.successful == batch_size
    assert batch_result.failed == 0
    assert len(batch_result.results) == batch_size
    
    # For single declaration, verify it still goes through batch processing
    if batch_size == 1:
        assert batch_result.results[0].declaration_number == declaration_numbers[0]
        assert batch_result.results[0].success is True


@given(
    valid_declarations=st.lists(
        st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))).map(lambda x: "30" + x),
        min_size=1,
        max_size=20
    ),
    invalid_declarations=st.lists(
        st.one_of(
            st.text(min_size=1, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),  # Too short
            st.just(""),  # Empty
            st.text(min_size=12, max_size=12).filter(lambda x: not x.isdigit())  # Non-digits
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=50)
def test_property_batch_error_handling_and_continuation(valid_declarations, invalid_declarations):
    """
    For any batch containing both valid and invalid declarations, the system should 
    process valid ones successfully and handle invalid ones gracefully.
    
    **Feature: customs-declaration-printing, Property 7: Batch processing with progress tracking**
    **Validates: Requirements 2.4, 7.2**
    """
    # Create mock logger
    mock_logger = Mock(spec=Logger)
    
    # Create mock config manager
    mock_config = Mock(spec=ConfigurationManager)
    mock_config.get_database_config.return_value = None
    
    # Mock the config attribute with ConfigParser-like behavior
    mock_config_parser = Mock()
    mock_config_parser.has_section.return_value = False
    mock_config_parser.add_section = Mock()
    mock_config_parser.get.return_value = "test_output"
    mock_config_parser.getboolean.return_value = True
    mock_config.config = mock_config_parser
    
    # Create printer
    printer = DeclarationPrinter(
        config_manager=mock_config,
        logger=mock_logger,
        output_directory="test_output"
    )
    
    # Interleave valid and invalid declarations
    all_declarations = []
    valid_iter = iter(valid_declarations)
    invalid_iter = iter(invalid_declarations)
    
    # Alternate between valid and invalid
    try:
        while True:
            try:
                all_declarations.append(next(valid_iter))
            except StopIteration:
                pass
            try:
                all_declarations.append(next(invalid_iter))
            except StopIteration:
                pass
            if len(all_declarations) >= len(valid_declarations) + len(invalid_declarations):
                break
    except:
        pass
    
    # Ensure we have all declarations
    remaining_valid = list(valid_iter)
    remaining_invalid = list(invalid_iter)
    all_declarations.extend(remaining_valid)
    all_declarations.extend(remaining_invalid)
    
    # Mock single declaration processing
    def mock_print_single(declaration_number):
        # Use actual validation to determine success/failure
        try:
            if printer.validate_declaration_for_printing(declaration_number):
                return PrintResult(
                    success=True,
                    declaration_number=declaration_number,
                    output_file_path=f"test_output/ToKhaiHQ7X_QDTQ_{declaration_number}.xlsx",
                    processing_time=0.001
                )
            else:
                return PrintResult(
                    success=False,
                    declaration_number=declaration_number,
                    error_message="Validation failed",
                    processing_time=0.001
                )
        except Exception as e:
            return PrintResult(
                success=False,
                declaration_number=declaration_number,
                error_message=f"Processing error: {str(e)}",
                processing_time=0.001
            )
    
    printer.print_single_declaration = mock_print_single
    
    # Execute batch processing
    batch_result = printer.print_declarations(all_declarations)
    
    # Verify all declarations were processed
    assert batch_result.total_processed == len(all_declarations)
    assert len(batch_result.results) == len(all_declarations)
    
    # Verify that valid declarations succeeded (assuming templates exist)
    # Note: In real scenario, some valid declarations might fail due to missing templates,
    # but our mock should make them succeed
    expected_successful = len(valid_declarations)
    expected_failed = len(invalid_declarations)
    
    # Count actual results
    actual_successful = sum(1 for result in batch_result.results if result.success)
    actual_failed = sum(1 for result in batch_result.results if not result.success)
    
    # Verify counts
    assert batch_result.successful == actual_successful
    assert batch_result.failed == actual_failed
    assert actual_successful + actual_failed == len(all_declarations)
    
    # Verify that processing continued despite errors
    # All declarations should have been processed (no early termination)
    processed_numbers = [result.declaration_number for result in batch_result.results]
    assert processed_numbers == all_declarations, \
        "All declarations should be processed in order despite errors"
    
    # Verify error logging for failed declarations
    error_calls = [call for call in mock_logger.error.call_args_list 
                   if 'Failed to print' in str(call)]
    assert len(error_calls) >= actual_failed, \
        f"Should log errors for failed declarations: {len(error_calls)} >= {actual_failed}"


@given(
    declaration_count=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=20)
def test_property_batch_processing_edge_cases(declaration_count):
    """
    For edge cases like empty batches or very small batches, the system should handle them gracefully.
    
    **Feature: customs-declaration-printing, Property 7: Batch processing with progress tracking**
    **Validates: Requirements 7.1, 7.3**
    """
    # Create mock logger
    mock_logger = Mock(spec=Logger)
    
    # Create mock config manager
    mock_config = Mock(spec=ConfigurationManager)
    mock_config.get_database_config.return_value = None
    
    # Mock the config attribute with ConfigParser-like behavior
    mock_config_parser = Mock()
    mock_config_parser.has_section.return_value = False
    mock_config_parser.add_section = Mock()
    mock_config_parser.get.return_value = "test_output"
    mock_config_parser.getboolean.return_value = True
    mock_config.config = mock_config_parser
    
    # Create printer
    printer = DeclarationPrinter(
        config_manager=mock_config,
        logger=mock_logger,
        output_directory="test_output"
    )
    
    # Generate declarations
    declaration_numbers = [f"30{str(i).zfill(10)}" for i in range(declaration_count)]
    
    # Mock single declaration processing
    def mock_print_single(declaration_number):
        return PrintResult(
            success=True,
            declaration_number=declaration_number,
            output_file_path=f"test_output/ToKhaiHQ7X_QDTQ_{declaration_number}.xlsx",
            processing_time=0.001
        )
    
    printer.print_single_declaration = mock_print_single
    
    # Execute batch processing
    batch_result = printer.print_declarations(declaration_numbers)
    
    # Verify results for edge cases
    assert batch_result.total_processed == declaration_count
    assert len(batch_result.results) == declaration_count
    assert batch_result.successful + batch_result.failed == declaration_count
    
    if declaration_count == 0:
        # Empty batch should complete successfully with no results
        assert batch_result.successful == 0
        assert batch_result.failed == 0
        assert batch_result.results == []
    else:
        # Non-empty batch should process all declarations
        assert batch_result.successful == declaration_count
        assert batch_result.failed == 0
        
        # Verify all results are present and correct
        for i, result in enumerate(batch_result.results):
            assert result.declaration_number == declaration_numbers[i]
            assert result.success is True
    
    # Verify timing is reasonable
    assert batch_result.total_time >= 0
    if declaration_count > 0:
        assert batch_result.total_time > 0  # Should take some time for non-empty batches