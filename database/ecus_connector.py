"""
ECUS5 Database Connector

This module handles all interactions with the ECUS5 SQL Server database,
including connection management and declaration data extraction.
"""

import pyodbc
from typing import List, Set, Optional
from datetime import datetime, timedelta
import time

from models.config_models import DatabaseConfig
from models.declaration_models import Declaration
from logging_system.logger import Logger


class DatabaseConnectionError(Exception):
    """Exception raised for database connection errors"""
    pass


class EcusDataConnector:
    """Handles all interactions with ECUS5 SQL Server database"""
    
    def __init__(self, config: DatabaseConfig, logger: Optional[Logger] = None):
        """
        Initialize ECUS5 data connector
        
        Args:
            config: Database configuration
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger
        self._connection: Optional[pyodbc.Connection] = None
        self._last_connection_attempt: Optional[datetime] = None
        self._reconnect_delay = 30  # seconds
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Helper method to log messages if logger is available"""
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message, **kwargs)
    
    def connect(self) -> bool:
        """
        Establish connection to ECUS5 database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._log('info', f"Connecting to database: {self.config.server}/{self.config.database}")
            
            connection_string = self.config.connection_string
            self._connection = pyodbc.connect(connection_string)
            self._last_connection_attempt = datetime.now()
            
            self._log('info', "Database connection established successfully")
            return True
            
        except pyodbc.Error as e:
            self._last_connection_attempt = datetime.now()
            self._log('error', f"Failed to connect to database: {e}", exc_info=True)
            return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self._connection:
            try:
                self._connection.close()
                self._log('info', "Database connection closed")
            except Exception as e:
                self._log('warning', f"Error closing database connection: {e}")
            finally:
                self._connection = None
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to the database
        
        Returns:
            True if reconnection successful, False otherwise
        """
        # Check if we should wait before reconnecting
        if self._last_connection_attempt:
            time_since_last_attempt = (datetime.now() - self._last_connection_attempt).total_seconds()
            if time_since_last_attempt < self._reconnect_delay:
                wait_time = self._reconnect_delay - time_since_last_attempt
                self._log('info', f"Waiting {wait_time:.1f}s before reconnection attempt")
                time.sleep(wait_time)
        
        self._log('info', "Attempting to reconnect to database")
        self.disconnect()
        return self.connect()
    
    def test_connection(self) -> bool:
        """
        Test if database connection is active
        
        Returns:
            True if connection is active, False otherwise
        """
        if not self._connection:
            return False
        
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except pyodbc.Error:
            return False
    
    def _ensure_connection(self) -> None:
        """
        Ensure database connection is active, reconnect if necessary
        
        Raises:
            DatabaseConnectionError: If connection cannot be established
        """
        if not self.test_connection():
            self._log('warning', "Database connection lost, attempting to reconnect")
            if not self.reconnect():
                raise DatabaseConnectionError("Failed to establish database connection")

    
    def get_declarations_by_date_range(self, from_date: datetime, to_date: datetime, tax_codes: Optional[List[str]] = None, include_pending: bool = False) -> List[Declaration]:
        """
        Extract declarations from ECUS5 database by date range
        
        Args:
            from_date: Start date
            to_date: End date
            tax_codes: Optional list of tax codes to filter by
            include_pending: If True, include declarations that are routed but not yet cleared (TTTK != 'T')
            
        Returns:
            List of Declaration objects (unique declarations only)
        """
        self._ensure_connection()
        
        try:
            cursor = self._connection.cursor()
            
            # Build SQL query with DISTINCT to prevent duplicates
            # Use subquery with ROW_NUMBER to select one record per unique declaration
            # Column mapping from DTOKHAIMD table:
            # - TTTK_HQ: Trạng thái tờ khai (e.g., "Đã chấp nhận thông quan")
            # - MA_LH: Mã loại hình (e.g., A11, A12, B11)
            # - VAN_DON: Số vận đơn
            # - SO_HDTM: Số hóa đơn thương mại (NOT SO_HD which is contract number)
            
            # Status filter: 
            # - Default: only cleared declarations (TTTK = 'T')
            # - With include_pending: also include routed but not cleared (PLUONG is set but TTTK != 'T')
            if include_pending:
                status_filter = "(tk.PLUONG = 'Xanh' OR tk.PLUONG = 'Vang' OR tk.PLUONG = 'Do')"
            else:
                status_filter = "tk.TTTK = 'T' AND (tk.PLUONG = 'Xanh' OR tk.PLUONG = 'Vang')"
            
            query = f"""
                SELECT 
                    declaration_number,
                    tax_code,
                    declaration_date,
                    customs_office_code,
                    transport_method,
                    channel,
                    status,
                    goods_description,
                    status_name,
                    declaration_type,
                    bill_of_lading,
                    invoice_number,
                    so_hstk
                FROM (
                    SELECT 
                        tk.SOTK as declaration_number,
                        tk.MA_DV as tax_code,
                        tk.NGAY_DK as declaration_date,
                        tk.MA_HQ as customs_office_code,
                        tk.MA_PTVT as transport_method,
                        tk.PLUONG as channel,
                        tk.TTTK as status,
                        hh.TEN_HANG as goods_description,
                        tk.TTTK_HQ as status_name,
                        tk.MA_LH as declaration_type,
                        tk.VAN_DON as bill_of_lading,
                        tk.SO_HDTM as invoice_number,
                        tk.SoHSTK as so_hstk,
                        ROW_NUMBER() OVER (
                            PARTITION BY tk.SOTK, tk.MA_DV, tk.NGAY_DK, tk.MA_HQ 
                            ORDER BY tk._DToKhaiMDID
                        ) as rn
                    FROM DTOKHAIMD tk
                    LEFT JOIN DHANGMDDK hh ON tk._DToKhaiMDID = hh._DToKhaiMDID
                    WHERE tk.NGAY_DK >= ? AND tk.NGAY_DK <= ?
                        AND {status_filter}
            """
            
            # Add tax code filter if provided
            params = [from_date, to_date]
            if tax_codes and len(tax_codes) > 0:
                placeholders = ','.join(['?' for _ in tax_codes])
                query += f" AND tk.MA_DV IN ({placeholders})"
                params.extend(tax_codes)
            
            query += """
                ) AS ranked
                WHERE rn = 1
                ORDER BY declaration_date DESC
            """
            
            self._log('debug', f"Executing query from {from_date} to {to_date}" + 
                     (f" for {len(tax_codes)} tax codes" if tax_codes else ""))
            cursor.execute(query, params)
            
            declarations = []
            row_count = 0
            
            for row in cursor:
                row_count += 1
                declaration = self._map_row_to_declaration(row)
                declarations.append(declaration)
            
            cursor.close()
            
            self._log('info', f"Fetched {row_count} unique declarations from database")
            return declarations
            
        except Exception as e:
            self._log('error', f"Database query failed: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to query declarations: {e}")
    
    def get_new_declarations(self, processed_ids: Set[str], days_back: int = 7, tax_codes: Optional[List[str]] = None) -> List[Declaration]:
        """
        Extract new declarations from ECUS5 database
        
        Args:
            processed_ids: Set of already processed declaration IDs
            days_back: Number of days to look back (default: 7)
            tax_codes: Optional list of tax codes to filter by
            
        Returns:
            List of Declaration objects
            
        Raises:
            DatabaseConnectionError: If database connection fails
        """
        self._ensure_connection()
        
        try:
            cursor = self._connection.cursor()
            
            # Build SQL query with optional tax code filter
            query = """
                SELECT 
                    tk.SOTK as declaration_number,
                    tk.MA_DV as tax_code,
                    tk.NGAY_DK as declaration_date,
                    tk.MA_HQ as customs_office_code,
                    tk.MA_PTVT as transport_method,
                    tk.PLUONG as channel,
                    tk.TTTK as status,
                    hh.TEN_HANG as goods_description
                FROM DTOKHAIMD tk
                LEFT JOIN DHANGMDDK hh ON tk._DToKhaiMDID = hh._DToKhaiMDID
                WHERE tk.NGAY_DK >= DATEADD(day, ?, GETDATE())
                    AND tk.TTTK = 'T'
                    AND (tk.PLUONG = 'Xanh' OR tk.PLUONG = 'Vang')
            """
            
            # Add tax code filter if provided
            params = [-days_back]
            if tax_codes and len(tax_codes) > 0:
                placeholders = ','.join(['?' for _ in tax_codes])
                query += f" AND tk.MA_DV IN ({placeholders})"
                params.extend(tax_codes)
            
            query += " ORDER BY tk.NGAY_DK DESC"
            
            self._log('debug', f"Executing query to fetch declarations from last {days_back} days" + 
                     (f" for {len(tax_codes)} tax codes" if tax_codes else ""))
            cursor.execute(query, params)
            
            declarations = []
            row_count = 0
            
            for row in cursor:
                row_count += 1
                
                # Create Declaration object
                declaration = self._map_row_to_declaration(row)
                
                # Skip if already processed
                if declaration.id not in processed_ids:
                    declarations.append(declaration)
            
            cursor.close()
            
            self._log('info', f"Fetched {row_count} declarations from database, {len(declarations)} are new")
            return declarations
            
        except pyodbc.Error as e:
            self._log('error', f"Database query failed: {e}", exc_info=True)
            raise DatabaseConnectionError(f"Failed to query declarations: {e}")
    
    def scan_all_companies(self, days_back: int = 90) -> List[tuple]:
        """
        Scan database and get all unique companies from recent declarations
        
        Args:
            days_back: Number of days to look back (default: 90)
            
        Returns:
            List of tuples (tax_code, company_name)
        """
        self._ensure_connection()
        
        try:
            cursor = self._connection.cursor()
            
            # Query to get unique tax codes and company names from recent declarations
            # Company name is stored in _Ten_DV_L1 column in DTOKHAIMD table
            query = """
                SELECT DISTINCT 
                    MA_DV as tax_code,
                    _Ten_DV_L1 as company_name
                FROM DTOKHAIMD
                WHERE NGAY_DK >= DATEADD(day, ?, GETDATE())
                    AND MA_DV IS NOT NULL
                    AND MA_DV != ''
                ORDER BY MA_DV
            """
            
            self._log('debug', f"Scanning companies from last {days_back} days")
            cursor.execute(query, (-days_back,))
            
            companies = []
            for row in cursor:
                tax_code = str(row.tax_code).strip() if row.tax_code else ""
                company_name = str(row.company_name).strip() if row.company_name else f"Công ty {tax_code}"
                
                if tax_code:
                    companies.append((tax_code, company_name))
            
            cursor.close()
            
            self._log('info', f"Found {len(companies)} unique companies")
            return companies
            
        except Exception as e:
            self._log('error', f"Failed to scan companies: {e}", exc_info=True)
            return []
    
    def get_company_name(self, tax_code: str) -> Optional[str]:
        """
        Get company name for a tax code
        
        Args:
            tax_code: Tax code to look up
            
        Returns:
            Company name or None if not found
        """
        self._ensure_connection()
        
        try:
            cursor = self._connection.cursor()
            
            # Query to get company name from DaiLy_DoanhNghiep table
            query = """
                SELECT TOP 1 TEN_DAI_LY
                FROM DaiLy_DoanhNghiep
                WHERE MA_SO_THUE = ?
            """
            
            cursor.execute(query, (tax_code,))
            row = cursor.fetchone()
            cursor.close()
            
            if row and row.TEN_DAI_LY:
                return str(row.TEN_DAI_LY).strip()
            return None
            
        except Exception as e:
            self._log('warning', f"Failed to get company name for {tax_code}: {e}")
            return None
    
    def _map_row_to_declaration(self, row) -> Declaration:
        """
        Map database row to Declaration object
        
        Args:
            row: Database row from query result
            
        Returns:
            Declaration object
        """
        # Get channel (PLUONG) value
        channel = str(row.channel).strip() if row.channel else ""
        
        # Determine status_name: use TTTK_HQ if available, otherwise derive from TTTK + PLUONG
        status_name = None
        if hasattr(row, 'status_name') and row.status_name:
            status_name = str(row.status_name).strip()
        else:
            # Derive status from TTTK and PLUONG
            status = str(row.status).strip() if row.status else ""
            if status == 'T':  # Thông quan
                if channel == 'Xanh':
                    status_name = "Thông quan (Xanh)"
                elif channel == 'Vang':
                    status_name = "Thông quan (Vàng)"
                else:
                    status_name = "Thông quan"
            else:
                # Not yet cleared - show routing status
                if channel == 'Xanh':
                    status_name = "Phân luồng Xanh"
                elif channel == 'Vang':
                    status_name = "Phân luồng Vàng"
                elif channel == 'Do':
                    status_name = "Phân luồng Đỏ"
                else:
                    status_name = "Chờ phân luồng"
        
        return Declaration(
            declaration_number=str(row.declaration_number).strip() if row.declaration_number else "",
            tax_code=str(row.tax_code).strip() if row.tax_code else "",
            declaration_date=row.declaration_date if isinstance(row.declaration_date, datetime) else datetime.now(),
            customs_office_code=str(row.customs_office_code).strip() if row.customs_office_code else "",
            transport_method=str(row.transport_method).strip() if row.transport_method else "",
            channel=channel,
            status=str(row.status).strip() if row.status else "",
            goods_description=str(row.goods_description).strip() if row.goods_description else None,
            status_name=status_name,
            declaration_type=str(row.declaration_type).strip() if hasattr(row, 'declaration_type') and row.declaration_type else None,
            bill_of_lading=str(row.bill_of_lading).strip() if hasattr(row, 'bill_of_lading') and row.bill_of_lading else None,
            invoice_number=str(row.invoice_number).strip() if hasattr(row, 'invoice_number') and row.invoice_number else None,
            so_hstk=str(row.so_hstk).strip() if hasattr(row, 'so_hstk') and row.so_hstk else None
        )
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
