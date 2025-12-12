"""
QRCode API Client Module

This module provides a client for the Customs QRCode SOAP WebService API.
Based on WSDL analysis from http://103.248.160.25:8086/WS_Container/QRCode.asmx?WSDL

The API provides container/declaration information for barcode generation.
"""

import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from logging_system.logger import Logger


@dataclass
class ContainerInfo:
    """Information about a container in the declaration"""
    stt: int = 0
    so_container: str = ""
    so_seal: str = ""
    so_seal_hq: str = ""
    trong_luong: float = 0.0
    barcode_image: str = ""  # Base64 encoded PNG for QR code
    ghi_chu: str = ""
    
    
@dataclass
class ContainerDeclarationInfo:
    """
    Data class containing declaration information from QRCode API.
    
    Maps to ServiceMessage type in WSDL.
    """
    # Basic declaration info
    ma_so_thue: str = ""
    so_to_khai: str = ""
    ngay_to_khai: str = ""
    
    # Company info
    ten_don_vi_xnk: str = ""
    
    # Customs info
    ma_hai_quan_gs: str = ""
    ten_chi_cuc_hai_quan_gs: str = ""
    ten_cuc_hai_quan: str = ""
    ten_chi_cuc_hai_quan: str = ""
    
    # Declaration type and status
    loai_hinh: str = ""
    ten_loai_hinh: str = ""
    ma_trang_thai_to_khai: str = ""
    trang_thai_to_khai: str = ""
    luong_to_khai: str = ""
    
    # Cargo info
    so_luong_hang: float = 0.0
    tong_trong_luong_hang: float = 0.0
    dvt_so_luong_hang: str = ""
    dvt_tong_trong_luong_hang: str = ""
    
    # Container/Transport info
    is_container: int = 0
    so_dinh_danh: str = ""
    ma_ptvc: str = ""
    ngay_tau: str = ""
    ma_ddgs: str = ""
    ten_ddgs: str = ""
    
    # Notes and metadata
    ghi_chu: str = ""
    thoi_gian_lay_du_lieu: str = ""
    thong_bao_loi: str = ""
    
    # Container list (from BangKe)
    containers: List[ContainerInfo] = field(default_factory=list)
    
    @property
    def has_error(self) -> bool:
        """Check if response contains an error"""
        return bool(self.thong_bao_loi)
    
    @property
    def is_valid(self) -> bool:
        """Check if declaration info is valid"""
        return bool(self.so_to_khai and self.ma_so_thue and not self.has_error)
    
    @property
    def is_container_declaration(self) -> bool:
        """Check if this is a container declaration (MaPTVC = 2)"""
        return str(self.ma_ptvc) == "2"


class QRCodeApiError(Exception):
    """Exception raised for QRCode API errors"""
    pass


