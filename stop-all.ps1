# HCM Chatbot - Stop All Services Script (PowerShell)
# This script stops all running services and cleans up

Write-Host "Stopping HCM Chatbot System..." -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

# Function to stop a service by PID file
function Stop-Service {
    param(
        [string]$ServiceName
    )
    
    $pidFile = "logs\$($ServiceName.ToLower()).pid"
    
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        
        if ($pid) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                
                if ($process) {
                    Write-Host "Stopping $ServiceName (PID: $pid)..." -ForegroundColor Yellow
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                    
                    # Force kill if still running
                    $stillRunning = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($stillRunning) {
                        Write-Host "   Force killing $ServiceName..." -ForegroundColor Red
                        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    }
                    
                    Write-Host "SUCCESS: $ServiceName stopped" -ForegroundColor Green
                } else {
                    Write-Host "WARNING: $ServiceName process not found (PID: $pid)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "ERROR: Failed to stop $ServiceName - $_" -ForegroundColor Red
            }
        }
        
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "WARNING: No PID file found for $ServiceName" -ForegroundColor Yellow
    }
}

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Stop individual services
Stop-Service "FRONTEND"
Stop-Service "PYTHON_AI"
Stop-Service "NET_API"

# Kill any remaining processes by port
Write-Host ""
Write-Host "Cleaning up remaining processes..." -ForegroundColor Cyan

# Kill processes on specific ports
$ports = @(3000, 9000, 8000)
foreach ($port in $ports) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            $pid = $connection.OwningProcess
            Write-Host "Killing process on port $port (PID: $pid)..." -ForegroundColor Yellow
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Port is free or error occurred
    }
}

# Kill by process name patterns
Write-Host "Killing processes by name patterns..." -ForegroundColor Cyan

# Kill dotnet Web_API processes
$dotnetProcesses = Get-Process -Name "dotnet" -ErrorAction SilentlyContinue
foreach ($proc in $dotnetProcesses) {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
    if ($cmdLine -match "Web_API") {
        Write-Host "Killing dotnet Web_API (PID: $($proc.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

# Kill Python http.server processes
$pythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue
foreach ($proc in $pythonProcesses) {
    $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
    if ($cmdLine -match "http.server.*3000" -or $cmdLine -match "uvicorn.*app.main") {
        Write-Host "Killing Python server (PID: $($proc.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "SUCCESS: All services stopped successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Log files are preserved in logs/ directory:" -ForegroundColor Cyan
Write-Host "   - logs/dotnet-api.log"
Write-Host "   - logs/python-ai.log"
Write-Host "   - logs/frontend.log"
Write-Host ""
Write-Host "To restart: .\start-all.ps1" -ForegroundColor Green
