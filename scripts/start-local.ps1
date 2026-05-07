$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonPath)) {
    Write-Host "Local virtual environment was not found at .venv\Scripts\python.exe" -ForegroundColor Red
    Write-Host "Create it first or install dependencies, then run this script again." -ForegroundColor Yellow
    exit 1
}

Set-Location $ProjectRoot

$env:APP_ENV = "test"
$env:APP_NAME = "ShopBuilder API"
$env:PLATFORM_DATABASE_URL = "sqlite:///./shopbuilder_dev_platform.db"
$env:TENANT_DATABASE_URLS = '{"merchant_alpha":"sqlite:///./shopbuilder_dev_alpha.db","merchant_beta":"sqlite:///./shopbuilder_dev_beta.db"}'
$env:REDIS_URL = "redis://localhost:6379/15"
$env:JWT_SECRET_KEY = "dev-access-secret-key-1234567890"
$env:JWT_REFRESH_SECRET_KEY = "dev-refresh-secret-key-0987654321"
$env:WEBHOOK_SIGNING_SECRET = "dev-webhook-secret-key-1234567890"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:8000"
$env:EMAIL_DELIVERY_MODE = "log"
$env:APP_PUBLIC_URL = "http://127.0.0.1:8000"

Write-Host "Starting ShopBuilder API locally..." -ForegroundColor Cyan
Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Health: http://127.0.0.1:8000/health" -ForegroundColor Green
Write-Host ""

& $PythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
