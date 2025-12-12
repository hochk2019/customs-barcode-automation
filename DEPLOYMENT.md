# Deployment Guide

This guide provides instructions for deploying the Customs Barcode Automation system on Windows machines.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Testing the Installation](#testing-the-installation)
5. [Deployment Checklist](#deployment-checklist)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10 or later (64-bit)
- **RAM**: Minimum 4GB, recommended 8GB
- **Disk Space**: Minimum 500MB for application, plus space for PDF storage
- **Network**: Internet connection for barcode retrieval
- **Database**: Access to ECUS5 SQL Server 2008 R2 or later

### Software Requirements

- **Python**: Version 3.8 or higher
- **Web Browser**: Chrome or Edge (for web scraping fallback)
- **WebDriver**: ChromeDriver or EdgeDriver matching browser version
- **Database Access**: SQL Server credentials with read permissions

## Installation Methods

### Method 1: Automated Installation (Recommended)

#### Using Batch Script (install.bat)

1. Download or extract the application package
2. Open Command Prompt as Administrator
3. Navigate to the application directory:
   ```cmd
   cd C:\path\to\customs-barcode-automation
   ```
4. Run the installation script:
   ```cmd
   install.bat
   ```
5. Follow the on-screen instructions

#### Using PowerShell Script (install.ps1)

1. Download or extract the application package
2. Open PowerShell as Administrator
3. Enable script execution (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Navigate to the application directory:
   ```powershell
   cd C:\path\to\customs-barcode-automation
   ```
5. Run the installation script:
   ```powershell
   .\install.ps1
   ```
6. Follow the on-screen instructions

### Method 2: Manual Installation

#### Step 1: Install Python

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```

#### Step 2: Install Dependencies

1. Open Command Prompt
2. Navigate to application directory
3. Upgrade pip:
   ```cmd
   python -m pip install --upgrade pip
   ```
4. Install requirements:
   ```cmd
   python -m pip install -r requirements.txt
   ```

#### Step 3: Install WebDriver

**For Chrome**:
1. Check Chrome version: `chrome://version/`
2. Download matching ChromeDriver from [chromedriver.chromium.org](https://chromedriver.chromium.org/)
3. Extract `chromedriver.exe`
4. Place in application directory or add to PATH

**For Edge**:
1. Check Edge version: `edge://version/`
2. Download matching EdgeDriver from [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
3. Extract `msedgedriver.exe`
4. Place in application directory or add to PATH

#### Step 4: Create Configuration

1. Copy the sample configuration:
   ```cmd
   copy config.ini.sample config.ini
   ```
2. Edit `config.ini` with your settings (see Configuration section)

#### Step 5: Create Directories

```cmd
mkdir logs
```

## Configuration

### Database Configuration

Edit the `[Database]` section in `config.ini`:

```ini
[Database]
server = your_server_address
database = ECUS5VNACCS
username = your_username
password = your_password
timeout = 30
```

**Important Notes**:
- Use server name or IP address
- For named instances: `server\instance`
- For custom ports: `server,port`
- Password will be encrypted on first run

### Application Configuration

Edit the `[Application]` section:

```ini
[Application]
output_directory = C:\CustomsBarcodes
polling_interval = 300
max_retries = 3
retry_delay = 5
operation_mode = automatic
```

**Configuration Options**:
- `output_directory`: Where PDF files are saved
- `polling_interval`: Seconds between polls (300 = 5 minutes)
- `max_retries`: Retry attempts for failed operations
- `retry_delay`: Base delay for exponential backoff
- `operation_mode`: `automatic` or `manual`

### Barcode Service Configuration

Usually no changes needed:

```ini
[BarcodeService]
api_url = http://103.248.160.25:8086/WS_Container/QRCode.asmx
primary_web_url = https://pus.customs.gov.vn/faces/ContainerBarcode
backup_web_url = https://pus1.customs.gov.vn/BarcodeContainer/BarcodeContainer.aspx
timeout = 30
```

### Logging Configuration

Adjust logging detail:

```ini
[Logging]
log_level = INFO
log_file = logs/app.log
max_log_size = 10485760
backup_count = 5
```

## Testing the Installation

### 1. Test Python Installation

```cmd
python --version
```

Expected output: `Python 3.8.x` or higher

### 2. Test Dependencies

```cmd
python -c "import pyodbc, selenium, requests, cryptography; print('All dependencies OK')"
```

Expected output: `All dependencies OK`

### 3. Test WebDriver

```cmd
chromedriver --version
```

or

```cmd
msedgedriver --version
```

Expected output: Version information

### 4. Test Database Connection

1. Run the application:
   ```cmd
   python main.py
   ```
2. Check the log panel for "Configuration loaded successfully"
3. Click "Run Once" in Manual mode
4. Check for "Connected to database" in logs

### 5. Test Barcode Retrieval

1. Ensure database has eligible declarations
2. Click "Run Once"
3. Monitor log panel for:
   - "Fetched X new declarations"
   - "Successfully saved barcode for..."
4. Check output directory for PDF files

## Deployment Checklist

### Pre-Deployment

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list` shows all packages)
- [ ] WebDriver downloaded and accessible
- [ ] `config.ini` created and configured
- [ ] Database credentials verified
- [ ] Output directory created with write permissions
- [ ] Firewall allows SQL Server connection (port 1433)
- [ ] Firewall allows HTTPS connections to customs websites

### Post-Deployment

- [ ] Application starts without errors
- [ ] Database connection successful
- [ ] Test polling cycle completes
- [ ] PDF files saved to output directory
- [ ] Tracking database created (`tracking.db`)
- [ ] Log files created in `logs/` directory
- [ ] Password encrypted in `config.ini`
- [ ] `.encryption_key` file created

### User Training

- [ ] User understands Automatic vs Manual mode
- [ ] User knows how to start/stop the application
- [ ] User can search and re-download declarations
- [ ] User knows how to interpret log messages
- [ ] User knows where to find PDF files
- [ ] User has contact information for support

## Troubleshooting

### Installation Issues

**Problem**: "Python is not recognized"

**Solution**:
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH:
   - System Properties → Environment Variables
   - Edit PATH variable
   - Add: `C:\Python38` and `C:\Python38\Scripts`

**Problem**: "pip install fails with SSL error"

**Solution**:
1. Update pip: `python -m pip install --upgrade pip`
2. Or use: `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt`

**Problem**: "WebDriver not found"

**Solution**:
1. Download correct version matching browser
2. Place in application directory
3. Or add to PATH environment variable

### Configuration Issues

**Problem**: "Failed to connect to database"

**Solution**:
1. Verify server address is correct
2. Test connection with SQL Server Management Studio
3. Check firewall allows port 1433
4. Verify SQL Server authentication is enabled
5. Confirm user has SELECT permissions

**Problem**: "Configuration file not found"

**Solution**:
1. Ensure `config.ini` exists in application directory
2. Copy from `config.ini.sample` if missing
3. Check file is not named `config.ini.txt`

### Runtime Issues

**Problem**: "Permission denied" when saving PDFs

**Solution**:
1. Run as Administrator
2. Or change output directory to user-writable location
3. Check folder permissions

**Problem**: "WebDriver session not created"

**Solution**:
1. Update WebDriver to match browser version
2. Close all browser instances
3. Restart application

## Deployment Scenarios

### Single User Deployment

1. Install on user's workstation
2. Configure with user's database credentials
3. Set output directory to user's Documents folder
4. Train user on basic operations

### Multi-User Deployment

1. Install on each user's workstation
2. Use shared database credentials (read-only user)
3. Set unique output directories per user
4. Configure separate log files per user
5. Consider using network share for PDF storage

### Server Deployment

1. Install on Windows Server
2. Configure as Windows Service (requires additional setup)
3. Use service account for database access
4. Set output directory to network share
5. Configure email alerts for errors (requires additional development)
6. Set up monitoring and logging

### Testing Environment

1. Install on test machine
2. Use test database or database copy
3. Set short polling interval (60 seconds)
4. Use Manual mode for controlled testing
5. Verify all features before production deployment

## Backup and Recovery

### Files to Backup

- `config.ini` - Configuration
- `.encryption_key` - Password encryption key
- `tracking.db` - Processed declarations database
- `logs/` - Historical logs (optional)

### Backup Procedure

```cmd
REM Create backup directory
mkdir backup\%date:~-4,4%%date:~-10,2%%date:~-7,2%

REM Copy files
copy config.ini backup\%date:~-4,4%%date:~-10,2%%date:~-7,2%\
copy .encryption_key backup\%date:~-4,4%%date:~-10,2%%date:~-7,2%\
copy tracking.db backup\%date:~-4,4%%date:~-10,2%%date:~-7,2%\
```

### Recovery Procedure

1. Reinstall application
2. Restore `config.ini` and `.encryption_key`
3. Restore `tracking.db` (or rebuild from PDFs)
4. Test database connection
5. Run test cycle

## Uninstallation

### Remove Application

1. Stop the application
2. Delete application directory
3. Remove Python (if not needed for other applications)
4. Remove WebDriver

### Clean Up

1. Delete output directory (if PDFs no longer needed)
2. Remove backup files
3. Remove database user (if dedicated user was created)

## Support

For deployment assistance:
1. Review this guide thoroughly
2. Check README.md for detailed usage instructions
3. Review log files for error details
4. Contact system administrator with:
   - Installation log output
   - Error messages
   - Configuration details (without passwords)

## Appendix

### Required Python Packages

```
pyodbc>=4.0.39
selenium>=4.15.0
requests>=2.31.0
APScheduler>=3.10.4
cryptography>=41.0.7
hypothesis>=6.92.0
pytest>=7.4.3
pytest-cov>=4.1.0
python-dateutil>=2.8.2
```

### Firewall Ports

- **SQL Server**: 1433 (TCP)
- **HTTPS**: 443 (TCP) - for customs websites
- **HTTP**: 80 (TCP) - for API (if used)

### File Permissions

- **Application directory**: Read/Write for user
- **Output directory**: Read/Write for user
- **Log directory**: Read/Write for user
- **config.ini**: Read/Write for user (restrict to prevent password exposure)
- **.encryption_key**: Read/Write for user (restrict to prevent key exposure)

### Environment Variables

Optional environment variables for advanced configuration:

- `CUSTOMS_CONFIG_PATH`: Override config.ini location
- `CUSTOMS_OUTPUT_DIR`: Override output directory
- `WEBDRIVER_PATH`: Override WebDriver location

Example:
```cmd
set CUSTOMS_CONFIG_PATH=C:\CustomsConfig\config.ini
python main.py
```
