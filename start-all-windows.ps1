# HCM Chatbot - Start All Services Script for Windows
# This script starts all three components of the HCM Chatbot system

Write-Host "Starting HCM Chatbot System..." -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Function to start a service in background
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Command,
        [int]$Port,
        [string]$LogFile
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Yellow
    
    # Check if port is available
    if (Test-Port -Port $Port) {
        Write-Host "Port $Port is already in use!" -ForegroundColor Red
        return $false
    }
    
    # Create logs directory if it doesn't exist
    if (!(Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }
    
    # Start the service
    $process = Start-Process -FilePath "powershell" -ArgumentList "-Command", $Command -PassThru -WindowStyle Hidden
    
    # Save PID for later cleanup
    $process.Id | Out-File -FilePath "logs\$($ServiceName.ToLower()).pid" -Encoding ASCII
    
    Write-Host "$ServiceName started (PID: $($process.Id))" -ForegroundColor Green
    return $true
}

# Function to wait for service to be ready
function Wait-ForService {
    param(
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "Waiting for $ServiceName to be ready..." -ForegroundColor Yellow
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "$ServiceName is ready!" -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Service not ready yet
        }
        
        Write-Host "   Attempt $attempt/$MaxAttempts..." -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
    
    Write-Host "$ServiceName failed to start within timeout" -ForegroundColor Red
    return $false
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

# Check if .NET is installed
try {
    $dotnetVersion = dotnet --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "dotnet not found"
    }
    Write-Host ".NET $dotnetVersion found" -ForegroundColor Green
}
catch {
    Write-Host ".NET is not installed. Please install .NET 8.0 or later." -ForegroundColor Red
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "python not found"
    }
    Write-Host "$pythonVersion found" -ForegroundColor Green
}
catch {
    Write-Host "Python 3 is not installed. Please install Python 3.8 or later." -ForegroundColor Red
    exit 1
}

Write-Host "Prerequisites check completed!" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "Starting services..." -ForegroundColor Cyan
Write-Host ""

# 1. Start .NET API
$netCommand = "cd dotnet-api/hcm-chatbot-api; dotnet run --project Web_API/Web_API.csproj --urls http://localhost:9000"
if (Start-Service -ServiceName "NET_API" -Command $netCommand -Port 9000 -LogFile "dotnet-api.log") {
    Start-Sleep -Seconds 5
    if (Wait-ForService -ServiceName ".NET API" -Url "http://localhost:9000/health") {
        Write-Host ""
    } else {
        Write-Host "Failed to start .NET API" -ForegroundColor Red
        exit 1
    }
} else {
    exit 1
}

# 2. Start Python AI Backend
$pythonCommand = "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
if (Start-Service -ServiceName "PYTHON_AI" -Command $pythonCommand -Port 8000 -LogFile "python-ai.log") {
    Start-Sleep -Seconds 5
    if (Wait-ForService -ServiceName "Python AI" -Url "http://localhost:8000/health") {
        Write-Host ""
    } else {
        Write-Host "Failed to start Python AI" -ForegroundColor Red
        exit 1
    }
} else {
    exit 1
}

# 3. Start Frontend
$frontendCommand = "cd frontend; python -m http.server 3000"
if (Start-Service -ServiceName "FRONTEND" -Command $frontendCommand -Port 3000 -LogFile "frontend.log") {
    Start-Sleep -Seconds 3
    if (Wait-ForService -ServiceName "Frontend" -Url "http://localhost:3000") {
        Write-Host ""
    } else {
        Write-Host "Failed to start Frontend" -ForegroundColor Red
        exit 1
    }
} else {
    exit 1
}

# Success message
Write-Host "HCM Chatbot System Started Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000/welcome.html" -ForegroundColor White
Write-Host "   .NET API:    http://localhost:9000/swagger" -ForegroundColor White
Write-Host "   Python AI:   http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Admin Account:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "   Stop all:    .\stop-all-windows.ps1" -ForegroundColor White
Write-Host "   Status:      .\status-windows.ps1" -ForegroundColor White
Write-Host "   Logs:        Get-Content logs\*.log -Wait" -ForegroundColor White
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "   1. Open: http://localhost:3000/welcome.html" -ForegroundColor White
Write-Host "   2. Click 'Dang nhap' or 'Dang ky'" -ForegroundColor White
Write-Host "   3. Start chatting about Ho Chi Minh's thoughts!" -ForegroundColor White
Write-Host ""
Write-Host "Enjoy using HCM Chatbot!" -ForegroundColor Green