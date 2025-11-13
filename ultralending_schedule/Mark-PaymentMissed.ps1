param(
    [Parameter(Mandatory=$true)]
    [string]$LoanId,
    
    [Parameter(Mandatory=$true)]
    [int]$PaymentNumber,
    
    [Parameter(Mandatory=$false)]
    [string]$MissedDate = (Get-Date).ToString('yyyy-MM-dd')
)

Write-Host "Marking payment as missed: Loan $LoanId, Payment #$PaymentNumber" -ForegroundColor Red

$Event = @{
    event_type = "PaymentMissed"
    loan_id = $LoanId
    payment_number = $PaymentNumber
    missed_date = $MissedDate
    recorded_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json -Compress

echo $Event | docker exec -i ultracore-kafka kafka-console-producer --broker-list localhost:9092 --topic ultralending.schedule.events

Write-Host "Published PaymentMissed to Kafka!" -ForegroundColor Yellow
