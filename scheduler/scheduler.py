"""
Workflow Scheduler

This module orchestrates periodic execution of the customs barcode automation workflow
with support for automatic and manual operation modes.
"""

from typing import List, Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models.declaration_models import Declaration, WorkflowResult, OperationMode
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from logging_system.logger import Logger


class Scheduler:
    """
    Orchestrates periodic execution of the workflow with mode support.
    
    Responsibilities:
    - Schedule polling at configured intervals (automatic mode)
    - Execute the main workflow
    - Handle workflow errors gracefully
    - Provide manual trigger capability
    - Support automatic/manual mode switching
    """
    
    def __init__(
        self,
        config_manager: ConfigurationManager,
        ecus_connector: EcusDataConnector,
        tracking_db: TrackingDatabase,
        processor: DeclarationProcessor,
        barcode_retriever: BarcodeRetriever,
        file_manager: FileManager,
        logger: Logger
    ):
        """
        Initialize scheduler with all required components
        
        Args:
            config_manager: Configuration manager instance
            ecus_connector: ECUS5 database connector
            tracking_db: Tracking database instance
            processor: Declaration processor
            barcode_retriever: Barcode retriever instance
            file_manager: File manager instance
            logger: Logger instance
        """
        self.config_manager = config_manager
        self.ecus_connector = ecus_connector
        self.tracking_db = tracking_db
        self.processor = processor
        self.barcode_retriever = barcode_retriever
        self.file_manager = file_manager
        self.logger = logger
        
        # Initialize APScheduler
        self._scheduler = BackgroundScheduler()
        self._job_id = "workflow_job"
        self._is_running = False
        
        # Load operation mode from configuration
        mode_str = self.config_manager.get_operation_mode()
        self._operation_mode = OperationMode(mode_str)
        
        self.logger.info(f"Scheduler initialized in {self._operation_mode.value} mode")
    
    def start(self) -> None:
        """
        Start the scheduler
        
        In automatic mode, schedules periodic workflow execution.
        In manual mode, does nothing (workflow only runs on manual trigger).
        """
        if self._is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        if self._operation_mode == OperationMode.AUTOMATIC:
            # Start automatic scheduling
            polling_interval = self.config_manager.get_polling_interval()
            
            self._scheduler.add_job(
                func=self._execute_workflow_safe,
                trigger=IntervalTrigger(seconds=polling_interval),
                id=self._job_id,
                replace_existing=True,
                max_instances=1  # Prevent overlapping executions
            )
            
            self._scheduler.start()
            self._is_running = True
            
            self.logger.info(f"Scheduler started in automatic mode (interval: {polling_interval}s)")
        else:
            # Manual mode - just mark as running
            self._is_running = True
            self.logger.info("Scheduler started in manual mode")
    
    def stop(self) -> None:
        """
        Stop the scheduler
        
        Stops automatic scheduling if in automatic mode.
        """
        if not self._is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        if self._operation_mode == OperationMode.AUTOMATIC:
            # Stop automatic scheduling
            if self._scheduler.running:
                self._scheduler.shutdown(wait=True)
            
            self.logger.info("Scheduler stopped (automatic mode)")
        else:
            self.logger.info("Scheduler stopped (manual mode)")
        
        self._is_running = False
    
    def set_operation_mode(self, mode: OperationMode) -> None:
        """
        Set operation mode and persist to configuration
        
        Args:
            mode: OperationMode enum value
        """
        old_mode = self._operation_mode
        self._operation_mode = mode
        
        # Persist to configuration
        self.config_manager.set_operation_mode(mode.value)
        self.config_manager.save()
        
        self.logger.info(f"Operation mode changed from {old_mode.value} to {mode.value}")
        
        # If scheduler is running, restart with new mode
        if self._is_running:
            self.stop()
            self.start()
    
    def get_operation_mode(self) -> OperationMode:
        """
        Get current operation mode
        
        Returns:
            Current OperationMode
        """
        return self._operation_mode
    
    def run_once(self, force_redownload: bool = False, days_back: int = 7, tax_codes: Optional[List[str]] = None, progress_callback=None) -> WorkflowResult:
        """
        Execute workflow once (manual trigger)
        
        Args:
            force_redownload: If True, re-download all declarations regardless of tracking
            days_back: Number of days to look back
            tax_codes: Optional list of tax codes to filter by
            progress_callback: Optional callback function for progress updates
            
        Returns:
            WorkflowResult with execution statistics
        """
        self.logger.info(f"Manual workflow execution triggered (force_redownload={force_redownload}, days_back={days_back})")
        return self._execute_workflow(force_redownload=force_redownload, days_back=days_back, tax_codes=tax_codes, progress_callback=progress_callback)
    
    def redownload_declarations(self, declarations: List[Declaration]) -> WorkflowResult:
        """
        Re-download barcodes for specific declarations
        
        Args:
            declarations: List of declarations to re-download
            
        Returns:
            WorkflowResult with execution statistics
        """
        self.logger.info(f"Re-downloading {len(declarations)} declarations")
        
        result = WorkflowResult()
        result.start_time = datetime.now()
        result.total_fetched = len(declarations)
        result.total_eligible = len(declarations)
        
        for declaration in declarations:
            try:
                # Retrieve barcode
                pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
                
                if pdf_content:
                    # Save to file (overwrite existing)
                    file_path = self.file_manager.save_barcode(
                        declaration,
                        pdf_content,
                        overwrite=True
                    )
                    
                    if file_path:
                        # Update timestamp
                        self.tracking_db.update_processed_timestamp(declaration)
                        result.success_count += 1
                        self.logger.info(f"Successfully re-downloaded barcode for {declaration.id}")
                    else:
                        result.error_count += 1
                        self.logger.error(f"Failed to save re-downloaded barcode for {declaration.id}")
                else:
                    result.error_count += 1
                    self.logger.error(f"Failed to retrieve barcode for {declaration.id}")
                    
            except Exception as e:
                self.logger.error(f"Error re-downloading {declaration.id}: {e}", exc_info=True)
                result.error_count += 1
        
        result.end_time = datetime.now()
        
        self.logger.info(
            f"Re-download completed: {result.success_count} successful, "
            f"{result.error_count} errors, duration: {result.duration}"
        )
        
        return result
    
    def _execute_workflow_safe(self) -> None:
        """
        Execute workflow with exception handling (for scheduled execution)
        
        This wrapper ensures that exceptions don't crash the scheduler.
        """
        try:
            self._execute_workflow()
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}", exc_info=True)
    
    def _execute_workflow(self, force_redownload: bool = False, days_back: int = None, tax_codes: Optional[List[str]] = None, progress_callback=None) -> WorkflowResult:
        """
        Execute the main workflow
        
        Args:
            force_redownload: If True, re-download all declarations regardless of tracking
            days_back: Number of days to look back (None = use default based on mode)
            tax_codes: Optional list of tax codes to filter by
            progress_callback: Optional callback function for progress updates
            
        Returns:
            WorkflowResult with execution statistics
        """
        result = WorkflowResult()
        result.start_time = datetime.now()
        
        try:
            self.logger.info("Starting workflow execution")
            
            # Determine days_back based on operation mode if not specified
            if days_back is None:
                if self._operation_mode == OperationMode.AUTOMATIC:
                    days_back = 3  # Automatic mode: 3 days
                else:
                    days_back = 7  # Manual mode default: 7 days
            
            if progress_callback:
                progress_callback("Đang tải danh sách tờ khai đã xử lý...", 0, 100)
            
            # 1. Get processed IDs (skip if force_redownload)
            processed_ids = set() if force_redownload else self.tracking_db.get_all_processed()
            self.logger.debug(f"Loaded {len(processed_ids)} processed declaration IDs")
            
            if progress_callback:
                progress_callback(f"Đang truy vấn cơ sở dữ liệu ({days_back} ngày gần nhất)...", 10, 100)
            
            # 2. Fetch new declarations from ECUS5
            declarations = self.ecus_connector.get_new_declarations(processed_ids, days_back=days_back, tax_codes=tax_codes)
            result.total_fetched = len(declarations)
            self.logger.info(f"Fetched {result.total_fetched} declarations from ECUS5")
            
            if progress_callback:
                progress_callback(f"Tìm thấy {result.total_fetched} tờ khai, đang lọc...", 20, 100)
            
            # 3. Filter declarations using business rules
            eligible = self.processor.filter_declarations(declarations)
            result.total_eligible = len(eligible)
            self.logger.info(f"{result.total_eligible} declarations are eligible for processing")
            
            if progress_callback:
                progress_callback(f"Đang xử lý {result.total_eligible} tờ khai hợp lệ...", 30, 100)
            
            # 4. Process each eligible declaration
            for idx, declaration in enumerate(eligible):
                try:
                    # Update progress
                    if progress_callback:
                        progress = 30 + int((idx / len(eligible)) * 60)
                        progress_callback(f"Đang xử lý tờ khai {idx+1}/{len(eligible)}: {declaration.declaration_number}", progress, 100)
                    
                    self.logger.debug(f"Processing declaration: {declaration.id}")
                    
                    # Retrieve barcode
                    pdf_content = self.barcode_retriever.retrieve_barcode(declaration)
                    
                    if pdf_content:
                        # Save to file (overwrite if force_redownload)
                        file_path = self.file_manager.save_barcode(
                            declaration,
                            pdf_content,
                            overwrite=force_redownload
                        )
                        
                        if file_path:
                            # Mark as processed or update timestamp
                            if force_redownload and self.tracking_db.is_processed(declaration):
                                self.tracking_db.update_processed_timestamp(declaration)
                            else:
                                self.tracking_db.add_processed(declaration, file_path)
                            
                            # Store company information
                            try:
                                company_name = self.ecus_connector.get_company_name(declaration.tax_code)
                                if company_name:
                                    self.tracking_db.add_or_update_company(declaration.tax_code, company_name)
                            except Exception as e:
                                self.logger.warning(f"Failed to store company info for {declaration.tax_code}: {e}")
                            
                            result.success_count += 1
                            self.logger.info(f"Successfully processed declaration: {declaration.id}")
                        else:
                            result.error_count += 1
                            self.logger.warning(f"File save skipped for declaration: {declaration.id}")
                    else:
                        result.error_count += 1
                        self.logger.error(f"Failed to retrieve barcode for declaration: {declaration.id}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing declaration {declaration.id}: {e}", exc_info=True)
                    result.error_count += 1
            
            result.end_time = datetime.now()
            
            if progress_callback:
                progress_callback(f"Hoàn thành: {result.success_count} thành công, {result.error_count} lỗi", 100, 100)
            
            self.logger.info(
                f"Workflow execution completed: {result.success_count} successful, "
                f"{result.error_count} errors, duration: {result.duration}"
            )
            
        except Exception as e:
            result.end_time = datetime.now()
            self.logger.error(f"Workflow execution failed: {e}", exc_info=True)
            raise
        
        return result
    
    def is_running(self) -> bool:
        """
        Check if scheduler is running
        
        Returns:
            True if running, False otherwise
        """
        return self._is_running
