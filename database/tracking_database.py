"""
Tracking database for processed declarations

This module provides SQLite-based tracking of processed declarations
to prevent duplicate processing and support re-download functionality.
"""

import sqlite3
import os
from typing import Set, List, Optional
from datetime import datetime
from models.declaration_models import Declaration, ProcessedDeclaration
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
        self._ensure_directory_exists()
        self._initialize_database()
    
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
            
            if self.logger:
                self.logger.info("Tracking database initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize tracking database: {e}", exc_info=True)
            raise
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
