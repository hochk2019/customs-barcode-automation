# Design Document

## Overview

Ứng dụng Customs Barcode Automation là một hệ thống Windows desktop được xây dựng bằng Python, sử dụng kiến trúc modular để tự động hóa quy trình lấy mã vạch tờ khai hải quan. Hệ thống kết nối với cơ sở dữ liệu ECUS5 SQL Server, trích xuất thông tin tờ khai, áp dụng các quy tắc lọc nghiệp vụ, và tự động lấy mã vạch thông qua API hoặc web scraping.

Kiến trúc được thiết kế theo nguyên tắc separation of concerns, với các module độc lập chịu trách nhiệm cho từng chức năng cụ thể. Điều này đảm bảo tính dễ bảo trì, khả năng mở rộng và khả năng test.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                  (Windows Desktop GUI - Tkinter)             │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Application Core Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scheduler  │  │  Declaration │  │    Logger    │     │
│  │              │  │  Processor   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Service Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ECUS5 Data   │  │   Barcode    │  │    File      │     │
│  │  Connector   │  │  Retriever   │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  SQL Server  │  │    SQLite    │  │  File System │     │
│  │   (ECUS5)    │  │  (Tracking)  │  │   (PDFs)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language**: Python 3.8+
- **Database Connectivity**: pyodbc (SQL Server), sqlite3 (tracking)
- **Web Automation**: Selenium WebDriver with Chrome/Edge
- **HTTP Client**: requests (for API calls)
- **GUI Framework**: tkinter (built-in with Python)
- **Scheduling**: APScheduler
- **Logging**: Python logging module
- **Configuration**: configparser (INI files)
- **Encryption**: cryptography (Fernet)

## Components and Interfaces

### 1. ConfigurationManager

**Purpose**: Centralized configuration management with encryption support.

**Responsibilities**:
- Load configuration from INI file
- Encrypt/decrypt sensitive data (passwords)
- Provide configuration access to other modules
- Validate configuration completeness

**Interface**:
```python
class ConfigurationManager:
    def __init__(self, config_path: str)
    def get_database_config(self) -> DatabaseConfig
    def get_barcode_service_config(self) -> BarcodeServiceConfig
    def get_output_path(self) -> str
    def get_polling_interval(self) -> int
    def set_output_path(self, path: str) -> None
    def save(self) -> None
```

**Configuration File Structure** (config.ini):
```ini
[Database]
server = Server
database = ECUS5VNACCS
username = sa
password = <encrypted>

[BarcodeService]
api_url = http://103.248.160.25:8086/WS_Container/QRCode.asmx
primary_web_url = https://pus.customs.gov.vn/faces/ContainerBarcode
backup_web_url = https://pus1.customs.gov.vn/BarcodeContainer/BarcodeContainer.aspx
timeout = 30

[Application]
output_directory = C:\CustomsBarcodes
polling_interval = 300
max_retries = 3
retry_delay = 5
operation_mode = automatic

[Logging]
log_level = INFO
log_file = logs/app.log
max_log_size = 10485760
backup_count = 5
```

### 2. EcusDataConnector

**Purpose**: Handle all interactions with ECUS5 SQL Server database.

**Responsibilities**:
- Establish and maintain database connection
- Execute queries to extract declaration data
- Handle connection errors and reconnection
- Map database records to domain objects

**Interface**:
```python
class EcusDataConnector:
    def __init__(self, config: DatabaseConfig)
    def connect(self) -> bool
    def disconnect(self) -> None
    def get_new_declarations(self, processed_ids: Set[str]) -> List[Declaration]
    def test_connection(self) -> bool
    def reconnect(self) -> bool
```

**SQL Query**:
```sql
SELECT 
    tk.SOTK as declaration_number,
    tk.MA_DV as tax_code,
    tk.NGAY_DK as declaration_date,
    tk.MA_HQ as customs_office_code,
    tk.MA_PTVT as transport_method,
    tk.PLUONG as channel,
    tk.TTTK as status,
    hh.TEN_HANG as goods_description
FROM DToKhaiMDIDs tk
LEFT JOIN DHangMDDKs hh ON tk._DToKhaiMDID = hh._DToKhaiMDID
WHERE tk.NGAY_DK >= DATEADD(day, -7, GETDATE())
    AND tk.TTTK = 'T'
    AND (tk.PLUONG = 'Xanh' OR tk.PLUONG = 'Vang')
ORDER BY tk.NGAY_DK DESC
```

