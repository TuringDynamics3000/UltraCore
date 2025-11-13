param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("Property", "Vehicle", "Equipment", "Securities", "CashDeposit", "Other")]
    [string]$CollateralType,
    
    [Parameter(Mandatory=$true)]
    [string]$Description,
    
    [Parameter(Mandatory=$true)]
    [decimal]$EstimatedValue,
    
    [Parameter(Mandatory=$false)]
    [string]$OwnerName = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = ""
)

$CollateralId = [guid]::NewGuid().ToString()
$EventId = [guid]::NewGuid().ToString()

Write-Host "COLLATERAL REGISTRATION" -ForegroundColor Cyan
Write-Host "ID: $CollateralId | Type: $CollateralType | Value: $EstimatedValue" -ForegroundColor Yellow

$Event = @{
    event_id = $EventId
    event_type = "CollateralRegistered"
    event_version = "v1"
    aggregate_id = $CollateralId
    domain = "collateral"
    metadata = @{ requires_ai_assessment = $true }
    payload = @{
        collateral_id = $CollateralId
        collateral_type = $CollateralType
        description = $Description
        estimated_value = $EstimatedValue
        owner_name = $OwnerName
        location = $Location
    }
} | ConvertTo-Json -Depth 10 -Compress

echo $Event | docker exec -i ultracore-kafka kafka-console-producer --broker-list localhost:9092 --topic ultralending.collateral.events

Write-Host "Published to Kafka!" -ForegroundColor Green
