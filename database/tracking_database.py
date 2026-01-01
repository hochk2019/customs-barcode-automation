"""
Tracking database for processed declarations

This module provides SQLite-based tracking of processed declarations
to prevent duplicate processing and support re-download functionality.
"""

import sqlite3
import os
from typing import Set, List, Optional, Any
from datetime import datetime, timedelta
from models.declaration_models import Declaration, ProcessedDeclaration, TrackingDeclaration, ClearanceStatus
from logging_system.logger import Logger


class TrackingDatabase:
    """SQLite database for tracking processed declarations"""
    
    def __init__(self, db_path: str, logger: Optional[Logger] = None):
        """
        Initialize tracking database
        
        Args:
            db_path: Path to SQLite database file
            logger: Optional logger instance
        """
        self.db_path = db_path
        self.logger = logger
        self._busy_timeout = 30  # v2.0: 30 second busy timeout
        self._ensure_directory_exists()
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get SQLite connection with busy timeout.
        
        v2.0: Added busy timeout to prevent lock errors.
        
        Returns:
            sqlite3.Connection with timeout configured
        """
        conn = sqlite3.connect(self.db_path, timeout=self._busy_timeout)
        conn.execute(f"PRAGMA busy_timeout = {self._busy_timeout * 1000}")  # milliseconds
        return conn
    
    def _ensure_directory_exists(self) -> None:
        """Create database directory if it doesn't exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self) -> None:
        """Create database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Create processed_declarations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_declarations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    declaration_number TEXT NOT NULL,
                    tax_code TEXT NOT NULL,
                    declaration_date TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(declaration_number, tax_code, declaration_date)
                )
            """)
            
            # Create companies table for storing company names and tax codes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tax_code TEXT NOT NULL UNIQUE,
                    company_name TEXT NOT NULL,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_declaration_lookup 
                ON processed_declarations(declaration_number, tax_code, declaration_date)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_search 
                ON processed_declarations(declaration_number, tax_code)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_company_tax_code 
                ON companies(tax_code)
            """)
            
            conn.commit()
            
            # Create tracking_declarations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracking_declarations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tax_code TEXT NOT NULL,
                    declaration_number TEXT NOT NULL,
                    customs_code TEXT,
                    declaration_date TEXT,
                    company_name TEXT,
                    status TEXT DEFAULT 'pending',
                    last_checked TEXT,
                    cleared_at TEXT,
                    added_at TEXT NOT NULL,
                    notified INTEGER DEFAULT 0,
                    UNIQUE(declaration_number)
                )
            ''')
            
            # Create check_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS check_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    declaration_id INTEGER NOT NULL,
                    checked_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_data TEXT,
                    FOREIGN KEY (declaration_id) REFERENCES tracking_declarations(id)
                )
            ''')

            if self.logger:
                self.logger.info("Tracking database initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize tracking database: {e}", exc_info=True)
            raise
        finally:
            conn.close()
            
    def cleanup_old_records(self, retention_days: int) -> int:
        """
        Delete cleared/processed declarations older than retention days.
        
        Args:
            retention_days: Number of days to keep data
            
        Returns:
            Number of records deleted
        """
        if retention_days < 1:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
            
            # Delete from check_history first (FK constraint usually, but good practice)
            cursor.execute("""
                DELETE FROM check_history 
                WHERE declaration_id IN (
                    SELECT id FROM tracking_declarations 
                    WHERE (status = 'cleared' OR status = 'error') 
                    AND cleared_at < ?
                )
            """, (cutoff_str,))
            
            # This query is tricky because we don't have 'updated_at' index in tracking_declarations
            # But we have 'cleared_at'. Let's use cleared_at for cleared items.
            # For pending items, we usually don't delete them unless they are very old?
            # Requirement says "Retention: Keep tracking data...". 
            # Usually implies completed items. Pending items should probably stay until cleared or manually deleted.
            # Let's delete ONLY cleared items explicitly.
            
            cursor.execute("""
                DELETE FROM tracking_declarations
                WHERE status = 'cleared' 
                AND cleared_at IS NOT NULL 
                AND cleared_at < ?
            """, (cutoff_str,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            if self.logger and deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old tracking records (older than {retention_days} days)")
                
            return deleted_count
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to cleanup old records: {e}")
            return 0
        finally:
            conn.close()
            
    def get_pending_declarations(self) -> List[TrackingDeclaration]:
        """
        Get all declarations with 'pending' status.
        
        Returns:
            List of TrackingDeclaration objects
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, tax_code, declaration_number, customs_code, 
                       declaration_date, company_name, status, last_checked, 
                       cleared_at, added_at, notified
                FROM tracking_declarations
                WHERE status = 'pending'
            """)
            
            declarations = []
            for row in cursor.fetchall():
                declarations.append(TrackingDeclaration(
                    id=row[0],
                    tax_code=row[1],
                    declaration_number=row[2],
                    customs_code=row[3],
                    declaration_date=row[4],
                    company_name=row[5],
                    status=row[6],
                    last_checked=row[7],
                    cleared_at=row[8],
                    added_at=row[9],
                    notified=bool(row[10])
                ))
            
            return declarations
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get pending declarations: {e}", exc_info=True)
            return []
        finally:
            conn.close()
    
    def add_to_tracking(self, declaration_number: str, tax_code: str, declaration_date: Any, 
                       company_name: str = "", customs_code: str = "") -> bool:
        """
        Add a declaration to tracking.
        
        Args:
            declaration_number: Declaration number
            tax_code: Tax code
            declaration_date: Declaration date (string or datetime)
            company_name: Company name
            customs_code: Customs office code
            
        Returns:
            True if added, False if duplicate or failed
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Format date
            date_str = ""
            if isinstance(declaration_date, datetime):
                # We want just the date part for display usually, but DB stores as TEXT.
                # Let's standardize on YYYY-MM-DD for sorting/filtering consistency
                date_str = declaration_date.strftime("%Y-%m-%d")
            elif isinstance(declaration_date, str):
                date_str = declaration_date
            
            # Check if exists
            cursor.execute("SELECT id FROM tracking_declarations WHERE declaration_number = ?", (declaration_number,))
            if cursor.fetchone():
                if self.logger:
                    self.logger.info(f"Declaration {declaration_number} already in tracking.")
                return False
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO tracking_declarations (
                    tax_code, declaration_number, customs_code, 
                    declaration_date, company_name, status, 
                    last_checked, added_at, notified
                ) VALUES (?, ?, ?, ?, ?, 'pending', NULL, ?, 0)
            """, (
                tax_code, declaration_number, customs_code, 
                date_str, company_name, now
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add to tracking: {e}", exc_info=True)
            raise # Let caller handle exception if needed, or return False? 
                  # Caller in customs_gui catches exception.
        finally:
            conn.close()

    def delete_by_id(self, tracking_id: int) -> bool:
        """
        Delete a tracking declaration by its ID.
        
        Args:
            tracking_id: The ID of the tracking declaration to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # First delete from check_history (foreign key constraint)
            cursor.execute("DELETE FROM check_history WHERE declaration_id = ?", (tracking_id,))
            
            # Then delete from tracking_declarations
            cursor.execute("DELETE FROM tracking_declarations WHERE id = ?", (tracking_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if self.logger and deleted:
                self.logger.info(f"Deleted tracking declaration id={tracking_id}")
                
            return deleted
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to delete tracking id={tracking_id}: {e}")
            return False
        finally:
            conn.close()

    def add_processed(self, declaration: Declaration, file_path: str) -> None:
        """
        Add a processed declaration to the tracking database
        
        Args:
            declaration: Declaration that was processed
            file_path: Path to the saved PDF file
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Format date as string
            date_str = declaration.declaration_date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT OR REPLACE INTO processed_declarations 
                (declaration_number, tax_code, declaration_date, file_path, processed_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                declaration.declaration_number,
                declaration.tax_code,
                date_str,
                file_path
            ))
            
            conn.commit()
            
            if self.logger:
                self.logger.info(f"Added processed declaration: {declaration.id}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add processed declaration {declaration.id}: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def is_processed(self, declaration: Declaration) -> bool:
        """
        Check if a declaration has already been processed
        
        Args:
            declaration: Declaration to check
            
        Returns:
            True if declaration is in tracking database, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Format date as string
            date_str = declaration.declaration_date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT COUNT(*) FROM processed_declarations
                WHERE declaration_number = ? AND tax_code = ? AND declaration_date = ?
            """, (
                declaration.declaration_number,
                declaration.tax_code,
                date_str
            ))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to check if declaration {declaration.id} is processed: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def get_all_processed(self) -> Set[str]:
        """
        Get set of all processed declaration IDs
        
        Returns:
            Set of declaration IDs (format: tax_code_declaration_number_date)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT declaration_number, tax_code, declaration_date
                FROM processed_declarations
            """)
            
            processed_ids = set()
            for row in cursor.fetchall():
                declaration_number, tax_code, declaration_date = row
                # Convert date string to format used in Declaration.id
                date_obj = datetime.strptime(declaration_date, '%Y-%m-%d')
                date_str = date_obj.strftime('%Y%m%d')
                declaration_id = f"{tax_code}_{declaration_number}_{date_str}"
                processed_ids.add(declaration_id)
            
            return processed_ids
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get all processed declarations: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def get_all_processed_details(self) -> List[ProcessedDeclaration]:
        """
        Get detailed information about all processed declarations for GUI display
        
        Returns:
            List of ProcessedDeclaration objects
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, declaration_number, tax_code, declaration_date, 
                       file_path, processed_at, updated_at
                FROM processed_declarations
                ORDER BY updated_at DESC
            """)
            
            processed_list = []
            for row in cursor.fetchall():
                id_val, declaration_number, tax_code, declaration_date, file_path, processed_at, updated_at = row
                
                # Parse timestamps
                processed_at_dt = datetime.strptime(processed_at, '%Y-%m-%d %H:%M:%S')
                updated_at_dt = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                
                processed_decl = ProcessedDeclaration(
                    id=id_val,
                    declaration_number=declaration_number,
                    tax_code=tax_code,
                    declaration_date=declaration_date,
                    file_path=file_path,
                    processed_at=processed_at_dt,
                    updated_at=updated_at_dt
                )
                processed_list.append(processed_decl)
            
            return processed_list
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get processed declaration details: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def search_declarations(self, query: str) -> List[ProcessedDeclaration]:
        """
        Search for declarations by declaration number or tax code
        
        Args:
            query: Search query string
            
        Returns:
            List of matching ProcessedDeclaration objects
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Use LIKE for partial matching
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT id, declaration_number, tax_code, declaration_date, 
                       file_path, processed_at, updated_at
                FROM processed_declarations
                WHERE declaration_number LIKE ? OR tax_code LIKE ?
                ORDER BY updated_at DESC
            """, (search_pattern, search_pattern))
            
            processed_list = []
            for row in cursor.fetchall():
                id_val, declaration_number, tax_code, declaration_date, file_path, processed_at, updated_at = row
                
                # Parse timestamps
                processed_at_dt = datetime.strptime(processed_at, '%Y-%m-%d %H:%M:%S')
                updated_at_dt = datetime.strptime(updated_at, '%Y-%m-%d %H:%M:%S')
                
                processed_decl = ProcessedDeclaration(
                    id=id_val,
                    declaration_number=declaration_number,
                    tax_code=tax_code,
                    declaration_date=declaration_date,
                    file_path=file_path,
                    processed_at=processed_at_dt,
                    updated_at=updated_at_dt
                )
                processed_list.append(processed_decl)
            
            return processed_list
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to search declarations with query '{query}': {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def update_processed_timestamp(self, declaration: Declaration) -> None:
        """
        Update the processed timestamp for a declaration (used for re-downloads)
        
        Args:
            declaration: Declaration to update
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Format date as string
            date_str = declaration.declaration_date.strftime('%Y-%m-%d')
            
            cursor.execute("""
                UPDATE processed_declarations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE declaration_number = ? AND tax_code = ? AND declaration_date = ?
            """, (
                declaration.declaration_number,
                declaration.tax_code,
                date_str
            ))
            
            conn.commit()
            
            if self.logger:
                self.logger.info(f"Updated timestamp for declaration: {declaration.id}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to update timestamp for declaration {declaration.id}: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def add_or_update_company(self, tax_code: str, company_name: str) -> None:
        """
        Add or update company information
        
        Args:
            tax_code: Company tax code
            company_name: Company name
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO companies (tax_code, company_name, last_seen, created_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(tax_code) DO UPDATE SET
                    company_name = excluded.company_name,
                    last_seen = CURRENT_TIMESTAMP
            """, (tax_code, company_name))
            
            conn.commit()
            
            if self.logger:
                self.logger.debug(f"Added/updated company: {company_name} ({tax_code})")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add/update company {tax_code}: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def get_all_companies(self) -> List[tuple]:
        """
        Get all companies from database
        
        Returns:
            List of tuples (tax_code, company_name, last_seen)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tax_code, company_name, last_seen
                FROM companies
                ORDER BY company_name
            """)
            
            return cursor.fetchall()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get companies: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def search_companies(self, query: str) -> List[tuple]:
        """
        Search companies by name or tax code
        
        Args:
            query: Search query string
            
        Returns:
            List of tuples (tax_code, company_name, last_seen)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT tax_code, company_name, last_seen
                FROM companies
                WHERE company_name LIKE ? OR tax_code LIKE ?
                ORDER BY company_name
            """, (search_pattern, search_pattern))
            
            return cursor.fetchall()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to search companies: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def save_recent_company(self, tax_code: str) -> None:
        """
        Save a tax code to the recent companies list.
        
        If the tax code already exists, updates its last_used timestamp.
        
        Args:
            tax_code: Tax code to save
            
        Requirements: 11.3, 11.4
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Create recent_companies table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tax_code TEXT NOT NULL UNIQUE,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert or update
            cursor.execute("""
                INSERT INTO recent_companies (tax_code, last_used)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(tax_code) DO UPDATE SET
                    last_used = CURRENT_TIMESTAMP
            """, (tax_code,))
            
            conn.commit()
            
            if self.logger:
                self.logger.debug(f"Saved recent company: {tax_code}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save recent company {tax_code}: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def get_recent_companies(self, limit: int = 5) -> List[str]:
        """
        Get list of recently used tax codes.
        
        Args:
            limit: Maximum number of tax codes to return (default 5)
            
        Returns:
            List of tax codes ordered by most recently used
            
        Requirements: 11.3, 11.4
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Create table if not exists (for first run)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recent_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tax_code TEXT NOT NULL UNIQUE,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                SELECT tax_code
                FROM recent_companies
                ORDER BY last_used DESC
                LIMIT ?
            """, (limit,))
            
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get recent companies: {e}", exc_info=True)
            return []
        finally:
            conn.close()
    
    def clear_recent_companies(self) -> None:
        """Clear all recent companies."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recent_companies")
            conn.commit()
            
            if self.logger:
                self.logger.debug("Cleared recent companies")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to clear recent companies: {e}", exc_info=True)
        finally:
            conn.close()
    
    def rebuild_from_directory(self, directory: str) -> None:
        """
        Rebuild tracking database from PDF files in directory (recovery function)
        
        Args:
            directory: Directory containing PDF files
        """
        if not os.path.exists(directory):
            if self.logger:
                self.logger.error(f"Directory does not exist: {directory}")
            raise ValueError(f"Directory does not exist: {directory}")
        
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Clear existing records
            cursor.execute("DELETE FROM processed_declarations")
            
            # Scan directory for PDF files
            rebuilt_count = 0
            for filename in os.listdir(directory):
                if filename.endswith('.pdf'):
                    try:
                        # Parse filename: TaxCode_DeclarationNumber.pdf
                        name_without_ext = filename[:-4]  # Remove .pdf
                        parts = name_without_ext.split('_')
                        
                        if len(parts) == 2:
                            tax_code, declaration_number = parts
                            file_path = os.path.join(directory, filename)
                            
                            # Get file modification time as processed_at
                            file_mtime = os.path.getmtime(file_path)
                            processed_at = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            
                            # We don't have the original declaration date, so use file date
                            declaration_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d')
                            
                            cursor.execute("""
                                INSERT INTO processed_declarations 
                                (declaration_number, tax_code, declaration_date, file_path, processed_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                declaration_number,
                                tax_code,
                                declaration_date,
                                file_path,
                                processed_at,
                                processed_at
                            ))
                            
                            rebuilt_count += 1
                            
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Failed to parse file {filename}: {e}")
                        continue
            
            conn.commit()
            
            if self.logger:
                self.logger.info(f"Rebuilt tracking database with {rebuilt_count} records from {directory}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to rebuild tracking database: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    # =========================================================================
    # Tracking Methods (v1.5.0)
    # =========================================================================

    def add_declaration(
        self,
        tax_code: str,
        declaration_number: str,
        customs_code: str = "",
        declaration_date: str = "",
        company_name: str = ""
    ) -> Optional[int]:
        """
        Add a declaration to track.
        
        Args:
            tax_code: Company tax code
            declaration_number: Declaration number
            customs_code: Customs office code
            declaration_date: Declaration date
            company_name: Company name
            
        Returns:
            ID of inserted row, or None if already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO tracking_declarations 
                (tax_code, declaration_number, customs_code, declaration_date, 
                 company_name, status, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tax_code,
                declaration_number,
                customs_code,
                declaration_date,
                company_name,
                ClearanceStatus.PENDING.value,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            conn.commit()
            
            # Also save company if new
            if company_name:
                self.add_or_update_company(tax_code, company_name)
                
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Already exists
            return None
        finally:
            conn.close()
    
    def get_all_tracking(self) -> List[TrackingDeclaration]:
        """
        Get all tracked declarations.
        
        Returns:
            List of TrackingDeclaration objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, tax_code, declaration_number, customs_code, 
                       declaration_date, company_name, status, last_checked,
                       cleared_at, added_at, notified
                FROM tracking_declarations
                ORDER BY added_at DESC
            ''')
            
            results = []
            for row in cursor.fetchall():
                results.append(TrackingDeclaration(
                    id=row[0],
                    tax_code=row[1],
                    declaration_number=row[2],
                    customs_code=row[3] or "",
                    declaration_date=row[4] or "",
                    company_name=row[5] or "",
                    status=ClearanceStatus(row[6]) if row[6] else ClearanceStatus.PENDING,
                    last_checked=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if row[7] else None,
                    cleared_at=datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S') if row[8] else None,
                    added_at=datetime.strptime(row[9], '%Y-%m-%d %H:%M:%S'),
                    notified=bool(row[10])
                ))
            return results
        finally:
            conn.close()
    
    def get_pending_declarations(self) -> List[TrackingDeclaration]:
        """
        Get all pending (not yet cleared) declarations.
        
        Returns:
            List of pending TrackingDeclaration objects
        """
        all_tracking = self.get_all_tracking()
        return [d for d in all_tracking if d.status == ClearanceStatus.PENDING]
    
    def update_status(
        self,
        declaration_id: int,
        status: ClearanceStatus,
        response_data: str = None
    ) -> None:
        """
        Update declaration status.
        
        Args:
            declaration_id: ID of declaration to update
            status: New status
            response_data: Optional response data from check
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update declaration
            if status in (ClearanceStatus.CLEARED, ClearanceStatus.TRANSFER):
                cursor.execute('''
                    UPDATE tracking_declarations
                    SET status = ?, last_checked = ?, cleared_at = ?
                    WHERE id = ?
                ''', (status.value, now, now, declaration_id))
            else:
                cursor.execute('''
                    UPDATE tracking_declarations
                    SET status = ?, last_checked = ?
                    WHERE id = ?
                ''', (status.value, now, declaration_id))
            
            # Record history
            cursor.execute('''
                INSERT INTO check_history (declaration_id, checked_at, status, response_data)
                VALUES (?, ?, ?, ?)
            ''', (declaration_id, now, status.value, response_data))
            
            conn.commit()
        finally:
            conn.close()
    
    def mark_notified(self, declaration_id: int) -> None:
        """Mark a declaration as notified."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE tracking_declarations
                SET notified = 1
                WHERE id = ?
            ''', (declaration_id,))
            conn.commit()
        finally:
            conn.close()
    
    def delete_declaration(self, declaration_id: int) -> None:
        """Delete a tracked declaration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM check_history WHERE declaration_id = ?', (declaration_id,))
            cursor.execute('DELETE FROM tracking_declarations WHERE id = ?', (declaration_id,))
            conn.commit()
        finally:
            conn.close()
    
    def cleanup_old_entries(self, retention_days: int = 7) -> int:
        """
        Remove entries older than retention period.
        
        Args:
            retention_days: Number of days to keep (1-10)
            
        Returns:
            Number of entries deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cutoff = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Get IDs to delete
            cursor.execute('''
                SELECT id FROM tracking_declarations
                WHERE added_at < ? AND status = 'cleared'
            ''', (cutoff,))
            
            ids_to_delete = [row[0] for row in cursor.fetchall()]
            
            if ids_to_delete:
                # Delete history first
                placeholders = ','.join('?' * len(ids_to_delete))
                cursor.execute(f'DELETE FROM check_history WHERE declaration_id IN ({placeholders})', ids_to_delete)
                cursor.execute(f'DELETE FROM tracking_declarations WHERE id IN ({placeholders})', ids_to_delete)
            
            conn.commit()
            return len(ids_to_delete)
        finally:
            conn.close()
    
    def get_unnotified_cleared(self) -> List[TrackingDeclaration]:
        """
        Get declarations that are cleared but not yet notified.
        
        Returns:
            List of unnotified cleared declarations
        """
        all_tracking = self.get_all_tracking()
        return [d for d in all_tracking if d.status == ClearanceStatus.CLEARED and not d.notified]