### 3. DeclarationProcessor

**Purpose**: Apply business rules to filter declarations.

**Responsibilities**:
- Filter by channel (Green/Yellow)
- Filter by cleared status
- Exclude by transport method
- Exclude by internal management codes
- Transform date formats

**Interface**:
```python
class DeclarationProcessor:
    def __init__(self)
    def filter_declarations(self, declarations: List[Declaration]) -> List[Declaration]
    def is_eligible(self, declaration: Declaration) -> bool
    def format_date(self, date: datetime) -> str  # to ddmmyyyy
```

**Business Rules**:
```python
def is_eligible(self, declaration: Declaration) -> bool:
    # Check channel
    if declaration.channel not in ['Xanh', 'Vang']:
        return False
    
    # Check status
    if declaration.status != 'T':
        return False
    
    # Check transport method
    if declaration.transport_method == '9999':
        return False
    
    # Check internal codes
    if declaration.goods_description:
        if declaration.goods_description.startswith('#&NKTC'):
            return False
        if declaration.goods_description.startswith('#&XKTC'):
            return False
    
    return True
```

### 4. BarcodeRetriever

**Purpose**: Retrieve barcode PDFs from customs services.

**Responsibilities**:
- Attempt API retrieval first
- Fallback to web scraping if API fails
- Handle multiple web URLs
- Return PDF content as bytes

**Interface**:
```python
class BarcodeRetriever:
    def __init__(self, config: BarcodeServiceConfig)
    def retrieve_barcode(self, declaration: Declaration) -> Optional[bytes]
    def _try_api(self, declaration: Declaration) -> Optional[bytes]
    def _try_web_scraping(self, url: str, declaration: Declaration) -> Optional[bytes]
    def _setup_webdriver(self) -> webdriver.Chrome
```

**API Call Structure** (SOAP):
```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetBarcode xmlns="http://tempuri.org/">
      <declarationNumber>{SOTK}</declarationNumber>
      <taxCode>{MA_DV}</taxCode>
      <declarationDate>{NGAY_DK}</declarationDate>
      <customsOffice>{MA_HQ}</customsOffice>
    </GetBarcode>
  </soap:Body>
</soap:Envelope>
```

**Web Scraping Flow**:
1. Initialize Selenium WebDriver (headless mode)
2. Navigate to barcode URL
3. Wait for page load
4. Fill form fields:
   - Mã doanh nghiệp: tax_code
   - Số tờ khai: declaration_number
   - Ngày tờ khai: declaration_date (ddmmyyyy)
   - Mã hải quan: customs_office_code
5. Click "Lấy thông tin" button
6. Wait for PDF generation
7. Download PDF content
8. Close WebDriver

### 5. FileManager

**Purpose**: Handle PDF file operations with overwrite support.

**Responsibilities**:
- Generate standardized filenames
- Save PDF content to disk
- Check for existing files
- Create directories as needed
- Support file overwriting for re-downloads

**Interface**:
```python
class FileManager:
    def __init__(self, output_directory: str)
    def save_barcode(self, declaration: Declaration, pdf_content: bytes, 
                     overwrite: bool = False) -> Optional[str]
    def generate_filename(self, declaration: Declaration) -> str
    def get_file_path(self, declaration: Declaration) -> str
    def file_exists(self, filename: str) -> bool
    def ensure_directory_exists(self) -> None
```

**Filename Format**:
```python
def generate_filename(self, declaration: Declaration) -> str:
    return f"{declaration.tax_code}_{declaration.declaration_number}.pdf"

def get_file_path(self, declaration: Declaration) -> str:
    filename = self.generate_filename(declaration)
    return os.path.join(self.output_directory, filename)
```

### 6. TrackingDatabase

**Purpose**: Track processed declarations to avoid duplicates and support re-download.

**Responsibilities**:
- Store processed declaration IDs with metadata
- Query for already processed declarations
- Rebuild from file system if corrupted
- Support searching and filtering
- Update processing timestamps

