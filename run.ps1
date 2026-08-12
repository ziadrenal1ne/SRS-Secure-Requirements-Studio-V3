# ==============================================================================
# FOCP Secure Requirements Studio — One-Click Unified Runner (PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"

function Write-Banner {
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host "   FOCP Secure Requirements Studio -- Starting Up       " -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host ""
}

Write-Banner

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $RootDir) { $RootDir = Get-Location }

$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$EnvFile = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $BackendDir ".env.example"

# 1. Environment file setup
if (-not (Test-Path $EnvFile)) {
    if (Test-Path $EnvExample) {
        Write-Host "--> [1/4] Copying backend/.env.example to backend/.env..." -ForegroundColor Yellow
        Copy-Item $EnvExample $EnvFile
    } else {
        Write-Host "--> [1/4] Creating basic backend/.env..." -ForegroundColor Yellow
        "ENVIRONMENT=development`nLOG_LEVEL=INFO" | Out-File -FilePath $EnvFile -Encoding utf8
    }
} else {
    Write-Host "--> [1/4] backend/.env already present." -ForegroundColor Green
}

# 2. Locate Python executable
$PythonPath = ""
$VenvPy1 = Join-Path $RootDir ".venv\Scripts\python.exe"
$VenvPy2 = Join-Path $BackendDir ".venv\Scripts\python.exe"

if (Test-Path $VenvPy1) {
    $PythonPath = $VenvPy1
} elseif (Test-Path $VenvPy2) {
    $PythonPath = $VenvPy2
} else {
    $SysPy = Get-Command python -ErrorAction SilentlyContinue
    if ($SysPy) {
        $PythonPath = $SysPy.Source
    } else {
        Write-Host "[ERROR] Python interpreter not found. Please install Python 3.12+." -ForegroundColor Red
        exit 1
    }
}
Write-Host "--> [2/4] Using Python: $PythonPath" -ForegroundColor Green

# 3. Frontend node check
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js is required but not installed." -ForegroundColor Red
    exit 1
}
Write-Host "--> [3/4] Node.js environment detected." -ForegroundColor Green

# 4. Launch Services
Write-Host ""
Write-Host "--> [4/4] Launching FastAPI Backend and Next.js Frontend..." -ForegroundColor Yellow
Write-Host "--> Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green

$backendJob = Start-Process -FilePath $PythonPath -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" -WorkingDirectory $BackendDir -PassThru

Write-Host "--> Starting Next.js frontend on http://localhost:3000 ..." -ForegroundColor Green
$npmCmd = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
if (-not $npmCmd) { $npmCmd = "npm" }
$frontendJob = Start-Process -FilePath $npmCmd -ArgumentList "run", "dev" -WorkingDirectory $FrontendDir -PassThru

# Open Browser in background after short delay
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:3000"
} | Out-Null

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " Everything started successfully!                       " -ForegroundColor Green
Write-Host " App     : http://localhost:3000" -ForegroundColor Cyan
Write-Host " API     : http://localhost:8000/api/v1" -ForegroundColor Cyan
Write-Host " AI Docs : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Green
Write-Host " Press Ctrl+C in this window to stop all services." -ForegroundColor Gray
Write-Host ""

try {
    while ($true) {
        if ($backendJob.HasExited -or $frontendJob.HasExited) {
            Write-Host "[WARN] One of the services has stopped." -ForegroundColor Yellow
            break
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nStopping backend and frontend services..." -ForegroundColor Yellow
    if ($backendJob -and -not $backendJob.HasExited) {
        Stop-Process -Id $backendJob.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendJob -and -not $frontendJob.HasExited) {
        Stop-Process -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "All services stopped clean." -ForegroundColor Green
}
