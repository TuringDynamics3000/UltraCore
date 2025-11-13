Write-Host "COLLATERAL CONSUMER" -ForegroundColor Cyan
docker exec -i ultracore-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ultralending.collateral.events --from-beginning | ForEach-Object {
    try {
        $event = $_ | ConvertFrom-Json
        if ($event.event_type -eq "CollateralRegistered") {
            Write-Host "NEW: $($event.payload.collateral_id)" -ForegroundColor Green
            $sql = "INSERT INTO ultralending.collateral (collateral_id, collateral_type, description, estimated_value, current_value, valuation_date, status) VALUES ('$($event.payload.collateral_id)', '$($event.payload.collateral_type)', '$($event.payload.description)', $($event.payload.estimated_value), $($event.payload.estimated_value), CURRENT_DATE, 'PENDING') ON CONFLICT DO NOTHING;"
            docker exec -i ultracore-postgres psql -U ultracore -d ultracore -c $sql 2>&1 | Out-Null
            if ($event.metadata.requires_ai_assessment) {
                Start-Job -ScriptBlock { param($i,$v); & "$PSScriptRoot\agents\AI-CollateralValuation.ps1" -CollateralId $i -EstimatedValue $v } -ArgumentList $event.payload.collateral_id, $event.payload.estimated_value | Out-Null
            }
        }
        if ($event.event_type -eq "AIValuationCompleted") {
            Write-Host "AI: $($event.payload.collateral_id) = $($event.payload.ai_valuation)" -ForegroundColor Magenta
            $sql = "UPDATE ultralending.collateral SET current_value = $($event.payload.ai_valuation), status = 'ACTIVE' WHERE collateral_id = '$($event.payload.collateral_id)';"
            docker exec -i ultracore-postgres psql -U ultracore -d ultracore -c $sql 2>&1 | Out-Null
        }
    } catch {}
}