**Interface**:
```python
class TrackingDatabase:
    def __init__(self, db_path: str)
    def add_processed(self, declaration: Declaration, file_path: str) -> None
    def is_processed(self, declaration: Declaration) -> bool
    def get_all_processed(self) -> Set[str]
    def get_all_processed_details(self) -> List[ProcessedDeclaration]
    def search_declarations(self, query: str) -> List[ProcessedDeclaration]
    def update_processed_timestamp(self, declaration: Declaration) -> None
    def rebuild_from_directory(self, directory: str) -> None
```

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS processed_declarations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    declaration_number TEXT NOT NULL,
    tax_code TEXT NOT NULL,
    declaration_date TEXT NOT NULL,
    file_path TEXT NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(declaration_number, tax_code, declaration_date)
);

CREATE INDEX idx_declaration_lookup 
ON processed_declarations(declaration_number, tax_code, declaration_date);

CREATE INDEX idx_search 
ON processed_declarations(declaration_number, tax_code);
```

### 7. Scheduler

**Purpose**: Orchestrate periodic execution of the workflow with mode support.

**Responsibilities**:
- Schedule polling at configured intervals (automatic mode)
- Execute the main workflow
- Handle workflow errors gracefully
- Provide manual trigger capability
- Support automatic/manual mode switching

**Interface**:
```python
class Scheduler:
    def __init__(self, config: ConfigurationManager)
    def start(self) -> None
    def stop(self) -> None
    def set_operation_mode(self, mode: OperationMode) -> None
    def get_operation_mode(self) -> OperationMode
    def run_once(self, force_redownload: bool = False) -> WorkflowResult
    def _execute_workflow(self, force_redownload: bool = False) -> WorkflowResult
```

**Workflow Execution**:
```python
def _execute_workflow(self, force_redownload: bool = False) -> WorkflowResult:
    result = WorkflowResult()
    
    # 1. Get processed IDs (skip if force_redownload)
    processed_ids = set() if force_redownload else tracking_db.get_all_processed()
    
    # 2. Fetch new declarations
    declarations = ecus_connector.get_new_declarations(processed_ids)
    result.total_fetched = len(declarations)
    
    # 3. Filter declarations
    eligible = processor.filter_declarations(declarations)
    result.total_eligible = len(eligible)
    
    # 4. Process each declaration
    for declaration in eligible:
        try:
            # Retrieve barcode
            pdf_content = barcode_retriever.retrieve_barcode(declaration)
            
            if pdf_content:
                # Save to file (overwrite if force_redownload)
                file_path = file_manager.save_barcode(
                    declaration, 
                    pdf_content, 
                    overwrite=force_redownload
                )
                
                if file_path:
                    # Mark as processed or update timestamp
                    if force_redownload and tracking_db.is_processed(declaration):
                        tracking_db.update_processed_timestamp(declaration)
                    else:
                        tracking_db.add_processed(declaration, file_path)
                    result.success_count += 1
                else:
                    result.error_count += 1
            else:
                result.error_count += 1
                
        except Exception as e:
            logger.error(f"Error processing {declaration.id}: {e}")
            result.error_count += 1
    
    return result
```

**Re-download Specific Declarations**:
```python
def redownload_declarations(self, declarations: List[Declaration]) -> WorkflowResult:
    """Re-download barcodes for specific declarations"""
    result = WorkflowResult()
    result.total_fetched = len(declarations)
    result.total_eligible = len(declarations)
    
    for declaration in declarations:
        try:
            # Retrieve barcode
            pdf_content = barcode_retriever.retrieve_barcode(declaration)
            
            if pdf_content:
                # Save to file (overwrite existing)
                file_path = file_manager.save_barcode(
                    declaration, 
                    pdf_content, 
                    overwrite=True
                )
                
                if file_path:
                    # Update timestamp
                    tracking_db.update_processed_timestamp(declaration)
                    result.success_count += 1
                else:
                    result.error_count += 1
            else:
                result.error_count += 1
                
        except Exception as e:
            logger.error(f"Error re-downloading {declaration.id}: {e}")
            result.error_count += 1
    
    return result
