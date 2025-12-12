# Quick Restart Script
Write-Host "=== Quick Restart ===" -ForegroundColor Cyan

# Kill running instances
$processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Auto ma vach*"}
if ($processes) {
    Write-Host "Stopping running instances..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    Start-Sleep -Seconds 1
}

# Clean GUI cache only
Write-Host "Cleaning GUI cache..." -ForegroundColor Yellow
Remove-Item -Recurse -Force gui/__pycache__ -ErrorAction SilentlyContinue

Write-Host "Starting application..." -ForegroundColor Green
Write-Host ""

python main.py
