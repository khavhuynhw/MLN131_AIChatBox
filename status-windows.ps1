# HCM Chatbot - Status Check Script for Windows
# This script checks the status of all HCM Chatbot services

Write-Host "📊 HCM Chatbot System Status" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

# Function to check service status
function Get-ServiceStatus {
    param(
        [string]$ServiceName,
        [string]$Url,
        [string]$PidFile
    )
    
    Write-Host "🔍 Checking $ServiceName..." -ForegroundColor Yellow
    
    # Check if PID file exists and process is running
    $isRunning = $false
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                $isRunning = $true
                Write-Host "   ✅ Process running (PID: $pid)" -ForegroundColor Green
            }
        }
    }
    
    # Check if service responds
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Service responding at $Url" -ForegroundColor Green
            return "Running"
        }
    }
    catch {
        if ($isRunning) {
            Write-Host "   ⚠️  Process running but service not responding" -ForegroundColor Yellow
            return "Starting"
        } else {
            Write-Host "   ❌ Service not responding" -ForegroundColor Red
            return "Stopped"
        }
    }
    
    return "Stopped"
}

# Check each service
$services = @(
    @{Name="Frontend"; Url="http://localhost:3000"; PidFile="logs\frontend.pid"},
    @{Name="Python AI"; Url="http://localhost:8000/health"; PidFile="logs\python_ai.pid"},
    @{Name=".NET API"; Url="http://localhost:9000/health"; PidFile="logs\net_api.pid"}
)

$allRunning = $true

foreach ($service in $services) {
    $status = Get-ServiceStatus -ServiceName $service.Name -Url $service.Url -PidFile $service.PidFile
    if ($status -ne "Running") {
        $allRunning = $false
    }
    Write-Host ""
}

# Summary
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan

if ($allRunning) {
    Write-Host "🎉 All services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Service URLs:" -ForegroundColor Cyan
    Write-Host "   🌐 Frontend:    http://localhost:3000/welcome.html" -ForegroundColor White
    Write-Host "   🔗 .NET API:    http://localhost:9000/swagger" -ForegroundColor White
    Write-Host "   🤖 Python AI:   http://localhost:8000/docs" -ForegroundColor White
} else {
    Write-Host "⚠️  Some services are not running properly" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Commands:" -ForegroundColor Cyan
    Write-Host "   🚀 Start all:   .\start-all-windows.ps1" -ForegroundColor White
    Write-Host "   🛑 Stop all:    .\stop-all-windows.ps1" -ForegroundColor White
    Write-Host "   📝 View logs:   Get-Content logs\*.log" -ForegroundColor White
}

Write-Host ""
Write-Host "✨ HCM Chatbot Status Check Complete! 🇻🇳" -ForegroundColor Green