```

### 8. Logger

**Purpose**: Centralized logging system.

**Responsibilities**:
- Log to file with rotation
- Log to console
- Support multiple log levels
- Format log messages consistently

**Interface**:
```python
class Logger:
    def __init__(self, config: LoggingConfig)
    def debug(self, message: str, **kwargs) -> None
    def info(self, message: str, **kwargs) -> None
    def warning(self, message: str, **kwargs) -> None
    def error(self, message: str, exc_info=None, **kwargs) -> None
    def critical(self, message: str, exc_info=None, **kwargs) -> None
```

**Log Format**:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 9. GUI Application

**Purpose**: Provide user interface for monitoring, control, and re-download management.

**Responsibilities**:
- Display application status
- Show statistics (processed, errors, etc.)
- Provide start/stop controls
- Support automatic/manual mode switching
- Allow configuration changes
- Display recent logs
- Manage processed declarations list
- Support re-download functionality

**Interface**:
```python
class CustomsAutomationGUI:
    def __init__(self, root: tk.Tk)
    def start_automation(self) -> None
    def stop_automation(self) -> None
    def run_manual_cycle(self) -> None
    def toggle_operation_mode(self) -> None
    def update_statistics(self, result: WorkflowResult) -> None
    def append_log(self, message: str) -> None
    def browse_output_directory(self) -> None
    def load_processed_declarations(self) -> None
    def search_declarations(self, query: str) -> None
    def redownload_selected(self) -> None
    def open_file_location(self, file_path: str) -> None
```

**GUI Layout**:
```
┌─────────────────────────────────────────────────────────────────────┐
│  Customs Barcode Automation                                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─ Control Panel ──────────────────────────────────────────────┐  │
│  │ Status: ● Running                                             │  │
│  │ Mode: ○ Automatic  ○ Manual                                   │  │
│  │                                                                │  │
│  │ Statistics:                                                    │  │
│  │   Declarations Processed: 1,234                                │  │
│  │   Barcodes Retrieved: 1,180                                    │  │
│  │   Errors: 54                                                   │  │
│  │   Last Run: 2023-12-06 14:30:25                                │  │
│  │                                                                │  │
│  │ [Start] [Stop] [Run Once]                                      │  │
│  │                                                                │  │
│  │ Output Directory: C:\CustomsBarcodes  [Browse...]              │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─ Processed Declarations ─────────────────────────────────────┐  │
│  │ Search: [________________]  [Search]                          │  │
│  │                                                                │  │
│  │ ┌──────────────────────────────────────────────────────────┐ │  │
│  │ │ ☐ 2300782217_308010891440  | 05/01/2023 | 14:25:30       │ │  │
│  │ │ ☐ 0700798384_305254416960  | 30/12/2022 | 10:15:22       │ │  │
│  │ │ ☐ 2300646077_105205185850  | 05/01/2023 | 09:47:18       │ │  │
│  │ │ ...                                                        │ │  │
│  │ └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │ [Re-download Selected] [Open File Location] [Refresh]          │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─ Recent Logs ────────────────────────────────────────────────┐  │
│  │ 14:30:25 - INFO - Starting workflow cycle                     │  │
│  │ 14:30:26 - INFO - Fetched 15 new declarations                 │  │
│  │ 14:30:27 - INFO - 12 declarations eligible                    │  │
│  │ 14:30:35 - INFO - Successfully saved barcode for 2300782217   │  │
│  │ 14:30:36 - ERROR - Failed to retrieve barcode for 0700798384  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Models

### Declaration

```python
@dataclass
class Declaration:
    declaration_number: str
    tax_code: str
    declaration_date: datetime
    customs_office_code: str
    transport_method: str
    channel: str  # 'Xanh' or 'Vang'
    status: str  # 'T' for cleared
    goods_description: Optional[str]
    
    @property
    def id(self) -> str:
        """Unique identifier for tracking"""
        date_str = self.declaration_date.strftime('%Y%m%d')
        return f"{self.tax_code}_{self.declaration_number}_{date_str}"
    
    def to_dict(self) -> dict:
        return asdict(self)
```

### DatabaseConfig

```python
@dataclass
class DatabaseConfig:
    server: str
    database: str
    username: str
    password: str
    timeout: int = 30
    
    @property
    def connection_string(self) -> str:
        return (
            f"DRIVER={{SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"Connection Timeout={self.timeout};"
        )
```

