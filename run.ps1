# ==============================================================================
# FOCP Secure Requirements Studio v2 - One-Click Runner (Windows / PowerShell)
# Run with:  ./run.ps1   or   .\run.bat
# ==============================================================================

$Host.UI.RawUI.WindowTitle = "FOCP SRS - Starting..."

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   FOCP Secure Requirements Studio v2 - Starting Up   " -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Ensure backend .env exists ─────────────────────────────────────────────
if (-not (Test-Path "backend/.env")) {
    Write-Host "[1/4] Copying backend/.env.example -> backend/.env..." -ForegroundColor Yellow
    Copy-Item "backend/.env.example" "backend/.env"
} else {
    Write-Host "[1/4] backend/.env already present." -ForegroundColor Green
}

# ── 2. Install backend dependencies (Poetry) ─────────────────────────────────
Write-Host ""
Write-Host "[2/4] Ensuring backend Python dependencies are installed..." -ForegroundColor Yellow
$poetryOk = $false
if (Get-Command "poetry" -ErrorAction SilentlyContinue) {
    Push-Location "backend"
    poetry install --no-interaction 2>$null | Out-Null
    $poetryOk = $true
    Pop-Location
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    Push-Location "backend"
    python -m poetry install --no-interaction 2>$null | Out-Null
    $poetryOk = $true
    Pop-Location
}
if ($poetryOk) {
    Write-Host "[OK] Backend dependencies ready." -ForegroundColor Green
} else {
    Write-Host "[X] Poetry not found. Install from https://python-poetry.org" -ForegroundColor Red
}

# ── 3. Check AI provider configuration ───────────────────────────────────
Write-Host ""
Write-Host "[3/4] Checking AI provider configuration..." -ForegroundColor Yellow
Write-Host "[OK] AI provider settings will be loaded from backend/.env" -ForegroundColor Green
Write-Host "[INFO] If using Google Gemini, set GEMINI_API_KEY in backend/.env" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] The application supports Gemini or template fallback only." -ForegroundColor Cyan

# ── 4. Detect Docker or start locally ────────────────────────────────────────
Write-Host ""
Write-Host "[4/4] Detecting orchestration mode..." -ForegroundColor Yellow

$dockerRunning = $false
try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $dockerRunning = $true }
} catch {}

if ($dockerRunning) {
    Write-Host ""
    Write-Host "[DOCKER] Launching with Docker Compose..." -ForegroundColor Green
    Write-Host "    App     : http://localhost:3000" -ForegroundColor Cyan
    Write-Host "    API     : http://localhost:8000/api/v1" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Cyan
    Write-Host ""
    docker compose up --build
} else {
    Write-Host "[LOCAL] Docker not running. Starting services in separate windows..." -ForegroundColor Yellow

    # Determine backend command
    $backendCmd = "cd backend; python -m poetry run uvicorn app.main:app --reload --port 8000"
    if (Get-Command "poetry" -ErrorAction SilentlyContinue) {
        $backendCmd = "cd backend; poetry run uvicorn app.main:app --reload --port 8000"
    }

    Write-Host "    [FastAPI] Starting on http://localhost:8000 ..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$backendCmd"

    Start-Sleep -Seconds 2

    Write-Host "    [Next.js] Starting on http://localhost:3000 ..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

    # Open browser after services have time to boot
    if (Get-Command "Start-ThreadJob" -ErrorAction SilentlyContinue) {
        Start-ThreadJob -ScriptBlock {
            Start-Sleep -Seconds 7
            Start-Process "http://localhost:3000"
        } | Out-Null
    }

    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host " Everything started in separate windows!" -ForegroundColor Green
    Write-Host " App     : http://localhost:3000" -ForegroundColor Cyan
    Write-Host " API     : http://localhost:8000/api/v1" -ForegroundColor Cyan
    Write-Host " AI docs : http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Close the spawned windows to stop backend/frontend." -ForegroundColor Gray
}
