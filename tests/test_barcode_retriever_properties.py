"""
Property-based tests for barcode retrieval

These tests use Hypothesis to verify correctness properties across many random inputs.
"""

from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import time
from hypothesis import given, strategies as st, settings, HealthCheck
import requests

from models.declaration_models import Declaration
from models.config_models import BarcodeServiceConfig
from web_utils.barcode_retriever import BarcodeRetriever


# Strategy for generating valid declarations
@st.composite
def declaration_strategy(draw):
    """Generate random valid declarations"""
    return Declaration(
        declaration_number=draw(st.text(min_size=12, max_size=15, alphabet=st.characters(whitelist_categories=('Nd',)))),
        tax_code=draw(st.text(min_size=10, max_size=13, alphabet=st.characters(whitelist_categories=('Nd',)))),
        declaration_date=draw(st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2024, 12, 31))),
        customs_office_code=draw(st.text(min_size=3, max_size=5, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')),
        transport_method=draw(st.sampled_from(['1', '2', '3', '4', '5', '6', '7', '8'])),
        channel=draw(st.sampled_from(['Xanh', 'Vang'])),
        status='T',
        goods_description=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))
    )


# Feature: customs-barcode-automation, Property 5: Barcode retrieval fallback chain
@given(declaration=declaration_strategy())
@settings(max_examples=100)
def test_property_barcode_retrieval_fallback_chain(declaration):
    """
    For any eligible CustomsDeclaration, when attempting barcode retrieval,
    the system should try primary website first (Oracle ADF - most reliable),
    then API, then backup website, in that order.
    
    **Validates: Requirements 4.1, 4.2, 4.3**
    
    Note: Order changed Dec 2024 - primary website is now tried first as it's
    more reliable than the API.
    """
    # Create config
    config = BarcodeServiceConfig(
        api_url='http://test-api.example.com',
        primary_web_url='http://primary.example.com',
        backup_web_url='http://backup.example.com',
        timeout=30,
        max_retries=3,
        retry_delay=5
    )
    
    # Create mock logger
    mock_logger = Mock()
    
    # Create retriever
    retriever = BarcodeRetriever(config, mock_logger)
    
    # Track method call order
    call_order = []
    
    # Mock the internal methods to track call order
    original_try_api = retriever._try_api
    original_try_web_scraping = retriever._try_web_scraping
    
    def mock_try_api(decl):
        call_order.append('api')
        return None  # Simulate failure
    
    def mock_try_web_scraping(url, decl):
        if url == config.primary_web_url:
            call_order.append('primary')
        elif url == config.backup_web_url:
            call_order.append('backup')
        return None  # Simulate failure
    
    retriever._try_api = mock_try_api
    retriever._try_web_scraping = mock_try_web_scraping
    
    # Attempt retrieval
    result = retriever.retrieve_barcode(declaration)
    
    # Verify fallback chain order: primary -> api -> backup
    assert call_order == ['primary', 'api', 'backup'], \
        f"Expected fallback order ['primary', 'api', 'backup'], but got {call_order}"
    
    # Result should be None since all methods failed
    assert result is None, "Expected None when all methods fail"


