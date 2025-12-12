# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create project directory structure with folders for config, database, processors, web_utils, file_utils, scheduler, models, logs
  - Create requirements.txt with all dependencies (pyodbc, selenium, requests, APScheduler, cryptography, hypothesis, pytest)
  - Create main.py as application entry point
  - Create README.md with installation and usage instructions
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 2. Implement configuration management





  - [x] 2.1 Create ConfigurationManager class


    - Implement INI file reading using configparser
    - Create data classes for DatabaseConfig, BarcodeServiceConfig
    - Implement password encryption/decryption using Fernet
    - Add configuration validation logic
    - Add methods to get and set configuration values
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [x] 2.2 Write property test for configuration encryption


    - **Property 10: Configuration encryption**
    - **Validates: Requirements 6.6**

  - [x] 2.3 Write property test for configuration validation


    - **Property 11: Configuration validation**
    - **Validates: Requirements 6.7**

  - [x] 2.4 Write unit tests for ConfigurationManager


    - Test loading valid configuration
    - Test handling missing configuration
    - Test password encryption/decryption
    - Test configuration validation
    - _Requirements: 6.1, 6.6, 6.7_

- [x] 3. Implement logging system





  - [x] 3.1 Create Logger class


    - Set up Python logging with file and console handlers
    - Implement log rotation using RotatingFileHandler
    - Configure log formatting with timestamp and module name
    - Support multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 3.2 Write property test for log entry completeness


    - **Property 12: Log entry completeness**
    - **Validates: Requirements 7.1**

  - [x] 3.3 Write property test for error log detail


    - **Property 13: Error log detail**
    - **Validates: Requirements 7.2**

  - [x] 3.4 Write property test for log rotation


    - **Property 14: Log rotation trigger**
    - **Validates: Requirements 7.6**

- [x] 4. Implement data models





  - [x] 4.1 Create Declaration dataclass


    - Define all required fields (declaration_number, tax_code, etc.)
    - Implement id property for unique identification
    - Add to_dict method for serialization
    - _Requirements: 1.2_

  - [x] 4.2 Create supporting data classes

    - Create ProcessedDeclaration dataclass with file_path and timestamps
    - Create WorkflowResult dataclass for execution results
    - Create OperationMode enum (AUTOMATIC, MANUAL)
    - _Requirements: 8.1, 11.2_

  - [x] 4.3 Write unit tests for data models


    - Test Declaration id generation
    - Test ProcessedDeclaration display_name
    - Test WorkflowResult duration calculation
    - _Requirements: 1.2, 8.3_

- [x] 5. Implement database connectivity




  - [x] 5.1 Create EcusDataConnector class


    - Implement SQL Server connection using pyodbc
    - Create connection string from DatabaseConfig
    - Implement connect, disconnect, and reconnect methods
    - Add connection testing functionality
    - _Requirements: 1.1, 1.3, 9.2_

  - [x] 5.2 Implement declaration extraction query


    - Write SQL query to extract declarations from DToKhaiMDIDs and DHangMDDKs
    - Filter by date range (last 7 days)
    - Filter by status (TTTK = 'T')
    - Filter by channel (PLUONG = 'Xanh' or 'Vang')
    - Map database records to Declaration objects
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 5.3 Write property test for database query completeness


    - **Property 1: Database query completeness**
    - **Validates: Requirements 1.2**

  - [x] 5.4 Write property test for automatic reconnection


    - **Property 18: Automatic reconnection**
    - **Validates: Requirements 9.2**

  - [x] 5.5 Write unit tests for EcusDataConnector


    - Test connection string generation
    - Test successful connection
    - Test connection failure handling
    - Test query execution with mock data
    - _Requirements: 1.1, 1.3, 9.2_

