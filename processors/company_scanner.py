"""
Company Scanner

This module provides business logic for scanning and managing companies
from the ECUS5 database for the Enhanced Manual Mode feature.
"""

from typing import List, Tuple, Optional, Callable
from database.ecus_connector import EcusDataConnector, DatabaseConnectionError
from database.tracking_database import TrackingDatabase
from logging_system.logger import Logger


class CompanyScanError(Exception):
    """Exception raised for company scanning errors"""
    pass


class CompanyScanner:
    """Business logic for scanning and managing companies"""
    
    def __init__(
        self,
        ecus_connector: EcusDataConnector,
        tracking_db: TrackingDatabase,
        logger: Optional[Logger] = None
    ):
        """
        Initialize CompanyScanner
        
        Args:
            ecus_connector: ECUS5 database connector
            tracking_db: Tracking database for persistence
            logger: Optional logger instance
        """
        self.ecus_connector = ecus_connector
        self.tracking_db = tracking_db
        self.logger = logger
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Helper method to log messages if logger is available"""
        if self.logger:
            log_method = getattr(self.logger, level, None)
            if log_method:
                log_method(message, **kwargs)
    
    def scan_companies(
        self,
        days_back: int = 90,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Tuple[str, str]]:
        """
        Scan database for all unique companies from recent declarations
        
        Args:
            days_back: Number of days to look back (default: 90)
            progress_callback: Optional callback function(current, total, message)
                             for progress updates
        
        Returns:
            List of tuples (tax_code, company_name)
            
        Raises:
            CompanyScanError: If scanning fails
        """
        try:
            self._log('info', f"Starting company scan for last {days_back} days")
            
            if progress_callback:
                progress_callback(0, 100, "Đang kết nối database...")
            
            # Scan companies from ECUS5 database
            companies = self.ecus_connector.scan_all_companies(days_back)
            
            if progress_callback:
                progress_callback(50, 100, f"Đã tìm thấy {len(companies)} công ty")
            
            self._log('info', f"Found {len(companies)} companies")
            
            if progress_callback:
                progress_callback(100, 100, "Hoàn thành quét công ty")
            
            return companies
            
        except DatabaseConnectionError as e:
            error_msg = f"Database connection failed: {e}"
            self._log('error', error_msg, exc_info=True)
            raise CompanyScanError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Failed to scan companies: {e}"
            self._log('error', error_msg, exc_info=True)
            raise CompanyScanError(error_msg) from e
    
    def save_companies(
        self,
        companies: List[Tuple[str, str]],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> int:
        """
        Save companies to tracking database
        
        Args:
            companies: List of tuples (tax_code, company_name)
            progress_callback: Optional callback function(current, total, message)
                             for progress updates
        
        Returns:
            Number of companies saved
            
        Raises:
            CompanyScanError: If saving fails
        """
        try:
            self._log('info', f"Saving {len(companies)} companies to tracking database")
            
            saved_count = 0
            total = len(companies)
            
            for idx, (tax_code, company_name) in enumerate(companies):
                try:
                    self.tracking_db.add_or_update_company(tax_code, company_name)
                    saved_count += 1
                    
                    if progress_callback and (idx % 10 == 0 or idx == total - 1):
                        progress = int((idx + 1) / total * 100)
                        progress_callback(
                            idx + 1,
                            total,
                            f"Đang lưu công ty {idx + 1}/{total}..."
                        )
                        
                except Exception as e:
                    self._log('warning', f"Failed to save company {tax_code}: {e}")
                    # Continue with other companies
            
            self._log('info', f"Successfully saved {saved_count}/{total} companies")
            
            if progress_callback:
                progress_callback(total, total, f"Đã lưu {saved_count} công ty")
            
            return saved_count
            
        except Exception as e:
            error_msg = f"Failed to save companies: {e}"
            self._log('error', error_msg, exc_info=True)
            raise CompanyScanError(error_msg) from e
    
    def scan_and_save_companies(
        self,
        days_back: int = 90,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[int, List[Tuple[str, str]]]:
        """
        Scan companies from database and save them to tracking database
        
        This is a convenience method that combines scan_companies() and save_companies()
        
        Args:
            days_back: Number of days to look back (default: 90)
            progress_callback: Optional callback function(current, total, message)
                             for progress updates
        
        Returns:
            Tuple of (saved_count, companies_list)
            
        Raises:
            CompanyScanError: If scanning or saving fails
        """
        try:
            # Scan companies
            companies = self.scan_companies(days_back, progress_callback)
            
            # Save companies
            saved_count = self.save_companies(companies, progress_callback)
            
            return saved_count, companies
            
        except CompanyScanError:
            # Re-raise CompanyScanError as-is
            raise
        except Exception as e:
            error_msg = f"Failed to scan and save companies: {e}"
            self._log('error', error_msg, exc_info=True)
            raise CompanyScanError(error_msg) from e
    
    def load_companies(self) -> List[Tuple[str, str]]:
        """
        Load companies from tracking database
        
        Returns:
            List of tuples (tax_code, company_name)
            
        Raises:
            CompanyScanError: If loading fails
        """
        try:
            self._log('debug', "Loading companies from tracking database")
            
            # Get all companies from tracking database
            companies_data = self.tracking_db.get_all_companies()
            
            # Convert to list of (tax_code, company_name) tuples
            companies = [(tax_code, company_name) for tax_code, company_name, _ in companies_data]
            
            self._log('info', f"Loaded {len(companies)} companies from tracking database")
            
            return companies
            
        except Exception as e:
            error_msg = f"Failed to load companies: {e}"
            self._log('error', error_msg, exc_info=True)
            raise CompanyScanError(error_msg) from e
