Write-Host "Kafka Consumer Started" -ForegroundColor Cyan
Write-Host "Topic: ultralending.schedule.events" -ForegroundColor Yellow
Write-Host ""

docker exec -i ultracore-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ultralending.schedule.events --from-beginning | ForEach-Object {
    try {
        $event = $_ | ConvertFrom-Json
        
        if ($event.event_type -eq "ScheduleGenerated") {
            Write-Host "NEW LOAN: $($event.loan_id)" -ForegroundColor Green
            
            $sql = "INSERT INTO ultralending.loan_schedules (loan_id, principal, annual_interest_rate, term_months, interest_method, repayment_frequency, disbursement_date, payment_amount, number_of_payments, total_principal, total_interest, total_repayment, payments_made, status, generated_at) VALUES ('$($event.loan_id)', $($event.principal), $($event.interest_rate), $($event.term_months), '$($event.interest_method)', '$($event.repayment_frequency)', '$($event.disbursement_date)', $($event.payment_amount), $($event.term_months), $($event.principal), $($event.total_interest), $($event.total_repayment), 0, 'ACTIVE', NOW()) ON CONFLICT (loan_id) DO NOTHING;"
            
            docker exec -i ultracore-postgres psql -U ultracore -d ultracore -c $sql 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Saved to PostgreSQL" -ForegroundColor Cyan
            }
        }
        elseif ($event.event_type -eq "PaymentMade") {
            Write-Host "PAYMENT: $($event.transaction_id) | Loan: $($event.loan_id) | Amount: $($event.payment_amount)" -ForegroundColor Yellow
            
            # Insert transaction
            $sql1 = "INSERT INTO ultralending.transactions (transaction_id, loan_id, payment_number, payment_date, payment_amount, payment_method, payment_reference, interest_paid, principal_paid, is_early_payment, is_partial_payment) VALUES ('$($event.transaction_id)', '$($event.loan_id)', 1, '$($event.payment_date)', $($event.payment_amount), '$($event.payment_method)', '$($event.payment_reference)', 0, $($event.payment_amount), false, false);"
            
            docker exec -i ultracore-postgres psql -U ultracore -d ultracore -c $sql1 2>&1 | Out-Null
            
            # Update loan schedule
            $sql2 = "UPDATE ultralending.loan_schedules SET payments_made = payments_made + 1, last_updated = NOW() WHERE loan_id = '$($event.loan_id)';"
            
            docker exec -i ultracore-postgres psql -U ultracore -d ultracore -c $sql2 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Saved to PostgreSQL" -ForegroundColor Cyan
            }
        }
    } catch {}
}
