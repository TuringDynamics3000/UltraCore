# UltraCore Complete Startup - Kafka-First Architecture

Write-Host "`n🚀 ULTRACORE BANKING PLATFORM - KAFKA-FIRST" -ForegroundColor Cyan
Write-Host "=" -repeat 70 -ForegroundColor Cyan

# Step 1: Start Infrastructure
Write-Host "`n1️⃣  Starting infrastructure (Kafka, PostgreSQL, Redis)..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start infrastructure" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Infrastructure started" -ForegroundColor Green
Write-Host "     Kafka UI: http://localhost:8080" -ForegroundColor White
Write-Host "     PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "     Redis: localhost:6379" -ForegroundColor White

# Wait for services to be ready
Write-Host "`n⏳ Waiting for services to be ready (30s)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 2: Initialize Database
Write-Host "`n2️⃣  Initializing database..." -ForegroundColor Cyan
python init_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to initialize database" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Database initialized" -ForegroundColor Green

# Step 3: Start Consumers (in background)
Write-Host "`n3️⃣  Starting Kafka consumers..." -ForegroundColor Cyan
$consumerJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python -m ultracore.events.consumer_service
}

Write-Host "  ✅ Consumers started (Job ID: $($consumerJob.Id))" -ForegroundColor Green

Start-Sleep -Seconds 5

# Step 4: Start API Server
Write-Host "`n4️⃣  Starting API server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -repeat 70 -ForegroundColor Green
Write-Host "🎉 ULTRACORE PLATFORM READY!" -ForegroundColor Green
Write-Host "=" -repeat 70 -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor Cyan
Write-Host "  • API Docs:   http://localhost:8000/api/v1/docs" -ForegroundColor White
Write-Host "  • API Health: http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host "  • Kafka UI:   http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Architecture:" -ForegroundColor Cyan
Write-Host "  • Write → Kafka (source of truth)" -ForegroundColor Green
Write-Host "  • Read  → PostgreSQL (materialized view)" -ForegroundColor Green
Write-Host "  • Cache → Redis (performance)" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Start API
try {
    python run.py
} finally {
    # Cleanup
    Write-Host "`n🛑 Stopping services..." -ForegroundColor Yellow
    Stop-Job -Id $consumerJob.Id
    Remove-Job -Id $consumerJob.Id
    docker-compose down
    Write-Host "  ✅ All services stopped" -ForegroundColor Green
}
