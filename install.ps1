# Customs Barcode Automation - Installation Script (PowerShell)
# This script installs all dependencies and sets up the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Customs Barcode Automation Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/5] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check Python version
$versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python 3.8 or higher is required" -ForegroundColor Red
    Write-Host "Please upgrade your Python installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Create configuration file
Write-Host "[3/5] Creating configuration file..." -ForegroundColor Cyan
if (-not (Test-Path "config.ini")) {
    Copy-Item "config.ini.sample" "config.ini"
    Write-Host "Configuration file created: config.ini" -ForegroundColor Green
    Write-Host "IMPORTANT: Edit config.ini with your database credentials" -ForegroundColor Yellow
} else {
    Write-Host "Configuration file already exists: config.ini" -ForegroundColor Green
}
Write-Host ""

# Create directories
Write-Host "[4/5] Creating directories..." -ForegroundColor Cyan
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "Created logs directory" -ForegroundColor Green
} else {
    Write-Host "Logs directory already exists" -ForegroundColor Green
}
Write-Host ""

# Check WebDriver
Write-Host "[5/5] Checking WebDriver..." -ForegroundColor Cyan
$chromedriverFound = Get-Command chromedriver.exe -ErrorAction SilentlyContinue
$edgedriverFound = Get-Command msedgedriver.exe -ErrorAction SilentlyContinue

if ($chromedriverFound) {
    Write-Host "ChromeDriver found" -ForegroundColor Green
} elseif ($edgedriverFound) {
    Write-Host "EdgeDriver found" -ForegroundColor Green
} else {
    Write-Host "WARNING: WebDriver not found in PATH" -ForegroundColor Yellow
    Write-Host "Please download ChromeDriver or EdgeDriver:" -ForegroundColor Yellow
    Write-Host "  ChromeDriver: https://chromedriver.chromium.org/" -ForegroundColor Yellow
    Write-Host "  EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/" -ForegroundColor Yellow
    Write-Host "Place the driver executable in this directory or add to PATH" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit config.ini with your database credentials"
Write-Host "2. Ensure WebDriver (ChromeDriver or EdgeDriver) is installed"
Write-Host "3. Run the application: python main.py"
Write-Host ""
Write-Host "For detailed instructions, see README.md" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
