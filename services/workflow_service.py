"""
Workflow Service v2.0

Unified workflow pipeline for both scheduler and manual mode.
Extracts core workflow logic from Scheduler to enable reuse.

Pipeline: fetch -> filter -> retrieve -> save -> track

Benefits:
1. Single source of truth for workflow logic
2. Event-driven progress updates
3. Cancellation support
4. Reusable by scheduler and manual panel
"""

import threading
from datetime import datetime
from typing import List, Optional, Callable, Set

from models.declaration_models import Declaration, WorkflowResult
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from logging_system.logger import Logger
from services.workflow_events import WorkflowEvent, WorkflowEventType


class WorkflowService:
    """
    Unified workflow service for barcode retrieval.
    
    Provides the core pipeline used by both automatic scheduler
    and manual mode operations.
    """
    
    def __init__(
        self,
        ecus_connector: EcusDataConnector,
        tracking_db: TrackingDatabase,
        processor: DeclarationProcessor,
        barcode_retriever: BarcodeRetriever,
        file_manager: FileManager,
        logger: Logger
    ):
        """
        Initialize workflow service.
        
        Args:
            ecus_connector: ECUS5 database connector
            tracking_db: Tracking database instance
            processor: Declaration processor for filtering
            barcode_retriever: Barcode retriever instance
            file_manager: File manager for saving
            logger: Logger instance
        """
        self.ecus_connector = ecus_connector
        self.tracking_db = tracking_db
        self.processor = processor
        self.barcode_retriever = barcode_retriever
        self.file_manager = file_manager
        self.logger = logger
        
        # Event listeners
        self._event_listeners: List[Callable[[WorkflowEvent], None]] = []
        
        # Cancellation support
        self._cancel_event = threading.Event()
        self._is_running = False
    
    def add_event_listener(self, listener: Callable[[WorkflowEvent], None]) -> None:
        """Add a listener for workflow events."""
        self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: Callable[[WorkflowEvent], None]) -> None:
        """Remove an event listener."""
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)
    
    def _emit_event(self, event: WorkflowEvent) -> None:
        """Emit an event to all listeners."""
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.warning(f"Event listener error: {e}")
    
    def cancel(self) -> None:
        """Cancel the running workflow."""
        self._cancel_event.set()
        self.logger.info("Workflow cancellation requested")
    
    @property
    def is_running(self) -> bool:
        """Check if workflow is currently running."""
        return self._is_running
    
    def execute(
        self,
        days_back: int = 7,
        tax_codes: Optional[List[str]] = None,
        force_redownload: bool = False,
        declarations: Optional[List[Declaration]] = None
    ) -> WorkflowResult:
        """
        Execute the workflow pipeline.
        
        Args:
            days_back: Number of days to look back
            tax_codes: Optional list of tax codes to filter
            force_redownload: If True, ignore processed tracking
            declarations: Optional pre-selected declarations (skip fetch)
            
        Returns:
            WorkflowResult with execution statistics
        """
        if self._is_running:
            self.logger.warning("Workflow already running")
            return WorkflowResult()
        
        self._is_running = True
        self._cancel_event.clear()
        
        result = WorkflowResult()
        result.start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting workflow (days_back={days_back}, tax_codes={tax_codes})")
            
            # 1. Get eligible declarations
            if declarations is None:
                # Fetch from database
                processed_ids = set() if force_redownload else self.tracking_db.get_all_processed()
                
                if self._cancel_event.is_set():
                    self._emit_event(WorkflowEvent.cancelled())
                    return result
                
                declarations = self.ecus_connector.get_new_declarations(
                    processed_ids, 
                    days_back=days_back, 
                    tax_codes=tax_codes
                )
                
                # Filter using business rules
                declarations = self.processor.filter_declarations(declarations)
            
            result.total_fetched = len(declarations)
            result.total_eligible = len(declarations)

            self._emit_event(WorkflowEvent.started(len(declarations)))

            if self.barcode_retriever and hasattr(self.barcode_retriever, 'reset_method_skip_list'):
                self.barcode_retriever.reset_method_skip_list()
            
            # 2. Process each declaration
            for idx, declaration in enumerate(declarations):
                if self._cancel_event.is_set():
                    self._emit_event(WorkflowEvent.cancelled())
                    break
                
                self._emit_event(WorkflowEvent.progress(
                    idx + 1, len(declarations), declaration.id
                ))
                
                try:
                    success, file_path = self._process_declaration(
                        declaration, force_redownload
                    )
                    
                    if success:
                        result.success_count += 1
                    else:
                        result.error_count += 1
                    
                    self._emit_event(WorkflowEvent.declaration_processed(
                        declaration.id, success, file_path
                    ))
                    
                except Exception as e:
                    result.error_count += 1
                    self.logger.error(f"Error processing {declaration.id}: {e}")
                    self._emit_event(WorkflowEvent.error(str(e), declaration.id))
            
            result.end_time = datetime.now()
            
            self._emit_event(WorkflowEvent.completed(
                result.success_count,
                result.error_count,
                result.duration.total_seconds() if result.duration else 0
            ))
            
            self.logger.info(
                f"Workflow completed: {result.success_count} success, "
                f"{result.error_count} errors"
            )
            
        except Exception as e:
            result.end_time = datetime.now()
            self.logger.error(f"Workflow failed: {e}", exc_info=True)
            self._emit_event(WorkflowEvent.error(str(e)))
            raise
        
        finally:
            self._is_running = False
        
        return result
    
    def _process_declaration(
        self, 
        declaration: Declaration, 
        force_overwrite: bool = False
    ) -> tuple:
        """
        Process a single declaration.
        
        Args:
            declaration: Declaration to process
            force_overwrite: If True, overwrite existing file
            
        Returns:
            Tuple of (success: bool, file_path: Optional[str])
        """
        self.logger.debug(f"Processing declaration: {declaration.id}")
        
        # Retrieve barcode
        pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
        
        if not pdf_content:
            self.logger.error(f"Failed to retrieve barcode for {declaration.id}")
            return False, None
        
        # Save to file
        file_path = self.file_manager.save_barcode(
            declaration,
            pdf_content,
            overwrite=force_overwrite
        )
        
        if not file_path:
            self.logger.warning(f"File save skipped for {declaration.id}")
            return False, None
        
        # Update tracking
        if force_overwrite and self.tracking_db.is_processed(declaration):
            self.tracking_db.update_processed_timestamp(declaration)
        else:
            self.tracking_db.add_processed(declaration, file_path)
        
        # Store company info
        try:
            company_name = self.ecus_connector.get_company_name(declaration.tax_code)
            if company_name:
                self.tracking_db.add_or_update_company(declaration.tax_code, company_name)
        except Exception as e:
            self.logger.warning(f"Failed to store company info: {e}")
        
        self.logger.info(f"Successfully processed: {declaration.id}")
        return True, file_path


# Global instance
_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> Optional[WorkflowService]:
    """Get the global workflow service instance."""
    return _workflow_service


def set_workflow_service(service: WorkflowService) -> None:
    """Set the global workflow service instance."""
    global _workflow_service
    _workflow_service = service
