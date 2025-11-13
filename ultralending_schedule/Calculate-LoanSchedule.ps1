param(
    [Parameter(Mandatory=$true)][decimal]$Principal,
    [Parameter(Mandatory=$true)][decimal]$AnnualInterestRate,
    [Parameter(Mandatory=$true)][int]$TermMonths
)

$LoanId = [guid]::NewGuid().ToString()
$MonthlyRate = $AnnualInterestRate / 100 / 12
$MonthlyPayment = $Principal * ($MonthlyRate * [Math]::Pow(1 + $MonthlyRate, $TermMonths)) / ([Math]::Pow(1 + $MonthlyRate, $TermMonths) - 1)
$TotalRepayment = $MonthlyPayment * $TermMonths
$TotalInterest = $TotalRepayment - $Principal

Write-Host "Loan: $LoanId | Payment: $([Math]::Round($MonthlyPayment, 2))" -ForegroundColor Green

$Event = @{
    event_type = "ScheduleGenerated"
    loan_id = $LoanId
    principal = $Principal
    interest_rate = $AnnualInterestRate
    term_months = $TermMonths
    payment_amount = [Math]::Round($MonthlyPayment, 2)
    interest_method = "DecliningBalance"
    repayment_frequency = "Monthly"
    disbursement_date = (Get-Date).ToString('yyyy-MM-dd')
    total_interest = [Math]::Round($TotalInterest, 2)
    total_repayment = [Math]::Round($TotalRepayment, 2)
} | ConvertTo-Json -Compress

echo $Event | docker exec -i ultracore-kafka kafka-console-producer --broker-list localhost:9092 --topic ultralending.schedule.events

Write-Host "Published to Kafka!" -ForegroundColor Cyan
