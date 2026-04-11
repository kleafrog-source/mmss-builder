# PowerShell script to run all services and test
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GEPA-Pezzo-MMSS Integration Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to test if port is available
function Test-Port($port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect("localhost", $port)
        $client.Close()
        return $false  # Port is in use
    } catch {
        return $true   # Port is free
    }
}

# Check ports
Write-Host "`nChecking ports..." -ForegroundColor Yellow
$optPort = Test-Port 8000
$mmssPort = Test-Port 8001

if (-not $optPort) {
    Write-Host "Port 8000 is already in use (Optimizer may be running)" -ForegroundColor Green
} else {
    Write-Host "Port 8000 is free" -ForegroundColor Green
}

if (-not $mmssPort) {
    Write-Host "Port 8001 is already in use (MMSS may be running)" -ForegroundColor Green
} else {
    Write-Host "Port 8001 is free" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "IMPORTANT: Manual Steps Required" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open Terminal 1 and run:" -ForegroundColor Yellow
Write-Host "   cd services\optimizer" -ForegroundColor White
Write-Host "   python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "2. Open Terminal 2 and run:" -ForegroundColor Yellow  
Write-Host "   cd services\mmss" -ForegroundColor White
Write-Host "   python -m uvicorn src.api:app --host 0.0.0.0 --port 8001 --reload" -ForegroundColor White
Write-Host ""
Write-Host "3. After both services are running, execute in this terminal:" -ForegroundColor Yellow
Write-Host "   python test_api_only.py" -ForegroundColor White
Write-Host ""
Write-Host "For Docker (Pezzo): https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe" -ForegroundColor Gray
Write-Host ""