### BarcodeServiceConfig

```python
@dataclass
class BarcodeServiceConfig:
    api_url: str
    primary_web_url: str
    backup_web_url: str
    timeout: int
    max_retries: int
    retry_delay: int
```

### WorkflowResult

```python
@dataclass
class WorkflowResult:
    total_fetched: int = 0
    total_eligible: int = 0
    success_count: int = 0
    error_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> timedelta:
        if self.end_time:
            return self.end_time - self.start_time
        return timedelta(0)
```

### ProcessedDeclaration

```python
@dataclass
class ProcessedDeclaration:
    id: int
    declaration_number: str
    tax_code: str
    declaration_date: str
    file_path: str
    processed_at: datetime
    updated_at: datetime
    
    @property
    def display_name(self) -> str:
        """Display name for UI"""
        return f"{self.tax_code}_{self.declaration_number}"
    
    def file_exists(self) -> bool:
        """Check if the PDF file still exists"""
        return os.path.exists(self.file_path)
```

### OperationMode

```python
class OperationMode(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



### Property 1: Database query completeness
*For any* polling cycle, when querying the database, all required fields (DeclarationNumber, TaxCode, declaration date, CustomsOfficeCode, TransportMethod, channel, status, goods description) should be extracted from the result set.
**Validates: Requirements 1.2**

### Property 2: Channel filtering correctness
*For any* CustomsDeclaration, it should be marked as eligible if and only if its channel is either 'Xanh' (Green) or 'Vang' (Yellow) AND its status is 'T' (Cleared).
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

### Property 3: Transport method exclusion
*For any* CustomsDeclaration with TransportMethod code '9999', it should be excluded from processing.
**Validates: Requirements 3.1**

### Property 4: Internal code exclusion
*For any* CustomsDeclaration where the goods description starts with "#&NKTC" or "#&XKTC", it should be excluded from processing.
**Validates: Requirements 3.2, 3.3**

### Property 5: Barcode retrieval fallback chain
*For any* eligible CustomsDeclaration, when attempting barcode retrieval, the system should try API first, then primary website, then backup website, in that order.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 6: API request completeness
*For any* API barcode retrieval request, all required fields (DeclarationNumber, TaxCode, declaration date, CustomsOfficeCode) should be included in the request.
**Validates: Requirements 4.4**

### Property 7: Filename format consistency
*For any* CustomsDeclaration, the generated PDF filename should follow the format "{TaxCode}_{DeclarationNumber}.pdf".
**Validates: Requirements 5.1**

### Property 8: Directory creation before save
*For any* file save operation, if the output directory does not exist, it should be created before attempting to save the file.
**Validates: Requirements 5.2**

### Property 9: Duplicate file handling
*For any* file save operation where a file with the same name already exists and overwrite is False, the system should skip saving and log a warning.
**Validates: Requirements 5.3**

### Property 10: Configuration encryption
*For any* password stored in configuration, it should be encrypted when saved to disk.
**Validates: Requirements 6.6**

### Property 11: Configuration validation
*For any* application startup, if required configuration fields are missing or invalid, the system should display an error and prevent startup.
**Validates: Requirements 6.7**

### Property 12: Log entry completeness
*For any* logged operation, the log entry should include a timestamp and module name.
**Validates: Requirements 7.1**

### Property 13: Error log detail
*For any* logged error, the log entry should include the full stack trace.
**Validates: Requirements 7.2**

### Property 14: Log rotation trigger
*For any* log file that exceeds the configured size limit, the system should rotate to a new log file.
**Validates: Requirements 7.6**

### Property 15: Tracking database uniqueness
*For any* CustomsDeclaration, the unique identifier in the tracking database should be the combination of DeclarationNumber, TaxCode, and declaration date.
**Validates: Requirements 8.3**

### Property 16: Duplicate processing prevention
*For any* CustomsDeclaration already in the tracking database, it should be excluded from the processing queue unless force_redownload is True.
**Validates: Requirements 8.2**

### Property 17: Retry with exponential backoff
*For any* network error during barcode retrieval, the system should retry up to 3 times with exponentially increasing delays.
**Validates: Requirements 9.1**

### Property 18: Automatic reconnection
*For any* database connection loss, the system should attempt to reconnect automatically before the next operation.
**Validates: Requirements 9.2**

### Property 19: Exception handling continuity
*For any* unhandled exception during workflow execution, the system should log the error and continue with the next polling cycle without terminating.
**Validates: Requirements 9.4, 9.5**

### Property 20: Statistics display accuracy
*For any* workflow execution, the displayed statistics (processed count, success count, error count) should match the actual WorkflowResult values.
**Validates: Requirements 10.2, 10.3, 10.4**

### Property 21: Operation mode persistence
*For any* operation mode change, the new mode should be saved to configuration and loaded on the next application start.
**Validates: Requirements 11.1, 11.6**

### Property 22: Automatic mode scheduling
*For any* time period when automatic mode is enabled, the system should execute polling cycles at the configured interval.
**Validates: Requirements 11.3**

### Property 23: Manual mode execution control
*For any* time period when manual mode is enabled, the system should only execute workflow when manually triggered by the user.
**Validates: Requirements 11.4**

### Property 24: Re-download overwrite behavior
*For any* re-download operation on a processed declaration, the system should overwrite the existing PDF file and update the processed timestamp.
**Validates: Requirements 12.4, 12.5**

### Property 25: Search functionality
*For any* search query in the processed declarations list, the results should include all declarations where the DeclarationNumber or TaxCode contains the query string.
**Validates: Requirements 12.6**

## Error Handling

### Error Categories

1. **Database Errors**
   - Connection failures: Retry with exponential backoff, log error
   - Query errors: Log error with SQL statement, skip current cycle
   - Timeout errors: Increase timeout, retry once

2. **Network Errors**
   - API unavailable: Fallback to web scraping
   - Website unavailable: Try backup URL
   - Timeout: Retry with increased timeout
   - SSL errors: Log error, skip declaration

3. **File System Errors**
   - Permission denied: Log error, notify user
   - Disk full: Log critical error, pause automation
   - Path not found: Create directory, retry

4. **Data Errors**
   - Invalid declaration data: Log warning, skip declaration
   - Missing required fields: Log error, skip declaration
   - Date format errors: Attempt parsing with multiple formats

5. **Configuration Errors**
   - Missing configuration: Display error, prevent startup
   - Invalid values: Use defaults, log warning
   - Decryption errors: Prompt user for re-entry

### Error Recovery Strategies

```python
class ErrorHandler:
    def __init__(self, max_retries: int = 3, base_delay: int = 5)
    
    def handle_with_retry(self, operation: Callable, 
                         error_types: Tuple[Type[Exception], ...]) -> Any:
        """Execute operation with exponential backoff retry"""
        for attempt in range(self.max_retries):
            try:
                return operation()
            except error_types as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. "
                             f"Retrying in {delay}s...")
                time.sleep(delay)
    
    def handle_gracefully(self, operation: Callable, 
                         default: Any = None) -> Any:
        """Execute operation and return default on error"""
        try:
            return operation()
        except Exception as e:
            logger.error(f"Operation failed: {e}", exc_info=True)
            return default