class QRCodeContainerApiClient:
    """
    Client for the Customs QRCode SOAP WebService API.
    
    Provides methods to query container/declaration information
    for barcode generation.
    """
    
    # Default service URL (port 80, not 8086 which is internal only)
    DEFAULT_SERVICE_URL = "http://103.248.160.25/WS_Container/QRCode.asmx"
    
    # SOAP namespaces
    SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    TEMPURI_NS = "http://tempuri.org/"
    
    def __init__(self, service_url: str = None, logger: Logger = None, timeout: int = 30):
        """
        Initialize the QRCode API client.
        
        Args:
            service_url: SOAP service URL. Defaults to DEFAULT_SERVICE_URL.
            logger: Logger instance for logging. If None, creates a default logger.
            timeout: Request timeout in seconds.
        """
        self.service_url = service_url or self.DEFAULT_SERVICE_URL
        self.logger = logger or Logger()
        self.timeout = timeout
        
        # Initialize HTTP session with connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'Accept': 'text/xml'
        })
    
    def query_bang_ke(
        self, 
        ma_so_thue: str, 
        so_to_khai: str, 
        ma_hai_quan: str, 
        ngay_dang_ky: date
    ) -> Optional[ContainerDeclarationInfo]:
        """
        Query declaration information using QueryBangKeDanhSachContainer method.
        
        Args:
            ma_so_thue: Tax code (Mã số thuế / Mã doanh nghiệp)
            so_to_khai: Declaration number (Số tờ khai)
            ma_hai_quan: Customs office code (Mã hải quan)
            ngay_dang_ky: Registration date (Ngày đăng ký)
            
        Returns:
            ContainerDeclarationInfo object if successful, None if failed.
            
        Raises:
            QRCodeApiError: If API request fails with error.
        """
        try:
            # Build SOAP request
            soap_request = self._build_soap_request(
                ma_so_thue, so_to_khai, ma_hai_quan, ngay_dang_ky
            )
            
            self.logger.debug(f"Sending SOAP request to {self.service_url}")
            self.logger.debug(f"Request params: MST={ma_so_thue}, TK={so_to_khai}, HQ={ma_hai_quan}, Date={ngay_dang_ky}")
            
            # Send request
            response = self.session.post(
                self.service_url,
                data=soap_request.encode('utf-8'),
                headers={
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': 'http://tempuri.org/QueryBangKeDanhSachContainer'
                },
                timeout=self.timeout
            )
            
            # Check HTTP status
            if response.status_code != 200:
                self.logger.error(f"API returned HTTP {response.status_code}: {response.text[:500]}")
                raise QRCodeApiError(f"HTTP {response.status_code}: {response.reason}")
            
            # Debug: log raw response
            self.logger.debug(f"Raw API response: {response.text[:2000]}")
            
            # Parse response
            result = self._parse_soap_response(response.text)
            
            if result:
                if result.has_error:
                    self.logger.warning(f"API returned error: {result.thong_bao_loi}")
                elif result.is_valid:
                    self.logger.info(f"Successfully retrieved declaration info for {so_to_khai}")
                else:
                    self.logger.warning(f"No valid data returned for {so_to_khai}")
                
            return result
            
        except requests.Timeout:
            self.logger.error(f"API request timed out after {self.timeout}s")
            raise QRCodeApiError(f"Request timed out after {self.timeout}s")
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise QRCodeApiError(f"Request failed: {e}")
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse API response: {e}")
            raise QRCodeApiError(f"Invalid XML response: {e}")
    
    def _build_soap_request(
        self, 
        ma_so_thue: str, 
        so_to_khai: str, 
        ma_hai_quan: str, 
        ngay_dang_ky: date
    ) -> str:
        """
        Build SOAP envelope for QueryBangKeDanhSachContainer request.
        
        Args:
            ma_so_thue: Tax code
            so_to_khai: Declaration number
            ma_hai_quan: Customs office code
            ngay_dang_ky: Registration date
            
        Returns:
            SOAP XML request as string.
        """
        # Format date as ISO datetime (required by WSDL: s:dateTime)
        # Use midnight of the given date
        if isinstance(ngay_dang_ky, datetime):
            date_iso = ngay_dang_ky.strftime('%Y-%m-%dT00:00:00')
        else:
            date_iso = ngay_dang_ky.strftime('%Y-%m-%dT00:00:00')
        
        soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" 
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <soap:Body>
    <QueryBangKeDanhSachContainer xmlns="http://tempuri.org/">
      <Ma_Doanh_Nghiep>{ma_so_thue}</Ma_Doanh_Nghiep>
      <TK_ID>{so_to_khai}</TK_ID>
      <Ma_HQ>{ma_hai_quan}</Ma_HQ>
      <Ngay_DK>{date_iso}</Ngay_DK>
    </QueryBangKeDanhSachContainer>
  </soap:Body>
