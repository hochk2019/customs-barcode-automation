# Build script for creating standalone executable (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Customs Barcode Automation - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
try {
    python -c "import PyInstaller" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
} catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Clean previous build
Write-Host "[1/4] Cleaning previous build..." -ForegroundColor Cyan
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "Build directories cleaned" -ForegroundColor Green
Write-Host ""

# Build executable
Write-Host "[2/4] Building executable with PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller customs_automation.spec --clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Build completed successfully" -ForegroundColor Green
Write-Host ""

# Copy additional files
Write-Host "[3/4] Copying additional files..." -ForegroundColor Cyan
Copy-Item "config.ini.sample" "dist\CustomsAutomation\"
Copy-Item "README.md" "dist\CustomsAutomation\"
Copy-Item "USER_GUIDE.md" "dist\CustomsAutomation\"
Copy-Item "DEPLOYMENT.md" "dist\CustomsAutomation\"

# DO NOT create config.ini - only provide config.ini.sample
# Users should copy config.ini.sample to config.ini and configure it
Write-Host "Skipping config.ini creation - users will use config.ini.sample" -ForegroundColor Yellow

# Create logs directory
if (-not (Test-Path "dist\CustomsAutomation\logs")) {
    New-Item -ItemType Directory -Path "dist\CustomsAutomation\logs" | Out-Null
}

Write-Host "Additional files copied" -ForegroundColor Green
Write-Host ""

# Create distribution package
Write-Host "[4/4] Creating distribution package..." -ForegroundColor Cyan
if (Test-Path "dist\CustomsAutomation.zip") {
    Remove-Item "dist\CustomsAutomation.zip"
}

# Package the contents directly (not the folder) for proper auto-update
Write-Host "Creating flat ZIP structure for auto-update compatibility..." -ForegroundColor Cyan
$currentDir = Get-Location
Set-Location "dist\CustomsAutomation"
Compress-Archive -Path "*" -DestinationPath "..\CustomsAutomation.zip" -Force
Set-Location $currentDir
Write-Host "Distribution package created: dist\CustomsAutomation.zip" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Executable location: dist\CustomsAutomation\CustomsAutomation.exe" -ForegroundColor Cyan
Write-Host "Distribution package: dist\CustomsAutomation.zip" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: WebDriver (chromedriver.exe or msedgedriver.exe) must be" -ForegroundColor Yellow
Write-Host "placed in the same directory as the executable or in system PATH." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