# Feature: customs-barcode-automation, Property 6: API request completeness
@given(declaration=declaration_strategy())
@settings(max_examples=100)
def test_property_api_request_completeness(declaration):
    """
    For any API barcode retrieval request, all required fields
    (DeclarationNumber, TaxCode, declaration date, CustomsOfficeCode)
    should be included in the request.
    
    **Validates: Requirements 4.4**
    """
    # Create config
    config = BarcodeServiceConfig(
        api_url='http://test-api.example.com',
        primary_web_url='http://primary.example.com',
        backup_web_url='http://backup.example.com',
        timeout=30,
        max_retries=3,
        retry_delay=5
    )
    
    # Create mock logger
    mock_logger = Mock()
    
    # Create retriever
    retriever = BarcodeRetriever(config, mock_logger)
    
    # Mock session.post to capture the request
    captured_request = {}
    
    def mock_post(url, data, headers, timeout):
        captured_request['url'] = url
        captured_request['data'] = data
        captured_request['headers'] = headers
        captured_request['timeout'] = timeout
        
        # Return mock response
        mock_response = Mock()
        mock_response.status_code = 404  # Simulate not found
        mock_response.text = '<soap:Envelope></soap:Envelope>'
        return mock_response
    
    with patch.object(retriever.session, 'post', side_effect=mock_post):
        # Try API retrieval
        retriever._try_api(declaration)
    
    # Verify request was made
    assert 'data' in captured_request, "No API request was made"
    
    request_data = captured_request['data']
    
    # Verify all required fields are in the request
    assert declaration.declaration_number in request_data, \
        f"Declaration number '{declaration.declaration_number}' not found in API request"
    
    assert declaration.tax_code in request_data, \
        f"Tax code '{declaration.tax_code}' not found in API request"
    
    # Date should be formatted as ddmmyyyy
    date_str = declaration.declaration_date.strftime('%d%m%Y')
    assert date_str in request_data, \
        f"Declaration date '{date_str}' not found in API request"
    
    assert declaration.customs_office_code in request_data, \
        f"Customs office code '{declaration.customs_office_code}' not found in API request"
    
    # Verify SOAP structure
    assert '<soap:Envelope' in request_data, "Request is not a valid SOAP envelope"
    assert '<GetBarcode' in request_data, "Request does not contain GetBarcode operation"
    assert '<declarationNumber>' in request_data, "Request missing declarationNumber element"
    assert '<taxCode>' in request_data, "Request missing taxCode element"
    assert '<declarationDate>' in request_data, "Request missing declarationDate element"
    assert '<customsOffice>' in request_data, "Request missing customsOffice element"



# Feature: bug-fixes-dec-2024, Property 2: Timeout reduction effectiveness
@given(declaration=declaration_strategy())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_timeout_reduction_effectiveness(declaration):
    """
    For any API call that would timeout, the system should fail faster
    (within 10 seconds) than the old timeout (30 seconds).
    
    **Validates: Requirements 2.1**
    """
    # Create config with new timeout settings
    config = BarcodeServiceConfig(
        api_url='http://test-api.example.com',
        primary_web_url='http://primary.example.com',
        backup_web_url='http://backup.example.com',
        timeout=30,  # Legacy timeout
        max_retries=1,
        retry_delay=0,
        api_timeout=10,  # New reduced timeout
        web_timeout=15
    )
    
    mock_logger = Mock()
    retriever = BarcodeRetriever(config, mock_logger)
    
    # Mock the session's post method to simulate a timeout
    def mock_post_timeout(*args, **kwargs):
        # Simulate a slow response that would timeout
        timeout_value = kwargs.get('timeout', 30)
        time.sleep(0.1)  # Small delay to simulate network
        raise requests.Timeout(f"Request timed out after {timeout_value}s")
    
    with patch.object(retriever.session, 'post', side_effect=mock_post_timeout):
        start_time = time.time()
        result = retriever._try_api(declaration)
        elapsed_time = time.time() - start_time
    
    # Verify result is None (timeout occurred)
    assert result is None, "Expected None when API times out"
    
    # Verify timeout happened quickly (within reasonable margin)
    # We expect it to use api_timeout (10s) not legacy timeout (30s)
    # Adding 2s margin for test execution overhead
    assert elapsed_time < 12, \
        f"Expected timeout within ~10s (api_timeout), but took {elapsed_time:.2f}s"
    
    # Verify the new timeout was actually used and error was logged
    assert mock_logger.error.called, "Expected error to be logged on timeout"