</soap:Envelope>"""
        
        return soap_envelope
    
    def _parse_soap_response(self, response_text: str) -> Optional[ContainerDeclarationInfo]:
        """
        Parse SOAP response and extract ContainerDeclarationInfo.
        
        Args:
            response_text: SOAP XML response as string.
            
        Returns:
            ContainerDeclarationInfo object, or None if parsing fails.
        """
        try:
            # Parse XML
            root = ET.fromstring(response_text)
            
            # Define namespaces
            namespaces = {
                'soap': self.SOAP_NS,
                'ns': self.TEMPURI_NS
            }
            
            # Find QueryBangKeDanhSachContainerResult element
            result_elem = root.find('.//ns:QueryBangKeDanhSachContainerResult', namespaces)
            
            if result_elem is None:
                # Try without namespace prefix
                result_elem = root.find('.//{http://tempuri.org/}QueryBangKeDanhSachContainerResult')
            
            if result_elem is None:
                self.logger.warning("No QueryBangKeDanhSachContainerResult found in response")
                return None
            
            # Extract fields into dataclass
            info = ContainerDeclarationInfo()
            
            # Map XML elements to dataclass fields
            field_mapping = {
                'MaSoThue': 'ma_so_thue',
                'SoToKhai': 'so_to_khai',
                'NgayToKhai': 'ngay_to_khai',
                'TenDonViXNK': 'ten_don_vi_xnk',
                'MaDDGS': 'ma_ddgs',
                'TenDDGS': 'ten_ddgs',
                'TenChiCucHaiQuanGS': 'ten_chi_cuc_hai_quan_gs',
                'TenCucHaiQuan': 'ten_cuc_hai_quan',
                'TenChiCucHaiQuan': 'ten_chi_cuc_hai_quan',
                'LoaiHinh': 'loai_hinh',
                'TenLoaiHinh': 'ten_loai_hinh',
                'MaTrangThaiToKhai': 'ma_trang_thai_to_khai',
                'TrangThaiToKhai': 'trang_thai_to_khai',
                'LuongToKhai': 'luong_to_khai',
                'So_Luong_Hang': 'so_luong_hang',
                'Tong_Trong_Luong_Hang': 'tong_trong_luong_hang',
                'DVT_So_Luong_Hang': 'dvt_so_luong_hang',
                'DVT_Tong_Trong_Luong_Hang': 'dvt_tong_trong_luong_hang',
                'IsContainer': 'is_container',
                'SoDinhDanh': 'so_dinh_danh',
                'MaPTVC': 'ma_ptvc',
                'NgayTau': 'ngay_tau',
                'Ghi_Chu': 'ghi_chu',
                'ThoiGianLayDuLieu': 'thoi_gian_lay_du_lieu',
                'ThongBaoLoi': 'thong_bao_loi'
            }
            
            for xml_name, attr_name in field_mapping.items():
                # Try with namespace first, then without
                elem = result_elem.find(f'ns:{xml_name}', namespaces)
                if elem is None:
                    elem = result_elem.find(xml_name)
                if elem is None:
                    # Try with full namespace
                    elem = result_elem.find(f'{{{self.TEMPURI_NS}}}{xml_name}')
                
                if elem is not None and elem.text:
                    value = elem.text
                    # Convert numeric fields
                    if attr_name in ('so_luong_hang', 'tong_trong_luong_hang'):
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0.0
                    elif attr_name == 'is_container':
                        try:
                            value = int(value)
                        except ValueError:
                            value = 0
                    setattr(info, attr_name, value)
            
            # Parse BangKe (container list) if present
            bang_ke_elem = result_elem.find('BangKe')
            if bang_ke_elem is None:
                bang_ke_elem = result_elem.find(f'{{{self.TEMPURI_NS}}}BangKe')
            if bang_ke_elem is not None:
                info.containers = self._parse_bang_ke(bang_ke_elem)
            
            return info
            
        except ET.ParseError as e:
            self.logger.error(f"XML parse error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return None
    
    def _parse_bang_ke(self, bang_ke_elem: ET.Element) -> List[ContainerInfo]:
        """
        Parse BangKe element to extract container list.
        
        Args:
            bang_ke_elem: BangKe XML element.
            
        Returns:
            List of ContainerInfo objects.
        """
        containers = []
        
        try:
            # BangKe contains a diffgram with container data
            # Look for Table_BangKe elements inside diffgram/DocumentElement
            for table in bang_ke_elem.iter():
                if 'Table_BangKe' in table.tag or 'Table' in table.tag:
                    container = ContainerInfo()
                    
                    # Parse Stt (sequence number)
                    stt_elem = table.find('Stt')
                    if stt_elem is not None and stt_elem.text:
                        try:
                            container.stt = int(stt_elem.text)
                        except ValueError:
                            pass
                    
                    # Parse SoContainer (trim whitespace)
                    so_cont = table.find('SoContainer')
                    if so_cont is not None and so_cont.text:
                        container.so_container = so_cont.text.strip()
                    else:
                        # Try old field name
                        so_cont = table.find('So_Container')
                        if so_cont is not None and so_cont.text:
                            container.so_container = so_cont.text.strip()
                    
                    # Parse SoSeal (trim whitespace)
                    so_seal = table.find('SoSeal')
                    if so_seal is not None and so_seal.text:
                        container.so_seal = so_seal.text.strip()
                    else:
                        # Try old field name
                        so_seal = table.find('So_Seal')
                        if so_seal is not None and so_seal.text:
                            container.so_seal = so_seal.text.strip()
                    
                    # Parse SoSealHQ (customs seal)
                    so_seal_hq = table.find('SoSealHQ')
                    if so_seal_hq is not None and so_seal_hq.text:
                        # Handle "#####" as empty
                        seal_hq_value = so_seal_hq.text.strip()
                        if seal_hq_value != "#####":
                            container.so_seal_hq = seal_hq_value
                    
                    # Parse BarcodeImage (base64 encoded PNG)
                    barcode_img = table.find('BarcodeImage')
                    if barcode_img is not None and barcode_img.text:
                        container.barcode_image = barcode_img.text
                    
                    # Parse GhiChu (notes)
                    ghi_chu = table.find('GhiChu')
                    if ghi_chu is not None and ghi_chu.text:
                        container.ghi_chu = ghi_chu.text
                    
                    # Parse Trong_Luong (weight) - for backward compatibility
                    trong_luong = table.find('Trong_Luong')
                    if trong_luong is not None and trong_luong.text:
                        try:
                            container.trong_luong = float(trong_luong.text)
                        except ValueError:
                            pass
                    
                    if container.so_container:
                        containers.append(container)
                        
        except Exception as e:
            self.logger.debug(f"Error parsing BangKe: {e}")
        
        return containers
    
    def test_connection(self) -> bool:
        """
        Test connection to the API service.
        
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            # Send a simple request to check if service is available
            response = self.session.get(
                self.service_url,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Close the HTTP session."""
        if hasattr(self, 'session'):
            self.session.close()
