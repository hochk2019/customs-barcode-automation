# Customs Barcode Automation

Hệ thống tự động hóa khai báo hải quan - Ứng dụng Windows tự động trích xuất thông tin tờ khai từ cơ sở dữ liệu ECUS5 và lấy mã vạch từ hệ thống Tổng Cục Hải Quan.

## Features

### Core Features
- Tự động trích xuất thông tin tờ khai từ ECUS5 SQL Server
- Lọc tờ khai theo luồng xanh/vàng và trạng thái thông quan
- Tự động lấy mã vạch qua API hoặc web scraping
- Lưu trữ PDF mã vạch với tên file chuẩn hóa
- Theo dõi tờ khai đã xử lý để tránh trùng lặp
- Giao diện đồ họa để giám sát và điều khiển
- Hỗ trợ chế độ tự động và thủ công
- Chức năng tải lại mã vạch cho tờ khai đã xử lý

### V1.1 New Features (December 2024)
- **Settings Dialog**: Cấu hình phương thức lấy mã vạch (Auto/API/Web) và định dạng tên file PDF trực tiếp từ giao diện
- **Smart Company Search**: Tìm kiếm công ty thông minh theo tên hoặc mã số thuế, tự động chọn khi khớp chính xác
- **Unified Company Panel**: Gộp khu vực quản lý công ty và chọn thời gian thành một panel thống nhất
- **PDF Naming Options**: Tùy chọn đặt tên file PDF theo 3 định dạng: MST_SốTK, SốHĐ_SốTK, SốVĐ_SốTK
- **Default Unchecked**: Tờ khai mặc định không được chọn khi xem trước, cho phép chọn thủ công

## System Requirements

- Windows 10 or later
- Python 3.8 or higher
- SQL Server 2008 R2 or later (ECUS5 database)
- Chrome or Edge browser (for web scraping fallback)
- Internet connection

## Installation

### 1. Install Python

Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/)

Make sure to check "Add Python to PATH" during installation.

### 2. Clone or Download the Project

```bash
git clone <repository-url>
cd customs-barcode-automation
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install WebDriver

For Selenium web scraping, you need ChromeDriver or EdgeDriver:

**Option A: ChromeDriver**
- Download from: https://chromedriver.chromium.org/
- Place `chromedriver.exe` in the project directory or add to PATH

**Option B: EdgeDriver**
- Download from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
- Place `msedgedriver.exe` in the project directory or add to PATH

### 5. Configure the Application

Create a `config.ini` file in the project root:

```ini
[Database]
server = your_server_address
database = ECUS5VNACCS
username = your_username
password = your_password

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

**Note**: The password will be automatically encrypted after the first run.

## Usage

### Running the Application

```bash
python main.py
```

### GUI Controls

- **Start**: Begin automatic polling (in automatic mode)
- **Stop**: Stop automatic polling
- **Run Once**: Manually trigger a single polling cycle
- **Mode Toggle**: Switch between Automatic and Manual modes
- **Browse**: Change the output directory for PDF files

### Processed Declarations Panel

- **Search**: Find declarations by number or tax code
- **Re-download Selected**: Re-download barcodes for selected declarations
- **Open File Location**: Open the folder containing the PDF file
- **Refresh**: Reload the list of processed declarations

### Operation Modes

**Automatic Mode**:
- System polls the database every 5 minutes (configurable)
- Automatically processes new declarations
- Runs continuously until stopped

**Manual Mode**:
- System only processes when "Run Once" is clicked
- Useful for testing or controlled processing

## Configuration Options

### Database Section

- `server`: SQL Server address
- `database`: Database name (usually ECUS5VNACCS)
- `username`: Database username
- `password`: Database password (will be encrypted)

### BarcodeService Section

- `api_url`: QRCode API endpoint
- `primary_web_url`: Primary website for web scraping
- `backup_web_url`: Backup website if primary fails
- `timeout`: Request timeout in seconds

### Application Section

