# ETF Data Scheduler - Windows Task Scheduler Installation
# Run this script as Administrator in PowerShell

param(
    [string]$UltraCoreDir = "C:\Users\mjmil\UltraCore",
    [string]$UpdateTime = "18:00",
    [string]$PythonPath = "python"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ETF Data Scheduler - Windows Installation" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Verify UltraCore directory
if (-not (Test-Path $UltraCoreDir)) {
    Write-Host "❌ UltraCore directory not found: $UltraCoreDir" -ForegroundColor Red
    $UltraCoreDir = Read-Host "Please enter the correct path to UltraCore"
    
    if (-not (Test-Path $UltraCoreDir)) {
        Write-Host "❌ Directory still not found. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "📁 UltraCore directory: $UltraCoreDir" -ForegroundColor Green
Write-Host ""

# Verify Python
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "🐍 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found at: $PythonPath" -ForegroundColor Red
    Write-Host "Please install Python or specify the correct path" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Create task action
$action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "-m ultracore.market_data.etf.cli update" `
    -WorkingDirectory $UltraCoreDir

# Create task trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger -Daily -At $UpdateTime

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Create task principal (run as current user)
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Register the task
$taskName = "ETF Data Daily Update"
$taskDescription = "Automatically updates ASX ETF historical data daily"

Write-Host "📝 Creating scheduled task: $taskName" -ForegroundColor Cyan
Write-Host "   Update time: $UpdateTime" -ForegroundColor Gray
Write-Host "   Working directory: $UltraCoreDir" -ForegroundColor Gray
Write-Host ""

try {
    # Remove existing task if it exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "⚠️  Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    # Register new task
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    
    Write-Host "✅ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Display task information
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Task Information:" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "Name: $($task.TaskName)" -ForegroundColor White
    Write-Host "State: $($task.State)" -ForegroundColor White
    Write-Host "Next Run: $((Get-ScheduledTaskInfo -TaskName $taskName).NextRunTime)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📊 Useful Commands:" -ForegroundColor Cyan
    Write-Host "   View task:        Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host "   Run now:          Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host "   Disable:          Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host "   Enable:           Enable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host "   Remove:           Unregister-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "✅ ETF data will update daily at $UpdateTime" -ForegroundColor Green
    Write-Host ""
    
    # Ask if user wants to run initial update now
    $runNow = Read-Host "Would you like to run the initial data collection now? (y/n)"
    if ($runNow -eq 'y' -or $runNow -eq 'Y') {
        Write-Host ""
        Write-Host "🚀 Running initial data collection..." -ForegroundColor Cyan
        Write-Host "This will take 3-5 minutes for 200+ ETFs" -ForegroundColor Yellow
        Write-Host ""
        
        Set-Location $UltraCoreDir
        & $PythonPath -m ultracore.market_data.etf.cli initialize
    }
    
} catch {
    Write-Host "❌ Error creating scheduled task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