- [x] 6. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement declaration processing logic





  - [x] 7.1 Create DeclarationProcessor class


    - Implement channel filtering (Xanh/Vang only)
    - Implement status filtering (T = cleared)
    - Implement transport method exclusion (code 9999)
    - Implement internal code exclusion (#&NKTC, #&XKTC)
    - Implement date formatting (to ddmmyyyy)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 7.2 Write property test for channel filtering


    - **Property 2: Channel filtering correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

  - [x] 7.3 Write property test for transport method exclusion


    - **Property 3: Transport method exclusion**
    - **Validates: Requirements 3.1**

  - [x] 7.4 Write property test for internal code exclusion


    - **Property 4: Internal code exclusion**
    - **Validates: Requirements 3.2, 3.3**

  - [x] 7.5 Write unit tests for DeclarationProcessor


    - Test green channel eligibility
    - Test yellow channel eligibility
    - Test red channel exclusion
    - Test transport method 9999 exclusion
    - Test internal code exclusion
    - Test date formatting
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3_

- [x] 8. Implement barcode retrieval





  - [x] 8.1 Create BarcodeRetriever class with API support


    - Implement SOAP API client for QRCode service
    - Build SOAP request with declaration details
    - Parse SOAP response to extract PDF content
    - Handle API errors and timeouts
    - _Requirements: 4.1, 4.4, 4.7_

  - [x] 8.2 Add web scraping fallback

    - Set up Selenium WebDriver (Chrome/Edge)
    - Implement navigation to barcode websites
    - Implement form filling with declaration data
    - Implement PDF download from web page
    - Handle web scraping errors
    - _Requirements: 4.2, 4.3, 4.5, 4.7_

  - [x] 8.3 Implement fallback chain logic

    - Try API first
    - Fallback to primary website if API fails
    - Fallback to backup website if primary fails
    - Log each attempt and result
    - _Requirements: 4.1, 4.2, 4.3, 4.6_

  - [x] 8.4 Write property test for barcode retrieval fallback chain


    - **Property 5: Barcode retrieval fallback chain**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [x] 8.5 Write property test for API request completeness


    - **Property 6: API request completeness**
    - **Validates: Requirements 4.4**

  - [x] 8.6 Write unit tests for BarcodeRetriever


    - Test API request building
    - Test API response parsing
    - Test web scraping with mock browser
    - Test fallback logic
    - Test error handling
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 9. Implement file management



  - [x] 9.1 Create FileManager class


    - Implement filename generation (TaxCode_DeclarationNumber.pdf)
    - Implement directory creation
    - Implement file existence checking
    - Implement PDF saving with overwrite support
    - Handle file system errors
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 9.2 Write property test for filename format


    - **Property 7: Filename format consistency**
    - **Validates: Requirements 5.1**

  - [x] 9.3 Write property test for directory creation


    - **Property 8: Directory creation before save**
    - **Validates: Requirements 5.2**

  - [x] 9.4 Write property test for duplicate file handling



    - **Property 9: Duplicate file handling**
    - **Validates: Requirements 5.3**

  - [x] 9.5 Write unit tests for FileManager


    - Test filename generation
    - Test directory creation
    - Test file saving
    - Test overwrite behavior
    - Test error handling
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 10. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement tracking database





  - [x] 11.1 Create TrackingDatabase class


    - Set up SQLite database connection
    - Create processed_declarations table with schema
    - Create indexes for performance
    - Implement add_processed method
    - Implement is_processed method
    - Implement get_all_processed method
    - _Requirements: 8.1, 8.2, 8.3, 8.5_

  - [x] 11.2 Add search and management features


    - Implement get_all_processed_details for GUI display
    - Implement search_declarations with query filtering
    - Implement update_processed_timestamp for re-downloads
    - Implement rebuild_from_directory for recovery
    - _Requirements: 8.4, 12.1, 12.6, 12.7_

  - [x] 11.3 Write property test for tracking uniqueness


    - **Property 15: Tracking database uniqueness**
    - **Validates: Requirements 8.3**

  - [x] 11.4 Write property test for duplicate prevention


    - **Property 16: Duplicate processing prevention**
    - **Validates: Requirements 8.2**

  - [x] 11.5 Write unit tests for TrackingDatabase


    - Test database creation
    - Test adding processed declarations
    - Test checking if processed
    - Test searching declarations
    - Test updating timestamps
    - Test rebuilding from directory
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 12.6_

- [x] 12. Implement error handling






  - [x] 12.1 Create ErrorHandler class

    - Implement retry with exponential backoff
    - Implement graceful error handling
    - Add error categorization
    - Add error logging
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 12.2 Write property test for retry with exponential backoff


    - **Property 17: Retry with exponential backoff**
    - **Validates: Requirements 9.1**

  - [x] 12.3 Write property test for exception handling continuity


    - **Property 19: Exception handling continuity**
    - **Validates: Requirements 9.4, 9.5**

  - [x] 12.4 Write unit tests for ErrorHandler


    - Test retry logic
    - Test exponential backoff timing
    - Test graceful error handling
    - Test error logging
    - _Requirements: 9.1, 9.4, 9.5_

- [x] 13. Implement workflow scheduler





  - [x] 13.1 Create Scheduler class


    - Set up APScheduler for periodic execution
    - Implement start and stop methods
    - Implement operation mode support (automatic/manual)
    - Implement run_once for manual execution
    - Implement mode persistence to configuration
    - _Requirements: 1.5, 11.1, 11.2, 11.3, 11.4, 11.6_

  - [x] 13.2 Implement workflow execution logic

    - Get processed IDs from tracking database
    - Fetch new declarations from ECUS5
    - Filter declarations using DeclarationProcessor
    - Process each eligible declaration
    - Retrieve barcode using BarcodeRetriever
    - Save PDF using FileManager
    - Update tracking database
    - Return WorkflowResult with statistics
    - _Requirements: 1.1, 1.5, 8.1, 8.2_

  - [x] 13.3 Add re-download functionality

    - Implement redownload_declarations method
    - Support force_redownload flag in workflow
    - Implement file overwriting for re-downloads
    - Update timestamps in tracking database
    - _Requirements: 12.3, 12.4, 12.5_

  - [x] 13.4 Write property test for operation mode persistence


    - **Property 21: Operation mode persistence**
    - **Validates: Requirements 11.1, 11.6**

  - [x] 13.5 Write property test for automatic mode scheduling


    - **Property 22: Automatic mode scheduling**
    - **Validates: Requirements 11.3**

  - [x] 13.6 Write property test for manual mode execution


    - **Property 23: Manual mode execution control**
    - **Validates: Requirements 11.4**

  - [x] 13.7 Write property test for re-download overwrite


    - **Property 24: Re-download overwrite behavior**
    - **Validates: Requirements 12.4, 12.5**

  - [x] 13.8 Write unit tests for Scheduler


    - Test workflow execution
    - Test mode switching
    - Test automatic scheduling
    - Test manual execution
    - Test re-download logic
    - _Requirements: 1.5, 11.3, 11.4, 12.3, 12.4_

- [x] 14. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Implement GUI application





  - [x] 15.1 Create main window layout


    - Set up tkinter root window
    - Create control panel frame with status display
    - Create statistics display area
    - Create operation mode toggle (radio buttons)
    - Add start, stop, and run once buttons
    - Add output directory configuration with browse button
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.8, 11.5, 11.7_

  - [x] 15.2 Create processed declarations panel

    - Create table/listbox for processed declarations
    - Add search input and button
    - Add checkboxes for selection
    - Add re-download button
    - Add open file location button
    - Add refresh button
    - Display declaration number, tax code, date, and timestamp
    - _Requirements: 12.1, 12.2, 12.3, 12.6, 12.7_

  - [x] 15.3 Create log display panel

    - Create scrollable text widget for logs
    - Implement log appending from logger
    - Add auto-scroll to latest log
    - Format logs with colors for different levels
    - _Requirements: 10.7_

  - [x] 15.4 Implement GUI event handlers

    - Connect start button to scheduler.start()
    - Connect stop button to scheduler.stop()
    - Connect run once button to scheduler.run_once()
    - Connect mode toggle to scheduler.set_operation_mode()
    - Connect browse button to directory selection dialog
    - Connect search button to tracking database search
    - Connect re-download button to redownload_declarations()
    - Connect open file location to file explorer
    - _Requirements: 10.5, 10.6, 10.8, 11.5, 12.2, 12.3_

  - [x] 15.5 Implement GUI updates

    - Update statistics display after each workflow execution
    - Update processed declarations list on refresh
    - Update log display in real-time
    - Update status indicator (running/stopped)
    - Update mode indicator (automatic/manual)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 11.7_

  - [x] 15.6 Write property test for statistics display accuracy


    - **Property 20: Statistics display accuracy**
    - **Validates: Requirements 10.2, 10.3, 10.4**

  - [x] 15.7 Write property test for search functionality


    - **Property 25: Search functionality**
    - **Validates: Requirements 12.6**

  - [x] 15.8 Write unit tests for GUI components


    - Test button click handlers
    - Test mode switching
    - Test statistics updates
    - Test search functionality
    - Test re-download selection
    - _Requirements: 10.5, 10.6, 11.5, 12.2, 12.6_

- [x] 16. Integrate all components in main application





  - [x] 16.1 Create main.py entry point


    - Initialize ConfigurationManager
    - Initialize Logger
    - Initialize all service components
    - Initialize Scheduler
    - Initialize GUI
    - Set up signal handlers for graceful shutdown
    - _Requirements: 6.1, 7.1_

  - [x] 16.2 Implement application lifecycle


    - Load configuration on startup
    - Validate configuration before proceeding
    - Initialize database connections
    - Start GUI main loop
    - Handle shutdown gracefully
    - _Requirements: 6.7, 9.5_

  - [x] 16.3 Write integration tests


    - Test end-to-end workflow execution
    - Test configuration loading and validation
    - Test database connectivity
    - Test file operations
    - Test error recovery
    - _Requirements: 1.1, 1.5, 6.7, 9.5_

- [x] 17. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Create documentation and packaging





  - [x] 18.1 Write user documentation


    - Create README.md with installation instructions
    - Document configuration options
    - Create user guide with screenshots
    - Document troubleshooting steps
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 18.2 Create deployment package


    - Create requirements.txt with all dependencies
    - Create sample configuration file (config.ini.sample)
    - Create installation script
    - Test installation on clean Windows machine
    - _Requirements: 6.1_

  - [x] 18.3 Create PyInstaller executable


    - Configure PyInstaller spec file
    - Bundle all dependencies
    - Include WebDriver
    - Test standalone executable
    - _Requirements: 6.1_
