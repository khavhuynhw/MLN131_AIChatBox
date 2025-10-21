# HCM Chatbot - Stop All Services Script for Windows
# This script stops all running HCM Chatbot services

Write-Host "Stopping HCM Chatbot System..." -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Red

# Function to stop service by PID
function Stop-ServiceByPid {
    param(
        [string]$ServiceName,
        [string]$PidFile
    )
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($pid) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Stop-Process -Id $pid -Force
                    Write-Host "Stopped $ServiceName (PID: $pid)" -ForegroundColor Green
                } else {
                    Write-Host "Process $ServiceName (PID: $pid) not found" -ForegroundColor Yellow
                }
            }
            catch {
                Write-Host "Could not stop $ServiceName (PID: $pid)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "PID file for $ServiceName not found" -ForegroundColor Yellow
    }
}

# Stop services
Write-Host "Stopping services..." -ForegroundColor Cyan

# Stop .NET API
Stop-ServiceByPid -ServiceName ".NET API" -PidFile "logs\net_api.pid"

# Stop Python AI
Stop-ServiceByPid -ServiceName "Python AI" -PidFile "logs\python_ai.pid"

# Stop Frontend
Stop-ServiceByPid -ServiceName "Frontend" -PidFile "logs\frontend.pid"

# Additional cleanup - kill any remaining processes on our ports
Write-Host "Cleaning up remaining processes..." -ForegroundColor Cyan

$ports = @(3000, 8000, 9000)
foreach ($port in $ports) {
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
                    Select-Object -ExpandProperty OwningProcess | 
                    Get-Unique
        
        foreach ($pid in $processes) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "Stopped process on port $port (PID: $pid)" -ForegroundColor Green
            }
            catch {
                # Process might already be stopped
            }
        }
    }
    catch {
        # No processes on this port
    }
}

Write-Host ""
Write-Host "HCM Chatbot System Stopped!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host ""
Write-Host "To start again, run:" -ForegroundColor Cyan
Write-Host "   .\start-all-windows.ps1" -ForegroundColor White