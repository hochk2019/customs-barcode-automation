@echo off
REM Customs Barcode Automation - Installation Script
REM This script installs all dependencies and sets up the application

echo ========================================
echo Customs Barcode Automation Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required
    echo Please upgrade your Python installation
    pause
    exit /b 1
)

echo [2/5] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

echo [3/5] Creating configuration file...
if not exist config.ini (
    copy config.ini.sample config.ini
    echo Configuration file created: config.ini
    echo IMPORTANT: Edit config.ini with your database credentials
) else (
    echo Configuration file already exists: config.ini
)
echo.

echo [4/5] Creating directories...
if not exist logs mkdir logs
echo Created logs directory

echo [5/5] Checking WebDriver...
where chromedriver.exe >nul 2>&1
if errorlevel 1 (
    where msedgedriver.exe >nul 2>&1
    if errorlevel 1 (
        echo WARNING: WebDriver not found in PATH
        echo Please download ChromeDriver or EdgeDriver:
        echo   ChromeDriver: https://chromedriver.chromium.org/
        echo   EdgeDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
        echo Place the driver executable in this directory or add to PATH
    ) else (
        echo EdgeDriver found
    )
) else (
    echo ChromeDriver found
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.ini with your database credentials
echo 2. Ensure WebDriver (ChromeDriver or EdgeDriver) is installed
echo 3. Run the application: python main.py
echo.
echo For detailed instructions, see README.md
echo.
pause
