"""
Manual Panel Service v2.0

Service layer for EnhancedManualPanel operations.
Removes direct access to private component state.

Benefits:
1. Clean separation of concerns
2. Testable business logic
3. No direct GUI dependencies in service
"""

from typing import Optional, List, Callable
from datetime import datetime, timedelta

from models.declaration_models import Declaration, WorkflowResult
from services.workflow_service import WorkflowService
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from logging_system.logger import Logger


class ManualPanelService:
    """
    Service layer for manual panel operations.
    
    Encapsulates all business logic that was previously
    scattered in EnhancedManualPanel with private state access.
    """
    
    def __init__(
        self,
        workflow_service: WorkflowService,
        ecus_connector: EcusDataConnector,
        tracking_db: TrackingDatabase,
        logger: Logger
    ):
        """
        Initialize manual panel service.
        
        Args:
            workflow_service: Unified workflow service
            ecus_connector: ECUS connector for queries
            tracking_db: Tracking database
            logger: Logger instance
        """
        self.workflow_service = workflow_service
        self.ecus_connector = ecus_connector
        self.tracking_db = tracking_db
        self.logger = logger
    
    def fetch_declarations(
        self,
        days_back: int = 7,
        tax_codes: Optional[List[str]] = None,
        include_pending: bool = True
    ) -> List[Declaration]:
        """
        Fetch declarations from ECUS database.
        
        Args:
            days_back: Number of days to look back
            tax_codes: Optional list of company tax codes
            include_pending: Include pending declarations
            
        Returns:
            List of Declaration objects
        """
        try:
            from_date = datetime.now() - timedelta(days=days_back)
            to_date = datetime.now()
            
            declarations = self.ecus_connector.get_declarations_by_date_range(
                from_date=from_date,
                to_date=to_date,
                tax_codes=tax_codes,
                include_pending=include_pending
            )
            
            self.logger.info(f"Fetched {len(declarations)} declarations")
            return declarations
            
        except Exception as e:
            self.logger.error(f"Failed to fetch declarations: {e}")
            return []
    
    def download_barcodes(
        self,
        declarations: List[Declaration],
        force_redownload: bool = False,
        on_progress: Callable[[int, int, str], None] = None
    ) -> WorkflowResult:
        """
        Download barcodes for selected declarations.
        
        Args:
            declarations: List of declarations to download
            force_redownload: Overwrite existing files
            on_progress: Progress callback (current, total, status)
            
        Returns:
            WorkflowResult with statistics
        """
        if on_progress:
            def event_handler(event):
                if event.data:
                    current = event.data.get("current", 0)
                    total = event.data.get("total", 0)
                    on_progress(current, total, event.message)
            
            self.workflow_service.add_event_listener(event_handler)
        
        try:
            result = self.workflow_service.execute(
                declarations=declarations,
                force_redownload=force_redownload
            )
            return result
            
        finally:
            if on_progress:
                self.workflow_service.remove_event_listener(event_handler)
    
    def get_processed_count(self) -> int:
        """Get count of processed declarations."""
        try:
            processed = self.tracking_db.get_all_processed()
            return len(processed)
        except Exception as e:
            self.logger.error(f"Failed to get processed count: {e}")
            return 0
    
    def is_declaration_processed(self, declaration: Declaration) -> bool:
        """
        Check if a declaration has already been processed.
        
        Args:
            declaration: Declaration to check
            
        Returns:
            True if already processed
        """
        try:
            processed_ids = self.tracking_db.get_all_processed()
            return declaration.id in processed_ids
        except Exception:
            return False
    
    def get_companies(self) -> List[dict]:
        """
        Get list of companies from tracking database.
        
        Returns:
            List of company dicts with tax_code and name
        """
        try:
            return self.tracking_db.get_all_companies()
        except Exception as e:
            self.logger.error(f"Failed to get companies: {e}")
            return []
    
    def cancel_download(self) -> None:
        """Cancel ongoing download operation."""
        self.workflow_service.cancel()


# Factory function
def create_manual_panel_service(
    workflow_service: WorkflowService,
    ecus_connector: EcusDataConnector,
    tracking_db: TrackingDatabase,
    logger: Logger
) -> ManualPanelService:
    """Create a ManualPanelService instance."""
    return ManualPanelService(
        workflow_service=workflow_service,
        ecus_connector=ecus_connector,
        tracking_db=tracking_db,
        logger=logger
    )