```

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Coverage Areas**:
- Configuration loading and validation
- Declaration filtering logic
- Filename generation
- Date format conversion
- Database query construction
- Error handling functions

**Example Unit Tests**:
```python
def test_filename_generation():
    """Test that filenames follow the correct format"""
    declaration = Declaration(
        declaration_number="308010891440",
        tax_code="2300782217",
        ...
    )
    file_manager = FileManager("/output")
    filename = file_manager.generate_filename(declaration)
    assert filename == "2300782217_308010891440.pdf"

def test_channel_filtering():
    """Test that only green and yellow channels are eligible"""
    processor = DeclarationProcessor()
    
    green_decl = Declaration(channel="Xanh", status="T", ...)
    assert processor.is_eligible(green_decl) == True
    
    yellow_decl = Declaration(channel="Vang", status="T", ...)
    assert processor.is_eligible(yellow_decl) == True
    
    red_decl = Declaration(channel="Do", status="T", ...)
    assert processor.is_eligible(red_decl) == False
```

### Property-Based Testing

**Framework**: Hypothesis (Python property-based testing library)

**Configuration**: Each property test should run a minimum of 100 iterations.

**Test Tagging**: Each property-based test must be tagged with a comment explicitly referencing the correctness property in the design document using this format: `# Feature: customs-barcode-automation, Property {number}: {property_text}`

