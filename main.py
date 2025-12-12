"""
Customs Barcode Automation - Main Entry Point

This application automates the process of extracting customs declaration information
from the ECUS5 database and retrieving barcodes from the General Department of Customs.
"""

import sys
import signal
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import threading

# Application version
APP_VERSION = "1.2.6"

# Import configuration and logging
from config.configuration_manager import ConfigurationManager, ConfigurationError
from logging_system.logger import Logger

# Import data layer components
from database.ecus_connector import EcusDataConnector
from database.tracking_database import TrackingDatabase

# Import service layer components
from processors.declaration_processor import DeclarationProcessor
from web_utils.barcode_retriever import BarcodeRetriever
from file_utils.file_manager import FileManager
from file_utils.pdf_naming_service import PdfNamingService

# Import application layer components
from scheduler.scheduler import Scheduler
from error_handling.error_handler import ErrorHandler

# Import GUI
from gui.customs_gui import CustomsAutomationGUI


# Global references for cleanup
scheduler_instance = None
ecus_connector_instance = None
logger_instance = None


def signal_handler(sig, frame):
    """Handle graceful shutdown on CTRL+C"""
    print("\nShutting down gracefully...")
    
    # Stop scheduler if running
    if scheduler_instance and scheduler_instance.is_running():
        print("Stopping scheduler...")
        scheduler_instance.stop()
    
    # Disconnect from database
    if ecus_connector_instance:
        print("Closing database connection...")
        ecus_connector_instance.disconnect()
    
    if logger_instance:
        logger_instance.info("Application shutdown complete")
    
    sys.exit(0)


