param(
    [Parameter(Mandatory=$true)]
    [string]$LoanId,
    
    [Parameter(Mandatory=$true)]
    [decimal]$PaymentAmount,
    
    [Parameter(Mandatory=$false)]
    [string]$PaymentMethod = "DirectDebit",
    
    [Parameter(Mandatory=$false)]
    [string]$PaymentReference = ""
)

$TransactionId = [guid]::NewGuid().ToString()
$PaymentDate = (Get-Date).ToString('yyyy-MM-dd')

if (-not $PaymentReference) {
    $PaymentReference = "AUTO-$TransactionId"
}

Write-Host "Payment: $TransactionId | Amount: $PaymentAmount | Loan: $LoanId" -ForegroundColor Green

$Event = @{
    event_type = "PaymentMade"
    transaction_id = $TransactionId
    loan_id = $LoanId
    payment_amount = $PaymentAmount
    payment_method = $PaymentMethod
    payment_reference = $PaymentReference
    payment_date = $PaymentDate
    recorded_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
} | ConvertTo-Json -Compress

echo $Event | docker exec -i ultracore-kafka kafka-console-producer --broker-list localhost:9092 --topic ultralending.schedule.events

Write-Host "Published to Kafka!" -ForegroundColor Cyan
