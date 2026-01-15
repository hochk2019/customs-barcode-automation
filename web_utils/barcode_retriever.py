"""
Barcode Retriever Module

This module handles retrieving barcode PDFs from customs services using
API calls and web scraping with fallback support.

V2.0 Updates (December 2024):
- Added API method using QueryBangKeDanhSachContainer to render PDF directly
- Added retrieval_method config option: 'api', 'web', 'auto'
- Removed backup_web_url (pus1.customs.gov.vn) due to CAPTCHA
"""

import time
import requests
from typing import Optional
from datetime import datetime
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from models.config_models import BarcodeServiceConfig, SelectorCache
from models.declaration_models import Declaration
from logging_system.logger import Logger
from web_utils.qrcode_api_client import QRCodeContainerApiClient, QRCodeApiError
from web_utils.barcode_pdf_generator import BarcodePdfGenerator


class BarcodeRetrievalError(Exception):
    """Exception raised for barcode retrieval errors"""
    pass


class RetrievalMethod(Enum):
    """Barcode retrieval method options"""
    API = "api"      # Use API to get data and render PDF
    WEB = "web"      # Use web scraping from pus.customs.gov.vn
    AUTO = "auto"    # Auto-select best method with fallback


class BarcodeRetriever:
    """
    Retrieves barcode PDFs from customs services.
    
    V2.0 supports multiple retrieval methods:
    - API: Query data from SOAP API and render PDF locally (faster, more reliable)
    - Web: Scrape from pus.customs.gov.vn website (fallback)
    - Auto: Try API first, fallback to Web if failed
    """
    
    # Adaptive selectors with multiple variations for each field
    # Updated December 2024 based on actual website analysis
    FIELD_SELECTORS = {
        'taxCode': [
            # Backup website (pus1.customs.gov.vn) - ASP.NET
            'MaDoanhNghiep',
            # Primary website (pus.customs.gov.vn) - Oracle ADF
            'pt1:it1::content', 'pt1:it1',
            # Legacy selectors
            'taxCode', 'ma_dv', 'maDoanhnghiep', 
            'mst', 'tax_code', 'MaDV', 'TaxCode',
            'MA_DV', 'MST'
        ],
        'declarationNumber': [
            # Backup website (pus1.customs.gov.vn) - ASP.NET
            'SoToKhai',
            # Primary website (pus.customs.gov.vn) - Oracle ADF
            'pt1:it2::content', 'pt1:it2',
            # Legacy selectors
            'declarationNumber', 'so_tk', 'soToKhai', 
            'so_to_khai', 'SoTK', 'DeclarationNumber',
            'SO_TK', 'SO_TOKHAI'
        ],
        'declarationDate': [
            # Backup website (pus1.customs.gov.vn) - ASP.NET
            'txtNgayToKhai',
            # Primary website (pus.customs.gov.vn) - Oracle ADF
            # CORRECTED Dec 2024: pt1:it4 is Declaration Date, NOT pt1:it3!
            'pt1:it4::content', 'pt1:it4',
            # Legacy selectors
            'declarationDate', 'ngay_dk', 'ngayToKhai',
            'ngay_to_khai', 'NgayDK', 'DeclarationDate',
            'NGAY_DK', 'NGAY_TOKHAI'
        ],
        'customsOffice': [
            # Backup website (pus1.customs.gov.vn) - ASP.NET
            'MaHQ',
            # Primary website (pus.customs.gov.vn) - Oracle ADF
            # CORRECTED Dec 2024: pt1:it3 is Customs Office, NOT pt1:it4!
            'pt1:it3::content', 'pt1:it3',
            # Legacy selectors
            'customsOffice', 'ma_hq', 'maHaiQuan',
            'ma_hai_quan', 'MaHQ', 'CustomsOffice',
            'MA_HQ', 'MA_HAIQUAN'
        ]
    }
    
    def __init__(self, config: BarcodeServiceConfig, logger: Logger, 
                 retrieval_method: str = "auto"):
        """
        Initialize barcode retriever
        
        Args:
            config: BarcodeServiceConfig object
            logger: Logger instance
            retrieval_method: Method to use - 'api', 'web', or 'auto' (default)
        """
        self.config = config
        self.logger = logger
        self._webdriver: Optional[webdriver.Chrome] = None
        self._selector_cache = SelectorCache()  # Initialize selector cache
        
        # Set retrieval method
        try:
            self.retrieval_method = RetrievalMethod(retrieval_method.lower())
        except ValueError:
            self.logger.warning(f"Invalid retrieval method '{retrieval_method}', using 'auto'")
            self.retrieval_method = RetrievalMethod.AUTO
        
        self.logger.info(f"Barcode retriever initialized with method: {self.retrieval_method.value}")
        
        # Initialize API client for API method
        api_url = getattr(self.config, 'api_url', None)
        # Fix URL: remove port 8086 if present (internal only)
        if api_url and ':8086' in api_url:
            api_url = api_url.replace(':8086', '')
        self._api_client = QRCodeContainerApiClient(
            service_url=api_url,
            logger=logger,
            timeout=getattr(self.config, 'api_timeout', 30)
        )
        
        # Initialize PDF generator for API method
        self._pdf_generator = BarcodePdfGenerator(logger=logger)
        
        # Initialize HTTP session with connection pooling for performance
        self.session = requests.Session()
        if getattr(self.config, 'session_reuse', True):
            # Configure HTTPAdapter with reduced retries and connection pooling
            from requests.adapters import Retry
            retry_strategy = Retry(
                total=getattr(self.config, 'max_retries', 1),
                backoff_factor=0,  # No delay between retries
                status_forcelist=[500, 502, 503, 504]
            )
            adapter = requests.adapters.HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=10
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)
            self.logger.debug(f"HTTP session initialized with max_retries={getattr(self.config, 'max_retries', 1)}, no retry delays")
        
        # Track failed methods for skipping (reset per batch)
        # Note: backup_web removed in V2.0 due to CAPTCHA
        self._failed_methods = {
            'api': 0,
            'web': 0,
            'primary_web': 0,
            'backup_web': 0
        }
        self._skip_threshold = 3  # Skip after 3 consecutive failures
    
    def set_retrieval_method(self, method: str) -> None:
        """
        Update the retrieval method at runtime.
        
        This allows changing the retrieval method without restarting the application.
        Called when user changes settings in the Settings dialog.
        
        Args:
            method: New retrieval method - 'api', 'web', or 'auto'
        """
        try:
            new_method = RetrievalMethod(method.lower())
            old_method = self.retrieval_method
            self.retrieval_method = new_method
            
            # Reset failed method counters when method changes
            self._failed_methods = {
                'api': 0,
                'web': 0
            }
            
            self.logger.info(f"Retrieval method changed from '{old_method.value}' to '{new_method.value}'")
        except ValueError:
            self.logger.warning(f"Invalid retrieval method '{method}', keeping current method '{self.retrieval_method.value}'")
    
    def retrieve_barcode(self, declaration: Declaration) -> Optional[bytes]:
        """
        Retrieve barcode PDF for a declaration based on configured method.
        
        V2.0: Supports API, Web, and Auto methods.
        - API: Query SOAP API and render PDF locally (faster)
        - Web: Scrape from pus.customs.gov.vn
        - Auto: Try API, then primary web, then backup web
        
        Args:
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if all methods fail
        """
        self.logger.info(f"Attempting to retrieve barcode for {declaration.id} using method: {self.retrieval_method.value}")
        self.logger.debug(f"Declaration details: tax_code={declaration.tax_code}, declaration_number={declaration.declaration_number}, customs_office={declaration.customs_office_code}, date={declaration.declaration_date}")
        
        # Determine which methods to try based on retrieval_method setting
        if self.retrieval_method == RetrievalMethod.API:
            # API only
            return self._try_api_method(declaration)
        
        elif self.retrieval_method == RetrievalMethod.WEB:
            # Web only
            return self._try_web_method(declaration)
        
        else:  # AUTO mode
            # Try API first, then primary web, then backup web
            if self._should_try_method('api'):
                pdf_content = self._try_api(declaration)
                if pdf_content:
                    self._record_method_success('api')
                    return pdf_content
                self._record_method_failure('api')

            if self._should_try_method('primary_web'):
                pdf_content = self._try_web_scraping(self.config.primary_web_url, declaration)
                if pdf_content:
                    self._record_method_success('primary_web')
                    return pdf_content
                self._record_method_failure('primary_web')

            backup_url = getattr(self.config, 'backup_web_url', None)
            if backup_url and self._should_try_method('backup_web'):
                pdf_content = self._try_web_scraping(backup_url, declaration)
                if pdf_content:
                    self._record_method_success('backup_web')
                    return pdf_content
                self._record_method_failure('backup_web')

            self.logger.error(f"All retrieval methods failed for {declaration.id}")
            return None
    
    def _try_api_method(self, declaration: Declaration) -> Optional[bytes]:
        """
        Try to retrieve barcode via API and render PDF.
        
        Args:
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        try:
            self.logger.debug(f"Trying API method for {declaration.id}")
            
            # Query API for declaration info
            info = self._api_client.query_bang_ke(
                ma_so_thue=declaration.tax_code,
                so_to_khai=declaration.declaration_number,
                ma_hai_quan=declaration.customs_office_code,
                ngay_dang_ky=declaration.declaration_date.date() if isinstance(declaration.declaration_date, datetime) else declaration.declaration_date
            )
            
            if not info:
                self.logger.warning(f"API returned no data for {declaration.id}")
                self._record_method_failure('api')
                return None
            
            if info.has_error:
                self.logger.warning(f"API error for {declaration.id}: {info.thong_bao_loi}")
                self._record_method_failure('api')
                return None
            
            # Generate PDF from API data
            pdf_content = self._pdf_generator.generate_pdf(info)
            
            if pdf_content:
                self.logger.info(f"Successfully generated PDF via API for {declaration.id}")
                self._record_method_success('api')
                return pdf_content
            
            self.logger.warning(f"Failed to generate PDF for {declaration.id}")
            self._record_method_failure('api')
            return None
            
        except QRCodeApiError as e:
            self.logger.error(f"API error for {declaration.id}: {e}")
            self._record_method_failure('api')
            return None
        except Exception as e:
            self.logger.error(f"API method failed for {declaration.id}: {e}")
            self._record_method_failure('api')
            return None
    
    def _try_web_method(self, declaration: Declaration) -> Optional[bytes]:
        """
        Try to retrieve barcode via web scraping.
        
        Args:
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        try:
            self.logger.debug(f"Trying web method for {declaration.id}")
            pdf_content = self._try_web_scraping(self.config.primary_web_url, declaration)
            
            if pdf_content:
                self.logger.info(f"Successfully retrieved barcode via web for {declaration.id}")
                self._record_method_success('web')
                return pdf_content
            
            self.logger.warning(f"Web method returned no content for {declaration.id}")
            self._record_method_failure('web')
            return None
            
        except Exception as e:
            self.logger.error(f"Web method failed for {declaration.id}: {e}")
            self._record_method_failure('web')
            return None
    
    def _try_api(self, declaration: Declaration) -> Optional[bytes]:
        """
        Try to retrieve barcode via SOAP API
        
        Args:
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        # Format date as ddmmyyyy
        date_str = declaration.declaration_date.strftime('%d%m%Y')
        
        # Build SOAP request
        soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <GetBarcode xmlns="http://tempuri.org/">
      <declarationNumber>{declaration.declaration_number}</declarationNumber>
      <taxCode>{declaration.tax_code}</taxCode>
      <declarationDate>{date_str}</declarationDate>
      <customsOffice>{declaration.customs_office_code}</customsOffice>
    </GetBarcode>
  </soap:Body>
</soap:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/GetBarcode'
        }
        
        try:
            # Use api_timeout if available, otherwise fall back to legacy timeout
            timeout = getattr(self.config, 'api_timeout', self.config.timeout)
            
            response = self.session.post(
                self.config.api_url,
                data=soap_request,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                # Parse SOAP response to extract PDF content
                pdf_content = self._parse_soap_response(response.text)
                return pdf_content
            else:
                self.logger.warning(f"API returned status code {response.status_code}")
                return None
                
        except requests.Timeout:
            timeout = getattr(self.config, 'api_timeout', self.config.timeout)
            self.logger.error(f"API request timed out after {timeout}s")
            return None
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return None
    
    def _parse_soap_response(self, response_text: str) -> Optional[bytes]:
        """
        Parse SOAP response to extract PDF content
        
        Args:
            response_text: SOAP response XML as string
            
        Returns:
            PDF content as bytes, or None if parsing failed
        """
        try:
            # Look for GetBarcodeResult or similar tag containing base64 PDF
            import xml.etree.ElementTree as ET
            import base64
            
            root = ET.fromstring(response_text)
            
            # Find the result element (namespace-aware)
            namespaces = {
                'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                'ns': 'http://tempuri.org/'
            }
            
            # Try to find the result element
            result = root.find('.//ns:GetBarcodeResult', namespaces)
            if result is None:
                # Try without namespace
                result = root.find('.//GetBarcodeResult')
            
            if result is not None and result.text:
                # Decode base64 content
                pdf_bytes = base64.b64decode(result.text)
                return pdf_bytes
            
            self.logger.warning("No PDF content found in SOAP response")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to parse SOAP response: {e}")
            return None
    
    def _try_web_scraping(self, url: str, declaration: Declaration) -> Optional[bytes]:
        """
        Try to retrieve barcode via web scraping
        
        Args:
            url: Website URL
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        driver = None
        try:
            # Set up WebDriver
            self.logger.debug(f"Setting up WebDriver for {url}")
            driver = self._setup_webdriver()
            
            # Navigate to URL
            self.logger.debug(f"Navigating to {url}")
            driver.get(url)
            self.logger.debug(f"Navigation complete, waiting for page to load")
            
            # Wait for page to load (use web_timeout if available)
            timeout = getattr(self.config, 'web_timeout', self.config.timeout)
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.logger.debug(f"Page body loaded")
            
            # Detect website type and use appropriate method
            if 'pus.customs.gov.vn' in url and 'faces' in url:
                # Oracle ADF website - use special handling
                self.logger.debug("Detected Oracle ADF website, using AJAX handling")
                return self._handle_oracle_adf_website(driver, declaration)
            else:
                # Standard website - use normal form submission
                return self._handle_standard_website(driver, declaration)
                
        except TimeoutException:
            self.logger.error(f"Web scraping timed out for {url}")
            return None
        except WebDriverException as e:
            self.logger.error(f"WebDriver error for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Web scraping failed for {url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def _handle_oracle_adf_website(self, driver: webdriver.Chrome, declaration: Declaration) -> Optional[bytes]:
        """
        Handle Oracle ADF website with AJAX form submission
        
        Oracle ADF uses AJAX for form submission, so we need to:
        1. Fill form fields using JavaScript
        2. Trigger the AJAX submit
        3. Wait for AJAX response
        4. Extract PDF from response
        
        Args:
            driver: WebDriver instance
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        try:
            timeout = getattr(self.config, 'web_timeout', self.config.timeout)
            
            # Format date as dd/mm/yyyy for Oracle ADF
            date_str = declaration.declaration_date.strftime('%d/%m/%Y')
            
            self.logger.debug(f"Filling Oracle ADF form for {declaration.id}")
            
            # Wait for ADF to fully load - Oracle ADF needs time to initialize JavaScript
            # Try multiple times with increasing wait
            form_loaded = False
            for wait_time in [3, 5, 10]:
                time.sleep(wait_time)
                try:
                    driver.find_element(By.ID, "pt1:it1::content")
                    self.logger.debug(f"ADF form fields loaded after {wait_time}s wait")
                    form_loaded = True
                    break
                except:
                    self.logger.debug(f"Form fields not found after {wait_time}s, retrying...")
            
            if not form_loaded:
                self.logger.error("ADF form fields not found after multiple attempts")
                return None
            
            # Fill form fields using JavaScript (more reliable for ADF)
            # IMPORTANT: Field order based on actual website HTML analysis (Dec 2024)
            # Field 1: Mã doanh nghiệp (Tax Code)
            self._fill_adf_field(driver, 'pt1:it1::content', declaration.tax_code)
            
            # Field 2: Số tờ khai (Declaration Number)
            self._fill_adf_field(driver, 'pt1:it2::content', declaration.declaration_number)
            
            # Field 3: Mã hải quan (Customs Office) - NOT Declaration Date!
            self._fill_adf_field(driver, 'pt1:it3::content', declaration.customs_office_code)
            
            # Field 4: Ngày tờ khai (Declaration Date) - dd/mm/yyyy format
            self._fill_adf_field(driver, 'pt1:it4::content', date_str)
            
            # Wait a bit for ADF to process field changes
            time.sleep(1)
            
            # Find and click the "Lấy thông tin" button
            # In Oracle ADF, buttons are often <a> tags with role="button"
            submit_clicked = self._click_adf_submit_button(driver)
            
            if not submit_clicked:
                self.logger.error("Failed to click ADF submit button")
                return None
            
            # Wait for AJAX response - need longer wait for server to process
            self.logger.debug("Waiting for ADF AJAX response...")
            time.sleep(10)  # Wait 10 seconds for AJAX response (server can be slow)
            
            # Wait for result content to appear
            try:
                WebDriverWait(driver, timeout).until(
                    lambda d: self._check_adf_result_loaded(d)
                )
                self.logger.debug("ADF result loaded")
            except TimeoutException:
                self.logger.warning("Timeout waiting for ADF result")
            
            # Try to extract PDF from the page
            pdf_content = self._extract_pdf_from_adf_page(driver)
            
            if pdf_content:
                self.logger.info(f"Successfully extracted PDF from Oracle ADF page")
                return pdf_content
            
            # If no PDF found, try to find and click "Lưu bảng kê" link
            pdf_content = self._try_adf_save_link(driver)
            
            return pdf_content
            
        except Exception as e:
            self.logger.error(f"Oracle ADF handling failed: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def _fill_adf_field(self, driver: webdriver.Chrome, field_id: str, value: str) -> bool:
        """
        Fill an Oracle ADF form field using JavaScript
        
        Args:
            driver: WebDriver instance
            field_id: Field ID
            value: Value to fill
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to find element first
            element = driver.find_element(By.ID, field_id)
            
            # Clear and fill using JavaScript (more reliable for ADF)
            driver.execute_script("""
                var element = arguments[0];
                var value = arguments[1];
                element.value = value;
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
            """, element, value)
            
            self.logger.debug(f"Filled ADF field {field_id} with value")
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to fill ADF field {field_id}: {e}")
            
            # Try alternative: direct JavaScript by ID
            try:
                driver.execute_script(f"""
                    var element = document.getElementById('{field_id}');
                    if (element) {{
                        element.value = '{value}';
                        element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                return True
            except:
                return False
    
    def _click_adf_submit_button(self, driver: webdriver.Chrome) -> bool:
        """
        Click the submit button in Oracle ADF page
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if button was clicked, False otherwise
        """
        # Try multiple methods to find and click the button
        
        # Method 1: Find by text "Lấy thông tin"
        try:
            button = driver.find_element(By.XPATH, "//a[contains(@class, 'xfp') and contains(., 'Lấy thông tin')]")
            driver.execute_script("arguments[0].click();", button)
            self.logger.debug("Clicked ADF button using XPATH (xfp class)")
            return True
        except:
            pass
        
        # Method 2: Find by role="button" and text
        try:
            button = driver.find_element(By.XPATH, "//a[@role='button' and contains(., 'Lấy thông tin')]")
            driver.execute_script("arguments[0].click();", button)
            self.logger.debug("Clicked ADF button using role='button'")
            return True
        except:
            pass
        
        # Method 3: Find by span text inside link
        try:
            button = driver.find_element(By.XPATH, "//a[.//span[contains(text(), 'Lấy thông tin')]]")
            driver.execute_script("arguments[0].click();", button)
            self.logger.debug("Clicked ADF button using span text")
            return True
        except:
            pass
        
        # Method 4: Try JavaScript to trigger ADF action
        try:
            # ADF often uses specific JavaScript functions
            driver.execute_script("""
                var buttons = document.querySelectorAll('a[role="button"]');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.indexOf('Lấy thông tin') !== -1) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            """)
            self.logger.debug("Clicked ADF button using JavaScript query")
            return True
        except:
            pass
        
        # Method 5: Find any clickable element with the text
        try:
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Lấy thông tin')]")
            for elem in elements:
                try:
                    driver.execute_script("arguments[0].click();", elem)
                    self.logger.debug("Clicked element containing 'Lấy thông tin'")
                    return True
                except:
                    continue
        except:
            pass
        
        self.logger.error("Could not find or click ADF submit button")
        return False
    
    def _check_adf_result_loaded(self, driver: webdriver.Chrome) -> bool:
        """
        Check if ADF result content has loaded
        
        Args:
            driver: WebDriver instance
            
        Returns:
            True if result is loaded, False otherwise
        """
        try:
            # Check for result content div
            result_div = driver.find_element(By.ID, "content")
            if result_div and result_div.text.strip():
                return True
        except:
            pass
        
        try:
            # Check for "Lưu bảng kê" link (appears when result is ready)
            save_link = driver.find_element(By.ID, "lbl_BanLuu")
            if save_link:
                return True
        except:
            pass
        
        try:
            # Check for any table with barcode data
            tables = driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                if "container" in table.text.lower() or "mã vạch" in table.text.lower():
                    return True
        except:
            pass
        
        return False
    
    def _extract_pdf_from_adf_page(self, driver: webdriver.Chrome) -> Optional[bytes]:
        """
        Extract PDF content from Oracle ADF page
        
        Args:
            driver: WebDriver instance
            
        Returns:
            PDF content as bytes, or None if not found
        """
        try:
            # Check if there's a PDF iframe
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src")
                if src and ".pdf" in src.lower():
                    timeout = getattr(self.config, 'web_timeout', self.config.timeout)
                    response = self.session.get(src, timeout=timeout, verify=False)
                    if response.status_code == 200 and response.content.startswith(b'%PDF'):
                        return response.content
        except:
            pass
        
        try:
            # Check for PDF links
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            for link in pdf_links:
                href = link.get_attribute("href")
                if href:
                    timeout = getattr(self.config, 'web_timeout', self.config.timeout)
                    response = self.session.get(href, timeout=timeout, verify=False)
                    if response.status_code == 200 and response.content.startswith(b'%PDF'):
                        return response.content
        except:
            pass
        
        return None
    
    def _try_adf_save_link(self, driver: webdriver.Chrome) -> Optional[bytes]:
        """
        Try to extract content and convert to PDF using Chrome DevTools Protocol
        
        The Oracle ADF website returns HTML content, not PDF directly.
        We need to:
        1. Hide all page elements except the print content
        2. Use Chrome's print-to-PDF functionality to generate clean PDF
        
        Args:
            driver: WebDriver instance
            
        Returns:
            PDF content as bytes, or None if not found
        """
        try:
            # Check if there's result content by looking for "Lưu bảng kê" link
            try:
                save_link = driver.find_element(By.ID, "lbl_BanLuu")
                if not save_link:
                    self.logger.debug("No 'Lưu bảng kê' link found - no result to export")
                    return None
            except:
                self.logger.debug("No result content found")
                return None
            
            # Log result panel status for debugging
            try:
                result_panel = driver.find_element(By.ID, "pt1:pgl2")
                panel_style = result_panel.get_attribute("style") or ""
                png1_panel = driver.find_element(By.ID, "pt1:png1")
                png1_style = png1_panel.get_attribute("style") or ""
                self.logger.debug(f"Result panels: pgl2 style='{panel_style}', png1 style='{png1_style}'")
            except Exception as e:
                self.logger.debug(f"Could not check result panels: {e}")
            
            self.logger.info("Found result content, preparing print view...")
            
            # Step 1: Prepare page for printing by hiding unnecessary elements
            # IMPORTANT: Keep original layout, only hide unwanted elements
            driver.execute_script("""
                // Hide header (blue banner), menu, footer - but keep layout intact
                var elementsToHide = [
                    'PortalHeader',           // Blue header banner
                    'PortalMainMenuContainer', 
                    'PortalFooter',
                    'PortalBottomMenuContainer', 
                    'PortalSearchContainer',
                    'PortalSubMenuContainer', 
                    'PortalBreadcrumb',
                    'PortalTopMenuContainer'
                ];
                
                elementsToHide.forEach(function(id) {
                    var elem = document.getElementById(id);
                    if (elem) elem.style.display = 'none';
                });
                
                // Hide ALL form input panels (pt1:pfl1 to pt1:pfl5)
                var formPanels = document.querySelectorAll('[id^="pt1:pfl"]');
                formPanels.forEach(function(panel) {
                    panel.style.display = 'none';
                });
                
                // Hide "Trang để in" and "Lưu bảng kê" buttons
                var btnPrint = document.getElementById('lbl_BanIn');
                var btnSave = document.getElementById('lbl_BanLuu');
                if (btnPrint) btnPrint.style.display = 'none';
                if (btnSave) btnSave.style.display = 'none';
                
                // Hide "Đã kết nối EMC" section by ID
                var ghichuDiv = document.getElementById('ghichu');
                if (ghichuDiv) ghichuDiv.style.display = 'none';
                
                // Hide instruction text at top of page (browser recommendation, etc.)
                // These texts should be hidden to match the manual PDF output
                // NOTE: Do NOT hide 'ĐỦ ĐIỀU KIỆN QUA KHU VỰC GIÁM SÁT' - this is part of the barcode title!
                // Also keep 'DANH SÁCH HÀNG HÓA' and 'Tờ khai không phải niêm phong'
                var instructionTexts = [
                    'Đề nghị sử dụng trình duyệt',
                    'IE9, Firefox',
                    'KIỂM TRA SỐ KIỆN, CONTAINER',
                    'PHƯƠNG TIỆN CHỨA HÀNG',
                    'Nhập Mã doanh nghiệp',
                    'bấm nút Lấy thông tin',
                    'kết nối EMC',
                    'Đã kết nối EMC'
                ];
                
                // Hide elements containing instruction text (leaf nodes only)
                document.querySelectorAll('span, label, div, td, p').forEach(function(elem) {
                    // Skip if element has many children (container)
                    if (elem.children.length > 3) return;
                    
                    var text = elem.innerText || elem.textContent || '';
                    if (text.length > 500) return; // Skip large containers
                    
                    for (var i = 0; i < instructionTexts.length; i++) {
                        if (text.indexOf(instructionTexts[i]) !== -1) {
                            elem.style.display = 'none';
                            break;
                        }
                    }
                });
                
                // Show the result panels (they might be hidden by default)
                var pgl2 = document.getElementById('pt1:pgl2');
                var pgl3 = document.getElementById('pt1:pgl3');
                var png1 = document.getElementById('pt1:png1');
                if (pgl2) pgl2.style.display = 'block';
                if (pgl3) pgl3.style.display = 'block';
                if (png1) png1.style.display = 'block';
                
                // Reset body/html padding and margin to move content to top
                document.body.style.backgroundColor = 'white';
                document.body.style.margin = '0';
                document.body.style.padding = '0';
                document.documentElement.style.margin = '0';
                document.documentElement.style.padding = '0';
                
                // Hide the right sidebar if exists
                var rightDiv = document.querySelector('.right');
                if (rightDiv) rightDiv.style.display = 'none';
                
                // Make left content take full width and remove top padding
                var leftDiv = document.querySelector('.left');
                if (leftDiv) {
                    leftDiv.style.width = '100%';
                    leftDiv.style.paddingTop = '0';
                    leftDiv.style.marginTop = '0';
                }
                
                // Remove padding/margin from content div
                var contentDiv = document.getElementById('content');
                if (contentDiv) {
                    contentDiv.style.paddingTop = '0';
                    contentDiv.style.marginTop = '0';
                }
                
                // Ensure PortalMainContent has no top spacing
                var mainContent = document.getElementById('PortalMainContent');
                if (mainContent) {
                    mainContent.style.minHeight = 'auto';
                    mainContent.style.paddingTop = '0';
                    mainContent.style.marginTop = '0';
                }
                
                // Remove spacing from pt1 form container
                var pt1Form = document.querySelector('[id^="pt1"]');
                if (pt1Form) {
                    pt1Form.style.paddingTop = '0';
                    pt1Form.style.marginTop = '0';
                }
                
                // Find and remove top spacing from all parent containers of result
                var resultPanels = document.querySelectorAll('[id^="pt1:pgl"], [id^="pt1:png"]');
                resultPanels.forEach(function(panel) {
                    var parent = panel.parentElement;
                    while (parent && parent !== document.body) {
                        parent.style.paddingTop = '0';
                        parent.style.marginTop = '0';
                        parent = parent.parentElement;
                    }
                });
                
                // Move entire content up by using negative margin on first visible element
                // This compensates for any remaining whitespace in the HTML
                var firstContent = document.querySelector('.left') || document.getElementById('content') || document.body.firstElementChild;
                if (firstContent) {
                    firstContent.style.marginTop = '-1in';  // Move up by 1 inch
                }
            """)
            
            self.logger.debug("Prepared print-friendly view")
            time.sleep(0.5)
            
            # Step 2: Use Chrome DevTools Protocol to print page to PDF
            try:
                import base64
                
                # Execute CDP command to print to PDF - matching manual PDF layout
                # Target: content starts at ~1-1.5in from top (ruler), width ~7.7in
                # Reduced top margin to move content up
                pdf_params = {
                    'printBackground': True,
                    'landscape': False,
                    'paperWidth': 8.27,   # A4 width in inches
                    'paperHeight': 11.69, # A4 height in inches
                    'marginTop': 0.1,     # Minimal top margin (content starts ~1-1.5in)
                    'marginBottom': 0.3,  # Small bottom margin
                    'marginLeft': 0.3,    # Small left margin
                    'marginRight': 0.3,   # Small right margin
                    'scale': 1.4,         # Scale up to match manual PDF size
                    'preferCSSPageSize': False
                }
                
                result = driver.execute_cdp_cmd('Page.printToPDF', pdf_params)
                
                if result and 'data' in result:
                    pdf_bytes = base64.b64decode(result['data'])
                    
                    # Verify it's a valid PDF
                    if pdf_bytes.startswith(b'%PDF'):
                        self.logger.info(f"Successfully generated PDF ({len(pdf_bytes)} bytes)")
                        return pdf_bytes
                    else:
                        self.logger.warning("Generated content is not a valid PDF")
                        return None
                else:
                    self.logger.warning("CDP printToPDF returned no data")
                    return None
                    
            except Exception as e:
                self.logger.warning(f"CDP printToPDF failed: {e}")
                
                # Fallback: Try to get HTML content and convert using alternative method
                return self._convert_html_to_pdf_fallback(driver)
                    
        except Exception as e:
            self.logger.debug(f"Error in _try_adf_save_link: {e}")
            return None
    
    def _convert_html_to_pdf_fallback(self, driver: webdriver.Chrome) -> Optional[bytes]:
        """
        Fallback method to convert HTML content to PDF
        
        Args:
            driver: WebDriver instance
            
        Returns:
            PDF content as bytes, or None if failed
        """
        try:
            # Get the content div HTML
            content_div = driver.find_element(By.ID, "content")
            if not content_div:
                return None
            
            html_content = content_div.get_attribute("outerHTML")
            
            # Try using weasyprint if available
            try:
                from weasyprint import HTML
                pdf_bytes = HTML(string=html_content).write_pdf()
                if pdf_bytes:
                    self.logger.info("Generated PDF using weasyprint")
                    return pdf_bytes
            except ImportError:
                self.logger.debug("weasyprint not available")
            except Exception as e:
                self.logger.debug(f"weasyprint failed: {e}")
            
            # Try using pdfkit if available
            try:
                import pdfkit
                pdf_bytes = pdfkit.from_string(html_content, False)
                if pdf_bytes:
                    self.logger.info("Generated PDF using pdfkit")
                    return pdf_bytes
            except ImportError:
                self.logger.debug("pdfkit not available")
            except Exception as e:
                self.logger.debug(f"pdfkit failed: {e}")
            
            self.logger.warning("No PDF conversion library available")
            return None
            
        except Exception as e:
            self.logger.debug(f"HTML to PDF fallback failed: {e}")
            return None
    
    def _handle_standard_website(self, driver: webdriver.Chrome, declaration: Declaration) -> Optional[bytes]:
        """
        Handle standard website with normal form submission
        
        Args:
            driver: WebDriver instance
            declaration: Declaration object
            
        Returns:
            PDF content as bytes, or None if failed
        """
        # Format date as ddmmyyyy
        date_str = declaration.declaration_date.strftime('%d%m%Y')
        
        # Fill form fields using adaptive selectors
        tax_code_selector = self._try_adaptive_selectors(driver, 'taxCode', declaration.tax_code)
        decl_num_selector = self._try_adaptive_selectors(driver, 'declarationNumber', declaration.declaration_number)
        date_selector = self._try_adaptive_selectors(driver, 'declarationDate', date_str)
        customs_selector = self._try_adaptive_selectors(driver, 'customsOffice', declaration.customs_office_code)
        
        # Check if all fields were filled successfully
        if not all([tax_code_selector, decl_num_selector, date_selector, customs_selector]):
            self.logger.error(f"Failed to fill all form fields for {declaration.id}")
            return None
        
        # Click submit button
        submit_button = self._find_submit_button(driver)
        if submit_button:
            submit_button.click()
            
            # Wait for PDF generation
            time.sleep(3)
            
            # Try to download PDF
            pdf_content = self._download_pdf(driver)
            return pdf_content
        else:
            self.logger.warning("Could not find submit button")
            return None
    
    def _setup_webdriver(self) -> webdriver.Chrome:
        """
        Set up Selenium WebDriver in headless mode with CDP support
        
        Returns:
            WebDriver instance
        """
        options = webdriver.ChromeOptions()
        # Use standard headless mode for better compatibility
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--ignore-certificate-errors')
        
        # Enable CDP for print-to-PDF functionality
        options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
        
        # Set download preferences
        prefs = {
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
            'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}'
        }
        options.add_experimental_option('prefs', prefs)
        
        driver = webdriver.Chrome(options=options)
        # Use web_timeout if available, otherwise fall back to legacy timeout
        timeout = getattr(self.config, 'web_timeout', self.config.timeout)
        driver.set_page_load_timeout(timeout)
        
        return driver
    
    def _fill_form_field(self, driver: webdriver.Chrome, value: str, 
                        possible_names: list) -> bool:
        """
        Fill a form field by trying multiple possible field names
        
        Args:
            driver: WebDriver instance
            value: Value to fill
            possible_names: List of possible field names/IDs
            
        Returns:
            True if field was filled, False otherwise
        """
        for name in possible_names:
            try:
                # Try by ID
                element = driver.find_element(By.ID, name)
                element.clear()
                element.send_keys(value)
                return True
            except:
                pass
            
            try:
                # Try by name
                element = driver.find_element(By.NAME, name)
                element.clear()
                element.send_keys(value)
                return True
            except:
                pass
        
        self.logger.warning(f"Could not find form field with names: {possible_names}")
        return False
    
    def _try_adaptive_selectors(self, driver: webdriver.Chrome, field_type: str, 
                                value: str) -> Optional[str]:
        """
        Try adaptive selectors for a field, returning the working selector
        
        Args:
            driver: WebDriver instance
            field_type: Type of field (taxCode, declarationNumber, etc.)
            value: Value to fill in the field
            
        Returns:
            The working selector name if successful, None otherwise
        """
        if field_type not in self.FIELD_SELECTORS:
            self.logger.error(f"Unknown field type: {field_type}")
            return None
        
        # Try cached selector first if cache is valid
        cached_selector = self._get_cached_selector(field_type)
        if cached_selector and self._selector_cache.is_valid():
            try:
                # Try by ID
                element = driver.find_element(By.ID, cached_selector)
                element.clear()
                element.send_keys(value)
                self.logger.debug(f"Successfully used cached selector '{cached_selector}' (by ID) for {field_type}")
                return cached_selector
            except:
                pass
            
            try:
                # Try by name
                element = driver.find_element(By.NAME, cached_selector)
                element.clear()
                element.send_keys(value)
                self.logger.debug(f"Successfully used cached selector '{cached_selector}' (by name) for {field_type}")
                return cached_selector
            except:
                self.logger.debug(f"Cached selector '{cached_selector}' failed for {field_type}, trying alternatives")
        
        # Try all selectors if cache miss or cache invalid
        selectors = self.FIELD_SELECTORS[field_type]
        
        for selector in selectors:
            try:
                # Try by ID
                element = driver.find_element(By.ID, selector)
                element.clear()
                element.send_keys(value)
                self.logger.debug(f"Successfully used selector '{selector}' (by ID) for {field_type}")
                # Cache the working selector
                self._cache_working_selector(field_type, selector)
                return selector
            except:
                pass
            
            try:
                # Try by name
                element = driver.find_element(By.NAME, selector)
                element.clear()
                element.send_keys(value)
                self.logger.debug(f"Successfully used selector '{selector}' (by name) for {field_type}")
                # Cache the working selector
                self._cache_working_selector(field_type, selector)
                return selector
            except:
                pass
        
        self.logger.error(f"All selectors failed for {field_type}: {selectors}")
        # Log HTML structure for debugging
        self._log_html_structure_on_failure(driver, field_type)
        return None
    
    def _get_cached_selector(self, field_type: str) -> Optional[str]:
        """
        Get cached selector for a field type
        
        Args:
            field_type: Type of field (taxCode, declarationNumber, etc.)
            
        Returns:
            Cached selector name if available, None otherwise
        """
        field_map = {
            'taxCode': self._selector_cache.tax_code_selector,
            'declarationNumber': self._selector_cache.declaration_number_selector,
            'declarationDate': self._selector_cache.declaration_date_selector,
            'customsOffice': self._selector_cache.customs_office_selector
        }
        return field_map.get(field_type)
    
    def _cache_working_selector(self, field_type: str, selector: str) -> None:
        """
        Cache a working selector for future use
        
        Args:
            field_type: Type of field (taxCode, declarationNumber, etc.)
            selector: The working selector name
        """
        if field_type == 'taxCode':
            self._selector_cache.tax_code_selector = selector
        elif field_type == 'declarationNumber':
            self._selector_cache.declaration_number_selector = selector
        elif field_type == 'declarationDate':
            self._selector_cache.declaration_date_selector = selector
        elif field_type == 'customsOffice':
            self._selector_cache.customs_office_selector = selector
        
        # Update last_updated timestamp
        self._selector_cache.last_updated = datetime.now()
        self.logger.debug(f"Cached selector '{selector}' for {field_type}")
    
    def _log_html_structure_on_failure(self, driver: webdriver.Chrome, field_name: str) -> None:
        """
        Log HTML structure when selectors fail for debugging
        
        Args:
            driver: WebDriver instance
            field_name: Name of the field that failed
        """
        try:
            self.logger.error(f"=== HTML Structure Debug Info for failed field: {field_name} ===")
            self.logger.debug(f"Page title: {driver.title}")
            self.logger.debug(f"Current URL: {driver.current_url}")
            
            # Log all forms on the page
            forms = driver.find_elements(By.TAG_NAME, 'form')
            self.logger.debug(f"Found {len(forms)} form(s) on page")
            
            for i, form in enumerate(forms):
                try:
                    form_html = form.get_attribute('outerHTML')
                    # Truncate to first 500 characters to avoid log overflow
                    form_snippet = form_html[:500] if form_html else "No HTML"
                    self.logger.debug(f"Form {i}: {form_snippet}...")
                except Exception as e:
                    self.logger.debug(f"Form {i}: Could not get HTML - {e}")
            
            # Log all input fields
            inputs = driver.find_elements(By.TAG_NAME, 'input')
            self.logger.debug(f"Found {len(inputs)} input field(s) on page")
            
            for inp in inputs:
                try:
                    input_id = inp.get_attribute('id') or 'N/A'
                    input_name = inp.get_attribute('name') or 'N/A'
                    input_type = inp.get_attribute('type') or 'N/A'
                    input_class = inp.get_attribute('class') or 'N/A'
                    self.logger.debug(
                        f"Input: id='{input_id}', name='{input_name}', "
                        f"type='{input_type}', class='{input_class}'"
                    )
                except Exception as e:
                    self.logger.debug(f"Input: Could not get attributes - {e}")
            
            # Log all select fields
            selects = driver.find_elements(By.TAG_NAME, 'select')
            self.logger.debug(f"Found {len(selects)} select field(s) on page")
            
            for sel in selects:
                try:
                    select_id = sel.get_attribute('id') or 'N/A'
                    select_name = sel.get_attribute('name') or 'N/A'
                    self.logger.debug(f"Select: id='{select_id}', name='{select_name}'")
                except Exception as e:
                    self.logger.debug(f"Select: Could not get attributes - {e}")
            
            self.logger.error(f"=== End HTML Structure Debug Info ===")
            
        except Exception as e:
            self.logger.error(f"Failed to log HTML structure: {e}")
    
    def _find_submit_button(self, driver: webdriver.Chrome) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        Find the submit button on the page
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Submit button element, or None if not found
        """
        # Try specific button IDs first (from website analysis December 2024)
        button_ids = [
            'Button1',  # Backup website (pus1.customs.gov.vn)
            'pt1:cb1',  # Primary website Oracle ADF
            'pt1:commandButton1',
        ]
        
        for btn_id in button_ids:
            try:
                button = driver.find_element(By.ID, btn_id)
                self.logger.debug(f"Found submit button by ID: {btn_id}")
                return button
            except:
                pass
        
        # Try common button texts
        button_texts = ['Lấy thông tin', 'Tìm kiếm', 'Submit', 'Search', 'Get Barcode', 'Xem', 'Tra cứu']
        
        for text in button_texts:
            try:
                button = driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                return button
            except:
                pass
            
            try:
                button = driver.find_element(By.XPATH, f"//input[@type='submit' and contains(@value, '{text}')]")
                return button
            except:
                pass
            
            try:
                # Try link that looks like button
                button = driver.find_element(By.XPATH, f"//a[contains(text(), '{text}')]")
                return button
            except:
                pass
        
        # Try generic submit button
        try:
            button = driver.find_element(By.XPATH, "//button[@type='submit']")
            return button
        except:
            pass
        
        try:
            button = driver.find_element(By.XPATH, "//input[@type='submit']")
            return button
        except:
            pass
        
        # Try any button
        try:
            button = driver.find_element(By.XPATH, "//input[@type='button']")
            return button
        except:
            pass
        
        return None
    
    def _download_pdf(self, driver: webdriver.Chrome) -> Optional[bytes]:
        """
        Download PDF from the page
        
        Args:
            driver: WebDriver instance
            
        Returns:
            PDF content as bytes, or None if failed
        """
        try:
            # Look for PDF link or iframe
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            if pdf_links:
                pdf_url = pdf_links[0].get_attribute('href')
                timeout = getattr(self.config, 'web_timeout', self.config.timeout)
                response = self.session.get(pdf_url, timeout=timeout)
                if response.status_code == 200:
                    return response.content
            
            # Look for iframe with PDF
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src and '.pdf' in src:
                    timeout = getattr(self.config, 'web_timeout', self.config.timeout)
                    response = self.session.get(src, timeout=timeout)
                    if response.status_code == 200:
                        return response.content
            
            # Try to get PDF from current page if it's a PDF
            if 'application/pdf' in driver.page_source or driver.current_url.endswith('.pdf'):
                timeout = getattr(self.config, 'web_timeout', self.config.timeout)
                response = self.session.get(driver.current_url, timeout=timeout)
                if response.status_code == 200:
                    return response.content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download PDF: {e}")
            return None
    
    def _should_try_method(self, method_name: str) -> bool:
        """
        Check if a method should be tried based on failure count
        
        Args:
            method_name: Name of the method ('api', 'primary_web', 'backup_web')
            
        Returns:
            True if method should be tried, False if it should be skipped
        """
        return self._failed_methods.get(method_name, 0) < self._skip_threshold
    
    def _record_method_failure(self, method_name: str) -> None:
        """
        Record a method failure
        
        Args:
            method_name: Name of the method that failed
        """
        self._failed_methods[method_name] = self._failed_methods.get(method_name, 0) + 1
        if self._failed_methods[method_name] >= self._skip_threshold:
            self.logger.warning(
                f"Method '{method_name}' has failed {self._failed_methods[method_name]} times, "
                f"will be skipped for remaining declarations in this batch"
            )
    
    def _record_method_success(self, method_name: str) -> None:
        """
        Record a method success (resets failure count)
        
        Args:
            method_name: Name of the method that succeeded
        """
        self._failed_methods[method_name] = 0
    
    def reset_method_skip_list(self) -> None:
        """
        Reset the method skip list for a new batch
        
        This should be called at the start of processing a new batch of declarations
        """
        self._failed_methods = {
            'api': 0,
            'web': 0,
            'primary_web': 0,
            'backup_web': 0
        }
        self.logger.debug("Method skip list reset for new batch")
    
    def set_retrieval_method(self, method: str) -> None:
        """
        Change the retrieval method at runtime.
        
        Args:
            method: 'api', 'web', or 'auto'
        """
        try:
            self.retrieval_method = RetrievalMethod(method.lower())
            self.logger.info(f"Retrieval method changed to: {self.retrieval_method.value}")
        except ValueError:
            self.logger.warning(f"Invalid retrieval method '{method}', keeping current: {self.retrieval_method.value}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self._webdriver:
            try:
                self._webdriver.quit()
            except:
                pass
            self._webdriver = None
        
        # Close HTTP session
        if hasattr(self, 'session'):
            try:
                self.session.close()
                self.logger.debug("HTTP session closed")
            except:
                pass
        
        # Close API client
        if hasattr(self, '_api_client'):
            try:
                self._api_client.close()
                self.logger.debug("API client closed")
            except:
                pass