- `output_directory`: Where to save PDF files
- `polling_interval`: Seconds between automatic polls (default: 300)
- `max_retries`: Maximum retry attempts for failed operations
- `retry_delay`: Base delay in seconds for retry backoff
- `operation_mode`: Start in 'automatic' or 'manual' mode

### Logging Section

- `log_level`: DEBUG, INFO, WARNING, ERROR, or CRITICAL
- `log_file`: Path to log file
- `max_log_size`: Maximum log file size in bytes before rotation
- `backup_count`: Number of backup log files to keep

## Project Structure

```
customs-barcode-automation/
├── config/                 # Configuration management
├── database/              # Database connectivity
├── processors/            # Declaration processing logic
├── web_utils/             # Barcode retrieval (API & web scraping)
├── file_utils/            # File management
├── scheduler/             # Workflow scheduling
├── models/                # Data models
├── logs/                  # Application logs
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── config.ini            # Configuration file
└── README.md            # This file
```

## User Guide

### First Time Setup

1. **Configure Database Connection**
   - Open `config.ini` in a text editor
   - Update the `[Database]` section with your ECUS5 server details
   - Save the file

2. **Set Output Directory**
   - Choose a location where PDF files will be saved
   - Update `output_directory` in `config.ini` or use the Browse button in the GUI
   - Ensure the directory has write permissions

3. **Test Connection**
   - Run the application: `python main.py`
   - The GUI will display connection status
   - Check the log panel for any errors

### Daily Operations

#### Automatic Mode (Recommended)

1. Start the application
2. Ensure "Automatic" mode is selected
3. Click "Start" button
4. The system will poll every 5 minutes automatically
5. Monitor the statistics panel for progress
6. Check the log panel for any issues

#### Manual Mode

1. Start the application
2. Select "Manual" mode
3. Click "Run Once" whenever you want to process declarations
4. Wait for the cycle to complete
5. Review results in the statistics panel

### Managing Processed Declarations

#### Searching for Declarations

1. Navigate to the "Processed Declarations" panel
2. Enter a declaration number or tax code in the search box
3. Click "Search"
4. Results will be filtered in the list below

#### Re-downloading Barcodes

If you need to re-download a barcode (e.g., file was corrupted or deleted):

1. Find the declaration in the "Processed Declarations" list
2. Check the checkbox next to the declaration(s)
3. Click "Re-download Selected"
4. The system will retrieve and overwrite the existing PDF
5. The timestamp will be updated in the tracking database

#### Opening File Location

1. Select a declaration from the list
2. Click "Open File Location"
3. Windows Explorer will open to the folder containing the PDF

### Understanding Statistics

- **Declarations Processed**: Total number of declarations processed in the current session
- **Barcodes Retrieved**: Number of barcodes successfully downloaded
- **Errors**: Number of failures (network issues, invalid data, etc.)
- **Last Run**: Timestamp of the most recent polling cycle

### Log Messages

The log panel displays real-time information:

- **INFO** (blue): Normal operations
- **WARNING** (yellow): Non-critical issues (e.g., duplicate file skipped)
- **ERROR** (red): Failures that need attention
- **DEBUG** (gray): Detailed technical information (only in DEBUG mode)

## Troubleshooting

### Database Connection Issues

**Problem**: "Failed to connect to database" error

**Solutions**:
1. Verify SQL Server is running and accessible
   ```bash
   ping your_server_address
   ```
2. Check SQL Server authentication mode:
   - Open SQL Server Management Studio
   - Right-click server → Properties → Security
   - Ensure "SQL Server and Windows Authentication mode" is enabled
3. Verify firewall allows SQL Server port (default: 1433)
4. Test connection string:
   - Check server name format: `server\instance` or `server,port`
   - Verify database name is correct
5. Ensure user has SELECT permissions on ECUS5 tables:
   - `DToKhaiMDIDs`
   - `DHangMDDKs`

**Problem**: "Connection timeout" error

**Solutions**:
1. Increase timeout in `config.ini`:
   ```ini
   [Database]
   timeout = 60
   ```
