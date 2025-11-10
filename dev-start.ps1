# dev-start.ps1
# Start development environment

Write-Host "
🚀 Starting UltraCore development environment...
" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ .env file not found. Copy from .env.example" -ForegroundColor Yellow
    Write-Host "   cp .env.example .env
" -ForegroundColor Cyan
    exit
}

# Start Docker services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services
Write-Host "
⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check services
Write-Host "
✅ Services status:" -ForegroundColor Green
docker-compose ps

# Start application
Write-Host "
🚀 Starting UltraCore API..." -ForegroundColor Yellow
Write-Host "   API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Docs: http://localhost:8000/docs
" -ForegroundColor Cyan

python -m ultracore.main
