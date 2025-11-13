param(
    [Parameter(Mandatory=$true)]
    [string]$LoanId,
    
    [Parameter(Mandatory=$true)]
    [decimal]$NewInterestRate,
    
    [Parameter(Mandatory=$false)]
    [string]$Reason = "Interest rate adjustment"
)

Write-Host "Recalculating schedule for loan: $LoanId" -ForegroundColor Yellow
Write-Host "New rate: $NewInterestRate%" -ForegroundColor Cyan

$Event = @{
    event_type = "ScheduleRecalculated"
    loan_id = $LoanId
    new_interest_rate = $NewInterestRate
    reason = $Reason
    recalculated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json -Compress

echo $Event | docker exec -i ultracore-kafka kafka-console-producer --broker-list localhost:9092 --topic ultralending.schedule.events

Write-Host "Published ScheduleRecalculated to Kafka!" -ForegroundColor Green