2. Check network latency to SQL Server
3. Verify SQL Server is not overloaded

### Barcode Retrieval Failures

**Problem**: "Failed to retrieve barcode via API"

**Solutions**:
1. Check internet connection
2. Verify API URL is accessible:
   ```bash
   curl http://103.248.160.25:8086/WS_Container/QRCode.asmx
   ```
3. Check if customs API service is online
4. System will automatically fallback to web scraping

**Problem**: "Web scraping failed"

**Solutions**:
1. Ensure Chrome or Edge browser is installed
2. Download matching WebDriver version:
   - Chrome: Check version in `chrome://version/`
   - Download ChromeDriver: https://chromedriver.chromium.org/
3. Place WebDriver in project directory or system PATH
4. Check customs website availability:
   - https://pus.customs.gov.vn/faces/ContainerBarcode
   - https://pus1.customs.gov.vn/BarcodeContainer/BarcodeContainer.aspx
5. Verify declaration data is valid (number, tax code, date)

**Problem**: "WebDriver not found"

**Solutions**:
1. Download ChromeDriver or EdgeDriver (see Installation section)
2. Place executable in project root directory
3. Or add to system PATH:
   - Windows: System Properties → Environment Variables → Path
4. Restart the application

### File Permission Errors

**Problem**: "Permission denied" when saving PDF

**Solutions**:
1. Check output directory permissions:
   - Right-click folder → Properties → Security
   - Ensure your user has "Write" permission
2. Run application as Administrator (if necessary)
3. Choose a different output directory with write access
4. Close any programs that might have PDF files open

**Problem**: "Disk full" error

**Solutions**:
1. Free up disk space on the target drive
2. Change output directory to a drive with more space
3. Archive or delete old PDF files

### Configuration Errors

**Problem**: "Configuration file not found"

**Solutions**:
1. Ensure `config.ini` exists in the project root
2. Copy from `config.ini.sample`:
   ```bash
   copy config.ini.sample config.ini
   ```
3. Edit with your settings

**Problem**: "Invalid configuration" error

**Solutions**:
1. Check all required fields are present in `config.ini`
2. Verify no typos in section names: `[Database]`, `[BarcodeService]`, etc.
3. Ensure values are properly formatted (no extra quotes)
4. Check for special characters in paths (use `\\` or `/` for paths)

**Problem**: "Password decryption failed"

**Solutions**:
1. Delete encrypted password from `config.ini`
2. Enter plain text password
3. Application will re-encrypt on next run
4. If `.encryption_key` file is missing or corrupted, delete it and re-enter password

### Application Performance Issues

**Problem**: Application is slow or unresponsive

**Solutions**:
1. Reduce polling interval if processing many declarations:
   ```ini
   [Application]
   polling_interval = 600  # 10 minutes instead of 5
   ```
2. Check database query performance
3. Ensure adequate system resources (RAM, CPU)
4. Close unnecessary applications
5. Check network speed to SQL Server and customs websites

**Problem**: High memory usage

**Solutions**:
1. Restart the application periodically
2. Reduce log level to WARNING or ERROR:
   ```ini
   [Logging]
   log_level = WARNING
   ```
3. Enable log rotation (already configured by default)
4. Process declarations in smaller batches

### Common Error Messages

**"Transport method 9999 excluded"**
- This is normal - declarations with transport method 9999 are intentionally skipped
- No action needed

**"Internal management code detected"**
- Declarations with `#&NKTC` or `#&XKTC` codes are excluded per business rules
- No action needed

**"Declaration already processed"**
- The system tracks processed declarations to avoid duplicates
- Use "Re-download Selected" if you need to retrieve the barcode again

**"No new declarations found"**
- No eligible declarations in the database for the current polling cycle
- This is normal during periods of low activity

### Log Files

For detailed troubleshooting, check the log files:

**Location**: `logs/app.log`

**View recent logs**:
```bash
type logs\app.log
```

