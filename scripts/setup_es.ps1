# Requires: .env in project root with ES_URL and ES_API_KEY
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

foreach ($line in Get-Content (Join-Path $root ".env")) {
    if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
    $parts = $line -split '=', 2
    if ($parts.Count -lt 2) { continue }
    $name = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"')
    Set-Item -Path "Env:$name" -Value $value
}

if (-not $env:ES_URL -or -not $env:ES_API_KEY) {
    Write-Error "ES_URL and ES_API_KEY must be set in .env"
}

Write-Host "Creating blr-rentals index..."
$mappingPath = Join-Path $root "ingest/mappings/blr_rentals.json"
$headers = @{
    "Authorization" = "ApiKey $($env:ES_API_KEY)"
    "Content-Type"  = "application/json"
}
Invoke-RestMethod -Uri "$($env:ES_URL.TrimEnd('/'))/blr-rentals" -Method Put -Headers $headers -InFile $mappingPath | Out-Null

Write-Host ""
Write-Host "Verifying ELSER endpoint..."
Invoke-RestMethod -Uri "$($env:ES_URL.TrimEnd('/'))/_inference/.elser-2-elasticsearch" -Headers @{ "Authorization" = "ApiKey $($env:ES_API_KEY)" }

Write-Host ""
Write-Host "Setup complete."
