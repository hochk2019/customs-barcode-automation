@echo off
REM Build script for creating standalone executable

echo ========================================
echo Customs Barcode Automation - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [1/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Build directories cleaned
echo.

echo [2/4] Building executable with PyInstaller...
python -m PyInstaller customs_automation.spec --clean
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo Build completed successfully
echo.

echo [3/4] Copying additional files...
copy config.ini.sample dist\CustomsAutomation\
copy README.md dist\CustomsAutomation\
copy USER_GUIDE.md dist\CustomsAutomation\
copy DEPLOYMENT.md dist\CustomsAutomation\

REM Create logs directory in dist
if not exist dist\CustomsAutomation\logs mkdir dist\CustomsAutomation\logs

echo Additional files copied
echo.

echo [4/4] Creating distribution package...
cd dist
if exist CustomsAutomation.zip del CustomsAutomation.zip
powershell Compress-Archive -Path CustomsAutomation -DestinationPath CustomsAutomation.zip
cd ..
echo Distribution package created: dist\CustomsAutomation.zip
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\CustomsAutomation\CustomsAutomation.exe
echo Distribution package: dist\CustomsAutomation.zip
echo.
echo IMPORTANT: WebDriver (chromedriver.exe or msedgedriver.exe) must be
echo placed in the same directory as the executable or in system PATH.
echo.
pause