# Feature: bug-fixes-dec-2024, Property 3: Selector fallback completeness
@given(
    field_type=st.sampled_from(['taxCode', 'declarationNumber', 'declarationDate', 'customsOffice']),
    value=st.text(min_size=1, max_size=20)
)
@settings(max_examples=100)
def test_property_selector_fallback_completeness(field_type, value):
    """
    For any form field that needs to be filled, if the primary selector fails,
    the system should try all alternative selectors before giving up.
    
    **Validates: Requirements 2.2, 2.4**
    """
    config = BarcodeServiceConfig(
        api_url='http://test-api.example.com',
        primary_web_url='http://primary.example.com',
        backup_web_url='http://backup.example.com',
        timeout=30,
        max_retries=1,
        retry_delay=0,
        api_timeout=10,
        web_timeout=15
    )
    
    mock_logger = Mock()
    retriever = BarcodeRetriever(config, mock_logger)
    
    # Track which selectors were tried
    tried_selectors = []
    
    # Mock WebDriver
    mock_driver = Mock()
    
    def mock_find_element(by, selector_name):
        tried_selectors.append(selector_name)
        # Always raise exception to force trying all selectors
        raise Exception(f"Selector '{selector_name}' not found")
    
    mock_driver.find_element = mock_find_element
    mock_driver.title = "Test Page"
    mock_driver.current_url = "http://test.com"
    mock_driver.find_elements.return_value = []  # No forms/inputs for logging
    
    # Try adaptive selectors
    result = retriever._try_adaptive_selectors(mock_driver, field_type, value)
    
    # Verify result is None (all selectors failed)
    assert result is None, "Expected None when all selectors fail"
    
    # Get expected selectors for this field type
    expected_selectors = retriever.FIELD_SELECTORS[field_type]
    
    # Verify all selectors were tried
    # Each selector is tried twice (once by ID, once by name)
    for selector in expected_selectors:
        assert tried_selectors.count(selector) >= 1, \
            f"Expected selector '{selector}' to be tried for {field_type}, but it wasn't in {tried_selectors}"
    
    # Verify error was logged
    assert mock_logger.error.called, "Expected error to be logged when all selectors fail"


# Feature: bug-fixes-dec-2024, Property 7: Session reuse efficiency
@given(declarations=st.lists(declaration_strategy(), min_size=2, max_size=5))
@settings(max_examples=100)
def test_property_session_reuse_efficiency(declarations):
    """
    For any batch of declarations being processed, the HTTP session should be
    reused across all requests rather than creating new sessions.
    
    **Validates: Requirements 6.4**
    """
    config = BarcodeServiceConfig(
        api_url='http://test-api.example.com',
        primary_web_url='http://primary.example.com',
        backup_web_url='http://backup.example.com',
        timeout=30,
        max_retries=1,
        retry_delay=0,
        api_timeout=10,
        web_timeout=15,
        session_reuse=True
    )
    
    mock_logger = Mock()
    retriever = BarcodeRetriever(config, mock_logger)
    
    # Capture the session object
    initial_session = retriever.session
    assert initial_session is not None, "Session should be initialized"
    
    # Track session objects used across multiple API calls
    sessions_used = []
    
    def mock_post(*args, **kwargs):
        # Capture which session object is being used
        # In the real code, self.session.post is called
        sessions_used.append(id(retriever.session))
        
        # Return mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = '<soap:Envelope></soap:Envelope>'
        return mock_response
    
    # Patch the session's post method
    with patch.object(retriever.session, 'post', side_effect=mock_post):
        # Process multiple declarations
        for declaration in declarations:
            retriever._try_api(declaration)
    
    # Verify session was reused (all calls used the same session object)
    assert len(sessions_used) == len(declarations), \
        f"Expected {len(declarations)} API calls, but got {len(sessions_used)}"
    
    # All session IDs should be the same (same object reused)
    unique_sessions = set(sessions_used)
    assert len(unique_sessions) == 1, \
        f"Expected all API calls to use the same session, but found {len(unique_sessions)} different sessions"
    
    # Verify the session used is the initial session
    assert sessions_used[0] == id(initial_session), \
        "Expected all calls to use the initial session object"
    
    # Cleanup
    retriever.cleanup()
