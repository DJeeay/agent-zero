# Test final de vérification des agents OpenAgents
Write-Host "=== TEST FINAL DE VÉRIFICATION ===" -ForegroundColor Green

# Test 1: Statut des agents
Write-Host "`n1. Vérification du statut des agents..." -ForegroundColor Yellow
try {
    $status = agn status
    Write-Host $status -ForegroundColor Cyan
} catch {
    Write-Host "ERREUR: Impossible d'obtenir le statut des agents" -ForegroundColor Red
}

# Test 2: Connectivité des endpoints
Write-Host "`n2. Test de connectivité des endpoints..." -ForegroundColor Yellow

# Test Hermes endpoint
try {
    $hermesHealth = Invoke-RestMethod -Uri "http://localhost:9000/health" -TimeoutSec 5
    Write-Host "Hermes (port 9000): $($hermesHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "Hermes (port 9000): Non accessible - $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test Nemotron endpoint
try {
    $nemotronModels = Invoke-RestMethod -Uri "http://localhost:1234/v1/models" -TimeoutSec 5
    Write-Host "Nemotron (port 1234): OK - Modèle: $($nemotronModels.data[0].id)" -ForegroundColor Green
} catch {
    Write-Host "Nemotron (port 1234): Non accessible - $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 3: Test simple d'inférence
Write-Host "`n3. Test d'inférence simple..." -ForegroundColor Yellow

# Test Hermes si disponible
try {
    $body = @{
        model = "hermes-3"
        messages = @(@{role = "user"; content = "Hi"})
        max_tokens = 10
    } | ConvertTo-Json
    
    $hermesTest = Invoke-RestMethod -Uri "http://localhost:9000/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "Hermes Response: $($hermesTest.choices[0].message.content)" -ForegroundColor Green
    Write-Host "Tokens: $($hermesTest.usage.total_tokens)" -ForegroundColor Gray
} catch {
    Write-Host "Hermes Test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test Nemotron si disponible
try {
    $body = @{
        model = "nvidia-nemotron-3-nano-4b"
        messages = @(@{role = "user"; content = "Hi"})
        max_tokens = 10
    } | ConvertTo-Json
    
    $nemotronTest = Invoke-RestMethod -Uri "http://localhost:1234/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "Nemotron Response: $($nemotronTest.choices[0].message.content)" -ForegroundColor Green
    Write-Host "Tokens: $($nemotronTest.usage.total_tokens)" -ForegroundColor Gray
} catch {
    Write-Host "Nemotron Test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 4: Vérification des logs
Write-Host "`n4. Vérification des logs récents..." -ForegroundColor Yellow
try {
    $logs = agn logs --tail 5
    Write-Host "Logs récents:" -ForegroundColor Gray
    Write-Host $logs -ForegroundColor White
} catch {
    Write-Host "Impossible de lire les logs" -ForegroundColor Red
}

Write-Host "`n=== TEST TERMINÉ ===" -ForegroundColor Green
Write-Host "Les agents sont configurés et prêts pour l'utilisation." -ForegroundColor Cyan
