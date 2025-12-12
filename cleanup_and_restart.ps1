# Cleanup and Restart Script
# This script cleans Python cache and restarts the application

Write-Host "=== Customs Barcode Automation - Cleanup & Restart ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any running instances
Write-Host "Step 1: Checking for running instances..." -ForegroundColor Yellow
$processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Auto ma vach*"}
if ($processes) {
    Write-Host "  Found $($processes.Count) running instance(s)" -ForegroundColor Red
    Write-Host "  Stopping..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Stopped" -ForegroundColor Green
} else {
    Write-Host "  ✓ No running instances" -ForegroundColor Green
}

# Step 2: Clean __pycache__ directories
Write-Host ""
Write-Host "Step 2: Cleaning __pycache__ directories..." -ForegroundColor Yellow
$pycacheDirs = Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
if ($pycacheDirs) {
    Write-Host "  Found $($pycacheDirs.Count) __pycache__ directories" -ForegroundColor Yellow
    $pycacheDirs | Remove-Item -Recurse -Force
    Write-Host "  ✓ Cleaned" -ForegroundColor Green
} else {
    Write-Host "  ✓ No __pycache__ directories found" -ForegroundColor Green
}

# Step 3: Clean .pyc files
Write-Host ""
Write-Host "Step 3: Cleaning .pyc files..." -ForegroundColor Yellow
$pycFiles = Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
if ($pycFiles) {
    Write-Host "  Found $($pycFiles.Count) .pyc files" -ForegroundColor Yellow
    $pycFiles | Remove-Item -Force
    Write-Host "  ✓ Cleaned" -ForegroundColor Green
} else {
    Write-Host "  ✓ No .pyc files found" -ForegroundColor Green
}

# Step 4: Verify EnhancedManualPanel
Write-Host ""
Write-Host "Step 4: Verifying EnhancedManualPanel..." -ForegroundColor Yellow
try {
    $result = python diagnose_enhanced_panel.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ EnhancedManualPanel verified" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Verification failed" -ForegroundColor Red
        Write-Host $result
    }
} catch {
    Write-Host "  ✗ Error running diagnostic" -ForegroundColor Red
}

# Step 5: Start application
Write-Host ""
Write-Host "Step 5: Starting application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Application Starting ===" -ForegroundColor Cyan
Write-Host ""

python main.py