**Coverage Areas**:
- Declaration filtering with random inputs
- Filename generation with various tax codes and declaration numbers
- Configuration validation with random configurations
- Error handling with simulated failures
- Database operations with random data

**Example Property Tests**:
```python
from hypothesis import given, strategies as st

# Feature: customs-barcode-automation, Property 7: Filename format consistency
@given(
    tax_code=st.text(min_size=10, max_size=10, alphabet=st.characters(whitelist_categories=('Nd',))),
    declaration_number=st.text(min_size=12, max_size=12, alphabet=st.characters(whitelist_categories=('Nd',)))
)
def test_property_filename_format(tax_code, declaration_number):
    """For any declaration, filename should follow TaxCode_DeclarationNumber.pdf format"""
    declaration = Declaration(
        declaration_number=declaration_number,
        tax_code=tax_code,
        declaration_date=datetime.now(),
        customs_office_code="18A3",
        transport_method="9999",
        channel="Xanh",
        status="T",
        goods_description=None
    )
    file_manager = FileManager("/output")
    filename = file_manager.generate_filename(declaration)
    
    expected = f"{tax_code}_{declaration_number}.pdf"
    assert filename == expected
    assert filename.endswith(".pdf")
    assert "_" in filename

# Feature: customs-barcode-automation, Property 2: Channel filtering correctness
@given(
    channel=st.sampled_from(["Xanh", "Vang", "Do", "Tím", "Cam"]),
    status=st.sampled_from(["T", "P", "H", "K"])
)
def test_property_channel_filtering(channel, status):
    """For any declaration, eligibility should depend on channel and status"""
    declaration = Declaration(
        declaration_number="123456789012",
        tax_code="1234567890",
        declaration_date=datetime.now(),
        customs_office_code="18A3",
        transport_method="1",
        channel=channel,
        status=status,
        goods_description=None
    )
    processor = DeclarationProcessor()
    is_eligible = processor.is_eligible(declaration)
    
    expected_eligible = (channel in ["Xanh", "Vang"]) and (status == "T")
    assert is_eligible == expected_eligible
```

### Integration Testing

**Coverage Areas**:
- End-to-end workflow execution
- Database connectivity and queries
- API/Web scraping integration
- File system operations
- GUI interactions

**Test Environment**:
- Test SQL Server database with sample data
- Mock API endpoints
- Temporary file system directories
- Headless browser for web scraping tests

### Manual Testing Checklist

- [ ] Application starts successfully with valid configuration
- [ ] Application prevents startup with invalid configuration
- [ ] Automatic mode executes at configured intervals
- [ ] Manual mode only executes on user trigger
- [ ] Mode switching persists across restarts
- [ ] Declarations are filtered correctly
- [ ] Barcodes are retrieved via API
- [ ] Barcodes are retrieved via web scraping when API fails
- [ ] PDF files are saved with correct names
- [ ] Duplicate declarations are skipped
- [ ] Re-download overwrites existing files
- [ ] Search finds declarations correctly
- [ ] Statistics display accurately
- [ ] Logs are written and rotated
- [ ] Error handling works for all error types
- [ ] GUI is responsive and updates correctly

## Performance Considerations

### Database Optimization

- Use indexed queries on declaration_number, tax_code, and declaration_date
- Limit query results to recent declarations (last 7 days by default)
- Use connection pooling for database connections
- Cache processed IDs in memory to reduce database queries

### Web Scraping Optimization

- Reuse WebDriver instances when possible
- Use headless mode to reduce resource usage
- Implement request throttling to avoid overwhelming servers
- Cache session cookies to reduce authentication overhead

### File System Optimization

- Batch file operations when possible
- Use asynchronous I/O for large files
- Implement file system caching for frequently accessed files
- Monitor disk space and alert when low

### Memory Management

- Limit the number of declarations processed per cycle
- Stream large PDF files instead of loading into memory
- Clear WebDriver cache periodically
- Implement garbage collection for long-running processes

