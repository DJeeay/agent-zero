# Fix API keys for all agents
Write-Host "=== FIXING API KEYS ===" -ForegroundColor Green

# Set global environment variables
$env:OPENAI_API_KEY = "lm-studio"
$env:OPENAI_BASE_URL = "http://localhost:9000/v1"

# Restart daemon with fresh env
Write-Host "Restarting daemon with correct API keys..." -ForegroundColor Yellow
agn down

# Clear any cached environment
Remove-Item Env:\OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:\OPENAI_BASE_URL -ErrorAction SilentlyContinue

# Set fresh
$env:OPENAI_API_KEY = "lm-studio"
$env:OPENAI_BASE_URL = "http://localhost:9000/v1"
$env:NANOCLAW_MODEL = "hermes-3"

agn up -d

Write-Host "Daemon restarted. Testing hermes-local..." -ForegroundColor Yellow

# Test
sleep 5

try {
    $body = @{
        model = "hermes-3"
        messages = @(@{role = "user"; content = "Bonjour"})
        max_tokens = 30
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:9000/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "SUCCESS! Response: $($response.choices[0].message.content)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== DONE ===" -ForegroundColor Green