def main():
    """Main application entry point"""
    global scheduler_instance, ecus_connector_instance, logger_instance
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Customs Barcode Automation")
    print("=" * 50)
    
    try:
        # 1. Initialize ConfigurationManager
        print("Loading configuration...")
        config_path = "config.ini"
        
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found: {config_path}")
            print("Please create a config.ini file based on config.ini.sample")
            sys.exit(1)
        
        try:
            config_manager = ConfigurationManager(config_path)
            config_manager.validate()
            print("✓ Configuration loaded successfully")
        except ConfigurationError as e:
            print(f"ERROR: Configuration validation failed:")
            print(f"  {e}")
            sys.exit(1)
        
        # 2. Initialize Logger
        print("Initializing logging system...")
        logging_config = config_manager.get_logging_config()
        logger = Logger(logging_config)
        logger_instance = logger
        logger.info("=" * 60)
        logger.info("Customs Barcode Automation Starting")
        logger.info("=" * 60)
        print("✓ Logging system initialized")
        
        # 3. Initialize Database Connector
        print("Initializing database connector...")
        db_config = config_manager.get_database_config()
        ecus_connector = EcusDataConnector(db_config, logger)
        ecus_connector_instance = ecus_connector
        
        # Try to connect to database (don't exit if failed - allow GUI to start)
        db_connected = False
        try:
            db_connected = ecus_connector.connect()
        except Exception as e:
            logger.warning(f"Database connection attempt failed: {e}")
        
        if db_connected:
            logger.info("Database connection established")
            print("✓ Database connector initialized")
        else:
            logger.warning("Failed to connect to ECUS5 database - application will start without database connection")
            print("⚠ WARNING: Failed to connect to ECUS5 database")
            print("  Application will start, but you need to configure database connection.")
            print("  Use 'Cấu hình DB' button in the application to set up database.")
        
        # 4. Initialize Tracking Database
        print("Initializing tracking database...")
        tracking_db_path = "data/tracking.db"
        tracking_db = TrackingDatabase(tracking_db_path, logger)
        logger.info("Tracking database initialized")
        print("✓ Tracking database initialized")
        
        # 5. Initialize Declaration Processor
        print("Initializing declaration processor...")
        processor = DeclarationProcessor()
        logger.info("Declaration processor initialized")
        print("✓ Declaration processor initialized")
        
        # 6. Initialize Barcode Retriever
        print("Initializing barcode retriever...")
        barcode_config = config_manager.get_barcode_service_config()
        barcode_retriever = BarcodeRetriever(
            barcode_config, 
            logger,
            retrieval_method=barcode_config.retrieval_method
        )
        logger.info(f"Barcode retriever initialized with method: {barcode_config.retrieval_method}")
        print("✓ Barcode retriever initialized")
        
        # 7. Initialize File Manager with PDF Naming Service
        print("Initializing file manager...")
        output_path = config_manager.get_output_path()
        pdf_naming_format = config_manager.get_pdf_naming_format()
        pdf_naming_service = PdfNamingService(pdf_naming_format)
        file_manager = FileManager(output_path, pdf_naming_service)
        file_manager.ensure_directory_exists()
        logger.info(f"File manager initialized with output path: {output_path}, naming format: {pdf_naming_format}")
        print("✓ File manager initialized")
        
        # 8. Initialize Error Handler
        print("Initializing error handler...")
        error_handler = ErrorHandler(
            max_retries=barcode_config.max_retries,
            base_delay=barcode_config.retry_delay,
            logger=logger.get_logger()
        )
        logger.info("Error handler initialized")
        print("✓ Error handler initialized")
        
        # 9. Initialize Scheduler
        print("Initializing scheduler...")
        scheduler = Scheduler(
            config_manager=config_manager,
            ecus_connector=ecus_connector,
            tracking_db=tracking_db,
            processor=processor,
            barcode_retriever=barcode_retriever,
            file_manager=file_manager,
            logger=logger
        )
        scheduler_instance = scheduler
        logger.info("Scheduler initialized")
        print("✓ Scheduler initialized")
        
        # 10. Initialize GUI
        print("Initializing GUI...")
        root = tk.Tk()
        
        # Set up window close handler
        def on_closing():
            """Handle window close event"""
            if scheduler.is_running():
                if messagebox.askokcancel("Quit", "Scheduler is running. Do you want to stop it and quit?"):
                    logger.info("User requested application shutdown")
                    scheduler.stop()
                    ecus_connector.disconnect()
                    logger.info("Application shutdown complete")
                    root.destroy()
            else:
                logger.info("Application shutdown")
                ecus_connector.disconnect()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        app = CustomsAutomationGUI(
            root=root,
            scheduler=scheduler,
            tracking_db=tracking_db,
            ecus_connector=ecus_connector,
            config_manager=config_manager,
            logger=logger,
            barcode_retriever=barcode_retriever,
            file_manager=file_manager
        )
        
        logger.info("GUI initialized")
        print("✓ GUI initialized")
        
        # 11. Check for updates in background
        def check_updates_background():
            """Check for updates in background thread."""
            try:
                from update.update_checker import UpdateChecker
                from gui.update_dialog import UpdateDialog, DownloadProgressDialog, InstallPromptDialog
                from update.download_manager import DownloadManager, DownloadCancelledError
                from update.models import DownloadProgress
                
                github_repo = config_manager.get('Update', 'github_repo', fallback='')
                if not github_repo:
                    logger.debug("No GitHub repo configured for updates")
                    return
                
                checker = UpdateChecker(APP_VERSION, github_repo, config_manager)
                update_info = checker.check_for_updates()
                
                if update_info:
                    logger.info(f"Update available: {update_info.latest_version}")
                    
                    # Show update dialog on main thread
                    def show_update_dialog():
                        dialog = UpdateDialog(root, update_info)
                        result = dialog.show()
                        
                        if result == "update_now":
                            # Download update
                            download_manager = DownloadManager()
                            progress_dialog = DownloadProgressDialog(root, f"CustomsBarcodeAutomation_{update_info.latest_version}.exe")
                            
                            def progress_callback(downloaded, total, speed):
                                progress = DownloadProgress(downloaded, total, speed)
                                root.after(0, lambda: progress_dialog.update_progress(progress))
                            
                            def download_thread():
                                try:
                                    filepath = download_manager.download_file(
                                        update_info.download_url,
                                        f"CustomsBarcodeAutomation_{update_info.latest_version}.exe",
                                        update_info.file_size,
                                        progress_callback
                                    )
                                    
                                    root.after(0, progress_dialog.close)
                                    
                                    # Show install prompt
                                    def show_install_prompt():
                                        install_dialog = InstallPromptDialog(root, filepath)
                                        install_result = install_dialog.show()
                                        
                                        if install_result == "install_now":
                                            # Launch installer and close app
                                            import subprocess
                                            subprocess.Popen([filepath], shell=True)
                                            root.after(500, root.destroy)
                                        else:
                                            # Save pending installer
                                            download_manager.save_pending_installer(filepath, config_manager)
                                    
                                    root.after(0, show_install_prompt)
                                    
                                except DownloadCancelledError:
                                    logger.info("Download cancelled by user")
                                except Exception as e:
                                    logger.error(f"Download failed: {e}")
                                    root.after(0, lambda: messagebox.showerror("Lỗi", f"Tải xuống thất bại: {e}"))
                            
                            threading.Thread(target=download_thread, daemon=True).start()
                            
                        elif result == "skip_version":
                            checker.skip_version(update_info.latest_version)
                    
                    root.after(1000, show_update_dialog)
                else:
                    logger.debug("No updates available")
                    
            except Exception as e:
                logger.warning(f"Update check failed: {e}")
        
        # Start update check in background
        threading.Thread(target=check_updates_background, daemon=True).start()
        
        print("\n" + "=" * 50)
        print("Application initialized successfully")
        print("Starting GUI...")
        print("=" * 50 + "\n")
        
        logger.info("Starting GUI main loop")
        
        # Start GUI main loop
        root.mainloop()
        
        # Cleanup after GUI closes
        logger.info("GUI closed, cleaning up...")
        if scheduler.is_running():
            scheduler.stop()
        ecus_connector.disconnect()
        logger.info("Application terminated normally")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if logger_instance:
            logger_instance.info("Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        if logger_instance:
            logger_instance.critical(f"Fatal error during initialization: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