### Expected Performance Metrics

- Database query: < 2 seconds for 1000 records
- API barcode retrieval: < 5 seconds per declaration
- Web scraping retrieval: < 15 seconds per declaration
- File save operation: < 1 second per file
- Full workflow cycle: < 5 minutes for 50 declarations
- Memory usage: < 500 MB during normal operation
- CPU usage: < 30% during active processing

## Security Considerations

### Data Protection

- Encrypt database passwords in configuration files using Fernet symmetric encryption
- Store encryption keys separately from configuration
- Use Windows Credential Manager for sensitive data storage (optional enhancement)
- Implement secure deletion of temporary files

### Network Security

- Use HTTPS for all API and web requests
- Validate SSL certificates
- Implement request signing for API calls (if supported)
- Use secure WebDriver configurations

### Access Control

- Require Windows user authentication to run application
- Log all user actions for audit trail
- Implement role-based access for multi-user scenarios (future enhancement)
- Protect configuration files with appropriate file permissions

### Audit Trail

- Log all barcode retrievals with timestamps
- Log all configuration changes
- Log all re-download operations
- Maintain immutable log files for compliance

## Deployment

### System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **Python**: 3.8 or later
- **RAM**: Minimum 4 GB, recommended 8 GB
- **Disk Space**: Minimum 500 MB for application, additional space for PDF storage
- **Network**: Stable internet connection for API and web access
- **Database**: SQL Server 2008 R2 or later (ECUS5)

### Installation Steps

1. Install Python 3.8+ from python.org
2. Install required Python packages: `pip install -r requirements.txt`
3. Install Chrome or Edge browser for web scraping
4. Install appropriate WebDriver (ChromeDriver or EdgeDriver)
5. Configure database connection in config.ini
6. Configure output directory and other settings
7. Run application: `python main.py`

### Dependencies (requirements.txt)

```
pyodbc>=4.0.35
selenium>=4.15.0
requests>=2.31.0
APScheduler>=3.10.4
cryptography>=41.0.7
hypothesis>=6.92.0
pytest>=7.4.3
```

### Packaging

- Use PyInstaller to create standalone executable
- Include all dependencies in the package
- Bundle WebDriver with the application
- Create installer using Inno Setup or NSIS

### Configuration Management

- Provide sample configuration file (config.ini.sample)
- Document all configuration options
- Implement configuration validation on startup
- Support environment variables for sensitive data

## Maintenance and Monitoring

### Logging and Monitoring

- Monitor log files for errors and warnings
- Set up alerts for critical errors (disk full, database connection lost)
- Track performance metrics (processing time, success rate)
- Generate daily summary reports

### Backup and Recovery

- Backup tracking database daily
- Backup configuration files
- Implement database recovery from PDF files
- Document recovery procedures

### Updates and Upgrades

- Implement version checking
- Support in-place updates
- Maintain backward compatibility with configuration
- Provide migration scripts for database schema changes

### Troubleshooting Guide

**Common Issues**:

1. **Database connection fails**
   - Check SQL Server is running
   - Verify network connectivity
   - Confirm credentials are correct
   - Check firewall settings

2. **Barcode retrieval fails**
   - Verify internet connectivity
   - Check API endpoint is accessible
   - Confirm website URLs are correct
   - Update WebDriver if browser updated

3. **Files not saving**
   - Check disk space
   - Verify output directory permissions
   - Confirm path is valid
   - Check for file system errors

4. **Application crashes**
   - Check log files for errors
   - Verify all dependencies are installed
   - Confirm Python version compatibility
   - Check for memory issues

## Future Enhancements

### Phase 2 Features

- Multi-user support with role-based access
- Cloud storage integration (Google Drive, OneDrive)
- Email notifications for errors and summaries
- Advanced search and filtering in GUI
- Batch operations (bulk re-download, bulk delete)
- Export processed declarations to Excel
- Dashboard with charts and statistics
- Mobile app for monitoring

### Phase 3 Features

- Machine learning for error prediction
- Automatic retry scheduling optimization
- Integration with other customs systems
- RESTful API for external integrations
- Web-based interface
- Multi-language support
- Advanced reporting and analytics
- Automated testing and deployment (CI/CD)