**View last 50 lines**:
```bash
powershell Get-Content logs\app.log -Tail 50
```

**Search for errors**:
```bash
findstr /i "error" logs\app.log
```

**Log Rotation**:
- Logs automatically rotate when they reach 10MB
- Up to 5 backup files are kept (`app.log.1`, `app.log.2`, etc.)
- Older logs are automatically deleted

### Getting Help

1. **Check the logs**: Most issues are explained in the log files
2. **Review error messages**: The GUI displays user-friendly error messages
3. **Verify configuration**: Double-check all settings in `config.ini`
4. **Test components individually**:
   - Database connection: Check SQL Server connectivity
   - API access: Test API URL in browser or curl
   - WebDriver: Run a simple Selenium test
5. **Contact support**: Provide log files and error messages

## Advanced Configuration

### Custom Polling Interval

Adjust how often the system checks for new declarations:

```ini
[Application]
polling_interval = 300  # seconds (5 minutes)
```

Recommended values:
- High volume: 180 seconds (3 minutes)
- Normal volume: 300 seconds (5 minutes)
- Low volume: 600 seconds (10 minutes)

### Retry Configuration

Configure retry behavior for failed operations:

```ini
[Application]
max_retries = 3      # Number of retry attempts
retry_delay = 5      # Base delay in seconds (exponential backoff)
```

With these settings:
- 1st retry: after 5 seconds
- 2nd retry: after 10 seconds
- 3rd retry: after 20 seconds

### Log Level Configuration

Control the amount of logging detail:

```ini
[Logging]
log_level = INFO
```

Available levels (from most to least verbose):
- **DEBUG**: Detailed technical information for troubleshooting
- **INFO**: General informational messages (recommended)
- **WARNING**: Warning messages for non-critical issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause application failure

### Database Query Optimization

If you have a large ECUS5 database, you can optimize queries:

1. Ensure indexes exist on:
   - `DToKhaiMDIDs.NGAY_DK`
   - `DToKhaiMDIDs.TTTK`
   - `DToKhaiMDIDs.PLUONG`

2. Adjust the date range in the query (default: 7 days)
   - Edit `database/ecus_connector.py` if needed

### Multiple Instances

To run multiple instances for different tax codes:

1. Create separate directories for each instance
2. Copy the application to each directory
3. Create separate `config.ini` files with different:
   - `output_directory`
   - `log_file`
4. Run each instance independently

## Backup and Recovery

### Backup Tracking Database

The tracking database prevents duplicate processing:

**Location**: `tracking.db` (SQLite file in project root)

**Backup**:
```bash
copy tracking.db tracking.db.backup
```

**Restore**:
```bash
copy tracking.db.backup tracking.db
```

### Rebuild Tracking Database

If the tracking database is corrupted:

1. Delete `tracking.db`
2. Restart the application
3. The system will rebuild from the PDF files in the output directory

### Backup Configuration

**Important files to backup**:
- `config.ini` - Your configuration
- `.encryption_key` - Password encryption key
- `tracking.db` - Processed declarations database
- `logs/` - Historical logs (optional)

## Security Considerations

### Password Encryption

- Passwords in `config.ini` are automatically encrypted using Fernet encryption
- The encryption key is stored in `.encryption_key`
- Keep `.encryption_key` secure and backed up
- If `.encryption_key` is lost, you'll need to re-enter passwords

### File Permissions

- Restrict access to `config.ini` (contains encrypted passwords)
- Restrict access to `.encryption_key`
- Set appropriate permissions on output directory
- Consider using Windows file encryption for sensitive directories

### Network Security

- Use VPN if accessing SQL Server over public networks
- Ensure SQL Server uses encrypted connections (TLS)
- Keep WebDriver and dependencies updated for security patches

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review log files in `logs/app.log`
3. Verify configuration in `config.ini`
4. Contact your system administrator with:
   - Error messages from GUI
   - Relevant log file excerpts
   - Configuration details (without passwords)

## License

Internal use only - Customs Department
