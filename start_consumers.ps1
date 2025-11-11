# UltraCore Consumer Service Startup

Write-Host "`n🔄 STARTING KAFKA CONSUMER SERVICE" -ForegroundColor Cyan
Write-Host "=" -repeat 70 -ForegroundColor Cyan

Write-Host "`n📋 Prerequisites:" -ForegroundColor Yellow
Write-Host "  1. Kafka must be running (docker-compose up -d)" -ForegroundColor White
Write-Host "  2. Database must be initialized" -ForegroundColor White
Write-Host "  3. Migrations must be applied" -ForegroundColor White

# Check if Kafka is running
Write-Host "`n🔍 Checking Kafka..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✅ Kafka UI accessible at http://localhost:8080" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Kafka UI not accessible" -ForegroundColor Yellow
    Write-Host "     Run: docker-compose up -d" -ForegroundColor Cyan
    
    $continue = Read-Host "`n  Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Apply migrations
Write-Host "`n📊 Applying database migrations..." -ForegroundColor Cyan
python -c "from ultracore.database.config import get_db_manager; db = get_db_manager(); db.engine.execute('CREATE TABLE IF NOT EXISTS processed_events (id BIGSERIAL PRIMARY KEY, event_id VARCHAR(50) UNIQUE NOT NULL, event_type VARCHAR(100) NOT NULL, aggregate_id VARCHAR(100) NOT NULL, tenant_id VARCHAR(50) NOT NULL, processed_at TIMESTAMP NOT NULL, consumer_group VARCHAR(100))')"

Write-Host "  ✅ Migrations applied" -ForegroundColor Green

# Start consumer service
Write-Host "`n🚀 Starting consumer service..." -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m ultracore.events.consumer_service
