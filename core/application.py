"""
Application Container v2.0

Manages application lifecycle and dependency injection.
Replaces the monolithic main() function with a structured container.

Benefits:
1. Testable - Can inject mock dependencies
2. Lifecycle management - Proper startup/shutdown
3. No globals - All dependencies managed centrally
"""

import sys
import atexit
import threading
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from logging_system.logger import Logger
from config.configuration_manager import ConfigurationManager
from config.preferences_service import get_preferences_service
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from scheduler.scheduler import Scheduler
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager


class Application:
    """
    Application container managing all services and lifecycle.
    
    Usage:
        app = Application()
        app.initialize()
        app.start()
        # ... run main loop ...
        app.shutdown()
    """
    
    def __init__(self, config_path: str = "config.ini"):
        """
        Initialize application container.
        
        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path
        self._initialized = False
        self._started = False
        self._shutdown_handlers: list = []
        
        # Core services (initialized later)
        self.logger: Optional[Logger] = None
        self.config_manager: Optional[ConfigurationManager] = None
        self.ecus_connector: Optional[EcusDataConnector] = None
        self.tracking_db: Optional[TrackingDatabase] = None
        self.scheduler: Optional[Scheduler] = None
        self.processor: Optional[DeclarationProcessor] = None
        self.barcode_retriever: Optional[BarcodeRetriever] = None
        self.file_manager: Optional[FileManager] = None
        
        # GUI (optional, set externally)
        self.gui = None
        
        # Register atexit handler
        atexit.register(self._atexit_handler)
    
    def initialize(self) -> bool:
        """
        Initialize all services.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            # 1. Configuration
            print("Loading configuration...")
            self.config_manager = ConfigurationManager(self._config_path)
            self.config_manager.validate()
            print("✓ Configuration loaded successfully")
            
            # 2. Logging
            print("Initializing logging system...")
            logging_config = self.config_manager.get_logging_config()
            self.logger = Logger(
                name="CustomsAutomation",
                log_dir=logging_config.log_directory,
                log_level=logging_config.level,
                max_size_mb=logging_config.max_file_size_mb,
                backup_count=logging_config.backup_count
            )
            print("✓ Logging system initialized")
            
            # 3. Database connector
            print("Initializing database connector...")
            db_config = self.config_manager.get_database_config()
            self.ecus_connector = EcusDataConnector(db_config, self.logger)
            if not self.ecus_connector.connect():
                raise RuntimeError("Failed to connect to ECUS5 database")
            print("✓ Database connector initialized")
            self._add_shutdown_handler(self.ecus_connector.disconnect)
            
            # 4. Tracking database
            print("Initializing tracking database...")
            self.tracking_db = TrackingDatabase(logger=self.logger)
            print("✓ Tracking database initialized")
            
            # 5. Declaration processor
            print("Initializing declaration processor...")
            self.processor = DeclarationProcessor(self.ecus_connector, self.logger)
            print("✓ Declaration processor initialized")
            
            # 6. Barcode retriever
            print("Initializing barcode retriever...")
            barcode_config = self.config_manager.get_barcode_service_config()
            retrieval_method = self.config_manager.get_retrieval_method()
            self.barcode_retriever = BarcodeRetriever(
                barcode_config,
                self.logger,
                retrieval_method=retrieval_method
            )
            print("✓ Barcode retriever initialized")
            
            # 7. File manager
            print("Initializing file manager...")
            output_path = self.config_manager.get_output_path()
            naming_format = self.config_manager.get_pdf_naming_format()
            self.file_manager = FileManager(
                output_directory=output_path,
                naming_format=naming_format,
                logger=self.logger
            )
            print("✓ File manager initialized")
            
            # 8. Scheduler
            print("Initializing scheduler...")
            self.scheduler = Scheduler(
                config_manager=self.config_manager,
                ecus_connector=self.ecus_connector,
                tracking_db=self.tracking_db,
                processor=self.processor,
                barcode_retriever=self.barcode_retriever,
                file_manager=self.file_manager,
                logger=self.logger
            )
            print("✓ Scheduler initialized")
            self._add_shutdown_handler(self.scheduler.stop)
            
            self._initialized = True
            self.logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            print(f"FATAL ERROR: {e}")
            if self.logger:
                self.logger.critical(f"Failed to initialize application: {e}", exc_info=True)
            return False
    
    def start(self) -> None:
        """Start the application services."""
        if not self._initialized:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        if self._started:
            return
        
        self.logger.info("Starting application services...")
        
        # Start scheduler if in automatic mode
        if self.scheduler:
            self.scheduler.start()
        
        self._started = True
        self.logger.info("Application started")
    
    def shutdown(self) -> None:
        """Gracefully shutdown all services."""
        if not self._started:
            return
        
        self.logger.info("Shutting down application...")
        
        # Run shutdown handlers in reverse order
        for handler in reversed(self._shutdown_handlers):
            try:
                handler()
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Error during shutdown: {e}")
        
        self._started = False
        self.logger.info("Application shutdown complete")
    
    def _add_shutdown_handler(self, handler: Callable) -> None:
        """Add a shutdown handler to be called during shutdown."""
        self._shutdown_handlers.append(handler)
    
    def _atexit_handler(self) -> None:
        """Handler called on program exit."""
        if self._started:
            self.shutdown()
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    @property
    def is_running(self) -> bool:
        return self._started


# Global application instance
_app: Optional[Application] = None


def get_application() -> Application:
    """Get the global application instance."""
    global _app
    if _app is None:
        _app = Application()
    return _app
