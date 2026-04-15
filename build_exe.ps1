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
}
catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Clean previous build
Write-Host "[1/5] Cleaning previous build..." -ForegroundColor Cyan
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "Build directories cleaned" -ForegroundColor Green
Write-Host ""

# Build executable
Write-Host "[2/5] Building executable with PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller customs_automation.spec --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Build completed successfully" -ForegroundColor Green
Write-Host ""

# Copy additional files
Write-Host "[3/5] Copying additional files..." -ForegroundColor Cyan
Copy-Item "config.ini.sample" "dist\CustomsAutomation\"
Copy-Item "README.md" "dist\CustomsAutomation\"
Copy-Item "USER_GUIDE.md" "dist\CustomsAutomation\"
if (Test-Path "DEPLOYMENT.md") {
    Copy-Item "DEPLOYMENT.md" "dist\CustomsAutomation\"
}

# Create logs directory
if (-not (Test-Path "dist\CustomsAutomation\logs")) {
    New-Item -ItemType Directory -Path "dist\CustomsAutomation\logs" | Out-Null
}

Write-Host "Additional files copied" -ForegroundColor Green
Write-Host ""

# Create distribution ZIP (for auto-update)
Write-Host "[4/5] Creating distribution ZIP (for auto-update)..." -ForegroundColor Cyan
if (Test-Path "dist\CustomsAutomation.zip") {
    Remove-Item "dist\CustomsAutomation.zip"
}

# Package the contents directly (not the folder) for proper auto-update
$currentDir = Get-Location
Set-Location "dist\CustomsAutomation"
Compress-Archive -Path "*" -DestinationPath "..\CustomsAutomation.zip" -Force
Set-Location $currentDir
Write-Host "Distribution ZIP created: dist\CustomsAutomation.zip" -ForegroundColor Green
Write-Host ""

# Build Inno Setup installer
Write-Host "[5/5] Building installer with Inno Setup..." -ForegroundColor Cyan
$isccPaths = @(
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)
$isccExe = $null
foreach ($path in $isccPaths) {
    if (Test-Path $path) {
        $isccExe = $path
        break
    }
}

if ($isccExe) {
    & $isccExe "installer.iss"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer created successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Inno Setup build failed" -ForegroundColor Yellow
    }
}
else {
    Write-Host "WARNING: Inno Setup not found. Skipping installer build." -ForegroundColor Yellow
    Write-Host "  Install from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Outputs:" -ForegroundColor Cyan
Write-Host "  Executable:   dist\CustomsAutomation\CustomsAutomation.exe" -ForegroundColor White
Write-Host "  Update ZIP:   dist\CustomsAutomation.zip" -ForegroundColor White
if (Test-Path "dist\CustomsBarcodeAutomation_Setup_*.exe") {
    $setupFile = Get-ChildItem "dist\CustomsBarcodeAutomation_Setup_*.exe" | Select-Object -First 1
    Write-Host "  Installer:    $($setupFile.Name)" -ForegroundColor White
}
Write-Host ""
Read-Host "Press Enter to exit"
