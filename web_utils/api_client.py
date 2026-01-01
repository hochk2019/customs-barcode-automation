"""
Barcode API Client v2.0

Clean SOAP API client extracted from BarcodeRetriever.
Handles QR code data retrieval from customs SOAP service.

Benefits:
1. Single responsibility - only SOAP communication
2. Easy to mock for testing
3. Circuit breaker ready
"""

import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from datetime import datetime
import threading

from models.config_models import BarcodeServiceConfig
from logging_system.logger import Logger


@dataclass
class QRCodeData:
    """QR code data from SOAP API."""
    declaration_number: str
    tax_code: str
    qr_data: Optional[str] = None
    raw_response: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None


class CircuitBreaker:
    """
    Simple circuit breaker for API calls.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failing, reject all calls
    - HALF_OPEN: Testing if service is back
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self._failures = 0
        self._last_failure_time: Optional[datetime] = None
        self._state = "CLOSED"
        self._lock = threading.Lock()
    
    @property
    def is_open(self) -> bool:
        with self._lock:
            if self._state == "OPEN":
                # Check if we should try again
                if self._last_failure_time:
                    elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                    if elapsed > self.recovery_timeout:
                        self._state = "HALF_OPEN"
                        return False
                return True
            return False
    
    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = "CLOSED"
    
    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            self._last_failure_time = datetime.now()
            if self._failures >= self.failure_threshold:
                self._state = "OPEN"
    
    def reset(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = "CLOSED"
            self._last_failure_time = None


class BarcodeApiClient:
    """
    SOAP API client for customs barcode service.
    
    Provides clean interface for retrieving QR code data
    from the customs SOAP web service.
    """
    
    def __init__(
        self,
        config: BarcodeServiceConfig,
        logger: Logger,
        timeout: int = 30
    ):
        """
        Initialize API client.
        
        Args:
            config: Barcode service configuration
            logger: Logger instance
            timeout: Request timeout in seconds
        """
        self.config = config
        self.logger = logger
        self.timeout = timeout
        
        # Session with connection pooling
        self._session = requests.Session()
        self._session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': '"http://tempuri.org/GetData"'
        })
        
        # Circuit breaker for resilience
        self.circuit_breaker = CircuitBreaker()
    
    def get_qr_data(self, tax_code: str, declaration_number: str) -> QRCodeData:
        """
        Get QR code data for a declaration.
        
        Args:
            tax_code: Company tax code
            declaration_number: Declaration number
            
        Returns:
            QRCodeData with result or error
        """
        result = QRCodeData(
            declaration_number=declaration_number,
            tax_code=tax_code
        )
        
        # Check circuit breaker
        if self.circuit_breaker.is_open:
            result.error_message = "API circuit breaker is open"
            self.logger.warning(f"Circuit breaker open, skipping API call for {declaration_number}")
            return result
        
        try:
            # Build SOAP request
            soap_request = self._build_soap_request(tax_code, declaration_number)
            
            # Make request
            response = self._session.post(
                self.config.url,
                data=soap_request,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            qr_data = self._parse_soap_response(response.text)
            
            if qr_data:
                result.qr_data = qr_data
                result.raw_response = response.text
                result.success = True
                self.circuit_breaker.record_success()
                self.logger.debug(f"API success for {declaration_number}")
            else:
                result.error_message = "No QR data in response"
                self.circuit_breaker.record_failure()
                
        except requests.Timeout:
            result.error_message = "API timeout"
            self.circuit_breaker.record_failure()
            self.logger.warning(f"API timeout for {declaration_number}")
            
        except requests.RequestException as e:
            result.error_message = f"API error: {str(e)}"
            self.circuit_breaker.record_failure()
            self.logger.error(f"API error for {declaration_number}: {e}")
            
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
            self.circuit_breaker.record_failure()
            self.logger.error(f"Unexpected error for {declaration_number}: {e}", exc_info=True)
        
        return result
    
    def _build_soap_request(self, tax_code: str, declaration_number: str) -> str:
        """Build SOAP XML request."""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <GetData xmlns="http://tempuri.org/">
            <taxCode>{tax_code}</taxCode>
            <declarationNumber>{declaration_number}</declarationNumber>
        </GetData>
    </soap:Body>
</soap:Envelope>"""
    
    def _parse_soap_response(self, response_text: str) -> Optional[str]:
        """
        Parse SOAP response to extract QR data.
        
        Args:
            response_text: Raw SOAP XML response
            
        Returns:
            QR data string or None
        """
        try:
            # Remove SOAP wrapper namespaces for easier parsing
            root = ET.fromstring(response_text)
            
            # Find the GetDataResult element
            for elem in root.iter():
                if 'GetDataResult' in elem.tag:
                    return elem.text
                    
            return None
            
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse SOAP response: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test if API is reachable.
        
        Returns:
            True if API responds, False otherwise
        """
        try:
            response = self._session.get(
                self.config.url,
                timeout=5
            )
            return response.status_code < 500
        except Exception:
            return False
    
    def close(self) -> None:
        """Close the session."""
        self._session.close()
