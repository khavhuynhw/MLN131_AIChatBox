# Start all services for HCM Chatbot on Windows (PowerShell)
# - .NET API on port 9000
# - Python FastAPI on port 8000
# - Frontend static server on port 3000
# Logs and PID files are under ./logs

$ErrorActionPreference = 'Stop'

# Set UTF-8 encoding to avoid Vietnamese font issues in console
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Test-PortFree {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop
        return $false
    } catch {
        return $true
    }
}

function Start-ServiceProc {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [int]$Port,
        [string]$LogFile
    )

    if (-not (Test-PortFree -Port $Port)) {
        Write-Host "Port $Port is busy. Cannot start $Name"
        return $false
    }

    if (-not (Test-Path $global:LogsDir)) {
        New-Item -ItemType Directory -Path $global:LogsDir -Force | Out-Null
    }

    $stdout = Join-Path $global:LogsDir $LogFile
    # stderr is written to a different file than stdout
    if ($stdout -match '\.log$') {
        $stderr = ($stdout -replace '\.log$', '.err.log')
    } else {
        $stderr = "$stdout.err"
    }

    # Use cmd.exe redirection for stdout and stderr to avoid conflicts
    $processInfo = @{
        FilePath = $FilePath
        ArgumentList = $Arguments
        WorkingDirectory = $WorkingDirectory
        NoNewWindow = $true
        PassThru = $true
        RedirectStandardOutput = $stdout
        RedirectStandardError = $stderr
    }
    
    $p = Start-Process @processInfo

    $pidPath = Join-Path $global:LogsDir ("{0}.pid" -f ($Name.ToLower()))
    Set-Content -Path $pidPath -Value $p.Id

    Write-Host "$Name started (PID $($p.Id))"
    return $true
}

function Wait-ForUrl {
    param(
        [string]$Name,
        [string]$Url,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )

    Write-Host "Waiting for $Name to be ready..."
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            Write-Host "$Name is ready"
            return $true
        } catch {
            Start-Sleep -Seconds $DelaySeconds
        }
    }

    Write-Host "$Name did not become ready in time"
    return $false
}

$Root = $PSScriptRoot
$LogsDir = Join-Path $Root 'logs'
$global:LogsDir = $LogsDir

$DotnetPort = 9000
$PythonPort = 8000
$FrontendPort = 3000

# === Prerequisite Checks ===
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Error ".NET SDK is not installed. Please install .NET 8 or later."
    exit 1
}

$backendDir = Join-Path $Root 'backend'
$pythonVenv = Join-Path $backendDir 'venv\Scripts\python.exe'
if (Test-Path $pythonVenv) {
    $pythonCmd = $pythonVenv
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = 'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = 'python'
} else {
    Write-Error "Python is not installed. Please install Python 3.10 or later."
    exit 1
}

# --- PostgreSQL check (optional) ---
try {
    $pg = Test-NetConnection -ComputerName localhost -Port 5432
    if (-not $pg.TcpTestSucceeded) {
        Write-Host "⚠️ Warning: PostgreSQL is not running on port 5432. The .NET API will still start, but database features will be unavailable."
    }
} catch {}

# --- GEMINI_API_KEY check (optional but recommended) ---
$envFile = Join-Path $backendDir '.env'
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️ Warning: Missing backend\\.env (GEMINI_API_KEY). The Python backend may fail to start."
} else {
    $hasKey = Select-String -Path $envFile -Pattern '^GEMINI_API_KEY=' -Quiet
    if (-not $hasKey) {
        Write-Host "⚠️ Warning: GEMINI_API_KEY not found in backend\\.env."
    }
}

# --- 1) Start .NET API ---
$dotnetDir = Join-Path $Root 'dotnet-api\hcm-chatbot-api'
$dnArgs = @('run','--project','Web_API/Web_API.csproj','--urls',"http://localhost:$DotnetPort")
$ok = Start-ServiceProc -Name 'NET_API' -FilePath 'dotnet' -Arguments $dnArgs -WorkingDirectory $dotnetDir -Port $DotnetPort -LogFile 'dotnet-api.log'
if ($ok) { [void](Wait-ForUrl -Name '.NET API' -Url "http://localhost:$DotnetPort/health") }

# --- 2) Start Python AI Backend ---
# Set UTF-8 encoding environment variable for Python (will be inherited by child processes)
$env:PYTHONIOENCODING = 'utf-8'
$pyArgs = @('-m','uvicorn','app.main:app','--host','0.0.0.0','--port',"$PythonPort")
$ok = Start-ServiceProc -Name 'PYTHON_AI' -FilePath $pythonCmd -Arguments $pyArgs -WorkingDirectory $backendDir -Port $PythonPort -LogFile 'python-ai.log'
if ($ok) { [void](Wait-ForUrl -Name 'Python AI' -Url "http://localhost:$PythonPort/health" -MaxAttempts 120 -DelaySeconds 2) }

# --- 3) Start Frontend static server ---
$frontendDir = Join-Path $Root 'frontend'
$feArgs = @('-m','http.server',"$FrontendPort")
$ok = Start-ServiceProc -Name 'FRONTEND' -FilePath $pythonCmd -Arguments $feArgs -WorkingDirectory $frontendDir -Port $FrontendPort -LogFile 'frontend.log'
if ($ok) { [void](Wait-ForUrl -Name 'Frontend' -Url "http://localhost:$FrontendPort") }

Write-Host ""
Write-Host "=== Service URLs ==="
Write-Host "Frontend:    http://localhost:$FrontendPort/index.html"
Write-Host ".NET API:    http://localhost:$DotnetPort/swagger"
Write-Host "Python API:  http://localhost:$PythonPort/docs"

Write-Host ""
Write-Host "Default Admin (if database is empty):"
Write-Host "Username: admin"
Write-Host "Password: admin123"

Write-Host ""
Write-Host "Logs: .\\logs\\*.log"
