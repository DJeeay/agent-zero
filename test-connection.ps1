$ErrorActionPreference = "Continue"

Write-Host "=== Testing LLM Server Connection ===" -ForegroundColor Green

Write-Host "`n1. Checking if llama-server is running..."
docker ps | Select-String llama-server

Write-Host "`n2. Testing HTTP connection to llama-server..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
    $response.Content | ConvertFrom-Json
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3. Testing completion endpoint..."
$body = @{
    prompt = "test"
    n_predict = 10
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/completion" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 10
    Write-Host "   Success: Response received" -ForegroundColor Green
} catch {
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n4. Agent Zero status..."
docker ps | Select-String agent-zero
docker logs agent-zero --tail 3

Write-Host "`nDone."
