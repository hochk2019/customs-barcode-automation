"""
Unit tests for BarcodeRetriever

These tests verify specific examples and edge cases for barcode retrieval.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import base64

from models.declaration_models import Declaration
from models.config_models import BarcodeServiceConfig
from web_utils.barcode_retriever import BarcodeRetriever


class TestBarcodeRetriever:
    """Unit tests for BarcodeRetriever class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = BarcodeServiceConfig(
            api_url='http://test-api.example.com/QRCode.asmx',
            primary_web_url='http://primary.example.com',
            backup_web_url='http://backup.example.com',
            timeout=30,
            max_retries=3,
            retry_delay=5
        )
        self.mock_logger = Mock()
        self.retriever = BarcodeRetriever(self.config, self.mock_logger)
        
        self.test_declaration = Declaration(
            declaration_number='308010891440',
            tax_code='2300782217',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description='Normal goods'
        )
    
    def test_api_request_building(self):
        """Test that API request is built correctly with all required fields"""
        with patch.object(self.retriever.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = '<soap:Envelope></soap:Envelope>'
            mock_post.return_value = mock_response
            
            self.retriever._try_api(self.test_declaration)
            
            # Verify post was called
            assert mock_post.called
            
            # Get the call arguments
            call_args = mock_post.call_args
            
            # Verify URL
            assert call_args[0][0] == self.config.api_url
            
            # Verify request data contains required fields
            request_data = call_args[1]['data']
            assert self.test_declaration.declaration_number in request_data
            assert self.test_declaration.tax_code in request_data
            assert '05012023' in request_data  # Date formatted as ddmmyyyy
            assert self.test_declaration.customs_office_code in request_data
            
            # Verify SOAP structure
            assert '<soap:Envelope' in request_data
            assert '<GetBarcode' in request_data
            assert '<declarationNumber>' in request_data
            assert '<taxCode>' in request_data
            assert '<declarationDate>' in request_data
            assert '<customsOffice>' in request_data
            
            # Verify headers
            headers = call_args[1]['headers']
            assert 'Content-Type' in headers
            assert 'text/xml' in headers['Content-Type']
            assert 'SOAPAction' in headers
    
    def test_api_response_parsing_success(self):
        """Test parsing successful SOAP response with PDF content"""
        # Create a mock PDF content
        pdf_content = b'%PDF-1.4 mock pdf content'
        encoded_pdf = base64.b64encode(pdf_content).decode()
        
        soap_response = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBarcodeResponse xmlns="http://tempuri.org/">
      <GetBarcodeResult>{encoded_pdf}</GetBarcodeResult>
    </GetBarcodeResponse>
  </soap:Body>
</soap:Envelope>"""
        
        result = self.retriever._parse_soap_response(soap_response)
        
        assert result is not None
        assert result == pdf_content
    
    def test_api_response_parsing_no_result(self):
        """Test parsing SOAP response with no result"""
        soap_response = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBarcodeResponse xmlns="http://tempuri.org/">
    </GetBarcodeResponse>
  </soap:Body>
</soap:Envelope>"""
        
        result = self.retriever._parse_soap_response(soap_response)
        
        assert result is None
    
    def test_api_response_parsing_invalid_xml(self):
        """Test parsing invalid XML response"""
        soap_response = "This is not valid XML"
        
        result = self.retriever._parse_soap_response(soap_response)
        
        assert result is None
    
    def test_api_timeout_handling(self):
        """Test handling of API timeout"""
        import requests
        with patch.object(self.retriever.session, 'post') as mock_post:
            mock_post.side_effect = requests.Timeout("Connection timed out")
            
            result = self.retriever._try_api(self.test_declaration)
            
            assert result is None
            # Verify error was logged
            assert self.mock_logger.error.called
    
    def test_api_request_exception_handling(self):
        """Test handling of API request exceptions"""
        import requests
        with patch.object(self.retriever.session, 'post') as mock_post:
            mock_post.side_effect = requests.RequestException("Network error")
            
            result = self.retriever._try_api(self.test_declaration)
            
            assert result is None
            # Verify error was logged
            assert self.mock_logger.error.called
    
    def test_fallback_logic_api_success(self):
        """Test that fallback stops when API succeeds (called first)"""
        pdf_content = b'%PDF-1.4 mock pdf'
        
        # API is called first, so we mock _try_api to succeed
        with patch.object(self.retriever, '_try_api', return_value=pdf_content):
            with patch.object(self.retriever, '_try_web_scraping') as mock_web:
                result = self.retriever.retrieve_barcode(self.test_declaration)
                
                assert result == pdf_content
                # Web scraping should not be called since API succeeded
                assert not mock_web.called
    
    def test_fallback_logic_api_fails_primary_succeeds(self):
        """Test fallback to primary website when API fails"""
        pdf_content = b'%PDF-1.4 mock pdf'
        
        with patch.object(self.retriever, '_try_api', return_value=None):
            with patch.object(self.retriever, '_try_web_scraping', return_value=pdf_content):
                result = self.retriever.retrieve_barcode(self.test_declaration)
                
                assert result == pdf_content
    
    def test_fallback_logic_api_and_primary_fail_backup_succeeds(self):
        """Test fallback to backup website when API and primary fail"""
        pdf_content = b'%PDF-1.4 mock pdf'
        
        with patch.object(self.retriever, '_try_api', return_value=None):
            with patch.object(self.retriever, '_try_web_scraping') as mock_web:
                # Primary fails, backup succeeds
                def web_scraping_side_effect(url, decl):
                    if url == self.config.primary_web_url:
                        return None
                    elif url == self.config.backup_web_url:
                        return pdf_content
                
                mock_web.side_effect = web_scraping_side_effect
                
                result = self.retriever.retrieve_barcode(self.test_declaration)
                
                assert result == pdf_content
                # Web scraping should be called twice (primary and backup)
                assert mock_web.call_count == 2
    
    def test_fallback_logic_all_fail(self):
        """Test when all retrieval methods fail"""
        with patch.object(self.retriever, '_try_api', return_value=None):
            with patch.object(self.retriever, '_try_web_scraping', return_value=None):
                result = self.retriever.retrieve_barcode(self.test_declaration)
                
                assert result is None
                # Error should be logged
                assert self.mock_logger.error.called
    
    def test_web_scraping_timeout(self):
        """Test handling of web scraping timeout"""
        from selenium.common.exceptions import TimeoutException
        
        with patch.object(self.retriever, '_setup_webdriver') as mock_setup:
            mock_driver = Mock()
            mock_driver.get.side_effect = TimeoutException("Page load timeout")
            mock_setup.return_value = mock_driver
            
            result = self.retriever._try_web_scraping(
                self.config.primary_web_url,
                self.test_declaration
            )
            
            assert result is None
            # Driver should be quit
            assert mock_driver.quit.called
    
    def test_web_scraping_webdriver_exception(self):
        """Test handling of WebDriver exceptions"""
        from selenium.common.exceptions import WebDriverException
        
        with patch.object(self.retriever, '_setup_webdriver') as mock_setup:
            mock_driver = Mock()
            mock_driver.get.side_effect = WebDriverException("WebDriver error")
            mock_setup.return_value = mock_driver
            
            result = self.retriever._try_web_scraping(
                self.config.primary_web_url,
                self.test_declaration
            )
            
            assert result is None
            # Driver should be quit
            assert mock_driver.quit.called
    
    def test_cleanup(self):
        """Test cleanup of resources"""
        mock_driver = Mock()
        self.retriever._webdriver = mock_driver
        
        self.retriever.cleanup()
        
        assert mock_driver.quit.called
        assert self.retriever._webdriver is None
    
    def test_cleanup_with_no_driver(self):
        """Test cleanup when no driver exists"""
        self.retriever._webdriver = None
        
        # Should not raise exception
        self.retriever.cleanup()
        
        assert self.retriever._webdriver is None
    
    def test_date_formatting_in_api_request(self):
        """Test that dates are formatted correctly in API requests"""
        # Test with different dates
        test_cases = [
            (datetime(2023, 1, 5), '05012023'),
            (datetime(2022, 12, 30), '30122022'),
            (datetime(2024, 7, 15), '15072024'),
        ]
        
        for test_date, expected_format in test_cases:
            declaration = Declaration(
                declaration_number='123456789012',
                tax_code='1234567890',
                declaration_date=test_date,
                customs_office_code='18A3',
                transport_method='1',
                channel='Xanh',
                status='T',
                goods_description=None
            )
            
            with patch.object(self.retriever.session, 'post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.text = '<soap:Envelope></soap:Envelope>'
                mock_post.return_value = mock_response
                
                self.retriever._try_api(declaration)
                
                request_data = mock_post.call_args[1]['data']
                assert expected_format in request_data, \
                    f"Expected date format '{expected_format}' not found in request"



class TestAdaptiveSelectors:
    """Unit tests for adaptive selector functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = BarcodeServiceConfig(
            api_url='http://test-api.example.com/QRCode.asmx',
            primary_web_url='http://primary.example.com',
            backup_web_url='http://backup.example.com',
            timeout=30,
            max_retries=3,
            retry_delay=5,
            api_timeout=10,
            web_timeout=15
        )
        self.mock_logger = Mock()
        self.retriever = BarcodeRetriever(self.config, self.mock_logger)
    
    def test_adaptive_selector_tries_all_variations(self):
        """Test that adaptive selector tries all variations for a field"""
        mock_driver = Mock()
        
        # Track which selectors were tried
        tried_selectors = []
        
        def mock_find_element(by, selector_name):
            tried_selectors.append(selector_name)
            raise Exception(f"Selector '{selector_name}' not found")
        
        mock_driver.find_element = mock_find_element
        mock_driver.title = "Test Page"
        mock_driver.current_url = "http://test.com"
        mock_driver.find_elements.return_value = []
        
        # Try to fill tax code field
        result = self.retriever._try_adaptive_selectors(mock_driver, 'taxCode', '1234567890')
        
        # Should return None since all failed
        assert result is None
        
        # Verify all tax code selectors were tried
        expected_selectors = self.retriever.FIELD_SELECTORS['taxCode']
        for selector in expected_selectors:
            assert selector in tried_selectors, \
                f"Expected selector '{selector}' to be tried"
    
    def test_adaptive_selector_returns_first_working_selector(self):
        """Test that adaptive selector returns the first working selector"""
        mock_driver = Mock()
        mock_element = Mock()
        
        # Make the third selector work
        working_selector = self.retriever.FIELD_SELECTORS['taxCode'][2]
        
        def mock_find_element(by, selector_name):
            if selector_name == working_selector:
                return mock_element
            raise Exception(f"Selector '{selector_name}' not found")
        
        mock_driver.find_element = mock_find_element
        
        result = self.retriever._try_adaptive_selectors(mock_driver, 'taxCode', '1234567890')
        
        # Should return the working selector
        assert result == working_selector
        
        # Verify element was filled
        assert mock_element.clear.called
        assert mock_element.send_keys.called
    
    def test_adaptive_selector_uses_cached_selector_first(self):
        """Test that cached selector is tried first when cache is valid"""
        mock_driver = Mock()
        mock_element = Mock()
        
        # Set up cache with a working selector
        cached_selector = 'ma_dv'
        self.retriever._cache_working_selector('taxCode', cached_selector)
        
        # Track which selectors were tried
        tried_selectors = []
        
        def mock_find_element(by, selector_name):
            tried_selectors.append(selector_name)
            if selector_name == cached_selector:
                return mock_element
            raise Exception(f"Selector '{selector_name}' not found")
        
        mock_driver.find_element = mock_find_element
        
        result = self.retriever._try_adaptive_selectors(mock_driver, 'taxCode', '1234567890')
        
        # Should return the cached selector
        assert result == cached_selector
        
        # Cached selector should be tried first
        assert tried_selectors[0] == cached_selector
    
    def test_selector_cache_validation(self):
        """Test that selector cache validates correctly"""
        from datetime import datetime, timedelta
        from models.config_models import SelectorCache
        
        # Test valid cache
        cache = SelectorCache(
            tax_code_selector='ma_dv',
            last_updated=datetime.now()
        )
        assert cache.is_valid(max_age_hours=24)
        
        # Test expired cache
        cache_expired = SelectorCache(
            tax_code_selector='ma_dv',
            last_updated=datetime.now() - timedelta(hours=25)
        )
        assert not cache_expired.is_valid(max_age_hours=24)
        
        # Test cache with no timestamp
        cache_no_timestamp = SelectorCache(
            tax_code_selector='ma_dv',
            last_updated=None
        )
        assert not cache_no_timestamp.is_valid()
    
    def test_html_structure_logging_on_failure(self):
        """Test that HTML structure is logged when selectors fail"""
        mock_driver = Mock()
        mock_driver.title = "Test Page"
        mock_driver.current_url = "http://test.com"
        
        # Mock forms
        mock_form = Mock()
        mock_form.get_attribute.return_value = '<form id="testForm">...</form>'
        
        # Mock inputs
        mock_input = Mock()
        mock_input.get_attribute.side_effect = lambda attr: {
            'id': 'testInput',
            'name': 'testName',
            'type': 'text',
            'class': 'form-control'
        }.get(attr, 'N/A')
        
        # Mock selects
        mock_select = Mock()
        mock_select.get_attribute.side_effect = lambda attr: {
            'id': 'testSelect',
            'name': 'selectName'
        }.get(attr, 'N/A')
        
        def mock_find_elements(by, tag_name):
            if tag_name == 'form':
                return [mock_form]
            elif tag_name == 'input':
                return [mock_input]
            elif tag_name == 'select':
                return [mock_select]
            return []
        
        mock_driver.find_elements = mock_find_elements
        
        # Call the logging method
        self.retriever._log_html_structure_on_failure(mock_driver, 'taxCode')
        
        # Verify logging occurred
        assert self.mock_logger.error.called
        assert self.mock_logger.debug.called
        
        # Check that relevant information was logged
        debug_calls = [str(call) for call in self.mock_logger.debug.call_args_list]
        debug_text = ' '.join(debug_calls)
        
        assert 'Test Page' in debug_text
        assert 'http://test.com' in debug_text
    
    def test_timeout_configuration_backward_compatibility(self):
        """Test that timeout configuration works with legacy config"""
        # Config without new timeout fields (but they have defaults)
        legacy_config = BarcodeServiceConfig(
            api_url='http://test-api.example.com',
            primary_web_url='http://primary.example.com',
            backup_web_url='http://backup.example.com',
            timeout=30,
            max_retries=3,
            retry_delay=5
        )
        
        retriever = BarcodeRetriever(legacy_config, self.mock_logger)
        
        # New fields should have default values
        assert legacy_config.api_timeout == 10  # Default value
        assert legacy_config.web_timeout == 15  # Default value
        
        # Verify the retriever can use these values
        assert hasattr(legacy_config, 'api_timeout')
        assert hasattr(legacy_config, 'web_timeout')
    
    def test_new_timeout_configuration(self):
        """Test that new timeout configuration is used when available"""
        # Config with new timeout fields
        new_config = BarcodeServiceConfig(
            api_url='http://test-api.example.com',
            primary_web_url='http://primary.example.com',
            backup_web_url='http://backup.example.com',
            timeout=30,
            max_retries=3,
            retry_delay=5,
            api_timeout=10,
            web_timeout=15
        )
        
        retriever = BarcodeRetriever(new_config, self.mock_logger)
        
        # Should use new timeouts
        assert new_config.api_timeout == 10
        assert new_config.web_timeout == 15


class TestPerformanceOptimizations:
    """Unit tests for performance optimization features"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.config = BarcodeServiceConfig(
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
        self.mock_logger = Mock()
        self.retriever = BarcodeRetriever(self.config, self.mock_logger)
    
    def test_session_is_initialized_with_connection_pooling(self):
        """Test that HTTP session is initialized with connection pooling"""
        # Verify session exists
        assert hasattr(self.retriever, 'session')
        assert self.retriever.session is not None
        
        # Verify session is a requests.Session
        import requests
        assert isinstance(self.retriever.session, requests.Session)
        
        # Verify adapters are mounted
        assert 'http://' in self.retriever.session.adapters
        assert 'https://' in self.retriever.session.adapters
    
    def test_session_is_reused_across_multiple_requests(self):
        """Test that the same session is reused across multiple API calls"""
        test_declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        # Capture the initial session
        initial_session = self.retriever.session
        
        # Mock the session's post method
        with patch.object(self.retriever.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = '<soap:Envelope></soap:Envelope>'
            mock_post.return_value = mock_response
            
            # Make multiple API calls
            self.retriever._try_api(test_declaration)
            self.retriever._try_api(test_declaration)
            self.retriever._try_api(test_declaration)
            
            # Verify post was called 3 times
            assert mock_post.call_count == 3
            
            # Verify the same session object is still being used
            assert self.retriever.session is initial_session
    
    def test_timeout_occurs_within_new_limits(self):
        """Test that timeout occurs within the new reduced limits"""
        import time
        import requests
        
        test_declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        # Mock session.post to simulate timeout
        def mock_post_timeout(*args, **kwargs):
            timeout_value = kwargs.get('timeout', 30)
            # Verify the new timeout is being used
            assert timeout_value == 10, f"Expected timeout=10, got {timeout_value}"
            raise requests.Timeout(f"Request timed out after {timeout_value}s")
        
        with patch.object(self.retriever.session, 'post', side_effect=mock_post_timeout):
            start_time = time.time()
            result = self.retriever._try_api(test_declaration)
            elapsed_time = time.time() - start_time
            
            # Verify result is None
            assert result is None
            
            # Verify it failed quickly (within 1 second since we're mocking)
            assert elapsed_time < 1.0
    
    def test_method_skipping_tracks_failures(self):
        """Test that method skipping tracks failed methods correctly"""
        test_declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        # Initially, all methods should be tried
        assert self.retriever._should_try_method('api')
        assert self.retriever._should_try_method('primary_web')
        assert self.retriever._should_try_method('backup_web')
        
        # Record 3 failures for API
        self.retriever._record_method_failure('api')
        self.retriever._record_method_failure('api')
        self.retriever._record_method_failure('api')
        
        # API should now be skipped
        assert not self.retriever._should_try_method('api')
        
        # Other methods should still be tried
        assert self.retriever._should_try_method('primary_web')
        assert self.retriever._should_try_method('backup_web')
    
    def test_method_skipping_resets_on_success(self):
        """Test that method failure count resets on success"""
        # Record 2 failures
        self.retriever._record_method_failure('api')
        self.retriever._record_method_failure('api')
        
        assert self.retriever._failed_methods['api'] == 2
        
        # Record success
        self.retriever._record_method_success('api')
        
        # Failure count should be reset
        assert self.retriever._failed_methods['api'] == 0
        assert self.retriever._should_try_method('api')
    
    def test_method_skipping_in_retrieve_barcode(self):
        """Test that method skipping works in the retrieve_barcode flow"""
        test_declaration = Declaration(
            declaration_number='123456789012',
            tax_code='1234567890',
            declaration_date=datetime(2023, 1, 5),
            customs_office_code='18A3',
            transport_method='1',
            channel='Xanh',
            status='T',
            goods_description=None
        )
        
        # Mock all methods to fail
        with patch.object(self.retriever, '_try_api', return_value=None):
            with patch.object(self.retriever, '_try_web_scraping', return_value=None):
                # Process 5 declarations to trigger skipping
                for i in range(5):
                    result = self.retriever.retrieve_barcode(test_declaration)
                    assert result is None
                
                # After 3 failures, API should be skipped
                assert not self.retriever._should_try_method('api')
                
                # Verify API is no longer being called
                api_call_count_before = self.retriever._try_api.call_count
                self.retriever.retrieve_barcode(test_declaration)
                api_call_count_after = self.retriever._try_api.call_count
                
                # Call count should not increase (method is skipped)
                assert api_call_count_after == api_call_count_before
    
    def test_reset_method_skip_list(self):
        """Test that method skip list can be reset for new batches"""
        # Record failures to trigger skipping
        for i in range(3):
            self.retriever._record_method_failure('api')
            self.retriever._record_method_failure('primary_web')
        
        # Methods should be skipped
        assert not self.retriever._should_try_method('api')
        assert not self.retriever._should_try_method('primary_web')
        
        # Reset skip list
        self.retriever.reset_method_skip_list()
        
        # All methods should be tried again
        assert self.retriever._should_try_method('api')
        assert self.retriever._should_try_method('primary_web')
        assert self.retriever._should_try_method('backup_web')
        
        # Failure counts should be reset
        assert self.retriever._failed_methods['api'] == 0
        assert self.retriever._failed_methods['primary_web'] == 0
        assert self.retriever._failed_methods['backup_web'] == 0
    
    def test_retry_logic_respects_new_max_retries(self):
        """Test that retry logic respects the new max_retries configuration"""
        # The HTTPAdapter should be configured with max_retries=1
        adapter = self.retriever.session.get_adapter('http://test.com')
        
        # Verify adapter exists
        assert adapter is not None
        
        # Verify max_retries is configured
        assert hasattr(adapter, 'max_retries')
        
        # The Retry object should have total=1
        from requests.adapters import Retry
        if isinstance(adapter.max_retries, Retry):
            assert adapter.max_retries.total == 1
    
    def test_session_cleanup(self):
        """Test that session is properly closed during cleanup"""
        # Verify session exists
        assert hasattr(self.retriever, 'session')
        
        # Mock the session's close method
        with patch.object(self.retriever.session, 'close') as mock_close:
            self.retriever.cleanup()
            
            # Verify close was called
            assert mock_close.called
    
    def test_session_reuse_disabled(self):
        """Test behavior when session reuse is disabled"""
        config_no_reuse = BarcodeServiceConfig(
            api_url='http://test-api.example.com',
            primary_web_url='http://primary.example.com',
            backup_web_url='http://backup.example.com',
            timeout=30,
            max_retries=1,
            retry_delay=0,
            api_timeout=10,
            web_timeout=15,
            session_reuse=False
        )
        
        retriever = BarcodeRetriever(config_no_reuse, self.mock_logger)
        
        # Session should still exist (for basic functionality)
        assert hasattr(retriever, 'session')
        assert retriever.session is not None
