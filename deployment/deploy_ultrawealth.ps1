#!/usr/bin/env pwsh
<#
.SYNOPSIS
    UltraWealth Deployment Script

.DESCRIPTION
    Deploys the UltraWealth automated investment system with all dependencies

.PARAMETER Action
    Action to perform: start, stop, restart, logs, status

.EXAMPLE
    .\deploy_ultrawealth.ps1 start
    .\deploy_ultrawealth.ps1 logs
    .\deploy_ultrawealth.ps1 stop
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'init-db')]
    [string]$Action
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Color, [string]$Message)
    Write-Host "${Color}${Message}${Reset}"
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput $Blue "===> $Message"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput $Green "✓ $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput $Yellow "⚠ $Message"
}

function Write-Error-Message {
    param([string]$Message)
    Write-ColorOutput $Red "✗ $Message"
}

# Check Docker
function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        return $true
    } catch {
        Write-Error-Message "Docker or Docker Compose not found. Please install Docker Desktop."
        return $false
    }
}

# Start UltraWealth
function Start-UltraWealth {
    Write-Step "Starting UltraWealth Automated Investment System..."
    
    # Check Docker
    if (-not (Test-Docker)) {
        exit 1
    }
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Step "Creating .env file..."
        @"
SECRET_KEY=$(New-Guid)
ULTRAWEALTH_DATABASE_URL=postgresql://ultracore:ultracore_password@postgres:5432/ultracore
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
REDIS_URL=redis://redis:6379
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Success "Created .env file"
    }
    
    # Start services
    Write-Step "Starting Docker containers..."
    docker-compose -f docker-compose.ultrawealth.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "UltraWealth started successfully!"
        Write-Host ""
        Write-ColorOutput $Green "🚀 UltraWealth is running!"
        Write-Host ""
        Write-Host "Services:"
        Write-Host "  • API:          http://localhost:8891"
        Write-Host "  • API Docs:     http://localhost:8891/docs"
        Write-Host "  • Kafka UI:     http://localhost:8082"
        Write-Host "  • Prometheus:   http://localhost:9090"
        Write-Host "  • Grafana:      http://localhost:3000 (admin/admin)"
        Write-Host ""
        Write-Host "Database:"
        Write-Host "  • PostgreSQL:   localhost:5432"
        Write-Host "  • Redis:        localhost:6379"
        Write-Host ""
    } else {
        Write-Error-Message "Failed to start UltraWealth"
        exit 1
    }
}

# Stop UltraWealth
function Stop-UltraWealth {
    Write-Step "Stopping UltraWealth..."
    docker-compose -f docker-compose.ultrawealth.yml down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "UltraWealth stopped successfully!"
    } else {
        Write-Error-Message "Failed to stop UltraWealth"
        exit 1
    }
}

# Restart UltraWealth
function Restart-UltraWealth {
    Write-Step "Restarting UltraWealth..."
    Stop-UltraWealth
    Start-Sleep -Seconds 2
    Start-UltraWealth
}

# View logs
function Show-Logs {
    Write-Step "Showing UltraWealth logs (Ctrl+C to exit)..."
    docker-compose -f docker-compose.ultrawealth.yml logs -f ultrawealth-api
}

# Show status
function Show-Status {
    Write-Step "UltraWealth Status:"
    docker-compose -f docker-compose.ultrawealth.yml ps
}

# Initialize database
function Initialize-Database {
    Write-Step "Initializing UltraWealth database..."
    
    # Wait for PostgreSQL to be ready
    Write-Step "Waiting for PostgreSQL..."
    Start-Sleep -Seconds 5
    
    # Run database initialization
    docker-compose -f docker-compose.ultrawealth.yml exec ultrawealth-api python -m ultrawealth.database.init_db
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Database initialized successfully!"
    } else {
        Write-Error-Message "Failed to initialize database"
        exit 1
    }
}

# Main execution
Write-Host ""
Write-ColorOutput $Blue "╔════════════════════════════════════════╗"
Write-ColorOutput $Blue "║   UltraWealth Deployment Manager      ║"
Write-ColorOutput $Blue "║   Automated Investment System         ║"
Write-ColorOutput $Blue "╚════════════════════════════════════════╝"
Write-Host ""

switch ($Action) {
    'start' {
        Start-UltraWealth
    }
    'stop' {
        Stop-UltraWealth
    }
    'restart' {
        Restart-UltraWealth
    }
    'logs' {
        Show-Logs
    }
    'status' {
        Show-Status
    }
    'init-db' {
        Initialize-Database
    }
}

Write-Host ""
