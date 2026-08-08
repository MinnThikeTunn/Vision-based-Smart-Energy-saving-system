# PowerShell Bootstrap Script for Vision-Based Smart Energy Saving System
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Vision-Based Smart Energy Saving System Bootstrap " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Create virtual environment if missing
if (-not (Test-Path ".venv")) {
    Write-Host "[1/3] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/3] Virtual environment (.venv) already exists." -ForegroundColor Green
}

# 2. Install dependencies
Write-Host "[2/3] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements.txt websockets

# 3. Launch application server
Write-Host "[3/3] Starting FastAPI server on http://127.0.0.1:8000 ..." -ForegroundColor Green
& .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
