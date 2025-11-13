# Setup-Module.ps1 - Environment Verification
Clear-Host
Write-Host "UltraLending Setup Check..." -ForegroundColor Cyan
Write-Host ""

$pass = 0

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -ge 5) { 
    Write-Host "[PASS] PowerShell version OK" -ForegroundColor Green
    $pass++ 
} else {
    Write-Host "[FAIL] Need PowerShell 5.0+" -ForegroundColor Red
}

# Check PostgresHelper module
if (Test-Path "$PSScriptRoot\PostgresHelper.psm1") { 
    Write-Host "[PASS] PostgresHelper.psm1 found" -ForegroundColor Green
    $pass++ 
} else {
    Write-Host "[FAIL] PostgresHelper.psm1 missing" -ForegroundColor Red
}

# Check Kafka
$kafkaCheck = docker ps --filter "name=ultracore-kafka" --format "{{.Names}}" 2>$null
if ($kafkaCheck -eq "ultracore-kafka") { 
    Write-Host "[PASS] Kafka running" -ForegroundColor Green
    $pass++ 
} else {
    Write-Host "[FAIL] Kafka not running" -ForegroundColor Red
}

# Check PostgreSQL
$pgCheck = docker ps --filter "name=ultracore-postgres" --format "{{.Names}}" 2>$null
if ($pgCheck -eq "ultracore-postgres") { 
    Write-Host "[PASS] PostgreSQL running" -ForegroundColor Green
    $pass++ 
} else {
    Write-Host "[FAIL] PostgreSQL not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "Score: $pass/4" -ForegroundColor White
Write-Host ""

if ($pass -eq 4) { 
    Write-Host "SUCCESS - ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Run the demo:" -ForegroundColor Yellow
    Write-Host "  .\Example-CompleteLoanJourney.ps1" -ForegroundColor Cyan
} else { 
    Write-Host "FAILED - Fix issues above" -ForegroundColor Red
}
