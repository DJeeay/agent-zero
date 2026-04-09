#!/usr/bin/env powershell

Write-Host "=== Docker LLM Setup Verification ===" -ForegroundColor Green

Write-Host "`n1. Checking llama-server status..." -ForegroundColor Cyan
$status = docker inspect llama-server --format='{{.State.Health.Status}}'
Write-Host "   Status: $status"

Write-Host "`n2. Testing llama-server health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8080/health" -ErrorAction Stop
    Write-Host "   Health: HEALTHY" -ForegroundColor Green
    Write-Host "   Response: $($health.StatusCode)"
} catch {
    Write-Host "   Health: UNREACHABLE (still warming up)" -ForegroundColor Yellow
    Write-Host "   Error: $_"
}

Write-Host "`n3. Current containers..." -ForegroundColor Cyan
docker ps --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"

Write-Host "`n4. Network configuration..." -ForegroundColor Cyan
docker network inspect llm-network --format='{{range .Containers}}{{.Name}}: {{.IPv4Address}}\n{{end}}'

Write-Host "`n5. Quick test - Call llama-server API..." -ForegroundColor Cyan
$testPayload = @{
    prompt = "Hello, World!"
    temperature = 0.7
} | ConvertTo-Json

Write-Host "   Sending test request to http://localhost:8080/completion"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/completion" `
        -Method POST `
        -ContentType "application/json" `
        -Body $testPayload `
        -ErrorAction Stop
    
    Write-Host "   API Response: Success" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)"
    $result = $response.Content | ConvertFrom-Json
    Write-Host "   First 100 chars: $($result.content.Substring(0, [Math]::Min(100, $result.content.Length)))"
} catch {
    Write-Host "   API Response: Not yet available (model still loading)" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)"
}

Write-Host "`n6. Docker logs (last 10 lines)..." -ForegroundColor Cyan
docker logs llama-server --tail 10 | Select-Object -Last 3

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Wait for 'Health: HEALTHY' status"
Write-Host "  2. Test API: curl http://localhost:8080/completion -X POST -H 'Content-Type: application/json' -d '{""prompt"":""Hi""}'"
Write-Host "  3. Start Agent Zero: docker compose -f docker-compose.agent-zero.yml up -d"
Write-Host "  4. Access Agent Zero: http://localhost:50080"
