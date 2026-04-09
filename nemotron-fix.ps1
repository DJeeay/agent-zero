# Script pour corriger la configuration Nemoton
Write-Host "=== CORRECTION NEMOTRON ===" -ForegroundColor Green

# Mettre à jour les variables d'environnement pour Nemotron
$env:OPENAI_BASE_URL = "http://localhost:1234/v1"
$env:OPENAI_API_KEY = "dummy"
$env:NANOCLAW_MODEL = "nvidia-nemotron-3-nano-4b"

# Ajouter des paramètres pour forcer la réponse normale
$env:OPENAI_EXTRA_HEADERS = "{'X-Force-Response-Format': 'text'}"

Write-Host "Configuration Nemotron mise à jour" -ForegroundColor Cyan

# Redémarrer le daemon
Write-Host "Redémarrage du daemon..." -ForegroundColor Yellow
agn down
agn up -d

Write-Host "Test de l'agent Nemotron..." -ForegroundColor Yellow

# Test direct
try {
    $body = @{
        model = "nvidia-nemotron-3-nano-4b"
        messages = @(@{role = "user"; content = "Bonjour"})
        max_tokens = 100
        temperature = 0.7
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:1234/v1/chat/completions" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 30
    Write-Host "Réponse Nemotron:" -ForegroundColor Green
    Write-Host "Content: $($response.choices[0].message.content)" -ForegroundColor White
    Write-Host "Reasoning: $($response.choices[0].message.reasoning_content)" -ForegroundColor Gray
    Write-Host "Tokens: $($response.usage.total_tokens)" -ForegroundColor Cyan
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== TERMINÉ ===" -ForegroundColor Green
