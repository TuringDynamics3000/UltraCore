# dev-stop.ps1
# Stop development environment

Write-Host "
🛑 Stopping UltraCore development environment...
" -ForegroundColor Cyan

docker-compose down

Write-Host "✅ Development environment stopped
" -ForegroundColor Green
