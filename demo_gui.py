"""
Demo script for Customs Barcode Automation GUI

This script demonstrates how to initialize and run the GUI application.
Note: This requires a valid config.ini file and all dependencies installed.
"""

import tkinter as tk
from gui.customs_gui import CustomsAutomationGUI
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from scheduler.scheduler import Scheduler
from logging_system.logger import Logger


def main():
    """Initialize and run the GUI application"""
    
    # Load configuration
    config_manager = ConfigurationManager("config.ini")
    config_manager.validate()
    
    # Initialize logger
    logging_config = config_manager.get_logging_config()
    logger = Logger(logging_config)
    
    logger.info("Starting Customs Barcode Automation GUI")
    
    # Initialize database components
    db_config = config_manager.get_database_config()
    ecus_connector = EcusDataConnector(db_config, logger)
    
    tracking_db_path = "tracking.db"
    tracking_db = TrackingDatabase(tracking_db_path, logger)
    
    # Initialize processors
    processor = DeclarationProcessor(logger)
    
    # Initialize barcode retriever
    barcode_config = config_manager.get_barcode_service_config()
    barcode_retriever = BarcodeRetriever(barcode_config, logger)
    
    # Initialize file manager
    output_path = config_manager.get_output_path()
    file_manager = FileManager(output_path, logger)
    
    # Initialize scheduler
    scheduler = Scheduler(
        config_manager=config_manager,
        ecus_connector=ecus_connector,
        tracking_db=tracking_db,
        processor=processor,
        barcode_retriever=barcode_retriever,
        file_manager=file_manager,
        logger=logger
    )
    
    # Create GUI
    root = tk.Tk()
    
    gui = CustomsAutomationGUI(
        root=root,
        scheduler=scheduler,
        tracking_db=tracking_db,
        config_manager=config_manager,
        logger=logger
    )
    
    logger.info("GUI initialized successfully")
    
    # Run GUI main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    finally:
        # Cleanup
        if scheduler.is_running():
            scheduler.stop()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
